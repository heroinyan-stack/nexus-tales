#!/usr/bin/env python3
"""
Concurrent translator for 'lines' format chapters.
Uses proxy (Clash Verge on 7897) + Google Translate.
6 parallel workers.
"""
import json, os, time, signal, sys, traceback, threading, queue, urllib.request, urllib.parse, subprocess

CHAPTERS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'chapters')
PROGRESS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'translate_lines_progress.json')
PROXY = 'http://127.0.0.1:7897'
N_WORKERS = 6

stopping = False
progress_lock = threading.Lock()
done_count = 0
fail_count = 0

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

def translate_text(text, timeout=20):
    """Translate text using Google Translate via curl + proxy."""
    if not text or len(text.strip()) < 3:
        return text
    text = text[:1800]
    encoded_q = urllib.parse.quote(text)
    url = f'https://translate.googleapis.com/translate_a/single?client=gtx&sl=zh-CN&tl=en&dt=t&q={encoded_q}'
    
    for attempt in range(4):
        try:
            r = subprocess.run(
                ['curl', '-s', '--connect-timeout', '15', '-m', str(timeout),
                 '--proxy', PROXY,
                 '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                 '-o', '-', url],
                capture_output=True, timeout=timeout + 5
            )
            if not r.stdout or r.returncode != 0:
                raise Exception(f"curl failed: {r.returncode}")
            
            resp = r.stdout.decode('utf-8')
            if not resp or resp[0] == '<':
                raise Exception(f"Invalid response (HTML error page)")
            
            parsed = json.loads(resp)
            result = ''.join(seg[0] for seg in parsed[0] if seg and seg[0])
            if result and len(result.strip()) >= 3:
                return result.strip()
            if attempt == 3:
                raise Exception("Translation too short or empty")
            time.sleep(1.5 * (attempt + 1))
        except json.JSONDecodeError as e:
            if attempt == 3:
                raise Exception(f"JSON parse error: {resp[:100]}")
            time.sleep(1.5 * (attempt + 1))
        except Exception as e:
            if attempt == 3:
                raise
            time.sleep(1.5 * (attempt + 1))
    return text

def translate_lines(lines):
    """Translate a list of lines."""
    text = '\n'.join(lines)
    chunk_size = 1200
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    results = []
    for chunk in chunks:
        if stopping: break
        result = translate_text(chunk)
        results.append(result)
        time.sleep(0.15)  # Be polite to Google
    return ''.join(results)

def process_chapter(filepath, rel_path):
    """Process a single chapter file."""
    global done_count, fail_count

    try:
        with open(filepath) as f:
            ch = json.load(f)

        lines = ch.get('lines', [])
        if not lines:
            return True

        # Translate
        content_en = translate_lines(lines)
        if stopping:
            return False

        # Build content_zh from lines
        content_zh = '\n\n'.join('\n'.join(lines[i:i+20]) for i in range(0, len(lines), 20))

        ch['content_zh'] = content_zh
        ch['content_en'] = content_en
        ch['translated'] = True
        if 'lines' in ch:
            del ch['lines']

        with open(filepath, 'w') as f:
            json.dump(ch, f, ensure_ascii=False, indent=2)

        with progress_lock:
            done_count += 1

        return True
    except Exception as e:
        with progress_lock:
            fail_count += 1
        return False

def worker(q, worker_id):
    global stopping
    local_done = 0
    while not stopping:
        try:
            item = q.get(timeout=2)
            if item is None:
                break
            filepath, rel_path = item
            ok = process_chapter(filepath, rel_path)
            q.task_done()
            if ok:
                local_done += 1
        except queue.Empty:
            break
        except Exception as e:
            q.task_done()

    sys.stderr.write(f"\n  Worker {worker_id} done: {local_done} chapters\n")

def main():
    global stopping, done_count, fail_count

    progress = load_progress()
    done_set = set(progress['done'])
    failed_set = set(progress['failed'])

    print("🔍 Scanning for 'lines' format chapters...")
    needs_work = []
    for root, dirs, files in os.walk(CHAPTERS_DIR):
        for fname in sorted(files):
            if not fname.endswith('.json'): continue
            rel_path = os.path.relpath(os.path.join(root, fname), CHAPTERS_DIR)
            if rel_path in done_set or rel_path in failed_set: continue
            try:
                with open(os.path.join(root, fname)) as f:
                    ch = json.load(f)
                if 'lines' not in ch: continue
                if not ch['lines']: 
                    done_set.add(rel_path)
                    continue
                if ch.get('content_en') and len(ch.get('content_en','')) > 50:
                    done_set.add(rel_path)
                    continue
                needs_work.append((os.path.join(root, fname), rel_path))
            except:
                pass

    remaining = [x for x in needs_work if x[1] not in done_set and x[1] not in failed_set]
    total = len(remaining) + len(done_set) + len(failed_set)
    print(f"📊 Need translate: {len(remaining)}, Done: {len(done_set)}, Failed: {len(failed_set)}")

    if not remaining:
        print("✅ All done!")
        return

    # Start workers
    q = queue.Queue()
    for item in remaining:
        q.put(item)

    workers = []
    for i in range(N_WORKERS):
        t = threading.Thread(target=worker, args=(q, i+1), daemon=True)
        t.start()
        workers.append(t)

    # Monitor progress
    last_done = 0
    last_check = time.time()
    last_save = time.time()
    while q.unfinished_tasks > 0 and not stopping:
        time.sleep(10)
        elapsed = time.time() - last_check
        delta = done_count - last_done
        rate = delta / elapsed if elapsed > 0 else 0
        last_done = done_count
        last_check = time.time()
        remaining_count = q.unfinished_tasks
        rate_per_worker = rate * N_WORKERS
        eta_s = remaining_count / rate_per_worker if rate_per_worker > 0 else 0
        print(f"  ⏳ {done_count} done, {fail_count} failed, {remaining_count} left (~{rate_per_worker:.1f}/s, ETA {eta_s/3600:.1f}h)")
        
        # Save checkpoint every 30s
        if time.time() - last_save > 30:
            p = load_progress()
            # Mark done chapters
            done_list = sorted([r[1] for r in remaining[:done_count]])
            p['done'] = sorted(set(p.get('done', []) + done_list))
            save_progress(p)
            last_save = time.time()

    for t in workers:
        t.join(timeout=5)

    progress['done'] = sorted(done_set)
    progress['failed'] = sorted(failed_set)
    progress['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    save_progress(progress)
    print(f"\n🏁 Done! Success: {done_count}, Failed: {fail_count}")

if __name__ == '__main__':
    from datetime import datetime
    try:
        main()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
