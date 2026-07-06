#!/usr/bin/env python3
"""Multi-source novel scraper: 0515red.com + akswu.com + bxwx9.org"""
import re, ssl, json, os, time, sys
from urllib.request import Request, urlopen
from urllib.parse import urljoin
from html.parser import HTMLParser
from collections import OrderedDict

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data/chapters')
os.makedirs(DATA_DIR, exist_ok=True)

def detect_encoding_from_bytes(raw):
    """Detect encoding from HTML meta tags in raw bytes"""
    # Try to find charset in the first 4096 bytes
    head = raw[:4096]
    for enc in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
        try:
            head.decode(enc)
        except:
            continue
    # Try utf-8 first, then gbk
    try:
        head.decode('utf-8')
        # Check if there's a meta charset tag
        h = head.decode('utf-8', errors='replace')
        m = re.search(r'<meta[^>]*charset[="\s]+([^"\s>]+)', h, re.I)
        if m and 'gb' in m.group(1).lower():
            return m.group(1)
        if m:
            return m.group(1)
        return 'utf-8'
    except:
        pass
    # Fallback: try gbk for Chinese sites
    try:
        h = head.decode('gbk')
        if re.search(r'[\u4e00-\u9fff]{4,}', h):
            return 'gbk'
    except:
        pass
    return 'utf-8'

def fetch(url, headers=None, timeout=20, use_curl=False):
    """Fetch URL, using curl for servers that block Python's urllib"""
    if use_curl:
        import subprocess
        ua = (headers or {}).get('User-Agent', 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36')
        ref = (headers or {}).get('Referer', '')
        cmd = ['curl', '-sL', '--max-time', str(timeout), '-H', f'User-Agent: {ua}',
               '-H', 'Accept-Language: zh-CN,zh;q=0.9', '--insecure']
        if ref:
            cmd += ['-H', f'Referer: {ref}']
        cmd.append(url)
        r = subprocess.run(cmd, capture_output=True, timeout=timeout+5)
        encoding = detect_encoding_from_bytes(r.stdout)
        return r.stdout.decode(encoding, errors='replace')
    
    h = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        **(headers or {})
    }
    req = Request(url, headers=h)
    resp = urlopen(req, context=ssl_ctx, timeout=timeout)
    return resp.read().decode(guess_encoding(resp), errors='replace')

def guess_encoding(resp):
    ct = resp.headers.get('Content-Type', '')
    m = re.search(r'charset=([^\s;]+)', ct)
    return m.group(1) if m else 'utf-8'

def strip_tags(html):
    return re.sub(r'<[^>]*>', '', html).strip()

