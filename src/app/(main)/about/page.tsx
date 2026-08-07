import type { Metadata } from "next";
import Link from "next/link";
import { BookOpen, Globe, Sparkles, HeartHandshake } from "lucide-react";

export const metadata: Metadata = {
  title: "About Nexus Tales — Your Home for Translated Chinese Web Novels",
  description: "Learn about Nexus Tales: our mission to bring the best Chinese cultivation, xianxia, wuxia, and fantasy web novels to English readers worldwide — free, daily, and beautifully presented.",
  alternates: { canonical: "https://novelhub.beauty/about" },
};

export default function AboutPage() {
  return (
    <div className="pt-28 pb-24">
      <div className="max-w-3xl mx-auto px-6">
        {/* Hero */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-neon-cyan/10 border border-neon-cyan/20 text-neon-cyan text-sm mb-4">
            <Sparkles className="w-4 h-4" /> Our Story
          </div>
          <h1 className="text-4xl lg:text-5xl font-bold text-stardust mb-4" style={{ fontFamily: "Orbitron" }}>
            About Nexus Tales
          </h1>
          <p className="text-moon/50 text-lg">
            Bridging cultures, one chapter at a time.
          </p>
        </div>

        {/* Mission */}
        <section className="glass-card rounded-2xl p-8 mb-8">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-neon-cyan/10 border border-neon-cyan/20 flex items-center justify-center shrink-0">
              <Globe className="w-6 h-6 text-neon-cyan" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-stardust mb-2">Our Mission</h2>
              <p className="text-moon/60 leading-relaxed">
                Chinese web novels represent one of the richest storytelling traditions of the 21st century —
                spanning cultivation epics, wuxia adventures, romance dramas, and fantasy worlds beloved by
                hundreds of millions of readers. Yet for English-speaking audiences, this treasure trove remains
                largely inaccessible. Nexus Tales exists to change that. We curate, translate, and present the
                finest Chinese web novels with the respect and polish they deserve.
              </p>
            </div>
          </div>
        </section>

        {/* What we do */}
        <section className="glass-card rounded-2xl p-8 mb-8">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-neon-purple/10 border border-neon-purple/20 flex items-center justify-center shrink-0">
              <BookOpen className="w-6 h-6 text-neon-purple" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-stardust mb-2">What We Offer</h2>
              <ul className="text-moon/60 leading-relaxed space-y-2 mt-2">
                <li>• <strong className="text-stardust">A growing library</strong> of 1,300+ novels across cultivation, xianxia, wuxia, romance, and fantasy.</li>
                <li>• <strong className="text-stardust">Daily chapter updates</strong> — fresh translations added every single day.</li>
                <li>• <strong className="text-stardust">Beautiful presentation</strong> — clean reading experience, custom covers, and mobile-friendly design.</li>
                <li>• <strong className="text-stardust">Free to read</strong> — our core library is and always will be free.</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Editorial standards */}
        <section className="glass-card rounded-2xl p-8 mb-8">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-neon-green/10 border border-neon-green/20 flex items-center justify-center shrink-0">
              <HeartHandshake className="w-6 h-6 text-neon-green" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-stardust mb-2">Our Editorial Standards</h2>
              <p className="text-moon/60 leading-relaxed">
                Every novel in our collection is selected for its storytelling merit. We provide chapter
                summaries, author backgrounds, and genre guides to help readers navigate the vast world of
                Chinese web fiction. Our blog features original guides, recommendations, and deep dives written
                by our editorial team — not auto-generated filler.
              </p>
            </div>
          </div>
        </section>

        {/* CTA */}
        <div className="text-center mt-12">
          <p className="text-moon/50 mb-6">
            Ready to start your cultivation journey?
          </p>
          <div className="flex gap-4 justify-center flex-wrap">
            <Link
              href="/novels"
              className="px-6 py-3 rounded-xl bg-neon-cyan/10 border border-neon-cyan/30 text-neon-cyan hover:bg-neon-cyan/20 transition-all font-medium"
            >
              Browse Novels
            </Link>
            <Link
              href="/blog"
              className="px-6 py-3 rounded-xl bg-white/5 border border-white/10 text-stardust hover:bg-white/10 transition-all font-medium"
            >
              Read the Blog
            </Link>
          </div>
        </div>

        {/* Footer note */}
        <p className="text-center text-moon/30 text-sm mt-16">
          Nexus Tales is a fan-driven project celebrating Chinese web literature. All novels are translated
          for promotional and educational purposes. Original copyrights belong to their respective authors and publishers.
        </p>
      </div>
    </div>
  );
}
