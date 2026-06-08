#!/usr/bin/env python3
"""
Nexus Tales - 完结小说爬虫
=============================
只爬取已完结（完本）的小说，跳过连载中作品。

数据源：
  1. bxwx9.org (笔下文学) - 主要来源，无加密HTML
  2. ssofu.net (全本小说网) - 小说发现（章节详情页AES加密，仅用发现）

输出：
  data/chapters/{slug}/ch-{N}.json  (与现有格式兼容)

用法：
  python3 scripts/crawl_completed.py discover [源站] [页数]   发现完结小说
  python3 scripts/crawl_completed.py details                  拉取详细信息(作者/简介/章节列表)
  python3 scripts/crawl_completed.py pull [N]                 每个小说拉取N章(N默认5)
  python3 scripts/crawl_completed.py full [N]                 全量拉取(直到全部章节或N章上限)
  python3 scripts/crawl_completed.py translate                翻译章节为英文
"""

import json, os, re, time, random, sys
import urllib.request
import ssl

ssl_ctx = ssl.create_default_context()
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}

PROJECT_DIR = '/Users/myan/.qclaw/workspace/novel-site'
DATA_DIR = f'{PROJECT_DIR}/data'
os.makedirs(DATA_DIR, exist_ok=True)

# Files
BXWX_NOVELS_FILE = f'{DATA_DIR}/bxwx_completed_novels.json'
SSOFU_NOVELS_FILE = f'{DATA_DIR}/ssofu_novels.json'
SITE_NOVELS_FILE = f'{DATA_DIR}/novels.json'

# Patterns to filter from chapter content
FILTER_PATTERNS = [
    r'请记住本书首发域名',
    r'笔趣阁.*?网址',
    r'wap\..*?\.org',
    r'一秒记住.*?网址',
    r'手机阅读地址',
    r'本书网址',
    r'浏览阅读地址',
    r'更新最快网址',
    r'最快更新.*?网址',
    r'笔趣阁.*?提醒您',
    r'第一时间更新',
    r'下载.*?阅读',
    r'本章未完.*?下一页',
    r'.*?提示您：看后求收藏',
    r'记住本站网址',
    r'如果您喜欢.*?收藏',
    r'推荐阅读.*?类似.*?小说',
    r'相关推荐',
    r'笔下文学网',
    r'喜欢本书请.*?收藏',
    r'手机阅读：',
    r'www\..*?\.(com|net|org|io)',
    r'https?://[^\s]*',
]


def fetch(url, referer=None, timeout=15):
    headers = dict(HEADERS)
    if referer:
        headers['Referer'] = referer
    req = urllib.request.Request(url, headers=headers)
    try:
        resp = urllib.request.urlopen(req, context=ssl_ctx, timeout=timeout)
        return resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        print(f'  ⚠ {url[:80]}: {e}')
        return None


def is_completed(html):
    """Check if novel status is 完结/完本"""
    status_m = re.search(r'<meta property="og:novel:status" content="(.*?)"', html)
    if status_m:
        return status_m.group(1) == '完结'
    # Fallback: check for 完本 badge
    if '状态：完结' in html or '完本' in html:
        return True
    return False


def slugify(title):
    """Convert Chinese/English title to URL-safe slug"""
    import unicodedata
    # Try to use English title or transliterate
    slug = title.lower().strip()
    slug = unicodedata.normalize('NFKD', slug)
    slug = re.sub(r'[^\x00-\x7F]+', '', slug)  # remove non-ASCII
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    if len(slug) < 3:
        # If title is all Chinese, use romanized version
        slug = f'novel-{abs(hash(title)) % 1000000}'
    return slug.lower().strip('-')


def filter_content(text):
    """Remove site prompts, ads, URLs from chapter content"""
    lines = text.split('\n')
    clean_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if clean_lines and clean_lines[-1]:
                clean_lines.append('')
            continue
        # Check filter patterns
        skip = False
        for pat in FILTER_PATTERNS:
            if re.search(pat, stripped, re.IGNORECASE):
                skip = True
                break
        if not skip:
            clean_lines.append(stripped)
    return '\n'.join(clean_lines).strip()


