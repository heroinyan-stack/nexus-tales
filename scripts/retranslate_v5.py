#!/usr/bin/env python3
"""
v5b: Direct Google Translate API calls with timeout + retry.
No deep-translator dependency issues. 15s timeout per request.
"""
import json, os, time, signal, sys
import urllib.request, urllib.parse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CHAPTERS_DIR = os.path.join(SCRIPT_DIR, '..', 'data', 'chapters')
PROGRESS_FILE = os.path.join(SCRIPT_DIR, '..', 'data', 'retranslate_progress.json')
TRANSLATE_URL = "https://translate.googleapis.com/translate_a/single"

stopping = False

def sig_handler(sig, frame):
    global stopping
    stopping = True
    sys.stderr.write("\n🛑 Stopping after current chapter...\n")
    sys.stderr.flush()
signal.signal(signal.SIGTERM, sig_handler)
signal.signal(signal.SIGINT, sig_handler)

# --- Translation ---
def is_chinese(text, threshold=0.3):
    if not text:
        return False
    sample = text[:500]
    if not sample:
        return False
    cn = sum(1 for c in sample if '\u4e00' <= c <= '\u9fff')
    return cn / len(sample) > threshold

def translate_via_google(text, source='zh-CN', target='en', timeout=15):
    """Direct Google Translate API call with timeout."""
    params = urllib.parse.urlencode({
        'client': 'gtx',
        'sl': source,
        'tl': target,
        'dt': 't',
        'q': text
    })
    url = f"{TRANSLATE_URL}?{params}"
    
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
    })
    
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        raise Exception(f"HTTP {e.code}: {body[:200]}")
    except urllib.error.URLError as e:
        raise Exception(f"URLError: {e.reason}")
    except json.JSONDecodeError as e:
        raise Exception(f"JSON decode error: {e}")
    
    # Parse response: [[["translated text","original",...]],...]
    if not data or not isinstance(data, list) or not data[0]:
        raise Exception("Empty response")
    
    parts = []
    for segment in data[0]:
        if segment and len(segment) > 0:
            parts.append(segment[0])
    
    result = ''.join(parts)
    if not result or len(result.strip()) < 3:
        raise Exception(f"Translation too short: {repr(result[:50])}")
    return result

def translate_text(text, max_retries=5):
    """Translate Chinese -> English with retry + exponential backoff."""
    if not text or not text.strip():
        return text
    
    # Split very long texts
    if len(text) > 4000:
        return translate_long_text(text, max_retries)
    
    for attempt in range(max_retries):
        try:
            result = translate_via_google(text)
            if result and len(result.strip()) > 3:
                return result.strip()
        except Exception as e:
            err_msg = str(e)
            if 'HTTP 429' in err_msg or 'Too Many' in err_msg:
                wait = min(60, 5 * (2 ** attempt))
                sys.stderr.write(f"  ⚠️ Rate limited, waiting {wait}s...\n")
                sys.stderr.flush()
                time.sleep(wait)
            elif 'timed out' in err_msg.lower() or 'URLError' in err_msg:
                time.sleep(3 * (attempt + 1))
            else:
                sys.stderr.write(f"  ⚠️ Translation error (attempt {attempt+1}): {err_msg[:120]}\n")
                sys.stderr.flush()
                if attempt < max_retries - 1:
                    time.sleep(2 * (attempt + 1))
    return None

def translate_long_text(text, max_retries=5):
    """Split long text into chunks under 4000 chars at paragraph boundaries."""
    paragraphs = text.split('\n')
    chunks = []
    current = ""
    for p in paragraphs:
        p = p.strip()
        if not p:
            if current:
                chunks.append(current)
                current = ""
            continue
        if len(current) + len(p) + 1 < 4000:
            current = (current + '\n' + p) if current else p
        else:
            if current:
                chunks.append(current)
            current = p
    if current:
        chunks.append(current)
    
    if len(chunks) <= 1:
        return translate_text(text, max_retries)
    
    results = []
    for chunk in chunks:
        translated = translate_text(chunk, max_retries)
        if translated:
            results.append(translated)
        else:
            return None
        time.sleep(0.3)
    
    return '\n'.join(results)

