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

const FONTS: Record<FontFamily, string> = {
  sans: "font-sans",
  serif: "font-serif",
};

const LINE_HEIGHTS: Record<LineHeight, string> = {
  tight: "leading-tight",
  normal: "leading-relaxed",
  relaxed: "leading-loose",
};

interface ChapterReaderClientProps {
  // For static shell (passed even before content loads)
  novelSlug: string;
  chapterNum: number;
  totalChapters: number;
  novelTitle?: string;
  zone?: string;
  initialContent?: string; // optional, for SSG compatibility
}

export default function ChapterReaderClient({
  novelSlug,
  chapterNum,
  totalChapters,
  novelTitle = "",
  zone = "free",
  initialContent,
}: ChapterReaderClientProps) {
  // Chapter content — fetched client-side from Blob API
  const [content, setContent] = useState<string>(initialContent || "");
  const [loading, setLoading] = useState(!initialContent);
  const [error, setError] = useState<string | null>(null);

  // Reading progress
  const [progress, setProgress] = useState({ chapterNum, scrollPercent: 0 });

  // Settings drawer
  const [showSettings, setShowSettings] = useState(false);
  const [showChapters, setShowChapters] = useState(false);

  // Display settings
  const [theme, setTheme] = useState<Theme>("dark");
  const [fontSize, setFontSize] = useState(18);
  const [fontFamily, setFontFamily] = useState<FontFamily>("serif");
  const [lineHeight, setLineHeight] = useState<LineHeight>("normal");

  // Auth
  const { data: session } = useSession();

  const contentRef = useRef<HTMLDivElement>(null);
  const lastSavedRef = useRef({ chapterNum, scrollPercent: 0 });

  // Fetch chapter from Blob API
  useEffect(() => {
    if (initialContent) {
      setContent(initialContent);
      setLoading(false);
      return;
    }
    let cancelled = false;
    setLoading(true);
    setError(null);

    fetch(`/api/chapters/${encodeURIComponent(novelSlug)}/${chapterNum}`)
      .then((r) => {
        if (!r.ok) throw new Error("Chapter not found");
        return r.json();
      })
      .then((data) => {
        if (cancelled) return;
        setContent(data.content_en || data.content || "");
        setLoading(false);
      })
      .catch((err) => {
        if (cancelled) return;
        setError(err.message || "Failed to load chapter");
        setLoading(false);
      });

    return () => { cancelled = true; };
  }, [novelSlug, chapterNum, initialContent]);

  // Restore scroll position
  useEffect(() => {
    if (!contentRef.current) return;
    const saved = localStorage.getItem(`reading-progress-${novelSlug}`);
    if (saved) {
      try {
        const data = JSON.parse(saved);
        if (data.chapterNum === chapterNum) {
          const el = contentRef.current;
          const scrollPct = data.scrollPercent / 100;
          const targetY = scrollPct * el.scrollHeight;
          el.scrollTop = targetY;
        }
      } catch {}
    }
  }, [content, chapterNum, novelSlug]);

  const saveProgress = useCallback(
    (chNum: number, pct: number) => {
      if (typeof window === "undefined") return;
      localStorage.setItem(
        `reading-progress-${novelSlug}`,
        JSON.stringify({ chapterNum: chNum, scrollPercent: pct })
      );
    },
    [novelSlug]
  );

  // Track scroll progress
  const handleScroll = useCallback(() => {
    if (!contentRef.current) return;
    const el = contentRef.current;
    const scrollPct = Math.round((el.scrollTop / (el.scrollHeight - el.clientHeight)) * 100);
    setProgress({ chapterNum, scrollPercent: scrollPct });
    if (el.scrollHeight > el.clientHeight) {
      saveProgress(chapterNum, scrollPct);
    }
  }, [chapterNum, saveProgress]);

  useEffect(() => {
    const el = contentRef.current;
    if (!el) return;
    el.addEventListener("scroll", handleScroll, { passive: true });
    return () => el.removeEventListener("scroll", handleScroll);
  }, [handleScroll]);

  const wordCount = content ? content.split(/\s+/).length : 0;

  // Navigate chapters
  const prevChapter = chapterNum > 1 ? chapterNum - 1 : null;
  const nextChapter = chapterNum < totalChapters ? chapterNum + 1 : null;

  const navigateTo = (num: number) => {
    const el = contentRef.current;
    if (el) el.scrollTop = 0;
    lastSavedRef.current = { chapterNum: num, scrollPercent: 0 };
    window.location.href = `/novel/${novelSlug}/chapter/${num}`;
  };

  // Theme/typography classes
  const themeStyle = THEMES[theme];
  const fontClass = FONTS[fontFamily];
  const lhClass = LINE_HEIGHTS[lineHeight];

  return (
    <div className={`min-h-screen ${themeStyle.bg} ${themeStyle.text} ${fontClass} flex flex-col`}>
      {/* Fixed top bar */}
      <div className={`sticky top-0 z-20 flex items-center justify-between px-4 py-3 border-b ${themeStyle.border} ${themeStyle.bg} backdrop-blur-sm`}>
        <Link
          href={`/novel/${novelSlug}`}
          className={`flex items-center gap-1 text-sm ${themeStyle.muted} hover:${themeStyle.text} transition-colors`}
        >
          <ChevronLeft size={16} />
          <span className="hidden sm:inline">Back</span>
        </Link>

        <div className="flex items-center gap-2">
          {/* Progress */}
          <span className={`text-xs ${themeStyle.muted}`}>
            {progress.scrollPercent}%
          </span>

          <button
            onClick={() => setShowChapters(!showChapters)}
            className={`p-1.5 rounded-lg ${themeStyle.border} hover:bg-white/5 transition-colors`}
            title="Chapters"
          >
            <List size={16} />
          </button>
          <button
            onClick={() => setShowSettings(!showSettings)}
            className={`p-1.5 rounded-lg ${themeStyle.border} hover:bg-white/5 transition-colors`}
            title="Settings"
          >
            <Settings size={16} />
          </button>
        </div>
      </div>

      {/* Settings drawer */}
      {showSettings && (
        <div className={`${themeStyle.bg} border-b ${themeStyle.border} px-4 py-3 space-y-3`}>
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Font Size</span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setFontSize((s) => Math.max(14, s - 2))}
                className={`p-1.5 rounded ${themeStyle.border}`}
              >
                <Minus size={14} />
              </button>
              <span className="text-sm w-8 text-center">{fontSize}px</span>
              <button
                onClick={() => setFontSize((s) => Math.min(24, s + 2))}
                className={`p-1.5 rounded ${themeStyle.border}`}
              >
                <Plus size={14} />
              </button>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Theme</span>
            <div className="flex gap-2">
              {(["dark", "light", "sepia"] as Theme[]).map((t) => (
                <button
                  key={t}
                  onClick={() => setTheme(t)}
                  className={`px-3 py-1 text-xs rounded capitalize ${
                    theme === t ? "bg-purple-600 text-white" : `${themeStyle.border}`
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Font</span>
            <div className="flex gap-2">
              {([["serif", "Serif"], ["sans", "Sans"]] as [FontFamily, string][]).map(
                ([f, label]) => (
                  <button
                    key={f}
                    onClick={() => setFontFamily(f)}
                    className={`px-3 py-1 text-xs rounded ${
                      fontFamily === f ? "bg-purple-600 text-white" : `${themeStyle.border}`
                    }`}
                  >
                    {label}
                  </button>
                )
              )}
            </div>
          </div>
        </div>
      )}

      {/* Chapters drawer */}
      {showChapters && (
        <ChapterDrawer
          novelSlug={novelSlug}
          currentChapter={chapterNum}
          totalChapters={totalChapters}
          onSelect={navigateTo}
          themeStyle={themeStyle}
          theme={theme}
        />
      )}

      {/* Main content area */}
      <div className="flex-1 flex">
        {/* Mobile chapter nav */}
        <div className="flex-1 overflow-auto" ref={contentRef}>
          <div className="max-w-2xl mx-auto px-4 sm:px-6 py-8">
            {loading ? (
              <div className="space-y-4 animate-pulse">
                {[...Array(8)].map((_, i) => (
                  <div
                    key={i}
                    className={`h-4 ${themeStyle.muted} rounded`}
                    style={{ width: `${70 + Math.random() * 30}%` }}
                  />
                ))}
              </div>
            ) : error ? (
              <div className="text-center py-16">
                <p className={`${themeStyle.muted} text-lg mb-4`}>{error}</p>
                <button
                  onClick={() => window.location.reload()}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg"
                >
                  Retry
                </button>
              </div>
            ) : (
              <article
                className={`prose-custom ${lhClass}`}
                style={{ fontSize: `${fontSize}px` }}
                dangerouslySetInnerHTML={{ __html: formatContent(content) }}
              />
            )}
          </div>
        </div>
      </div>

      {/* Bottom navigation */}
      <div className={`sticky bottom-0 border-t ${themeStyle.border} ${themeStyle.bg} backdrop-blur-sm`}>
        <div className="max-w-2xl mx-auto flex items-center justify-between px-4 py-3">
          {prevChapter ? (
            <button
              onClick={() => navigateTo(prevChapter)}
              className={`flex items-center gap-1 text-sm px-3 py-1.5 rounded-lg border ${themeStyle.border} hover:bg-white/5 transition-colors`}
            >
              <ChevronLeft size={16} />
              <span className="hidden sm:inline">Ch.{prevChapter}</span>
              <span className="sm:hidden">Prev</span>
            </button>
          ) : (
            <div />
          )}

          <span className={`text-xs ${themeStyle.muted}`}>
            {chapterNum} / {totalChapters} · {wordCount.toLocaleString()} words
          </span>

          {nextChapter ? (
            <button
              onClick={() => navigateTo(nextChapter)}
              className={`flex items-center gap-1 text-sm px-3 py-1.5 rounded-lg border ${themeStyle.border} hover:bg-white/5 transition-colors`}
            >
              <span className="hidden sm:inline">Ch.{nextChapter}</span>
              <span className="sm:hidden">Next</span>
              <ChevronRight size={16} />
            </button>
          ) : (
            <div />
          )}
        </div>
      </div>
    </div>
  );
}

// Format content: paragraph breaks, no raw newlines, basic cleanup
function formatContent(text: string): string {
  if (!text) return "";
  return text
    .replace(/\r\n/g, "\n")
    .split(/\n\n+/)
    .map((p) => {
      const trimmed = p.trim();
      if (!trimmed) return "";
      if (trimmed.startsWith("<") && trimmed.endsWith(">")) return trimmed;
      return `<p>${trimmed.replace(/\n/g, "<br/>")}</p>`;
    })
    .filter(Boolean)
    .join("");
}

// Chapters drawer
function ChapterDrawer({
  novelSlug,
  currentChapter,
  totalChapters,
  onSelect,
  themeStyle,
  theme,
}: {
  novelSlug: string;
  currentChapter: number;
  totalChapters: number;
  onSelect: (n: number) => void;
  themeStyle: { bg: string; text: string; muted: string; border: string };
  theme: Theme;
}) {
  const [chapters, setChapters] = useState<{ num: number; title_en: string }[]>([]);

  useEffect(() => {
    // Fetch chapter list from /api/chapters-list/[slug] or fall back to localStorage
    fetch(`/api/novels/${encodeURIComponent(novelSlug)}`)
      .then((r) => r.ok ? r.json() : null)
      .then((data) => {
        if (data?.chapters) setChapters(data.chapters);
      })
      .catch(() => {});
  }, [novelSlug]);

  return (
    <div className={`${themeStyle.bg} border-b ${themeStyle.border} max-h-64 overflow-y-auto`}>
      <div className="px-4 py-2 grid grid-cols-4 gap-1">
        {[...Array(totalChapters)].map((_, i) => {
          const num = i + 1;
          const isActive = num === currentChapter;
          return (
            <button
              key={num}
              onClick={() => onSelect(num)}
              className={`px-2 py-1 text-xs rounded text-center transition-colors ${
                isActive
                  ? "bg-purple-600 text-white"
                  : `${themeStyle.border} hover:bg-white/5`
              }`}
            >
              {num}
            </button>
          );
        })}
      </div>
    </div>
  );
}
