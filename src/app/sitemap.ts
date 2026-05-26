import { MetadataRoute } from "next";
import { getAllNovels, getChapterList } from "@/lib/novels";

const BASE_URL = "https://novelhub.beauty";

export default function sitemap(): MetadataRoute.Sitemap {
  const novels = getAllNovels();
  
  // Homepage
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

  // Each novel detail page
  for (const novel of novels) {
    // Novel detail
    routes.push({
      url: `${BASE_URL}/novel/${novel.slug}`,
      lastModified: new Date(novel.updated_at),
      changeFrequency: "weekly",
      priority: novel.zone === "free" ? 0.9 : 0.8,
    });

    // Chapter pages
    const chapters = getChapterList(novel.slug);
    for (const ch of chapters) {
      routes.push({
        url: `${BASE_URL}/novel/${novel.slug}/chapter/${ch.num}`,
        lastModified: new Date(novel.updated_at),
        changeFrequency: "monthly",
        priority: 0.6,
      });
    }
  }

  return routes;
}
