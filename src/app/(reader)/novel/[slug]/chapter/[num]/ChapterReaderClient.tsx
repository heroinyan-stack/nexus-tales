"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import Link from "next/link";
import { useSession } from "next-auth/react";
import { ChevronLeft, ChevronRight, ChevronDown, Settings, List, X, Minus, Plus, ArrowLeft, Home } from "lucide-react";

type Theme = "dark" | "light" | "sepia";
type FontFamily = "sans" | "serif";
type LineHeight = "tight" | "normal" | "relaxed";

const THEMES: Record<Theme, { bg: string; text: string; muted: string; border: string }> = {
  dark: {
    bg: "bg-[#0a0a0f]",
    text: "text-[#e0d8ff]",
    muted: "text-white/40",
    border: "border-white/10",
  },
  light: {
    bg: "bg-[#fafaf9]",
    text: "text-[#1c1917]",
    muted: "text-stone-400",
    border: "border-stone-200",
  },
  sepia: {
    bg: "bg-[#f4ecd8]",
    text: "text-[#43302a]",
    muted: "text-[#6b5344]",
    border: "border-[#d4c4a8]",
  },
};

const FONT_FAMILY: Record<FontFamily, string> = {
  sans: "font-sans",
  serif: "font-serif",
};

const LINE_HEIGHTS: Record<LineHeight, string> = {
  tight: "leading-relaxed",
  normal: "leading-loose",
  relaxed: "leading-[2.2]",
};

