import { notFound } from "next/navigation";
import Link from "next/link";
import type { Metadata } from "next";
import fs from "fs";
import path from "path";
import { Calendar, ArrowLeft, Clock } from "lucide-react";

interface Post {
  slug: string;
  title: string;
  date: string;
  author: string;
  excerpt: string;
  tags: string[];
  content: string;
}

// Generate static params for all blog posts
export function generateStaticParams() {
  const postsFile = path.join(process.cwd(), "data", "blog", "posts.json");
  if (!fs.existsSync(postsFile)) return [];
  const posts: Post[] = JSON.parse(fs.readFileSync(postsFile, "utf-8"));
  return posts.map((p) => ({ slug: p.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const postsFile = path.join(process.cwd(), "data", "blog", "posts.json");
  if (!fs.existsSync(postsFile)) return {};
  const posts: Post[] = JSON.parse(fs.readFileSync(postsFile, "utf-8"));
  const post = posts.find((p) => p.slug === slug);
  if (!post) return {};
  return {
    title: `${post.title} — Nexus Tales Blog`,
    description: post.excerpt,
    alternates: { canonical: `https://novelhub.beauty/blog/${slug}` },
  };
}

export default async function BlogPostPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const postsFile = path.join(process.cwd(), "data", "blog", "posts.json");
  if (!fs.existsSync(postsFile)) notFound();
  const posts: Post[] = JSON.parse(fs.readFileSync(postsFile, "utf-8"));
  const post = posts.find((p) => p.slug === slug);
  if (!post) notFound();

  // Parse reading time (~200 wpm)
  const wordCount = post.content.split(/\s+/).length;
  const readingTime = Math.max(1, Math.round(wordCount / 200));

  return (
    <article className="pt-28 pb-24">
      <div className="max-w-3xl mx-auto px-6">
        {/* Back */}
        <Link href="/blog" className="inline-flex items-center gap-1.5 text-moon/40 hover:text-neon-cyan transition-colors text-sm mb-8">
          <ArrowLeft className="w-4 h-4" /> Back to Blog
        </Link>

        {/* Tags */}
        <div className="flex flex-wrap gap-2 mb-4">
          {post.tags.map((tag) => (
            <span key={tag} className="text-xs px-2.5 py-1 rounded-full bg-white/5 border border-white/10 text-moon/40">
              {tag}
            </span>
          ))}
        </div>

        {/* Title */}
        <h1 className="text-3xl lg:text-4xl font-bold text-stardust mb-4" style={{ fontFamily: "Orbitron" }}>
          {post.title}
        </h1>

        {/* Meta */}
        <div className="flex items-center gap-4 text-xs text-moon/30 mb-10 pb-8 border-b border-white/5">
          <span className="flex items-center gap-1"><Calendar className="w-3.5 h-3.5" /> {post.date}</span>
          <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" /> {readingTime} min read</span>
          <span>By {post.author}</span>
        </div>

        {/* Content */}
        <div className="prose prose-invert prose-lg max-w-none
          prose-headings:text-stardust prose-headings:font-bold
          prose-h2:text-2xl prose-h2:mt-10 prose-h2:mb-4
          prose-h3:text-xl prose-h3:mt-8 prose-h3:mb-3
          prose-p:text-moon/70 prose-p:leading-relaxed prose-p:mb-5
          prose-strong:text-stardust prose-strong:font-semibold
          prose-li:text-moon/60
          prose-a:text-neon-cyan prose-a:no-underline hover:prose-a:underline"
        >
          {post.content.split('\n').map((line, i) => {
            if (line.startsWith('## ')) {
              return <h2 key={i}>{line.slice(3)}</h2>;
            }
            if (line.startsWith('### ')) {
              return <h3 key={i}>{line.slice(4)}</h3>;
            }
            if (line.startsWith('- **')) {
              const match = line.match(/^- \*\*(.+?)\*\*(.+)?$/);
              if (match) {
                return <li key={i}><strong>{match[1]}</strong>{match[2] || ''}</li>;
              }
            }
            if (line.startsWith('1. ') || line.startsWith('2. ') || line.startsWith('3. ') || line.startsWith('4. ') || line.startsWith('5. ')) {
              const text = line.replace(/^\d+\.\s*/, '');
              const boldMatch = text.match(/^\*\*(.+?)\*\*(.+)?$/);
              if (boldMatch) {
                return <li key={i}><strong>{boldMatch[1]}</strong>{boldMatch[2] || ''}</li>;
              }
              return <li key={i}>{text}</li>;
            }
            if (line.trim() === '') return <br key={i} />;
            return <p key={i}>{line}</p>;
          })}
        </div>

        {/* Back to Blog */}
        <div className="mt-14 pt-8 border-t border-white/5 text-center">
          <Link href="/blog" className="inline-flex items-center gap-2 text-neon-cyan hover:text-neon-cyan/80 transition-colors font-medium">
            <ArrowLeft className="w-4 h-4" /> Read More Articles
          </Link>
        </div>
      </div>
    </article>
  );
}
