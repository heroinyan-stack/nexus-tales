#!/usr/bin/env python3
"""Fix new free novels: add missing fields + move chapter files to correct paths."""
import json, os, shutil, glob

DATA_DIR = '/Users/myan/.qclaw/workspace/novel-site/data'
CHAPTERS_FLAT = os.path.join(DATA_DIR, 'chapters')

# New novel slugs that need fixing
NEW_SLUGS = [
    'strange-tales-chinese-studio', 'investiture-of-the-gods', 'gullivers-travels',
    'creation-of-the-gods', 'monkey-kings-birth', 'white-snake-legend',
]

# Fields to add/fix
FIXES = {
    'strange-tales-chinese-studio': {'genre': 'classic', 'description_en': 'Nearly 500 supernatural tales from Qing Dynasty China. Fox spirits, ghosts, and immortals walk among mortals in this timeless classic of Chinese weird fiction.'},
    'investiture-of-the-gods': {'genre': 'xianxia', 'description_en': 'The great war between Shang and Zhou becomes a battlefield for gods and demons. Jiang Ziya must bestow divine titles upon the fallen in this epic of Chinese mythology.'},
    'gullivers-travels': {'genre': 'fantasy', 'description_en': "Lemuel Gulliver voyages to Lilliput, Brobdingnag, Laputa, and beyond — a timeless adventure of wonder, satire, and dark truth about human nature."},
    'creation-of-the-gods': {'genre': 'classic', 'description_en': 'Before heaven and earth, there was chaos. Witness the birth of Pangu, the mending of the sky by Nüwa, and the first gods taking their celestial thrones.'},
    'monkey-kings-birth': {'genre': 'xianxia', 'description_en': 'From a stone egg atop the Mountain of Flowers and Fruit, Sun Wukong is born. Follow his earliest days: the Water Curtain Cave, the quest for immortality, and the mischief that makes him legend.'},
    'white-snake-legend': {'genre': 'romance', 'description_en': "A thousand-year-old white snake spirit falls in love with a mortal man at West Lake. One of China's Four Great Folktales, retold for modern readers."},
}

# 1. Fix novels.json
with open(os.path.join(DATA_DIR, 'novels.json')) as f:
    novels = json.load(f)

for novel in novels:
    slug = novel.get('slug', '')
    if slug in FIXES:
        fix = FIXES[slug]
        if 'genre' not in novel or not novel.get('genre'):
            novel['genre'] = fix['genre']
        if 'description_en' not in novel or not novel.get('description_en'):
            novel['description_en'] = fix['description_en'] if 'description_en' in fix else novel.get('description', '')
        if 'is_adult' not in novel:
            novel['is_adult'] = False
        if 'readers' not in novel:
            novel['readers'] = novel.get('reads', novel.get('readers', 1000))
        if 'cover_url' not in novel:
            novel['cover_url'] = novel.get('cover', f'/covers/{slug}.jpg')
        if 'source_url' not in novel:
            novel['source_url'] = ''
        if 'source_site' not in novel:
            novel['source_site'] = 'Nexus Tales'
        if 'created_at' not in novel:
            novel['created_at'] = '2026-05-25T00:00:00Z'
        if 'updated_at' not in novel:
            novel['updated_at'] = '2026-05-25T00:00:00Z'
        if 'id' not in novel:
            novel['id'] = novels.index(novel) + 1
        # Rename 'reads' → 'readers' if exists
        if 'reads' in novel and 'readers' in novel and novel['reads'] != novel['readers']:
            pass  # already fixed above
        print(f"  ✓ Fixed {slug}: genre={novel['genre']}, readers={novel['readers']}")

# Also fix existing novels that might be missing fields
for novel in novels:
    if 'genre' not in novel:
        novel['genre'] = 'fantasy'
    if 'is_adult' not in novel:
        novel['is_adult'] = False
    if 'readers' not in novel:
        novel['readers'] = novel.get('reads', 1000)
    if 'description_en' not in novel:
        novel['description_en'] = novel.get('description', 'A great novel.')

with open(os.path.join(DATA_DIR, 'novels.json'), 'w') as f:
    json.dump(novels, f, ensure_ascii=False, indent=2)
print(f"\n✅ novels.json fixed ({len(novels)} novels)")

# 2. Move chapter files: flat → directory format
for slug in NEW_SLUGS:
    flat_files = glob.glob(os.path.join(CHAPTERS_FLAT, f'{slug}_*.json'))
    if not flat_files:
        print(f"  ⚠ No flat files for {slug}")
        continue
    
    # Create directory
    dir_path = os.path.join(CHAPTERS_FLAT, slug)
    os.makedirs(dir_path, exist_ok=True)
    
    for flat_file in sorted(flat_files):
        # Extract chapter number from filename
        basename = os.path.basename(flat_file)
        # Format: slug_N.json
        num_str = basename.replace(f'{slug}_', '').replace('.json', '')
        try:
            num = int(num_str)
        except ValueError:
            print(f"  ⚠ Cannot parse number from {basename}")
            continue
        
        # Read content
        with open(flat_file) as f:
            data = json.load(f)
        
        # Write in correct format
        ch_data = {
            'num': num,
            'title_en': data.get('title', f'Chapter {num}'),
            'content_en': data.get('content', ''),
            'translated': True,
        }
        target = os.path.join(dir_path, f'ch-{num}.json')
        with open(target, 'w') as f:
            json.dump(ch_data, f, ensure_ascii=False)
        
        # Remove flat file
        os.remove(flat_file)
    
    print(f"  ✓ Moved {len(flat_files)} chapters for {slug}")

print("\n✅ All done!")