export default function ChapterReaderClient({
  content,
  novelSlug,
  chapterNum,
  totalChapters,
  novelTitle = "",
  zone = "free",
}: {
  content: string;
  novelSlug: string;
  chapterNum: number;
  totalChapters: number;
  novelTitle?: string;
  zone?: string;
}) {
  const { data: session } = useSession();
  const [theme, setTheme] = useState<Theme>("dark");
  const [fontFamily, setFontFamily] = useState<FontFamily>("serif");
  const [fontSize, setFontSize] = useState(18);
  const [lineHeight, setLineHeight] = useState<LineHeight>("normal");
  const [showSettings, setShowSettings] = useState(false);
  const [showChapterList, setShowChapterList] = useState(false);
  const [progress, setProgress] = useState(0);
  const [isImmersive, setIsImmersive] = useState(false);
  const contentRef = useRef<HTMLDivElement>(null);
  const lastSavedRef = useRef({ chapterNum, scrollPercent: 0 });
  const saveTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Calculate reading time
  const wordCount = content.split(/\s+/).length;
  const readingTime = Math.ceil(wordCount / 200);

  // Save reading progress — always localStorage, +API when logged in (debounced)
  const saveProgress = useCallback((chNum: number, scrollPct: number) => {
    if (chNum === lastSavedRef.current.chapterNum && 
        Math.abs(scrollPct - lastSavedRef.current.scrollPercent) < 5) return;

    lastSavedRef.current = { chapterNum: chNum, scrollPercent: scrollPct };

    // Always save to localStorage (guest + logged-in)
    try {
      localStorage.setItem(`reading_progress_${novelSlug}`, JSON.stringify({
        chapterNum: chNum,
        scrollPercent: Math.round(scrollPct),
        finished: scrollPct > 90,
        updatedAt: Date.now(),
      }));
    } catch {} // quota exceeded or private browsing

    // Also POST to API for logged-in users
    if (!(session?.user as any)?.id) return;

    if (saveTimerRef.current) clearTimeout(saveTimerRef.current);
    saveTimerRef.current = setTimeout(() => {
      fetch("/api/progress", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          novelSlug,
          chapterNum: chNum,
          scrollPercent: Math.round(scrollPct),
          finished: scrollPct > 90,
        }),
      }).catch(() => {});
    }, 2000);
  }, [session, novelSlug]);

  // Track reading progress
  useEffect(() => {
    const handleScroll = () => {
      if (!contentRef.current) return;
      const scrollTop = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const scrollPercent = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
      const pct = Math.min(100, Math.max(0, scrollPercent));
      setProgress(pct);
      saveProgress(chapterNum, pct);
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, [chapterNum, saveProgress]);

  // Save progress on chapter change
  useEffect(() => {
    saveProgress(chapterNum, 0);
    window.scrollTo(0, 0);
  }, [chapterNum]);

  // Save on leaving (localStorage sync + API beacon)
  useEffect(() => {
    const handleBeforeUnload = () => {
      // Always flush to localStorage
      try {
        localStorage.setItem(`reading_progress_${novelSlug}`, JSON.stringify({
          chapterNum,
          scrollPercent: Math.round(progress),
          finished: progress > 90,
          updatedAt: Date.now(),
        }));
      } catch {}
      // API beacon for logged-in users
      if ((session?.user as any)?.id) {
        if (saveTimerRef.current) clearTimeout(saveTimerRef.current);
        navigator.sendBeacon("/api/progress", JSON.stringify({
          novelSlug,
          chapterNum,
          scrollPercent: Math.round(progress),
          finished: progress > 90,
        }));
      }
    };
    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => window.removeEventListener("beforeunload", handleBeforeUnload);
  }, [chapterNum, progress, novelSlug]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "ArrowLeft" && chapterNum > 1) {
        window.location.href = `/novel/${novelSlug}/chapter/${chapterNum - 1}`;
      } else if (e.key === "ArrowRight" && chapterNum < totalChapters) {
        window.location.href = `/novel/${novelSlug}/chapter/${chapterNum + 1}`;
      } else if (e.key === "Escape") {
        setShowSettings(false);
        setShowChapterList(false);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [chapterNum, totalChapters, novelSlug]);

  // Generate chapter list
  const chapters = Array.from({ length: totalChapters }, (_, i) => i + 1);

  // Theme colors
  const colors = THEMES[theme];

  return (
    <div className={`min-h-screen transition-colors duration-300 ${colors.bg}`}>
      {/* Progress bar */}
      <div className="fixed top-0 left-0 right-0 h-1 z-50 bg-black/20">
        <div
          className="h-full bg-gradient-to-r from-[#00f0ff] to-[#b44dff] transition-all duration-150"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Top bar: back button + full screen toggle */}
      {!isImmersive && (
        <div className="fixed top-4 left-4 right-4 z-40 flex items-center justify-between">
          <Link
            href={`/novel/${novelSlug}`}
            className={`flex items-center gap-1.5 ${colors.bg} ${colors.text} ${colors.border} border px-3 py-1.5 rounded-full text-xs opacity-60 hover:opacity-100 transition-opacity`}
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Novel</span>
          </Link>
          <button
            onClick={() => setIsImmersive(true)}
            className={`${colors.bg} ${colors.text} ${colors.border} border px-3 py-1.5 rounded-full text-xs opacity-60 hover:opacity-100 transition-opacity`}
          >
            Full Screen
          </button>
        </div>
      )}

      {/* Main content area */}
      <div
        ref={contentRef}
        className={`max-w-2xl mx-auto px-6 pt-16 pb-32 ${
          isImmersive ? "pt-8" : ""
        }`}
      >
        {/* Reading time & progress */}
        <div
          className={`flex items-center justify-between mb-8 text-xs ${colors.muted}`}
        >
          <span>{readingTime} min read</span>
          <span>
            {chapterNum} / {totalChapters}
          </span>
        </div>

        {/* Chapter content */}
        <article
          className={`${colors.text} ${FONT_FAMILY[fontFamily]} ${LINE_HEIGHTS[lineHeight]}`}
          style={{ fontSize: `${fontSize}px` }}
        >
          {content.split("\n\n").map((paragraph, i) => (
            <p
              key={i}
              className="mb-6 text-indent-8"
              style={{ textIndent: "2rem" }}
            >
              {paragraph.trim()}
            </p>
          ))}
        </article>
      </div>

      {/* Bottom navigation bar */}
      <div
        className={`fixed bottom-0 left-0 right-0 z-40 ${colors.bg} ${colors.border} border-t`}
      >
        {/* Chapter navigation */}
        <div className="flex items-center justify-between px-4 py-3 max-w-2xl mx-auto">
          {chapterNum > 1 ? (
            <Link
              href={`/novel/${novelSlug}/chapter/${chapterNum - 1}`}
              className={`flex items-center gap-1 ${colors.text} opacity-60 hover:opacity-100 transition-opacity`}
            >
              <ChevronLeft className="w-5 h-5" />
              <span className="text-sm">Prev</span>
            </Link>
          ) : (
            <div />
          )}

          {/* Center controls */}
          <div className="flex items-center gap-3">
            {/* Back to novel */}
            <Link
              href={`/novel/${novelSlug}`}
              className={`flex items-center gap-1 ${colors.text} opacity-60 hover:opacity-100 transition-opacity`}
            >
              <Home className="w-4 h-4" />
              <span className="text-xs">Novel</span>
            </Link>

            {/* Chapter list button */}
            <button
              onClick={() => setShowChapterList(true)}
              className={`flex items-center gap-1 ${colors.text} opacity-60 hover:opacity-100 transition-opacity`}
            >
              <span className="text-sm font-medium">Ch. {chapterNum}</span>
              <ChevronDown className="w-4 h-4" />
            </button>

            {/* Settings button */}
            <button
              onClick={() => setShowSettings(true)}
              className={`p-2 ${colors.text} opacity-60 hover:opacity-100 transition-opacity`}
            >
              <Settings className="w-5 h-5" />
            </button>
          </div>

          {chapterNum < totalChapters ? (
            <Link
              href={`/novel/${novelSlug}/chapter/${chapterNum + 1}`}
              className={`flex items-center gap-1 ${colors.text} opacity-60 hover:opacity-100 transition-opacity`}
            >
              <span className="text-sm">Next</span>
              <ChevronRight className="w-5 h-5" />
            </Link>
          ) : (
            <div />
          )}
        </div>
      </div>

      {/* Settings panel */}
      {showSettings && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
          onClick={() => setShowSettings(false)}
        >
          <div
            className={`${colors.bg} ${colors.text} ${colors.border} border rounded-2xl p-6 w-full max-w-sm mx-4 shadow-2xl`}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="font-semibold text-lg">Reading Settings</h3>
              <button
                onClick={() => setShowSettings(false)}
                className="opacity-60 hover:opacity-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Theme */}
            <div className="mb-6">
              <label className={`text-xs ${colors.muted} mb-2 block`}>
                Theme
              </label>
              <div className="flex gap-2">
                {(["dark", "light", "sepia"] as Theme[]).map((t) => (
                  <button
                    key={t}
                    onClick={() => setTheme(t)}
                    className={`flex-1 py-2.5 rounded-lg border transition-all ${
                      theme === t
                        ? "border-[#00f0ff] bg-[#00f0ff]/10"
                        : colors.border
                    }`}
                  >
                    <span className="text-sm capitalize">{t}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Font family */}
            <div className="mb-6">
              <label className={`text-xs ${colors.muted} mb-2 block`}>
                Font Style
              </label>
              <div className="flex gap-2">
                {(["sans", "serif"] as FontFamily[]).map((f) => (
                  <button
                    key={f}
                    onClick={() => setFontFamily(f)}
                    className={`flex-1 py-2.5 rounded-lg border transition-all ${
                      fontFamily === f
                        ? "border-[#00f0ff] bg-[#00f0ff]/10"
                        : colors.border
                    } ${FONT_FAMILY[f]}`}
                  >
                    <span className="text-sm">{f === "sans" ? "Modern" : "Classic"}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Font size */}
            <div className="mb-6">
              <label className={`text-xs ${colors.muted} mb-2 block`}>
                Font Size: {fontSize}px
              </label>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => setFontSize((s) => Math.max(14, s - 2))}
                  className={`${colors.border} border w-10 h-10 rounded-lg flex items-center justify-center hover:bg-white/5`}
                >
                  <Minus className="w-4 h-4" />
                </button>
                <div className="flex-1 h-2 rounded-full bg-white/10 relative">
                  <div
                    className="absolute h-full bg-gradient-to-r from-[#00f0ff] to-[#b44dff] rounded-full"
                    style={{ width: `${((fontSize - 14) / 10) * 100}%` }}
                  />
                </div>
                <button
                  onClick={() => setFontSize((s) => Math.min(24, s + 2))}
                  className={`${colors.border} border w-10 h-10 rounded-lg flex items-center justify-center hover:bg-white/5`}
                >
                  <Plus className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Line height */}
            <div>
              <label className={`text-xs ${colors.muted} mb-2 block`}>
                Line Spacing
              </label>
              <div className="flex gap-2">
                {(["tight", "normal", "relaxed"] as LineHeight[]).map((l) => (
                  <button
                    key={l}
                    onClick={() => setLineHeight(l)}
                    className={`flex-1 py-2.5 rounded-lg border transition-all ${
                      lineHeight === l
                        ? "border-[#00f0ff] bg-[#00f0ff]/10"
                        : colors.border
                    }`}
                  >
                    <span className="text-sm capitalize">{l}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Chapter list panel */}
      {showChapterList && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
          onClick={() => setShowChapterList(false)}
        >
          <div
            className={`${colors.bg} ${colors.text} ${colors.border} border rounded-2xl w-full max-w-md mx-4 max-h-[70vh] overflow-hidden shadow-2xl`}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between p-4 border-b border-white/10">
              <h3 className="font-semibold">Chapters</h3>
              <button
                onClick={() => setShowChapterList(false)}
                className="opacity-60 hover:opacity-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="overflow-y-auto max-h-[calc(70vh-60px)]">
              {chapters.map((num) => (
                <Link
                  key={num}
                  href={`/novel/${novelSlug}/chapter/${num}`}
                  className={`block px-4 py-3 hover:bg-white/5 transition-colors ${
                    num === chapterNum ? "bg-[#00f0ff]/10 text-[#00f0ff]" : ""
                  }`}
                >
                  <span className="text-sm">Chapter {num}</span>
                </Link>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
