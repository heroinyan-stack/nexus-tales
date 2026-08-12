#!/usr/bin/env node
/**
 * Upload small metadata files to Vercel Blob
 */
const BLOB_BASE = "https://izr20vnpplvtebl1.private.blob.vercel-storage.com";
const TOKEN = process.env.BLOB_READ_WRITE_TOKEN;

const files = [
  "data/blog/posts.json",
];

async function uploadFile(localPath, blobPath) {
  const fs = await import("fs");
  const content = fs.readFileSync(localPath);
  const res = await fetch(`${BLOB_BASE}/${blobPath}`, {
    method: "PUT",
    headers: {
      "Authorization": `Bearer ${TOKEN}`,
      "Content-Type": "application/json",
    },
    body: content,
  });
  if (res.ok) {
    console.log(`✅ Uploaded: ${blobPath}`);
  } else {
    const text = await res.text();
    console.error(`❌ Failed: ${blobPath} — ${res.status} ${text}`);
  }
  return res.ok;
}

(async () => {
  for (const file of files) {
    await uploadFile(file, file);
  }
  console.log("Done.");
})();