# ═══════════════════════════════════════════════════
# BXWX9.ORG CRAWLER
# ═══════════════════════════════════════════════════

def discover_bxwx9_completed(pages=5):
    """Discover completed novels from bxwx9.org /full/ listing"""
    novels = {}
    
    for page in range(1, pages + 1):
        url = f'https://www.bxwx9.org/full/{"" if page == 1 else page}'
        if page == 1:
            url = 'https://www.bxwx9.org/full/'
        else:
            url = f'https://www.bxwx9.org/full/index_{page}.html'
        
        print(f'\n  Page {page}/{pages}: {url}')
        html = fetch(url)
        if not html:
            continue
        
        # Find novel links with category
        links = re.findall(r'\[(.*?)\]\s*<a href="(/b/\d+/\d+/)"[^>]*>(.*?)</a>', html)
        print(f'    Found {len(links)} novels')
        
        for category, url_path, raw_title in links:
            novel_id = re.search(r'/b/(\d+)/(\d+)/', url_path)
            nid = f'{novel_id.group(1)}_{novel_id.group(2)}' if novel_id else url_path
            if nid in novels:
                continue
            
            clean_title = re.sub(r'<[^>]+>', '', raw_title).strip()
            novels[nid] = {
                'id': nid,
                'title': clean_title,
                'url': f'https://www.bxwx9.org{url_path}',
                'source': 'bxwx9.org',
                'category': category.strip(),
                'source_url': f'https://www.bxwx9.org{url_path}',
            }
        
        time.sleep(random.uniform(1.0, 2.0))
    
    return novels


def fetch_bxwx9_details(novel):
    """Fetch novel detail: description, author, cover, chapter list"""
    print(f'    [{novel.get("title", "?")[:30]}]')
    html = fetch(novel['url'])
    if not html:
        return novel
    
    # Verify completed status
    novel['completed'] = is_completed(html)
    
    # Meta info
    for field, keyword in [
        ('category', 'og:novel:category'),
        ('author', 'og:novel:author'),
        ('book_name', 'og:novel:book_name'),
        ('status', 'og:novel:status'),
        ('update_time', 'og:novel:update_time'),
    ]:
        m = re.search(f'<meta property="{keyword}" content="(.*?)"', html)
        if m:
            novel[field] = m.group(1).strip()
    
    # Description
    desc_m = re.search(r'<meta property="og:description" content="(.*?)"', html)
    if desc_m:
        novel['description'] = desc_m.group(1).strip()
    
    # Cover image
    cover_m = re.search(r'<meta property="og:image" content="(.*?)"', html)
    if cover_m:
        novel['cover_url'] = 'https:' + cover_m.group(1) if cover_m.group(1).startswith('//') else cover_m.group(1)
    
    # Chapter list
    chapters = re.findall(r'href="(/b/\d+/\d+/(\d+)(?:_\d+)?\.html)"[^>]*>(.*?)</a>', html)
    seen = set()
    chapter_list = []
    for url_path, chapter_id, raw_title in chapters:
        if chapter_id in seen:
            continue
        seen.add(chapter_id)
        clean_title = re.sub(r'<[^>]+>', '', raw_title).strip()
        # Check pagination markers
        # Base URL (page 1) never has _N suffix
        chapter_list.append({
            'id': chapter_id,
            'title': clean_title,
            'url': f'https://www.bxwx9.org{url_path}',
        })
    
    novel['chapters'] = chapter_list
    novel['total_chapters'] = len(chapter_list)
    
    # Generate slug
    novel['slug'] = slugify(novel.get('book_name', novel.get('title', novel['id'])))
    
    time.sleep(random.uniform(0.8, 1.5))
    return novel


