#!/usr/bin/env python3
"""
Re-crawl remaining chapters for 文豪1978：从军旅作家开始 from bxwx9.org.
The bxwx9_daily.py only got 27/102 because the novel wasn't in novels.json with a bxwx9 source_url.
This script directly targets the novel index page and pulls all missing chapters.
"""
import json, re, time, os, subprocess, ssl, urllib.request, sys

# Config
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(SCRIPT_DIR, '..')
CHAPTERS_DIR = os.path.join(PROJECT_DIR, 'data', 'chapters', '文豪1978_从军旅作家开始')
NOVEL_INDEX_URL = 'https://www.bxwx9.org/b/135/135119/'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
DELAY = 0.6  # seconds between requests

def log(msg):
    print(msg, flush=True)

def fetch(url, referer=None):
    """Fetch URL with curl (most reliable for Chinese sites)."""
    cmd = ['curl', '-sk', '--max-time', '30', '--connect-timeout', '10', '-A', UA]
    if referer:
        cmd += ['-H', f'Referer: {referer}']
    cmd.append(url)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
    if r.returncode != 0:
        raise Exception(f"curl rc={r.returncode}")
    return r.stdout

def clean_text(raw):
    text = re.sub(r'<script[^>]*>.*?</script>', '', raw, flags=re.S)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.S)
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.I)
    text = re.sub(r'</?p[^>]*>', '\n', text, flags=re.I)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&nbsp;', '').replace('&lt;', '<').replace('&gt;', '>')
    for pat in [
        r'本站所有收录.*?删除。', r'笔下文学网.*?小说迷。',
        r'努力打造最干净.*', r'请记住本书首发域名.*',
        r'天才一秒记住.*', r'手机用户请浏览.*',
        r'温馨提示.*?bsp;.*', r'如果您喜欢.*?推荐.*',
        r'--&gt;&gt;.*', r'第\(\d+/\d+\)页', r'&gt;&gt;.*',
        r'\w+\([^)]*\)\s*;?', r'-->', r'&lt;!--',
    ]:
        text = re.sub(pat, '', text, flags=re.S)
    lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) > 2]
    return '\n'.join(lines)

def extract_content(html):
    idx = html.find('关灯')
    if idx < 0:
        idx = html.find('content"')
    if idx < 0:
        main = html
    else:
        main = html[idx:idx + 12000]
    return clean_text(main)

def get_existing():
    if not os.path.isdir(CHAPTERS_DIR):
        return set()
    return {int(re.search(r'ch-(\d+)', f).group(1))
            for f in os.listdir(CHAPTERS_DIR)
            if f.endswith('.json') and re.search(r'ch-(\d+)', f)}

def main():
    existing = get_existing()
    log(f"=== 文豪1978 Re-Crawl ===")
    log(f"  Existing chapters: {len(existing)} (nos {sorted(existing)[:5]}...{sorted(existing)[-3:] if len(existing) > 3 else ''})")
    
    # Fetch chapter list from novel index page
    log(f"\n  Fetching chapter list from index page...")
    try:
        html = fetch(NOVEL_INDEX_URL)
    except Exception as e:
        log(f"  ❌ Failed to fetch index: {e}")
        sys.exit(1)
    
    chapters = re.findall(r'href="(/b/\d+/\d+/\d+\.html)"[^>]*>([^<]+)<', html)
    log(f"  Found {len(chapters)} chapters on site")
    
    if not chapters:
        log("  ❌ No chapter links found!")
        # Try alternative pattern
        chapters = re.findall(r'href=[\'"](/b/\d+/\d+/\d+\.html)[\'"][^>]*>([^<]+)<', html)
        log(f"  Alt pattern: {len(chapters)} chapters")
    
    if not chapters:
        log("  Showing HTML snippet for debug:")
        log(html[:2000])
        sys.exit(1)
    
    BASE = 'https://www.bxwx9.org'
    total_site = len(chapters)
    needed = total_site - len(existing)
    log(f"\n  Total on site: {total_site} | Have: {len(existing)} | Need: {needed}")
    
    if needed <= 0:
        log("  ✅ Already complete!")
        return
    
    pulled = 0
    skipped = 0
    errors = 0
    
    for i, (ch_path, ch_title) in enumerate(chapters, 1):
        if i in existing:
            skipped += 1
            continue
        
        ch_url = BASE + ch_path
        try:
            ch_html = fetch(ch_url, referer=NOVEL_INDEX_URL)
            text = extract_content(ch_html)
            
            if len(text) < 80:
                log(f"  ch-{i:04d}: too short ({len(text)} chars), skipping")
                errors += 1
                continue
            
            ch_data = {
                "title": ch_title,
                "novel_title": "文豪1978：从军旅作家开始",
                "chapter_number": i,
                "content_zh": text,
                "content_en": text,
                "source": "bxwx9",
                "source_url": ch_url,
            }
            
            os.makedirs(CHAPTERS_DIR, exist_ok=True)
            ch_path_out = os.path.join(CHAPTERS_DIR, f'ch-{i:04d}.json')
            with open(ch_path_out, 'w', encoding='utf-8') as f:
                json.dump(ch_data, f, ensure_ascii=False, indent=2)
            
            existing.add(i)
            pulled += 1
            
            if pulled % 10 == 0:
                log(f"    ... {pulled}/{needed} pulled so far")
            
            time.sleep(DELAY)
        except Exception as e:
            log(f"  ch-{i:04d}: ERR {str(e)[:80]}")
            errors += 1
            time.sleep(1)
    
    log(f"\n  📊 Results: +{pulled} new | {skipped} skipped | {errors} errors")
    log(f"  📚 Total chapters now: {len(existing)}/{total_site}")
    
    if len(existing) >= total_site:
        log("  ✅ ALL CHAPTERS PULLED!")
    else:
        log(f"  ⚠️ Still missing {total_site - len(existing)} chapters")

if __name__ == '__main__':
    main()
