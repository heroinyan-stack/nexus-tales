#!/usr/bin/env python3
"""
Comprehensive Chinese Novel Crawler for Nexus Tales
======================================================
Sources:
  1. bxwx9.org (笔下文学) - primary, no encryption
  2. ssofu.net (全本小说网) - novel discovery only (chapters AES encrypted)
  3. more sources TBD

Output format: data/cn_novels_ssofu.json (novels), data/chapters/{slug}/ch-{N}.json
"""

import json, os, re, time, random
import urllib.request
import ssl

ssl_ctx = ssl.create_default_context()
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}

PROJECT_DIR = '/Users/myan/.qclaw/workspace/novel-site'
DATA_FILE = f'{PROJECT_DIR}/data/novels_ssofu.json'
TOTAL_PAGES = 10  # pages to scan


def fetch(url, referer=None, timeout=15):
    headers = dict(HEADERS)
    if referer:
        headers['Referer'] = referer
    req = urllib.request.Request(url, headers=headers)
    try:
        resp = urllib.request.urlopen(req, context=ssl_ctx, timeout=timeout)
        return resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        print(f'  [ERR] {url[:80]}: {e}')
        return None


def discover_ssofu_novels():
    """Discover novels from ssofu.net listing pages"""
    novels = {}
    
    for page in range(1, TOTAL_PAGES + 1):
        url = f'https://www.ssofu.net/fl/all/{page}/'
        print(f'\n  Page {page}/{TOTAL_PAGES}: {url}')
        
        html = fetch(url)
        if not html:
            continue
        
        # Find novel links: /du_NNNN/
        du_matches = re.findall(r'href="(/du_(\d+)/)"[^>]*>(.*?)</a>', html)
        print(f'    Found {len(du_matches)} novel links')
        
        for url_path, novel_id, raw_title in du_matches:
            if novel_id in novels:
                continue
            clean_title = re.sub(r'<[^>]+>', '', raw_title).strip()
            novels[novel_id] = {
                'id': novel_id,
                'title': clean_title,
                'url': f'https://www.ssofu.net{url_path}',
                'source': 'ssofu.net',
            }
        
        time.sleep(random.uniform(1.5, 3.0))
    
    print(f'\n  Total unique novels: {len(novels)}')
    return novels


def fetch_novel_details(novel):
    """Fetch novel detail page: description, author, chapter list, cover"""
    html = fetch(novel['url'], referer='https://www.ssofu.net/')
    if not html:
        return novel
    
    # Title from meta
    title_m = re.search(r'<meta name="og:title"[^>]*content="(.*?)"', html)
    if not title_m:
        title_m = re.search(r'<title>(.*?)</title>', html)
    if title_m:
        novel['full_title'] = title_m.group(1).strip()
    
    # Description
    desc_m = re.search(r'<meta name="description"[^>]*content="(.*?)"', html)
    if desc_m:
        desc = desc_m.group(1)
        # Remove site name suffix
        desc = re.sub(r'\s*[-_]+\s*.*?小说网.*$', '', desc)
        novel['description'] = desc.strip()
    
    # Author - from const declarations
    author_m = re.search(r"const\s+author\s*=\s*['\"]([^'\"]*)['\"]", html)
    if author_m:
        novel['author'] = author_m.group(1).strip()
    
    # Cover image
    cover_m = re.search(r"const\s+imgurl\s*=\s*['\"]([^'\"]*)['\"]", html)
    if cover_m:
        novel['cover_url'] = cover_m.group(1)
    
    # Category
    cat_m = re.search(r'<a[^>]*href="/fl/[^/]+/"', html)
    if cat_m:
        cat_text = re.search(r'<a[^>]*href="/fl/[^/]+/"[^>]*>(.*?)</a>', html)
        if cat_text:
            novel['category'] = re.sub(r'<[^>]+>', '', cat_text.group(1)).strip()
    
    # Chapter list
    chapters = re.findall(r'href="(/book/\d+/(\d+)\.html)"[^>]*>(.*?)</a>', html)
    seen_chapter_ids = set()
    chapter_list = []
    for url_path, chapter_id, raw_title in chapters:
        if chapter_id in seen_chapter_ids:
            continue
        seen_chapter_ids.add(chapter_id)
        clean_title = re.sub(r'<[^>]+>', '', raw_title).strip()
        chapter_list.append({
            'id': chapter_id,
            'title': clean_title,
            'url': f'https://www.ssofu.net{url_path}',
        })
    
    novel['chapters'] = chapter_list
    novel['total_chapters'] = len(chapter_list)
    
    return novel


