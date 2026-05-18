import Link from "next/link";
import { BookOpen, Star, TrendingUp, Search, ChevronLeft } from "lucide-react";
import { getNovelBySlug, getChapterList, getAllNovels } from "@/lib/novels";
import { notFound } from "next/navigation";

export function generateStaticParams() {
  return getAllNovels().map((n) => ({ slug: n.slug }));
}

export default function NovelDetailPage({ params }: { params: { slug: string } }) {
  const novel = getNovelBySlug(params.slug);
  
  if (!novel) {
    notFound();
  }

  const chapters = getChapterList(novel.slug);

  return (
    <div className="pt-24 pb-24">
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
              <div className="w-full h-full bg-gradient-to-br from-neon-cyan/30 via-neon-purple/20 to-cosmic flex items-center justify-center">
                <BookOpen className="w-16 h-16 text-white/10" />
              </div>
            </div>
            <div className="mt-4">
              <Link
                href={`/novel/${novel.slug}/chapter/1`}
                className="block w-full neon-btn py-3 rounded-xl text-sm font-bold text-center"
              >
                ▶ Start Reading
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
            {novel.title_zh !== novel.title_en && (
              <p className="text-moon/30 text-lg mb-1">{novel.title_zh}</p>
            )}
            <p className="text-moon/50 mb-6">
              by {novel.author_en || novel.author_zh}
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
                <span className="text-stardust font-bold">{novel.total_chapters.toLocaleString()}</span>
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
                {novel.description_en || novel.description_zh}
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
              Showing {chapters.length} of {novel.total_chapters.toLocaleString()} chapters
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {chapters.map((ch) => (
              <Link
                key={ch.num}
                href={`/novel/${novel.slug}/chapter/${ch.num}`}
                className="flex items-center justify-between p-4 rounded-xl glass-card hover:border-neon-cyan/30 transition-all group"
              >
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-stardust group-hover:text-neon-cyan transition-colors">
                    Ch. {ch.num}
                  </div>
                  <div className="text-xs text-moon/40 mt-0.5 truncate">
                    {ch.title_en || ch.title_zh}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}