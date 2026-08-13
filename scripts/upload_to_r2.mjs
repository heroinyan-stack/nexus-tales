// Upload novel data (novels.json, cover-manifest, chapters, blog) to Cloudflare R2.
// Run: node --env-file=.env.local scripts/upload_to_r2.mjs
// Env: R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET
import {
  readdirSync,
  readFileSync,
  statSync,
  existsSync,
  writeFileSync,
} from "fs";
import path from "path";
import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";

const ACCOUNT_ID = process.env.R2_ACCOUNT_ID;
const ACCESS_KEY_ID = process.env.R2_ACCESS_KEY_ID;
const SECRET_ACCESS_KEY = process.env.R2_SECRET_ACCESS_KEY;
const BUCKET = process.env.R2_BUCKET;

if (!ACCOUNT_ID || !ACCESS_KEY_ID || !SECRET_ACCESS_KEY || !BUCKET) {
  console.error(
    "Missing R2 env vars. Required: R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET"
  );
  process.exit(1);
}

const client = new S3Client({
  region: "auto",
  endpoint: `https://${ACCOUNT_ID}.r2.cloudflarestorage.com`,
  credentials: { accessKeyId: ACCESS_KEY_ID, secretAccessKey: SECRET_ACCESS_KEY },
});

const DATA_DIR = path.join(process.cwd(), "data");
const PROGRESS_FILE = path.join(DATA_DIR, "r2_upload_progress.json");

// Resume support
let done = new Set();
if (existsSync(PROGRESS_FILE)) {
  try {
    done = new Set(JSON.parse(readFileSync(PROGRESS_FILE, "utf-8")));
  } catch {
    done = new Set();
  }
}
console.log(`Resumed with ${done.size} already uploaded`);

// Build file list: { localPath, key }
const files = [];

// Metadata files (small, must be present for the app)
const metaFiles = [
  ["novels.json", "data/novels.json"],
  ["cover-manifest.json", "data/cover-manifest.json"],
  ["chapter_counts.json", "data/chapter_counts.json"],
  ["blog/posts.json", "data/blog/posts.json"],
];
for (const [rel, key] of metaFiles) {
  const p = path.join(DATA_DIR, rel);
  if (existsSync(p) && statSync(p).isFile()) files.push({ localPath: p, key });
}

// Chapter files (the big one)
const chaptersDir = path.join(DATA_DIR, "chapters");
if (existsSync(chaptersDir)) {
  for (const slug of readdirSync(chaptersDir)) {
    const slugDir = path.join(chaptersDir, slug);
    if (!statSync(slugDir).isDirectory()) continue;
    for (const f of readdirSync(slugDir)) {
      if (!f.endsWith(".json")) continue;
      files.push({ localPath: path.join(slugDir, f), key: `data/chapters/${slug}/${f}` });
    }
  }
}

console.log(`Total files to consider: ${files.length}`);
const todo = files.filter((f) => !done.has(f.key));
console.log(`Remaining to upload: ${todo.length}`);

const CONCURRENCY = 20;
let completed = 0;
let failed = 0;
const failedKeys = [];
let lastLog = Date.now();

async function uploadOne(f) {
  const body = readFileSync(f.localPath);
  try {
    await client.send(new PutObjectCommand({ Bucket: BUCKET, Key: f.key, Body: body }));
    done.add(f.key);
    completed++;
  } catch (e) {
    failed++;
    failedKeys.push(f.key);
    if (failedKeys.length <= 10) console.error("FAIL", f.key, e.message);
  }
  const now = Date.now();
  if (now - lastLog > 2000) {
    lastLog = now;
    console.log(
      `progress: ${completed} ok / ${failed} fail / ${done.size}/${files.length} total`
    );
    writeFileSync(PROGRESS_FILE, JSON.stringify([...done]));
  }
}

async function main() {
  let i = 0;
  const workers = Array.from({ length: CONCURRENCY }, async () => {
    while (i < todo.length) {
      const idx = i++;
      await uploadOne(todo[idx]);
    }
  });
  await Promise.all(workers);
  writeFileSync(PROGRESS_FILE, JSON.stringify([...done]));
  console.log(`DONE. completed=${completed} failed=${failed}`);
  if (failedKeys.length) {
    writeFileSync(path.join(DATA_DIR, "r2_upload_failed.json"), JSON.stringify(failedKeys));
    console.log(`Wrote ${failedKeys.length} failed keys to data/r2_upload_failed.json`);
  }
}

main();
