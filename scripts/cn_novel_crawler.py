#!/usr/bin/env python3
"""
Chinese Novel Crawler — Multi-site unified crawler for small novel sites.
Crawls: bxwx9.org, 1pzw.com, biquge365.net, shuben.org, etc.

Usage:
  python3 cn_novel_crawler.py discover    # Discover novels from category pages
  python3 cn_novel_crawler.py pull SLUG   # Pull chapters for a specific novel
  python3 cn_novel_crawler.py pull-all    # Pull chapters for all discovered novels
  python3 cn_novel_crawler.py stats       # Show novel/chapter stats
"""

import re, json, os, sys, time, hashlib
import urllib.request
import urllib.parse
from pathlib import Path
from html import unescape

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CHAPTERS_DIR = DATA_DIR / "chapters"
NOVELS_FILE = DATA_DIR / "cn_novels.json"  # Separate from existing novels.json
COVERS_DIR = BASE_DIR / "public" / "covers"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Site definitions
SITES = {
    "bxwx9": {
        "name": "笔下文学",
        "domain": "www.bxwx9.org",
        "base": "https://www.bxwx9.org",
        "novel_pattern": r"/b/(\d+)/(\d+)/",  # /b/{cat}/{id}/
        "chapter_pattern": r"/b/\d+/(\d+\.html?)",  # Relative chapter links
        "categories": {f"list{i}": i for i in range(1, 8)},
        "cat_names": {"list1": "玄幻", "list2": "武侠", "list3": "都市", 
                      "list4": "历史", "list5": "网游", "list6": "科幻", "list7": "言情"},
        "referer_needed": False,
        "content_id": "content",
    },
    "1pzw": {
        "name": "一品中文",
        "domain": "www.1pzw.com",
        "base": "https://www.1pzw.com",
        "novel_pattern": r"/(\d+)/(\d+)/",  # /{cat}/{id}/
        "chapter_pattern": r"/\d+/\d+/(\d+\.html?)",
        "categories": {f"list{i}": i for i in range(1, 8)},
        "cat_names": {"list1": "玄幻", "list2": "武侠", "list3": "都市",
                      "list4": "历史", "list5": "网游", "list6": "科幻", "list7": "言情"},
        "referer_needed": True,
        "content_id": "content",
    },
    "biquge365": {
        "name": "笔趣阁360",
        "domain": "www.biquge365.net",
        "base": "https://www.biquge365.net",
        "novel_pattern": r"/(?:new)?book/(\d+)/",
        "chapter_pattern": r"/chapter/(\d+)/",
        "categories": None,  # No category listing, use homepage
        "referer_needed": False,
        "content_id": "content",
    },
    "shuben": {
        "name": "书本网",
        "domain": "www.shuben.org",
        "base": "https://www.shuben.org",
        "novel_pattern": r"/(\d+)/",
        "categories": None,
        "referer_needed": False,
        "content_id": "content",
    },
}


def fetch(url, referer=None, retries=3):
    """Fetch URL with retries and optional referer"""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    if referer:
        req.add_header("Referer", referer)
    
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
                # Try to detect encoding
                charset = resp.headers.get_content_charset()
                if not charset:
                    # Try to find charset in HTML
                    m = re.search(rb'charset=["\']?([^"\'>\s]+)', data[:1024])
                    charset = m.group(1).decode('ascii') if m else 'utf-8'
                return data.decode(charset, errors='replace')
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                print(f"  ⚠️ Failed: {url} → {e}")
                return None


def slugify(title):
    """Create URL-friendly slug from Chinese/English title"""
    # Transliterate common patterns
    slug = title.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')[:80] or hashlib.md5(title.encode()).hexdigest()[:10]


