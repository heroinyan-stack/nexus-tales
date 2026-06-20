#!/usr/bin/env python3
"""
全站翻译：遍历 data/chapters 下所有小说目录，译本所有中文章节。
增量保存、断点续传、出错跳过、自动退出。
Usage: python3 scripts/translate_all_novels.py
"""
import json, os, re, sys, time, signal

try:
    from googletrans import Translator
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "googletrans==4.0.0-rc1", "-q"])
    from googletrans import Translator

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CHAPTERS_DIR = os.path.join(DATA_DIR, "chapters")
STATE_FILE = os.path.join(DATA_DIR, "translate_all_state.json")

stop = False
def on_signal(sig, frame):
    global stop
    stop = True
    print("\n🛑 Stopping after current chapter...", flush=True)
signal.signal(signal.SIGTERM, on_signal)
signal.signal(signal.SIGINT, on_signal)

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

def translate_text(translator, text):
    if not text:
        return text
    if len(text) <= 4000:
        return translator.translate(text, src='zh-cn', dest='en').text
    parts = []
    for i in range(0, len(text), 4000):
        try:
            parts.append(translator.translate(text[i:i+4000], src='zh-cn', dest='en').text)
            time.sleep(0.3)
        except:
            parts.append(text[i:i+4000])
    return ''.join(parts)

def main():
    # Find ALL novel directories
    all_slugs = sorted([d for d in os.listdir(CHAPTERS_DIR) if os.path.isdir(os.path.join(CHAPTERS_DIR, d))])
    
    state = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            state = json.load(f)
    
    translator = Translator()
    total_saved = state.get('total_translated', 0)
    log(f'🚀 Starting translation: {len(all_slugs)} novels, {total_saved} in state')
    
    max_rounds = 1000  # safety limit
    for round_num in range(max_rounds):
        if stop:
            break
        
        saved_this_round = False
        
        for slug in all_slugs:
            if stop:
                break
            
            ch_dir = os.path.join(CHAPTERS_DIR, slug)
            if not os.path.isdir(ch_dir):
                continue
            
            # Find one untranslated chapter
            files = sorted([f for f in os.listdir(ch_dir) if f.startswith('ch-') and f.endswith('.json')],
                          key=lambda x: int(re.search(r'ch-(\d+)', x).group(1)))
            
            found = False
            for fn in files:
                ch_path = os.path.join(ch_dir, fn)
                with open(ch_path) as f:
                    ch = json.load(f)
                
                if ch.get('content_en') or ch.get('translated'):
                    continue
                
                cn_text = get_cn_text(ch)
                if not cn_text or cn_text == '[No content]':
                    continue
                
                found = True
                num = int(re.search(r'ch-(\d+)', fn).group(1))
                cn_title = ch.get('title', '')
                
                try:
                    # Translate title
                    title_en = cn_title
                    if cn_title and any('\u4e00' <= c <= '\u9fff' for c in cn_title):
                        title_en = translator.translate(cn_title[:500], src='zh-cn', dest='en').text
                    
                    # Translate content
                    content_en = translate_text(translator, cn_text)
                    
                    # Normalize and save
                    if ch.get('lines') and not ch.get('content_zh'):
                        ch['content_zh'] = '\n\n'.join([l.strip() for l in ch['lines'] if l.strip()])
                        if 'lines' in ch:
                            del ch['lines']
                    elif ch.get('content') and not ch.get('content_zh'):
                        ch['content_zh'] = ch['content']
                    
                    ch['content_en'] = content_en
                    ch['title_en'] = title_en
                    ch['translated'] = True
                    
                    with open(ch_path, 'w') as f:
                        json.dump(ch, f, ensure_ascii=False, indent=2)
                    
                    total_saved += 1
                    saved_this_round = True
                    # Save state immediately (not just every 20)
                    state['total_translated'] = total_saved
                    state['last_run'] = time.strftime('%Y-%m-%d %H:%M')
                    with open(STATE_FILE, 'w') as f2:
                        json.dump(state, f2, ensure_ascii=False, indent=2)
                    time.sleep(1.2)
                except Exception as e:
                    log(f"  ⚠️ {slug}/ch-{num}: {str(e)[:60]}")
                break  # one per novel per round
            
            if not found:
                continue  # novel complete
        
        # Progress report every 20 chapters
        if saved_this_round and total_saved % 20 == 0:
            remaining = 0
            for s in all_slugs:
                d = os.path.join(CHAPTERS_DIR, s)
                if not os.path.isdir(d): continue
                for f in os.listdir(d):
                    if not f.startswith('ch-') or not f.endswith('.json'): continue
                    with open(os.path.join(d, f)) as fc: ch = json.load(fc)
                    if not ch.get('content_en') and not ch.get('translated'):
                        cn = get_cn_text(ch)
                        if cn and cn != '[No content]': remaining += 1
            log(f"📊 {total_saved} done, ~{remaining} remaining")
            
            state['total_translated'] = total_saved
            state['last_run'] = time.strftime('%Y-%m-%d %H:%M')
            with open(STATE_FILE, 'w') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        
        if not saved_this_round:
            log("🎉 All chapters translated!")
            break
    
    # Final count
    remaining = 0
    for s in all_slugs:
        d = os.path.join(CHAPTERS_DIR, s)
        if not os.path.isdir(d): continue
        for f in os.listdir(d):
            if not f.startswith('ch-') or not f.endswith('.json'): continue
            with open(os.path.join(d, f)) as fc: ch = json.load(fc)
            if not ch.get('content_en') and not ch.get('translated'):
                cn = get_cn_text(ch)
                if cn and cn != '[No content]': remaining += 1
    
    state['total_translated'] = total_saved
    state['last_run'] = time.strftime('%Y-%m-%d %H:%M')
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    
    log(f"\n🏁 Done: translated {total_saved} in this session")
    log(f"Remaining untranslated: ~{remaining}")

if __name__ == "__main__":
    main()
