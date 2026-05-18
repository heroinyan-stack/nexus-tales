import Link from "next/link";
import { ChevronLeft, ChevronRight, Sun, Moon, Type, ArrowLeft } from "lucide-react";
import { notFound } from "next/navigation";
import { getNovelBySlug, getChapterContent } from "@/lib/novels";

// This is a client component for the reading controls
import ChapterReaderClient from "./ChapterReaderClient";

export default async function ChapterPage({ params }: { params: { slug: string; num: string } }) {
  const novel = getNovelBySlug(params.slug);
  const chapterNum = parseInt(params.num);

  if (!novel) notFound();

  const content = getChapterContent(params.slug, chapterNum);
  const title = `Chapter ${chapterNum}`;

  return (
    <div className="pt-24 pb-24">
      <div className="max-w-3xl mx-auto px-6">
        {/* Header */}
        <div className="mb-10">
          <Link
            href={`/novel/${params.slug}`}
            className="inline-flex items-center gap-2 text-moon/40 hover:text-neon-cyan transition-colors mb-6 text-sm"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to {novel.title_en}
          </Link>
          <h1
            className="text-3xl lg:text-4xl font-bold text-stardust mb-2"
            style={{ fontFamily: "Orbitron" }}
          >
            <span className="text-gradient">Chapter {chapterNum}</span>
          </h1>
          <h2 className="text-xl text-moon/50">{title}</h2>
        </div>

        {/* Content - passing to client for reading controls */}
        <ChapterReaderClient
          content={content}
          novelSlug={params.slug}
          chapterNum={chapterNum}
          totalChapters={novel.total_chapters}
        />
      </div>
    </div>
  );
}