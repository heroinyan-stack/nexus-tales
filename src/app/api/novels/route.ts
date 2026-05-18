import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

const NOVELS_FILE = path.join(process.cwd(), "data", "novels.json");

export async function GET() {
  try {
    if (!fs.existsSync(NOVELS_FILE)) {
      return NextResponse.json({ novels: [], genres: [] });
    }
    
    const content = fs.readFileSync(NOVELS_FILE, "utf-8");
    const novels = JSON.parse(content);

    // Build genre list
    const genreMap = new Map();
    novels.forEach((n: any) => {
      const existing = genreMap.get(n.genre);
      if (existing) {
        existing.count++;
      } else {
        genreMap.set(n.genre, { name: n.genre, count: 1, is_adult: n.is_adult });
      }
    });

    const genres = Array.from(genreMap.values());

    return NextResponse.json({ novels, genres });
  } catch (error) {
    console.error("Error reading novels:", error);
    return NextResponse.json({ novels: [], genres: [], error: "Failed to load" }, { status: 500 });
  }
}