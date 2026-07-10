#!/usr/bin/env python3
"""
Fill Incomplete Novels — re-scrape missing & garbled chapters from source sites.

Reachable sites (tested):
  - quanwenyuedu.io  (plain HTML, div#content, ch URLs: /n/{slug}/{num}.html)
  - 23wx.io→23wx.tv  (base64 via qsbs.bb(), catalog: /book/{id}/ml_{N}.html)
  - 00ksw.com        (base64 via qqfsdxev.gap(), catalog: /html/{id}/ml{N}.html)
  - bxwx9.org        (plain HTML, article#font_max)

UNREACHABLE: tmwxw.net (connection timeout from this network)

Usage:
  detect                  Show missing stats by domain
  gap-hunt                List garbled novels
  fix-garbled [N]         Re-scrape N garbled novels
  fill-missing [N]        Fill N incomplete novels (worst offenders first)
  all [--delay=1.5]       Do both phases
"""

import json, os, re, sys, time, ssl, base64, subprocess
from urllib.parse import urljoin, urlparse
from collections import OrderedDict, defaultdict

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_DIR, 'data')
CHAPTERS_DIR = os.path.join(DATA_DIR, 'chapters')
NOVELS_FILE = os.path.join(DATA_DIR, 'novels.json')
STATE_FILE = os.path.join(DATA_DIR, 'fill_incomplete_state.json')

UA = 'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
UNREACHABLE = {'tmwxw.net'}


# ─── HTTP ─────────────────────────────────────────
def fetch(url, referer=None, timeout=20):
    cmd = ['curl', '-sL', '--max-time', str(timeout),
           '-H', f'User-Agent: {UA}',
           '-H', 'Accept-Language: zh-CN,zh;q=0.9',
           '--insecure']
    if referer:
        cmd += ['-H', f'Referer: {referer}']
    cmd.append(url)
    r = subprocess.run(cmd, capture_output=True, timeout=timeout + 5)
    raw = r.stdout
    head = raw[:4096]
    enc = 'utf-8'
    try:
        h = head.decode('utf-8')
        m = re.search(r'charset[="\s]+([^"\s>;]+)', h, re.I)
        if m: enc = m.group(1).lower()
    except:
        try:
            h = head.decode('gbk')
            if re.search(r'[\u4e00-\u9fff]{4,}', h): enc = 'gbk'
        except: pass
    try: return raw.decode(enc, errors='replace')
    except: return raw.decode('utf-8', errors='replace')


def head_check(url, timeout=6):
    """Quick HEAD check if URL exists"""
    r = subprocess.run(['curl', '-sI', '--max-time', str(timeout),
                        '-H', f'User-Agent: {UA}', '--insecure', url],
                       capture_output=True, timeout=timeout + 3)
    return '200 OK' in r.stdout.decode(errors='replace').split('\n')[0] if r.stdout else False


def strip_html(s):
    return re.sub(r'<[^>]*>', '', s).strip()


def clean_content(text):
    pats = [
        r'请记住本书首发域名.*', r'笔趣阁.*?网址.*', r'一秒记住.*?网址.*',
        r'手机阅读地址.*', r'本书网址.*', r'浏览阅读地址.*', r'更新最快网址.*',
        r'最快更新.*?网址.*', r'笔趣阁.*?提醒您.*', r'.*?提示您：看后求收藏.*',
        r'记住本站网址.*', r'如果您喜欢.*?收藏.*', r'笔下文学网.*', r'零点看书.*',
        r'请收藏本站.*', r'天才一秒记住.*', r'本章未完，请点击下一页继续阅读.*',
        r'第\(\d+/\d+\)页.*', r'&nbsp;', r'\r', r'喜欢本书请.*?收藏.*',
        r'热点小说网.*', r'手机用户请浏览.*', r'顶点小说.*',
        r'www\..*?\.(com|net|org|io|tv).*', r'https?://[^\s]+',
    ]
    for p in pats:
        text = re.sub(p, '', text, flags=re.I | re.M)
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    return text


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f: return json.load(f)
    return {'garbled_fixed': [], 'missing_filled': []}


def save_state(s):
    with open(STATE_FILE, 'w') as f: json.dump(s, f, ensure_ascii=False, indent=2)


# ─── SITE SCRAPERS ────────────────────────────────

