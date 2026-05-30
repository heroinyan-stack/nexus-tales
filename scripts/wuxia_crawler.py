#!/usr/bin/env python3
"""
WuxiaWorld Crawler - Pull English-translated chapters
Uses WuxiaWorld's API + abbreviation pattern for chapter URLs

Usage:
  python3 scripts/wuxia_crawler.py search "martial god"
  python3 scripts/wuxia_crawler.py pull "martial-god-asura" --start 1 --end 10
  python3 scripts/wuxia_crawler.py pull "battle-through-the-heavens" --start 1 --end 5
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CHAPTERS_DIR = DATA_DIR / "chapters"
NOVELS_FILE = DATA_DIR / "novels.json"

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
API_BASE = "https://www.wuxiaworld.com/api"

# ── HTTP helpers ───────────────────────────────────────────────
def http_get(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8")


def http_json(url):
    return json.loads(http_get(url))


# ── WuxiaWorld API ─────────────────────────────────────────────
def search_novels(query, limit=20):
    """Search WuxiaWorld novels via API"""
    q = urllib.parse.quote(query)
    url = f"{API_BASE}/novels/search?query={q}&limit={limit}"
    data = http_json(url)
    return data.get("items", [])


def build_chapter_url(novel, chapter_num):
    """Build chapter URL using abbreviation pattern"""
    slug = novel['slug']
    abbr = novel.get('abbreviation', '').lower()
    if not abbr:
        abbr = ''.join(w[0] for w in slug.split('-')).lower()
    return f"https://www.wuxiaworld.com/novel/{slug}/{abbr}-chapter-{chapter_num}"


def get_chapter(novel, chapter_num):
    """Fetch and parse a single chapter"""
    url = build_chapter_url(novel, chapter_num)
    try:
        html = http_get(url, timeout=15)
    except Exception as e:
        return None, str(e), url
    
    # Extract title
    title_match = re.search(r'<title>([^<]+)</title>', html)
    chapter_title = title_match.group(1) if title_match else f"Chapter {chapter_num}"
    if " – " in chapter_title:
        chapter_title = chapter_title.split(" – ", 1)[-1].strip()
    elif " - " in chapter_title:
        chapter_title = chapter_title.split(" - ", 1)[-1].strip()
    
    # Extract content - try multiple patterns
    content = None
    for pattern in [
        r'<div[^>]*class="[^"]*chapter-content[^"]*"[^>]*>(.*?)</div>',
        r'<div[^>]*class="[^"]*fr-view[^"]*"[^>]*>(.*?)</div>',
        r'<div[^>]*id="chapter-content"[^>]*>(.*?)</div>',
    ]:
        m = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
        if m:
            raw = m.group(1)
            # Strip HTML tags
            import html as html_mod
            content = html_mod.unescape(re.sub(r'<[^>]+>', '', raw))
            content = re.sub(r'\s+', ' ', content).strip()
            break
    
    if not content or len(content) < 100:
        return None, "content too short or not found", url
    
    word_count = len(content.split())
    return {
        "title": chapter_title,
        "content": content,
        "url": url,
        "chapter_num": chapter_num,
        "word_count": word_count,
    }, None, url


def update_novels_json(slug, name, novel_info):
    """Add/update novel in novels.json"""
    novels = []
    if NOVELS_FILE.exists():
        novels = json.loads(NOVELS_FILE.read_text())
    
    existing = {n.get('slug'): i for i, n in enumerate(novels)}
    
    novel_data = {
        "id": novel_info.get('id', len(novels) + 1),
        "slug": slug,
        "title_en": name,
        "title_zh": novel_info.get('name', name),
        "author_en": "WuxiaWorld",
        "author_zh": "",
        "genre": ", ".join(novel_info.get('genres', [])),
        "tags": novel_info.get('tags', []),
        "is_adult": "Mature" in novel_info.get('genres', []),
        "status": "completed" if "Completed" in novel_info.get('tags', []) else "ongoing",
        "rating": novel_info.get('reviewScore', 0),
        "total_chapters": novel_info.get('chapterCount', 0),
        "readers": 0,
        "description_en": re.sub(r'<[^>]+>', '', novel_info.get('synopsis', ''))[:500],
        "description": "",
        "zone": "vip",
        "source": "wuxiaworld",
        "cover_url": novel_info.get('coverUrl', ''),
        "abbreviation": novel_info.get('abbreviation', ''),
    }
    
    if slug in existing:
        novels[existing[slug]] = novel_data
    else:
        novels.append(novel_data)
    
    NOVELS_FILE.write_text(json.dumps(novels, ensure_ascii=False, indent=2))
    print(f"Updated {NOVELS_FILE}")


# ── Commands ───────────────────────────────────────────────────
def cmd_search(args):
    """Search for novels on WuxiaWorld"""
    print(f"Searching: {args.query}")
    results = search_novels(args.query, args.limit)
    
    if not results:
        print("No results found")
        return 0
    
    print(f"\nFound {len(results)} novels:\n")
    for n in results:
        print(f"  [{n['id']}] {n['name']}")
        print(f"      Slug: {n['slug']}")
        print(f"      Abbr: {n.get('abbreviation', '?')}")
        print(f"      Chapters: {n.get('chapterCount', '?')}")
        print(f"      Genres: {', '.join(n.get('genres', []))}")
        print()
    
    return 0


def cmd_pull(args):
    """Pull chapters from WuxiaWorld"""
    # Search for the novel
    query = args.novel.replace('-', ' ')
    results = search_novels(query, limit=5)
    
    if not results:
        print(f"❌ Novel '{args.novel}' not found on WuxiaWorld")
        return 1
    
    # Find best match
    n = results[0]
    slug = n['slug']
    name = n['name']
    abbr = n.get('abbreviation', '')
    total = n.get('chapterCount', 0)
    
    print(f"📖 {name}")
    print(f"   ID: {n['id']}")
    print(f"   Slug: {slug}")
    print(f"   Abbreviation: {abbr}")
    print(f"   Total chapters: {total}")
    print(f"   URL pattern: .../{slug}/{abbr.lower()}-chapter-{{N}}")
    
    # Determine range
    start = args.start or 1
    end = args.end or min(total, start + 49)
    end = min(end, total)
    
    print(f"\n📥 Pulling chapters {start}-{end}...\n")
    
    # Create output dir
    out_dir = CHAPTERS_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    
    pulled = 0
    errors = 0
    consecutive_errors = 0
    
    for ch_num in range(start, end + 1):
        print(f"  [{ch_num}/{total}]", end=" ", flush=True)
        
        ch_data, error, url = get_chapter(n, ch_num)
        
        if error:
            print(f"❌ {error[:60]}")
            errors += 1
            consecutive_errors += 1
            if consecutive_errors >= 5:
                print(f"\n  ⛔ Too many consecutive errors, stopping")
                break
            time.sleep(0.5)
            continue
        
        consecutive_errors = 0
        
        # Save
        ch_file = out_dir / f"chapter-{ch_num}.json"
        save_data = {
            "num": ch_num,
            "title": ch_data["title"],
            "content_en": ch_data["content"],
            "source": "wuxiaworld",
            "url": url,
            "word_count": ch_data["word_count"],
        }
        ch_file.write_text(json.dumps(save_data, ensure_ascii=False, indent=2))
        pulled += 1
        print(f"✅ {ch_data['word_count']} words")
        
        time.sleep(args.delay)
    
    print(f"\n✅ Done: {pulled} chapters pulled, {errors} errors")
    
    # Update novels.json
    if pulled > 0:
        update_novels_json(slug, name, n)
    
    return 0


def cmd_batch(args):
    """Pull first N chapters for top novels"""
    novels = [
        "martial-god-asura",
        "battle-through-the-heavens",
        "against-the-gods",
        "i-shall-seal-the-heavens",
        "a-will-eternal",
        "renegade-immortal",
    ]
    
    for novel in novels[:args.limit]:
        print(f"\n{'='*60}")
        print(f"Processing: {novel}")
        print('='*60)
        try:
            cmd_pull(argparse.Namespace(
                novel=novel,
                start=1,
                end=args.chapters,
                delay=args.delay
            ))
        except Exception as e:
            print(f"Failed: {e}")
        time.sleep(2)
    
    return 0


# ── Main ───────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="WuxiaWorld Crawler")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between requests")
    sub = parser.add_subparsers(dest="cmd", required=True)
    
    p = sub.add_parser("search", help="Search novels")
    p.add_argument("query")
    p.add_argument("--limit", type=int, default=10)
    
    p = sub.add_parser("pull", help="Pull chapters")
    p.add_argument("novel", help="Novel slug or search term")
    p.add_argument("--start", type=int, default=1)
    p.add_argument("--end", type=int, default=None)
    p.add_argument("--delay", type=float, default=1.0)
    
    p = sub.add_parser("batch", help="Batch pull multiple novels")
    p.add_argument("--limit", type=int, default=3, help="Number of novels")
    p.add_argument("--chapters", type=int, default=10, help="Chapters per novel")
    p.add_argument("--delay", type=float, default=1.0)
    
    args = parser.parse_args()
    
    if args.cmd == "search":
        return cmd_search(args)
    elif args.cmd == "pull":
        return cmd_pull(args)
    elif args.cmd == "batch":
        return cmd_batch(args)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
