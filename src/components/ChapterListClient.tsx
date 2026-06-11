"use client";

import { useSession } from "next-auth/react";
import Link from "next/link";
import { Lock, Unlock } from "lucide-react";

interface Chapter {
  num: number;
  title_en: string;
}

interface ChapterListClientProps {
  slug: string;
  zone: string;
  chapters: Chapter[];
}

export default function ChapterListClient({
  slug,
  zone,
  chapters,
}: ChapterListClientProps) {
  const { data: session } = useSession();
  const isPremium = session && ["premium", "ultimate", "admin"].includes(
    (session.user as any)?.role || ""
  );

  // VIP zone: chapters 1-5 always free; 6+ require premium
  const isVip = zone === "vip";

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
      {chapters.map((ch) => {
        const locked = isVip && ch.num > 5 && !isPremium;
        return (
          <Link
            key={ch.num}
            href={locked ? `/login?callbackUrl=/novel/${slug}/chapter/${ch.num}` : `/novel/${slug}/chapter/${ch.num}`}
            className={`flex items-center justify-between p-4 rounded-xl glass-card hover:border-neon-cyan/30 transition-all group ${
              locked ? "opacity-50 cursor-not-allowed" : ""
            }`}
            onClick={(e) => locked && e.preventDefault()}
          >
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-stardust group-hover:text-neon-cyan transition-colors flex items-center gap-2">
                Ch. {ch.num}
                {isVip && ch.num <= 5 && (
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-neon-cyan/10 text-neon-cyan font-bold">
                    FREE
                  </span>
                )}
                {locked && (
                  <Lock className="w-3 h-3 text-moon/30" />
                )}
              </div>
              <div className="text-xs text-moon/40 mt-0.5 truncate">
                {ch.title_en}
              </div>
            </div>
            <div className="ml-2">
              {locked ? (
                <Lock className="w-4 h-4 text-moon/30" />
              ) : (
                <Unlock className="w-4 h-4 text-neon-cyan/50 group-hover:text-neon-cyan transition-colors" />
              )}
            </div>
          </Link>
        );
      })}
    </div>
  );
}
