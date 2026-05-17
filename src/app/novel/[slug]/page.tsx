"use client";

import { useParams } from "next/navigation";
import { motion } from "framer-motion";
import Link from "next/link";
import { BookOpen, Star, Clock, Users, Bookmark, Share2, ChevronLeft } from "lucide-react";

// This would normally come from a database/API
const NOVEL_DATA: Record<string, {
  title: string;
  author: string;
  genre: string;
  rating: number;
  totalChapters: number;
  status: string;
  readers: string;
  lastUpdated: string;
  description: string;
  longDescription: string;
  tags: string[];
  chapters: { num: number; title: string; date: string }[];
}> = {
  "martial-god-asura": {
    title: "Martial God Asura",
    author: "Kindhearted Bee",
    genre: "Cultivation",
    rating: 4.8,
    totalChapters: 5842,
    status: "Ongoing",
    readers: "1.2M",
    lastUpdated: "2025-05-16",
    description: "In a world where the strong prey on the weak, one young man defies the heavens with forbidden martial techniques.",
    longDescription: `In the Nine Provinces, strength is everything. Those who possess power rule over the weak, and the martial path is the only way to rise above one's station.\n\nChu Feng was an ordinary outer disciple of the Azure Dragon School, mocked for his lack of talent and low-born status. But when a mysterious lightning strikes him during a fateful night, everything changes.\n\nA strange power awakens within him — the ability to devour any martial technique and perfect it instantly. Armed with this heaven-defying gift, Chu Feng embarks on a journey that will shake the very foundations of the cultivation world.\n\nFrom a despised outcast to a Martial God feared across the continents, witness the rise of a legend.`,
    tags: ["Xianxia", "Action", "Romance", "Harem", "Overpowered MC"],
    chapters: Array.from({ length: 50 }, (_, i) => ({
      num: i + 1,
      title: `Chapter ${i + 1}: ${["The Outer Disciple", "Lightning from the Heavens", "The Mysterious Power", "First Battle", "Rising Fame", "The Azure Dragon Tournament"][i % 6]}`,
      date: new Date(2025, 4, 16 - i).toISOString().split("T")[0],
    })),
  },
  "against-the-gods": {
    title: "Against the Gods",
    author: "Mars Gravity",
    genre: "Fantasy",
    rating: 4.9,
    totalChapters: 2014,
    status: "Ongoing",
    readers: "980K",
    lastUpdated: "2025-05-15",
    description: "A boy cursed with crippled meridians obtains a mysterious pearl that changes his destiny forever.",
    longDescription: `Yun Che was a genius — once. After a tragic accident destroyed his meridians, he became the laughing stock of his clan. Crippled and betrayed, he lived a life of misery until a single act of defiance cost him everything.\n\nBut death was not the end. Reborn into a new world with the Heaven Punishing Ancestral Sword and a mysterious pearl containing a primordial True God's legacy, Yun Che will carve his own path against the heavens themselves.\n\nThis is a story of vengeance, love, and absolute power in a world where gods play games with mortal lives.`,
    tags: ["Xuanhuan", "Harem", "Revenge", "Overpowered MC"],
    chapters: Array.from({ length: 50 }, (_, i) => ({
      num: i + 1,
      title: `Chapter ${i + 1}`,
      date: new Date(2025, 4, 16 - i).toISOString().split("T")[0],
    })),
  },
  "i-shall-seal-the-heavens": {
    title: "I Shall Seal the Heavens",
    author: "Er Gen",
    genre: "Cultivation",
    rating: 4.9,
    totalChapters: 1614,
    status: "Completed",
    readers: "850K",
    lastUpdated: "2024-12-01",
    description: "A failed scholar is kidnapped and thrust into the world of cultivation.",
    longDescription: `Meng Hao was a scholar who had failed the imperial exams three times. Just as he resigned himself to a life of mediocrity, he was kidnapped by a group of cultivators and forced to join the Reliance Sect.\n\nArmed with nothing but a bronze mirror and an indomitable will, Meng Hao must navigate a world of schemes, deadly sects, and ancient secrets. His journey will take him from the humble State of Zhao to the very pinnacle of the universe.\n\n"I shall seal the heavens, suppress the earth, and forge an eternal legend!"`,
    tags: ["Xianxia", "Comedy", "Tragedy", "Alchemy"],
    chapters: Array.from({ length: 50 }, (_, i) => ({
      num: i + 1,
      title: `Chapter ${i + 1}`,
      date: new Date(2024, 11, 1 - i).toISOString().split("T")[0],
    })),
  },
  "reverend-insanity": {
    title: "Reverend Insanity",
    author: "Gu Zhen Ren",
    genre: "Dark Fantasy",
    rating: 4.7,
    totalChapters: 2334,
    status: "Ongoing",
    readers: "720K",
    lastUpdated: "2025-05-16",
    description: "A demon lord travels 500 years back in time to achieve eternal life — no matter the cost.",
    longDescription: `Fang Yuan was a demonic cultivator who had lived for over 500 years. Betrayed and cornered, he used the Spring Autumn Cicada to travel back in time to his youth.\n\nWith centuries of experience and knowledge of future events, Fang Yuan will stop at nothing to achieve his goal: eternal life. Morality, love, friendship — these are mere tools for the truly ambitious.\n\nThis is not a story of a hero. This is the legend of a true demon.`,
    tags: ["Xianxia", "Dark", "Anti-Hero", "Ruthless MC"],
    chapters: Array.from({ length: 50 }, (_, i) => ({
      num: i + 1,
      title: `Chapter ${i + 1}`,
      date: new Date(2025, 4, 16 - i).toISOString().split("T")[0],
    })),
  },
};

