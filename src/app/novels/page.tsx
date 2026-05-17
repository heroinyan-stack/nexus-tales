"use client";

import { motion } from "framer-motion";
import { useState } from "react";
import Link from "next/link";
import { Search, Star, BookOpen, Filter, X } from "lucide-react";

const GENRES = [
  "All",
  "Cultivation",
  "Fantasy",
  "Xianxia",
  "Xuanhuan",
  "Wuxia",
  "Sci-Fi",
  "Romance",
  "Dark Fantasy",
];

const NOVELS = [
  {
    slug: "martial-god-asura",
    title: "Martial God Asura",
    author: "Kindhearted Bee",
    genre: "Cultivation",
    rating: 4.8,
    chapters: 5842,
    status: "Ongoing",
    readers: "1.2M",
    description:
      "In a world where the strong prey on the weak, one young man defies the heavens.",
    tags: ["Xianxia", "Action", "Romance"],
  },
  {
    slug: "against-the-gods",
    title: "Against the Gods",
    author: "Mars Gravity",
    genre: "Fantasy",
    rating: 4.9,
    chapters: 2014,
    status: "Ongoing",
    readers: "980K",
    description: "A boy cursed with crippled meridians obtains a mysterious pearl.",
    tags: ["Xuanhuan", "Harem", "Revenge"],
  },
  {
    slug: "i-shall-seal-the-heavens",
    title: "I Shall Seal the Heavens",
    author: "Er Gen",
    genre: "Cultivation",
    rating: 4.9,
    chapters: 1614,
    status: "Completed",
    readers: "850K",
    description: "A failed scholar is kidnapped into the world of cultivation.",
    tags: ["Xianxia", "Comedy", "Tragedy"],
  },
  {
    slug: "reverend-insanity",
    title: "Reverend Insanity",
    author: "Gu Zhen Ren",
    genre: "Dark Fantasy",
    rating: 4.7,
    chapters: 2334,
    status: "Ongoing",
    readers: "720K",
    description: "A demon lord travels 500 years back in time to achieve eternal life.",
    tags: ["Xianxia", "Dark", "Anti-Hero"],
  },
  {
    slug: "a-will-eternal",
    title: "A Will Eternal",
    author: "Er Gen",
    genre: "Cultivation",
    rating: 4.8,
    chapters: 1314,
    status: "Completed",
    readers: "690K",
    description: "A cowardly youth pursues eternal life, one hilarious step at a time.",
    tags: ["Xianxia", "Comedy"],
  },
  {
    slug: "tales-of-demons-and-gods",
    title: "Tales of Demons and Gods",
    author: "Mad Snail",
    genre: "Fantasy",
    rating: 4.6,
    chapters: 496,
    status: "Ongoing",
    readers: "550K",
    description: "A powerful demon spiritualist returns to his 13-year-old self.",
    tags: ["Xuanhuan", "Rebirth"],
  },
  {
    slug: "coiling-dragon",
    title: "Coiling Dragon",
    author: "I Eat Tomatoes",
    genre: "Fantasy",
    rating: 4.9,
    chapters: 806,
    status: "Completed",
    readers: "1.1M",
    description: "Linley's journey from a noble child to a sovereign of the universe.",
    tags: ["Xuanhuan", "Magic", "War"],
  },
  {
    slug: "desolate-era",
    title: "Desolate Era",
    author: "I Eat Tomatoes",
    genre: "Cultivation",
    rating: 4.8,
    chapters: 1450,
    status: "Completed",
    readers: "780K",
    description: "Ji Ning's path through the Three Realms from mortal to supreme being.",
    tags: ["Xianxia", "Reincarnation"],
  },
  {
    slug: "wu-dong-qian-kun",
    title: "Wu Dong Qian Kun",
    author: "Heavenly Silkworm Potato",
    genre: "Cultivation",
    rating: 4.5,
    chapters: 1306,
    status: "Completed",
    readers: "620K",
    description: "A young man from a fallen clan rises through sheer determination.",
    tags: ["Xianxia", "Action"],
  },
  {
    slug: "library-of-heavens-path",
    title: "Library of Heaven's Path",
    author: "Heng Sao Tian Ya",
    genre: "Fantasy",
    rating: 4.7,
    chapters: 2252,
    status: "Completed",
    readers: "580K",
    description: "A teacher transmigrates and gains the ability to see the flaws in everything.",
    tags: ["Xuanhuan", "Comedy", "Teacher"],
  },
  {
    slug: "supreme-magus",
    title: "Supreme Magus",
    author: "Legion20",
    genre: "Dark Fantasy",
    rating: 4.6,
    chapters: 3200,
    status: "Ongoing",
    readers: "460K",
    description: "A man reincarnates into a world of magic as a hybrid monster.",
    tags: ["Fantasy", "Dark", "Magic"],
  },
  {
    slug: "shadow-slave",
    title: "Shadow Slave",
    author: "Guiltythree",
    genre: "Dark Fantasy",
    rating: 4.8,
    chapters: 2100,
    status: "Ongoing",
    readers: "900K",
    description: "In a world of nightmares, Sunny must outsmart fate with a divine shadow.",
    tags: ["Fantasy", "Dark", "Survival"],
  },
];