def discover_site(site_key, max_pages=5):
    """Discover novels from a site's category pages"""
    site = SITES[site_key]
    base = site["base"]
    novels = []
    
    if site["categories"]:
        for cat_slug, cat_id in site["categories"].items():
            cat_name = site["cat_names"].get(cat_slug, cat_slug)
            print(f"\n📂 {site['name']} / {cat_name} ({cat_slug})")
            
            for page in range(1, max_pages + 1):
                if page == 1:
                    url = f"{base}/{cat_slug}/"
                else:
                    url = f"{base}/{cat_slug}/{page}.html"
                
                html = fetch(url, referer=base if site["referer_needed"] else None)
                if not html or len(html) < 5000:
                    break
                
                # Extract novel entries: <h3><a href="...">Title</a></h3>
                entries = re.findall(
                    r'<h3>\s*<a\s+href="([^"]+)"[^>]*>([^<]+)</a>\s*</h3>',
                    html
                )
                if not entries:
                    # Fallback: any link with title attribute 
                    entries = re.findall(
                        r'<a[^>]+href="(/b?[^"]*\d+/)"[^>]+title="([^"]+)"',
                        html
                    )
                
                if not entries:
                    break
                
                for href, title in entries:
                    title = unescape(title.strip())
                    full_url = urllib.parse.urljoin(base, href)
                    novels.append({
                        "title": title,
                        "url": full_url,
                        "site": site_key,
                        "category": cat_name,
                    })
                
                print(f"  Page {page}: {len(entries)} novels (total: {len(novels)})")
                time.sleep(0.5)
    else:
        # Homepage-based discovery
        print(f"\n📂 {site['name']} (homepage)")
        html = fetch(base)
        if html:
            entries = re.findall(
                r'<a[^>]+href="(/(?:new)?book/\d+/)[^"]*"[^>]*>([^<]{2,50})</a>',
                html
            )
            for href, title in entries:
                title = unescape(title.strip())
                full_url = urllib.parse.urljoin(base, href)
                novels.append({
                    "title": title,
                    "url": full_url,
                    "site": site_key,
                    "category": "homepage",
                })
            print(f"  Found: {len(novels)} novels")
    
    return novels


def get_novel_meta(site_key, novel_url):
    """Extract metadata from novel page"""
    site = SITES[site_key]
    base = site["base"]
    
    html = fetch(novel_url, referer=base if site["referer_needed"] else None)
    if not html or len(html) < 2000:
        return None
    
    meta = {"source_url": novel_url, "site": site_key}
    
    # Title
    title_m = re.search(r'<title>([^<]+)</title>', html)
    if title_m:
        meta["title_raw"] = unescape(title_m.group(1).strip())
        # Clean: "XXX目录最新章节_XXX全文免费阅读_站点名" → "XXX"
        clean = re.sub(r'目录.*$', '', meta["title_raw"])
        clean = re.sub(r'[_\s]*最新章节.*$', '', clean)
        clean = re.sub(r'全文免费阅读.*$', '', clean)
        meta["title"] = clean.strip()
    
    # Author
    author_m = re.search(r'作者[：:]\s*([^<\n]{2,30})', html)
    if not author_m:
        author_m = re.search(r'<[^>]+>作者[：:]\s*</[^>]+>\s*([^<\n]{2,30})', html)
    if author_m:
        meta["author"] = author_m.group(1).strip()
    
    # Slug
    if "title" in meta:
        meta["slug"] = slugify(meta["title"])
    else:
        # Use URL last segment as slug
        path = urllib.parse.urlparse(novel_url).path.strip('/')
        meta["slug"] = path.replace('/', '-')
    
    # Chapter links - extract and sort by chapter number
    chapter_links = []
    
    # Pattern 1: <a href="...">第X章 Title</a>
    chapters = re.findall(
        r'<a\s+href="([^"]+)"[^>]*>\s*(第[^<]{2,80})\s*</a>',
        html
    )
    
    def ch_sort_key(item):
        """Extract chapter number for sorting"""
        url, title_text = item
        # Try to extract number from Chinese numeral in title
        num_map = {'零':0,'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,
                   '十':10,'百':100,'千':1000,'万':10000}
        m = re.search(r'第([\d零一二三四五六七八九十百千万]+)章', title_text)
        if m:
            num_str = m.group(1)
            if num_str.isdigit():
                return int(num_str)
            # Try Chinese numeral
            result = 0
            unit = 1
            for ch in reversed(num_str):
                if ch in '十百千万':
                    unit = num_map[ch]
                else:
                    result += num_map.get(ch, 0) * unit
                    unit = 1
            return result if result > 0 else 999999
        return 999999
    
    # Sort by chapter number
    chapters.sort(key=ch_sort_key)
    
    for href, cn in chapters:
        full = urllib.parse.urljoin(novel_url, href)
        chapter_links.append({"url": full, "title": cn.strip()})
    
    if not chapter_links:
        # Pattern 2: numbered chapters without 第 prefix
        chapters = re.findall(
            r'<a\s+href="([^"]+)"[^>]*>\s*(\d+[、.\s]+[^<]{5,50})\s*</a>',
            html
        )
        for href, cn in chapters[:100]:
            full = urllib.parse.urljoin(novel_url, href)
            chapter_links.append({"url": full, "title": cn.strip()})
    
    meta["chapters"] = chapter_links
    meta["chapter_count"] = len(chapter_links)
    
    # Cover image
    cover_m = re.search(r'<img[^>]+src="([^"]+)"[^>]*(?:alt="封面"|class="[^"]*cover[^"]*")', html, re.I)
    if not cover_m:
        cover_m = re.search(r'<img[^>]+src="([^"]+s\.jpg)"', html)  # biquge thumbnail pattern
    if cover_m:
        meta["cover_url"] = urllib.parse.urljoin(novel_url, cover_m.group(1))
    
    return meta


