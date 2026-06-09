#!/usr/bin/env python3
"""Bulk pull chapters from bxwx9.org for all novels with bxwx9 source_url.
Target: 30+ chapters per novel. Skips existing chapters.
Handles multi-page chapters and cleans junk footer text.
"""
import json, os, re, time, ssl
import urllib.request
from pathlib import Path

CHAPTERS_DIR = Path(__file__).parent.parent / 'data' / 'chapters'
NOVELS_JSON = Path(__file__).parent.parent / 'data' / 'novels.json'
TARGET_CHAPTERS = 30
DELAY = 0.5  # seconds between requests
PULL_AT_MOST = 5  # max new chapters per novel per run (to be polite)

ssl_ctx = ssl.create_default_context()
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
}

def fetch(url, referer=None):
    """Fetch URL with retries."""
    hdr = dict(HEADERS)
    if referer:
        hdr['Referer'] = referer
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=hdr)
            resp = urllib.request.urlopen(req, context=ssl_ctx, timeout=15)
            return resp.read().decode('utf-8', errors='replace')
        except Exception as e:
            if attempt == 2:
                raise
            time.sleep(1)

def clean_text(raw):
    """Clean chapter text: remove script/style tags, HTML, junk footer."""
    # Remove scripts
    text = re.sub(r'<script[^>]*>.*?</script>', '', raw, flags=re.S)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.S)

    # Remove JS function calls
    text = re.sub(r'\b\w+\([^)]*\)\s*;?', '', text)

    # Replace common entities
    text = text.replace('&nbsp;', '').replace('&lt;', '<').replace('&gt;', '>')

    # Remove HTML tags (preserving line breaks for p/br)
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.I)
    text = re.sub(r'</?p[^>]*>', '\n', text, flags=re.I)
    text = re.sub(r'<[^>]+>', '', text)

    # Clean whitespace
    lines = []
    for line in text.split('\n'):
        line = line.strip()
        if line:
            lines.append(line)

    text = '\n'.join(lines)

    # Remove junk footers
    junk_patterns = [
        r'本站所有收录的内容均来自互联网.*?删除。',
        r'笔下文学网.*?小说迷。',
        r'努力打造最干净的阅读环境.*?',
        r'请记住本书首发域名.*',
        r'天才一秒记住本站地址.*',
        r'手机用户请浏览.*阅读.*',
        r'温馨提示.*?bsp;.*',
        r'如果您喜欢.*?推荐给您的书友.*',
        r'--&gt;&gt;.*',
        r'第\(\d+/\d+\)页',
    ]
    for pat in junk_patterns:
        text = re.sub(pat, '', text, flags=re.S)

    # Clean up extra blank lines
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    return '\n'.join(lines)

def extract_content(html):
    """Extract chapter content from bxwx9 chapter page."""
    # Find the content area
    idx = html.find('关灯')
    if idx < 0:
        idx = html.find('content')
    if idx < 0:
        # Fallback: use the whole page, clean it
        main = html
    else:
        main = html[idx:idx + 10000]

    return clean_text(main)

def get_chapter_list(novel_url):
    """Fetch list of chapter URLs from bxwx9 novel detail page."""
    html = fetch(novel_url)
    # Find chapter links: href="/b/133/133515/274620.html"
    links = re.findall(
        r'href="(/b/\d+/\d+/\d+\.html)"[^>]*>([^<]+)<',
        html
    )
    return [(novel_url.rstrip('/').split('/b/')[0] + url, title.strip()) for url, title in links]

def get_chapter_num(chapter_url):
    """Extract chapter number from URL or title."""
    # bxwx9 URLs are like .../274620.html - we use index
    # Title often has 第X章 prefix
    return None  # We'll use order

def existing_chapters(slug):
    """Return set of existing chapter numbers for a slug."""
    ch_dir = CHAPTERS_DIR / slug
    if not ch_dir.exists():
        return set(), 0
    existing = set()
    for f in ch_dir.glob('*.json'):
        m = re.search(r'ch(?:apter)?-?(\d+)', f.stem)
        if m:
            existing.add(int(m.group(1)))
    return existing, len(existing)

def main():
    with open(NOVELS_JSON) as f:
        novels = json.load(f)

    # Find bxwx9 novels
    bxwx9_novels = [
        (n['slug'], n['source_url'], n.get('title', n['slug']))
        for n in novels
        if n.get('source_url') and 'bxwx9' in n['source_url']
    ]

    total_pulled = 0
    for slug, src_url, title in bxwx9_novels:
        existing, count = existing_chapters(slug)
        if count >= TARGET_CHAPTERS:
            print(f"  SKIP {title}: already {count} ch")
            continue

        try:
            chapters = get_chapter_list(src_url)
        except Exception as e:
            print(f"  FAIL {title}: list error: {e}")
            continue

        print(f"\n  {title}: {count} ch → pulling (found {len(chapters)} on site)")

        pulled = 0
        for i, (ch_url, ch_title) in enumerate(chapters, 1):
            if pulled >= PULL_AT_MOST:
                break
            if i in existing:
                continue

            try:
                html = fetch(ch_url, referer=src_url)
                text = extract_content(html)

                if len(text) < 50:
                    continue

                # Save chapter
                ch_dir = CHAPTERS_DIR / slug
                ch_dir.mkdir(parents=True, exist_ok=True)

                ch_data = {
                    "num": i,
                    "title": ch_title or f"Chapter {i}",
                    "slug": slug,
                    "lines": [l for l in text.split('\n') if l.strip()]
                }

                ch_path = ch_dir / f'ch-{i}.json'
                with open(ch_path, 'w', encoding='utf-8') as f:
                    json.dump(ch_data, f, ensure_ascii=False)

                existing.add(i)
                pulled += 1
                total_pulled += 1
                print(f"    ch-{i}: {len(text)} chars ✓")

                time.sleep(DELAY)

            except Exception as e:
                print(f"    ch-{i}: ERROR {e}")
                continue

        print(f"    → +{pulled} chapters (now {count + pulled})")

    print(f"\n✅ Total pulled: {total_pulled} chapters")

if __name__ == '__main__':
    main()
