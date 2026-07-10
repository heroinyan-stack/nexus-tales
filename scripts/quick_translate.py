#!/usr/bin/env python3
"""
Quick translate remaining clean chapters (no EN, not garbled).
Runs until done or interrupted.
"""
import json, os, time, signal, sys, urllib.request, urllib.parse

CHAPTERS_DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'chapters')

def translate(text, timeout=15):
    params = {'client': 'gtx', 'sl': 'zh-CN', 'tl': 'en', 'dt': 't', 'q': text[:1800]}
    url = 'https://translate.googleapis.com/translate_a/single?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                resp = r.read().decode('utf-8')
            break
        except Exception as e:
            if attempt == 3: raise
            time.sleep(2 * (attempt + 1))
    parsed = json.loads(resp)
    return ''.join(seg[0] for seg in parsed[0] if seg and seg[0])

def find_remaining():
    remaining = []
    for root, dirs, files in os.walk(CHAPTERS_DIR):
        for fname in files:
            if not fname.endswith('.json'): continue
            fp = os.path.join(root, fname)
            try:
                with open(fp) as f: ch = json.load(f)
                if ch.get('_garbled'): continue
                if ch.get('content_en') or ch.get('translated'): continue
                zh = ch.get('content_zh', ch.get('content', ''))
                if zh and sum(1 for c in zh[:500] if '\u4e00' <= c <= '\u9fff') > 20:
                    remaining.append((fp, zh))
            except: pass
    return remaining

remaining = find_remaining()
print(f"📊 Remaining to translate: {len(remaining)}")
if not remaining:
    print("✅ All done!")
    sys.exit(0)

for i, (fp, zh) in enumerate(remaining):
    try:
        chunks = [zh[j:j+1400] for j in range(0, len(zh), 1400)]
        en_parts = [translate(c) for c in chunks]
        with open(fp) as f: ch = json.load(f)
        ch['content_en'] = ''.join(en_parts)
        ch['translated'] = True
        with open(fp, 'w') as f: json.dump(ch, f, ensure_ascii=False, indent=2)
        print(f"  ✅ [{i+1}/{len(remaining)}] {os.path.basename(fp)}")
        time.sleep(0.5)
    except Exception as e:
        print(f"  ❌ [{i+1}/{len(remaining)}] {os.path.basename(fp)}: {e}")
        time.sleep(2)

print(f"\n🏁 Done! {len(remaining)} processed")
