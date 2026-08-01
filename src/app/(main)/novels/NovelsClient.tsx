"use client";

import { useState, useMemo } from "react";
import Link from "next/link";
import {
  Search,
  Star,
  X,
  Library,
} from "lucide-react";

interface Novel {
  id: number;
  slug: string;
  title_en: string;
  author_en: string;
  genre: string;
  tags: string[];
  is_adult: boolean;
  status: string;
  rating: number;
  total_chapters: number;
  readers: number;
  description_en: string;
  zone: string;
  cover_ext?: string;
  cover_url?: string;
  available_chapters?: number;
}

interface Genre {
  name: string;
  count: number;
  is_adult: boolean;
}

const GENRE_LABELS: Record<string, string> = {
  xianxia: "Xianxia",
  xuanhuan: "Xuanhuan",
  fantasy: "Fantasy",
  scifi: "Sci-Fi",
  romance: "Romance",
  history: "History",
  wuxia: "Wuxia",
  urban: "Urban",
  classic: "Classics",
  erotica: "Adult 🔞",
};

export default function NovelsClient({
  novels,
  genres,
}: {
  novels: Novel[];
  genres: Genre[];
}) {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedGenre, setSelectedGenre] = useState("all");
  const [sortBy, setSortBy] = useState<"rating" | "readers" | "newest">("readers");
  const [showAdult, setShowAdult] = useState(false);

  const vipNovels = useMemo(
    () => novels.filter((n) => n.zone !== "free"),
    [novels]
  );
  const freeNovels = useMemo(
    () => novels.filter((n) => n.zone === "free"),
    [novels]
  );

  const filtered = useMemo(() => {
    let result = searchQuery ? novels : [...vipNovels];

    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      result = novels.filter(
        (n) =>
          n.title_en.toLowerCase().includes(q) ||
          n.author_en.toLowerCase().includes(q) ||
          n.tags?.some((t) => t.toLowerCase().includes(q))
      );
    }

    if (selectedGenre !== "all") {
      result = result.filter((n) => n.genre === selectedGenre);
    }

    if (!showAdult) {
      result = result.filter((n) => !n.is_adult);
    }

    switch (sortBy) {
      case "rating":
        result.sort((a, b) => b.rating - a.rating || b.readers - a.readers);
        break;
      case "readers":
        result.sort((a, b) => b.readers - a.readers);
        break;
      case "newest":
        result.sort((a, b) => b.id - a.id);
        break;
    }

    return result;
  }, [novels, vipNovels, searchQuery, selectedGenre, sortBy, showAdult]);

  return (
    <div className="pt-24 pb-24">
      <div className="max-w-7xl mx-auto px-6">
        {/* Header */}
        <div className="text-center mb-10">
          <h1
            className="text-3xl lg:text-5xl font-bold mb-3"
            style={{ fontFamily: "Orbitron" }}
          >
            <span className="text-gradient">Browse</span>{" "}
            <span className="text-stardust">All Novels</span>
          </h1>
          <p className="text-moon/50 text-lg max-w-xl mx-auto">
            {novels.length} translated cultivation & fantasy novels
          </p>
        </div>

        {/* Search + Filters */}
        <div className="glass-card rounded-2xl p-4 mb-8">
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-moon/30" />
              <input
                type="text"
                placeholder="Search by title, author, or tags..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-transparent border border-white/10 rounded-xl pl-12 pr-4 py-3 text-stardust placeholder:text-moon/30 focus:outline-none focus:border-neon-cyan/50 transition-all"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery("")}
                  className="absolute right-4 top-1/2 -translate-y-1/2"
                >
                  <X className="w-4 h-4 text-moon/30 hover:text-moon" />
                </button>
              )}
            </div>

            <div className="flex gap-2 overflow-x-auto pb-1">
              {genres
                .filter((g) => !g.is_adult)
                .map((g) => (
                  <button
                    key={g.name}
                    onClick={() =>
                      setSelectedGenre(g.name === selectedGenre ? "all" : g.name)
                    }
                    className={`text-xs md:text-sm px-4 py-2 rounded-full border transition-all whitespace-nowrap ${
                      selectedGenre === g.name
                        ? "bg-neon-cyan/10 border-neon-cyan/50 text-neon-cyan"
                        : "bg-white/5 border-white/5 text-moon/50 hover:text-moon hover:border-white/20"
                    }`}
                  >
                    {GENRE_LABELS[g.name] || g.name} ({g.count})
                  </button>
                ))}
            </div>

            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="bg-white/5 border border-white/10 rounded-xl px-3 py-2 text-sm text-moon focus:outline-none focus:border-neon-cyan/50"
            >
              <option value="readers">👥 Popular</option>
              <option value="rating">⭐ Rating</option>
              <option value="newest">🆕 Newest</option>
            </select>
          </div>
        </div>

        {/* Free Classics */}
        {freeNovels.length > 0 && !searchQuery && selectedGenre === "all" && (
          <section className="mb-10">
            <div className="flex items-center gap-3 mb-5">
              <div className="p-2 rounded-xl bg-amber-500/10 border border-amber-500/20">
                <Library className="w-5 h-5 text-amber-400" />
              </div>
              <h2 className="text-lg font-bold text-stardust">
                Free Classics ({freeNovels.length})
              </h2>
            </div>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
              {freeNovels.map((novel) => (
                <NovelCard key={novel.slug} novel={novel} isFree />
              ))}
            </div>
          </section>
        )}

        {/* All Novels */}
        <section>
          {!searchQuery && selectedGenre === "all" && freeNovels.length > 0 && (
            <div className="flex items-center gap-3 mb-5">
              <h2 className="text-lg font-bold text-stardust">
                Premium Novels ({vipNovels.length})
              </h2>
            </div>
          )}

          {filtered.length > 0 ? (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
              {filtered.map((novel) => (
                <NovelCard key={novel.slug} novel={novel} />
              ))}
            </div>
          ) : (
            <div className="text-center py-16">
              <p className="text-moon/30 text-lg">
                No novels match your search
              </p>
              <p className="text-moon/20 text-sm mt-2">
                Try different keywords or clear filters
              </p>
            </div>
          )}

          <div className="text-center mt-10 text-moon/30 text-sm">
            {filtered.length} novels displayed
            {selectedGenre !== "all" && <> &middot; {selectedGenre}</>}
            {searchQuery && <> &middot; matching &quot;{searchQuery}&quot;</>}
          </div>
        </section>
      </div>
    </div>
  );
}

