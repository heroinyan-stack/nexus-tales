#!/usr/bin/env node
/**
 * High-performance Vercel Blob uploader
 * Uses 10 concurrent workers for ~5-10 files/sec
 */
const { put } = require('@vercel/blob');
const fs = require('fs');
const path = require('path');

const TOKEN = process.env.BLOB_READ_WRITE_TOKEN;
const DATA_DIR = path.join(__dirname, '..', 'data');
const LOG_FILE = path.join(__dirname, '..', 'scripts', 'blob_upload_fast.log');
const PROGRESS_FILE = path.join(__dirname, '..', 'data', 'blob_upload_progress.json');

const CONCURRENCY = 20;
const BATCH_SIZE = 50; // commit every 50 files

function log(msg) {
  const ts = new Date().toISOString().slice(11, 19);
  const line = `[${ts}] ${msg}`;
  console.log(line);
  fs.appendFileSync(LOG_FILE, line + '\n');
}

function loadProgress() {
  try {
    return JSON.parse(fs.readFileSync(PROGRESS_FILE, 'utf-8'));
  } catch {
    return { uploaded: [], failed: [] };
  }
}

function saveProgress(progress) {
  fs.writeFileSync(PROGRESS_FILE, JSON.stringify(progress));
}

async function uploadFile(localPath, blobPath) {
  const content = fs.readFileSync(localPath);
  const result = await put(blobPath, content, {
    access: 'private',
    allowOverwrite: true,
    token: TOKEN,
  });
  return result;
}

async function worker(queue, progress, startTime) {
  while (true) {
    const item = queue.shift();
    if (!item) break;

    try {
      await uploadFile(item.local, item.blob);
      progress.uploaded.push(item.blob);
    } catch (err) {
      progress.failed.push({ blob: item.blob, error: err.message });
      if (progress.failed.length <= 5) {
        log(`❌ ${item.blob}: ${err.message}`);
      }
    }

    // Progress
    const total = progress.uploaded.length + progress.failed.length + queue.length;
    const done = progress.uploaded.length + progress.failed.length;
    if (done % 100 === 0) {
      const elapsed = (Date.now() - startTime) / 1000;
      const rate = done / elapsed;
      const remain = queue.length / rate;
      log(`📤 ${done}/${total} (${rate.toFixed(1)}/s, ~${Math.ceil(remain)}s remaining)`);
    }

    // Save progress every batch
    if (done % BATCH_SIZE === 0) {
      saveProgress(progress);
    }
  }
}

async function main() {
  log('🚀 高速上传开始 (concurrency=' + CONCURRENCY + ')');

  const progress = loadProgress();
  const uploadedSet = new Set(progress.uploaded);
  log(`📂 已有 ${uploadedSet.size} 个文件已上传，跳过`);

  // Build queue of all chapter files
  const chaptersDir = path.join(DATA_DIR, 'chapters');
  const queue = [];

  for (const slug of fs.readdirSync(chaptersDir)) {
    const slugDir = path.join(chaptersDir, slug);
    if (!fs.statSync(slugDir).isDirectory()) continue;

    for (const file of fs.readdirSync(slugDir)) {
      if (!file.endsWith('.json')) continue;
      const blobPath = `data/chapters/${slug}/${file}`;
      if (uploadedSet.has(blobPath)) continue;
      queue.push({
        local: path.join(slugDir, file),
        blob: blobPath,
      });
    }
  }

  log(`📋 待上传: ${queue.length} 文件`);

  if (queue.length === 0) {
    log('✅ 全部完成！');
    return;
  }

  const startTime = Date.now();
  const workers = Array.from({ length: CONCURRENCY }, () =>
    worker(queue, progress, startTime)
  );

  await Promise.all(workers);
  saveProgress(progress);

  const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
  log(`\n✅ 上传完成! 耗时: ${elapsed}s`);
  log(`   成功: ${progress.uploaded.length}`);
  log(`   失败: ${progress.failed.length}`);
  if (progress.failed.length > 0) {
    log(`   失败列表:`);
    progress.failed.slice(0, 10).forEach(f => log(`     ${f.blob}: ${f.error}`));
  }
}

main().catch(err => {
  console.error('❌ 致命错误:', err);
  process.exit(1);
});
