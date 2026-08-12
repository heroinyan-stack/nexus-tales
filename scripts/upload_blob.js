#!/usr/bin/env node
/**
 * Upload novel-site data to Vercel Blob Storage
 * Usage: BLOB_READ_WRITE_TOKEN=xxx node scripts/upload_blob.js
 */
const { put } = require('@vercel/blob');
const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(__dirname, '..', 'data');
const TOKEN = process.env.BLOB_READ_WRITE_TOKEN;
const STORE_ID = process.env.BLOB_STORE_ID || 'store_izr20VnPPLvtebL1';

async function uploadFile(localPath, blobPath) {
  const content = fs.readFileSync(localPath);
  const result = await put(blobPath, content, {
    access: 'private',
    allowOverwrite: true,
    token: TOKEN,
  });
  return result;
}

async function main() {
  console.log('🚀 开始上传到 Vercel Blob...');
  console.log(`Store ID: ${STORE_ID}`);

  // 1. novels.json
  console.log('\n[1/3] 上传 novels.json...');
  const novelsResult = await uploadFile(
    path.join(DATA_DIR, 'novels.json'),
    'data/novels.json'
  );
  console.log(`✅ novels.json → ${novelsResult.url}`);

  // 2. cover-manifest.json
  console.log('\n[2/3] 上传 cover-manifest.json...');
  const manifestPath = path.join(DATA_DIR, 'cover-manifest.json');
  let manifestUrl = null;
  if (fs.existsSync(manifestPath)) {
    const m = await uploadFile(manifestPath, 'data/cover-manifest.json');
    manifestUrl = m.url;
    console.log(`✅ cover-manifest.json → ${manifestUrl}`);
  }

  // 3. chapters (分批，每批50个文件)
  console.log('\n[3/3] 上传章节 (chapters/)...');
  const chaptersDir = path.join(DATA_DIR, 'chapters');
  const novels = fs.readdirSync(chaptersDir).filter(d =>
    fs.statSync(path.join(chaptersDir, d)).isDirectory()
  );

  let totalUploaded = 0;
  let totalFailed = 0;
  const failedList = [];

  for (const slug of novels) {
    const novelDir = path.join(chaptersDir, slug);
    const files = fs.readdirSync(novelDir).filter(f => f.endsWith('.json'));

    for (const file of files) {
      const blobPath = `data/chapters/${slug}/${file}`;
      const localPath = path.join(novelDir, file);
      try {
        await uploadFile(localPath, blobPath);
        totalUploaded++;

        if (totalUploaded % 200 === 0) {
          console.log(`  📤 已上传 ${totalUploaded} 章节...`);
        }
      } catch (err) {
        totalFailed++;
        if (failedList.length < 10) {
          failedList.push(`${blobPath}: ${err.message}`);
        }
      }
    }
  }

  console.log(`\n✅ 全部完成！`);
  console.log(`   上传成功: ${totalUploaded} 章节`);
  if (totalFailed > 0) {
    console.log(`   上传失败: ${totalFailed} 个`);
    console.log(`   失败列表:`, failedList);
  }

  // 写一份映射文件到本地，记录Blob URLs
  const novelsData = JSON.parse(fs.readFileSync(path.join(DATA_DIR, 'novels.json'), 'utf-8'));
  const blobMap = {
    storeId: STORE_ID,
    novelsUrl: novelsResult.url,
    manifestUrl: manifestUrl,
    updatedAt: new Date().toISOString(),
    totalNovels: novelsData.length,
  };
  fs.writeFileSync(
    path.join(DATA_DIR, 'blob_config.json'),
    JSON.stringify(blobMap, null, 2)
  );
  console.log(`\n📝 Blob配置已保存到 data/blob_config.json`);
  console.log(`   novelsUrl: ${novelsResult.url}`);
}

main().catch(err => {
  console.error('❌ 上传出错:', err);
  process.exit(1);
});