def fetch_chapter_page(html):
    """Extract content from a single chapter page HTML"""
    # Strategy 1: <article class="font_max"> (bxwx9, 1pzw)
    m = re.search(r'<article[^>]*class="[^"]*font[^"]*"[^>]*>(.*?)</article>', html, re.S)
    if m:
        return m.group(1)
    
    # Strategy 2: id="content" (older biquge)
    m = re.search(r'<div[^>]+id="content"[^>]*>(.*?)</div>', html, re.S)
    if m and len(m.group(1)) > 100:
        return m.group(1)
    
    # Strategy 3: id="chaptercontent"
    m = re.search(r'<div[^>]+id="chaptercontent"[^>]*>(.*?)</div>', html, re.S)
    if m and len(m.group(1)) > 100:
        return m.group(1)
    
    return None


def fetch_chapter(site_key, chapter_url):
    """Fetch and extract chapter content (handles multi-page)"""
    site = SITES[site_key]
    base = site["base"]
    
    all_lines = []
    title = ""
    
    # Fetch all pages
    page_urls = [chapter_url]
    # Detect pagination pattern: 12794.html → 12794_2.html → 12794_3.html
    page_base = re.sub(r'(\.html?)$', '', chapter_url)
    
    for page_idx in range(10):  # Max 10 pages
        url = page_urls[0] if page_idx == 0 else f"{page_base}_{page_idx + 1}.html"
        
        html = fetch(url, referer=base if site["referer_needed"] else None)
        if not html or len(html) < 300:
            break
        
        # Extract title from first page
        if page_idx == 0:
            title_m = re.search(r'<title>([^<]+)</title>', html)
            if title_m:
                title = unescape(title_m.group(1).strip())
                title = re.sub(r'[_\s]*(?:笔下文学|E品中文|笔趣阁|新笔趣阁).*$', '', title).strip()
        
        # Extract content
        content_html = fetch_chapter_page(html)
        if not content_html:
            if page_idx == 0:
                return None
            break
        
        # Clean HTML
        text = content_html
        text = re.sub(r'<br\s*/?>', '\n', text)
        text = re.sub(r'<p[^>]*>', '\n', text)
        text = re.sub(r'</p>', '', text)
        text = re.sub(r'<[^>]+>', '', text)
        text = unescape(text)
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        text = text.replace('\u3000', '').replace('\xa0', '').replace('&nbsp;', '')
        
        # Remove page markers and ads
        text = re.sub(r'第\(\d+/\d+\)页', '', text)
        text = re.sub(r'(?:记住本站|一秒记住|手机用户|请记住|本章未完|点击下一页|天才一秒).*?\n', '', text)
        text = re.sub(r'.*?(?:笔下文学|E品中文|笔趣阁|顶点小说).*?\n', '', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) > 2]
        all_lines.extend(lines)
        
        # Check if there's a next page in content
        if page_idx > 0 and len(lines) < 5:
            break
    
    return {
        "title": title,
        "lines": all_lines,
        "char_count": sum(len(l) for l in all_lines),
    } if all_lines else None


