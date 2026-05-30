#!/usr/bin/env python3
"""
Biquge Crawler - 笔趣阁中文小说爬虫
抓取中文原文 → 保存到 data/chapters/<slug>/chapter-N.json
配合 translate_pipeline.py 做中→英翻译

用法:
  python3 scripts/biquge_crawler.py search "不败战神"
  python3 scripts/biquge_crawler.py info "不败战神"
  python3 scripts/biquge_crawler.py pull "不败战神" --start 1 --end 20
  python3 scripts/biquge_crawler.py pull-by-id 5226 --start 1 --end 20
"""

import argparse
import json
import re
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path
from html import unescape

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CHAPTERS_DIR = DATA_DIR / "chapters"
NOVELS_FILE = DATA_DIR / "novels.json"

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
BASE_URL = "https://www.ibiquge.com"


# ── HTTP ────────────────────────────────────────────────────────
def http_get(url, timeout=15):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        # Try to detect encoding
        content = r.read()
        # Try UTF-8 first, then GBK
        for enc in ("utf-8", "gbk", "gb2312", "gb18030"):
            try:
                return content.decode(enc)
            except:
                continue
        return content.decode("utf-8", errors="replace")


# ── Search ──────────────────────────────────────────────────────
def search_novels(query):
    """Search biquge via search.php"""
    q = urllib.parse.quote(query.encode("gbk", errors="replace"))
    url = f"{BASE_URL}/search.php?q={q}&p=1"
    try:
        html = http_get(url)
    except Exception as e:
        print(f"Search failed: {e}")
        return []

    results = []
    # Pattern: /digit/  as novel URL
    pattern = r'<a[^>]+href="(/(\d+)/)"[^>]*>\s*([^<]+)\s*</a>'
    for m in re.finditer(pattern, html):
        url_path = m.group(1)
        novel_id = m.group(2)
        title = re.sub(r'\s+', ' ', m.group(3)).strip()
        if not any(n['id'] == novel_id for n in results):
            results.append({"id": novel_id, "url": url_path, "title": title})
    return results[:10]