# --- Main ---
def main():
    progress = {}
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            progress = json.load(f)
    
    done_set = set()
    failed_set = set()
    total_processed = 0
    
    if progress.get('translator') == 'googletrans':
        for p in progress.get('done_list', []):
            done_set.add(os.path.normpath(os.path.abspath(p)))
        for p in progress.get('failed', []):
            failed_set.add(os.path.normpath(os.path.abspath(p)))
        total_processed = progress.get('done', 0)
        sys.stderr.write(f"📊 Resuming: {total_processed} done, {len(failed_set)} failed\n")
        sys.stderr.flush()
    else:
        sys.stderr.write("📊 Starting fresh with Google Translate API\n")
        sys.stderr.flush()
        # Import previously done from v4
        for p in progress.get('done_list', []):
            fp = os.path.normpath(os.path.abspath(p))
            if os.path.exists(fp):
                try:
                    ch = json.load(open(fp))
                    ce = ch.get('content_en', '')
                    if ce and not is_chinese(ce):
                        done_set.add(fp)
                        total_processed += 1
                except:
                    pass
        if total_processed > 0:
            sys.stderr.write(f"📊 Found {total_processed} already-translated from v4\n")
            sys.stderr.flush()
    
    # Scan for fake chapters
    fake_chapters = []
    for novel_dir in sorted(os.listdir(CHAPTERS_DIR)):
        novel_path = os.path.join(CHAPTERS_DIR, novel_dir)
        if not os.path.isdir(novel_path):
            continue
        for fn in sorted(os.listdir(novel_path)):
            if not fn.startswith('ch-') or not fn.endswith('.json'):
                continue
            fp = os.path.join(novel_path, fn)
            norm_fp = os.path.normpath(os.path.abspath(fp))
            
            if norm_fp in done_set or norm_fp in failed_set:
                continue
            
            try:
                ch = json.load(open(fp))
            except:
                continue
            
            ce = ch.get('content_en', '')
            cn = ch.get('content_zh') or ch.get('content') or ''
            
            if not ce or not cn:
                continue
            
            if is_chinese(ce):
                fake_chapters.append((novel_dir, fn, fp, ch, cn))
    
    total = len(fake_chapters)
    sys.stderr.write(f"📚 {total} chapters remaining\n")
    sys.stderr.flush()
    
    if total == 0:
        sys.stderr.write("✨ All done!\n")
        sys.stderr.flush()
        return
    
    save_every = 10
    new_done = [os.path.normpath(os.path.abspath(p)) for p in done_set]
    new_failed = [os.path.normpath(os.path.abspath(p)) for p in failed_set]
    
    for i, (novel_dir, fn, fp, ch, cn) in enumerate(fake_chapters):
        if stopping:
            sys.stderr.write("\n🛑 Stopped by signal\n")
            sys.stderr.flush()
            break
        
        title = ch.get('title', fn)
        norm_fp = os.path.normpath(os.path.abspath(fp))
        idx = total_processed + i + 1
        
        sys.stderr.write(f"📖 [{idx}/{total_processed + total}] {novel_dir}/{fn}\n")
        sys.stderr.write(f"   Title: {title}\n")
        sys.stderr.flush()
        
        # Translate content
        content_en = translate_text(cn)
        
        if content_en and not is_chinese(content_en, threshold=0.15):
            # Translate title if needed
            title_en = ch.get('title_en', '')
            if not title_en or is_chinese(title_en):
                try:
                    title_en = translate_via_google(title)
                    time.sleep(0.3)
                except:
                    title_en = None
            
            ch['content_en'] = content_en
            if title_en:
                ch['title_en'] = title_en
            
            tmp = fp + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(ch, f, ensure_ascii=False)
            os.replace(tmp, fp)
            
            new_done.append(norm_fp)
            total_processed += 1
            sys.stderr.write(f"   ✅ ({len(content_en)} chars)\n")
            sys.stderr.flush()
        else:
            new_failed.append(norm_fp)
            sys.stderr.write(f"   ❌ Failed\n")
            sys.stderr.flush()
        
        # Save progress
        if (i + 1) % save_every == 0 or i == len(fake_chapters) - 1:
            progress_data = {
                'done': total_processed,
                'total': total_processed + total - (i + 1),
                'failed': new_failed,
                'done_list': new_done,
                'last_update': time.strftime('%Y-%m-%d %H:%M:%S'),
                'translator': 'googletrans'
            }
            with open(PROGRESS_FILE, 'w') as f:
                json.dump(progress_data, f)
        
        time.sleep(1.5)
    
    sys.stderr.write(f"\n🏁 Done! {total_processed} translated, {len(new_failed)} failed\n")
    sys.stderr.flush()

if __name__ == "__main__":
    main()
