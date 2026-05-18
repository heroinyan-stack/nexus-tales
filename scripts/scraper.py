#!/usr/bin/env python3
"""
Nexus Tales Scraper - 小说爬虫 + 翻译管道
目标源: 笔趣阁 (biquge) 镜像站
翻译: deep-translator (免费, 无需 API key)
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urljoin
import sys

# ========== 配置 ==========
SOURCE_SITE = "https://www.biquge5200.com"  # 笔趣阁镜像
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

# ========== 工具函数 ==========
def safe_request(url, max_retries=3):
    """带重试的 HTTP 请求"""
    for i in range(max_retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            resp.encoding = 'utf-8'
            return resp
        except Exception as e:
            print(f"请求失败 ({i+1}/{max_retries}): {url} - {e}")
            time.sleep(2)
    return None

def clean_text(text):
    """清理文本"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def slugify(text):
    """生成 URL 友好的 slug"""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text[:100]

# ========== 爬虫函数 ==========
def get_novel_list(genre_url, max_pages=3):
    """获取小说列表"""
    novels = []
    
    for page in range(1, max_pages + 1):
        page_url = f"{genre_url}/index_{page}.html"
        print(f"  抓取第 {page} 页: {page_url}")
        
        resp = safe_request(page_url)
        if not resp:
            continue
            
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 笔趣阁列表结构: .novel-list .novel-item
        items = soup.select('.novel-list .novel-item')
        
        for item in items:
            try:
                # 提取小说信息
                title_elem = item.select_one('.novel-name a')
                author_elem = item.select_one('.author')
                
                if not title_elem:
                    continue
                    
                title = clean_text(title_elem.get_text())
                href = title_elem.get('href', '')
                author = clean_text(author_elem.get_text()) if author_elem else "Unknown"
                
                if href and title:
                    novel_url = urljoin(SOURCE_SITE, href)
                    novel_slug = slugify(title)
                    
                    novels.append({
                        'title': title,
                        'slug': novel_slug,
                        'author': author,
                        'url': novel_url,
                        'source': 'biquge5200'
                    })
            except Exception as e:
                print(f"  解析小说项失败: {e}")
                continue
                
        time.sleep(1)  # 礼貌爬取
    
    return novels

def get_novel_detail(novel_url):
    """获取小说详情"""
    resp = safe_request(novel_url)
    if not resp:
        return None
        
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # 提取小说信息
    info = {}
    
    # 标题
    title_elem = soup.select_one('#info h1')
    info['title'] = clean_text(title_elem.get_text()) if title_elem else ""
    
    # 作者
    author_elem = soup.select_one('#info p')
    if author_elem:
        text = clean_text(author_elem.get_text())
        if '作者' in text:
            info['author'] = text.split('：')[-1] if '：' in text else text
    
    # 简介
    desc_elem = soup.select_one('#intro')
    info['description'] = clean_text(desc_elem.get_text()) if desc_elem else ""
    
    # 章节列表
    chapters = []
    chapter_list = soup.select('#list dl dd a')
    for i, ch in enumerate(chapter_list[:500], 1):  # 最多500章
        chapters.append({
            'num': i,
            'title': clean_text(ch.get_text()),
            'url': urljoin(SOURCE_SITE, ch.get('href', ''))
        })
    
    info['chapters'] = chapters
    return info

def get_chapter_content(chapter_url):
    """获取章节内容"""
    resp = safe_request(chapter_url)
    if not resp:
        return ""
        
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # 内容在 #content
    content_elem = soup.select_one('#content')
    if content_elem:
        # 获取所有段落
        paragraphs = content_elem.find_all('p')
        text = '\n\n'.join([clean_text(p.get_text()) for p in paragraphs if p.get_text()])
        return text
    
    return ""

# ========== 主程序 ==========
def main():
    print("=" * 50)
    print("Nexus Tales Scraper - 小说爬虫")
    print("=" * 50)
    
    # 测试: 抓取一个分类的前几页
    # 笔趣阁分类URL
    genres = [
        ('xianxia', 'https://www.biquge5200.com/xianxia'),
        ('xuanhuan', 'https://www.biquge5200.com/xuanhuan'),
        ('dushi', 'https://www.biquge5200.com/dushi'),
    ]
    
    all_novels = []
    
    for genre_name, genre_url in genres[:1]:  # 先测试一个分类
        print(f"\n[分类: {genre_name}]")
        novels = get_novel_list(genre_url, max_pages=2)
        print(f"  获取到 {len(novels)} 本小说")
        all_novels.extend(novels)
    
    # 取第一本测试详情页
    if all_novels:
        test_novel = all_novels[0]
        print(f"\n测试详情页: {test_novel['title']}")
        detail = get_novel_detail(test_novel['url'])
        if detail:
            print(f"  章节数: {len(detail.get('chapters', []))}")
            if detail.get('chapters'):
                ch = detail['chapters'][0]
                print(f"  第一章: {ch['title']}")
                content = get_chapter_content(ch['url'])
                print(f"  内容长度: {len(content)} 字符")
    
    print("\n测试完成!")
    return all_novels

if __name__ == "__main__":
    main()