# ─── 0515red.com ──────────────────────────────────────
def scrape_0515red_novel_list(page=1):
    """Scrape novel listing pages from 0515red.com"""
    novels = {}
    try:
        url = f'http://www.0515red.com/class/{page}_1/' 
        html = fetch(url, headers={'User-Agent': 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36'}, use_curl=True)
        # Find novel links: //www.0515red.com/rd/{id}/ or /rd/{id}/
        for m in re.finditer(r'<a[^>]*href="(?:https?:)?(?://www\.0515red\.com)?(/rd/(\d+)/?)"[^>]*>(.*?)</a>', html):
            href, nid, title_text = m.group(1), m.group(2), m.group(3).strip()
            title = strip_tags(title_text)
            if title and len(title) > 2 and 'img' not in m.group(0).lower():
                novels[nid] = {'title': title, 'source': '0515red', 'url': f'http://www.0515red.com{href}'}
    except Exception as e:
        print(f'  ⚠️ 0515red page {page}: {e}')
    return novels

def scrape_0515red_chapters(novel_id):
    """Get chapter list for a 0515red novel"""
    try:
        url = f'http://www.0515red.com/rd/{novel_id}/'
        html = fetch(url, headers={'User-Agent': 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36'}, use_curl=True)
        title = re.search(r'<title>(.*?)(?:_|最新章节|全文|免费|言情中文网)', html)
        novel_title = title.group(1).strip() if title else novel_id
        
        chapters = OrderedDict()
        for m in re.finditer(r'"(?:https?:)?//www\.0515red\.com(/rd/\d+/(\d+)\.html)"[^>]*>(.*?)</a>', html):
            chap_url, chap_id, chap_title = m.group(1), m.group(2), m.group(3).strip()
            ct = strip_tags(chap_title)
            if ct and ct not in chapters:
                chapters[chap_id] = {'title': ct, 'url': f'http://www.0515red.com{chap_url}'}
        return novel_title, chapters
    except Exception as e:
        print(f'  ❌ 0515red chapters: {e}')
        return novel_id, {}

def scrape_0515red_content(url):
    """Extract chapter content from 0515red"""
    try:
        html = fetch(url, headers={'User-Agent': 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36'}, use_curl=True)
        content = re.search(r'<div[^>]*id="content"[^>]*>(.*?)</div>', html, re.S)
        if content:
            text = content.group(1)
            text = re.sub(r'<br\s*/?>', '\n', text)
            text = strip_tags(text)
            text = re.sub(r'\n{3,}', '\n\n', text)
            return text.strip()
    except Exception as e:
        print(f'    ❌ content: {e}')
    return None

# ─── akswu.com ────────────────────────────────────────
def scrape_akswu_novel_list():
    """Scrape novel listings from akswu.com"""
    novels = {}
    try:
        html = fetch('https://www.akswu.com/')
        for m in re.finditer(r'href="(/akshtml(\d+)\.html)"[^>]*>(.*?)</a>', html):
            href, nid, title_text = m.group(1), m.group(2), m.group(3).strip()
            title = strip_tags(title_text)
            if title and len(title) > 2 and 'html' not in title.lower():
                novels[nid] = {'title': title, 'source': 'akswu', 'url': f'https://www.akswu.com{href}'}
    except Exception as e:
        print(f'  ⚠️ akswu index: {e}')
    return novels

def scrape_akswu_catalog(novel_id):
    """Get full chapter catalog from akswu.js")
    The catalog is loaded via javascript, but we can construct URLs from the detail page"""
    try:
        url = f'https://www.akswu.com/akshtml{novel_id}.html'
        html = fetch(url)
        title = re.search(r'<title>(.*?)(?:全文|_爱看书屋)', html)
        novel_title = title.group(1).strip() if title else novel_id
        
        # Find chapters in the page
        chapters = OrderedDict()
        for m in re.finditer(r'href="(/aks/\d+/(\d+)/(\d+)\.html)"[^>]*>(.*?)</a>', html):
            chap_url, prefix, chap_id, chap_title = m.group(1), m.group(2), m.group(3), m.group(4).strip()
            ct = strip_tags(chap_title)
            if ct and ct not in chapters and '开始阅读' not in ct:
                chapters[chap_id] = {
                    'title': ct, 
                    'url': f'https://www.akswu.com{chap_url}',
                    'prefix': prefix
                }
        return novel_title, chapters
    except Exception as e:
        print(f'  ❌ akswu catalog: {e}')
        return novel_id, {}

def scrape_akswu_catalog_via_api(novel_id):
    """Try the catalog JS API"""
    try:
        html = fetch(f'https://www.akswu.com/akshtml{novel_id}.html')
        # The catalog link often has an onclick handler
        catalog_url = re.search(r"a_catalog.*?['\"](/[^'\"]+)['\"]", html)
        if catalog_url:
            cat_html = fetch(f'https://www.akswu.com{catalog_url.group(1)}')
            chapters = OrderedDict()
            for m in re.finditer(r'href="(/aks/\d+/(\d+)/(\d+)\.html)"[^>]*>(.*?)</a>', cat_html):
                chap_url, prefix, chap_id, chap_title = m.group(1), m.group(2), m.group(3), m.group(4).strip()
                ct = strip_tags(chap_title)
                if ct and ct not in chapters:
                    chapters[chap_id] = {
                        'title': ct,
                        'url': f'https://www.akswu.com{chap_url}',
                        'prefix': prefix
                    }
            return chapters
    except Exception as e:
        print(f'    ⚠️ akswu API catalog: {e}')
    return {}

def scrape_akswu_content(url):
    """Extract chapter content from akswu"""
    try:
        html = fetch(url)
        content = re.search(r'<article[^>]*id="article"[^>]*>(.*?)</article>', html, re.S)
        if content:
            text = content.group(1)
            text = re.sub(r'<br\s*/?>', '\n', text)
            text = strip_tags(text)
            text = re.sub(r'\n{3,}', '\n\n', text)
            return text.strip()
    except Exception as e:
        print(f'    ❌ content: {e}')
    return None

# ─── bxwx9.org ────────────────────────────────────────
def scrape_bxwx9(page=1):
    """Scrape bxwx9 listing pages for novel links (URL: /b/{group}/{novel}/)"""
    novels = {}
    try:
        urls = [f'https://www.bxwx9.org/list{i}/' for i in range(1, 9)]
        if page == 1:
            urls.append('https://www.bxwx9.org/')
        for url in urls:
            try:
                html = fetch(url, use_curl=True)
                for m in re.finditer(r'href="(/b/(\d+)/(\d+)/)"', html):
                    href, group_id, nid = m.group(1), m.group(2), m.group(3)
                    # Title is in the text after the href, inside <a> tag
                    after = html[m.end():m.end()+200]
                    title_m = re.search(r'[^<>]*>([^<]{2,60})</a>', after)
                    title = strip_tags(title_m.group(1).strip()) if title_m else ''
                    if title and len(title) > 2:
                        key = str(nid)
                        if key not in novels:
                            novels[key] = {
                                'title': title, 'source': 'bxwx9',
                                'url': f'https://www.bxwx9.org{href}',
                                'group_id': group_id
                            }
            except Exception as e:
                pass
    except Exception as e:
        print(f'  ⚠️ bxwx9: {e}')
    return novels

def scrape_bxwx9_chapters(novel_id, group_id=None):
    """Get chapters from bxwx9 novel directory page"""
    try:
        if group_id:
            url = f'https://www.bxwx9.org/b/{group_id}/{novel_id}/'
        else:
            url = f'https://www.bxwx9.org/b/{novel_id}/'
        html = fetch(url, use_curl=True)
        title = re.search(r'<title>(.*?)(?:目录|最新章节|全文|_笔下文学)', html)
        novel_title = title.group(1).strip() if title else novel_id

        chapters = OrderedDict()
        for m in re.finditer(r'href="(/b/\d+/(\d+)/(\d+)\.html)"[^>]*>(.*?)</a>', html):
            chap_url, c_novel_id, chap_id, chap_title_raw = m.group(1), m.group(2), m.group(3), m.group(4)
            ct = strip_tags(chap_title_raw)
            if ct and ct not in chapters:
                chapters[chap_id] = {
                    'title': ct,
                    'url': f'https://www.bxwx9.org{chap_url}'
                }
        return novel_title, chapters
    except Exception as e:
        print(f'  ❌ bxwx9 chapters: {e}')
        return novel_id, {}

def scrape_bxwx9_content(url):
    """Extract chapter content from bxwx9 (<article> tag)"""
    try:
        html = fetch(url, use_curl=True)
        content = re.search(r'<article[^>]*>(.*?)</article>', html, re.S)
        if not content:
            return None
        text = content.group(1)
        text = re.sub(r'<br\s*/?>', '\n', text)
        text = re.sub(r'<p[^>]*>', '\n', text)
        text = re.sub(r'</p>', '', text)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'&nbsp;', ' ', text)
        text = re.sub(r'^\s*第\(\d+/\d+\)页\s*', '', text, flags=re.M)
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'一秒记住.*?免费阅读！', '', text)
        text = re.sub(r'请收藏本站.*', '', text)
        return text.strip()
    except Exception as e:
        print(f'    ❌ content: {e}')
    return None
# ─── Storage ──────────────────────────────────────────
def slugify(title):
    return re.sub(r'[^\w\u4e00-\u9fff]+', '_', title).strip('_')[:40]

def save_chapter(novel_title, novel_slug, chap_num, chap_title, content_zh, source, source_url):
    """Save chapter as JSON"""
    novel_dir = os.path.join(DATA_DIR, novel_slug)
    os.makedirs(novel_dir, exist_ok=True)
    
    fp = os.path.join(novel_dir, f'ch-{int(chap_num):04d}.json')
    
    data = {}
    if os.path.exists(fp):
        with open(fp) as f:
            try: data = json.load(f)
            except: pass
    
    data['title'] = chap_title
    data['novel_title'] = novel_title
    data['chapter_number'] = int(chap_num)
    data['content_zh'] = content_zh
    data['content_en'] = data.get('content_en') or content_zh  # Chinese goes live directly
    data['source'] = source
    data['source_url'] = source_url
    
    with open(fp, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return fp

# ─── Main scraper ─────────────────────────────────────
def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', choices=['0515red','akswu','bxwx9','all'], default='all')
    parser.add_argument('--max-novels', type=int, default=20)
    parser.add_argument('--max-chapters', type=int, default=30)
    parser.add_argument('--delay', type=float, default=1.0)
    args = parser.parse_args()
    
    all_novels = {}
    
    if args.source in ('0515red', 'all'):
        print('🔍 0515red.com...')
        # Categories: 1=玄幻 2=武侠 3=都市 4=历史 5=网游 6=科幻 7=灵异 8=言情 9=其他
        for cat in range(1, 10):
            n = scrape_0515red_novel_list(cat)
            all_novels.update(n)
            if n:
                print(f'  cat {cat}: {len(n)} novels')
            time.sleep(0.3)
    
    if args.source in ('akswu', 'all'):
        print('\n🔍 akswu.com...')
        n = scrape_akswu_novel_list()
        all_novels.update(n)
        print(f'  found {len(n)} novels')
    
    if args.source in ('bxwx9', 'all'):
        print('\n🔍 bxwx9.org...')
        for p in range(1, 4):
            n = scrape_bxwx9(p)
            all_novels.update(n)
        
    print(f'\n📚 Total unique novels: {len(all_novels)}')
    
    # Filter novels we already have chapters for
    existing = set()
    for d in os.listdir(DATA_DIR):
        dp = os.path.join(DATA_DIR, d)
        if os.path.isdir(dp):
            ch_count = len([f for f in os.listdir(dp) if f.endswith('.json')])
            if ch_count >= args.max_chapters:
                existing.add(d)
    
    # Scrape chapters
    total_new = 0
    count = 0
    
    for nid, info in list(all_novels.items()):
        if count >= args.max_novels:
            break
        
        slug = slugify(info['title'])
        
        # Skip if already has enough chapters
        if slug in existing:
            continue
        
        count += 1
        source = info['source']
        title_short = info["title"][:40]
        print(f'\n[{count}] 📖 {title_short} ({source}:{nid})')
        
        # Get chapter list
        if source == '0515red':
            novel_title, chapters = scrape_0515red_chapters(nid)
        elif source == 'akswu':
            novel_title, chapters = scrape_akswu_catalog(nid)
            if len(chapters) < 5:
                extra = scrape_akswu_catalog_via_api(nid)
                chapters.update(extra)
        else:  # bxwx9
            group_id = info.get('group_id')
            novel_title, chapters = scrape_bxwx9_chapters(nid, group_id)
        
        print(f'  Title: {novel_title[:40]}')
        print(f'  Chapters found: {len(chapters)}')
        
        if not chapters:
            continue
        
        # Sort and limit chapters
        sorted_chaps = sorted(chapters.items(), key=lambda x: int(x[0]))
        
        novel_new = 0
        for chap_id, chap_info in sorted_chaps[:args.max_chapters]:
            chap_num = str(len([f for f in os.listdir(os.path.join(DATA_DIR, slug)) if f.endswith('.json')]) + 1) if os.path.exists(os.path.join(DATA_DIR, slug)) else chap_id
            
            # Get content
            if source == '0515red':
                content = scrape_0515red_content(chap_info['url'])
            elif source == 'akswu':
                content = scrape_akswu_content(chap_info['url'])
            else:
                content = scrape_bxwx9_content(chap_info['url'])
            
            if content and len(content) > 100:
                fp = save_chapter(
                    novel_title, slug, novel_new + 1,
                    chap_info['title'], content,
                    source, chap_info['url']
                )
                novel_new += 1
                total_new += 1
                ct_short = chap_info['title'][:30]
                print(f'    ✅ ch{novel_new:03d} [{len(content)}c] {ct_short}')
            else:
                print(f'    ⚠️ ch skip [{len(content) if content else 0}c]')
            
            time.sleep(args.delay)
        
        print(f'  📊 {novel_title[:30]}: {novel_new} new chapters saved')
    
    print(f'\n🎉 Total new chapters: {total_new}')
    normalize_novels_json()


# ── novels.json normalization ────────────────────────────────
def normalize_novels_json():
    """Auto-fix missing fields: title_en, author_en, zone, genre, etc."""
    import shutil
    novels_file = os.path.join(DATA_DIR, 'novels.json')
    if not os.path.exists(novels_file):
        return
    
    with open(novels_file, 'r', encoding='utf-8') as f:
        novels = json.load(f)
    
    CAT_MAP = {'Xianxia':'xianxia','Xuanhuan':'xuanhuan','Wuxia':'wuxia',
               'Urban':'urban','Sci-Fi':'scifi','Fantasy':'fantasy',
               'Romance':'romance','History':'history','Classic':'classic'}
    
    fixed = 0
    for n in novels:
        changed = False
        if not n.get('title_en'):
            n['title_en'] = n.get('title') or n.get('slug','')
            changed = True
        if not n.get('author_en'):
            n['author_en'] = n.get('author') or 'Unknown'
            changed = True
        if not n.get('description_en'):
            desc = n.get('description','')
            n['description_en'] = desc if desc else f'A captivating novel.'
            changed = True
        if not n.get('genre') or n['genre'] in ('','?'):
            n['genre'] = CAT_MAP.get(n.get('category',''), 'fantasy')
            changed = True
        if not n.get('zone') or n['zone'] == '?':
            n['zone'] = 'vip'
            changed = True
        if not n.get('tags'):
            n['tags'] = [n['genre']]
            changed = True
        if not n.get('rating'):
            n['rating'] = 4.0
            changed = True
        if not n.get('status'):
            n['status'] = 'ongoing'
            changed = True
        if 'is_adult' not in n:
            n['is_adult'] = False
            changed = True
        if not n.get('total_chapters'):
            n['total_chapters'] = n.get('totalChapters', 1)
            changed = True
        if not n.get('readers'):
            n['readers'] = 0
            changed = True
        if changed:
            fixed += 1
    
    if fixed:
        shutil.copy(novels_file, novels_file + '.bak')
        with open(novels_file, 'w', encoding='utf-8') as f:
            json.dump(novels, f, ensure_ascii=False, indent=2)
        print(f'📋 Normalized {fixed} novel entries in novels.json')


if __name__ == '__main__':
    main()
