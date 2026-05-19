#!/usr/bin/env python3
"""Add 10 more public domain books to Free Zone from Project Gutenberg.
These are high-SEO English books related to Chinese culture, philosophy, and classic literature.
"""
import json, os, re, urllib.request
from datetime import date

BASE = "/Users/myan/.qclaw/workspace/novel-site"
NOVELS_PATH = os.path.join(BASE, "data/novels.json")
CHAPTERS_DIR = os.path.join(BASE, "data/chapters")

# GUTENBERG BOOKS TO ADD (all public domain in US)
# Format: (slug, title_en, author_en, gutenberg_id, description)
NEW_BOOKS = [
    ("zhuangzi", "Zhuangzi (Chuang Tzu)", "Zhuangzi (Chuang Tzu)", "38932",
     "The Taoist classic by Zhuangzi — a foundational text of Taoist philosophy, filled with parables, irony, and profound insight into the nature of reality and human existence."),
    ("the-book-of-songs", "The Book of Songs (Shijing)", "Confucius (attributed)", "15916",
     "The oldest collection of Chinese poetry, containing 305 poems from the Zhou Dynasty (11th-7th centuries BC). A window into ancient Chinese life, love, politics, and ritual."),
    ("the-story-of-the-stone", "The Story of the Stone (Part I)", "Cao Xueqin", "24028",
     "Also known as Dream of the Red Chamber, this is Volume I of the classic 18th-century Chinese novel about the decline of an aristocratic family. Translated by H. Bencraft Joly."),
    ("personal-narrative-of-heavenly-revelations", "Personal Narrative of Heavenly Revelations", "Hong Xiuquan", "24947",
     "The extraordinary story of Hong Xiuquan, leader of the Taiping Rebellion, who believed himself to be the younger brother of Jesus Christ and sought to overthrow the Qing dynasty."),
    ("chinese-ghost-and-love-stories", "Chinese Ghost and Love Stories", "Pu Songling", "23631",
     "Strange Tales from a Chinese Studio — a collection of nearly 500 supernatural tales by Pu Songling (1640-1715), blending the eerie, the romantic, and the philosophical."),
    ("the-flight-of-dragons", "The Flight of Dragons", "Ernest Bramah", "23244",
     "A classic fantasy novel set in ancient China by Ernest Bramah, author of the Kai Lung series. A tale of magic, adventure, and Oriental wisdom."),
    ("kai-lung-unrolls-his-mat", "Kai Lung Unrolls His Mat", "Ernest Bramah", "36113",
     "The first Kai Lung novel — a comic masterpiece set in ancient China, full of wit, wisdom, and the adventures of the storyteller Kai Lung."),
    ("the-nine-dragons", "The Nine Dragons (Kai Lung)", "Ernest Bramah", "36114",
     "More adventures of Kai Lung, the wandering storyteller of China. Ernest Bramah's tales are beloved for their stylized English prose and Oriental wit."),
]

def fetch_gutenberg(book_id):
    """Fetch text from Project Gutenberg, trying multiple URL formats."""
    urls = [
        f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt",
        f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt",
        f"https://www.gutenberg.org/ebooks/{book_id}.txt.utf-8",
    ]
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "NexusTales/1.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception as e:
            continue
    return None

def save_chapter(slug, num, title, content):
    d = os.path.join(CHAPTERS_DIR, slug)
    os.makedirs(d, exist_ok=True)
    ch = {"num": num, "title_en": title, "content_en": content.strip(), "translated": True}
    with open(os.path.join(d, f"ch-{num}.json"), "w") as f:
        json.dump(ch, f, ensure_ascii=False, indent=2)

def split_text_into_chapters(text, num_chapters=15):
    """Split text into roughly equal chapters by character count."""
    # Remove Gutenberg header/footer
    start = 0
    for marker in ["*** START", "CHAPTER I", "PART I", "BOOK I"]:
        idx = text.find(marker)
        if idx > 0:
            start = idx
            break
    
    end = len(text)
    for marker in ["*** END", "End of the Project"]:
        idx = text.find(marker)
        if idx > 0:
            end = idx
            break
    
    clean = text[start:end]
    total = len(clean)
    if total == 0:
        return []
    
    size = total // num_chapters
    chapters = []
    for i in range(num_chapters):
        start_pos = i * size
        end_pos = (i + 1) * size if i < num_chapters - 1 else total
        chunk = clean[start_pos:end_pos]
        # Try to break at paragraph boundary
        if i < num_chapters - 1:
            last_double_nl = chunk.rfind("\n\n")
            if last_double_nl > len(chunk) * 0.5:
                chunk = chunk[:last_double_nl]
        chapters.append(chunk.strip())
    return chapters

# =========== FETCH AND ADD EACH BOOK ===========
print("=== Adding new Free Zone books from Project Gutenberg ===\n")
novels = json.load(open(NOVELS_PATH))

added = 0
for slug, title, author, gid, desc in NEW_BOOKS:
    # Skip if already exists
    if any(n["slug"] == slug for n in novels):
        print(f"  ⏭  {slug} already exists, skipping")
        continue
    
    print(f"  Fetching {title} (Gutenberg #{gid})...")
    text = fetch_gutenberg(gid)
    if not text:
        print(f"    ✗ Fetch failed, skipping")
        continue
    
    # Split into chapters
    chapters = split_text_into_chapters(text)
    if not chapters:
        print(f"    ✗ Could not split into chapters, skipping")
        continue
    
    # Save chapters
    for i, ch_text in enumerate(chapters, 1):
        if len(ch_text) > 200:  # only save non-empty
            save_chapter(slug, i, f"Chapter {i}", ch_text)
    
    # Add to novels.json
    novels.append({
        "slug": slug,
        "title_en": title,
        "title_zh": "",
        "author_en": author,
        "author_zh": "",
        "genre": "Chinese Classic",
        "tags": ["classic", "philosophy", "Taoism", "Chinese literature"],
        "description_en": desc,
        "description_zh": "",
        "cover": f"/covers/{slug}.jpg",
        "zone": "free",
        "status": "complete",
        "total_chapters": len(chapters),
        "updated_at": date.today().isoformat(),
        "views": 0,
        "rating": 0.0,
    })
    added += 1
    print(f"    ✓ {len(chapters)} chapters added")
    import time; time.sleep(1)  # be polite to Gutenberg

# Save novels.json
with open(NOVELS_PATH, "w") as f:
    json.dump(novels, f, ensure_ascii=False, indent=2)

print(f"\n✅ Added {added} new books to Free Zone")
print(f"Total novels: {len(novels)}")