def pull_bxwx9_chapter(novel, chapter_info):
    """Pull a single chapter from bxwx9.org, handling pagination"""
    base_url = chapter_info['url']
    chapter_num = int(chapter_info['id'])
    chapter_title = chapter_info['title']
    
    all_content = []
    page = 1
    
    while True:
        if page == 1:
            url = base_url
        else:
            url = base_url.replace('.html', f'_{page}.html')
        
        html = fetch(url, referer=novel['url'])
        if not html:
            if page == 1:
                return None
            break  # pagination ended
        
        # Extract content from <article class="font_max">
        art_m = re.search(r'<article class="font_max">(.*?)</article>', html, re.S)
        if not art_m:
            if page == 1:
                return None
            break
        
        content = art_m.group(1)
        # Clean
        content = re.sub(r'<br\s*/?>', '\n', content)
        content = re.sub(r'<[^>]+>', '', content)
        # Remove &nbsp; sequences
        content = re.sub(r'&nbsp;', '', content)
        # Remove pagination markers
        content = re.sub(r'第\(\d+/\d+\)页', '', content)
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        all_content.append(content.strip())
        
        # Check for next page
        next_m = re.search(r'href="[^"]*_(\d+)\.html"[^>]*data=["\'][^"\']*["\']\s*>下一章</a>', html)
        if not next_m:
            break
        
        page += 1
        if page > 10:  # safety limit
            break
        
        time.sleep(random.uniform(0.3, 0.6))
    
    full_content = '\n'.join(all_content)
    return filter_content(full_content)


def save_chapter(slug, chapter_num, title, content):
    """Save chapter as JSON"""
    chapter_dir = f'{DATA_DIR}/chapters/{slug}'
    os.makedirs(chapter_dir, exist_ok=True)
    
    lines = [l.strip() for l in content.split('\n') if l.strip()]
    if len(lines) < 3:
        return False
    
    chapter = {
        'num': chapter_num,
        'title': title,
        'slug': slug,
        'lines': lines,
    }
    
    filepath = f'{chapter_dir}/ch-{chapter_num}.json'
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(chapter, f, ensure_ascii=False, indent=2)
    return True


# ═══════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════

def cmd_discover(args):
    source = args[1] if len(args) > 1 else 'bxwx9'
    pages = int(args[2]) if len(args) > 2 else 5
    
    if source == 'bxwx9':
        print('=== 发现 bxwx9.org 完结小说 (完本专区) ===')
        novels = discover_bxwx9_completed(pages)
        out_file = BXWX_NOVELS_FILE
    else:
        print(f'Unknown source: {source}')
        return
    
    novels_list = list(novels.values())
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(novels_list, f, ensure_ascii=False, indent=2)
    print(f'\n  ✅ 共发现 {len(novels_list)} 部完结小说 → {out_file}')


def cmd_details(args):
    if not os.path.exists(BXWX_NOVELS_FILE):
        print('❌ 没有已发现的小说，先运行 "discover"')
        return
    
    with open(BXWX_NOVELS_FILE, 'r', encoding='utf-8') as f:
        novels = json.load(f)
    
    print(f'=== 拉取 {len(novels)} 部小说详情 ===')
    updated = 0
    for i, novel in enumerate(novels):
        if 'author' in novel and novel.get('author'):
            continue  # already fetched
        
        print(f'  [{i+1}/{len(novels)}]', end=' ')
        novels[i] = fetch_bxwx9_details(novel)
        updated += 1
        
        if updated % 10 == 0:
            with open(BXWX_NOVELS_FILE, 'w', encoding='utf-8') as f:
                json.dump(novels, f, ensure_ascii=False, indent=2)
            print(f'    💾 已保存')
    
    with open(BXWX_NOVELS_FILE, 'w', encoding='utf-8') as f:
        json.dump(novels, f, ensure_ascii=False, indent=2)
    
    completed = sum(1 for n in novels if n.get('completed'))
    total_ch = sum(n.get('total_chapters', 0) for n in novels)
    print(f'\n  ✅ 详情完成: {completed}/{len(novels)} 部已完结, 共 {total_ch} 章节')


