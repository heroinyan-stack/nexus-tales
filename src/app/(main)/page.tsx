"use client";

import { useState, useEffect, useMemo } from "react";
import Link from "next/link";
import {
  BookOpen,
  Search,
  Star,
  TrendingUp,
  Crown,
  Sparkles,
  X,
  Library,
  Flame,
  Clock,
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
}

interface Genre {
  name: string;
  count: number;
  is_adult: boolean;
}

export default function HomePage() {
  const [novels, setNovels] = useState<Novel[]>([]);
  const [genres, setGenres] = useState<Genre[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedGenre, setSelectedGenre] = useState("all");
  const [sortBy, setSortBy] = useState<"rating" | "readers" | "newest">("rating");
  const [showAdult, setShowAdult] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const res = await fetch("/api/novels");
        const data = await res.json();
        setNovels(data.novels || data);
        setGenres(data.genres || []);
      } catch (e) {
        console.error("Failed to fetch novels:", e);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const genreLabels: Record<string, string> = {
    all: "All",
    "free-classics": "📜 Classics",
    classic: "📜 Classics",
    xianxia: "Xianxia",
    xuanhuan: "Xuanhuan",
    fantasy: "Fantasy",
    scifi: "Sci-Fi",
    romance: "Romance",
    history: "History",
    wuxia: "Wuxia",
    urban: "Urban",
    erotica: "Adult 🔞",
  };

  const freeBooks = useMemo(() => novels.filter((n) => n.zone === "free"), [novels]);
  const vipBooks = useMemo(() => novels.filter((n) => n.zone === "vip"), [novels]);

  // Sort helpers
  const hottestBooks = useMemo(() =>
    [...vipBooks].filter(n => !n.is_adult).sort((a, b) => b.readers - a.readers).slice(0, 8),
    [vipBooks]
  );
  const newestBooks = useMemo(() =>
    [...vipBooks].filter(n => !n.is_adult).sort((a, b) => b.id - a.id).slice(0, 8),
    [vipBooks]
  );
  const topRatedBooks = useMemo(() =>
    [...vipBooks].filter(n => !n.is_adult).sort((a, b) => b.rating - a.rating || b.readers - a.readers).slice(0, 8),
    [vipBooks]
  );

  const filteredNovels = useMemo(() => {
    // Search across ALL novels (free + VIP)
    let allBooks = [...vipBooks, ...freeBooks];
    let result = searchQuery ? allBooks : [...vipBooks];

    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      result = result.filter(
        (n) =>
          n.title_en.toLowerCase().includes(q) ||
          n.author_en.toLowerCase().includes(q) ||
          n.tags?.some((t: string) => t.toLowerCase().includes(q))
      );
      if (result.length === 0) {
        // Fallback: fuzzy search on description
        result = allBooks.filter(
          (n) =>
            n.description_en?.toLowerCase().includes(q) ||
            n.title_en.toLowerCase().includes(q)
        );
      }
    }

    if (selectedGenre !== "all") {
      result = result.filter((n) => n.genre === selectedGenre);
    }

    if (!showAdult) {
      result = result.filter((n) => !n.is_adult);
    }

    switch (sortBy) {
      case "rating":
        result.sort((a, b) => b.rating - a.rating);
        break;
      case "readers":
        result.sort((a, b) => b.readers - a.readers);
        break;
      case "newest":
        result.sort((a, b) => b.id - a.id);
        break;
    }

    return result;
  }, [vipBooks, searchQuery, selectedGenre, sortBy, showAdult]);

  if (loading) {
    return (
      <div className="pt-32 pb-24 text-center">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-neon-cyan"></div>
        <p className="mt-4 text-moon/50">Loading novels...</p>
      </div>
    );
  }

  return (
    <div className="pt-24 pb-24">
      <div className="max-w-7xl mx-auto px-6">
        {/* ========== HERO ========== */}
        <div className="text-center mb-14">
          <h1
            className="text-3xl lg:text-5xl font-bold mb-3"
            style={{ fontFamily: "Orbitron" }}
          >
            <span className="text-gradient">NEXUS</span>{" "}
            <span className="text-stardust">TALES</span>
          </h1>
          <p className="text-moon/50 text-lg max-w-xl mx-auto">
            Chinese web novels &mdash; translated for English readers
          </p>
          <p className="text-moon/30 text-sm mt-2">
            {novels.length} novels &middot; Free classics + Premium translations
          </p>
        </div>

        {/* ========== 🔥 TRENDING NOW (Hottest by readers) ========== */}
        <section className="mb-14">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 rounded-xl bg-red-500/10 border border-red-500/20">
              <Flame className="w-5 h-5 text-red-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-stardust" style={{ fontFamily: "Orbitron" }}>
                Trending Now
              </h2>
              <p className="text-moon/40 text-sm">Most read stories this week</p>
            </div>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {hottestBooks.map((novel) => (
              <NovelCard key={novel.slug} novel={novel} />
            ))}
          </div>
        </section>

        {/* ========== ⭐ TOP RATED ========== */}
        <section className="mb-14">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 rounded-xl bg-neon-cyan/10 border border-neon-cyan/20">
              <Star className="w-5 h-5 text-neon-cyan" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-stardust" style={{ fontFamily: "Orbitron" }}>
                Top Rated
              </h2>
              <p className="text-moon/40 text-sm">Highest rated by our readers</p>
            </div>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {topRatedBooks.map((novel) => (
              <NovelCard key={novel.slug} novel={novel} />
            ))}
          </div>
        </section>

        {/* ========== 🆕 NEWEST ADDITIONS ========== */}
        <section className="mb-14">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 rounded-xl bg-neon-purple/10 border border-neon-purple/20">
              <Clock className="w-5 h-5 text-neon-purple" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-stardust" style={{ fontFamily: "Orbitron" }}>
                Newest Additions
              </h2>
              <p className="text-moon/40 text-sm">Freshly translated chapters</p>
            </div>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {newestBooks.map((novel) => (
              <NovelCard key={novel.slug} novel={novel} />
            ))}
          </div>
        </section>

        {/* ========== 📚 FREE ZONE (Classics — in the middle) ========== */}
        <section className="mb-14">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 rounded-xl bg-amber-500/10 border border-amber-500/20">
              <Library className="w-5 h-5 text-amber-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-stardust" style={{ fontFamily: "Orbitron" }}>
                Free Zone
              </h2>
              <p className="text-moon/40 text-sm">
                Timeless Chinese classics &mdash; completely free, forever
              </p>
            </div>
            <Link
              href="/novels?zone=free"
              className="ml-auto text-sm text-amber-400 hover:text-amber-300 transition-colors flex items-center gap-1"
            >
              View all {freeBooks.length} <span className="text-xs">→</span>
            </Link>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6 gap-4">
            {freeBooks.slice(0, 6).map((novel) => (
              <NovelCard key={novel.slug} novel={novel} isFree />
            ))}
          </div>
        </section>

        {/* ========== 👑 ALL VIP NOVELS ========== */}
        <section>
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 rounded-xl bg-neon-purple/10 border border-neon-purple/20">
              <Crown className="w-5 h-5 text-neon-purple" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-stardust" style={{ fontFamily: "Orbitron" }}>
                All Premium Novels
              </h2>
              <p className="text-moon/40 text-sm">
                First 20 chapters free &middot; Subscribe for full access
              </p>
            </div>
          </div>

          {/* Search + Filters */}
          <div className="glass-card rounded-2xl p-4 mb-8">
            <div className="flex flex-col lg:flex-row gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-moon/30" />
                <input
                  type="text"
                  placeholder="Search web novels..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full bg-transparent border border-white/10 rounded-xl pl-12 pr-4 py-3 text-stardust placeholder:text-moon/30 focus:outline-none focus:border-neon-cyan/50 transition-all"
                />
                {searchQuery && (
                  <button onClick={() => setSearchQuery("")} className="absolute right-4 top-1/2 -translate-y-1/2">
                    <X className="w-4 h-4 text-moon/30 hover:text-moon" />
                  </button>
                )}
              </div>

              <div className="flex gap-2 overflow-x-auto pb-1">
                {genres
                  .filter((g) => !g.is_adult && g.name !== "free-classics" && g.name !== "classic")
                  .map((g) => (
                    <button
                      key={g.name}
                      onClick={() => setSelectedGenre(g.name === selectedGenre ? "all" : g.name)}
                      className={`text-xs md:text-sm px-4 py-2 rounded-full border transition-all whitespace-nowrap ${
                        selectedGenre === g.name
                          ? "bg-neon-cyan/10 border-neon-cyan/50 text-neon-cyan"
                          : "bg-white/5 border-white/5 text-moon/50 hover:text-moon hover:border-white/20"
                      }`}
                    >
                      {genreLabels[g.name] || g.name} ({g.count})
                    </button>
                  ))}
              </div>

              <div className="flex gap-2">
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as any)}
                  className="bg-white/5 border border-white/10 rounded-xl px-3 py-2 text-sm text-moon focus:outline-none focus:border-neon-cyan/50"
                >
                  <option value="rating">⭐ Rating</option>
                  <option value="readers">👥 Popular</option>
                  <option value="newest">🆕 Newest</option>
                </select>
              </div>
            </div>
          </div>

          {/* Novel Grid */}
          {filteredNovels.length > 0 ? (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {filteredNovels.map((novel) => (
                <NovelCard key={novel.slug} novel={novel} />
              ))}
            </div>
          ) : (
            <div className="text-center py-16">
              <p className="text-moon/30 text-lg">No novels found for "{searchQuery}"</p>
              <p className="text-moon/20 text-sm mt-2">Try a different keyword or browse all novels below</p>
            </div>
          )}

          <div className="text-center mt-10 text-moon/30 text-sm">
            {filteredNovels.length} novels{searchQuery ? ' found' : ' in VIP Zone'} &middot; First 20 chapters free, subscribe for full access
          </div>
        </section>
      </div>
    </div>
  );
}

/* ── Reusable Novel Card ──────────────────────────────── */
function NovelCard({ novel, isFree = false }: { novel: Novel; isFree?: boolean }) {
  const ext = novel.cover_ext || "jpg";
  return (
    <Link
      href={`/novel/${novel.slug}`}
      className="block group"
    >
      <div className={`glass-card rounded-2xl overflow-hidden h-full transition-all duration-300 ${
        isFree
          ? "border-amber-500/10 hover:border-amber-500/30"
          : "hover:border-neon-cyan/30"
      }`}>
        <div className="relative h-44 overflow-hidden bg-cosmic">
          <img
            src={`/covers/${novel.slug}.${ext}`}
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
          <h3 className={`font-bold group-hover:text-neon-cyan transition-colors line-clamp-1 text-sm mb-1 ${
            isFree ? "text-stardust group-hover:text-amber-400" : "text-stardust"
          }`}>
            {novel.title_en}
          </h3>
          <p className="text-moon/40 text-xs mb-2">{novel.author_en}</p>
          <div className="flex items-center gap-3 text-xs text-moon/30">
            <span className="flex items-center gap-1">
              <Star className="w-3 h-3 fill-amber-400 text-amber-400" /> {novel.rating}
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
