#!/usr/bin/env python3
"""
Translate all bxwx9 chapters using googletrans.
Handles lines[] and content formats. Incremental with resume.
Usage: python3 scripts/translate_all_chapters.py [--novels N] [--chapters N]
"""
import json, os, re, sys, time

try:
    from googletrans import Translator
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "googletrans==4.0.0-rc1", "-q"])
    from googletrans import Translator

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CHAPTERS_DIR = os.path.join(DATA_DIR, "chapters")
NOVELS_FILE = os.path.join(DATA_DIR, "novels.json")
STATE_FILE = os.path.join(DATA_DIR, "translate_state.json")

NOVELS_PER_RUN = 3
CHAPTERS_PER_NOVEL = 10

for a in sys.argv[1:]:
    if a.startswith('--novels='):
        NOVELS_PER_RUN = int(a.split('=')[1])
    if a.startswith('--chapters='):
        CHAPTERS_PER_NOVEL = int(a.split('=')[1])

state = {}
if os.path.exists(STATE_FILE):
    with open(STATE_FILE) as f:
        state = json.load(f)

with open(NOVELS_FILE) as f:
    novels = json.load(f)
novels = novels if isinstance(novels, list) else novels.get('novels', [])
bxwx9_slugs = [n['slug'] for n in novels if n.get('source_url', '') and 'bxwx9' in n.get('source_url', '')]

def log(msg):
    print(msg, flush=True)

def get_cn_text(ch):
    if ch.get('content'):
        return ch['content']
    if ch.get('content_zh'):
        return ch['content_zh']
    if ch.get('lines'):
        return '\n\n'.join([l.strip() for l in ch['lines'] if l.strip()])
    return None

def translate_text(translator, text, max_chars=4000):
    """Translate text, chunking if too long"""
    if not text:
        return text
    if len(text) <= max_chars:
        return translator.translate(text, src='zh-cn', dest='en').text
    parts = []
    for i in range(0, len(text), max_chars):
        chunk = text[i:i+max_chars]
        try:
            parts.append(translator.translate(chunk, src='zh-cn', dest='en').text)
            time.sleep(0.5)
        except:
            parts.append(chunk)
    return ''.join(parts)

def process_novel(slug, translator):
    ch_dir = os.path.join(CHAPTERS_DIR, slug)
    if not os.path.isdir(ch_dir):
        return 0
    
    # Find untranslated
    untranslated = []
    for fn in os.listdir(ch_dir):
        if fn == 'meta.json' or not fn.endswith('.json'):
            continue
        p = os.path.join(ch_dir, fn)
        with open(p) as f:
            ch = json.load(f)
        if ch.get('content_en') or ch.get('translated'):
            continue
        cn = get_cn_text(ch)
        if not cn or cn == '[No content]':
            continue
        m = re.search(r'ch-(\d+)', fn)
        num = int(m.group(1)) if m else 0
        untranslated.append((fn, num, cn, ch.get('title', '')))
    
    if not untranslated:
        return 0
    
    untranslated.sort(key=lambda x: x[1])
    batch = untranslated[:CHAPTERS_PER_NOVEL]
    
    log(f"\n📖 {slug}: {len(untranslated)} remaining, translating {len(batch)} chapters")
    
    saved = 0
    for i, (fn, num, cn_text, cn_title) in enumerate(batch):
        try:
            # Translate title
            title_en = cn_title
            if cn_title and sum(1 for c in cn_title if '\u4e00' <= c <= '\u9fff') > 0:
                title_en = translator.translate(cn_title[:500], src='zh-cn', dest='en').text
            
            # Translate content
            content_en = translate_text(translator, cn_text)
            
            # Save
            ch_path = os.path.join(ch_dir, fn)
            with open(ch_path) as f:
                ch = json.load(f)
            
            # Normalize format
            if ch.get('lines') and not ch.get('content_zh'):
                ch['content_zh'] = '\n\n'.join([l.strip() for l in ch['lines'] if l.strip()])
                del ch['lines']
            elif ch.get('content') and not ch.get('content_zh'):
                ch['content_zh'] = ch['content']
            
            ch['content_en'] = content_en
            ch['title_en'] = title_en
            ch['translated'] = True
            
            with open(ch_path, 'w') as f:
                json.dump(ch, f, ensure_ascii=False, indent=2)
            
            saved += 1
            if saved % 5 == 0:
                log(f"  ✓ {saved}/{len(batch)}")
            
            time.sleep(1.0)
        except Exception as e:
            log(f"  ⚠️ ch-{num} failed: {str(e)[:60]}")
    
    return saved

def main():
    log("=" * 50)
    log(f"Nexus Tales — Translate chapters ({NOVELS_PER_RUN} novels × {CHAPTERS_PER_NOVEL} ch)")
    log("=" * 50)
    
    progress = state.get('progress', {})
    
    # Build priority: most untranslated first
    novel_order = []
    for slug in bxwx9_slugs:
        ch_dir = os.path.join(CHAPTERS_DIR, slug)
        if not os.path.isdir(ch_dir):
            continue
        cnt = 0
        for fn in os.listdir(ch_dir):
            if fn == 'meta.json' or not fn.endswith('.json'):
                continue
            with open(os.path.join(ch_dir, fn)) as f:
                ch = json.load(f)
            if not ch.get('content_en') and not ch.get('translated'):
                cn = get_cn_text(ch)
                if cn and cn != '[No content]':
                    cnt += 1
        novel_order.append((slug, cnt))
    
    novel_order.sort(key=lambda x: -x[1])
    
    translator = Translator()
    total_saved = 0
    processed = 0
    
    for slug, remaining in novel_order:
        if processed >= NOVELS_PER_RUN or remaining <= 0:
            break
        saved = process_novel(slug, translator)
        total_saved += saved
        processed += 1
        if saved > 0:
            progress[slug] = progress.get(slug, 0) + saved
    
    state['progress'] = progress
    state['last_run'] = time.strftime('%Y-%m-%d %H:%M')
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    
    remaining = sum(r for _, r in novel_order)
    log(f"\n🎯 Saved: {total_saved} ch | Total remaining: ~{remaining}")

if __name__ == "__main__":
    main()
