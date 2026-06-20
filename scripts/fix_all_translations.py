#!/usr/bin/env python3
"""
批量翻译修复：googletrans 版
- 章节 content_en → 翻译 content_zh
- novels.json title_en / description_en
"""

import json, os, sys, time, re

from googletrans import Translator

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAP_DIR = os.path.join(BASE, "data", "chapters")
NOVELS_FILE = os.path.join(BASE, "data", "novels.json")
DELAY = 0.5

translator = Translator()

def is_chinese(text):
    if not text: return False
    cn = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    return cn > 10 and cn / max(len(text), 1) > 0.3

def trans(text, retries=3):
    """翻译中文→英文，重试机制"""
    text = text[:4000] if len(text) > 4000 else text
    if not text.strip(): return ""
    for attempt in range(retries):
        try:
            result = translator.translate(text, src='zh-cn', dest='en')
            en = result.text if result else ""
            cn = sum(1 for c in en if '\u4e00' <= c <= '\u9fff')
            if cn > len(en) * 0.3 or len(en) < 40:
                if attempt < retries - 1:
                    time.sleep(3)
                    continue
            return en
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(5)
            else:
                return ""
    return ""

# ── Step 1: 扫描 ──
print("=" * 60)
print("Step 1: Scanning chapters...")
sys.stdout.flush()

to_trans = []
for ndir in sorted(os.listdir(CHAP_DIR)):
    dp = os.path.join(CHAP_DIR, ndir)
    if not os.path.isdir(dp): continue
    for fn in sorted(os.listdir(dp)):
        if not fn.endswith('.json'): continue
        fp = os.path.join(dp, fn)
        try:
            with open(fp) as f: ch = json.load(f)
        except: continue
        en = ch.get('content_en','')
        if is_chinese(en):
            zh = ch.get('content_zh','')
            src = zh if is_chinese(zh) else en
            to_trans.append((fp, ch, src))

print(f"  {len(to_trans)} chapters with CN in content_en")
sys.stdout.flush()

# ── Step 2: 翻译章节 ──
print("\n" + "=" * 60)
print("Step 2: Translating chapters...")
sys.stdout.flush()

ok = fail = 0
total = len(to_trans)
for i, (fp, ch, zh) in enumerate(to_trans):
    n = i + 1
    slug = ch.get('slug','?')
    num = ch.get('num','?')
    
    en_text = trans(zh)
    
    if not en_text or len(en_text) < 40:
        fail += 1
        print(f"  [{n}/{total}] {slug} ch{num} ❌ FAIL")
    else:
        ch['content_en'] = en_text
        if not ch.get('content_zh') or not is_chinese(ch.get('content_zh','')):
            ch['content_zh'] = zh
        with open(fp, 'w', encoding='utf-8') as f:
            json.dump(ch, f, ensure_ascii=False, indent=2)
        ok += 1
        if n % 20 == 0:
            print(f"  [{n}/{total}] {slug} ch{num} ✅ ({ok} ok, {fail} fail)")
    sys.stdout.flush()
    time.sleep(DELAY)

print(f"\n  Chapters: {ok} translated, {fail} failed")

# ── Step 3: novels.json ──
print("\n" + "=" * 60)
print("Step 3: Fixing novel metadata...")
sys.stdout.flush()

with open(NOVELS_FILE) as f:
    data = json.load(f)

novels = data if isinstance(data, list) else data.get('novels', [])
title_ok = desc_ok = 0

for i, nov in enumerate(novels):
    title = nov.get('title_en','')
    desc = nov.get('description_en','')
    
    if title and is_chinese(title):
        cn_title = nov.get('title_cn', title)
        en = trans(cn_title[:200])
        if en and len(en) > 1:
            nov['title_en'] = en
            title_ok += 1
            if title_ok % 30 == 0:
                print(f"  [{title_ok}] {en[:60]}...")
        time.sleep(DELAY/2)
    
    if desc and is_chinese(desc):
        en_desc = trans(desc[:500])
        if en_desc and len(en_desc) > 20:
            nov['description_en'] = en_desc
            desc_ok += 1
        time.sleep(DELAY/2)

with open(NOVELS_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"  Titles: {title_ok} updated | Descriptions: {desc_ok} updated")

print(f"\n✓ DONE: {ok} chapters + {title_ok} titles + {desc_ok} descriptions")
