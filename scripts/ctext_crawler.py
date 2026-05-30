#!/usr/bin/env python3
"""
Ctext.org Classical Chinese Texts Crawler
直接从 ctext.org API 抓取古典中文文本，无认证限制

用法:
  python3 scripts/ctext_crawler.py search 论语
  python3 scripts/ctext_crawler.py list
  python3 scripts/ctext_crawler.py pull 论语 --chapters 1-5
  python3 scripts/ctext_crawler.py pull dao-de-jing
  python3 scripts/ctext_crawler.py batch
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
API_BASE = "https://api.ctext.org"

# ── 预置高质量古典文本清单（无需认证即可拉取） ──────────────────────────────
# key = ctext URN, value = (title_en, title_cn, zone)
CLASSICS = {
    # 四书
    "analects/xue-er":       ("The Analects",           "论语·学而",     "free"),
    "analects/xu-wen":       ("The Analects 2",         "论语·为政",     "free"),
    "analects/ba-yi":        ("The Analects 3",         "论语·八佾",     "free"),
    "analects/li-ren":       ("The Analects 4",         "论语·里仁",     "free"),
    "analects/gong-ye-chang":("The Analects 5",         "论语·公冶长",   "free"),
    "analects/yong-ye":      ("The Analects 6",         "论语·雍也",     "free"),
    "analects/shu-er":       ("The Analects 7",         "论语·述而",     "free"),
    "analects/tai-bo":       ("The Analects 8",         "论语·泰伯",     "free"),
    "analects/zi-han":       ("The Analects 9",         "论语·子罕",     "free"),
    "analects/xiang-dang":   ("The Analects 10",        "论语·乡党",     "free"),
    "analects/xian-jin":     ("The Analects 11",        "论语·先进",     "free"),
    "analects/gu-shan":      ("The Analects 12",        "论语·颜渊",     "free"),
    "analects/zi-lu":        ("The Analects 13",        "论语·子路",     "free"),
    "analects/wei-zheng":    ("The Analects 14",        "论语·卫灵公",   "free"),
    "analects/ji-shi":       ("The Analects 15",        "论语·季氏",     "free"),
    "analects/yang-huo":     ("The Analects 16",        "论语·阳货",     "free"),
    "analects/wei-ling-gong":("The Analects 17",        "论语·微子",     "free"),
    "analects/yao-yue":      ("The Analects 18",        "论语·尧曰",     "free"),
    
    # 道德经
    "dao-de-jing":           ("Dao De Jing",             "道德经",        "free"),
    
    # 三字经
    "three-character-classic":("Three Character Classic", "三字经",        "free"),
    
    # 诗经 (部分章节，无需认证)
    "book-of-songs/shijing-min-yao":("Songs of the People",   "诗经·国风",  "free"),
    "book-of-songs/shijing-ya-song": ("Odes of Shang",         "诗经·商颂",  "free"),
    "book-of-songs/shijing-da-ya-1": ("Great Odes 1",          "诗经·大雅",  "free"),
    "book-of-songs/shijing-xiao-ya": ("Minor Odes",            "诗经·小雅",  "free"),
    
    # 庄子 (需认证，但试拉内篇)
    "zhuangzi/xiao-yao-you": ("Zhuangzi: Happy Excursion",  "庄子·逍遥游",  "free"),
    "zhuangzi/qi-wu-lun":    ("Zhuangzi: Adjustment of Circumstances", "庄子·齐物论", "free"),
    
    # 孙子兵法 (需认证)
    "sunzi/the-strategist":  ("The Art of War",           "孙子兵法",       "free"),
    "sunzi/shiliu-jin":      ("Art of War: 13 Articles",  "孙子兵法十三篇", "free"),
    
    # 荀子
    "xunzi/qiang-guo":       ("Xunzi: Encouraging Learning", "荀子·劝学",   "free"),
    
    # 韩非子
    "hanfeizi/wu-du":        ("Han Feizi: Five Vermin",     "韩非子·五蠹", "free"),
    
    # 大学·中庸
    "da-xue":                ("The Great Learning",         "大学",         "free"),
    "zhong-yong":            ("The Doctrine of the Mean",   "中庸",         "free"),
    
    # 唐诗选 (部分)
    "tang-shi/ti-huai-nong": ("Poems of Li Bai",           "李白诗选",     "free"),
    "tang-shi/ti-huai-shi":  ("Poems of Du Fu",            "杜甫诗选",     "free"),
    
    # 三十六计 (无需认证)
    "thirty-six-stratagems": ("Thirty-Six Stratagems",     "三十六计",     "free"),
}

# ── HTTP helpers ──────────────────────────────────────────────
def api_get(endpoint, params=None, apikey=None):
    """Call ctext.org API"""
    url = f"{API_BASE}/{endpoint}"
    if params:
        qs = "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items())
        url += "?" + qs
    if apikey:
        url += ("&" if "?" in url else "?") + f"apikey={apikey}"
    
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode("utf-8"))


def get_chapter(urn, apikey=None):
    """Get a single chapter/text"""
    return api_get("gettext", {"urn": f"ctp:{urn}"}, apikey)


def search_texts(query, apikey=None):
    """Search ctext.org"""
    return api_get("search", {"query": query, "format": "json"}, apikey)


def get_all_titles(apikey=None):
    """Get list of available titles (requires auth for full list)"""
    try:
        return api_get("gettree", {"urn": "ctp:", "format": "json"}, apikey)
    except:
        return None


# ── Parse classical Chinese to English (rule-based) ──────────
# For the Free Zone, we keep the original Chinese text
# Translation can be added later via LLM

def format_classical_text(chapter_data):
    """Format chapter data into a readable structure"""
    title = chapter_data.get("title", "Unknown")
    fulltext = chapter_data.get("fulltext", [])
    
    if not fulltext:
        return None
    
    # Join paragraphs with double newlines
    content = "\n\n".join(fulltext)
    
    return {
        "title": title,
        "content": content,
        "paragraphs": fulltext,
        "char_count": len(content),
        "paragraph_count": len(fulltext),
    }


# ── Commands ───────────────────────────────────────────────────
def cmd_list(args):
    """List all available classical texts"""
    print(f"Available texts ({len(CLASSICS)}):\n")
    for urn, (title_en, title_cn, zone) in CLASSICS.items():
        status = "✅" if zone == "free" else "🔒"
        print(f"  {status} [{zone:5s}] {title_en} ({title_cn})")
        print(f"           urn: ctp:{urn}")
        print()
    return 0


def cmd_search(args):
    """Search ctext.org for texts"""
    print(f"Searching: {args.query}")
    results = search_texts(args.query)
    
    if "results" in results:
        items = results["results"]
        print(f"\nFound {len(items)} results:\n")
        for item in items[:20]:
            title = item.get("title", "Unknown")
            urn = item.get("urn", "")
            print(f"  {title}")
            print(f"    urn: {urn}")
    else:
        print(f"Results: {results}")
    return 0


def cmd_pull(args):
    """Pull one or more classical texts"""
    apikey = os.environ.get("CTEXT_API_KEY") or args.apikey
    
    targets = []
    if args.urn:
        targets.append(args.urn)
    elif args.all:
        targets = list(CLASSICS.keys())
    else:
        print("Specify --urn or --all")
        return 1
    
    pulled = 0
    failed = []
    
    for urn in targets:
        title_en = CLASSICS.get(urn, ("Unknown", "Unknown", "free"))[0]
        print(f"\n📖 Pulling: {title_en} (urn: ctp:{urn})")
        
        data = get_chapter(urn, apikey)
        
        if "error" in data:
            err_code = data["error"].get("code", "UNKNOWN")
            print(f"  ⚠️  Error ({err_code}): {data['error'].get('description', '')[:100]}")
            failed.append((urn, title_en, err_code))
            continue
        
        formatted = format_classical_text(data)
        if not formatted:
            print(f"  ⚠️  Empty content")
            failed.append((urn, title_en, "EMPTY"))
            continue
        
        # Save
        slug = urn.replace("/", "-")
        out_dir = CHAPTERS_DIR / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        
        # One file per text (classical texts are single-chapter)
        out_file = out_dir / "chapter-1.json"
        chapter_data = {
            "num": 1,
            "title_en": formatted["title"],
            "title_cn": CLASSICS.get(urn, ("", "", ""))[1],
            "content_en": "",  # Keep Chinese original for free zone
            "content_cn": formatted["content"],
            "paragraphs_cn": formatted["paragraphs"],
            "source": "ctext.org",
            "urn": f"ctp:{urn}",
            "translated": False,
            "char_count": formatted["char_count"],
        }
        with open(out_file, 'w') as f:
            json.dump(chapter_data, f, ensure_ascii=False, indent=2)
        
        print(f"  ✅ Saved {formatted['paragraph_count']} paragraphs ({formatted['char_count']} chars)")
        print(f"     → {out_file}")
        pulled += 1
        
        time.sleep(0.3)  # Rate limit
    
    # Update novels.json
    if pulled > 0:
        update_novels_json()
    
    print(f"\n✅ Pulled {pulled}/{len(targets)} texts")
    if failed:
        print(f"\n⚠️  Failed ({len(failed)}):")
        for urn, title, err in failed:
            print(f"     [{err}] {title} (ctp:{urn})")
        print(f"\n  Note: Some texts require ctext.org subscription for full access.")
        print(f"  See: https://ctext.org/tools/subscribe")
    
    return 0


def cmd_batch(args):
    """Pull all free-access classical texts (batch)"""
    print("Starting batch pull of all classical texts...")
    print(f"Total texts: {len(CLASSICS)}\n")
    return cmd_pull(args)


def update_novels_json():
    """Add/update classical texts in novels.json"""
    if NOVELS_FILE.exists():
        novels = json.loads(NOVELS_FILE.read_text())
    else:
        novels = []
    
    existing_slugs = {n.get("slug") for n in novels}
    
    for urn, (title_en, title_cn, zone) in CLASSICS.items():
        slug = urn.replace("/", "-")
        if slug in existing_slugs:
            continue
        
        # Find chapter file
        ch_dir = CHAPTERS_DIR / slug
        total_chapters = len(list(ch_dir.glob("*.json"))) if ch_dir.exists() else 1
        
        novels.append({
            "id": len(novels) + 1,
            "slug": slug,
            "title_en": title_en,
            "title": title_cn,
            "author_en": "Traditional",
            "author": "古典",
            "genre": "Classics",
            "tags": ["classical", "chinese", "free"],
            "is_adult": False,
            "status": "completed",
            "rating": 4.5,
            "total_chapters": total_chapters,
            "readers": 0,
            "description_en": f"Classical Chinese text: {title_en} ({title_cn})",
            "description": f"古典中文经典：{title_cn}",
            "zone": zone,
            "source": "ctext.org",
            "ctext_urn": f"ctp:{urn}",
        })
        existing_slugs.add(slug)
    
    NOVELS_FILE.write_text(json.dumps(novels, ensure_ascii=False, indent=2))
    print(f"Updated {NOVELS_FILE} with {len(novels)} total entries")


# ── Main ───────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Ctext.org Classical Texts Crawler")
    sub = parser.add_subparsers(dest="cmd", required=True)
    
    p = sub.add_parser("list", help="List available classical texts")
    
    p = sub.add_parser("search", help="Search ctext.org")
    p.add_argument("query")
    
    p = sub.add_parser("pull", help="Pull one or more texts")
    p.add_argument("--urn", default=None, help="ctext URN (e.g. 'dao-de-jing')")
    p.add_argument("--all", action="store_true", help="Pull all texts")
    p.add_argument("--apikey", default=None, help="ctext.org API key")
    
    p = sub.add_parser("batch", help="Batch pull all classical texts")
    p.add_argument("--apikey", default=None)
    
    args = parser.parse_args()
    
    if args.cmd == "list":
        return cmd_list(args)
    elif args.cmd == "search":
        return cmd_search(args)
    elif args.cmd == "pull":
        return cmd_pull(args)
    elif args.cmd == "batch":
        return cmd_batch(args)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
