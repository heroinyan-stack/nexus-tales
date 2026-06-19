#!/usr/bin/env python3
"""Batch translate CN→EN using googletrans (works from China)."""
import json, os, time, sys
from googletrans import Translator

def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ch_root = os.path.join(base, 'data/chapters')
    
    todo = []
    for ndir in sorted(os.listdir(ch_root)):
        dp = os.path.join(ch_root, ndir)
        if not os.path.isdir(dp): continue
        for fn in sorted(os.listdir(dp)):
            if not fn.endswith('.json'): continue
            fp = os.path.join(dp, fn)
            try:
                with open(fp) as f: ch = json.load(f)
            except: continue
            zh = ch.get('content_zh','')
            en = ch.get('content_en','')
            if zh and len(zh)>300 and (not en or len(en)<200):
                todo.append((fp, ch, zh))
    
    print(f"📚 {len(todo)} chapters (~{sum(len(z)//1000 for _,_,z in todo)}k chars total)")
    
    # Rework: translate chapter as whole (googletrans handles long text internally)
    translator = Translator()
    ok = 0; fail = 0
    
    for i, (fp, ch, zh) in enumerate(todo):
        slug = ch.get('slug','?'); num = ch.get('num','?')
        n = i+1; total = len(todo)
        
        # Truncate very long chapters to first 4500 chars (Google limit)
        text_to_translate = zh[:4500]
        
        try:
            result = translator.translate(text_to_translate, src='zh-cn', dest='en')
            en_text = result.text if result else ""
            
            cn_ratio = sum(1 for c in en_text if '\u4e00'<=c<='\u9fff') / max(len(en_text),1)
            if cn_ratio > 0.3 or len(en_text) < 50:
                print(f"[{n}/{total}] {slug} ch{num} ❌ quality({len(en_text)}c,{cn_ratio:.0%}CN)", flush=True)
                fail += 1
                continue
            
            ch['content_en'] = en_text
            with open(fp, 'w') as f: json.dump(ch, f, ensure_ascii=False, indent=2)
            ok += 1
            preview = en_text[:120].replace('\n',' ')
            print(f"[{n}/{total}] {slug} ch{num} ✅ {preview}...", flush=True)
            
        except Exception as e:
            err = str(e)[:80]
            print(f"[{n}/{total}] {slug} ch{num} ❌ {err}", flush=True)
            fail += 1
            time.sleep(1)
        
        time.sleep(0.5)
    
    print(f"\n✅ {ok} | ❌ {fail} | chapters now with EN: see below")

if __name__ == '__main__':
    main()