# ---- quanwenyuedu.io ----
def scrape_qwy_catalog(source_url, expected_count=0):
    """quanwenyuedu.io: chapters at /n/{slug}/{N}.html, sequential.
    Uses expected_count from novels.json as hint, binary searches for actual last."""
    slug = source_url.rstrip('/').split('/')[-1] or source_url.rstrip('/').split('/')[-2]
    chapters = OrderedDict()
    novel_title = ''

    html = fetch(source_url)
    if html:
        t = re.search(r'<title>(.*?)(?:全文阅读|_,)', html)
        if t: novel_title = t.group(1).strip()

    # Determine last chapter
    last = 0
    if expected_count > 0:
        # Verify expected last chapter
        if head_check(f'https://www.quanwenyuedu.io/n/{slug}/{expected_count}.html'):
            last = expected_count
        else:
            lo, hi = 1, expected_count
            while lo < hi:
                mid = (lo + hi + 1) // 2
                if head_check(f'https://www.quanwenyuedu.io/n/{slug}/{mid}.html'):
                    lo = mid
                else: hi = mid - 1
            last = lo
    else:
        # Probe checkpoints
        for probe in [1, 10, 100, 500, 1000, 1500, 2000, 2500, 3000, 4000, 5000]:
            if head_check(f'https://www.quanwenyuedu.io/n/{slug}/{probe}.html'):
                last = probe
            elif last > 0: break

    if last == 0: return novel_title, chapters

    for n in range(1, last + 1):
        chapters[n] = {'title': f'第{n}章', 'url': f'https://www.quanwenyuedu.io/n/{slug}/{n}.html', 'num': n}
    return novel_title, chapters


def scrape_qwy_content(url):
    html = fetch(url)
    if not html: return None
    content = re.search(r'<div[^>]*id="content"[^>]*>(.*?)</div>', html, re.S)
    if content:
        text = content.group(1)
        text = re.sub(r'<br\s*/?>', '\n', text)
        text = strip_html(text)
        return clean_content(text)
    return None


# ---- 23wx.io → 23wx.tv ----
def scrape_23wx_catalog(source_url):
    """23wx → 23wx.tv: catalog at /book/{book_id}/ml_{page}.html"""
    url = source_url.replace('23wx.io', '23wx.tv')
    html = fetch(url)
    if not html: return None, {}

    t = re.search(r'<title>(.*?)(?:全文阅读|_热点小说网)', html)
    novel_title = t.group(1).strip() if t else ''

    m = re.search(r'/book/(\d+)/?', url)
    book_id = m.group(1) if m else None
    if not book_id: return novel_title, {}

    chapters = OrderedDict()
    page, max_page, empty_streak = 1, 50, 0
    while page <= max_page:
        ml_html = fetch(f'https://www.23wx.tv/book/{book_id}/ml_{page}.html', referer=url)
        if not ml_html: break
        found = 0
        for m in re.finditer(r'href="(/book/\d+/(\d+)\.html)"[^>]*>(.*?)</a>', ml_html):
            href, cid, raw = m.group(1), m.group(2), m.group(3).strip()
            ct = strip_html(raw)
            if not ct or len(ct) < 2 or 'ml_' in href or ct == '开始阅读': continue
            cid = int(cid)
            if cid not in chapters:
                chapters[cid] = {'title': ct, 'url': f'https://www.23wx.tv{href}', 'num': cid}
                found += 1
        if found == 0:
            empty_streak += 1
            if empty_streak >= 2: break
        else: empty_streak = 0
        page += 1
        time.sleep(0.2)
    return novel_title, chapters


def scrape_23wx_content(url):
    url = url.replace('23wx.io', '23wx.tv')
    html = fetch(url)
    if not html: return None
    parts = re.findall(r"qsbs\.bb\('([^']+)'\)", html)
    if parts:
        decoded = []
        for b64 in parts:
            try:
                d = base64.b64decode(b64).decode('utf-8', errors='replace')
                decoded.append(strip_html(d))
            except: pass
        if decoded: return clean_content(''.join(decoded))
    return None


