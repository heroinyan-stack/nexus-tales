#!/usr/bin/env python3
"""
Retranslate fake translations (content_en is Chinese) using OpenClaw CLI.
Uses `openclaw infer model run` which handles auth automatically via the gateway.
"""
import json, os, time, signal, sys, subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CHAPTERS_DIR = os.path.join(SCRIPT_DIR, '..', 'data', 'chapters')
PROGRESS_FILE = os.path.join(SCRIPT_DIR, '..', 'data', 'retranslate_progress.json')

stopping = False
def sig_handler(sig, frame):
    global stopping
    stopping = True
    print("\n🛑 Stopping after current chapter...")
signal.signal(signal.SIGTERM, sig_handler)
signal.signal(signal.SIGINT, sig_handler)

def is_chinese(text, threshold=0.3):
    if not text:
        return False
    sample = text[:500]
    if len(sample) == 0:
        return False
    cn_chars = sum(1 for c in sample if '\u4e00' <= c <= '\u9fff')
    return cn_chars / len(sample) > threshold

def translate_via_cli(text, mode='content'):
    """Translate Chinese text to English via openclaw CLI."""
    if mode == 'title':
        prompt = f"Translate this Chinese chapter title to English. Return ONLY the English title, no quotes, no explanation, no other text:\n\n{text}"
    else:
        # Truncate very long text to avoid CLI issues
        if len(text) > 8000:
            text = text[:8000] + "\n\n[TRUNCATED - translate what you can]"
        prompt = f"Translate the following Chinese novel chapter content to English. Return ONLY the translation, no explanation, no notes, no Chinese text:\n\n{text}"
    
    # Use openclaw infer model run
    result = subprocess.run(
        ['openclaw', 'infer', 'model', 'run',
         '--model', 'qclaw/pool-deepseek-v4-pro',
         '--prompt', prompt,
         '--json'],
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, 'OPENCLAW_LOG_LEVEL': 'error'}
    )
    
    if result.returncode != 0:
        raise Exception(f"CLI error: {result.stderr[:200]}")
    
    # Parse JSON output - find the JSON line in stdout
    output = result.stdout.strip()
    # Find JSON object in output (may have extra text before/after)
    for line in output.split('\n'):
        line = line.strip()
        if line.startswith('{') and line.endswith('}'):
            try:
                data = json.loads(line)
                if data.get('ok') and 'outputs' in data:
                    return data['outputs'][0]['text'].strip()
            except json.JSONDecodeError:
                continue
    
    # Fallback: try to parse entire output
    try:
        data = json.loads(output)
        if data.get('ok') and 'outputs' in data:
            return data['outputs'][0]['text'].strip()
    except (json.JSONDecodeError, KeyError):
        pass
    
    # Last resort: return output as-is
    return output.strip()

def translate_text(text, mode='content', max_retries=2):
    """Translate with retry."""
    for attempt in range(max_retries):
        try:
            result = translate_via_cli(text, mode)
            if result and len(result) > 5:
                return result
        except Exception as e:
            print(f"  ⚠️ API error (attempt {attempt+1}): {e}")
            time.sleep(3 * (attempt + 1))
    return None

def main():
    # Load progress
    progress = {}
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            progress = json.load(f)
    
    done_count = progress.get('done', 0)
    failed_list = progress.get('failed', [])
    done_list = progress.get('done_list', [])
    
    if done_count > 0:
        print(f"📊 Resuming: {done_count} done, {len(failed_list)} failed")
    
    # Collect all fake translations
    fake_chapters = []
    for novel_dir in sorted(os.listdir(CHAPTERS_DIR)):
        novel_path = os.path.join(CHAPTERS_DIR, novel_dir)
        if not os.path.isdir(novel_path):
            continue
        for fn in sorted(os.listdir(novel_path)):
            if not fn.startswith('ch-') or not fn.endswith('.json'):
                continue
            fp = os.path.join(novel_path, fn)
            try:
                ch = json.load(open(fp))
            except:
                continue
            
            ce = ch.get('content_en', '')
            cn = ch.get('content') or ch.get('content_zh') or ''
            
            if not ce or not cn:
                continue
            
            if is_chinese(ce):
                fake_chapters.append({
                    'path': fp,
                    'novel': novel_dir,
                    'file': fn,
                    'cn_text': cn,
                    'title_cn': ch.get('title', ''),
                })
    
    print(f"🔍 Found {len(fake_chapters)} chapters with fake translations")
    
    done_set = set(done_list)
    failed_set = set(failed_list)
    
    for i, ch in enumerate(fake_chapters):
        if stopping:
            break
        
        ch_path = f"data/chapters/{ch['novel']}/{ch['file']}"
        if ch_path in done_set:
            print(f"\n  ⏭️ [{i+1}/{len(fake_chapters)}] SKIPPED (already done): {ch['novel']}/{ch['file']}")
            continue
        
        print(f"\n📖 [{i+1}/{len(fake_chapters)}] {ch['novel']}/{ch['file']}")
        print(f"   Title: {ch['title_cn'][:60]}")
        
        # Translate title
        title_en = None
        if ch['title_cn'] and is_chinese(ch['title_cn']):
            title_en = translate_text(ch['title_cn'], mode='title')
            if title_en:
                print(f"   Title EN: {title_en[:80]}")
        
        # Translate content (in chunks if long)
        cn_text = ch['cn_text']
        content_en = None
        if cn_text:
            max_chunk = 3000
            if len(cn_text) <= max_chunk:
                content_en = translate_text(cn_text, mode='content')
            else:
                parts = []
                for j in range(0, len(cn_text), max_chunk):
                    chunk = cn_text[j:j+max_chunk]
                    if not is_chinese(chunk):
                        parts.append(chunk)
                        continue
                    part = translate_text(chunk, mode='content')
                    if part is None:
                        print(f"  ⚠️ Chunk {j//max_chunk+1} failed, aborting chapter")
                        content_en = None
                        break
                    parts.append(part)
                    time.sleep(0.5)
                content_en = '\n'.join(parts)
        
        if content_en and not is_chinese(content_en):
            try:
                chapter_data = json.load(open(ch['path']))
                if title_en:
                    chapter_data['title_en'] = title_en
                chapter_data['content_en'] = content_en
                chapter_data['translated'] = True
                json.dump(chapter_data, open(ch['path'], 'w'), ensure_ascii=False, indent=2)
                done_count += 1
                done_list.append(ch_path)
                print(f"   ✅ Translated and saved")
            except Exception as e:
                print(f"   ❌ Save error: {e}")
                failed_list.append(ch['path'])
        else:
            print(f"   ⚠️ Translation failed or still Chinese, skipped")
            failed_list.append(ch['path'])
        
        # Save progress
        progress['done'] = done_count
        progress['done_list'] = done_list
        progress['failed'] = failed_list
        progress['total'] = len(fake_chapters)
        progress['last_update'] = time.strftime('%Y-%m-%d %H:%M:%S')
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
        
        time.sleep(1)  # rate limiting
    
    print(f"\n🏁 Done: {done_count}/{len(fake_chapters)} translated")
    if failed_list:
        print(f"⚠️ {len(failed_list)} failures saved to progress file")
    
    if stopping:
        progress['done'] = done_count
        progress['done_list'] = done_list
        progress['failed'] = failed_list
        progress['total'] = len(fake_chapters)
        progress['last_update'] = time.strftime('%Y-%m-%d %H:%M:%S')
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
        print("💾 Progress saved, resume later")

if __name__ == '__main__':
    main()
