#!/usr/bin/env python3
"""Download real book covers — multi-source, replaces ugly SVG placeholders."""

import json
import os
import time
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path

COVERS_DIR = Path(__file__).parent.parent / "public" / "covers"
NOVELS_FILE = Path(__file__).parent.parent / "data" / "novels.json"
COVERS_DIR.mkdir(parents=True, exist_ok=True)

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

# ── Multi-source cover URLs for each novel ──────────────
# Each entry: list of [url, source_label]
KNOWN_COVERS = {
    # VIP Novels — Amazon / Goodreads / NovelUpdates
    "martial-god-asura": [
        "https://images-na.ssl-images-amazon.com/images/I/81y1GzJlSoL.jpg",
        "https://images-na.ssl-images-amazon.com/images/I/91YBXFM1svL.jpg",
    ],
    "against-the-gods": [
        "https://images-na.ssl-images-amazon.com/images/I/815sAcsXgDL.jpg",
        "https://images-na.ssl-images-amazon.com/images/I/81RmGCL+jyL.jpg",
    ],
    "i-shall-seal-the-heavens": [
        "https://images-na.ssl-images-amazon.com/images/I/81P1URyWRDL.jpg",
        "https://images-na.ssl-images-amazon.com/images/I/91HZfBp0H6L.jpg",
    ],
    "reverend-insanity": [
        "https://images-na.ssl-images-amazon.com/images/I/81rPBYeMYTL.jpg",
        "https://images-na.ssl-images-amazon.com/images/I/91MCDqmOFzL.jpg",
    ],
    "a-will-eternal": [
        "https://images-na.ssl-images-amazon.com/images/I/81A-WhZ5H-L.jpg",
        "https://images-na.ssl-images-amazon.com/images/I/91L+UFY+XJL.jpg",
    ],
    "battle-through-the-heavens": [
        "https://images-na.ssl-images-amazon.com/images/I/81qXEqrmGXL.jpg",
        "https://images-na.ssl-images-amazon.com/images/I/91DoaCOSleL.jpg",
    ],
    "renegade-immortal": [
        "https://images-na.ssl-images-amazon.com/images/I/81vF5vDuWkL.jpg",
        "https://images-na.ssl-images-amazon.com/images/I/91-Ee4WtUSL.jpg",
    ],
    "the-remarried-empress": [
        "https://images-na.ssl-images-amazon.com/images/I/91-hKrJmTqL.jpg",
        "https://images-na.ssl-images-amazon.com/images/I/81Dv7Q89QyL.jpg",
    ],
    "hidden-marriage": [
        "https://images-na.ssl-images-amazon.com/images/I/81VW0JHxCuL.jpg",
        "https://images-na.ssl-images-amazon.com/images/I/91Q5sRyhixL.jpg",
    ],
    "secret-lovers": [
        "https://images-na.ssl-images-amazon.com/images/I/81sZJ4r5NFL.jpg",
        "https://images-na.ssl-images-amazon.com/images/I/91zHzGYBb0L.jpg",
    ],
    "super-gene": [
        "https://images-na.ssl-images-amazon.com/images/I/81XLYoLERwL.jpg",
    ],
    "city-of-sin": [
        "https://images-na.ssl-images-amazon.com/images/I/81rFJyUUGLL.jpg",
    ],
    # Free Zone — Classics (Amazon editions)
    "journey-to-the-west": [
        "https://images-na.ssl-images-amazon.com/images/I/81HvULIPqJL.jpg",
        "https://images-na.ssl-images-amazon.com/images/I/716dvv8-SwL.jpg",
    ],
    "strange-tales-chinese-studio": [
        "https://images-na.ssl-images-amazon.com/images/I/71PQ581F7LL.jpg",
        "https://images-na.ssl-images-amazon.com/images/I/815ymMMpFvL.jpg",
    ],
    "dream-of-the-red-chamber": [
        "https://images-na.ssl-images-amazon.com/images/I/81CtRNwhTrL.jpg",
        "https://images-na.ssl-images-amazon.com/images/I/91jRlk2y+XL.jpg",
    ],
    "romance-of-the-three-kingdoms": [
        "https://images-na.ssl-images-amazon.com/images/I/81ry2+JxyLL.jpg",
        "https://images-na.ssl-images-amazon.com/images/I/71KPEMpu2-L.jpg",
    ],
    "water-margin": [
        "https://images-na.ssl-images-amazon.com/images/I/81ZzlMh7jFL.jpg",
        "https://images-na.ssl-images-amazon.com/images/I/711rJn2rN8L.jpg",
    ],
    "art-of-war": [
        "https://images-na.ssl-images-amazon.com/images/I/71BM6N-2j3L.jpg",
        "https://images-na.ssl-images-amazon.com/images/I/71kG7s8b3ML.jpg",
    ],
    "analects-of-confucius": [
        "https://images-na.ssl-images-amazon.com/images/I/71gTWMYLQoL.jpg",
        "https://images-na.ssl-images-amazon.com/images/I/81BLc0LmEKL.jpg",
    ],
    "tao-te-ching": [
        "https://images-na.ssl-images-amazon.com/images/I/71iDxSzwpAL.jpg",
        "https://images-na.ssl-images-amazon.com/images/I/81yf9WkZ-KL.jpg",
    ],
    "zhuangzi": [
        "https://images-na.ssl-images-amazon.com/images/I/71CYD5TBj4L.jpg",
        "https://images-na.ssl-images-amazon.com/images/I/81nQJLu97HL.jpg",
    ],
    "art-of-war-sun-tzu": [
        "https://images-na.ssl-images-amazon.com/images/I/71BM6N-2j3L.jpg",
        "https://images-na.ssl-images-amazon.com/images/I/71kG7s8b3ML.jpg",
    ],
    "gullivers-travels": [
        "https://images-na.ssl-images-amazon.com/images/I/71SzpNNqGiL.jpg",
        "https://images-na.ssl-images-amazon.com/images/I/81CMqb7sKkL.jpg",
    ],
    "chinese-ghost-and-love-stories": [
        "https://images-na.ssl-images-amazon.com/images/I/71sQxjcBRPL.jpg",
        "https://images-na.ssl-images-amazon.com/images/I/81pM7UxkL+L.jpg",
    ],
    "kai-lung-unrolls-his-mat": [
        "https://images-na.ssl-images-amazon.com/images/I/71d2JdUivNL.jpg",
    ],
    "the-flight-of-dragons": [
        "https://images-na.ssl-images-amazon.com/images/I/71SObcOF5CL.jpg",
    ],
    "the-story-of-the-stone": [
        "https://images-na.ssl-images-amazon.com/images/I/81CtRNwhTrL.jpg",
        "https://images-na.ssl-images-amazon.com/images/I/91jRlk2y+XL.jpg",
    ],
    "investiture-of-the-gods": [
        "https://images-na.ssl-images-amazon.com/images/I/81fGTbAQyIL.jpg",
        "https://images-na.ssl-images-amazon.com/images/I/71kooBF5UPL.jpg",
    ],
    "creation-of-the-gods": [
        "https://images-na.ssl-images-amazon.com/images/I/81fGTbAQyIL.jpg",
        "https://images-na.ssl-images-amazon.com/images/I/71kooBF5UPL.jpg",
    ],
    "monkey-kings-birth": [
        "https://images-na.ssl-images-amazon.com/images/I/81HvULIPqJL.jpg",
        "https://images-na.ssl-images-amazon.com/images/I/716dvv8-SwL.jpg",
    ],
    "white-snake-legend": [
        "https://images-na.ssl-images-amazon.com/images/I/71-sBhSofnL.jpg",
        "https://images-na.ssl-images-amazon.com/images/I/81mYL3KaEQL.jpg",
    ],
}

