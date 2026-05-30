import { MetadataRoute } from "next";
import { getAllNovels, getChapterList } from "@/lib/novels";

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
  ];

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
