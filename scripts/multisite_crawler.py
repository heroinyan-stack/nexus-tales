#!/usr/bin/env python3
"""
Multi-site Chinese Novel Crawler
Sources: quanwenyuedu.io, tmwxw.net, yqxxs.com (mobile)
"""

import json, os, re, time, hashlib, subprocess
from urllib.request import Request, urlopen
from urllib.parse import quote, urljoin
import ssl
import gzip
from io import BytesIO

ctx = ssl.create_default_context()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CHAPTERS_DIR = os.path.join(DATA_DIR, "chapters")
NOVELS_FILE = os.path.join(DATA_DIR, "novels.json")

HEADERS_MOBILE = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "zh-CN,zh;q=0.9",
}
HEADERS_DESKTOP = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "zh-CN,zh;q=0.9",
}
HEADERS_DESKTOP_REFERER = {
    **HEADERS_DESKTOP,
    "Referer": "https://www.google.com/",
}

def fetch_curl(url, timeout=15):
    """Fetch using curl (bypasses Python TLS issues)."""
    try:
        r = subprocess.run(
            ['curl', '-sL', '--connect-timeout', str(timeout), '-A',
             HEADERS_DESKTOP.get('User-Agent',''), '-o', '-', url],
            capture_output=True, timeout=timeout+5)
        if r.returncode != 0 or not r.stdout:
            return None
        raw = r.stdout
        # Detect encoding
        try:
            test = raw[:2000].decode('gbk', errors='replace')
            if any('\u4e00' <= c <= '\u9fff' for c in test[:500]):
                return raw.decode('gbk', errors='replace')
        except:
            pass
        return raw.decode('utf-8', errors='replace')
    except:
        return None

def fetch(url, headers=None, timeout=20, encoding=None, retries=2):
    """Fetch URL with retries and auto-decode gb2312."""
    for attempt in range(retries):
        try:
            req = Request(url, headers=headers or HEADERS_DESKTOP)
            resp = urlopen(req, context=ctx, timeout=timeout)
            raw = resp.read()
            # Handle gzip
            if resp.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            # Try to decode
            ct = resp.headers.get("Content-Type", "")
            charset = encoding
            if not charset:
                m = re.search(r'charset=([^\s;]+)', ct)
                if m:
                    charset = m.group(1)
            if not charset:
                # Try to detect from HTML bytes
                # Prioritize: check bytes for charset meta before decoding
                try:
                    # Try gbk first (common for Chinese sites)
                    test = raw[:2000].decode('gbk', errors='replace')
                    m = re.search(r'charset=["\']?([^"\'>\s;]+)', test, re.I)
                    if m:
                        enc = m.group(1).lower()
                        if enc in ('gbk', 'gb2312', 'gb18030'):
                            return raw.decode('gbk', errors='replace')
                        if enc == 'utf-8':
                            return raw.decode('utf-8', errors='replace')
                except:
                    pass
                # Try utf-8 detection
                try:
                    test = raw[:2000].decode('utf-8', errors='replace')
                    m = re.search(r'charset=["\']?([^"\'>\s;]+)', test, re.I)
                    if m:
                        charset = m.group(1).lower()
                        if charset in ('gbk', 'gb2312', 'gb18030'):
                            return raw.decode('gbk', errors='replace')
                except:
                    pass
            if charset and charset.lower() in ('gbk', 'gb2312', 'gb18030'):
                return raw.decode('gbk', errors='replace')
            # Default: try gbk first for Chinese domain, then utf-8
            try:
                decoded = raw.decode('gbk')
                if any('\u4e00' <= c <= '\u9fff' for c in decoded[:1000]):
                    return decoded
            except:
                pass
            return raw.decode('utf-8', errors='replace')
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(1 * (attempt + 1))
            else:
                print(f"  ⚠ fetch failed: {url} - {e}")
                return None

def slugify(text):
    """Create URL-friendly slug from title."""
    text = re.sub(r'[【】《》「」『』〔〕\[\]()（）]', '', text)
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text).strip('-').lower()
    return text[:60] or hashlib.md5(text.encode()).hexdigest()[:10]

def clean_text(text):
    """Clean extracted text."""
    text = re.sub(r'[ \t]*&nbsp;[ \t]*', '', text)
    text = re.sub(r'　　', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'(?:一秒记住|笔趣阁|手机用户请浏览|记住本站|网址[：:]?\s*|www\.|https?://)[^\n]{0,50}[\n]?', '', text)
    text = re.sub(r'(?:记住|收藏|打开|阅读)[^\n]{0,30}[\n]?', '', text)
    lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) > 3]
    # Filter out navigation/site lines
    lines = [l for l in lines if not re.match(r'^(首页|返回|目录|上一(章|页)|下一(章|页)|列表)$', l)]
    return lines

