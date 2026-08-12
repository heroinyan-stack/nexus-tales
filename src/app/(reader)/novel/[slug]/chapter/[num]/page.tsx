import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getNovelBySlug } from "@/lib/novels";
import ChapterReaderClient from "./ChapterReaderClient";

const BASE_URL = "https://novelhub.beauty";

export async function generateMetadata({ params }: { params: { slug: string; num: string } }): Promise<Metadata> {
  const novel = getNovelBySlug(params.slug);
  if (!novel) return {};
  const chapterNum = parseInt(params.num);

  return {
    title: `Ch.${chapterNum} — ${novel.title_en}`,
    description: `Read ${novel.title_en} Chapter ${chapterNum} online free at Nexus Tales.`,
    alternates: { canonical: `${BASE_URL}/novel/${novel.slug}/chapter/${chapterNum}` },
    robots: { index: true, follow: true },
  };
}

export default async function ChapterPage({ params }: { params: { slug: string; num: string } }) {
  const novel = getNovelBySlug(params.slug);
  const chapterNum = parseInt(params.num);

  if (!novel) notFound();

  return (
    <ChapterReaderClient
      novelSlug={novel.slug}
      chapterNum={chapterNum}
      totalChapters={novel.available_chapters || novel.total_chapters}
      novelTitle={novel.title_en}
      zone={novel.zone}
    />
  );
}
