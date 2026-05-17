"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import {
  BookOpen,
  Sparkles,
  TrendingUp,
  Star,
  Shield,
  Globe,
} from "lucide-react";

const FEATURED_NOVELS = [
  {
    slug: "martial-god-asura",
    title: "Martial God Asura",
    author: "Kindhearted Bee",
    genre: "Cultivation",
    rating: 4.8,
    chapters: 5842,
    cover: "/covers/martial-god-asura.jpg",
    description:
      "In a world where the strong prey on the weak, one young man defies the heavens with forbidden martial techniques.",
    tags: ["Xianxia", "Action", "Romance"],
  },
  {
    slug: "against-the-gods",
    title: "Against the Gods",
    author: "Mars Gravity",
    genre: "Fantasy",
    rating: 4.9,
    chapters: 2014,
    cover: "/covers/against-the-gods.jpg",
    description:
      "A boy cursed with crippled meridians obtains a mysterious pearl that changes his destiny forever.",
    tags: ["Xuanhuan", "Harem", "Revenge"],
  },
  {
    slug: "i-shall-seal-the-heavens",
    title: "I Shall Seal the Heavens",
    author: "Er Gen",
    genre: "Cultivation",
    rating: 4.9,
    chapters: 1614,
    cover: "/covers/issth.jpg",
    description:
      "A failed scholar is kidnapped and thrust into the world of cultivation, where he must seal the heavens themselves.",
    tags: ["Xianxia", "Comedy", "Tragedy"],
  },
  {
    slug: "reverend-insanity",
    title: "Reverend Insanity",
    author: "Gu Zhen Ren",
    genre: "Dark Fantasy",
    rating: 4.7,
    chapters: 2334,
    cover: "/covers/reverend-insanity.jpg",
    description:
      "A demon lord travels 500 years back in time, determined to achieve eternal life — no matter the cost.",
    tags: ["Xianxia", "Dark", "Anti-Hero"],
  },
];

const STATS = [
  { icon: BookOpen, value: "500+", label: "Novels" },
  { icon: Globe, value: "12+", label: "Languages" },
  { icon: Sparkles, value: "50K+", label: "Daily Readers" },
  { icon: TrendingUp, value: "2M+", label: "Chapters" },
];