# ---- 00ksw.com ----
def scrape_00ksw_catalog(source_url):
    html = fetch(source_url)
    if not html: return None, {}
    t = re.search(r'<title>(.*?)(?:免费阅读|_零点看书)', html) if html else None
    novel_title = t.group(1).strip() if t else ''

    m = re.search(r'/html/\d+/(\d+)/?', source_url) or re.search(r'/html/(\d+)/?', source_url)
    book_id = m.group(1) if m else None
    if not book_id: return novel_title, {}

    chapters = OrderedDict()
    page, empty_streak = 1, 0
    while empty_streak < 2:
        ml_html = fetch(f'https://www.00ksw.com/html/{book_id}/ml{page}.html', referer=source_url)
        if not ml_html or len(ml_html) < 500:
            empty_streak += 1; page += 1; continue
        found = 0
        for m in re.finditer(r'href="(/books/\d+/(\d+)\.html)"[^>]*>(.*?)</a>', ml_html):
            href, cid, raw = m.group(1), m.group(2), m.group(3).strip()
            ct = strip_html(raw)
            if not ct or len(ct) < 2 or 'iconfont' in ct or ct == '阅读': continue
            cid = int(cid)
            if cid not in chapters:
                chapters[cid] = {'title': ct, 'url': f'https://www.00ksw.com{href}', 'num': cid}
                found += 1
        empty_streak = 0 if found > 0 else empty_streak + 1
        page += 1
        time.sleep(0.3)
    return novel_title, chapters


def scrape_00ksw_content(url):
    html = fetch(url)
    if not html: return None
    parts = re.findall(r"qqfsdxev\.gap\('([^']+)'\)", html)
    if parts:
        decoded = []
        for b64 in parts:
            try: decoded.append(strip_html(base64.b64decode(b64).decode('utf-8', errors='replace')))
            except: pass
        if decoded: return clean_content(''.join(decoded))
    return None


# ---- bxwx9.org ----
def scrape_bxwx9_catalog(source_url):
    html = fetch(source_url)
    if not html: return None, {}
    t = re.search(r'<title>(.*?)(?:目录|最新章节|全文|_笔下文学)', html)
    novel_title = t.group(1).strip() if t else ''
    chapters = OrderedDict()
    for m in re.finditer(r'href="(/b/\d+/(\d+)/(\d+)\.html)"[^>]*>(.*?)</a>', html):
        href, _, cid, raw = m.group(1), m.group(2), m.group(3), m.group(4).strip()
        ct = strip_html(raw)
        if ct:
            n = int(cid)
            chapters[n] = {'title': ct, 'url': f'https://www.bxwx9.org{href}', 'num': n}
    return novel_title, chapters


def scrape_bxwx9_content(url):
    html = fetch(url)
    if not html: return None
    c = re.search(r'<article[^>]*>(.*?)</article>', html, re.S)
    if c:
        text = c.group(1)
        text = re.sub(r'<br\s*/?>', '\n', text)
        text = re.sub(r'<p[^>]*>', '\n', text); text = re.sub(r'</p>', '', text)
        text = strip_html(text); text = re.sub(r'&nbsp;', ' ', text)
        return clean_content(text)
    return None


# ---- Router ----
def get_handlers(url):
    if not url: return None, None
    domain = urlparse(url).netloc.lower()
    if 'quanwenyuedu.io' in domain: return scrape_qwy_catalog, scrape_qwy_content
    if '23wx' in domain: return scrape_23wx_catalog, scrape_23wx_content
    if '00ksw.com' in domain: return scrape_00ksw_catalog, scrape_00ksw_content
    if 'bxwx9.org' in domain: return scrape_bxwx9_catalog, scrape_bxwx9_content
    if 'tmwxw.net' in domain: return (lambda u: (None, {})), (lambda u: None)
    return None, None


# ─── STORAGE ──────────────────────────────────────
def count_existing(slug):
    d = os.path.join(CHAPTERS_DIR, slug)
    existing = {}
    if os.path.exists(d):
        for f in os.listdir(d):
            m = re.match(r'ch-(\d+)\.json', f)
            if m:
                n = int(m.group(1))
                try:
                    with open(os.path.join(d, f)) as fh:
                        j = json.load(fh)
                    has = bool(j.get('content_zh')) or (j.get('lines') and len(j.get('lines', [])) > 3)
                    existing[n] = {'garbled': j.get('_garbled', False), 'ok': has}
                except: pass
    return existing


