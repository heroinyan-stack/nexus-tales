#!/usr/bin/env python3
"""
quanwenyuedu.io scraper — scrape chapters from www.quanwenyuedu.io
Pattern: /n/{slug}/xiaoshuo.html → chapter list → /n/{slug}/{N}.html → content
"""
import json, os, re, sys, time, urllib.request, ssl

BASE = "https://www.quanwenyuedu.io"
CHARS_PER_RUN = 5  # chapters per novel per run (conservative to avoid rate limiting)
ctx = ssl.create_default_context()

def fetch(url, retries=2):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml',
                'Accept-Language': 'zh-CN,zh;q=0.9',
            })
            resp = urllib.request.urlopen(req, context=ctx, timeout=15)
            return resp.read().decode('utf-8', errors='replace')
        except Exception as e:
            if attempt == retries - 1:
                print(f"  ❌ failed: {e}")
                return None
            time.sleep(2)
    return None

def parse_chapter_list(html):
    """Extract chapter URLs from xiaoshuo.html page"""
    links = re.findall(r'<a\s[^>]*href="(\d+\.html)"[^>]*>(.*?)</a>', html)
    return [{"num": int(m[0].replace('.html','')), "title": re.sub(r'<[^>]+>', '', m[1]).strip(), "url": m[0]} for m in links]

def parse_content(html):
    """Extract title + body content from chapter page"""
    # Title
    t = re.search(r'<h1>([^<]+)</h1>', html)
    title = t.group(1).strip() if t else ''

    # Content
    body = re.search(r'<body[^>]*>(.*?)</body>', html, re.S)
    if not body:
        return title, ''
    text = body.group(1)
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.S)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.S)
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'<[^>]+>', '\n', text)

    lines = [l.strip() for l in text.split('\n') if l.strip()]
    # Skip nav lines
    skip = {'返回','首页','上一章','下一章','加入书签','推荐本书','最新网址','手机阅读','电脑版'}
    content_lines = []
    started = False
    for l in lines:
        if title and title[:6] in l:
            started = True
            continue
        if started:
            if l in skip or '全文阅读' in l or 'www.quanwenyuedu.io' in l or 'https://' in l:
                continue
            if len(l) > 15:
                content_lines.append(l)
    return title, '\n\n'.join(content_lines)

def get_or_create_chapter(slug, ch_num):
    """Check if chapter exists and return its data; return None if we should scrape"""
    d = f'data/chapters/{slug}'
    os.makedirs(d, exist_ok=True)
    for fmt in [f'ch-{ch_num}.json', f'ch-{ch_num:04d}.json']:
        fp = os.path.join(d, fmt)
        if os.path.exists(fp):
            with open(fp) as f:
                ch = json.load(f)
                cn = ch.get('content_zh', '')
                en = ch.get('content_en', '')
                # If has meaningful content, skip
                if len(cn) > 500 or (en and len(en) > 500):
                    return ch
            return None  # exists but thin
    return None  # doesn't exist

def save_chapter(slug, ch_num, ch_title, content_zh):
    d = f'data/chapters/{slug}'
    os.makedirs(d, exist_ok=True)
    ch = {
        "num": ch_num,
        "title": ch_title,
        "slug": slug,
        "content_zh": content_zh,
        "content_en": "",  # to be translated later
        "translated": False
    }
    # Check existing files to determine naming convention
    existing = sorted([f for f in os.listdir(d) if f.endswith('.json')])
    if existing:
        # Use same naming pattern
        fp = os.path.join(d, existing[0].replace(existing[0].split('-')[-1].replace('.json',''), f'{ch_num:04d}.json'))
    else:
        fp = os.path.join(d, f'ch-{ch_num:04d}.json')
    
    # If file exists, preserve any content_en
    if os.path.exists(fp):
        with open(fp) as f:
            old = json.load(f)
            if old.get('content_en') and len(old['content_en']) > 500:
                ch['content_en'] = old['content_en']
                ch['translated'] = True
    
    with open(fp, 'w') as f:
        json.dump(ch, f, ensure_ascii=False, indent=2)
    return fp

def update_novel_meta(slug, title, author, total_chs):
    """Update novels.json with metadata"""
    with open('data/novels.json') as f:
        novels = json.load(f)
    for n in novels:
        if n['slug'] == slug:
            if title and not n.get('title'):
                n['title'] = title
            if author and not n.get('author'):
                n['author'] = author
            if total_chs:
                n['chapter_count'] = total_chs
            break
    with open('data/novels.json', 'w') as f:
        json.dump(novels, f, ensure_ascii=False, indent=2)

