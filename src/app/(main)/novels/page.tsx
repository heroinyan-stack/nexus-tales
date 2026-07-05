import type { Metadata } from "next";
import fs from "fs";
import path from "path";
import { isNovelFullyTranslated } from "@/lib/novels";
import NovelsClient from "./NovelsClient";

export const metadata: Metadata = {
  title: "Browse All Novels",
  description:
    "Browse all translated cultivation, xianxia, wuxia, and classic Chinese novels. Free chapters available daily.",
  alternates: { canonical: "https://novelhub.beauty/novels" },
  openGraph: {
    title: "Browse All Novels | Nexus Tales",
    description:
      "Browse all translated cultivation, xianxia, wuxia, and classic Chinese novels. Free chapters available daily.",
    url: "https://novelhub.beauty/novels",
    siteName: "Nexus Tales",
    type: "website",
  },
};

interface Novel {
  id: number;
  slug: string;
  title_en: string;
  author_en: string;
  genre: string;
  tags: string[];
  is_adult: boolean;
  status: string;
  rating: number;
  total_chapters: number;
  readers: number;
  description_en: string;
  zone: string;
  cover_ext?: string;
  cover_url?: string;
  available_chapters?: number;
}

interface Genre {
  name: string;
  count: number;
  is_adult: boolean;
}

const NOVELS_FILE = path.join(process.cwd(), "data", "novels.json");
const COVER_MANIFEST = path.join(process.cwd(), "data", "cover-manifest.json");
const CHAPTERS_DIR = path.join(process.cwd(), "data", "chapters");
const MIN_CHAPTERS = 3;

function loadNovels(): { novels: Novel[]; genres: Genre[] } {
  if (!fs.existsSync(NOVELS_FILE)) return { novels: [], genres: [] };

  const novels: Novel[] = JSON.parse(fs.readFileSync(NOVELS_FILE, "utf-8"));

  // Chapter counts
  const chapterCounts: Record<string, number> = {};
  if (fs.existsSync(CHAPTERS_DIR)) {
    for (const dir of fs.readdirSync(CHAPTERS_DIR)) {
      const dirPath = path.join(CHAPTERS_DIR, dir);
      if (fs.statSync(dirPath).isDirectory()) {
        chapterCounts[dir] = fs
          .readdirSync(dirPath)
          .filter((f) => f.startsWith("ch-") || f.startsWith("chapter-")).length;
      }
    }
  }

  // Cover manifest
  let extMap: Record<string, string> = {};
  if (fs.existsSync(COVER_MANIFEST)) {
    try {
      extMap = JSON.parse(fs.readFileSync(COVER_MANIFEST, "utf-8"));
    } catch {}
  }

  for (const n of novels) {
    const ext = extMap[n.slug] || "jpg";
    n.cover_ext = ext;
    n.cover_url = ext.startsWith("-gen.")
      ? `/covers/${n.slug}${ext}`
      : `/covers/${n.slug}.${ext}`;
    n.available_chapters = chapterCounts[n.slug] || 0;
  }

  // Filter novels with enough chapters & fully translated
  const filtered = novels.filter((n) => {
    if (!n.slug) return false;
    if ((n.available_chapters || 0) < MIN_CHAPTERS) return false;
    return isNovelFullyTranslated(n.slug);
  });

  // Genre map
  const genreMap = new Map<string, Genre>();
  for (const n of filtered) {
    const g = genreMap.get(n.genre);
    if (g) {
      g.count++;
    } else {
      genreMap.set(n.genre, { name: n.genre, count: 1, is_adult: n.is_adult });
    }
  }
  const genres = Array.from(genreMap.values());

  return { novels: filtered, genres };
}

export default function NovelsPage() {
  const { novels, genres } = loadNovels();

  return <NovelsClient novels={novels} genres={genres} />;
}
