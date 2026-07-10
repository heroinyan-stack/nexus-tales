#!/usr/bin/env python3
"""
Batch translate chapters NOT marked garbled and without content_en.
Uses Google Translate public API (free, no key).
Checkpoint: saves progress every 10 chapters.
Resumes from checkpoint on restart.
"""
import json, os, time, signal, sys, traceback, urllib.request, urllib.parse
from datetime import datetime

CHAPTERS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'chapters')
PROGRESS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'batch_translate_progress.json')

stopping = False

def sig_handler(sig, frame):
    global stopping
    stopping = True
    sys.stderr.write("\n🛑 收到停止信号\n")
    sys.stderr.flush()
signal.signal(signal.SIGTERM, sig_handler)
signal.signal(signal.SIGINT, sig_handler)

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {'done': [], 'failed': [], 'total': 0}

def save_progress(progress):
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

def translate(text, timeout=15):
    """Google Translate public API"""
    params = {
        'client': 'gtx', 'sl': 'zh-CN', 'tl': 'en', 'dt': 't',
        'q': text[:1800]
    }
    url = 'https://translate.googleapis.com/translate_a/single?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                resp = r.read().decode('utf-8')
            break
        except Exception as e:
            if attempt == 3:
                raise
            time.sleep(2 * (attempt + 1))
    parsed = json.loads(resp)
    result = ''.join(seg[0] for seg in parsed[0] if seg and seg[0])
    if not result or len(result.strip()) < 3:
        raise Exception(f"Too short: {len(result) if result else 0}")
    return result.strip()

def is_real_chinese(text):
    """Check if text contains actual readable Chinese (not garbled)"""
    if not text: return False
    sample = text[:1000]
    cn = sum(1 for c in sample if '\u4e00' <= c <= '\u9fff')
    return cn / len(sample) > 0.1

def batch_translate():
    progress = load_progress()
    done_set = set(progress['done'])
    failed_set = set(progress['failed'])
    
    # Scan for chapters that need translation
    print("🔍 Scanning for chapters needing translation...")
    needs_work = []
    for root, dirs, files in os.walk(CHAPTERS_DIR):
        for fname in files:
            if not fname.endswith('.json'): continue
            rel_path = os.path.relpath(os.path.join(root, fname), CHAPTERS_DIR)
            if rel_path in done_set or rel_path in failed_set: continue
            try:
                with open(os.path.join(root, fname)) as f:
                    ch = json.load(f)
                if ch.get('_garbled'): continue
                if ch.get('content_en') or ch.get('translated'): continue
                content = ch.get('content_zh', ch.get('content', ''))
                if content and is_real_chinese(content):
                    needs_work.append((os.path.join(root, fname), rel_path))
            except: pass
    
    remaining = [x for x in needs_work if x[1] not in done_set and x[1] not in failed_set]
    progress['total'] = len(remaining) + len(done_set) + len(failed_set)
    save_progress(progress)
    
    print(f"📊 需翻译: {len(remaining)}, 已完成: {len(done_set)}, 失败: {len(failed_set)}")
    
    if not remaining:
        print("✅ 没有需要翻译的章节!")
        return
    
    success = 0
    fail = 0
    for i, (filepath, rel_path) in enumerate(remaining):
        if stopping:
            break
        
        try:
            with open(filepath) as f:
                ch = json.load(f)
            content_zh = ch.get('content_zh', ch.get('content', ''))
            if not content_zh:
                done_set.add(rel_path)
                continue
            
            # Translate in chunks for long content
            chunk_size = 1500
            chunks = [content_zh[j:j+chunk_size] for j in range(0, len(content_zh), chunk_size)]
            translated = []
            for chunk in chunks:
                if stopping: break
                result = translate(chunk)
                translated.append(result)
            
            if stopping: break
            
            ch['content_en'] = ''.join(translated)
            ch['translated'] = True
            with open(filepath, 'w') as f:
                json.dump(ch, f, ensure_ascii=False, indent=2)
            
            done_set.add(rel_path)
            success += 1
            print(f"  ✅ [{i+1}/{len(remaining)}] {rel_path}")
            
            # Save checkpoint every 10
            if (i + 1) % 10 == 0:
                progress['done'] = sorted(done_set)
                progress['failed'] = sorted(failed_set)
                save_progress(progress)
            
            time.sleep(0.3)  # rate limit
            
        except Exception as e:
            failed_set.add(rel_path)
            fail += 1
            print(f"  ❌ [{i+1}/{len(remaining)}] {rel_path}: {str(e)[:80]}")
            time.sleep(2)
    
    progress['done'] = sorted(done_set)
    progress['failed'] = sorted(failed_set)
    progress['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    save_progress(progress)
    
    print(f"\n🏁 完成! 成功: {success}, 失败: {fail}, 总计: {len(done_set)+len(failed_set)}/{progress['total']}")

if __name__ == '__main__':
    try:
        batch_translate()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
