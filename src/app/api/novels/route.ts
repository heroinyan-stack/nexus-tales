import { NextResponse } from "next/server";
import { getR2Json } from "@/lib/r2";

// Minimum chapters to show on homepage
const MIN_HOMEPAGE_CHAPTERS = 3;

export async function GET() {
  try {
    const [novels, extMap] = await Promise.all([
      getR2Json<any[]>("data/novels.json"),
      getR2Json<Record<string, string>>("data/cover-manifest.json"),
    ]);

    if (!novels) {
      return NextResponse.json({ novels: [], genres: [] });
    }

    // Attach cover info
    for (const n of novels) {
      const ext = extMap?.[n.slug] || ".jpg";
      n.cover_ext = ext;
      n.cover_url = `/covers/${n.slug}${ext}`;
    }

    // Filter: enough chapters + English-or-Chinese description (>=30 chars, CJK-free)
    // description_zh added as fallback so Chinese-only novels still pass
    const filtered = novels.filter((n: any) => {
      const chCount = n.available_chapters || n.chapter_count || 0;
      if (chCount < MIN_HOMEPAGE_CHAPTERS) return false;
      const desc = n.description_en || n.description_zh || "";
      if (desc.length >= 30 && isMostlyCJK(desc)) return false;
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
    console.error("Error loading novels:", error);
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
