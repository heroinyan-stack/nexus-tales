#!/usr/bin/env python3
"""Re-translate chapters where content_en is still Chinese (fake translations)."""
import json, os, sys, time, signal

CHAPTERS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'chapters')
PROGRESS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'retranslate_progress.json')

stopping = False

def sig_handler(sig, frame):
    global stopping
    stopping = True
    print("\n🛑 Stopping after current chapter...")

signal.signal(signal.SIGTERM, sig_handler)
signal.signal(signal.SIGINT, sig_handler)

def is_chinese(text, threshold=0.3):
    """Check if text is predominantly Chinese."""
    if not text:
        return False
    sample = text[:500]
    if len(sample) == 0:
        return False
    cn_chars = sum(1 for c in sample if '\u4e00' <= c <= '\u9fff')
    return cn_chars / len(sample) > threshold

def is_garbled(text):
    """Check if text has mojibake (garbled encoding).
    Detection: Garbled CJK text has many DIFFERENT Latin-1 supplement chars (0xA0-0xFF)
    alongside CJK, caused by encoding mismatch. Normal Chinese may have NO-BREAK SPACE
    (U+00A0) from web scraping, which is NOT garbled."""
    if not text: return False
    if len(text) < 10: return False
    sample = text[:500]
    cjk = sum(1 for c in sample if '\u4e00' <= c <= '\u9fff' or '\u3400' <= c <= '\u4dbf')
    if cjk == 0:
        return False  # No CJK means not garbled CJK text
    # Count UNIQUE Latin-1 supplement codepoints (0xA0-0xFF)
    latin_unique = set()
    for c in sample:
        o = ord(c)
        if 0xA0 <= o <= 0xFF:
            latin_unique.add(o)
    # Garbled: 3+ unique Latin-ext codepoints means encoding mismatch
    # (Normal Chinese at most has U+00A0 no-break space)
    return len(latin_unique) >= 3

def translate_text(translator, text):
    """Translate Chinese text to English using googletrans (Google Translate non-official), with retry."""
    if not text:
        return text
    if not is_chinese(text):
        return text  # already English
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Use googletrans (non-official Google Translate API)
            from googletrans import Translator
            t = Translator()
            result = t.translate(text, src='zh-CN', dest='en').text
            if result and len(result) > 10 and not is_chinese(result, 0.2):
                return result
            print(f"  ⚠️ API returned Chinese, retry {attempt+1}/{max_retries}")
            time.sleep(3 * (attempt + 1))
        except Exception as e:
            print(f"  ⚠️ API error (attempt {attempt+1}): {e}")
            time.sleep(3 * (attempt + 1))
    
    print("  ❌ Failed after all retries")
    return None

def main():
    # No translator instance needed - deep-translator creates its own
    translator = None
    
    # Load progress
    progress = {}
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            progress = json.load(f)
    
    done_count = progress.get('done', 0)
    failed_list = progress.get('failed', [])
    
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
    
    if done_count >= len(fake_chapters):
        print("✅ All chapters already processed!")
        return
    
    failed_set = set(failed_list)
    
    # Process
    batch_size = 5  # Small batch to avoid rate limits
    for i, ch in enumerate(fake_chapters):
        if i < done_count:
            continue
        if stopping:
            break
        
        # Skip known-failed chapters (garbled dirs, etc.) — path-based
        ch_path = f"data/chapters/{ch['novel']}/{ch['file']}"
        if ch_path in failed_set:
            print(f"\n  ⏭️ [{i+1}/{len(fake_chapters)}] SKIPPED (known failed): {ch['novel']}/{ch['file']}")
            continue
        
        print(f"\n📖 [{i+1}/{len(fake_chapters)}] {ch['novel']}/{ch['file']}")
        print(f"   Title: {ch['title_cn'][:60]}")
        
        cn_text = ch['cn_text']
        
        # Translate title
        title_en = None
        if ch['title_cn'] and is_chinese(ch['title_cn']):
            title_en = translate_text(translator, ch['title_cn'])
            if title_en:
                print(f"   Title EN: {title_en[:60]}")
        
        # Translate content
        content_en = None
        if cn_text:
            max_chunk = 4000
            if len(cn_text) <= max_chunk:
                content_en = translate_text(translator, cn_text)
            else:
                # Split into chunks
                parts = []
                for j in range(0, len(cn_text), max_chunk):
                    chunk = cn_text[j:j+max_chunk]
                    if not is_chinese(chunk):
                        parts.append(chunk)
                        continue
                    part = translate_text(translator, chunk)
                    if part is None:
                        # Chunk failed - abort this chapter entirely
                        print(f"  ⚠️ Chunk {j//max_chunk+1}/{len(cn_text)//max_chunk+1} failed, aborting chapter")
                        content_en = None
                        break
                    else:
                        parts.append(part)
                    time.sleep(1)
                content_en = ''.join(parts)
        
        if content_en and not is_chinese(content_en):
            # Save
            try:
                chapter_data = json.load(open(ch['path']))
                if title_en:
                    chapter_data['title_en'] = title_en
                chapter_data['content_en'] = content_en
                chapter_data['translated'] = True
                json.dump(chapter_data, open(ch['path'], 'w'), ensure_ascii=False, indent=2)
                done_count += 1
                print(f"   ✅ Translated and saved")
            except Exception as e:
                print(f"   ❌ Save error: {e}")
                failed_list.append(ch['path'])
        else:
            print(f"   ⚠️ Translation failed or still Chinese, skipped")
            failed_list.append(ch['path'])
        
        # Save progress
        progress['done'] = done_count
        progress['failed'] = failed_list
        progress['total'] = len(fake_chapters)
        progress['last_update'] = time.strftime('%Y-%m-%d %H:%M:%S')
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
        
        # Rate limiting - longer delay to avoid API blocks
        time.sleep(4)
    
    print(f"\n🏁 Done: {done_count}/{len(fake_chapters)} translated")
    if failed_list:
        print(f"⚠️ {len(failed_list)} failures saved to progress file")
    
    if stopping:
        # Save progress for resume
        progress['done'] = done_count
        progress['failed'] = failed_list
        progress['total'] = len(fake_chapters)
        progress['last_update'] = time.strftime('%Y-%m-%d %H:%M:%S')
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
        print("💾 Progress saved, resume later")

if __name__ == '__main__':
    main()
