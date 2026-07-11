#!/usr/bin/env python3
"""Generate SVG cover images for novels that don't have one."""
import json, os, sys, textwrap

PROJECT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
NOVELS_FILE = os.path.join(PROJECT_DIR, 'data', 'novels.json')
COVERS_DIR = os.path.join(PROJECT_DIR, 'public', 'covers')

os.makedirs(COVERS_DIR, exist_ok=True)

COLORS = [
    ("#667eea", "#764ba2"),  # purple
    ("#f093fb", "#f5576c"),  # pink
    ("#4facfe", "#00f2fe"),  # blue
    ("#43e97b", "#38f9d7"),  # green
    ("#fa709a", "#fee140"),  # peach
    ("#a18cd1", "#fbc2eb"),  # lavender
    ("#fccb90", "#d57eeb"),  # orange-purple
    ("#e0c3fc", "#8ec5fc"),  # light purple
    ("#f5576c", "#ff6f00"),  # red-orange
    ("#667eea", "#4facfe"),  # purple-blue
    ("#ff9a9e", "#fecfef"),  # soft pink
    ("#a6c0fe", "#f68084"),  # blue-pink
]

def get_color(slug):
    import hashlib
    h = int(hashlib.md5(slug.encode()).hexdigest()[:8], 16)
    return COLORS[h % len(COLORS)]

def generate_svg(title, slug):
    color1, color2 = get_color(slug)
    # Truncate title for display
    display = title[:20] if title else slug[:20]
    # Wrap long titles
    if len(display) > 12:
        mid = len(display) // 2
        line1 = display[:mid]
        line2 = display[mid:]
        text = f'<text x="200" y="125" text-anchor="middle" font-family="Arial,sans-serif" font-size="24" fill="white" font-weight="bold">{line1}</text>\n      <text x="200" y="160" text-anchor="middle" font-family="Arial,sans-serif" font-size="24" fill="white" font-weight="bold">{line2}</text>'
    else:
        text = f'<text x="200" y="145" text-anchor="middle" font-family="Arial,sans-serif" font-size="28" fill="white" font-weight="bold">{display}</text>'
    
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{color1}"/>
      <stop offset="100%" style="stop-color:{color2}"/>
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#bg)" rx="8"/>
  {text}
  <text x="200" y="240" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="rgba(255,255,255,0.6)">NovelHub</text>
</svg>'''

with open(NOVELS_FILE) as f:
    novels = json.load(f)

existing = set(os.listdir(COVERS_DIR))
created = 0

for n in novels:
    slug = n['slug']
    # Check if any cover exists
    has_cover = any(f'{slug}.{ext}' in existing or f'{slug}-gen.{ext}' in existing
                    for ext in ['svg', 'jpg', 'png'])
    if has_cover:
        continue
    
    title = n.get('title_en') or n.get('title_zh') or slug
    svg = generate_svg(title, slug)
    filepath = os.path.join(COVERS_DIR, f'{slug}-gen.svg')
    with open(filepath, 'w') as f:
        f.write(svg)
    created += 1
    if created % 50 == 0:
        print(f"  Generated {created} covers...")

print(f"✅ Generated {created} new cover SVGs")
print(f"Total covers now: {len(os.listdir(COVERS_DIR))}")
