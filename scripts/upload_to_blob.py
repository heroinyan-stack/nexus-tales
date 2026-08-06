#!/usr/bin/env python3.10
"""
Upload novel-site data to Vercel Blob Storage
Usage: python3.10 scripts/upload_to_blob.py
"""

import os
import json
import glob
from pathlib import Path
from vercel_blob import put

# Vercel Blob需要BLOB_READ_WRITE_TOKEN环境变量
# 在Vercel项目设置中获取

DATA_DIR = Path(__file__).parent.parent / "data"
CHUNK_SIZE = 100  # 每批上传章节数

def upload_novels_list():
    """上传novels.json主索引"""
    novels_file = DATA_DIR / "novels.json"
    print(f"上传 novels.json...")

    with open(novels_file, 'rb') as f:
        result = put('data/novels.json', f, token=os.environ.get('BLOB_READ_WRITE_TOKEN'))

    print(f"✓ novels.json → {result['url']}")
    return result['url']

def upload_chapters():
    """上传所有章节（分批）"""
    chapters_dir = DATA_DIR / "chapters"
    all_novels = [d for d in chapters_dir.iterdir() if d.is_dir()]

    uploaded = 0
    failed = []

    for novel_dir in all_novels:
        slug = novel_dir.name
        chapter_files = list(novel_dir.glob("*.json"))

        for ch_file in chapter_files:
            blob_path = f"data/chapters/{slug}/{ch_file.name}"
            try:
                with open(ch_file, 'rb') as f:
                    result = put(blob_path, f, token=os.environ.get('BLOB_READ_WRITE_TOKEN'))
                uploaded += 1
                if uploaded % 100 == 0:
                    print(f"  已上传 {uploaded} 章节...")
            except Exception as e:
                failed.append((blob_path, str(e)))

    print(f"\n✓ 上传完成: {uploaded} 章节")
    if failed:
        print(f"✗ 失败 {len(failed)} 个:")
        for path, err in failed[:5]:
            print(f"  {path}: {err}")

    return uploaded, failed

def main():
    if not os.environ.get('BLOB_READ_WRITE_TOKEN'):
        print("错误: 需要设置 BLOB_READ_WRITE_TOKEN 环境变量")
        print("在 Vercel 项目 Settings > Storage > Blob 中创建并复制token")
        return

    print("开始上传到 Vercel Blob Storage...")
    print(f"数据目录: {DATA_DIR}")

    # 1. 上传主索引
    novels_url = upload_novels_list()

    # 2. 上传章节
    uploaded, failed = upload_chapters()

    print(f"\n完成！")
    print(f"主索引: {novels_url}")
    print(f"章节数: {uploaded}")

if __name__ == "__main__":
    main()