# ── Open Library fallback ───────────────────────────────
def search_openlibrary(title, author=""):
    try:
        q = urllib.parse.quote(f"{title} {author}".strip())
        url = f"https://openlibrary.org/search.json?q={q}&limit=3"
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        for doc in data.get("docs", []):
            cid = doc.get("cover_i")
            if cid:
                return f"https://covers.openlibrary.org/b/id/{cid}-L.jpg"
        return None
    except Exception:
        return None

def download(url, slug):
    """Download cover. Returns extension string or None."""
    ext = url.rsplit(".", 1)[-1].split("?")[0].lower()
    if ext not in ("jpg", "jpeg", "png", "webp"):
        ext = "jpg"
    path = COVERS_DIR / f"{slug}.{ext}"

    # Skip if already has good cover
    if path.exists() and path.stat().st_size > 2000:
        return ext

    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
        ct = resp.headers.get("Content-Type", "")
        if len(data) < 2000:
            return None
        if "text/html" in ct:
            return None

        path.write_bytes(data)
        print(f"    ✓ {path.name} ({len(data):,}B)")
        return ext
    except urllib.error.HTTPError as e:
        return None
    except Exception as e:
        return None

def main():
    with open(NOVELS_FILE) as f:
        novels = json.load(f)

    # Remove old .svg placeholders first
    for svg in COVERS_DIR.glob("*.svg"):
        svg.unlink()
        print(f"  🗑  Removed placeholder: {svg.name}")

    # Remove broken tiny files
    for f in COVERS_DIR.glob("*.*"):
        if f.stat().st_size < 2000:
            f.unlink()
            print(f"  🗑  Removed broken: {f.name}")

    manifest = {}
    total = 0
    success = 0

    for novel in novels:
        slug = novel["slug"]
        title = novel.get("title_en", "") or novel.get("title", "")
        author = novel.get("author_en", "") or novel.get("author", "")
        total += 1

        # Check if good cover already exists
        existing = list(COVERS_DIR.glob(f"{slug}.*"))
        if existing:
            best = max(existing, key=lambda p: p.stat().st_size)
            if best.stat().st_size > 2000:
                ext = best.suffix.lstrip(".")
                manifest[slug] = ext
                success += 1
                continue

        print(f"\n📖 {title}")

        ext = None

        # 1) Try known URLs
        urls = KNOWN_COVERS.get(slug, [])
        if novel.get("cover_url") and novel["cover_url"].startswith("http"):
            urls.append(novel["cover_url"])
        for url in urls:
            ext = download(url, slug)
            if ext:
                break

        # 2) Open Library fallback
        if not ext:
            print(f"    → Open Library...")
            ol = search_openlibrary(title, author)
            if ol:
                ext = download(ol, slug)

        if ext:
            manifest[slug] = ext
            success += 1
        else:
            print(f"    ✗ No cover found")

    # Save manifest
    mf = os.path.join(os.path.dirname(NOVELS_FILE), "cover-manifest.json")
    with open(mf, "w") as f:
        json.dump(manifest, f, indent=2)

    # Update novels.json
    for n in novels:
        s = n["slug"]
        if s in manifest:
            n["cover_ext"] = manifest[s]
    with open(NOVELS_FILE, "w") as f:
        json.dump(novels, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*50}")
    print(f"✅ {success}/{total} covers ready")
    print(f"📁 {COVERS_DIR}")
    print(f"📊 {sum(1 for p in COVERS_DIR.iterdir() if p.suffix in ('.jpg','.png','.webp'))} cover files")

if __name__ == "__main__":
    main()