/* ── Novel Card ──────────────────────────────────── */
function NovelCard({ novel, isFree = false }: { novel: Novel; isFree?: boolean }) {
  // cover_ext already includes leading dot (e.g., ".svg")
  const ext = (novel as any).cover_ext || ".svg";
  const coverSrc =
    (novel as any).cover_url ||
    `/covers/${novel.slug}${ext}`;
  return (
    <Link href={`/novel/${novel.slug}`} className="block group">
      <div
        className={`glass-card rounded-2xl overflow-hidden h-full transition-all duration-300 ${
          isFree
            ? "border-amber-500/10 hover:border-amber-500/30"
            : "hover:border-neon-cyan/30"
        }`}
      >
        <div className="relative h-44 overflow-hidden bg-cosmic">
          <img
            src={coverSrc}
            alt={`Cover: ${novel.title_en}`}
            className="w-full h-full object-cover"
            loading="lazy"
          />
          {isFree && (
            <div className="absolute top-2 left-2">
              <span className="text-xs px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30 font-medium">
                FREE
              </span>
            </div>
          )}
          <div className="absolute top-2 right-2">
            <span
              className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                novel.status === "completed"
                  ? "bg-neon-green/20 text-neon-green border border-neon-green/30"
                  : "bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/30"
              }`}
            >
              {novel.status === "completed" ? "✓ Done" : "⟳ Ongoing"}
            </span>
          </div>
        </div>

        <div className="p-4">
          <h3
            className={`font-bold group-hover:text-neon-cyan transition-colors line-clamp-1 text-sm mb-1 ${
              isFree
                ? "text-stardust group-hover:text-amber-400"
                : "text-stardust"
            }`}
          >
            {novel.title_en}
          </h3>
          <p className="text-moon/40 text-xs mb-2">{novel.author_en}</p>
          <div className="flex items-center gap-3 text-xs text-moon/30">
            <span className="flex items-center gap-1">
              <Star className="w-3 h-3 fill-amber-400 text-amber-400" />{" "}
              {novel.rating}
            </span>
            <span>{novel.total_chapters} ch</span>
            {novel.readers > 0 && (
              <span>{(novel.readers / 1000).toFixed(0)}K</span>
            )}
          </div>
        </div>
      </div>
    </Link>
  );
}
