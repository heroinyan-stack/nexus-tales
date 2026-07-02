import { MetadataRoute } from "next";
import { getAllNovels, getChapterList } from "@/lib/novels";
import fs from "fs";
import path from "path";

const BASE_URL = "https://novelhub.beauty";
const CHAPTERS_DIR = path.join(process.cwd(), "data", "chapters");

function safeDate(val?: string): Date {
  if (!val) return new Date();
  try {
    const d = new Date(val);
    if (isNaN(d.getTime())) return new Date();
    return d;
  } catch {
    return new Date();
  }
}

/** Get last-modified date for a chapter file (returns novel updated_at as fallback) */
function chapterLastMod(novelSlug: string, chapterNum: number, fallback: Date): Date {
  const dir = path.join(CHAPTERS_DIR, novelSlug);
  if (!fs.existsSync(dir)) return fallback;
  // Try ch-XXXX.json format
  const padded = String(chapterNum).padStart(4, '0');
  const candidates = [
    `ch-${padded}.json`,
    `ch-${chapterNum}.json`,
  ];
  for (const fn of candidates) {
    const fp = path.join(dir, fn);
    if (fs.existsSync(fp)) {
      try {
        const stat = fs.statSync(fp);
        return stat.mtime;
      } catch {
        // fall through
      }
    }
  }
  return fallback;
}

export default function sitemap(): MetadataRoute.Sitemap {
  const novels = getAllNovels();

  const routes: MetadataRoute.Sitemap = [
    {
      url: BASE_URL,
      lastModified: new Date(),
      changeFrequency: "daily",
      priority: 1,
    },
    {
      url: `${BASE_URL}/novels`,
      lastModified: new Date(),
      changeFrequency: "daily",
      priority: 0.9,
    },
    {
      url: `${BASE_URL}/blog`,
      lastModified: new Date(),
      changeFrequency: "weekly",
      priority: 0.8,
    },
    {
      url: `${BASE_URL}/pricing`,
      lastModified: new Date(),
      changeFrequency: "monthly",
      priority: 0.7,
    },
    {
      url: `${BASE_URL}/terms`,
      lastModified: new Date(),
      changeFrequency: "monthly",
      priority: 0.3,
    },
    {
      url: `${BASE_URL}/privacy`,
      lastModified: new Date(),
      changeFrequency: "monthly",
      priority: 0.3,
    },
    {
      url: `${BASE_URL}/contact`,
      lastModified: new Date(),
      changeFrequency: "monthly",
      priority: 0.3,
    },
  ];

  // Add blog post pages
  const blogFile = path.join(process.cwd(), "data", "blog", "posts.json");
  if (fs.existsSync(blogFile)) {
    const posts = JSON.parse(fs.readFileSync(blogFile, "utf-8"));
    for (const post of posts) {
      routes.push({
        url: `${BASE_URL}/blog/${post.slug}`,
        lastModified: safeDate(post.date),
        changeFrequency: "monthly",
        priority: 0.7,
      });
    }
  }

  for (const novel of novels) {
    const novelDate = safeDate(novel.updated_at);

    // Novel page with per-novel freshness
    routes.push({
      url: `${BASE_URL}/novel/${novel.slug}`,
      lastModified: novelDate,
      changeFrequency: "weekly",
      priority: novel.zone === "free" ? 0.9 : 0.8,
    });

    // Only include chapters with valid English translations
    const chapters = getChapterList(novel.slug);
    for (const ch of chapters) {
      const chDate = chapterLastMod(novel.slug, ch.num, novelDate);
      routes.push({
        url: `${BASE_URL}/novel/${novel.slug}/chapter/${ch.num}`,
        lastModified: chDate,
        // First 5 chapters: higher priority (onboarding), rest: standard
        changeFrequency: ch.num <= 5 ? "weekly" : "monthly",
        priority: ch.num <= 5 ? 0.7 : 0.6,
      });
    }
  }

  return routes;
}
