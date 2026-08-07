import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import fs from "fs";
import path from "path";
import { BookOpen, PenLine, Layers } from "lucide-react";

const NOVELS_FILE = path.join(process.cwd(), "data", "novels.json");

export function generateStaticParams() {
  if (!fs.existsSync(NOVELS_FILE)) return [];
  const novels = JSON.parse(fs.readFileSync(NOVELS_FILE, "utf-8"));
  const authors = new Map<string, any>();
  for (const n of novels) {
    const a = n.author_en || n.author_zh;
    if (a && !authors.has(a)) authors.set(a, true);
  }
  return Array.from(authors.keys()).map((a) => ({ slug: encodeURIComponent(a) }));
}

export async function generateMetadata({ params }: { params: { slug: string } }): Promise<Metadata> {
  const author = decodeURIComponent(params.slug);
  return {
    title: `${author} — Author Profile | Nexus Tales`,
    description: `Explore ${author}'s translated Chinese web novels on Nexus Tales. Browse their complete works, genres, and read free chapters online.`,
  };
}

export default function AuthorPage({ params }: { params: { slug: string } }) {
  const authorName = decodeURIComponent(params.slug);
  if (!fs.existsSync(NOVELS_FILE)) notFound();

  const novels = JSON.parse(fs.readFileSync(NOVELS_FILE, "utf-8"));
  const works = novels.filter((n: any) => (n.author_en || n.author_zh) === authorName);

  if (works.length === 0) notFound();

  // Editorial bio generated from data
  const genres = Array.from(new Set(works.map((w: any) => w.genre).filter(Boolean)));
  const totalChapters = works.reduce((s: number, w: any) => s + (w.total_chapters || 0), 0);
  const completed = works.filter((w: any) => w.status === "completed").length;

  return (
    <div className="pt-28 pb-24">
      <div className="max-w-4xl mx-auto px-6">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-neon-purple/10 border border-neon-purple/20 text-neon-purple text-sm mb-4">
            <PenLine className="w-4 h-4" /> Author Profile
          </div>
          <h1 className="text-3xl lg:text-4xl font-bold text-stardust mb-3" style={{ fontFamily: "Orbitron" }}>
            {authorName}
          </h1>
          <p className="text-moon/50">
            {works.length} work{works.length > 1 ? "s" : ""} · {totalChapters.toLocaleString()} chapters · {genres.length} genre{genres.length > 1 ? "s" : ""}
          </p>
        </div>

        {/* Bio card */}
        <div className="glass-card rounded-2xl p-8 mb-10">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-neon-purple/10 border border-neon-purple/20 flex items-center justify-center shrink-0">
              <Layers className="w-6 h-6 text-neon-purple" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-stardust mb-2">About the Author</h2>
              <p className="text-moon/60 leading-relaxed">
                {authorName} is a Chinese web novel author whose work spans {genres.slice(0, 3).join(", ")}
                {genres.length > 3 ? ", and more" : ""}. On Nexus Tales we host {works.length} of their
                {works.length > 1 ? " titles" : " title"}, comprising roughly {totalChapters.toLocaleString()} translated
                chapters. {completed > 0 ? `${completed} of these ${completed > 1 ? "works are" : "work is"} fully translated and complete.` : "Their ongoing series are updated with new chapters regularly."}
              </p>
              {genres.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-4">
                  {genres.map((g: any) => (
                    <span key={g} className="text-xs px-3 py-1 rounded-full bg-white/5 border border-white/10 text-moon/60">
                      {g}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Works */}
        <h2 className="text-xl font-bold text-stardust mb-6 flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-neon-cyan" /> Complete Works
        </h2>
        <div className="grid sm:grid-cols-2 gap-4">
          {works.map((w: any) => (
            <Link
              key={w.slug}
              href={`/novel/${w.slug}`}
              className="glass-card rounded-xl p-5 hover:border-neon-cyan/30 transition-all"
            >
              <h3 className="font-semibold text-stardust mb-1">{w.title_en || w.title_zh}</h3>
              <p className="text-sm text-moon/50 line-clamp-2">
                {(w.description_en || "").slice(0, 90)}...
              </p>
              <div className="flex justify-between items-center mt-3 text-xs text-moon/40">
                <span className="capitalize">{w.genre}</span>
                <span>{w.total_chapters || 0} ch</span>
              </div>
            </Link>
          ))}
        </div>

        <div className="text-center mt-12">
          <Link href="/novels" className="text-neon-cyan hover:underline text-sm">
            ← Back to all novels
          </Link>
        </div>
      </div>
    </div>
  );
}
