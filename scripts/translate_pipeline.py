#!/usr/bin/env python3
"""
Nexus Tales - 翻译管道
使用 deep-translator (免费 Google Translate) 将中文小说翻译成英文
"""

import json
import os
import time
import re
import sys

try:
    from deep_translator import GoogleTranslator
except ImportError:
    print("正在安装 deep-translator...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "deep-translator", "-q"])
    from deep_translator import GoogleTranslator

# ========== 配置 ==========
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CHAPTERS_DIR = os.path.join(DATA_DIR, "chapters")
NOVELS_FILE = os.path.join(DATA_DIR, "novels.json")
BATCH_SIZE = 500  # 每批翻译字符数
DELAY_BETWEEN_BATCHES = 5  # 批间延迟(秒)

# ========== 翻译函数 ==========
def translate_text(text, source='zh-CN', target='en'):
    """翻译文本，自动分段避免超长"""
    if not text or len(text.strip()) == 0:
        return ""
    
    translator = GoogleTranslator(source=source, target=target)
    
    # 如果文本太长，分段翻译
    if len(text) <= BATCH_SIZE:
        try:
            return translator.translate(text)
        except Exception as e:
            print(f"  翻译失败: {e}")
            return text  # 返回原文
    
    # 分段翻译
    segments = []
    for i in range(0, len(text), BATCH_SIZE):
        segment = text[i:i+BATCH_SIZE]
        try:
            translated = translator.translate(segment)
            segments.append(translated)
            time.sleep(1)  # 避免被限流
        except Exception as e:
            print(f"  段翻译失败 [{i}:{i+len(segment)}]: {e}")
            segments.append(segment)
        
        if i + BATCH_SIZE < len(text):
            time.sleep(DELAY_BETWEEN_BATCHES)
    
    return "".join(segments)

def translate_novel_info(novel):
    """翻译小说基本信息"""
    print(f"  翻译: {novel.get('title', novel.get('title_zh', ''))}")
    
    if novel.get('title_zh') and not novel.get('title_en'):
        novel['title_en'] = translate_text(novel['title_zh'])
        time.sleep(2)
    
    if novel.get('author_zh') and not novel.get('author_en'):
        novel['author_en'] = translate_text(novel['author_zh'])
        time.sleep(2)
    
    if novel.get('description_zh') and not novel.get('description_en'):
        novel['description_en'] = translate_text(novel['description_zh'])
        time.sleep(2)
    
    return novel

def translate_chapter(novel_slug, chapter_num):
    """翻译单个章节"""
    chapter_path = os.path.join(CHAPTERS_DIR, novel_slug, f"ch-{chapter_num}.json")
    
    if not os.path.exists(chapter_path):
        return False
    
    with open(chapter_path, 'r', encoding='utf-8') as f:
        chapter = json.load(f)
    
    # 如果已翻译就跳过
    if chapter.get('translated') and chapter.get('content_en'):
        return True
    
    print(f"  翻译章节 {chapter_num}: {chapter.get('title_zh', '')[:30]}...")
    
    # 翻译标题
    if chapter.get('title_zh') and not chapter.get('title_en'):
        chapter['title_en'] = translate_text(chapter['title_zh'])
        time.sleep(2)
    
    # 翻译内容
    if chapter.get('content_zh') and not chapter.get('content_en'):
        chapter['content_en'] = translate_text(chapter['content_zh'])
    
    chapter['translated'] = True
    
    # 保存
    with open(chapter_path, 'w', encoding='utf-8') as f:
        json.dump(chapter, f, ensure_ascii=False, indent=2)
    
    return True

def main():
    """主入口"""
    print("=" * 50)
    print("Nexus Tales - 翻译管道")
    print("=" * 50)
    
    # 翻译小说信息
    if os.path.exists(NOVELS_FILE):
        with open(NOVELS_FILE, 'r', encoding='utf-8') as f:
            novels = json.load(f)
        
        print(f"\n找到 {len(novels)} 本小说")
        
        for novel in novels:
            translate_novel_info(novel)
        
        with open(NOVELS_FILE, 'w', encoding='utf-8') as f:
            json.dump(novels, f, ensure_ascii=False, indent=2)
        
        print("\n小说信息翻译完成!")
    
    # 翻译章节
    if os.path.exists(CHAPTERS_DIR):
        translated = 0
        for novel_dir in os.listdir(CHAPTERS_DIR):
            novel_path = os.path.join(CHAPTERS_DIR, novel_dir)
            if not os.path.isdir(novel_path):
                continue
            
            chapter_files = sorted([f for f in os.listdir(novel_path) if f.startswith('ch-')])
            
            # 只翻译前3章（后续可扩展）
            for ch_file in chapter_files[:3]:
                ch_num = int(re.findall(r'ch-(\d+)', ch_file)[0])
                if translate_chapter(novel_dir, ch_num):
                    translated += 1
                
                time.sleep(DELAY_BETWEEN_BATCHES)
        
        print(f"\n共翻译 {translated} 章节!")

if __name__ == "__main__":
    main()