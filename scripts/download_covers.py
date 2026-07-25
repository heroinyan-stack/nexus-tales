#!/usr/bin/env python3.10
"""Fast parallel cover downloader for 4 source domains."""
import json, re, os, subprocess, time, urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

NOVELS_FILE = 'data/novels.json'
COVERS_DIR = 'public/covers'

os.makedirs(COVERS_DIR, exist_ok=True)
novels = json.load(open(NOVELS_FILE))
novel_map = {n['slug']: n for n in novels}
missing = [(i, n) for i, n in enumerate(novels) if not n.get('cover_ext')]
print(f'Target: {len(missing)} covers to download')

def dl(url, path, referer=''):
    cmd = ['curl', '-sL', '--connect-timeout', '8', '--max-time', '15',
           '-o', path, '-w', '%{http_code}|%{size_download}',
           '-A', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36']
    if referer: cmd += ['-e', referer]
    cmd.append(url)
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=20)
        parts = r.stdout.decode().split('|')
        code = int(parts[0]) if parts else 0
        size = int(parts[1]) if len(parts) > 1 else 0
        return code == 200 and size > 500
    except:
        return False

def fetch(url):
    try:
        r = subprocess.run(['curl', '-sL', '--connect-timeout', '6', '--max-time', '10',
            '-A', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            '-H', 'Accept-Language: zh-CN,zh;q=0.9', '-o', '-', url],
            capture_output=True, timeout=15)
        if r.returncode != 0 or not r.stdout: return None
        for enc in ['utf-8','gbk','gb2312','gb18030']:
            try: return r.stdout.decode(enc)
            except: pass
        return r.stdout.decode('utf-8','ignore')
    except: return None

def get_23wx(idx, novel):
    m = re.search(r'/book/(\d+)', novel.get('source_url',''))
    if not m: return None
    url = f"https://www.23wx.io/img/{m.group(1)}.jpg"
    path = os.path.join(COVERS_DIR, f"{novel['slug']}.jpg")
    if dl(url, path, 'https://www.23wx.io/'):
        novel['cover_ext'] = 'jpg'
        novel['cover_url'] = f"/covers/{novel['slug']}.jpg"
        return (idx, novel['slug'], 'OK')
    # Try removing cover_url so it falls back to SVG
    return (idx, novel['slug'], 'FAIL')

def get_html_based(idx, novel, patterns, referer_fn=None):
    source_url = novel.get('source_url', '')
    if not source_url: return (idx, novel['slug'], 'NO_URL')
    html = fetch(source_url)
    if not html: return (idx, novel['slug'], 'HTM_FAIL')
    
    cover_url = None
    for pat in patterns:
        m = re.search(pat, html, re.I)
        if m:
            cover_url = m.group(1)
            break
    if not cover_url: return (idx, novel['slug'], 'NO_MATCH')
    if cover_url.startswith('//'): cover_url = 'https:' + cover_url
    elif cover_url.startswith('/'): cover_url = urllib.parse.urljoin(source_url, cover_url)
    
    path = os.path.join(COVERS_DIR, f"{novel['slug']}.jpg")
    referer = referer_fn(source_url) if referer_fn else source_url
    if dl(cover_url, path, referer):
        novel['cover_ext'] = 'jpg'
        novel['cover_url'] = f"/covers/{novel['slug']}.jpg"
        return (idx, novel['slug'], 'OK')
    return (idx, novel['slug'], 'DL_FAIL')

tasks = []
for idx, novel in missing:
    domain = novel.get('source_domain','')
    if domain == '23wx.io':
        tasks.append((get_23wx, (idx, novel)))
    elif domain == 'jubiquge.com':
        tasks.append((get_html_based, (idx, novel, [r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"', r'<img[^>]*src="(https://img\.cdncnn\.com/[^"]+)"'])))
    elif domain == 'biquge8.xyz':
        tasks.append((get_html_based, (idx, novel, [r'<img[^>]*src="(https://cdn\.biquge\d+\.top/[^"]+\.(?:jpg|png|jpeg|webp))"', r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"'])))
    elif domain == 'quanwenyuedu.io':
        tasks.append((get_html_based, (idx, novel, [r'<img[^>]*src="(https?://img\.c0m\.io/[^"]+\.(?:jpg|png|jpeg|webp))"'])))
    else:
        tasks.append((get_html_based, (idx, novel, [])))

done = {}
with ThreadPoolExecutor(max_workers=10) as ex:
    futures = {ex.submit(fn, *args): args[0] for fn, args in tasks}
    for f in as_completed(futures):
        r = f.result()
        if r:
            idx, slug, status = r
            done[status] = done.get(status, 0) + 1
            if status == 'OK': print(f'  ✅ {slug[:40]}')

# Save
json.dump(novels, open(NOVELS_FILE, 'w'), ensure_ascii=False, indent=2)
manifest = {n['slug']: '.' + n['cover_ext'] for n in novels if n.get('cover_ext')}
json.dump(manifest, open('data/cover-manifest.json', 'w'), ensure_ascii=False, indent=2)

# Report
import glob
jpgs = len(glob.glob(f'{COVERS_DIR}/*.jpg'))
still = len([n for n in novels if not n.get('cover_ext')])
print(f'\nDone: {done}')
print(f'JPG files: {jpgs}  |  Still missing cover_ext: {still}')
