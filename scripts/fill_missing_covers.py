#!/usr/bin/env python3.10
import json, os, hashlib, glob

novels = json.load(open('data/novels.json'))
missing = [n for n in novels if not n.get('cover_ext')]
print(f'Generating gradient SVG covers for {len(missing)} books...')

def slug_to_colors(s):
    h = hashlib.md5(s.encode()).hexdigest()
    return f'#{h[0:6]}', f'#{h[6:12]}'

for n in missing:
    s = n['slug']
    c1, c2 = slug_to_colors(s)
    title = n.get('title_clean', n.get('title_en', n.get('title', s)))[:20]
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="300" height="450" viewBox="0 0 300 450">
  <defs>
    <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{c1}"/>
      <stop offset="100%" style="stop-color:{c2}"/>
    </linearGradient>
  </defs>
  <rect width="300" height="450" fill="url(#g)"/>
  <text x="150" y="200" text-anchor="middle" fill="white" font-family="sans-serif" font-size="16" opacity="0.9">{title}</text>
</svg>'''
    with open(f'public/covers/{s}.svg', 'w') as f:
        f.write(svg)
    n['cover_ext'] = 'svg'
    n['cover_url'] = f'/covers/{s}.svg'

json.dump(novels, open('data/novels.json', 'w'), ensure_ascii=False, indent=2)
manifest = {n['slug']: '.' + n['cover_ext'] for n in novels if n.get('cover_ext')}
json.dump(manifest, open('data/cover-manifest.json', 'w'), ensure_ascii=False, indent=2)

from collections import Counter
print(f"cover_ext: {dict(Counter(n.get('cover_ext','-') for n in novels))}")
print(f"files: {len(glob.glob('public/covers/*.svg'))} svg, {len(glob.glob('public/covers/*.jpg'))} jpg")