def save_ch(slug, n, title, content, novel_title, source, src_url):
    d = os.path.join(CHAPTERS_DIR, slug)
    os.makedirs(d, exist_ok=True)
    fp = os.path.join(d, f'ch-{n:04d}.json')
    data = {}
    if os.path.exists(fp):
        try:
            with open(fp) as f: data = json.load(f)
        except: pass
    data.update(title=title, novel_title=novel_title, content_zh=content,
                source=source, source_url=src_url, chapter_number=n, _garbled=False)
    if 'content_en' not in data: data['content_en'] = content
    with open(fp, 'w') as f: json.dump(data, f, ensure_ascii=False, indent=2)


# ─── GARBLED FIX ──────────────────────────────────
def find_garbled():
    g = {}
    for dn in os.listdir(CHAPTERS_DIR):
        dp = os.path.join(CHAPTERS_DIR, dn)
        if not os.path.isdir(dp): continue
        for fn in os.listdir(dp):
            if fn.endswith('.json'):
                try:
                    with open(os.path.join(dp, fn)) as f:
                        j = json.load(f)
                    if j.get('_garbled'):
                        s = j.get('slug', '')
                        if s not in g: g[s] = {'cnt': 0, 'dir': dn}
                        g[s]['cnt'] += 1; g[s][fn] = j
                    break
                except: pass

    with open(NOVELS_FILE) as f: novels = json.load(f)
    for n in novels:
        s = n.get('slug', '')
        if s in g:
            g[s]['source_url'] = n.get('source_url', '')
            g[s]['title'] = n.get('title', '') or n.get('title_en', '')
    return g


def fix_garbled_novel(slug, info, delay=1.0):
    su = info.get('source_url', '')
    if not su: print('  ❌ No source_url'); return 0
    dom = urlparse(su).netloc
    if any(u in dom for u in UNREACHABLE): print(f'  ⚠ unreachable: {dom}'); return 0

    cat_fn, con_fn = get_handlers(su)
    if not cat_fn: print(f'  ❌ No handler'); return 0

    ntitle, chs = cat_fn(su)
    if not chs: print('  ❌ No chapters from source'); return 0

    print(f'  📖 {info.get("title",slug)[:30]} ({info["cnt"]} garbled, {len(chs)} cat)')

    cd = os.path.join(CHAPTERS_DIR, info.get('dir', slug))
    fixed = 0
    for fn in sorted(os.listdir(cd)):
        if not fn.endswith('.json'): continue
        fp = os.path.join(cd, fn)
        try:
            with open(fp) as f: j = json.load(f)
        except: continue
        if not j.get('_garbled'): continue

        n = j.get('num') or j.get('chapter_number')
        if not n or n not in chs: continue

        ci = chs[n]
        print(f'    🔄 ch-{n:04d}: {ci["title"][:30]}', end=' ')
        content = con_fn(ci['url'])
        if content and len(content) > 50:
            j['title'] = ci['title']; j['novel_title'] = ntitle or j.get('novel_title','')
            j['content_zh'] = content; j['source'] = dom; j['source_url'] = ci['url']
            j['_garbled'] = False; j['_fixed'] = True
            with open(fp, 'w') as f: json.dump(j, f, ensure_ascii=False, indent=2)
            fixed += 1
            print(f'✅ [{len(content)}c]')
        else: print('❌')
        time.sleep(delay)
    return fixed


# ─── MISSING FILL ─────────────────────────────────
def find_missing():
    with open(NOVELS_FILE) as f: novels = json.load(f)
    missing = []
    for n in novels:
        su = n.get('source_url', '')
        slug = n.get('slug', '')
        exp = n.get('total_chapters', 0) or n.get('totalChapters', 0)
        act_files = count_existing(slug)
        file_ok = sum(1 for v in act_files.values() if not v['garbled'] and v['ok'])
        act = max(n.get('available_chapters', 0) or n.get('chapter_count', 0) or 0, file_ok)
        gap = max(0, exp - act)
        if gap > 0 and su:
            dom = urlparse(su).netloc
            if any(u in dom for u in UNREACHABLE): continue
            cf, _ = get_handlers(su)
            if cf:
                missing.append({'slug': slug, 'title': n.get('title','') or n.get('title_en',''),
                                'exp': exp, 'act': act, 'gap': gap,
                                'source_url': su, 'expected_count': exp})
    missing.sort(key=lambda x: -x['gap'])
    return missing


