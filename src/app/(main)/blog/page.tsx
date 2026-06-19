import Link from "next/link";
import type { Metadata } from "next";
import fs from "fs";
import path from "path";
import { BookOpen, Calendar, ArrowRight } from "lucide-react";

export const metadata: Metadata = {
  title: "Blog — Nexus Tales | Chinese Web Novel Guides & Insights",
  description: "Expert guides, reading recommendations, and deep dives into Chinese web novels, xianxia, wuxia, and cultivation fiction. Start your journey here.",
  alternates: { canonical: "https://novelhub.beauty/blog" },
};

interface Post {
  slug: string;
  title: string;
  date: string;
  author: string;
  excerpt: string;
  tags: string[];
}

export default function BlogPage() {
  const postsFile = path.join(process.cwd(), "data", "blog", "posts.json");
  let posts: Post[] = [];
  if (fs.existsSync(postsFile)) {
    posts = JSON.parse(fs.readFileSync(postsFile, "utf-8"));
  }
  posts.sort((a, b) => b.date.localeCompare(a.date));

  return (
    <div className="pt-28 pb-24">
      <div className="max-w-4xl mx-auto px-6">
        {/* Header */}
        <div className="text-center mb-14">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-neon-cyan/10 border border-neon-cyan/20 text-neon-cyan text-sm mb-4">
            <BookOpen className="w-4 h-4" /> Nexus Tales Blog
          </div>
          <h1 className="text-3xl lg:text-4xl font-bold text-stardust mb-3" style={{ fontFamily: "Orbitron" }}>
            Guides, Insights & Stories
          </h1>
          <p className="text-moon/40 text-lg max-w-lg mx-auto">
            Dive deeper into the world of Chinese web novels — cultivation guides, reading recommendations, and behind-the-scenes content.
          </p>
        </div>

        {/* Posts Grid */}
        <div className="grid sm:grid-cols-2 gap-6">
          {posts.map((post) => (
            <Link
              key={post.slug}
              href={`/blog/${post.slug}`}
              className="group glass-card rounded-2xl p-6 hover:border-neon-cyan/30 transition-all duration-300 flex flex-col"
            >
              <div className="flex flex-wrap gap-2 mb-3">
                {post.tags.map((tag) => (
                  <span key={tag} className="text-xs px-2.5 py-1 rounded-full bg-white/5 border border-white/10 text-moon/40">
                    {tag}
                  </span>
                ))}
              </div>
              <h2 className="text-lg font-bold text-stardust group-hover:text-neon-cyan transition-colors mb-2 line-clamp-2">
                {post.title}
              </h2>
              <p className="text-moon/40 text-sm mb-4 flex-grow line-clamp-3">
                {post.excerpt}
              </p>
              <div className="flex items-center justify-between text-xs text-moon/30 mt-auto pt-4 border-t border-white/5">
                <span className="flex items-center gap-1">
                  <Calendar className="w-3.5 h-3.5" />
                  {post.date}
                </span>
                <span className="flex items-center gap-1 text-neon-cyan/60 group-hover:text-neon-cyan transition-colors">
                  Read <ArrowRight className="w-3.5 h-3.5" />
                </span>
              </div>
            </Link>
          ))}
        </div>

        {/* CTA */}
        <div className="glass-card rounded-2xl p-8 text-center mt-14">
          <h3 className="text-xl font-bold text-stardust mb-2" style={{ fontFamily: "Orbitron" }}>
            Ready to Start Reading?
          </h3>
          <p className="text-moon/40 mb-4">Browse our collection of premium translated cultivation novels.</p>
          <Link
            href="/"
            className="inline-flex items-center gap-2 bg-neon-cyan/10 hover:bg-neon-cyan/20 border border-neon-cyan/30 text-neon-cyan px-6 py-3 rounded-xl font-medium transition-all"
          >
            Browse Novels <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    </div>
  );
}
