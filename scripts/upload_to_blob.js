#!/usr/bin/env node
/**
 * Upload novel-site data to Vercel Blob Storage
 * Usage: node scripts/upload_to_blob.js
 */

const { put } = require('@vercel/blob');
const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(__dirname, '..', 'data');

async function uploadNovelsList() {
  const novelsPath = path.join(DATA_DIR, 'novels.json');
  console.log('上传 novels.json...');

  const file = fs.readFileSync(novelsPath);
  const result = await put('data/novels.json', file, {
    access: 'public',
  });

  console.log(`✓ novels.json → ${result.url}`);
  return result.url;
}

async function uploadChapters() {
  const chaptersDir = path.join(DATA_DIR, 'chapters');
  const novels = fs.readdirSync(chaptersDir).filter(d =>
    fs.statSync(path.join(chaptersDir, d)).isDirectory()
  );

  let uploaded = 0;
  let failed = [];

  for (const slug of novels) {
    const novelDir = path.join(chaptersDir, slug);
    const files = fs.readdirSync(novelDir).filter(f => f.endsWith('.json'));

    for (const file of files) {
      const blobPath = `data/chapters/${slug}/${file}`;
      try {
        const filePath = path.join(novelDir, file);
        const content = fs.readFileSync(filePath);
        await put(blobPath, content, { access: 'public' });
        uploaded++;

        if (uploaded % 100 === 0) {
          console.log(`  已上传 ${uploaded} 章节...`);
        }
      } catch (err) {
        failed.push({ path: blobPath, error: err.message });
      }
    }
  }

  console.log(`\n✓ 上传完成: ${uploaded} 章节`);
  if (failed.length > 0) {
    console.log(`✗ 失败 ${failed.length} 个:`);
    failed.slice(0, 5).forEach(f => console.log(`  ${f.path}: ${f.error}`));
  }

  return { uploaded, failed };
}

async function main() {
  if (!process.env.BLOB_READ_WRITE_TOKEN) {
    console.error('错误: 需要设置 BLOB_READ_WRITE_TOKEN 环境变量');
    console.error('在 Vercel 项目 Settings > Storage > Blob 中创建并复制token');
    process.exit(1);
  }

  console.log('开始上传到 Vercel Blob Storage...');
  console.log(`数据目录: ${DATA_DIR}`);

  try {
    // 1. 上传主索引
    const novelsUrl = await uploadNovelsList();

    // 2. 上传章节
    const { uploaded, failed } = await uploadChapters();

    console.log('\n完成！');
    console.log(`主索引: ${novelsUrl}`);
    console.log(`章节数: ${uploaded}`);
  } catch (err) {
    console.error('上传失败:', err);
    process.exit(1);
  }
}

main();
