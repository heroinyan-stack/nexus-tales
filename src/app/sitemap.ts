import { MetadataRoute } from "next";
import { getAllNovels, getChapterList } from "@/lib/novels";
import fs from "fs";
import path from "path";

const BASE_URL = "https://novelhub.beauty";

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
    const lastMod = safeDate(novel.updated_at);

    routes.push({
      url: `${BASE_URL}/novel/${novel.slug}`,
      lastModified: lastMod,
      changeFrequency: "weekly",
      priority: novel.zone === "free" ? 0.9 : 0.8,
    });

    const chapters = getChapterList(novel.slug);
    for (const ch of chapters) {
      routes.push({
        url: `${BASE_URL}/novel/${novel.slug}/chapter/${ch.num}`,
        lastModified: lastMod,
        changeFrequency: "monthly",
        priority: 0.6,
      });
    }
  }

  return routes;
}
