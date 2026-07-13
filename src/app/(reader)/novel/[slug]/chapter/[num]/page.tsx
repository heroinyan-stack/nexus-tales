import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getNovelBySlug, getChapterContent } from "@/lib/novels";
import ChapterReaderClient from "./ChapterReaderClient";
import ChapterGate from "@/components/ChapterGate";
import Breadcrumbs from "@/components/Breadcrumbs";

const BASE_URL = "https://novelhub.beauty";
const PLACEHOLDER_PREFIX = "This chapter is being translated";
const NOT_AVAILABLE = "Content not available.";

function isPlaceholderContent(content: string): boolean {
  return content === NOT_AVAILABLE || content.startsWith(PLACEHOLDER_PREFIX);
}

export async function generateMetadata({ params }: { params: { slug: string; num: string } }): Promise<Metadata> {
  const novel = getNovelBySlug(params.slug);
  if (!novel) return {};
  const chapterNum = parseInt(params.num);
  const content = getChapterContent(params.slug, chapterNum);
  const isPlaceholder = isPlaceholderContent(content);
  const title = `Chapter ${chapterNum} — ${novel.title_en}`;
  const description = isPlaceholder
    ? `Read ${novel.title_en} online free at Nexus Tales. Chapter ${chapterNum} coming soon — translated cultivation novel chapters added daily.`
    : `Read ${novel.title_en} Chapter ${chapterNum} online free. ${content.slice(0, 120)}...`;

  return {
    title: `Ch.${chapterNum} — ${novel.title_en}`,
    description,
    alternates: { canonical: `${BASE_URL}/novel/${novel.slug}/chapter/${chapterNum}` },
    robots: isPlaceholder ? { index: false, follow: true } : { index: true, follow: true },
    openGraph: {
      title,
      description,
      url: `${BASE_URL}/novel/${novel.slug}/chapter/${chapterNum}`,
      type: "article",
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
    },
  };
}

export default async function ChapterPage({ params }: { params: { slug: string; num: string } }) {
  const novel = getNovelBySlug(params.slug);
  const chapterNum = parseInt(params.num);

  if (!novel) notFound();

  const content = getChapterContent(params.slug, chapterNum);
  const isPlaceholder = isPlaceholderContent(content);
  const title = `Chapter ${chapterNum}`;
  const chapterUrl = `${BASE_URL}/novel/${novel.slug}/chapter/${chapterNum}`;
  const novelUrl = `${BASE_URL}/novel/${novel.slug}`;

  const jsonLdBreadcrumb = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: "Home", item: BASE_URL },
      { "@type": "ListItem", position: 2, name: novel.title_en, item: novelUrl },
      { "@type": "ListItem", position: 3, name: `Chapter ${chapterNum}` },
    ],
  };

  const jsonLdArticle = {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: `${novel.title_en} — Chapter ${chapterNum}`,
    author: { "@type": "Person", name: novel.author_en },
    publisher: { "@type": "Organization", name: "Nexus Tales", url: BASE_URL },
    url: chapterUrl,
    isPartOf: {
      "@type": "Book",
      name: novel.title_en,
      url: novelUrl,
    },
    inLanguage: "en",
  };

  return (
    <>
      {/* JSON-LD structured data */}
      <script type="application/ld+json" dangerouslySetInnerHTML={{
        __html: JSON.stringify(jsonLdBreadcrumb),
      }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{
        __html: JSON.stringify(jsonLdArticle),
      }} />
      
      {/* Access gate — locks chapter 6+ for non-premium users */}
      <ChapterGate
        chapterNum={chapterNum}
        novelSlug={params.slug}
        novelTitle={novel.title_en}
        zone={novel.zone}
        totalChapters={novel.available_chapters || novel.total_chapters}
      />

      {/* Full-screen reader - no header/footer, fully immersive */}
      <ChapterReaderClient
        content={content}
        novelSlug={params.slug}
        chapterNum={chapterNum}
        totalChapters={novel.available_chapters || novel.total_chapters}
        novelTitle={novel.title_en}
        zone={novel.zone}
        breadcrumbs={
          <Breadcrumbs
            items={[
              { label: "Home", href: "/" },
              { label: "Novels", href: "/novels" },
              { label: novel.title_en, href: `/novel/${novel.slug}` },
              { label: `Chapter ${chapterNum}` },
            ]}
          />
        }
      />
    </>
  );
}