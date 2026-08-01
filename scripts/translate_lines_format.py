#!/usr/bin/env python3
"""
Translate chapters stored in 'lines' format (Chinese text as array of strings).
Converts lines → content_zh → content_en.
"""
import json, os, time, signal, sys, traceback, urllib.request, urllib.parse
from datetime import datetime

CHAPTERS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'chapters')
PROGRESS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'translate_lines_progress.json')

stopping = False

def sig_handler(sig, frame):
    global stopping
    stopping = True
    sys.stderr.write("\n🛑 Stopping...\n")
    sys.stderr.flush()
signal.signal(signal.SIGTERM, sig_handler)
signal.signal(signal.SIGINT, sig_handler)

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {'done': [], 'failed': [], 'total': 0}

def save_progress(p):
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(p, f, ensure_ascii=False, indent=2)

def translate(text, timeout=15):
    if not text or len(text.strip()) < 3:
        return text
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
        raise Exception(f"Translation too short")
    return result.strip()

def batch_translate_lines():
    progress = load_progress()
    done_set = set(progress['done'])
    failed_set = set(progress['failed'])

    print("🔍 Scanning for 'lines' format chapters...")
    needs_work = []
    for root, dirs, files in os.walk(CHAPTERS_DIR):
        for fname in files:
            if not fname.endswith('.json'): continue
            rel_path = os.path.relpath(os.path.join(root, fname), CHAPTERS_DIR)
            if rel_path in done_set or rel_path in failed_set: continue
            try:
                with open(os.path.join(root, fname)) as f:
                    ch = json.load(f)
                # Only chapters with 'lines' containing Chinese
                if 'lines' not in ch: continue
                if not ch['lines']: continue
                # Skip if already has content_en
                if ch.get('content_en') and len(ch.get('content_en','')) > 50:
                    continue
                # Check it's actually Chinese
                text_sample = '\n'.join(ch['lines'][:5])
                cn = sum(1 for c in text_sample if '\u4e00' <= c <= '\u9fff')
                if cn < 3: continue
                needs_work.append((os.path.join(root, fname), rel_path))
            except Exception as e:
                pass

    remaining = [x for x in needs_work if x[1] not in done_set and x[1] not in failed_set]
    progress['total'] = len(remaining) + len(done_set) + len(failed_set)
    save_progress(progress)

    print(f"📊 Need translate: {len(remaining)}, Done: {len(done_set)}, Failed: {len(failed_set)}")
    if not remaining:
        print("✅ All 'lines' chapters already translated!")
        return

    success = 0
    fail = 0
    for i, (filepath, rel_path) in enumerate(remaining):
        if stopping:
            break
        try:
            with open(filepath) as f:
                ch = json.load(f)

            lines = ch['lines']
            # Join lines into content_zh
            content_zh = '\n\n'.join('\n'.join(lines[i:i+20]) for i in range(0, len(lines), 20))
            ch['content_zh'] = content_zh

            # Translate in chunks
            chunk_size = 1500
            chunks = [content_zh[j:j+chunk_size] for j in range(0, len(content_zh), chunk_size)]
            translated = []
            for chunk in chunks:
                if stopping: break
                result = translate(chunk)
                translated.append(result)
                time.sleep(0.3)

            if stopping: break

            ch['content_en'] = ''.join(translated)
            ch['translated'] = True
            # Remove 'lines' to save space (content now in content_zh)
            del ch['lines']

            with open(filepath, 'w') as f:
                json.dump(ch, f, ensure_ascii=False, indent=2)

            done_set.add(rel_path)
            success += 1
            print(f"  ✅ [{i+1}/{len(remaining)}] {rel_path[:60]}")

            if (i + 1) % 10 == 0:
                progress['done'] = sorted(done_set)
                progress['failed'] = sorted(failed_set)
                save_progress(progress)

            time.sleep(0.2)

        except Exception as e:
            failed_set.add(rel_path)
            fail += 1
            print(f"  ❌ [{i+1}/{len(remaining)}] {rel_path[:60]}: {str(e)[:60]}")
            time.sleep(2)

    progress['done'] = sorted(done_set)
    progress['failed'] = sorted(failed_set)
    progress['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    save_progress(progress)
    print(f"\n🏁 Done! Success: {success}, Failed: {fail}, Total done: {len(done_set)+len(failed_set)}/{progress['total']}")

if __name__ == '__main__':
    try:
        batch_translate_lines()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