def fetch_bxwx9_chapter(url, chapter_num):
    """Fetch chapter content from bxwx9.org (no encryption)"""
    html = fetch(url, referer='https://www.bxwx9.org/')
    if not html:
        return None
    
    # Extract content from div with id="content"
    content_m = re.search(r'<div[^>]*id="content"[^>]*>(.*?)</div>', html, re.S)
    if not content_m:
        print(f'    No #content div found')
        return None
    
    content = content_m.group(1)
    # Clean HTML
    content = re.sub(r'<br\s*/?>', '\n', content)
    content = re.sub(r'<[^>]+>', '', content)
    content = re.sub(r'&nbsp;', ' ', content)
    content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
    
    # Filter site prompts and URLs
    lines = content.split('\n')
    clean_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            clean_lines.append('')
            continue
        # Skip prompts containing specific patterns
        skip_patterns = [
            r'请记住本书首发域名',
            r'笔趣阁.*?网址',
            r'wap\..*?\.org',
            r'一秒记住.*?网址',
            r'手机阅读地址',
            r'本书网址',
            r'浏览阅读地址',
            r'更新最快网址',
            r'最快更新.*?网址',
            r'笔趣阁.*?提醒您',
            r'第一时间更新',
            r'下载.*?阅读',
            r'本章未完.*?下一页',
            r'.*?提示您：看后求收藏',
            r'记住本站网址',
            r'如果您喜欢.*?收藏',
            r'推荐阅读.*?类似.*?小说',
            r'相关推荐',
        ]
        skip = False
        for pat in skip_patterns:
            if re.search(pat, line):
                skip = True
                break
        if not skip:
            clean_lines.append(line)
    
    content = '\n'.join(clean_lines).strip()
    # Remove trailing site URL
    content = re.sub(r'\n\s*www\..*$', '', content)
    
    return content


def save_chapter(slug, chapter_num, title, content_lines):
    """Save chapter as JSON compatible with existing format"""
    chapter_dir = f'{PROJECT_DIR}/data/chapters/{slug}'
    os.makedirs(chapter_dir, exist_ok=True)
    
    # Split content into paragraph lines
    lines = [l.strip() for l in content_lines.split('\n') if l.strip()]
    if not lines:
        return False
    
    chapter = {
        'num': chapter_num,
        'title': title,
        'slug': slug,
        'lines': lines,
    }
    
    filepath = f'{chapter_dir}/ch-{chapter_num}.json'
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(chapter, f, ensure_ascii=False, indent=2)
    return True


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    import sys
    
    args = sys.argv[1:]
    mode = args[0] if args else 'help'
    
    if mode == 'help':
        print(__doc__)
        print("""
Usage:
  python3 scripts/cn_novel_crawler_v2.py discover  - Discover novels from ssofu.net
  python3 scripts/cn_novel_crawler_v2.py details    - Fetch details for discovered novels
  python3 scripts/cn_novel_crawler_v2.py pull [N]   - Pull chapters from bxwx9.org (N chapters per novel, default 3)
  python3 scripts/cn_novel_crawler_v2.py translate  - Translate chapters to English
        """)
    
    elif mode == 'discover':
        print('=== DISCOVERING novels from ssofu.net ===')
        novels = discover_ssofu_novels()
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(novels, f, ensure_ascii=False, indent=2)
        print(f'Saved {len(novels)} novels to {DATA_FILE}')
    
    elif mode == 'details':
        print('=== FETCHING novel details ===')
        if not os.path.exists(DATA_FILE):
            print('No discovered novels. Run "discover" first.')
            sys.exit(1)
        
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            novels = json.load(f)
        
        count = 0
        for novel_id, novel in novels.items():
            if 'author' in novel and novel.get('author'):
                continue  # already fetched
            
            print(f'  [{count+1}/{len(novels)}] {novel["title"][:30]}')
            novels[novel_id] = fetch_novel_details(novel)
            count += 1
            
            if count % 20 == 0:
                with open(DATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump(novels, f, ensure_ascii=False, indent=2)
                print(f'    Saved checkpoint')
            
            time.sleep(random.uniform(1.0, 2.0))
        
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(novels, f, ensure_ascii=False, indent=2)
        print(f'  Done. Details fetched for {count} novels.')
    
    elif mode == 'pull':
        n = int(args[1]) if len(args) > 1 else 3
        print(f'=== PULLING chapters ({n} per novel) ===')
        
        # Load existing novels.json to know what's already in our site
        novels_json_path = f'{PROJECT_DIR}/data/novels.json'
        with open(novels_json_path, 'r', encoding='utf-8') as f:
            existing = json.load(f)
        
        # Also load ssofu discoveries for chapter URLs
        ssofu_novels = {}
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                ssofu_novels = json.load(f)
        
        total_pulled = 0
        for novel in existing:
            slug = novel.get('slug', '')
            source_url = novel.get('source_url', '')
            
            # Determine source
            if 'bxwx9.org' in source_url:
                base_url = source_url.rstrip('/')
                # Count existing chapters
                chapter_dir = f'{PROJECT_DIR}/data/chapters/{slug}'
                existing_chapters = set()
                if os.path.exists(chapter_dir):
                    for fname in os.listdir(chapter_dir):
                        m = re.match(r'ch-(\d+)\.json', fname)
                        if m:
                            existing_chapters.add(int(m.group(1)))
                
                next_ch = max(existing_chapters) + 1 if existing_chapters else 1
                pulled_this = 0
                
                for ch_num in range(next_ch, next_ch + n):
                    ch_url = f'{base_url}{ch_num}.html'
                    print(f'  [{slug[:20]}] Ch {ch_num}: {ch_url}')
                    
                    content = fetch_bxwx9_chapter(ch_url, ch_num)
                    if content and len(content) > 100:
                        save_chapter(slug, ch_num, f'Chapter {ch_num}', content)
                        pulled_this += 1
                    else:
                        print(f'    No content or too short, stopping')
                        break
                    
                    time.sleep(random.uniform(0.5, 1.5))
                
                total_pulled += pulled_this
                if pulled_this:
                    print(f'    => +{pulled_this} chapters')
            
            time.sleep(random.uniform(0.5, 1.0))
        
        print(f'\n  Total chapters pulled: {total_pulled}')
    
    print('\nDone.')