def scrape_novel(slug, base_path, max_chapters=None):
    """Scrape a single novel"""
    print(f"\n{'='*60}")
    print(f"📖 {slug}")
    
    # Step 1: Get chapter list
    list_url = f"{BASE}{base_path}xiaoshuo.html"
    print(f"  Chapter list: {list_url}")
    html = fetch(list_url)
    if not html:
        return 0
    
    chapters = parse_chapter_list(html)
    if not chapters:
        print(f"  ⚠️ No chapters found")
        return 0
    
    print(f"  Total chapters: {len(chapters)}")
    
    # Step 2: Get novel metadata from novel page
    novel_url = f"{BASE}{base_path}"
    novel_html = fetch(novel_url)
    author = ''
    novel_title = ''
    if novel_html:
        a = re.search(r'作者[：:]\s*([^<\s]+)', novel_html)
        author = a.group(1).strip() if a else ''
        t = re.search(r'<title>([^_<\s]+)', novel_html)
        novel_title = t.group(1).strip() if t else ''
        if novel_title:
            print(f"  Title: {novel_title}")
        if author:
            print(f"  Author: {author}")
    
    update_novel_meta(slug, novel_title, author, len(chapters))
    
    # Step 3: Determine how many chapters to fetch
    target = max_chapters or CHARS_PER_RUN
    to_fetch = chapters[:target]
    
    scraped = 0
    for ch in to_fetch:
        # Check if already have good content
        existing = get_or_create_chapter(slug, ch['num'])
        if existing:
            continue
        
        ch_url = f"{BASE}{base_path}{ch['url']}"
        print(f"  Fetching ch{ch['num']}: {ch['title'][:30]}...", end=' ')
        ch_html = fetch(ch_url)
        if not ch_html:
            print("❌")
            continue
        
        ch_title, content_zh = parse_content(ch_html)
        if not content_zh or len(content_zh) < 100:
            print(f"  ⚠️ too short ({len(content_zh)} chars)")
            continue
        
        save_chapter(slug, ch['num'], ch_title or ch['title'], content_zh)
        print(f"✅ ({len(content_zh)} chars)")
        scraped += 1
        time.sleep(0.5)  # polite delay
    
    return scraped

def main():
    # Load novels.json, find empty ones from quanwenyuedu.io
    with open('data/novels.json') as f:
        novels = json.load(f)
    
    empty = []
    for n in novels:
        slug = n['slug']
        src = n.get('source_url', '')
        if 'quanwenyuedu.io' not in src:
            continue
        # Check chapter count
        ch_dir = f'data/chapters/{slug}'
        existing_chs = 0
        if os.path.exists(ch_dir):
            for f in os.listdir(ch_dir):
                if f.endswith('.json'):
                    fp = os.path.join(ch_dir, f)
                    try:
                        with open(fp) as fh:
                            ch = json.load(fh)
                            cn = ch.get('content_zh', '')
                            en = ch.get('content_en', '')
                            if len(cn) > 500 or (en and len(en) > 500):
                                existing_chs += 1
                    except: pass
        empty.append({'slug': slug, 'src': src, 'existing': existing_chs, 'title': n.get('title', slug)})
    
    # Sort by existing chapters (none first)
    empty.sort(key=lambda x: x['existing'])
    
    print(f"Found {len(empty)} novels from quanwenyuedu.io")
    print(f"  Zero chapters: {sum(1 for e in empty if e['existing']==0)}")
    print(f"  Some chapters: {sum(1 for e in empty if e['existing']>0)}")
    
    total_scraped = 0
    for i, novel in enumerate(empty):
        # Extract path from source_url
        # e.g. "https://www.quanwenyuedu.io/n/douluodalu/" → "/n/douluodalu/"
        path = novel['src'].replace('https://www.quanwenyuedu.io', '').replace('http://www.quanwenyuedu.io', '')
        if not path.endswith('/'):
            path += '/'
        
        n = scrape_novel(novel['slug'], path)
        total_scraped += n
        print(f"  Scraped {n} new chapters for {novel['slug']} (total: {novel['existing'] + n})")
    
    print(f"\n{'='*60}")
    print(f"✅ Total new chapters scraped: {total_scraped}")

if __name__ == '__main__':
    os.chdir(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(__file__))
    main()
