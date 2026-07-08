#!/usr/bin/env python3
"""
v7: Resilient retranslate with rate-limit cooldown, restart-safe checkpointing.
Skips already-attempted chapters on restart regardless of success/fail.
"""
import json, os, time, signal, sys, random
import urllib.request, urllib.parse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CHAPTERS_DIR = os.path.join(SCRIPT_DIR, '..', 'data', 'chapters')
PROGRESS_FILE = os.path.join(SCRIPT_DIR, '..', 'data', 'retranslate_progress.json')
ATTEMPTED_FILE = os.path.join(SCRIPT_DIR, '..', 'data', 'retranslate_attempted.json')

stopping = False

def sig_handler(sig, frame):
    global stopping
    stopping = True
    sys.stderr.write("\n🛑 收到停止信号,当前章节完成后退出...\n")
    sys.stderr.flush()
signal.signal(signal.SIGTERM, sig_handler)
signal.signal(signal.SIGINT, sig_handler)

def load_attempted():
    """Load set of already-attempted chapter paths"""
    if os.path.exists(ATTEMPTED_FILE):
        with open(ATTEMPTED_FILE) as f:
            return set(json.load(f))
    return set()

def save_attempted(s):
    with open(ATTEMPTED_FILE, 'w') as f:
        json.dump(sorted(s), f)

def is_chinese(text, threshold=0.15):
    if not text: return True
    sample = text[:500]
    if not sample: return True
    cn = sum(1 for c in sample if '\u4e00' <= c <= '\u9fff')
    return cn / len(sample) > threshold