def cmd_pull(args):
    per_novel = int(args[1]) if len(args) > 1 else 5
    
    if not os.path.exists(BXWX_NOVELS_FILE):
        print('❌ 先运行 discover + details')
        return
    
    with open(BXWX_NOVELS_FILE, 'r', encoding='utf-8') as f:
        novels = json.load(f)
    
    # Filter completed novels only
    completed = [n for n in novels if n.get('completed') and n.get('chapters')]
    print(f'=== 拉取章节: {per_novel}章/部, {len(completed)} 部完结小说 ===')
    
    total_pulled = 0
    for novel in completed:
        slug = novel.get('slug', novel['id'])
        
        # Count existing chapters
        chapter_dir = f'{DATA_DIR}/chapters/{slug}'
        existing = set()
        if os.path.exists(chapter_dir):
            for fname in os.listdir(chapter_dir):
                m = re.match(r'ch-(\d+)\.json', fname)
                if m:
                    existing.add(int(m.group(1)))
        
        chapters = novel['chapters']
        pulled_this = 0
        
        for ch_info in chapters:
            if pulled_this >= per_novel:
                break
            
            ch_num = int(ch_info['id'])
            # Find sequential chapter number if we have existing ones
            if str(existing)[:50] != 'set()' or len(existing) > 0:
                # Pull next N chapters sequentially
                next_ch = max(existing) + 1 if existing else 0
                if ch_num < next_ch:
                    continue
            
            print(f'  [{slug[:20]} Ch{ch_num}] {ch_info["title"][:30]}')
            content = pull_bxwx9_chapter(novel, ch_info)
            
            if content and len(content) > 50:
                save_chapter(slug, ch_num, ch_info['title'], content)
                pulled_this += 1
                existing.add(ch_num)
            else:
                print(f'    ⚠ 内容不足或拉取失败')
            
            time.sleep(random.uniform(0.5, 1.0))
        
        total_pulled += pulled_this
        if pulled_this:
            print(f'  ✅ +{pulled_this}章')
        
        time.sleep(random.uniform(0.5, 1.0))
    
    print(f'\n  🎯 共拉取 {total_pulled} 章')


def cmd_full(args):
    """Pull ALL chapters from completed novels"""
    max_chapters = int(args[1]) if len(args) > 1 else 0  # 0 = all
    
    if not os.path.exists(BXWX_NOVELS_FILE):
        print('❌ 先运行 discover + details')
        return
    
    with open(BXWX_NOVELS_FILE, 'r', encoding='utf-8') as f:
        novels = json.load(f)
    
    completed = [n for n in novels if n.get('completed') and n.get('chapters')]
    print(f'=== 全量拉取: {len(completed)} 部完结小说 ===')
    
    total_pulled = 0
    for novel in completed:
        slug = novel.get('slug', novel['id'])
        
        # Count existing
        chapter_dir = f'{DATA_DIR}/chapters/{slug}'
        existing = set()
        if os.path.exists(chapter_dir):
            for fname in os.listdir(chapter_dir):
                m = re.match(r'ch-(\d+)\.json', fname)
                if m:
                    existing.add(int(m.group(1)))
        
        chapters = novel['chapters']
        total_ch = novel.get('total_chapters', len(chapters))
        
        if len(existing) >= total_ch:
            print(f'  [{slug[:20]}] ✅ 已完成 ({len(existing)}/{total_ch}章)')
            continue
        
        pulled_this = 0
        for ch_info in chapters:
            if max_chapters and total_pulled >= max_chapters:
                break
            
            ch_num = int(ch_info['id'])
            if ch_num in existing:
                continue
            
            print(f'  [{slug[:20]} Ch{ch_num}/{total_ch}]', end=' ')
            content = pull_bxwx9_chapter(novel, ch_info)
            
            if content and len(content) > 50:
                save_chapter(slug, ch_num, ch_info['title'], content)
                pulled_this += 1
                total_pulled += 1
                existing.add(ch_num)
                print(f'✅ ({len(content)}字)')
            else:
                print(f'⚠ 跳过')
            
            time.sleep(random.uniform(0.3, 0.7))
        
        if pulled_this:
            print(f'  📦 +{pulled_this}章 (总计{len(existing)}/{total_ch})')
    
    print(f'\n  🎯 本次共拉取 {total_pulled} 章')


if __name__ == '__main__':
    args = sys.argv[1:]
    cmd = args[0] if args else 'help'
    
    if cmd == 'help':
        print(__doc__)
    elif cmd == 'discover':
        cmd_discover(args)
    elif cmd == 'details':
        cmd_details(args)
    elif cmd == 'pull':
        cmd_pull(args)
    elif cmd == 'full':
        cmd_full(args)
    else:
        print(f'未知命令: {cmd}. 用 "help" 查看帮助。')
