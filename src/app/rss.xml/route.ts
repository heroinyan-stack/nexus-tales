import { getAllNovels } from "@/lib/novels";
import fs from "fs";
import path from "path";

// Simple XML builder without external dependency
function escapeXml(str: string): string {
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&apos;");
}

const BASE_URL = "https://novelhub.beauty";
const CHAPTERS_DIR = path.join(process.cwd(), "data", "chapters");

function getLatestChapters(limit = 50) {
  const novels = getAllNovels();
  const entries: { slug: string; title: string; chapterNum: number; date: Date }[] = [];

  for (const novel of novels.slice(0, 100)) {
    const dir = path.join(CHAPTERS_DIR, novel.slug);
    if (!fs.existsSync(dir)) continue;
    const files = fs.readdirSync(dir).filter(f => f.endsWith(".json"));
    // Get the last 3 chapters per novel
    const nums = files
      .map(f => parseInt(f.replace(/[^0-9]/g, "")) || 0)
      .filter(n => n > 0)
      .sort((a, b) => b - a)
      .slice(0, 3);

    for (const num of nums) {
      const fp = path.join(dir, `ch-${String(num).padStart(4, "0")}.json`);
      const altFp = path.join(dir, `ch-${num}.json`);
      const realPath = fs.existsSync(fp) ? fp : (fs.existsSync(altFp) ? altFp : null);
      if (realPath) {
        try {
          const stat = fs.statSync(realPath);
          entries.push({ slug: novel.slug, title: novel.title_en, chapterNum: num, date: stat.mtime });
        } catch { /* skip */ }
      }
    }
  }
  return entries.sort((a, b) => b.date.getTime() - a.date.getTime()).slice(0, limit);
}

export async function GET() {
  const latestChapters = getLatestChapters(50);

  const items = latestChapters.map(ch => `
    <item>
      <title>${escapeXml(ch.title)} — Chapter ${ch.chapterNum}</title>
      <link>${BASE_URL}/novel/${ch.slug}/chapter/${ch.chapterNum}</link>
      <guid isPermaLink="true">${BASE_URL}/novel/${ch.slug}/chapter/${ch.chapterNum}</guid>
      <pubDate>${ch.date.toUTCString()}</pubDate>
      <description>Read ${escapeXml(ch.title)} Chapter ${ch.chapterNum} online free at Nexus Tales. New translated cultivation &amp; fantasy chapters added daily.</description>
    </item>
  `).join("\n");

  const rss = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Nexus Tales — New Translated Chapters</title>
    <link>${BASE_URL}</link>
    <description>Latest translated Chinese cultivation &amp; fantasy novel chapters. Read free online.</description>
    <language>en-us</language>
    <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>
    <atom:link href="${BASE_URL}/rss.xml" rel="self" type="application/rss+xml"/>
    ${items}
  </channel>
</rss>`;

  return new Response(rss, {
    headers: {
      "Content-Type": "application/xml; charset=utf-8",
      "Cache-Control": "public, max-age=3600, s-maxage=3600",
    },
  });
}

export const dynamic = "force-dynamic";