def translate_google(text, timeout=15):
    """Use batchexecute endpoint (web UI API) - no 429 rate limits."""
    chunk = text[:2000]  # batchexecute handles ~2000 chars comfortably
    payload = json.dumps([[[
        "MkEWBc",
        json.dumps([[chunk, "zh-CN", "en", True]]),
        None,
        "generic"
    ]]])
    data = ('f.req=' + urllib.parse.quote(payload)).encode()

    req = urllib.request.Request(
        'https://translate.google.com/_/TranslateWebserverUi/data/batchexecute',
        data=data,
        headers={
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        }
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        resp = r.read().decode('utf-8')

    # Parse batchexecute response
    resp = resp[resp.index('\n')+1:]
    parsed = json.loads(resp)
    inner = json.loads(parsed[0][2])

    if inner is None or not isinstance(inner, list) or len(inner) < 2:
        raise Exception("Invalid response structure")

    # Extract translated segments
    try:
        segments = inner[1][0][0][5]
        result = ''.join(seg[0] for seg in segments if seg and seg[0])
    except (IndexError, TypeError):
        raise Exception("Cannot extract translation")

    if not result or len(result.strip()) < 3:
        raise Exception(f"Too short: {len(result) if result else 0}")
    return result.strip()

def translate_chunk(text, retries=3):
    for attempt in range(retries):
        try:
            return translate_google(text)
        except Exception as e:
            err = str(e)
            if attempt < retries - 1:
                wait = 3 * (attempt + 1)
                sys.stderr.write(f"  ⚠️ 重试 {attempt+1}, wait {wait}s: {err[:80]}\n")
                sys.stderr.flush()
                time.sleep(wait)
    return None

def split_text(text):
    """Split at paragraph boundaries for texts >2000 chars."""
    if len(text) <= 2000:
        return [text]
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
        if len(current) + len(p) + 1 < 1800:
            current = (current + '\n' + p) if current else p
        else:
            if current:
                chunks.append(current)
            current = p
    if current:
        chunks.append(current)
    return chunks if chunks else [text]

def translate_text(text):
    """Full text translation with chunking."""
    chunks = split_text(text)
    results = []
    for ch in chunks:
        result = translate_chunk(ch)
        if result is None:
            return None
        results.append(result)
        if len(chunks) > 1:
            time.sleep(random.uniform(0.3, 0.7))
    return '\n'.join(results)

# ─── Main ───

def main():
    # Scan ALL chapters for missing English
    all_chapters = []
    for novel_dir in sorted(os.listdir(CHAPTERS_DIR)):
        novel_path = os.path.join(CHAPTERS_DIR, novel_dir)
        if not os.path.isdir(novel_path):
            continue
        for fn in sorted(os.listdir(novel_path)):
            if fn.startswith('ch-') and fn.endswith('.json'):
                all_chapters.append(os.path.join(novel_path, fn))

    # Find chapters needing translation
    attempted_set = load_attempted()
    need_en = []
    for fp in all_chapters:
        if fp in attempted_set:
            continue  # Skip already attempted (success or fail)
        try:
            ch = json.load(open(fp))
        except:
            continue
        ce = ch.get('content_en', '')
        cn_text = ch.get('content_zh') or ch.get('content') or ''
        if not cn_text:
            continue
        if not ce or len(ce) < 50 or is_chinese(ce):
            need_en.append(fp)

    total = len(need_en)
    skipped = len(attempted_set)
    done = len(all_chapters) - total - skipped

    sys.stderr.write(f"📊 全库扫描: {len(all_chapters)} 章, {done} 已有EN, {skipped} 已尝试跳过, {total} 需翻译\n")
    sys.stderr.flush()

    if total == 0:
        if skipped > 0:
            sys.stderr.write(f"⚠️ 还有 {skipped} 章节之前失败。删除 {ATTEMPTED_FILE} 可重试。\n")
        else:
            sys.stderr.write("✨ 全部完成!\n")
        sys.stderr.flush()
        return

    success = 0
    fail = 0

    for i, fp in enumerate(need_en):
        if stopping:
            sys.stderr.write(f"\n🛑 信号中断 (已完成 {success}, 失败 {fail})\n")
            sys.stderr.flush()
            break

        novel_dir = os.path.basename(os.path.dirname(fp))
        fn = os.path.basename(fp)

        try:
            ch = json.load(open(fp))
        except:
            fail += 1
            continue

        cn_text = ch.get('content_zh') or ch.get('content') or ''
        title = ch.get('title', fn)

        # Detect garbled (corrupted encoding) content
        if '\ufffd' in cn_text or '\ufffd' in title:
            sys.stderr.write(f"📖 [{i+1}/{total}] {novel_dir}/{fn} ({len(cn_text)}字) ⚠️ 乱码跳过\n")
            sys.stderr.flush()
            fail += 1
            # Mark for re-scrape
            ch['_garbled'] = True
            tmp = fp + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(ch, f, ensure_ascii=False)
            os.replace(tmp, fp)
            continue

        sys.stderr.write(f"📖 [{i+1}/{total}] {novel_dir}/{fn} ({len(cn_text)}字)\n")
        sys.stderr.flush()

        content_en = translate_text(cn_text)

        if content_en and not is_chinese(content_en):
            # Translate title
            title_en = ch.get('title_en', '')
            if not title_en or is_chinese(title_en):
                try:
                    title_en = translate_chunk(title[:200])
                    time.sleep(random.uniform(0.3, 0.8))
                except:
                    title_en = None

            ch['content_en'] = content_en
            if title_en:
                ch['title_en'] = title_en

            tmp = fp + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(ch, f, ensure_ascii=False)
            os.replace(tmp, fp)

            success += 1
            sys.stderr.write(f"   ✅ ({len(content_en)} chars)\n")
            sys.stderr.flush()
        else:
            fail += 1
            sys.stderr.write(f"   ❌ 失败\n")
            sys.stderr.flush()

        # Mark as attempted (regardless of success/fail)
        attempted_set.add(fp)

        # Save attempted list every 10 chapters
        if (i + 1) % 10 == 0:
            save_attempted(attempted_set)
        # Save progress every 25 chapters
        if (i + 1) % 25 == 0:
            with open(PROGRESS_FILE, 'w') as f:
                json.dump({
                    'done': done + success,
                    'total': len(all_chapters),
                    'pending': total - (i + 1),
                    'failed_count': fail,
                    'last_update': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'translator': 'googletrans+v6-full'
                }, f)

        # Delay between chapters
        if i < total - 1 and not stopping:
            time.sleep(random.uniform(1.0, 2.5))

    # Final save
    with open(PROGRESS_FILE, 'w') as f:
        json.dump({
            'done': done + success,
            'total': len(all_chapters),
            'pending': 0,
            'failed_count': fail,
            'last_update': time.strftime('%Y-%m-%d %H:%M:%S'),
            'translator': 'googletrans+v6-full'
        }, f)

    sys.stderr.write(f"\n🏁 完成! 成功: {success}, 失败: {fail}, 总计EN: {done + success}/{len(all_chapters)}\n")
    sys.stderr.flush()

if __name__ == "__main__":
    main()
