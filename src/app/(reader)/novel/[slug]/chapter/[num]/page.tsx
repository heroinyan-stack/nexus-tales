import Link from "next/link";
import type { Metadata } from "next";
import { ChevronLeft, ChevronRight, Sun, Moon, Type, ArrowLeft } from "lucide-react";
import { notFound } from "next/navigation";
import { getNovelBySlug, getChapterContent } from "@/lib/novels";

// This is a client component for the reading controls
import ChapterReaderClient from "./ChapterReaderClient";

const BASE_URL = "https://nexus-tales.vercel.app";

export async function generateMetadata({ params }: { params: { slug: string; num: string } }): Promise<Metadata> {
  const novel = getNovelBySlug(params.slug);
  if (!novel) return {};
  const chapterNum = parseInt(params.num);
  const content = getChapterContent(params.slug, chapterNum);
  const title = `Chapter ${chapterNum} — ${novel.title_en}`;
  const excerpt = content ? content.slice(0, 160) : `Read ${novel.title_en} Chapter ${chapterNum} online free.`;

  return {
    title: `Ch.${chapterNum} — ${novel.title_en}`,
    description: excerpt,
    alternates: { canonical: `${BASE_URL}/novel/${novel.slug}/chapter/${chapterNum}` },
    openGraph: {
      title,
      description: excerpt,
      url: `${BASE_URL}/novel/${novel.slug}/chapter/${chapterNum}`,
      type: "article",
    },
    twitter: {
      card: "summary_large_image",
      title,
      description: excerpt,
    },
  };
}

export default async function ChapterPage({ params }: { params: { slug: string; num: string } }) {
  const novel = getNovelBySlug(params.slug);
  const chapterNum = parseInt(params.num);

  if (!novel) notFound();

  const content = getChapterContent(params.slug, chapterNum);
  const title = `Chapter ${chapterNum}`;

  const jsonLdArticle = {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: `${novel.title_en} — Chapter ${chapterNum}`,
    author: { "@type": "Person", name: novel.author_en },
    publisher: { "@type": "Organization", name: "Nexus Tales" },
    url: `${BASE_URL}/novel/${novel.slug}/chapter/${chapterNum}`,
    isPartOf: {
      "@type": "Book",
      name: novel.title_en,
      url: `${BASE_URL}/novel/${novel.slug}`,
    },
    inLanguage: "en",
  };

  return (
    <>
      {/* JSON-LD structured data */}
      <script type="application/ld+json" dangerouslySetInnerHTML={{
        __html: JSON.stringify(jsonLdArticle),
      }} />
      
      {/* Full-screen reader - no header/footer, fully immersive */}
      <ChapterReaderClient
        content={content}
        novelSlug={params.slug}
        chapterNum={chapterNum}
        totalChapters={novel.total_chapters}
        novelTitle={novel.title_en}
      />
    </>
  );
}