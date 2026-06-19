import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";
const NOVELS_FILE = path.join(process.cwd(), "data", "novels.json");
const COVER_MANIFEST = path.join(process.cwd(), "data", "cover-manifest.json");
const CHAPTERS_DIR = path.join(process.cwd(), "data", "chapters");

// Minimum chapters to show on homepage (AdSense quality threshold)
const MIN_HOMEPAGE_CHAPTERS = 3;

export async function GET() {
  try {
    if (!fs.existsSync(NOVELS_FILE)) {
      return NextResponse.json({ novels: [], genres: [] });
    }
    
    const content = fs.readFileSync(NOVELS_FILE, "utf-8");
    const novels = JSON.parse(content);

    // Count chapters per novel for quality filtering
    const chapterCounts: Record<string, number> = {};
    if (fs.existsSync(CHAPTERS_DIR)) {
      const dirs = fs.readdirSync(CHAPTERS_DIR);
      for (const dir of dirs) {
        const dirPath = path.join(CHAPTERS_DIR, dir);
        if (fs.statSync(dirPath).isDirectory()) {
          const files = fs.readdirSync(dirPath).filter(f => f.startsWith('ch-') || f.startsWith('chapter-'));
          chapterCounts[dir] = files.length;
        }
      }
    }

    // Attach cover extension (jpg or svg) to each novel
    let extMap: Record<string, string> = {};
    if (fs.existsSync(COVER_MANIFEST)) {
      try {
        extMap = JSON.parse(fs.readFileSync(COVER_MANIFEST, "utf-8"));
      } catch {}
    }

    for (const n of novels) {
      n.cover_ext = extMap[n.slug] || "jpg";
      n.available_chapters = chapterCounts[n.slug] || 0;
    }

    const novelsWithCover = novels;

    // Build genre list (only from novels with chapters)
    const genreMap = new Map();
    for (const n of novelsWithCover) {
      if ((n.available_chapters || 0) < MIN_HOMEPAGE_CHAPTERS) continue;
      const existing = genreMap.get(n.genre);
      if (existing) {
        existing.count++;
      } else {
        genreMap.set(n.genre, { name: n.genre, count: 1, is_adult: n.is_adult });
      }
    }

    const genres = Array.from(genreMap.values());

    return NextResponse.json({ novels: novelsWithCover, genres });
  } catch (error) {
    console.error("Error reading novels:", error);
    return NextResponse.json({ novels: [], genres: [], error: "Failed to load" }, { status: 500 });
  }
}