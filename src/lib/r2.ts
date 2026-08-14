import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";
import fs from "fs";
import path from "path";

const ACCOUNT_ID = process.env.R2_ACCOUNT_ID || "";
const ACCESS_KEY_ID = process.env.R2_ACCESS_KEY_ID || "";
const SECRET_ACCESS_KEY = process.env.R2_SECRET_ACCESS_KEY || "";
const BUCKET = process.env.R2_BUCKET || "";

const DATA_DIR = path.join(process.cwd(), "data");

function getClient(): S3Client | null {
  if (!ACCOUNT_ID || !ACCESS_KEY_ID || !SECRET_ACCESS_KEY || !BUCKET) return null;
  return new S3Client({
    region: "auto",
    endpoint: `https://${ACCOUNT_ID}.r2.cloudflarestorage.com`,
    credentials: { accessKeyId: ACCESS_KEY_ID, secretAccessKey: SECRET_ACCESS_KEY },
    // R2 returns incorrect x-amz-checksum-crc32 headers for some objects,
    // causing false ChecksumMismatch errors on GET. Content is correct,
    // so we disable response checksum validation.
    responseChecksumValidation: "NEVER",
  });
}

/** Read a JSON file from R2 (production) or local disk (dev fallback). */
export async function getR2Json<T>(key: string): Promise<T | null> {
  const client = getClient();
  if (!client) {
    try {
      const p = path.join(DATA_DIR, key);
      if (fs.existsSync(p)) return JSON.parse(fs.readFileSync(p, "utf-8")) as T;
    } catch {
      /* ignore */
    }
    return null;
  }
  try {
    const res = await client.send(new GetObjectCommand({ Bucket: BUCKET, Key: key }));
    const body = await res.Body?.transformToString();
    if (!body) return null;
    return JSON.parse(body) as T;
  } catch {
    return null;
  }
}

/**
 * Read a single chapter from R2 (production) or local disk (dev fallback).
 * Handles the inconsistent on-disk naming: ch-N.json, ch-0016.json (padded),
 * chapter-N.json, chapter-0016.json.
 */
export async function getR2Chapter(slug: string, num: number): Promise<any | null> {
  const client = getClient();

  const variants = [
    `${num}`,
    `${String(num).padStart(3, "0")}`,
    `${String(num).padStart(4, "0")}`,
    `${String(num).padStart(5, "0")}`,
  ];
  const keys: string[] = [];
  for (const prefix of ["ch-", "chapter-"]) {
    for (const v of variants) keys.push(`data/chapters/${slug}/${prefix}${v}.json`);
  }

  if (!client) {
    // Dev fallback: read from local disk
    try {
      const dir = path.join(DATA_DIR, "chapters", slug);
      if (!fs.existsSync(dir)) return null;
      const files = fs.readdirSync(dir).filter((f: string) => f.endsWith(".json"));
      const target = files.find((f: string) => {
        const m = f.match(/ch(?:apter)?[_-]?(\d+)/i);
        return m && parseInt(m[1], 10) === num;
      });
      if (!target) return null;
      return JSON.parse(fs.readFileSync(path.join(dir, target), "utf-8"));
    } catch {
      return null;
    }
  }

  for (const key of keys) {
    try {
      const res = await client.send(new GetObjectCommand({ Bucket: BUCKET, Key: key }));
      const body = await res.Body?.transformToString();
      if (body) return JSON.parse(body);
    } catch {
      /* try next variant */
    }
  }
  return null;
}
