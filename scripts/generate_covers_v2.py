#!/usr/bin/env python3.10
"""
Generate professional book-cover style SVG covers for all novels.
Fixes: uses real title (never slug), portrait book format, genre-based design.
"""
import json, os, re, hashlib

PROJECT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
NOVELS_FILE = os.path.join(PROJECT_DIR, 'data', 'novels.json')
COVERS_DIR = os.path.join(PROJECT_DIR, 'public', 'covers')
os.makedirs(COVERS_DIR, exist_ok=True)

# Genre → color theme + decorative motif
GENRE_THEMES = {
    'cultivation':   ('#1a2a6c', '#b21f1f', '#fdbb2d', '☯'),
    'xianxia':       ('#2c3e50', '#4ca1af', '#e0eafc', '⚡'),
    'wuxia':         ('#16222a', '#3a6073', '#c0c0c0', '⚔'),
    'fantasy':       ('#41295a', '#2f0743', '#d7a9ff', '✦'),
    'romance':       ('#ff9a9e', '#fecfef', '#ff6a88', '♥'),
    'action':        ('#232526', '#414345', '#f83600', '✦'),
    'adventure':     ('#1e3c72', '#2a5298', '#6dd5ed', '➤'),
    'scifi':         ('#0f2027', '#203a43', '#2c5364', '◈'),
    'horror':        ('#000000', '#434343', '#8e0e00', '☾'),
    'mystery':       ('#232526', '#414345', '#bdc3c7', '?'),
    'historical':    ('#603813', '#b29f94', '#e6dada', '❖'),
    'urban':         ('#283048', '#859398', '#a8c0ff', '⌂'),
    'game':          ('#1d2671', '#c33764', '#ff9966', '◉'),
    'slice_of_life': ('#a8e063', '#56ab2f', '#f9f586', '❀'),
    'comedy':        ('#f7971e', '#ffd200', '#fff200', '☺'),
    'drama':         ('#cb2d3e', '#ef473a', '#ffd194', '♪'),
    'martial_arts':  ('#1f1c2c', '#928dab', '#d7d2cc', '✊'),
    'smut':          ('#8e2de2', '#4a00e0', '#ff6a88', '♥'),
}

DEFAULT_THEME = ('#0f2027', '#203a43', '#2c5364', '✦')

def get_theme(genre):
    g = (genre or '').lower().replace(' ', '_')
    return GENRE_THEMES.get(g, DEFAULT_THEME)

def clean_title(title):
    if not title:
        return ''
    # Remove HTML entities
    title = title.replace('&mdash;', '—').replace('&amp;', '&').replace('&#39;', "'")
    title = re.sub(r'&[a-z]+;', '', title)
    return title.strip()

def wrap_title(title, max_chars=14):
    """Wrap title into lines of ~max_chars for vertical stacking."""
    title = clean_title(title)
    if not title:
        return ['Untitled']
    words = title.split()
    if not words:
        return [title[:max_chars]]
    lines = []
    cur = ''
    for w in words:
        if len(cur) + len(w) + 1 <= max_chars:
            cur = (cur + ' ' + w).strip()
        else:
            if cur:
                lines.append(cur)
            # If single word too long, hard split
            if len(w) > max_chars:
                while len(w) > max_chars:
                    lines.append(w[:max_chars])
                    w = w[max_chars:]
                cur = w
            else:
                cur = w
    if cur:
        lines.append(cur)
    return lines[:6]  # max 6 lines

def generate_cover(novel):
    slug = novel.get('slug', '')
    title = clean_title(novel.get('title_en') or novel.get('title_zh') or '')
    author = clean_title(novel.get('author_en') or novel.get('author_zh') or '')
    genre = novel.get('genre', '')
    c1, c2, c3, motif = get_theme(genre)

    # Hash for subtle variation
    h = int(hashlib.md5(slug.encode()).hexdigest()[:6], 16)

    # Title lines
    lines = wrap_title(title)
    # Vertical centering
    line_height = 34
    total_h = line_height * len(lines)
    start_y = 230 - total_h / 2 + line_height / 2

    title_svg = ''
    for i, line in enumerate(lines):
        y = start_y + i * line_height
        # Alternate subtle style
        title_svg += f'    <text x="200" y="{y:.0f}" text-anchor="middle" font-family="Georgia, serif" font-size="26" fill="#ffffff" font-weight="bold" letter-spacing="0.5">{escape_xml(line)}</text>\n'

    author_display = author[:24] if author else ''

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="560" viewBox="0 0 400 560">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{c1}"/>
      <stop offset="55%" style="stop-color:{c2}"/>
      <stop offset="100%" style="stop-color:{c3}"/>
    </linearGradient>
    <radialGradient id="glow" cx="50%" cy="30%" r="70%">
      <stop offset="0%" style="stop-color:rgba(255,255,255,0.15)"/>
      <stop offset="100%" style="stop-color:rgba(255,255,255,0)"/>
    </radialGradient>
  </defs>
  <rect width="400" height="560" fill="url(#bg)"/>
  <rect width="400" height="560" fill="url(#glow)"/>
  <!-- Decorative top border -->
  <rect x="20" y="20" width="360" height="520" fill="none" stroke="rgba(255,255,255,0.25)" stroke-width="1.5"/>
  <rect x="26" y="26" width="348" height="508" fill="none" stroke="rgba(255,255,255,0.12)" stroke-width="0.8"/>
  <!-- Motif -->
  <text x="200" y="90" text-anchor="middle" font-size="40" fill="rgba(255,255,255,0.18)">{motif}</text>
  <!-- Title -->
{title_svg}  <!-- Separator -->
  <line x1="120" y1="400" x2="280" y2="400" stroke="rgba(255,255,255,0.3)" stroke-width="1"/>
  <!-- Author -->
  <text x="200" y="430" text-anchor="middle" font-family="Georgia, serif" font-size="15" fill="rgba(255,255,255,0.7)" font-style="italic">{escape_xml(author_display)}</text>
  <!-- Footer -->
  <text x="200" y="520" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="rgba(255,255,255,0.45)" letter-spacing="2">NEXUS TALES</text>
</svg>'''

def escape_xml(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

with open(NOVELS_FILE) as f:
    novels = json.load(f)

existing = set(os.listdir(COVERS_DIR))
regenerated = 0
skipped = 0

for n in novels:
    slug = n['slug']
    if not slug:
        continue
    # Only regenerate SVG covers (keep real jpg)
    svg_path = os.path.join(COVERS_DIR, f'{slug}.svg')
    gen_svg_path = os.path.join(COVERS_DIR, f'{slug}-gen.svg')

    # Skip if real jpg exists
    if f'{slug}.jpg' in existing:
        skipped += 1
        continue

    # Regenerate (overwrite existing svg or -gen.svg)
    svg = generate_cover(n)
    target = svg_path if os.path.exists(svg_path) else gen_svg_path
    if not os.path.exists(target):
        target = svg_path
    with open(target, 'w') as f:
        f.write(svg)
    regenerated += 1
    if regenerated % 100 == 0:
        print(f"  Regenerated {regenerated} covers...")

print(f"✅ Regenerated {regenerated} SVG covers (skipped {skipped} jpg)")
print(f"Total covers: {len(os.listdir(COVERS_DIR))}")
