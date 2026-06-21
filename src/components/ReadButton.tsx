"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import Link from "next/link";
import { BookOpen, Loader2 } from "lucide-react";

function getLocalProgress(slug: string): { chapterNum: number; finished: boolean; updatedAt: number } | null {
  try {
    const raw = localStorage.getItem(`reading_progress_${slug}`);
    if (!raw) return null;
    const data = JSON.parse(raw);
    if (typeof data.chapterNum !== "number") return null;
    return { chapterNum: data.chapterNum, finished: !!data.finished, updatedAt: data.updatedAt || 0 };
  } catch {
    return null;
  }
}

export default function ReadButton({
  slug,
  zone,
}: {
  slug: string;
  zone: string;
}) {
  const { data: session, status } = useSession();
  const [progress, setProgress] = useState<{
    chapterNum: number;
    finished: boolean;
  } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check localStorage first (instant, no network)
    const local = getLocalProgress(slug);

    if (status !== "authenticated" || !(session?.user as any)?.id) {
      // Guest user: use localStorage only
      if (local && !local.finished) {
        setProgress({ chapterNum: local.chapterNum, finished: false });
      }
      setLoading(false);
      return;
    }

    // Logged-in user: fetch API, fallback to localStorage if API is newer
    fetch(`/api/progress?novelSlug=${slug}`)
      .then((r) => r.json())
      .then((data) => {
        if (data.progress) {
          setProgress({
            chapterNum: data.progress.chapterNum,
            finished: data.progress.finished,
          });
        } else if (local && !local.finished) {
          // No server record yet, use localStorage fallback
          setProgress({ chapterNum: local.chapterNum, finished: false });
        }
      })
      .catch(() => {
        // Network error — fallback to localStorage
        if (local && !local.finished) {
          setProgress({ chapterNum: local.chapterNum, finished: false });
        }
      })
      .finally(() => setLoading(false));
  }, [slug, session, status]);

  if (status === "loading" || loading) {
    return (
      <span className="block w-full neon-btn py-3 rounded-xl text-sm font-bold text-center opacity-60 cursor-wait">
        <Loader2 className="w-4 h-4 animate-spin inline mr-2" />
        Loading...
      </span>
    );
  }

  if (progress && !progress.finished) {
    return (
      <Link
        href={`/novel/${slug}/chapter/${progress.chapterNum}`}
        className="block w-full neon-btn py-3 rounded-xl text-sm font-bold text-center"
      >
        <BookOpen className="w-4 h-4 inline mr-2" />
        Continue Reading (Ch. {progress.chapterNum})
      </Link>
    );
  }

  return (
    <Link
      href={`/novel/${slug}/chapter/1`}
      className="block w-full neon-btn py-3 rounded-xl text-sm font-bold text-center"
    >
      ▶ {zone === "vip" ? "Read Free Chapters" : "Start Reading"}
    </Link>
  );
}
