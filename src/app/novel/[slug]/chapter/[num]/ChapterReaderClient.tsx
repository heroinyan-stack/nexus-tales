"use client";

import { useState } from "react";
import Link from "next/link";
import { ChevronLeft, ChevronRight, Sun, Moon, Type } from "lucide-react";

export default function ChapterReaderClient({
  content,
  novelSlug,
  chapterNum,
  totalChapters,
}: {
  content: string;
  novelSlug: string;
  chapterNum: number;
  totalChapters: number;
}) {
  const [darkMode, setDarkMode] = useState(true);
  const [fontSize, setFontSize] = useState<"md" | "lg" | "xl">("md");

  const fontSizeClasses = {
    md: "text-base",
    lg: "text-lg",
    xl: "text-xl",
  };

  return (
    <div className={darkMode ? "text-white" : "text-gray-900"}>
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

      {/* Chapter content */}
      <div
        className={`glass-card rounded-2xl p-8 lg:p-12 mb-10 ${
          darkMode ? "" : "bg-white/90 text-gray-900"
        } ${fontSizeClasses[fontSize]}`}
      >
        {content.split("\n\n").map((paragraph, i) => (
          <p key={i} className="mb-4 last:mb-0 leading-relaxed">
            {paragraph}
          </p>
        ))}
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-between">
        {chapterNum > 1 ? (
          <Link
            href={`/novel/${novelSlug}/chapter/${chapterNum - 1}`}
            className="glass-card px-6 py-3 rounded-xl text-moon hover:text-neon-cyan transition-all flex items-center gap-2"
          >
            <ChevronLeft className="w-5 h-5" />
            Previous
          </Link>
        ) : (
          <div />
        )}

        <div className="text-sm text-moon/30">
          {chapterNum} / {totalChapters}
        </div>

        {chapterNum < totalChapters ? (
          <Link
            href={`/novel/${novelSlug}/chapter/${chapterNum + 1}`}
            className="neon-btn px-6 py-3 rounded-xl text-sm flex items-center gap-2"
          >
            Next
            <ChevronRight className="w-5 h-5" />
          </Link>
        ) : (
          <div />
        )}
      </div>
    </div>
  );
}
