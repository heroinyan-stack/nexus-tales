import { NextResponse } from "next/server";

// Blob store — public URLs (no Bearer needed for reads)
const BLOB_BASE = "https://izr20vnpplvtebl1.private.blob.vercel-storage.com";
const BLOB_TOKEN = process.env.BLOB_READ_WRITE_TOKEN || "";

// Minimum chapters to show on homepage
const MIN_HOMEPAGE_CHAPTERS = 3;

async function fetchBlobJson<T>(path: string): Promise<T | null> {
  if (!BLOB_TOKEN) {
    // Fallback to local fs for local dev
    try {
      const fs = await import("fs");
      const filePath = `${process.cwd()}/data/${path}`;
      const content = fs.readFileSync(filePath, "utf-8");
      return JSON.parse(content) as T;
    } catch {
      return null;
    }
  }
  try {
    const res = await fetch(`${BLOB_BASE}/${path}`, {
      next: { revalidate: 60 },
    });
    if (!res.ok) {
      // Fallback: try with Bearer token
      if (BLOB_TOKEN) {
        const res2 = await fetch(`${BLOB_BASE}/${path}`, {
          headers: { Authorization: `Bearer ${BLOB_TOKEN}` },
          next: { revalidate: 60 },
        });
        if (res2.ok) return res2.json() as Promise<T>;
      }
      return null;
    }
    return res.json() as Promise<T>;
  } catch {
    return null;
  }
}

export async function GET() {
  try {
    const [novels, extMap] = await Promise.all([
      fetchBlobJson<any[]>("novels.json"),
      fetchBlobJson<Record<string, string>>("cover-manifest.json"),
    ]);

    if (!novels) {
      return NextResponse.json({ novels: [], genres: [] });
    }

    // Attach cover info
    for (const n of novels) {
      const ext = extMap?.[n.slug] || ".jpg";
      n.cover_ext = ext;
      n.cover_url = ext.startsWith("-gen")
        ? `/covers/${n.slug}${ext}`
        : `/covers/${n.slug}${ext}`;
    }

    // Filter: enough chapters + valid English (not CJK-heavy)
    const filtered = novels.filter((n: any) => {
      const chCount = n.available_chapters || n.chapter_count || 0;
      if (chCount < MIN_HOMEPAGE_CHAPTERS) return false;
      const desc = n.description_en || "";
      if (isMostlyCJK(desc)) return false;
      return true;
    });

    // Build genre list
    const genreMap = new Map<string, any>();
    for (const n of filtered) {
      const existing = genreMap.get(n.genre);
      if (existing) {
        existing.count++;
      } else {
        genreMap.set(n.genre, { name: n.genre, count: 1, is_adult: n.is_adult });
      }
    }

    return NextResponse.json({
      novels: filtered,
      genres: Array.from(genreMap.values()),
    });
  } catch (error) {
    console.error("Error loading novels from Blob:", error);
    return NextResponse.json(
      { novels: [], genres: [], error: "Failed to load" },
      { status: 500 }
    );
  }
}

function isMostlyCJK(text: string): boolean {
  if (!text || text.length < 30) return false;
  const sample = text.slice(0, 1000);
  let cjk = 0;
  for (const c of sample) {
    const code = c.charCodeAt(0);
    if ((code >= 0x4e00 && code <= 0x9fff) || (code >= 0x3400 && code <= 0x4dbf)) cjk++;
  }
  return cjk / sample.length > 0.15;
}