def load_novels():
    """Load existing novels database."""
    try:
        with open(NOVELS_FILE) as f:
            return json.load(f)
    except:
        return []

def save_novels(novels):
    """Save novels database."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(NOVELS_FILE, 'w') as f:
        json.dump(novels, f, ensure_ascii=False, indent=2)

def save_chapter(slug, num, title, lines):
    """Save a single chapter to data/chapters/{slug}/ch-{num}.json."""
    d = os.path.join(CHAPTERS_DIR, slug)
    os.makedirs(d, exist_ok=True)
    ch = {"num": num, "title": title or f"Chapter {num}", "slug": slug, "lines": lines}
    with open(os.path.join(d, f"ch-{num:04d}.json"), 'w') as f:
        json.dump(ch, f, ensure_ascii=False, indent=2)

def count_chapters(slug):
    """Count existing chapter files for a slug."""
    d = os.path.join(CHAPTERS_DIR, slug)
    if not os.path.isdir(d):
        return 0
    return len([f for f in os.listdir(d) if f.startswith('ch-')])

def extract_title_desktop(html):
    """Extract title/lines from desktop novel sites (quanwenyuedu, tmwxw, bxwx9)."""
    # Try article body pattern (quanwenyuedu)
    m = re.search(r'<div[^>]*?class="[^"]*articlebody[^"]*"[^>]*>(.*?)</div>', html, re.S)
    if m:
        text = re.sub(r'<[^>]*>', '\n', m.group(1))
        text = re.sub(r'<br\s*/?>', '\n', text)
        return clean_text(text)
    # Try article tag pattern (tmwxw)
    m = re.search(r'<article[^>]*>(.*?)</article>', html, re.S)
    if m:
        text = re.sub(r'<[^>]*>', '\n', m.group(1))
        text = re.sub(r'<br\s*/?>', '\n', text)
        lines = clean_text(text)
        return lines
    # Try div#content
    m = re.search(r'<div[^>]*?id="content"[^>]*>(.*?)</div>', html, re.S)
    if m:
        text = re.sub(r'<[^>]*>', '\n', m.group(1))
        lines = clean_text(text)
        if len(lines) > 5:
            return lines
    # Generic fallback
    clean = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', html, flags=re.S)
    clean = re.sub(r'<[^>]*>', '\n', clean)
    lines = [l.strip() for l in clean.split('\n') if l.strip() and len(l.strip()) > 15]
    return lines

def extract_title_mobile(html):
    """Extract title/lines from mobile sites (yqxxs)."""
    # Try common content div patterns
    for pattern in [
        r'<div[^>]*?id="(?:nr|content|chapter|txt|text)"[^>]*>(.*?)</div>',
        r'<div[^>]*?class="[^"]*(?:nr|content|read-content)[^"]*"[^>]*>(.*?)</div>',
    ]:
        m = re.search(pattern, html, re.S)
        if m:
            text = re.sub(r'<[^>]*>', '\n', m.group(1))
            lines = clean_text(text)
            if len(lines) > 5:
                return lines
    # Full page text fallback
    clean = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', html, flags=re.S)
    clean = re.sub(r'<[^>]*>', '\n', clean)
    lines = [l.strip() for l in clean.split('\n') if l.strip() and len(l.strip()) > 15]
    return lines

# ─────────────────────────────────────────────────
# CRAWLER 1: quanwenyuedu.io
# ─────────────────────────────────────────────────
def crawl_quanwenyuedu(limit_novels=30, limit_chapters=10):
    """Discover novels from quanwenyuedu.io and scrape chapters."""
    DOMAIN = "https://www.quanwenyuedu.io"
    novels_db = load_novels()
    existing_slugs = {n.get('source_slug', n['slug']) for n in novels_db}
    new_count = 0
    total_chapters = 0

    # Category pages
    discovered = []
    for cat_id in range(1, 13, 2):  # 1,3,5,7,9,11
        html = fetch_curl(f"{DOMAIN}/c/{cat_id}.html")
        if not html:
            continue
        novel_links = re.findall(r'href="(/n/[^"]+?/)"[^>]*>(.{2,120})</a>', html)
        for url, raw_title in novel_links:
            title_full = re.sub(r'<[^>]*>', '', raw_title).strip()
            # Extract title and author if present
            title = title_full
            author = "Unknown"
            m = re.match(r'(.+?)[/\s]*作者[:：]?\s*(.+)', title_full)
            if m:
                title, author = m.group(1).strip(), m.group(2).strip()
            source_slug = url.strip('/').split('/')[-1]
            if source_slug in existing_slugs:
                continue
            discovered.append({
                "title": title,
                "author": author,
                "source_slug": source_slug,
                "source_url": f"{DOMAIN}{url}",
                "domain": "quanwenyuedu.io",
            })
        time.sleep(0.5)

    print(f"quanwenyuedu: discovered {len(discovered)} new novels")
    discovered = discovered[:limit_novels]

    for novel in discovered:
        if new_count >= limit_novels:
            break
        slug = slugify(novel['title'])
        # Check if slug already exists
        if any(n['slug'] == slug for n in novels_db):
            print(f"  Skip {slug} (exists)")
            continue

        # Get chapter list
        ch_html = fetch_curl(f"{DOMAIN}/n/{novel['source_slug']}/xiaoshuo.html")
        if not ch_html:
            continue
        chapter_links = re.findall(r'href="(\d+\.html)"[^>]*>(.{1,80})</a>', ch_html)
        if not chapter_links:
            chapter_links = re.findall(r'href="(/n/[^/]+/\d+\.html)"[^>]*>(.{1,80})</a>', ch_html)

        chapter_count = len(chapter_links)
        print(f"  {novel['title']}: {chapter_count} chapter links → {slug}")

        # Add novel
        new_novel = {
            "slug": slug,
            "title": novel['title'],
            "author": novel['author'],
            "category": "Wuxia & Xianxia",
            "source_url": novel['source_url'],
            "source_slug": novel['source_slug'],
            "source_domain": novel['domain'],
            "cover_url": f"/covers/{slug}.svg",
            "totalChapters": chapter_count,
            "available_chapters": 0,
            "description": f"Discover {novel['title']} — explore the full collection online.",
        }
        novels_db.append(new_novel)

        # Scrape chapters
        chapters_scraped = 0
        for ch_url, ch_title_raw in chapter_links[:limit_chapters]:
            ch_title = re.sub(r'<[^>]*>', '', ch_title_raw).strip()
            ch_html_page = fetch_curl(f"{DOMAIN}/n/{novel['source_slug']}/{ch_url}")
            if not ch_html_page:
                continue
            lines = extract_title_desktop(ch_html_page)
            if not lines or len(lines) < 3:
                continue
            chapters_scraped += 1
            save_chapter(slug, chapters_scraped, ch_title, lines)
            time.sleep(0.3)

        new_novel['available_chapters'] = chapters_scraped
        print(f"    scraped {chapters_scraped} chapters")
        new_count += 1
        total_chapters += chapters_scraped
        save_novels(novels_db)
        time.sleep(0.5)

    return new_count, total_chapters


# ─────────────────────────────────────────────────
# CRAWLER 2: tmwxw.net  
# ─────────────────────────────────────────────────
def crawl_tmwxw(limit_novels=30, limit_chapters=15):
    """Discover novels from tmwxw.net (笔趣阁 type) and scrape chapters."""
    DOMAIN = "https://www.tmwxw.net"
    novels_db = load_novels()
    existing_sources = {n.get('source_url', '') for n in novels_db}
    existing_slugs = {n['slug'] for n in novels_db}
    new_count = 0
    total_chapters = 0

    discovered = []
    # Try category pages and homepage
    urls_to_check = [f"{DOMAIN}/list1/", f"{DOMAIN}/list2/", f"{DOMAIN}/list3/",
                     f"{DOMAIN}/list4/", f"{DOMAIN}/list5/", f"{DOMAIN}/list6/",
                     f"{DOMAIN}/list7/", DOMAIN]

    for cat_url in urls_to_check:
        html = fetch(cat_url)
        if not html:
            continue
        # tmwxw format: /id_title/
        novel_links = re.findall(r'href="(/\d+_\d+/)"[^>]*>(.{2,120})</a>', html)
        for url, raw_title in novel_links:
            title = re.sub(r'<[^>]*>', '', raw_title).strip()
            if len(title) < 2:
                continue
            source_url = f"{DOMAIN}{url}"
            if source_url in existing_sources:
                continue
            # Extract book ID
            m = re.search(r'/(\d+)_\d+/', url)
            book_id = m.group(1) if m else ""
            discovered.append({
                "title": title,
                "source_url": source_url,
                "book_id": book_id,
                "domain": "tmwxw.net",
            })
        time.sleep(0.5)

    print(f"tmwxw: discovered {len(discovered)} new novels")
    # Deduplicate
    seen_urls = set()
    unique = []
    for d in discovered:
        if d['source_url'] not in seen_urls:
            seen_urls.add(d['source_url'])
            unique.append(d)
    discovered = unique[:limit_novels]

    for novel in discovered:
        if new_count >= limit_novels:
            break
        slug = slugify(novel['title'])
        if slug in existing_slugs:
            continue

        # Get detail page for chapters
        html = fetch(novel['source_url'])
        if not html:
            continue

        # Find author
        author = "Unknown"
        author_m = re.search(r'作者[:：]\s*(?:<[^>]*>)*([^<\n]{2,30})', html)
        if author_m:
            author = author_m.group(1).strip()

        # Find chapter links - tmwxw format: /id_title/chapterid.html
        base = novel['source_url'].rstrip('/')
        chapter_links = re.findall(rf'href="({re.escape(base)}/\d+\.html)"[^>]*>(.{{1,100}})</a>', html)
        if not chapter_links:
            # Try relative links
            m = re.search(r'/(\d+_\d+)/', novel['source_url'])
            if m:
                prefix = m.group(1)
                chapter_links_raw = re.findall(rf'href="(/{prefix}/\d+\.html)"[^>]*>(.{{1,100}})</a>', html)
                chapter_links = [(f"{DOMAIN}{url}", t) for url, t in chapter_links_raw]

        chapter_count = len(chapter_links)
        print(f"  {novel['title']}: {chapter_count} chapters → {slug}")

        if chapter_count == 0:
            continue

        # Determine category
        category = "Fantasy"
        for kw in ['都市', '现代', '言情', '职场', '总裁']:
            if kw in html[:2000]:
                category = "Urban"
                break
        for kw in ['玄幻', '仙侠', '修真', '修仙', '神话']:
            if kw in html[:2000]:
                category = "Xianxia"
                break

        new_novel = {
            "slug": slug,
            "title": novel['title'],
            "author": author,
            "category": category,
            "source_url": novel['source_url'],
            "source_domain": novel['domain'],
            "cover_url": f"/covers/{slug}.svg",
            "totalChapters": chapter_count,
            "available_chapters": 0,
            "description": f"Read {novel['title']} online free.",
        }
        novels_db.append(new_novel)

        # Scrape chapters
        chapters_scraped = 0
        for ch_url, ch_title_raw in chapter_links[:limit_chapters]:
            ch_title = re.sub(r'<[^>]*>', '', ch_title_raw).strip()
            ch_html_page = fetch(ch_url, headers=HEADERS_DESKTOP_REFERER)
            if not ch_html_page:
                continue
            lines = extract_title_desktop(ch_html_page)
            if not lines or len(lines) < 3:
                continue
            chapters_scraped += 1
            save_chapter(slug, chapters_scraped, ch_title, lines)
            time.sleep(0.3)

        new_novel['available_chapters'] = chapters_scraped
        print(f"    scraped {chapters_scraped} chapters")
        new_count += 1
        total_chapters += chapters_scraped
        save_novels(novels_db)
        time.sleep(0.5)

    return new_count, total_chapters


# ─────────────────────────────────────────────────
# CRAWLER 3: yqxxs.com (mobile)
# ─────────────────────────────────────────────────
def crawl_yqxxs(limit_novels=20, limit_chapters=10):
    """Discover novels from yqxxs.com mobile and scrape chapters."""
    DOMAIN = "https://m.yqxxs.com"
    novels_db = load_novels()
    existing_slugs = {n['slug'] for n in novels_db}
    new_count = 0
    total_chapters = 0

    # Discover from mobile homepage and list pages
    discovered = []
    for page in ["", "list.html", "top.html"]:
        url = f"{DOMAIN}/{page}" if page else DOMAIN
        html = fetch(url, headers=HEADERS_MOBILE, encoding='gbk')
        if not html:
            continue
        # yqxxs format: book_ID.html (may be absolute or relative)
        book_links = re.findall(r'(?:https?://m\.yqxxs\.com)?/?(book_(\d+)\.html)', html)
        for url_part, book_id in book_links:
            source_url = url_part if 'http' in url_part else f"{DOMAIN}/{url_part}"
            if source_url in [d['source_url'] for d in discovered]:
                continue
            # Extract title: text after <br/> inside same <a> tag
            title = 'Unknown'
            title_ctx = re.search(rf'(?:book_{book_id}\.html)[^"]*"[^>]*>(.+?)</a>', html, re.S)
            if title_ctx:
                raw = title_ctx.group(1)
                # Remove image tag
                raw = re.sub(r'<img[^>]*>', '', raw)
                raw = re.sub(r'<br\s*/?>', ' ', raw)
                raw = re.sub(r'<[^>]*>', '', raw).strip()
                if raw and len(raw) > 1:
                    title = raw
            if title == 'Unknown' or 'index' in title.lower():
                continue
            discovered.append({
                "title": title,
                "book_id": book_id,
                "source_url": source_url,
                "domain": "yqxxs.com",
            })
        time.sleep(0.5)

    print(f"yqxxs: discovered {len(discovered)} new novels")
    # Deduplicate by book_id
    seen_ids = set()
    unique = []
    for d in discovered:
        if d['book_id'] not in seen_ids:
            seen_ids.add(d['book_id'])
            unique.append(d)
    discovered = unique[:limit_novels]

    for novel in discovered:
        if new_count >= limit_novels:
            break
        slug = slugify(novel['title'])
        if slug in existing_slugs:
            continue

        html = fetch(novel['source_url'], headers=HEADERS_MOBILE, encoding='gbk')
        if not html:
            continue

        author = "Unknown"
        author_m = re.search(r'作者[:：]\s*(.{2,30})[<\n]', html)
        if author_m:
            author = author_m.group(1).strip()

        # Chapter pages pattern
        chapter_links = re.findall(rf'(?:https?://m\.yqxxs\.com)?/?(book_{novel["book_id"]}/\d+\.html)', html)
        chapter_count = len(chapter_links)
        print(f"  {novel['title']}: {chapter_count} chapter pages → {slug}")

        if chapter_count == 0:
            continue

        category = "Romance"  # yqxxs is primarily romance/言情

        new_novel = {
            "slug": slug,
            "title": novel['title'],
            "author": author,
            "category": category,
            "source_url": novel['source_url'],
            "source_domain": novel['domain'],
            "cover_url": f"/covers/{slug}.svg",
            "totalChapters": chapter_count,
            "available_chapters": 0,
            "description": f"Read {novel['title']} online free.",
        }
        novels_db.append(new_novel)

        chapters_scraped = 0
        for ch_url in chapter_links[:limit_chapters]:
            ch_url_full = ch_url if 'http' in ch_url else f"{DOMAIN}/{ch_url}"
            ch_html_page = fetch(ch_url_full, headers=HEADERS_MOBILE, encoding='gbk')
            if not ch_html_page:
                continue
            lines = extract_title_mobile(ch_html_page)
            if not lines or len(lines) < 3:
                continue
            chapters_scraped += 1
            save_chapter(slug, chapters_scraped, f"Page {chapters_scraped}", lines)
            time.sleep(0.3)

        new_novel['available_chapters'] = chapters_scraped
        print(f"    scraped {chapters_scraped} chapters")
        new_count += 1
        total_chapters += chapters_scraped
        save_novels(novels_db)
        time.sleep(0.5)

    return new_count, total_chapters


# ─────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    sites = sys.argv[1:] if len(sys.argv) > 1 else ['quanwenyuedu', 'tmwxw', 'yqxxs']
    
    print("=" * 60)
    print("Multi-site Novel Crawler")
    print("=" * 60)
    
    total_novels = 0
    total_chapters = 0
    
    if 'quanwenyuedu' in sites:
        print("\n📚 Crawling quanwenyuedu.io...")
        n, c = crawl_quanwenyuedu(limit_novels=20, limit_chapters=10)
        total_novels += n
        total_chapters += c
        print(f"  → {n} novels, {c} chapters")
    
    if 'tmwxw' in sites:
        print("\n📚 Crawling tmwxw.net...")
        n, c = crawl_tmwxw(limit_novels=25, limit_chapters=15)
        total_novels += n
        total_chapters += c
        print(f"  → {n} novels, {c} chapters")
    
    if 'yqxxs' in sites:
        print("\n📚 Crawling yqxxs.com...")
        n, c = crawl_yqxxs(limit_novels=15, limit_chapters=10)
        total_novels += n
        total_chapters += c
        print(f"  → {n} novels, {c} chapters")
    
    print(f"\n{'=' * 60}")
    print(f"TOTAL: {total_novels} new novels, {total_chapters} new chapters")
    
    # Final stats
    novels_db = load_novels()
    import glob as g
    ch_files = g.glob(f"{CHAPTERS_DIR}/*/ch-*.json")
    print(f"Database: {len(novels_db)} novels, {len(ch_files)} total chapter files")
    print(f"{'=' * 60}")
