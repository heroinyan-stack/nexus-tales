import Link from "next/link";
import type { Metadata } from "next";
import { BookOpen, Star, TrendingUp, Search, ChevronLeft, Lock } from "lucide-react";
import { getNovelBySlug, getChapterList, getAllNovels, getCoverUrl } from "@/lib/novels";
import { notFound } from "next/navigation";
import ChapterListClient from "@/components/ChapterListClient";

const BASE_URL = "https://novelhub.beauty";

export function generateStaticParams() {
  return getAllNovels().map((n) => ({ slug: n.slug }));
}

export function generateMetadata({ params }: { params: { slug: string } }): Metadata {
  const novel = getNovelBySlug(params.slug);
  if (!novel) return {};

  const isFree = novel.zone === "free";
  const title = `${novel.title_en} ${isFree ? "— Read Free" : "— Read Online"} | Nexus Tales`;
  const desc = novel.description_en.slice(0, 160);

  return {
    title: novel.title_en,
    description: desc,
    keywords: [novel.title_en, novel.author_en, novel.genre, ...novel.tags, "read online", "free", "translated"],
    alternates: { canonical: `${BASE_URL}/novel/${novel.slug}` },
    openGraph: {
      title,
      description: desc,
      url: `${BASE_URL}/novel/${novel.slug}`,
      type: "book",
      images: [{ url: `${BASE_URL}/og-default.png`, width: 1200, height: 630, alt: novel.title_en }],
    },
    twitter: {
      card: "summary_large_image",
      title,
      description: desc,
      images: [`${BASE_URL}/og-default.png`],
    },
  };
}

export default function NovelDetailPage({ params }: { params: { slug: string } }) {
  const novel = getNovelBySlug(params.slug);
  
  if (!novel) {
    notFound();
  }

  const chapters = getChapterList(novel.slug);
  const coverUrl = getCoverUrl(novel.slug);

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Book",
    name: novel.title_en,
    author: { "@type": "Person", name: novel.author_en },
    description: novel.description_en.slice(0, 200),
    genre: novel.genre,
    keywords: novel.tags.join(", "),
    inLanguage: "en",
    isAccessibleForFree: novel.zone === "free",
    url: `${BASE_URL}/novel/${novel.slug}`,
    publisher: { "@type": "Organization", name: "Nexus Tales" },
    numberOfPages: chapters.length,
  };

  return (
    <div className="pt-24 pb-24">
      {/* JSON-LD Structured Data */}
      <script type="application/ld+json" dangerouslySetInnerHTML={{
        __html: JSON.stringify(jsonLd),
      }} />
      <div className="max-w-7xl mx-auto px-6">
        {/* Back */}
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-moon/50 hover:text-neon-cyan transition-colors mb-8 text-sm"
        >
          <ChevronLeft className="w-4 h-4" />
          Back to Library
        </Link>

        {/* Header */}
        <div className="grid lg:grid-cols-[280px_1fr] gap-10 mb-16">
          {/* Cover */}
          <div>
            <div className="aspect-[3/4] rounded-2xl overflow-hidden glass-card">
                <img
                  src={coverUrl}
                  alt={`Cover: ${novel.title_en}`}
                  className="w-full h-full object-cover"
                />
            </div>
            {novel.zone === "vip" && (
              <div className="mt-4 mb-2">
                <div className="flex items-center gap-2 p-3 rounded-xl bg-neon-cyan/5 border border-neon-cyan/10">
                  <Lock className="w-4 h-4 text-neon-cyan" />
                  <span className="text-xs text-neon-cyan/80">
                    First <strong>5 chapters free</strong> — Premium to unlock all
                  </span>
                </div>
              </div>
            )}
            <div className="mt-4">
              <Link
                href={`/novel/${novel.slug}/chapter/1`}
                className="block w-full neon-btn py-3 rounded-xl text-sm font-bold text-center"
              >
                ▶ {novel.zone === "vip" ? "Read Free Chapters" : "Start Reading"}
              </Link>
            </div>
          </div>

          {/* Info */}
          <div>
            <div className="flex flex-wrap items-start gap-3 mb-2">
              <span
                className={`text-xs px-3 py-1 rounded-full font-medium ${
                  novel.status === "completed"
                    ? "bg-neon-green/10 text-neon-green border border-neon-green/20"
                    : "bg-neon-cyan/10 text-neon-cyan border border-neon-cyan/20"
                }`}
              >
                {novel.status}
              </span>
              <span className="glass-card px-3 py-1 rounded-full text-xs font-bold text-neon-purple">
                {novel.genre}
              </span>
              {novel.is_adult && (
                <span className="bg-neon-pink/10 text-neon-pink text-xs px-3 py-1 rounded-full border border-neon-pink/20">
                  🔞 Adult
                </span>
              )}
            </div>

            <h1
              className="text-3xl lg:text-5xl font-bold text-stardust mb-2"
              style={{ fontFamily: "Orbitron" }}
            >
              {novel.title_en}
            </h1>
            <p className="text-moon/50 mb-6">
              by {novel.author_en}
            </p>

            {/* Stats */}
            <div className="flex flex-wrap gap-6 mb-8">
              <div className="flex items-center gap-2">
                <Star className="w-5 h-5 fill-neon-cyan text-neon-cyan" />
                <span className="text-stardust font-bold text-lg">{novel.rating}</span>
                <span className="text-moon/40 text-sm">/ 5.0</span>
              </div>
              <div className="flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-neon-purple" />
                <span className="text-stardust font-bold">{(novel.available_chapters || novel.total_chapters).toLocaleString()}</span>
                <span className="text-moon/40 text-sm">chapters</span>
              </div>
              <div className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-neon-pink" />
                <span className="text-stardust font-bold">{(novel.readers / 1000).toFixed(0)}K</span>
                <span className="text-moon/40 text-sm">readers</span>
              </div>
            </div>

            {/* Tags */}
            <div className="flex flex-wrap gap-2 mb-6">
              {novel.tags.map((tag) => (
                <span
                  key={tag}
                  className="text-xs px-3 py-1.5 rounded-full bg-white/5 text-moon/70 border border-white/10"
                >
                  {tag}
                </span>
              ))}
            </div>

            {/* Description */}
            <div className="glass-card rounded-2xl p-6">
              <h3 className="text-lg font-bold text-stardust mb-3">Synopsis</h3>
              <p className="text-moon/60 leading-relaxed">
                {novel.description_en}
              </p>
            </div>
          </div>
        </div>

        {/* Chapters */}
        <section>
          <div className="flex items-center justify-between mb-8">
            <h2
              className="text-2xl font-bold text-stardust"
              style={{ fontFamily: "Orbitron" }}
            >
              <span className="text-gradient">Chapters</span>
            </h2>
            <div className="text-sm text-moon/40">
              Showing {chapters.length} of {(novel.available_chapters || novel.total_chapters).toLocaleString()} chapters
            </div>
          </div>

          <ChapterListClient
            slug={novel.slug}
            zone={novel.zone}
            chapters={chapters}
          />
        </section>
      </div>
    </div>
  );
}