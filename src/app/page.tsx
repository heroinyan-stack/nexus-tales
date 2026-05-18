"use client";

import { useState, useEffect, useMemo } from "react";
import Link from "next/link";
import {
  BookOpen,
  Search,
  Star,
  TrendingUp,
  Clock,
  Filter,
  X,
} from "lucide-react";

interface Novel {
  id: number;
  slug: string;
  title_zh: string;
  title_en: string;
  author_zh: string;
  author_en: string;
  genre: string;
  tags: string[];
  is_adult: boolean;
  status: string;
  rating: number;
  total_chapters: number;
  readers: number;
  description_zh: string;
  description_en: string;
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
    xianxia: "Xianxia",
    xuanhuan: "Xuanhuan",
    fantasy: "Fantasy",
    scifi: "Sci-Fi",
    romance: "Romance",
    history: "History",
    wuxia: "Wuxia",
    urban: "Urban",
    erotica: "Adult 🔞",
    smut: "Smut 🔞",
  };

  const filteredNovels = useMemo(() => {
    let result = [...novels];

    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      result = result.filter(
        (n) =>
          n.title_en.toLowerCase().includes(q) ||
          n.title_zh.toLowerCase().includes(q) ||
          n.author_en.toLowerCase().includes(q) ||
          n.author_zh.toLowerCase().includes(q) ||
          n.tags.some((t) => t.toLowerCase().includes(q))
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
  }, [novels, searchQuery, selectedGenre, sortBy, showAdult]);

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
        {/* Top banner */}
        <div className="text-center mb-12">
          <h1
            className="text-3xl lg:text-5xl font-bold mb-3"
            style={{ fontFamily: "Orbitron" }}
          >
            <span className="text-gradient">NEXUS</span>{" "}
            <span className="text-stardust">TALES</span>
          </h1>
          <p className="text-moon/50 text-lg max-w-xl mx-auto">
            Premium translations of the best Chinese web novels
          </p>
        </div>

        {/* Search + Filters */}
        <div className="glass-card rounded-2xl p-4 mb-10">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-moon/30" />
              <input
                type="text"
                placeholder="Search novels, authors, tags..."
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

            {/* Genre filter */}
            <div className="flex gap-2 overflow-x-auto pb-1">
              <button
                onClick={() => setSelectedGenre("all")}
                className={`text-xs md:text-sm px-4 py-2 rounded-full border transition-all whitespace-nowrap ${
                  selectedGenre === "all"
                    ? "bg-neon-cyan/10 border-neon-cyan/50 text-neon-cyan"
                    : "bg-white/5 border-white/5 text-moon/50 hover:text-moon hover:border-white/20"
                }`}
              >
                All
              </button>
              {genres.map((g) => (
                <button
                  key={g.name}
                  onClick={() => setSelectedGenre(g.name)}
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

            {/* Sort + Adult toggle */}
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
              <button
                onClick={() => setShowAdult(!showAdult)}
                className={`text-sm px-3 py-2 rounded-xl border transition-all ${
                  showAdult
                    ? "bg-neon-pink/10 border-neon-pink/50 text-neon-pink"
                    : "bg-white/5 border-white/5 text-moon/30"
                }`}
              >
                🔞
              </button>
            </div>
          </div>
        </div>

        {/* Novel Grid */}
        {filteredNovels.length === 0 ? (
          <div className="text-center py-20">
            <BookOpen className="w-16 h-16 text-moon/10 mx-auto mb-4" />
            <p className="text-moon/30 text-lg">No novels found. Try different filters.</p>
          </div>
        ) : (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredNovels.map((novel) => (
              <Link
                key={novel.id}
                href={`/novel/${novel.slug}`}
                className="block group"
              >
                <div className="glass-card rounded-2xl overflow-hidden h-full hover:border-neon-cyan/30 transition-all duration-300">
                  {/* Cover area */}
                  <div className="relative h-44 overflow-hidden bg-cosmic">
                    <div className="absolute inset-0 bg-gradient-to-br from-neon-cyan/20 via-neon-purple/10 to-cosmic" />
                    <div className="absolute inset-0 flex items-center justify-center">
                      <BookOpen className="w-10 h-10 text-white/10" />
                    </div>
                    <div className="absolute top-3 left-3">
                      <span
                        className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                          novel.status === "completed"
                            ? "bg-neon-green/20 text-neon-green border border-neon-green/30"
                            : "bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/30"
                        }`}
                      >
                        {novel.status === "completed" ? "✓ Complete" : "⟳ Ongoing"}
                      </span>
                    </div>
                    {novel.is_adult && (
                      <div className="absolute top-3 right-3 bg-neon-pink/20 text-neon-pink text-xs px-2 py-1 rounded-full border border-neon-pink/30">
                        🔞
                      </div>
                    )}
                  </div>

                  <div className="p-5">
                    <div className="flex items-start justify-between gap-2 mb-1">
                      <h3 className="font-bold text-stardust group-hover:text-neon-cyan transition-colors line-clamp-1 text-lg">
                        {novel.title_en || novel.title_zh}
                      </h3>
                    </div>
                    <p className="text-moon/40 text-sm mb-3">
                      {novel.author_en || novel.author_zh}
                    </p>

                    <div className="flex items-center justify-between text-sm mb-3">
                      <span className="flex items-center gap-1 text-neon-cyan font-medium">
                        <Star className="w-3.5 h-3.5 fill-neon-cyan" />
                        {novel.rating}
                      </span>
                      <span className="flex items-center gap-1 text-moon/30">
                        <BookOpen className="w-3.5 h-3.5" />
                        {novel.total_chapters.toLocaleString()}
                      </span>
                      <span className="flex items-center gap-1 text-moon/30">
                        <TrendingUp className="w-3.5 h-3.5" />
                        {(novel.readers / 1000).toFixed(0)}K
                      </span>
                    </div>

                    <p className="text-moon/50 text-sm leading-relaxed line-clamp-2">
                      {novel.description_en || novel.description_zh}
                    </p>

                    <div className="flex flex-wrap gap-1.5 mt-3">
                      {novel.tags.slice(0, 3).map((tag) => (
                        <span
                          key={tag}
                          className="text-xs px-2 py-0.5 rounded-full bg-white/5 text-moon/40 border border-white/5"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}

        <div className="text-center mt-10 text-moon/30 text-sm">
          Showing {filteredNovels.length} of {novels.length} novels
        </div>
      </div>
    </div>
  );
}