def fill_missing_novel(ni, max_ch=100, delay=1.0):
    slug, su, exp = ni['slug'], ni['source_url'], ni['exp']
    cat_fn, con_fn = get_handlers(su)
    if not cat_fn: return 0

    dom = urlparse(su).netloc
    print(f'  📖 {ni["title"][:30]} ({ni["act"]}/{exp}, gap={ni["gap"]})')

    # Pass expected count for quanwenyuedu binary search optimization
    if 'quanwenyuedu.io' in dom:
        ntitle, chs = cat_fn(su, expected_count=exp)
    else:
        ntitle, chs = cat_fn(su)

    if not chs: print('  ❌ No chapters'); return 0
    print(f'     Catalog: {len(chs)} chapters')

    existing = count_existing(slug)
    to_fill = []
    for n, ci in sorted(chs.items()):
        if n not in existing or existing[n]['garbled']:
            to_fill.append((n, ci))
    to_fill = to_fill[:max_ch]

    if not to_fill:
        en = sorted(existing.keys())[:5]; cn = sorted(chs.keys())[:5]
        print(f'     Existing: {en}, Catalog: {cn}')
        return 0

    print(f'     Filling {len(to_fill)} ch ({to_fill[0][0]}-{to_fill[-1][0]})')
    filled = 0
    for n, ci in to_fill:
        print(f'    📥 ch-{n:04d}: {ci["title"][:35]}', end=' ')
        content = con_fn(ci['url'])
        if content and len(content) > 50:
            save_ch(slug, n, ci['title'], content, ntitle or ni['title'], dom.replace('www.', ''), ci['url'])
            filled += 1
            print(f'✅ [{len(content)}c]')
        else: print('❌')
        time.sleep(delay)
    return filled


# ─── UPDATE NOVELS.JSON ───────────────────────────
def update_counts():
    with open(NOVELS_FILE) as f: novels = json.load(f)
    updated = 0
    for n in novels:
        existing = count_existing(n.get('slug', ''))
        good = sum(1 for v in existing.values() if not v['garbled'] and v['ok'])
        old = n.get('available_chapters', 0) or n.get('chapter_count', 0) or 0
        if good != old:
            n['available_chapters'] = good; n['chapter_count'] = good; updated += 1
    if updated:
        import shutil; shutil.copy(NOVELS_FILE, NOVELS_FILE + '.fill_backup')
        with open(NOVELS_FILE, 'w') as f: json.dump(novels, f, ensure_ascii=False, indent=2)
        print(f'  📊 Updated {updated} novels')


# ─── CLI ──────────────────────────────────────────
def cmd_detect():
    with open(NOVELS_FILE) as f: novels = json.load(f)
    by_d = defaultdict(lambda: {'cnt': 0, 'miss': 0})
    for n in novels:
        su = n.get('source_url', '')
        if not su: continue
        d = urlparse(su).netloc
        exp = n.get('total_chapters', 0) or n.get('totalChapters', 0)
        act = n.get('available_chapters', 0) or n.get('chapter_count', 0) or 0
        by_d[d]['cnt'] += 1
        by_d[d]['miss'] += max(0, exp - act)
    print('=== Missing by Domain ===')
    for d, i in sorted(by_d.items(), key=lambda x: -x[1]['miss']):
        tag = ' ⚠UNREACHABLE' if any(u in d for u in UNREACHABLE) else ''
        print(f'  {d}: {i["miss"]:,} missing{tag}')
    reach = sum(v['miss'] for k, v in by_d.items() if not any(u in k for u in UNREACHABLE))
    print(f'  Reachable: {reach:,} missing')


def cmd_gap_hunt():
    g = find_garbled()
    print(f'=== Garbled: {len(g)} novels ===')
    ok = []; bad = []
    for s, i in g.items():
        su = i.get('source_url', '')
        if su and not any(u in urlparse(su).netloc for u in UNREACHABLE): ok.append((s, i))
        else: bad.append((s, i))
    print(f'  Recoverable: {len(ok)}')
    for s, i in sorted(ok, key=lambda x: -x[1]['cnt']):
        print(f'    {i.get("title",s)[:30]}: {i["cnt"]}ch → {i["source_url"][:60]}')
    if bad:
        print(f'  Unrecoverable: {len(bad)}')
        for s, i in bad:
            su = i.get('source_url','') or 'NONE'
            print(f'    {i.get("title",s)[:30]}: {i["cnt"]}ch → {su[:60]}')


