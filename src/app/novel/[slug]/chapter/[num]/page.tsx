"use client";

import { useParams } from "next/navigation";
import { motion } from "framer-motion";
import Link from "next/link";
import {
  ChevronLeft,
  ChevronRight,
  Sun,
  Moon,
  Type,
  BookOpen,
  ArrowLeft,
} from "lucide-react";
import { useState } from "react";

// Sample chapter content (would come from a database)
const CHAPTER_CONTENT: Record<string, Record<number, { title: string; content: string }>> = {
  "martial-god-asura": {
    1: {
      title: "The Outer Disciple",
      content: `The Azure Dragon School spanned across ten peaks, each one towering into the clouds like ancient titans frozen in time. At the foot of the third peak, a young man sat cross-legged beneath a withered tree, his face pale and covered in sweat.\n\nChu Feng was seventeen years old this year, yet his cultivation had stagnated at the first level of the Spirit realm for three full years.\n\n"Trash."\n\n"You're wasting the school's resources." Every day, he heard these words. And every day, they cut deeper than any blade.\n\nToday had been particularly bad. A group of inner disciples had beaten him senseless for accidentally looking at one of them the wrong way. His ribs still ached with every breath.\n\nBut Chu Feng did not cry. He never did.\n\nHe simply closed his eyes and focused on the weak spiritual energy flowing through his damaged meridians. One day, he swore to himself. One day, everything would change.\n\nLittle did he know, that day was today.\n\nAbove the Azure Dragon School, storm clouds gathered with unnatural speed. Within moments, the clear blue sky had transformed into a churning sea of black and purple.\n\nAnd at the heart of that storm, a single bolt of golden lightning was forming — aimed directly at the foot of the third peak.`,
    },
    2: {
      title: "Lightning from the Heavens",
      content: `The golden lightning struck without warning.\n\nOne moment Chu Feng was meditating under the withered tree. The next, his entire world became light — blinding, all-consuming, divine light that seemed to pierce through his very soul.\n\nThe pain was indescribable. It felt as if every fiber of his being was being torn apart and rebuilt simultaneously. His meridians, long crippled and weak, began to crack and reform.\n\nAnd then, as suddenly as it had come, the lightning vanished.\n\nChu Feng collapsed to the ground, smoke rising from his body, his clothes reduced to rags. But when he opened his eyes, something was different.\n\nHe could feel it.\n\nThe spiritual energy of heaven and earth — which he had struggled to sense for years — was now flooding into his body like an unstoppable tide. His damaged meridians were not just healed; they had been transformed into something far beyond normal.\n\n"What... what happened to me?" he whispered, staring at his hands.\n\nIn his mind's eye, he could suddenly perceive strands of spiritual energy as clearly as he could see the grass beneath his feet. Not just perceive — he could almost... devour them.\n\nA strange, primal instinct surged within him. Without consciously deciding to, Chu Feng reached out with his newly awakened senses and pulled.\n\nThe spiritual energy in a hundred-meter radius rushed towards him like iron filings to a magnet. Within heartbeats, he had absorbed more energy than most cultivators could gather in a month.\n\nHis cultivation base, which had been stuck at the first level of Spirit realm for three years, instantly broke through to the second level.\n\nThen the third.\n\nThen the fourth.\n\nBy the time the energy settled, Chu Feng sat there in stunned silence at the peak of the fourth Spirit realm.\n\n"What in the nine heavens is happening to me?`,
    },
  },
};

export default function ChapterPage() {
  const params = useParams();
  const slug = params.slug as string;
  const chapterNum = parseInt(params.num as string);

  const novelChapters = CHAPTER_CONTENT[slug];
  const chapter = novelChapters?.[chapterNum];
  const totalChapters = novelChapters ? Object.keys(novelChapters).length : 0;

  const [darkMode, setDarkMode] = useState(true);
  const [fontSize, setFontSize] = useState<"md" | "lg" | "xl">("md");

  if (!chapter) {
    return (
      <div className="pt-32 pb-24 text-center">
        <BookOpen className="w-20 h-20 text-moon/20 mx-auto mb-6" />
        <h1 className="text-3xl font-bold text-stardust mb-2">Chapter Not Found</h1>
        <p className="text-moon/40 mb-8">This chapter doesn't exist yet. Check back soon!</p>
        <Link href={`/novel/${slug}`} className="neon-btn px-6 py-3 rounded-xl">
          Back to Novel
        </Link>
      </div>
    );
  }

  const fontSizeClasses = {
    md: "text-base",
    lg: "text-lg",
    xl: "text-xl",
  };

  return (
    <div className="pt-24 pb-24">
      <div className="max-w-3xl mx-auto px-6">
        {/* Reading controls */}
        <div className="fixed top-20 right-6 z-40 flex flex-col gap-2">
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="glass-card p-3 rounded-xl text-moon hover:text-neon-cyan transition-all"
            title="Toggle theme"
          >
            {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>
          {(["md", "lg", "xl"] as const).map((size) => (
            <button
              key={size}
              onClick={() => setFontSize(size)}
              className={`glass-card p-3 rounded-xl transition-all ${
                fontSize === size
                  ? "text-neon-cyan border-neon-cyan/50"
                  : "text-moon hover:text-neon-cyan"
              }`}
              title={`Font size: ${size}`}
            >
              <Type className={`w-4 h-4 ${size === "xl" ? "scale-125" : size === "md" ? "scale-90" : ""}`} />
            </button>
          ))}
        </div>

        {/* Chapter header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-10"
        >
          <Link
            href={`/novel/${slug}`}
            className="inline-flex items-center gap-2 text-moon/40 hover:text-neon-cyan transition-colors mb-6 text-sm"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Novel
          </Link>
          <h1
            className="text-3xl lg:text-4xl font-bold text-stardust mb-2"
            style={{ fontFamily: "Orbitron" }}
          >
            <span className="text-gradient">Chapter {chapterNum}</span>
          </h1>
          <h2 className="text-xl text-moon/50">{chapter.title}</h2>
        </motion.div>

        {/* Chapter content */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className={`glass-card rounded-2xl p-8 lg:p-12 mb-10 reader-content ${fontSizeClasses[fontSize]}`}
          style={{
            maxWidth: "100%",
          }}
        >
          {chapter.content.split("\n\n").map((paragraph, i) => (
            <motion.p
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 + i * 0.1 }}
            >
              {paragraph}
            </motion.p>
          ))}
        </motion.div>

        {/* Navigation */}
        <div className="flex items-center justify-between">
          {chapterNum > 1 ? (
            <Link
              href={`/novel/${slug}/chapter/${chapterNum - 1}`}
              className="glass-card px-6 py-3 rounded-xl text-moon hover:text-neon-cyan transition-all flex items-center gap-2"
            >
              <ChevronLeft className="w-5 h-5" />
              Previous Chapter
            </Link>
          ) : (
            <div />
          )}

          <div className="text-sm text-moon/30">
            Ch. {chapterNum} / {totalChapters}
          </div>

          {chapterNum < totalChapters ? (
            <Link
              href={`/novel/${slug}/chapter/${chapterNum + 1}`}
              className="neon-btn px-6 py-3 rounded-xl text-sm flex items-center gap-2"
            >
              Next Chapter
              <ChevronRight className="w-5 h-5" />
            </Link>
          ) : (
            <div />
          )}
        </div>
      </div>
    </div>
  );
}