import { NextResponse } from "next/server";

const BLOB_BASE = "https://izr20vnpplvtebl1.private.blob.vercel-storage.com";
const BLOB_TOKEN = process.env.BLOB_READ_WRITE_TOKEN || "";

async function fetchChapter(slug: string, num: number) {
  if (!BLOB_TOKEN) {
    // Local dev fallback
    try {
      const fs = await import("fs");
      const dir = `data/chapters/${slug}`;
      const files = fs.readdirSync(dir).filter((f: string) => f.endsWith(".json"));
      const target = files.find((f: string) => {
        const m = f.match(/ch(?:apter)?[_-]?(\d+)/i);
        return m && parseInt(m[1]) === num;
      });
      if (!target) return null;
      const content = fs.readFileSync(`${dir}/${target}`, "utf-8");
      return JSON.parse(content);
    } catch {
      return null;
    }
  }

  // Try blob: first check which slug maps to the chapter dir
  // Chapter dirs use the same slug as novels.json, files use ch-N.json format
  const blobPath = `data/chapters/${slug}/ch-${num}.json`;
  try {
    const res = await fetch(`${BLOB_BASE}/${blobPath}`, {
      headers: { Authorization: `Bearer ${BLOB_TOKEN}` },
      next: { revalidate: 60 },
    });
    if (res.ok) return res.json();
  } catch {}

  // Try chapter-N format as fallback
  const altPath = `data/chapters/${slug}/chapter-${num}.json`;
  try {
    const res = await fetch(`${BLOB_BASE}/${altPath}`, {
      headers: { Authorization: `Bearer ${BLOB_TOKEN}` },
      next: { revalidate: 60 },
    });
    if (res.ok) return res.json();
  } catch {}

  return null;
}

export async function GET(
  req: Request,
  { params }: { params: { slug: string; num: string } }
) {
  const num = parseInt(params.num);
  if (isNaN(num) || num < 1) {
    return NextResponse.json({ error: "Invalid chapter number" }, { status: 400 });
  }

  const chapter = await fetchChapter(params.slug, num);

  if (!chapter) {
    return NextResponse.json({ error: "Chapter not found" }, { status: 404 });
  }

  return NextResponse.json(chapter);
}
