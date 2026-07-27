#!/usr/bin/env python3.10
import json, subprocess, re, os, hashlib, glob

novels = json.load(open('data/novels.json'))
missing = [(i,n) for i,n in enumerate(novels) if not n.get('cover_ext')]
print(f'{len(missing)} missing covers')

def dl(url, path, ref=''):
    r = subprocess.run(['curl','-sL','--connect-timeout','8','--max-time','15',
        '-o',path,'-w','%{http_code}|%{size_download}',
        '-A','Mozilla/5.0 (Windows NT 10.0; Win64; x64)'],
        capture_output=True, timeout=20)
    raw = r.stdout.decode()
    try:
        code_str, size_str = raw.split('|')
        code = int(code_str)
        size = int(size_str)
        return code == 200 and size > 500 and os.path.getsize(path) > 500
    except:
        return False

def fetch(url):
    r = subprocess.run(['curl','-sL','--connect-timeout','6','--max-time','10',
        '-A','Mozilla/5.0','--compressed',url], capture_output=True, timeout=15)
    if r.returncode!=0: return None
    for e in ['utf-8','gbk','gb2312']:
        try: return r.stdout.decode(e)
        except: pass
    return r.stdout.decode('utf-8','ignore')

for idx, n in missing:
    slug = n['slug']; url = n.get('source_url',''); domain = n.get('source_domain','')
    path = f'public/covers/{slug}.jpg'; ok = False
    
    if domain=='23wx.io':
        m = re.search(r'/book/(\d+)', url)
        if m: ok = dl(f'https://www.23wx.io/img/{m.group(1)}.jpg', path, 'https://www.23wx.io/')
    elif domain=='biquge8.xyz':
        html = fetch(url)
        if html:
            m = re.search(r'cdn\.biquge\d+\.top/[^\"\s]+\.(?:jpg|png)', html)
            if m:
                cover = 'https://' + m.group(0)
                ok = dl(cover, path, url)
    
    if ok:
        n['cover_ext']='jpg'; n['cover_url']=f'/covers/{slug}.jpg'
        print(f'  {slug[:45]}: jpg OK')
    else:
        n['cover_ext']='svg'; n['cover_url']=f'/covers/{slug}.svg'
        h = hashlib.md5(slug.encode()).hexdigest()
        c1,c2 = f'#{h[0:6]}',f'#{h[6:12]}'
        t = n.get('title_clean',n.get('title_en',n.get('title',slug)))[:20]
        with open(f'public/covers/{slug}.svg','w') as f:
            f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="300" height="450"><defs><linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:{c1}"/><stop offset="100%" style="stop-color:{c2}"/></linearGradient></defs><rect width="300" height="450" fill="url(#g)"/><text x="150" y="200" text-anchor="middle" fill="white" font-family="sans-serif" font-size="16" opacity="0.9">{t}</text></svg>')
        print(f'  {slug[:45]}: svg')

json.dump(novels, open('data/novels.json','w'), ensure_ascii=False, indent=2)
manifest = {n['slug']:'.'+n['cover_ext'] for n in novels if n.get('cover_ext')}
json.dump(manifest, open('data/cover-manifest.json','w'), ensure_ascii=False, indent=2)
from collections import Counter
print(f"Done. cover_ext: {dict(Counter(n.get('cover_ext','-') for n in novels))}")