export default function HomePage() {
  return (
    <>
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center pt-16">
        <div className="hero-glow absolute inset-0 -top-20" />
        <div className="relative z-10 max-w-7xl mx-auto px-6 w-full">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
            >
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card mb-8 text-sm">
                <Sparkles className="w-4 h-4 text-neon-cyan" />
                <span className="text-moon">
                  #1 Source for Translated Chinese Novels
                </span>
              </div>

              <h1 className="text-5xl lg:text-7xl font-bold leading-tight mb-6">
                <span
                  className="text-gradient block"
                  style={{ fontFamily: "Orbitron" }}
                >
                  CULTIVATE
                </span>
                <span className="text-stardust">Your Imagination</span>
              </h1>

              <p className="text-lg text-moon/70 mb-10 max-w-lg leading-relaxed">
                Dive into epic tales of immortal heroes, forbidden arts, and
                world-shaking battles. Thousands of translated Chinese novels at
                your fingertips.
              </p>

              <div className="flex flex-wrap gap-4">
                <Link
                  href="/novels"
                  className="neon-btn px-8 py-4 rounded-xl text-lg inline-flex items-center gap-2"
                >
                  <BookOpen className="w-5 h-5" />
                  Start Reading
                </Link>
                <Link
                  href="#featured"
                  className="glass-card px-8 py-4 rounded-xl text-lg text-moon hover:text-neon-cyan transition-all"
                >
                  Featured Novels
                </Link>
              </div>

              {/* Stats row */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-6 mt-16">
                {STATS.map((stat) => (
                  <div key={stat.label} className="text-center">
                    <stat.icon className="w-5 h-5 text-neon-purple mx-auto mb-2" />
                    <div className="text-2xl font-bold text-stardust">
                      {stat.value}
                    </div>
                    <div className="text-xs text-moon/50 mt-1">
                      {stat.label}
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* Hero visual */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 1, delay: 0.3 }}
              className="hidden lg:block"
            >
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-br from-neon-cyan/20 via-neon-purple/10 to-transparent rounded-3xl blur-3xl" />
                <div className="relative glass-card rounded-3xl p-8 aspect-[4/5] overflow-hidden">
                  {/* Simulated book shelf */}
                  {[...Array(5)].map((_, i) => (
                    <div
                      key={i}
                      className="mb-4 p-4 rounded-xl"
                      style={{
                        background: `rgba(255,255,255,${0.03 + i * 0.01})`,
                      }}
                    >
                      <div className="flex gap-4 items-center">
                        <div
                          className="w-10 h-14 rounded flex-shrink-0"
                          style={{
                            background: `linear-gradient(135deg, 
                              ${["#00f0ff", "#b44dff", "#ff2d95", "#39ff14", "#ff8c00"][i]}40, 
                              ${["#00f0ff", "#b44dff", "#ff2d95", "#39ff14", "#ff8c00"][i]}10)`,
                          }}
                        />
                        <div className="flex-1">
                          <div className="h-3 bg-white/10 rounded w-3/4 mb-2" />
                          <div className="h-2 bg-white/5 rounded w-1/2" />
                        </div>
                        <Star className="w-4 h-4 text-neon-cyan" />
                      </div>
                    </div>
                  ))}
                  {/* Floating glow orbs */}
                  <div className="absolute top-10 right-10 w-20 h-20 bg-neon-cyan/20 rounded-full blur-2xl animate-pulse" />
                  <div className="absolute bottom-20 left-10 w-32 h-32 bg-neon-purple/15 rounded-full blur-3xl animate-pulse" />
                </div>
              </div>
            </motion.div>
          </div>
        </div>

        {/* Scroll indicator */}
        <motion.div
          animate={{ y: [0, 10, 0] }}
          transition={{ repeat: Infinity, duration: 2 }}
          className="absolute bottom-8 left-1/2 -translate-x-1/2"
        >
          <div className="w-6 h-10 rounded-full border-2 border-white/20 flex items-start justify-center p-1">
            <div className="w-1.5 h-3 bg-neon-cyan rounded-full animate-pulse" />
          </div>
        </motion.div>
      </section>

      {/* Why Choose Us */}
      <section className="py-24 relative">
        <div className="max-w-7xl mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2
              className="text-4xl lg:text-5xl font-bold mb-4"
              style={{ fontFamily: "Orbitron" }}
            >
              <span className="text-gradient">Why</span>{" "}
              <span className="text-stardust">Nexus Tales?</span>
            </h2>
            <p className="text-moon/60 text-lg max-w-2xl mx-auto">
              We bring the best Chinese web novels to readers worldwide, with
              daily updates and quality translations.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-6">
            {[
              {
                icon: Shield,
                title: "Quality Translations",
                desc: "Every chapter is carefully translated and edited by our team to preserve the original flavor and nuance.",
              },
              {
                icon: Sparkles,
                title: "Daily Updates",
                desc: "New chapters every day. Never wait weeks between updates — follow multiple novels simultaneously.",
              },
              {
                icon: Globe,
                title: "Worldwide Community",
                desc: "Join thousands of readers from 150+ countries. Discuss theories, share memes, and connect with fellow fans.",
              },
            ].map((item, i) => (
              <motion.div
                key={item.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.15 }}
                className="glass-card rounded-2xl p-8 text-center group"
              >
                <div className="w-16 h-16 rounded-2xl bg-neon-cyan/10 flex items-center justify-center mx-auto mb-6 group-hover:bg-neon-cyan/20 transition-all">
                  <item.icon className="w-8 h-8 text-neon-cyan" />
                </div>
                <h3 className="text-xl font-bold text-stardust mb-3">
                  {item.title}
                </h3>
                <p className="text-moon/60 text-sm leading-relaxed">
                  {item.desc}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Novels */}
      <section id="featured" className="py-24 relative">
        <div className="max-w-7xl mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="flex items-end justify-between mb-12"
          >
            <div>
              <h2
                className="text-4xl lg:text-5xl font-bold mb-3"
                style={{ fontFamily: "Orbitron" }}
              >
                <span className="text-gradient">Featured</span>{" "}
                <span className="text-stardust">Novels</span>
              </h2>
              <p className="text-moon/60">
                Start your cultivation journey with these epic tales
              </p>
            </div>
            <Link
              href="/novels"
              className="hidden sm:flex items-center gap-2 text-neon-cyan hover:text-neon-purple transition-colors text-sm font-semibold"
            >
              View All <span className="text-lg">&rarr;</span>
            </Link>
          </motion.div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {FEATURED_NOVELS.map((novel, i) => (
              <motion.div
                key={novel.slug}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
              >
                <Link
                  href={`/novel/${novel.slug}`}
                  className="block glass-card rounded-2xl overflow-hidden group h-full"
                >
                  {/* Cover */}
                  <div className="relative h-48 overflow-hidden bg-cosmic">
                    <div className="absolute inset-0 bg-gradient-to-br from-neon-cyan/30 via-neon-purple/20 to-cosmic" />
                    <div className="absolute inset-0 flex items-center justify-center">
                      <BookOpen className="w-12 h-12 text-white/20" />
                    </div>
                    <div className="absolute top-3 right-3 glass-card px-3 py-1 rounded-full text-xs font-bold text-neon-cyan">
                      {novel.genre}
                    </div>
                  </div>

                  <div className="p-5">
                    <h3 className="font-bold text-stardust mb-1 text-lg group-hover:text-neon-cyan transition-colors line-clamp-1">
                      {novel.title}
                    </h3>
                    <p className="text-moon/50 text-sm mb-3">{novel.author}</p>

                    {/* Rating + Stats */}
                    <div className="flex items-center gap-4 text-sm mb-3">
                      <span className="flex items-center gap-1 text-neon-cyan">
                        <Star className="w-3.5 h-3.5 fill-neon-cyan" />
                        {novel.rating}
                      </span>
                      <span className="text-moon/40">
                        {novel.chapters.toLocaleString()} ch
                      </span>
                    </div>

                    <p className="text-moon/50 text-sm leading-relaxed line-clamp-2 mb-4">
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

          {/* Mobile view all link */}
          <div className="text-center mt-8 sm:hidden">
            <Link
              href="/novels"
              className="neon-btn px-8 py-3 rounded-xl inline-flex items-center gap-2"
            >
              View All Novels <span>&rarr;</span>
            </Link>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 relative">
        <div className="absolute inset-0 hero-glow" />
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-4xl mx-auto px-6 text-center relative z-10"
        >
          <div className="glass-card rounded-3xl p-12 lg:p-16">
            <Sparkles className="w-12 h-12 text-neon-cyan mx-auto mb-6" />
            <h2
              className="text-3xl lg:text-5xl font-bold mb-4"
              style={{ fontFamily: "Orbitron" }}
            >
              <span className="text-gradient">Ready</span>{" "}
              <span className="text-stardust">to Cultivate?</span>
            </h2>
            <p className="text-moon/60 text-lg mb-8 max-w-2xl mx-auto">
              Join thousands of readers discovering the best Chinese web novels.
              Free to read, updated daily.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/novels"
                className="neon-btn px-10 py-4 rounded-xl text-lg inline-flex items-center justify-center gap-2"
              >
                <BookOpen className="w-5 h-5" />
                Browse Novels
              </Link>
              <Link
                href="/novels"
                className="glass-card px-10 py-4 rounded-xl text-lg text-moon hover:text-neon-cyan transition-all"
              >
                Top Rankings
              </Link>
            </div>
          </div>
        </motion.div>
      </section>
    </>
  );
}