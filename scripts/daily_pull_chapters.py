#!/usr/bin/env python3
"""Daily chapter puller — adds 2-3 chapters to each novel that needs more content."""
import urllib.request, re, json, os, time, socket
from html import unescape

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
socket.setdefaulttimeout(15)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOVELS_FILE = os.path.join(BASE_DIR, 'data/novels.json')
CHAPTERS_DIR = os.path.join(BASE_DIR, 'data/chapters')

def fetch(url, ref=None):
    headers = {'User-Agent': UA}
    if ref: headers['Referer'] = ref
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=15)
    data = resp.read()
    try: return data.decode('utf-8')
    except: return data.decode('gbk', errors='replace')

def extract_content(html):
    m = re.search(r'<article[^>]*>(.*?)</article>', html, re.DOTALL)
    if not m:
        m = re.search(r'<div[^>]*id="content"[^>]*>(.*?)</div>', html, re.DOTALL)
    if m:
        content = re.sub(r'<br\s*/?>', '\n', m.group(1))
        content = re.sub(r'<[^>]+>', '', content)
        content = unescape(content).replace('&nbsp;', ' ')
        return re.sub(r'\n{3,}', '\n\n', content).strip()
    return None

def count_existing_chapters(slug):
    ch_dir = os.path.join(CHAPTERS_DIR, slug)
    if not os.path.exists(ch_dir):
        return 0
    return len([f for f in os.listdir(ch_dir) 
                if (f.startswith('ch-') or f.startswith('chapter-')) and f.endswith('.json')])

with open(NOVELS_FILE) as f:
    novels = json.load(f)

pulled_total = 0
PER_NOVEL = 3  # chapters to pull per novel per run

for novel in novels:
    if novel.get('status') == 'completed':
        continue
    
    slug = novel['slug']
    source_url = novel.get('source_url', '')
    if not source_url or 'bxwx9' not in source_url:
        continue
    
    existing = count_existing_chapters(slug)
    total_avail = novel.get('total_chapters', 0)
    
    # Skip if already have enough chapters
    if existing >= min(total_avail, 50) or existing >= 50:
        continue
    
    print(f'[{novel["id"]}] {novel["title_en"][:35]}: {existing}/{total_avail} ch', end=' ')
    
    try:
        html = fetch(source_url)
        all_refs = re.findall(r'href="([^"]*?(\d+)\.html?)"', html)
        unique = []
        seen = set()
        for link, num_str in all_refs:
            if 'index' in link.lower() or 'book' in link.lower():
                continue
            n = int(num_str)
            if n not in seen:
                seen.add(n)
                unique.append((link, n))
        unique.sort(key=lambda x: x[1])
        
        if not unique:
            print('NO CHAPTERS')
            continue
        
        # Pull next chapters starting from existing+1
        base = '/'.join(source_url.split('/')[:5])
        new_count = 0
        
        for link, num in unique[existing:existing + PER_NOVEL]:
            ch_url = link if link.startswith('http') else (f'https://www.bxwx9.org{link}' if link.startswith('/') else f'{base}/{link}')
            try:
                ch_html = fetch(ch_url, ref=source_url)
                title_match = re.search(r'<h1[^>]*>(.+?)</h1>', ch_html)
                ch_title = unescape(title_match.group(1)).strip() if title_match else f'Chapter {num}'
                content = extract_content(ch_html)
                
                if content:
                    ch_dir = os.path.join(CHAPTERS_DIR, slug)
                    os.makedirs(ch_dir, exist_ok=True)
                    next_num = existing + new_count + 1
                    with open(os.path.join(ch_dir, f'ch-{next_num}.json'), 'w') as f:
                        json.dump({'num': next_num, 'title': ch_title, 'content': content}, f, ensure_ascii=False)
                    new_count += 1
                    pulled_total += 1
                time.sleep(0.5)
            except Exception as e:
                print(f'ERR(ch): {e}', end=' ')
        
        # Update available_chapters in metadata
        novel['available_chapters'] = existing + new_count
        print(f'+{new_count}')
    
    except Exception as e:
        print(f'ERR: {e}')
    
    time.sleep(1)

# Save updated metadata
if pulled_total > 0:
    with open(NOVELS_FILE, 'w') as f:
        json.dump(novels, f, ensure_ascii=False, indent=2)

print(f'\n✅ Pulled {pulled_total} chapters total')