def cmd_discover():
    """Discover novels from all configured sites"""
    all_novels = []
    
    for site_key in SITES:
        try:
            novels = discover_site(site_key, max_pages=5)
            all_novels.extend(novels)
        except Exception as e:
            print(f"  ❌ {site_key}: {e}")
    
    # Save
    NOVELS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(NOVELS_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_novels, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Saved {len(all_novels)} novels to {NOVELS_FILE}")


def cmd_pull(slug=None):
    """Pull chapters for novel(s)"""
    if not NOVELS_FILE.exists():
        print("❌ No novel database. Run 'discover' first.")
        return
    
    with open(NOVELS_FILE, 'r', encoding='utf-8') as f:
        novels = json.load(f)
    
    if slug:
        novels = [n for n in novels if slugify(n.get("title", "")) == slug or n.get("slug") == slug]
        if not novels:
            print(f"❌ Novel '{slug}' not found")
            return
    
    CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)
    
    for novel in novels[:20]:  # Limit batch size
        title = novel.get("title", novel.get("slug", "unknown"))
        if "slug" not in novel and "title" in novel:
            novel["slug"] = slugify(title)
        slug = novel.get("slug", title)
        
        novel_dir = CHAPTERS_DIR / slug
        novel_dir.mkdir(parents=True, exist_ok=True)
        
        # Get metadata
        print(f"\n📖 {title} ({novel['site']})")
        meta = get_novel_meta(novel["site"], novel["url"])
        if not meta or not meta.get("chapters"):
            print(f"  ⚠️ No chapters found, skipping")
            continue
        
        # Save metadata
        meta_file = novel_dir / "meta.json"
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        
        # Download cover
        if meta.get("cover_url"):
            cover_path = COVERS_DIR / f"{slug}.jpg"
            if not cover_path.exists():
                try:
                    req = urllib.request.Request(meta["cover_url"], headers={"User-Agent": UA})
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        cover_path.write_bytes(resp.read())
                    print(f"  🖼️ Cover saved ({cover_path.stat().st_size}B)")
                except Exception as e:
                    print(f"  ⚠️ Cover failed: {e}")
        
        # Download chapters
        total = len(meta["chapters"])
        existing = set(f.stem for f in novel_dir.glob("*.json"))
        new_count = 0
        
        for i, ch in enumerate(meta["chapters"]):
            ch_num = str(i + 1).zfill(4)
            if ch_num in existing:
                continue
            
            content = fetch_chapter(novel["site"], ch["url"])
            if content and content["char_count"] > 20:
                ch_file = novel_dir / f"chapter-{ch_num}.json"
                with open(ch_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "title": content["title"],
                        "index": i + 1,
                        "lines": content["lines"],
                    }, f, ensure_ascii=False, indent=2)
                new_count += 1
                if new_count % 10 == 0:
                    print(f"  Downloaded: {new_count}/{total}")
            
            time.sleep(0.3)  # Rate limiting
        
        # Copy chapters for site compatibility
        if new_count > 0:
            _export_chapters(slug, novel_dir)
        
        print(f"  ✅ {new_count} new chapters (total: {total})")


def _export_chapters(slug, novel_dir):
    """Export chapters to site-compatible format"""
    export_dir = DATA_DIR / "chapters" / slug
    export_dir.mkdir(parents=True, exist_ok=True)
    
    for ch_file in sorted(novel_dir.glob("chapter-*.json")):
        try:
            shutil = __import__('shutil')
            shutil.copy2(ch_file, export_dir / ch_file.name)
        except Exception:
            pass


def cmd_stats():
    """Show novel/chapter statistics"""
    if NOVELS_FILE.exists():
        with open(NOVELS_FILE, 'r', encoding='utf-8') as f:
            novels = json.load(f)
        print(f"📚 Discovered novels: {len(novels)}")
        for site in SITES:
            count = sum(1 for n in novels if n.get("site") == site)
            print(f"  {site}: {count}")
    
    if CHAPTERS_DIR.exists():
        dirs = [d for d in CHAPTERS_DIR.iterdir() if d.is_dir()]
        total_chs = 0
        for d in dirs:
            ch_count = len(list(d.glob("chapter-*.json")))
            total_chs += ch_count
        print(f"\n📄 Chapters: {total_chs} in {len(dirs)} novels")
        for d in sorted(dirs, key=lambda x: -len(list(x.glob("chapter-*.json"))))[:10]:
            ch_count = len(list(d.glob("chapter-*.json")))
            print(f"  {d.name:40s} {ch_count} chapters")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: cn_novel_crawler.py discover|pull [slug]|pull-all|stats")
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == "discover":
        cmd_discover()
    elif cmd == "pull":
        cmd_pull(sys.argv[2] if len(sys.argv) > 2 else None)
    elif cmd == "pull-all":
        cmd_pull(None)
    elif cmd == "stats":
        cmd_stats()
    else:
        print(f"Unknown command: {cmd}")
