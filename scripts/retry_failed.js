#!/usr/bin/env node
const BLOB_BASE = "https://izr20vnpplvtebl1.private.blob.vercel-storage.com";
const TOKEN = process.env.BLOB_READ_WRITE_TOKEN || process.argv[2] || "";
const fs = require("fs");

const failed = [
  "data/chapters/novel-123-the-proud-alchemy-god/ch-0210.json",
  "data/chapters/novel-123-the-proud-alchemy-god/ch-0211.json",
  "data/chapters/novel-123-the-proud-alchemy-god/ch-0213.json",
  "data/chapters/novel-123-the-proud-alchemy-god/ch-0212.json",
  "data/chapters/novel-123-the-proud-alchemy-god/ch-0216.json",
];

(async () => {
  for (const path of failed) {
    try {
      const content = fs.readFileSync(path);
      const res = await fetch(`${BLOB_BASE}/${path}`, {
        method: "PUT",
        headers: { "Authorization": `Bearer ${TOKEN}`, "Content-Type": "application/json" },
        body: content,
      });
      console.log(res.ok ? `✅ ${path}` : `❌ ${path}: ${res.status}`);
    } catch(e) {
      console.error(`❌ ${path}: ${e.message}`);
    }
    await new Promise(r => setTimeout(r, 2000));
  }
})();