export default function NovelDetailPage() {
  const params = useParams();
  const slug = params.slug as string;
  const novel = NOVEL_DATA[slug];

  if (!novel) {
    return (
      <div className="pt-32 pb-24 text-center">
        <BookOpen className="w-20 h-20 text-moon/20 mx-auto mb-6" />
        <h1 className="text-3xl font-bold text-stardust mb-2">Novel Not Found</h1>
        <p className="text-moon/40 mb-8">The novel you're looking for doesn't exist.</p>
        <Link href="/novels" className="neon-btn px-6 py-3 rounded-xl">
          Browse Novels
        </Link>
      </div>
    );
  }

  return (
    <div className="pt-24 pb-24">
      <div className="max-w-7xl mx-auto px-6">
        {/* Back button */}
        <Link
          href="/novels"
          className="inline-flex items-center gap-2 text-moon/50 hover:text-neon-cyan transition-colors mb-8"
        >
          <ChevronLeft className="w-4 h-4" />
          Back to Novels
        </Link>

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid lg:grid-cols-[280px_1fr] gap-10 mb-16"
        >
          {/* Cover */}
          <div>
            <div className="aspect-[3/4] rounded-2xl overflow-hidden glass-card">
              <div className="w-full h-full bg-gradient-to-br from-neon-cyan/30 via-neon-purple/20 to-cosmic flex items-center justify-center">
                <BookOpen className="w-16 h-16 text-white/10" />
              </div>
            </div>
            <div className="mt-4 flex gap-3">
              <button className="flex-1 neon-btn py-3 rounded-xl text-sm font-bold flex items-center justify-center gap-2">
                <BookOpen className="w-4 h-4" />
                Start Reading
              </button>
              <button className="glass-card p-3 rounded-xl text-moon hover:text-neon-cyan transition-colors">
                <Bookmark className="w-5 h-5" />
              </button>
              <button className="glass-card p-3 rounded-xl text-moon hover:text-neon-cyan transition-colors">
                <Share2 className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Info */}
          <div>
            <div className="flex flex-wrap items-start gap-3 mb-2">
              <span className={`text-xs px-3 py-1 rounded-full font-medium ${
                novel.status === "Completed"
                  ? "bg-neon-green/10 text-neon-green border border-neon-green/20"
                  : "bg-neon-cyan/10 text-neon-cyan border border-neon-cyan/20"
              }`}>
                {novel.status}
              </span>
              <span className="glass-card px-3 py-1 rounded-full text-xs font-bold text-neon-purple">
                {novel.genre}
              </span>
            </div>

            <h1
              className="text-4xl lg:text-6xl font-bold text-stardust mb-3"
              style={{ fontFamily: "Orbitron" }}
            >
              {novel.title}
            </h1>
            <p className="text-xl text-moon/50 mb-6">by {novel.author}</p>

            {/* Stats */}
            <div className="flex flex-wrap gap-6 mb-8">
              <div className="flex items-center gap-2">
                <Star className="w-5 h-5 fill-neon-cyan text-neon-cyan" />
                <span className="text-stardust font-bold text-lg">{novel.rating}</span>
                <span className="text-moon/40 text-sm">/ 5.0</span>
              </div>
              <div className="flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-neon-purple" />
                <span className="text-stardust font-bold">{novel.totalChapters.toLocaleString()}</span>
                <span className="text-moon/40 text-sm">chapters</span>
              </div>
              <div className="flex items-center gap-2">
                <Users className="w-5 h-5 text-neon-pink" />
                <span className="text-stardust font-bold">{novel.readers}</span>
                <span className="text-moon/40 text-sm">readers</span>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="w-5 h-5 text-neon-green" />
                <span className="text-moon text-sm">Updated {novel.lastUpdated}</span>
              </div>
            </div>

            {/* Tags */}
            <div className="flex flex-wrap gap-2 mb-6">
              {novel.tags.map((tag) => (
                <span key={tag} className="text-xs px-3 py-1.5 rounded-full bg-white/5 text-moon/70 border border-white/10">
                  {tag}
                </span>
              ))}
            </div>

            {/* Description */}
            <div className="glass-card rounded-2xl p-6">
              <h3 className="text-lg font-bold text-stardust mb-3">Synopsis</h3>
              {novel.longDescription.split("\n\n").map((p, i) => (
                <p key={i} className="text-moon/60 leading-relaxed mb-3 last:mb-0">
                  {p}
                </p>
              ))}
            </div>
          </div>
        </motion.div>

        {/* Chapters */}
        <section>
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-2xl font-bold text-stardust" style={{ fontFamily: "Orbitron" }}>
              <span className="text-gradient">Chapters</span>
            </h2>
            <div className="text-sm text-moon/40">
              Showing 1–50 of {novel.totalChapters.toLocaleString()}
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {novel.chapters.map((ch, i) => (
              <motion.div
                key={ch.num}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.02 }}
              >
                <Link
                  href={`/novel/${slug}/chapter/${ch.num}`}
                  className="flex items-center justify-between p-4 rounded-xl glass-card hover:border-neon-cyan/30 transition-all group"
                >
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-stardust group-hover:text-neon-cyan transition-colors truncate">
                      Ch. {ch.num}
                    </div>
                    <div className="text-xs text-moon/40 mt-0.5 truncate">
                      {ch.title}
                    </div>
                  </div>
                  <div className="text-xs text-moon/30 ml-3 flex-shrink-0">
                    {ch.date}
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}