export default function NovelsPage() {
  const [search, setSearch] = useState("");
  const [activeGenre, setActiveGenre] = useState("All");
  const [sortBy, setSortBy] = useState("rating");

  const filtered = NOVELS.filter((n) => {
    const matchesSearch =
      n.title.toLowerCase().includes(search.toLowerCase()) ||
      n.author.toLowerCase().includes(search.toLowerCase());
    const matchesGenre = activeGenre === "All" || n.genre === activeGenre;
    return matchesSearch && matchesGenre;
  }).sort((a, b) => {
    if (sortBy === "rating") return b.rating - a.rating;
    if (sortBy === "chapters") return b.chapters - a.chapters;
    if (sortBy === "readers") return parseInt(b.readers) - parseInt(a.readers);
    return 0;
  });

  return (
    <div className="pt-24 pb-24">
      <div className="max-w-7xl mx-auto px-6">
        {/* Hero */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-16"
        >
          <h1
            className="text-5xl lg:text-7xl font-bold mb-4"
            style={{ fontFamily: "Orbitron" }}
          >
            <span className="text-gradient">Browse</span>{" "}
            <span className="text-stardust">Novels</span>
          </h1>
          <p className="text-moon/60 text-lg max-w-2xl mx-auto">
            Explore our growing library of translated Chinese web novels.
            Cultivation, fantasy, sci-fi — your next obsession starts here.
          </p>
        </motion.div>

        {/* Search + Filters */}
        <div className="mb-12 space-y-6">
          {/* Search bar */}
          <div className="relative max-w-xl mx-auto">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-moon/40" />
            <input
              type="text"
              placeholder="Search novels or authors..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-12 pr-4 py-4 rounded-xl glass-card text-stardust placeholder:text-moon/30 focus:outline-none focus:border-neon-cyan/50 transition-all"
            />
            {search && (
              <button
                onClick={() => setSearch("")}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-moon/40 hover:text-moon"
              >
                <X className="w-5 h-5" />
              </button>
            )}
          </div>

          {/* Genre pills */}
          <div className="flex flex-wrap justify-center gap-2">
            {GENRES.map((genre) => (
              <button
                key={genre}
                onClick={() => setActiveGenre(genre)}
                className={`px-5 py-2 rounded-full text-sm font-medium transition-all ${
                  activeGenre === genre
                    ? "neon-btn"
                    : "glass-card text-moon/70 hover:text-stardust"
                }`}
              >
                {genre}
              </button>
            ))}
          </div>

          {/* Sort */}
          <div className="flex justify-center items-center gap-3">
            <Filter className="w-4 h-4 text-moon/40" />
            {[
              { key: "rating", label: "Top Rated" },
              { key: "chapters", label: "Most Chapters" },
              { key: "readers", label: "Most Popular" },
            ].map((opt) => (
              <button
                key={opt.key}
                onClick={() => setSortBy(opt.key)}
                className={`text-sm px-3 py-1.5 rounded-lg transition-all ${
                  sortBy === opt.key
                    ? "bg-neon-cyan/10 text-neon-cyan border border-neon-cyan/30"
                    : "text-moon/50 hover:text-moon"
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {/* Novel grid */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filtered.map((novel, i) => (
            <motion.div
              key={novel.slug}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              <Link
                href={`/novel/${novel.slug}`}
                className="block glass-card rounded-2xl overflow-hidden group h-full"
              >
                <div className="relative h-40 overflow-hidden bg-cosmic">
                  <div className="absolute inset-0 bg-gradient-to-br from-neon-cyan/20 via-neon-purple/15 to-cosmic" />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <BookOpen className="w-10 h-10 text-white/10" />
                  </div>
                  {/* Status badge */}
                  <div className="absolute top-3 left-3">
                    <span
                      className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                        novel.status === "Completed"
                          ? "bg-neon-green/10 text-neon-green border border-neon-green/20"
                          : "bg-neon-cyan/10 text-neon-cyan border border-neon-cyan/20"
                      }`}
                    >
                      {novel.status}
                    </span>
                  </div>
                  <div className="absolute top-3 right-3 glass-card px-3 py-1 rounded-full text-xs font-bold text-neon-purple">
                    {novel.genre}
                  </div>
                </div>
                <div className="p-5">
                  <h3 className="font-bold text-stardust mb-1 group-hover:text-neon-cyan transition-colors line-clamp-1">
                    {novel.title}
                  </h3>
                  <p className="text-moon/50 text-sm mb-3">{novel.author}</p>
                  <div className="flex items-center gap-4 text-sm mb-3">
                    <span className="flex items-center gap-1 text-neon-cyan">
                      <Star className="w-3.5 h-3.5 fill-neon-cyan" />
                      {novel.rating}
                    </span>
                    <span className="text-moon/40">{novel.chapters} ch</span>
                    <span className="text-moon/40">{novel.readers}</span>
                  </div>
                  <p className="text-moon/50 text-sm leading-relaxed line-clamp-2 mb-3">
                    {novel.description}
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {novel.tags.map((tag) => (
                      <span
                        key={tag}
                        className="text-xs px-2.5 py-1 rounded-full bg-white/5 text-moon/60 border border-white/5"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>

        {filtered.length === 0 && (
          <div className="text-center py-20">
            <BookOpen className="w-16 h-16 text-moon/20 mx-auto mb-4" />
            <p className="text-moon/40 text-lg">No novels found.</p>
          </div>
        )}
      </div>
    </div>
  );
}