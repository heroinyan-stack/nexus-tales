#!/usr/bin/env python3
"""
Daily bxwx9 chapter pull — pulls ALL chapters for N novels per run.
Tracks state so each run picks up where it left off.
Usage: python3 scripts/bxwx9_daily.py [--novels-per-run N]
"""
import json, re, time, os, subprocess, glob, sys

# ═════════ Config ═════════
CHAPTERS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'chapters')
NOVELS_JSON = os.path.join(os.path.dirname(__file__), '..', 'data', 'novels.json')
STATE_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'bxwx9_state.json')
NOVELS_PER_RUN = 3
DELAY = 0.5
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'

# Allow override from command line
for a in sys.argv[1:]:
    if a.startswith('--novels='):
        NOVELS_PER_RUN = int(a.split('=')[1])

# ═════════ Helpers ═════════
def log(msg):
    print(msg, flush=True)

def fetch(url, referer=None):
    cmd = ['curl', '-sk', '--max-time', '30', '--connect-timeout', '10', '-A', UA]
    if referer:
        cmd += ['-H', f'Referer: {referer}']
    cmd.append(url)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
    if r.returncode != 0:
        raise Exception(f"curl rc={r.returncode}")
    return r.stdout

def clean_text(raw):
    text = re.sub(r'<script[^>]*>.*?</script>', '', raw, flags=re.S)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.S)
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.I)
    text = re.sub(r'</?p[^>]*>', '\n', text, flags=re.I)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&nbsp;', '').replace('&lt;', '<').replace('&gt;', '>')
    for pat in [
        r'本站所有收录.*?删除。', r'笔下文学网.*?小说迷。',
        r'努力打造最干净.*', r'请记住本书首发域名.*',
        r'天才一秒记住.*', r'手机用户请浏览.*',
        r'温馨提示.*?bsp;.*', r'如果您喜欢.*?推荐.*',
        r'--&gt;&gt;.*', r'第\(\d+/\d+\)页', r'&gt;&gt;.*',
        r'\w+\([^)]*\)\s*;?', r'-->', r'&lt;!--',
    ]:
        text = re.sub(pat, '', text, flags=re.S)
    lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) > 2]
    return '\n'.join(lines)

def extract_content(html):
    idx = html.find('关灯')
    if idx < 0:
        idx = html.find('content"')
    if idx < 0:
        main = html
    else:
        main = html[idx:idx + 12000]
    return clean_text(main)

def get_existing(slug):
    ch_dir = os.path.join(CHAPTERS_DIR, slug)
    if not os.path.isdir(ch_dir):
        return set()
    return {int(re.search(r'ch-(\d+)', f).group(1))
            for f in os.listdir(ch_dir)
            if f.endswith('.json') and re.search(r'ch-(\d+)', f)}

def get_chapter_list(novel_url):
    html = fetch(novel_url)
    chapters = re.findall(r'href="(/b/\d+/\d+/\d+\.html)"[^>]*>([^<]+)<', html)
    return [('https://www.bxwx9.org' + u, t.strip()) for u, t in chapters]

# ═════════ Load state ═════════
if os.path.exists(STATE_FILE):
    with open(STATE_FILE) as f:
        state = json.load(f)
else:
    state = {'completed': [], 'processed_at': {}}

# ═════════ Load novels ═════════
with open(NOVELS_JSON) as f:
    all_novels = json.load(f)

bxwx9 = []
for n in all_novels:
    src = n.get('source_url', '')
    if src and 'bxwx9' in src:
        slug = n['slug']
        existing = get_existing(slug)
        bxwx9.append({
            'slug': slug,
            'source_url': src,
            'title': n.get('title', slug),
            'ch': len(existing)
        })

# Remove completed
pending = [n for n in bxwx9 if n['slug'] not in state['completed']]
pending.sort(key=lambda x: x['ch'])

log(f"=== bxwx9 Daily Pull: {min(NOVELS_PER_RUN, len(pending))} novels ===")
log(f"  Total: {len(bxwx9)} | Completed: {len(state['completed'])} | Pending: {len(pending)}")
log("")

if not pending:
    log("All novels complete!")
    sys.exit(0)

batch = pending[:NOVELS_PER_RUN]
total_pulled = 0

for novel in batch:
    slug, src_url, title = novel['slug'], novel['source_url'], novel['title']
    existing = get_existing(slug)
    
    log(f"📖 {title} ({len(existing)} ch) → fetching list...")
    try:
        chapters = get_chapter_list(src_url)
    except Exception as e:
        log(f"  ❌ List fetch failed: {e}")
        continue
    
    total_site = len(chapters)
    needed = total_site - len(existing)
    log(f"  Site: {total_site} ch | Have: {len(existing)} | Need: {needed}")
    
    if needed <= 0:
        state['completed'].append(slug)
        state['processed_at'][slug] = time.strftime('%Y-%m-%d %H:%M')
        log(f"  ✅ Already complete ({total_site} synced)")
        continue
    
    pulled = 0
    for i, (ch_url, ch_title) in enumerate(chapters, 1):
        if i in existing:
            continue
        try:
            html = fetch(ch_url, referer=src_url)
            text = extract_content(html)
            if len(text) < 80:
                continue
            
            ch_data = {
                "num": i,
                "title": ch_title,
                "slug": slug,
                "lines": [l for l in text.split('\n') if l.strip()]
            }
            ch_dir = os.path.join(CHAPTERS_DIR, slug)
            os.makedirs(ch_dir, exist_ok=True)
            with open(os.path.join(ch_dir, f'ch-{i}.json'), 'w') as f:
                json.dump(ch_data, f, ensure_ascii=False)
            
            existing.add(i)
            pulled += 1
            total_pulled += 1
            
            if pulled % 20 == 0:
                log(f"    ... {pulled}/{needed}")
            
            time.sleep(DELAY)
        except Exception as e:
            log(f"    ch-{i}: ERR {str(e)[:60]}")
    
    state['processed_at'][slug] = time.strftime('%Y-%m-%d %H:%M')
    new_total = len(existing)
    
    if new_total >= total_site:
        state['completed'].append(slug)
        log(f"  ✅ DONE: {new_total}/{total_site} 全部拉完")
    else:
        log(f"  📊 +{pulled} → {new_total}/{total_site} (剩{total_site - new_total}章)")
    
    log("")

# ═════════ Save state ═════════
with open(STATE_FILE, 'w') as f:
    json.dump(state, f, ensure_ascii=False, indent=2)

log(f"🎯 本次: +{total_pulled}章 | 已完成小说: {len(state['completed'])}")