def cmd_fix_garbled(args):
    limit = int(args[0]) if args and args[0].isdigit() else None
    state = load_state()
    g = find_garbled()
    todo = [(s, i) for s, i in g.items()
            if i.get('source_url') and s not in state['garbled_fixed']
            and not any(u in urlparse(i['source_url']).netloc for u in UNREACHABLE)]
    todo.sort(key=lambda x: -x[1]['cnt'])
    if limit: todo = todo[:limit]
    if not todo: print('✅ None to fix'); return
    print(f'=== Fixing {len(todo)} garbled ===')
    total = 0
    for idx, (s, i) in enumerate(todo):
        print(f'\n[{idx+1}/{len(todo)}]', end=' ')
        f = fix_garbled_novel(s, i)
        total += f
        if f: state['garbled_fixed'].append(s)
        if (idx + 1) % 5 == 0: save_state(state)
    if total: update_counts()
    save_state(state)
    print(f'\n  ✅ Fixed: {total}')


def cmd_fill_missing(args):
    limit = int(args[0]) if args and args[0].isdigit() else None
    state = load_state()
    missing = find_missing()
    todo = [n for n in missing if n['slug'] not in state['missing_filled']]
    if limit: todo = todo[:limit]
    if not todo: print('✅ None to fill'); return
    print(f'=== Filling {len(todo)} novels ===')
    total = 0
    for idx, ni in enumerate(todo):
        print(f'\n[{idx+1}/{len(todo)}]', end=' ')
        f = fill_missing_novel(ni, max_ch=100)
        total += f
        if ni['gap'] <= 100: state['missing_filled'].append(ni['slug'])
        if (idx + 1) % 5 == 0: save_state(state)
    if total: update_counts()
    save_state(state)
    print(f'\n  ✅ Filled: {total}')


def cmd_all(delay=1.0):
    state = load_state()

    # Phase 1
    g = find_garbled()
    todo = [(s, i) for s, i in g.items()
            if i.get('source_url') and s not in state['garbled_fixed']
            and not any(u in urlparse(i['source_url']).netloc for u in UNREACHABLE)]
    todo.sort(key=lambda x: -x[1]['cnt'])
    if todo:
        print(f'=== Phase 1: {len(todo)} garbled ===')
        tf = 0
        for idx, (s, i) in enumerate(todo):
            print(f'\n[{idx+1}/{len(todo)}]', end=' ')
            f = fix_garbled_novel(s, i, delay=delay)
            tf += f
            if f: state['garbled_fixed'].append(s)
        print(f'\n  ✅ Fixed: {tf}')
        save_state(state)
    else: print('=== Phase 1: none ===')

    # Phase 2
    missing = find_missing()
    todo2 = [n for n in missing if n['slug'] not in state['missing_filled']][:50]
    if todo2:
        print(f'\n=== Phase 2: {len(todo2)} novels ===')
        tf2 = 0
        for idx, ni in enumerate(todo2):
            print(f'\n[{idx+1}/{len(todo2)}]', end=' ')
            f = fill_missing_novel(ni, max_ch=100, delay=delay)
            tf2 += f
            if ni['gap'] <= 100: state['missing_filled'].append(ni['slug'])
        print(f'\n  ✅ Filled: {tf2}')
    else: print('\n=== Phase 2: none ===')

    update_counts(); save_state(state)


if __name__ == '__main__':
    args = sys.argv[1:]
    cmd = args[0] if args else 'help'
    if cmd == 'help': print(__doc__)
    elif cmd == 'detect': cmd_detect()
    elif cmd == 'gap-hunt': cmd_gap_hunt()
    elif cmd == 'fix-garbled': cmd_fix_garbled(args[1:])
    elif cmd == 'fill-missing': cmd_fill_missing(args[1:])
    elif cmd == 'all':
        delay = 1.0
        for a in args[1:]:
            if a.startswith('--delay='): delay = float(a.split('=',1)[1])
        cmd_all(delay=delay)
    else: print(f'Unknown: {cmd}'); print(__doc__)
