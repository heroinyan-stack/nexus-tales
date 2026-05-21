import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

const NOVELS_FILE = path.join(process.cwd(), "data", "novels.json");
const COVER_MANIFEST = path.join(process.cwd(), "data", "cover-manifest.json");

export async function GET() {
  try {
    if (!fs.existsSync(NOVELS_FILE)) {
      return NextResponse.json({ novels: [], genres: [] });
    }
    
    const content = fs.readFileSync(NOVELS_FILE, "utf-8");
    const novels = JSON.parse(content);

    // Attach cover extension (jpg or svg) to each novel
    let extMap: Record<string, string> = {};
    if (fs.existsSync(COVER_MANIFEST)) {
      try {
        extMap = JSON.parse(fs.readFileSync(COVER_MANIFEST, "utf-8"));
      } catch {}
    }
    const novelsWithCover = novels.map((n: any) => ({
      ...n,
      cover_ext: extMap[n.slug] || "jpg",
    }));

    // Build genre list
    const genreMap = new Map();
    novelsWithCover.forEach((n: any) => {
      const existing = genreMap.get(n.genre);
      if (existing) {
        existing.count++;
      } else {
        genreMap.set(n.genre, { name: n.genre, count: 1, is_adult: n.is_adult });
      }
    });

    const genres = Array.from(genreMap.values());

    return NextResponse.json({ novels: novelsWithCover, genres });
  } catch (error) {
    console.error("Error reading novels:", error);
    return NextResponse.json({ novels: [], genres: [], error: "Failed to load" }, { status: 500 });
  }
}