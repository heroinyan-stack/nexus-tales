#!/usr/bin/env python3
"""
批量翻译所有章节（MyMemory HTTP API版，无需翻墙）。
增量保存、断点续传、出错跳过。
Usage: python3 scripts/translate_all_v3.py
"""
import json, os, re, sys, time, signal, urllib.request, urllib.parse, urllib.error

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CHAPTERS_DIR = os.path.join(DATA_DIR, "chapters")
NOVELS_FILE = os.path.join(DATA_DIR, "novels.json")
STATE_FILE = os.path.join(DATA_DIR, "translate_state_v3.json")
MYMEMORY_API = "https://api.mymemory.translated.net/get"

stop = False
def on_signal(sig, frame):
    global stop
    stop = True
    print("\n🛑 Stopping after current chapter...", flush=True)
signal.signal(signal.SIGTERM, on_signal)
signal.signal(signal.SIGINT, on_signal)

def log(msg):
    print(msg, flush=True)

def translate_mymemory(text, retries=3):
    """Translate Chinese to English via MyMemory API."""
    if not text or len(text.strip()) < 3:
        return text
    
    # MyMemory limit is ~500 chars per request
    if len(text) <= 400:
        for attempt in range(retries):
            try:
                params = urllib.parse.urlencode({
                    'q': text,
                    'langpair': 'zh-CN|en',
                    'de': 'qclaw@novelhub.beauty'
                })
                url = f"{MYMEMORY_API}?{params}"
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode())
                    if data.get('responseStatus') == 200:
                        return data['responseData']['translatedText']
                    raise Exception(data.get('responseDetails', 'unknown'))
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep((attempt + 1) * 3)
                else:
                    raise
    else:
        # Chunk longer text
        parts = []
        for i in range(0, len(text), 400):
            chunk = text[i:i+400]
            for attempt in range(retries):
                try:
                    params = urllib.parse.urlencode({
                        'q': chunk,
                        'langpair': 'zh-CN|en',
                        'de': 'qclaw@novelhub.beauty'
                    })
                    url = f"{MYMEMORY_API}?{params}"
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=30) as resp:
                        data = json.loads(resp.read().decode())
                        if data.get('responseStatus') == 200:
                            parts.append(data['responseData']['translatedText'])
                            break
                except Exception as e:
                    if attempt < retries - 1:
                        time.sleep((attempt + 1) * 2)
                    else:
                        log(f"  ⚠️ chunk failed: {str(e)[:60]}")
                        parts.append(chunk)  # fallback: keep original
                    break
                time.sleep(0.3)
            time.sleep(0.2)
        return ''.join(parts)

def get_cn_text(ch):
    if ch.get('content_en') and len(ch['content_en'].strip()) > 20:
        return None
    if ch.get('content'):
        return ch['content']
    if ch.get('content_zh'):
        return ch['content_zh']
    if ch.get('lines'):
        return '\n\n'.join([l.strip() for l in ch['lines'] if l.strip()])
    return None

def count_remaining(all_slugs):
    remaining = 0
    for s in all_slugs:
        d = os.path.join(CHAPTERS_DIR, s)
        if not os.path.isdir(d): continue
        for f in os.listdir(d):
            if not f.startswith('ch-') or not f.endswith('.json'): continue
            try:
                with open(os.path.join(d, f)) as fc: ch = json.load(fc)
                if not ch.get('content_en') or len(ch.get('content_en','').strip()) < 20:
                    if not ch.get('translated'):
                        cn = get_cn_text(ch)
                        if cn and len(cn.strip()) >= 5: remaining += 1
            except: pass
    return remaining

def main():
    with open(NOVELS_FILE) as f:
        novels = json.load(f)
    novels = novels if isinstance(novels, list) else novels.get('novels', [])
    
    all_slugs = [n['slug'] for n in novels]
    
    state = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            state = json.load(f)
    
    total_saved = 0
    error_count = 0
    max_errors = 30
    
    max_rounds = 2000
    for round_num in range(max_rounds):
        if stop or error_count >= max_errors:
            break
        
        saved_this_round = False
        
        for slug in all_slugs:
            if stop or error_count >= max_errors:
                break
            
            ch_dir = os.path.join(CHAPTERS_DIR, slug)
            if not os.path.isdir(ch_dir):
                continue
            
            files = sorted([f for f in os.listdir(ch_dir) if f.startswith('ch-') and f.endswith('.json')],
                          key=lambda x: int(re.search(r'ch-(\d+)', x).group(1)))
            
            found = False
            for fn in files:
                ch_path = os.path.join(ch_dir, fn)
                try:
                    with open(ch_path) as f:
                        ch = json.load(f)
                except:
                    continue
                
                if ch.get('content_en') and len(ch['content_en'].strip()) > 20:
                    continue
                if ch.get('translated'):
                    continue
                
                cn_text = get_cn_text(ch)
                if not cn_text or len(cn_text.strip()) < 5:
                    continue
                
                found = True
                num = int(re.search(r'ch-(\d+)', fn).group(1))
                cn_title = ch.get('title', '')
                
                try:
                    # Translate title
                    title_en = cn_title
                    if cn_title and any('\u4e00' <= c <= '\u9fff' for c in cn_title):
                        title_en = translate_mymemory(cn_title[:400])
                    
                    # Translate content
                    content_en = translate_mymemory(cn_text)
                    
                    # Normalize fields
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
                    error_count = 0
                    time.sleep(0.3)
                except Exception as e:
                    error_count += 1
                    log(f"  ⚠️ {slug}/ch-{num:04d}: {str(e)[:80]}")
                    if error_count >= max_errors:
                        log(f"🛑 Too many errors ({error_count}), stopping")
                        break
                    time.sleep(1)
                break
            
            if not found:
                continue
        
        if saved_this_round and total_saved % 10 == 0:
            remaining = count_remaining(all_slugs)
            log(f"📊 {total_saved} done, ~{remaining} remaining")
            
            state['total_translated'] = total_saved
            state['last_run'] = time.strftime('%Y-%m-%d %H:%M')
            with open(STATE_FILE, 'w') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        
        if not saved_this_round:
            log("🎉 All chapters translated!")
            break
    
    remaining = count_remaining(all_slugs)
    
    state['total_translated'] = total_saved + state.get('total_translated', 0)
    state['last_run'] = time.strftime('%Y-%m-%d %H:%M')
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    
    log(f"\n🏁 Done: translated {total_saved} in this session")
    log(f"Remaining untranslated: ~{remaining}")
    if error_count >= max_errors:
        log("⚠️ Stopped due to too many errors")

if __name__ == "__main__":
    main()