def get_novel_info(novel_id):
    """Get novel info from its index page"""
    url = f"{BASE_URL}/{novel_id}/"
    try:
        html = http_get(url)
    except Exception as e:
        return None, str(e)

    info = {"id": novel_id, "url": url}

    # Title
    m = re.search(r'<title>([^_]+)', html)
    if m:
        info["title"] = m.group(1).strip()

    # Author
    m = re.search(r'作者：<a[^>]*>([^<]+)</a>', html)
    if not m:
        m = re.search(r'作者：([^\n<]+)', html)
    if m:
        info["author"] = m.group(1).strip()

    # Description
    m = re.search(r'简介[：:]\s*</div>\s*<div[^>]*>(.*?)</div>', html, re.DOTALL)
    if not m:
        m = re.search(r'intro[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
    if m:
        desc = re.sub(r'<[^>]+>', '', m.group(1))
        info["description"] = unescape(desc).strip()

    # Chapter list
    chapters = []
    # Pattern: /novel_id/digit+.html
    ch_pattern = rf'/{novel_id}/(\d+)\.html'
    seen = set()
    for m in re.finditer(ch_pattern, html):
        ch_id = m.group(1)
        if ch_id in seen:
            continue
        seen.add(ch_id)
        chapters.append({"id": ch_id, "url": f"{BASE_URL}/{novel_id}/{ch_id}.html"})

    # Also try to get titles
    title_pattern = rf'href="/{novel_id}/(\d+)\.html"[^>]*>([^<]*)</a>'
    ch_titles = {}
    for m in re.finditer(title_pattern, html):
        ch_id = m.group(1)
        ch_title = m.group(2).strip()
        if ch_id not in ch_titles:
            ch_titles[ch_id] = ch_title

    for ch in chapters:
        ch["title"] = ch_titles.get(ch["id"], f"第{ch['id']}章")

    info["chapters"] = chapters
    info["chapter_count"] = len(chapters)
    return info, None


def get_chapter_content(novel_id, chapter_id):
    """Fetch a single chapter's content"""
    url = f"{BASE_URL}/{novel_id}/{chapter_id}.html"
    try:
        html = http_get(url)
    except Exception as e:
        return None, str(e)

    # Extract title
    title = f"Chapter {chapter_id}"
    m = re.search(r'<title>([^_]+)', html)
    if m:
        title = m.group(1).strip()
    # Also try h1
    m = re.search(r'<h1[^>]*>([^<]+)</h1>', html, re.IGNORECASE)
    if m:
        title = m.group(1).strip()

    # Extract content - biquge typically uses <div id="content"> or similar
    content = None
    for pattern in [
        r'<div[^>]+id="content"[^>]*>(.*?)</div>',
        r'<div[^>]+class="[^"]*content[^"]*"[^>]*>(.*?)</div>',
        r'<div[^>]+id="txt"[^>]*>(.*?)</div>',
    ]:
        m = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
        if m:
            raw = m.group(1)
            # Remove script/style tags
            raw = re.sub(r'<script[^>]*>.*?</script>', '', raw, flags=re.DOTALL | re.IGNORECASE)
            raw = re.sub(r'<style[^>]*>.*?</style>', '', raw, flags=re.DOTALL | re.IGNORECASE)
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', '\n', raw)
            text = unescape(text)
            # Clean up
            text = re.sub(r'[\r\f\v]', '', text)
            text = re.sub(r'\n{3,}', '\n\n', text)
            text = re.sub(r'^\s*\n', '', text)
            text = text.strip()
            if len(text) > 200:
                content = text
                break

    if not content:
        # Fallback: just get all text between first <p> and last </p>
        paragraphs = re.findall(r'<p>(.*?)</p>', html, re.DOTALL)
        if paragraphs:
            text = '\n'.join(unescape(re.sub(r'<[^>]+>', '', p)) for p in paragraphs)
            text = re.sub(r'\s+', ' ', text).strip()
            if len(text) > 200:
                content = text

    if not content or len(content) < 100:
        return None, "content too short or not found"

    char_count = len(content)
    return {
        "title": title,
        "content_cn": content,
        "chapter_id": chapter_id,
        "char_count": char_count,
        "url": url,
    }, None


def update_novels_json(novel_id, title, author, chapter_count, description=""):
    """Add/update novel in novels.json"""
    novels = []
    if NOVELS_FILE.exists():
        novels = json.loads(NOVELS_FILE.read_text())

    existing = {n.get("slug"): i for i, n in enumerate(novels)}

    slug = f"biquge-{novel_id}"
    novel_data = {
        "id": len(novels) + 1,
        "slug": slug,
        "title_zh": title,
        "title_en": "",
        "author_zh": author or "",
        "author_en": "",
        "genre": "Chinese Web Novel",
        "tags": ["chinese", "biquge", "to-translate"],
        "is_adult": False,
        "status": "ongoing",
        "rating": 4.0,
        "total_chapters": chapter_count,
        "readers": 0,
        "description_zh": description or "",
        "description_en": "",
        "zone": "vip",
        "source": "biquge",
        "biquge_id": novel_id,
    }

    if slug in existing:
        novels[existing[slug]] = novel_data
    else:
        novels.append(novel_data)

    NOVELS_FILE.write_text(json.dumps(novels, ensure_ascii=False, indent=2))
    print(f"Updated novels.json ({len(novels)} total)")


# ── Commands ────────────────────────────────────────────────────
def cmd_search(args):
    print(f"Searching: {args.query}")
    results = search_novels(args.query)
    if not results:
        print("No results found")
        return 0
    print(f"\nFound {len(results)} results:\n")
    for n in results:
        print(f"  [{n['id']}] {n['title']}")
        print(f"      URL: {BASE_URL}{n['url']}")
        print()
    return 0


def cmd_info(args):
    novel_id = args.id
    print(f"Fetching info for novel {novel_id}...")
    info, error = get_novel_info(novel_id)
    if error:
        print(f"Error: {error}")
        return 1
    print(f"\nTitle: {info.get('title', '?')}")
    print(f"Author: {info.get('author', '?')}")
    print(f"Chapters: {info['chapter_count']}")
    print(f"URL: {info['url']}")
    if info.get('description'):
        print(f"\nDescription: {info['description'][:300]}...")
    print(f"\nFirst 5 chapters:")
    for ch in info['chapters'][:5]:
        print(f"  {ch['id']}: {ch.get('title', '?')}")
    return 0


def cmd_pull(args):
    query = args.query
    # First search if it's not an ID
    if not query.isdigit():
        print(f"Searching for: {query}")
        results = search_novels(query)
        if not results:
            print(f"No results for '{query}'")
            return 1
        novel_id = results[0]["id"]
        print(f"Using: [{novel_id}] {results[0]['title']}")
    else:
        novel_id = query

    # Get novel info
    print(f"\nFetching novel info (ID: {novel_id})...")
    info, error = get_novel_info(novel_id)
    if error:
        print(f"Error: {error}")
        return 1

    title = info.get("title", f"Novel {novel_id}")
    chapters = info["chapters"]
    total = len(chapters)
    print(f"Novel: {title}")
    print(f"Total chapters: {total}")

    # Determine range
    start = max(0, (args.start or 1) - 1)
    end = min(total, args.end or min(total, start + 49))
    print(f"Pulling chapters {start + 1}-{end}...\n")

    # Create output dir
    slug = f"biquge-{novel_id}"
    out_dir = CHAPTERS_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    pulled = 0
    errors = 0
    for i in range(start, end):
        ch = chapters[i]
        ch_id = ch["id"]
        print(f"  [{i+1}/{total}] {ch.get('title', ch_id)}...", end=" ", flush=True)

        data, error = get_chapter_content(novel_id, ch_id)
        if error:
            print(f"❌ {error[:60]}")
            errors += 1
            time.sleep(0.5)
            continue

        # Save
        ch_file = out_dir / f"chapter-{i+1:04d}.json"
        save_data = {
            "num": i + 1,
            "title": data["title"],
            "title_zh": data.get("title", ""),
            "content_cn": data["content_cn"],
            "source": "biquge",
            "biquge_id": novel_id,
            "biquge_chapter_id": ch_id,
            "char_count": data["char_count"],
            "url": data["url"],
            "translated": False,
        }
        ch_file.write_text(json.dumps(save_data, ensure_ascii=False, indent=2))
        pulled += 1
        print(f"✅ {data['char_count']} chars")
        time.sleep(args.delay)

    print(f"\n✅ Done: {pulled} chapters pulled, {errors} errors")

    # Update novels.json
    if pulled > 0:
        update_novels_json(
            novel_id, title,
            info.get("author"),
            total,
            info.get("description", "")
        )

    return 0


# ── Main ───────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Biquge Novel Crawler")
    parser.add_argument("--delay", type=float, default=0.8, help="Delay between requests")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("search", help="Search novels")
    p.add_argument("query")

    p = sub.add_parser("info", help="Show novel info")
    p.add_argument("id", help="Novel ID (number)")

    p = sub.add_parser("pull", help="Pull chapters")
    p.add_argument("query", help="Novel name or ID")
    p.add_argument("--start", type=int, default=1)
    p.add_argument("--end", type=int, default=None)
    p.add_argument("--delay", type=float, default=0.8)

    args = parser.parse_args()

    if args.cmd == "search":
        return cmd_search(args)
    elif args.cmd == "info":
        return cmd_info(args)
    elif args.cmd == "pull":
        return cmd_pull(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
