"use client";

import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import {
  User, Crown, Zap, Calendar, CreditCard, Shield,
  BookOpen, Clock, Bookmark, Trash2, Bell,
  ChevronRight, Loader2, CheckCircle, AlertCircle,
} from "lucide-react";
import Link from "next/link";

interface ReadingProgress {
  id: string;
  novelSlug: string;
  chapterNum: number;
  scrollPercent: number;
  finished: boolean;
  updatedAt: string;
  startedAt: string;
}

interface NovelInfo {
  slug: string;
  title_en: string;
  total_chapters: number;
  cover_url: string;
  genre: string;
}

export default function ProfilePage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [loadingPortal, setLoadingPortal] = useState(false);
  const [bookshelf, setBookshelf] = useState<(ReadingProgress & { novel?: NovelInfo })[]>([]);
  const [loadingShelf, setLoadingShelf] = useState(true);
  const [removing, setRemoving] = useState<string | null>(null);

  // Load bookshelf + novel info
  useEffect(() => {
    if (!(session?.user as any)?.id) return;

    async function load() {
      try {
        // Fetch progress and novels in parallel
        const [progressRes, novelsRes] = await Promise.all([
          fetch("/api/progress"),
          fetch("/api/novels"),
        ]);
        const [progressData, novelsData] = await Promise.all([
          progressRes.json(),
          novelsRes.json(),
        ]);

        const progress = (progressData.progress || []) as ReadingProgress[];
        const novels = (novelsData.novels || []) as NovelInfo[];
        const novelMap = new Map(novels.map((n) => [n.slug, n]));

        setBookshelf(
          progress.map((p) => ({
            ...p,
            novel: novelMap.get(p.novelSlug),
          }))
        );
      } catch (err) {
        console.error("Failed to load bookshelf:", err);
      } finally {
        setLoadingShelf(false);
      }
    }

    load();
  }, [session]);

  if (status === "loading") {
    return (
      <div className="min-h-screen pt-24 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-neon-cyan" />
      </div>
    );
  }

  if (!session) {
    router.push("/login?callbackUrl=/profile");
    return null;
  }

  const user = session.user as any;
  const role = user.role || "free";
  const subStatus = user.subscription as string | null;
  const expiresAt = user.subExpiresAt as string | null;

  const roleConfig: Record<string, { name: string; icon: any; color: string; emoji: string }> = {
    free: { name: "Free", icon: BookOpen, color: "text-moon/50", emoji: "📚" },
    premium: { name: "Premium", icon: Zap, color: "text-neon-cyan", emoji: "⚡️" },
    ultimate: { name: "Ultimate", icon: Crown, color: "text-neon-purple", emoji: "👑" },
    admin: { name: "Admin", icon: Shield, color: "text-neon-cyan", emoji: "🛡️" },
  };

  const rc = roleConfig[role] || roleConfig.free;

  async function handleManageBilling() {
    setLoadingPortal(true);
    const res = await fetch("/api/payment/billing-portal", { method: "POST" });
    const data = await res.json();
    if (data.url) router.push(data.url);
    setLoadingPortal(false);
  }

  async function handleRemove(novelSlug: string) {
    setRemoving(novelSlug);
    await fetch(`/api/progress?novelSlug=${novelSlug}`, { method: "DELETE" });
    setBookshelf((prev) => prev.filter((b) => b.novelSlug !== novelSlug));
    setRemoving(null);
  }

  const currentlyReading = bookshelf.filter((b) => !b.finished);
  const finishedReading = bookshelf.filter((b) => b.finished);

  return (
    <div className="min-h-screen pt-24 pb-16 px-6">
      <div className="max-w-3xl mx-auto">
        {/* Profile Header */}
        <div className="glass-card rounded-2xl p-8 mb-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-neon-cyan to-purple-500 flex items-center justify-center text-2xl font-bold text-abyss shrink-0">
              {(user.name?.[0] || user.email?.[0] || "U").toUpperCase()}
            </div>
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-stardust">
                {user.name || "Reader"}
              </h1>
              <p className="text-sm text-moon/40">{user.email}</p>
            </div>
            <div className={`flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 border border-white/10 ${rc.color}`}>
              <span className="text-lg">{rc.emoji}</span>
              <rc.icon className="w-4 h-4" />
              <span className="font-bold text-sm">{rc.name}</span>
            </div>
          </div>
        </div>

        {/* Subscription Info */}
        {role !== "free" && (
          <div className="glass-card rounded-2xl p-6 mb-6 space-y-4">
            <h2 className="text-lg font-bold text-stardust flex items-center gap-2">
              <CreditCard className="w-5 h-5 text-neon-cyan" />
              Subscription
            </h2>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="p-3 rounded-xl bg-white/5">
                <div className="text-xs text-moon/40 mb-1">Plan</div>
                <div className="font-bold text-stardust text-sm">{rc.name}</div>
              </div>
              <div className="p-3 rounded-xl bg-white/5">
                <div className="text-xs text-moon/40 mb-1">Status</div>
                <div className="flex items-center gap-1.5">
                  {subStatus === "active" ? (
                    <CheckCircle className="w-3 h-3 text-emerald-400" />
                  ) : subStatus === "past_due" ? (
                    <AlertCircle className="w-3 h-3 text-red-400" />
                  ) : (
                    <Clock className="w-3 h-3 text-yellow-400" />
                  )}
                  <span className="font-bold text-stardust text-sm capitalize">
                    {subStatus || "unknown"}
                  </span>
                </div>
              </div>
              <div className="p-3 rounded-xl bg-white/5">
                <div className="text-xs text-moon/40 mb-1">Expires</div>
                <div className="font-bold text-stardust text-sm">
                  {expiresAt
                    ? new Date(expiresAt).toLocaleDateString("en-US", {
                        month: "short",
                        day: "numeric",
                      })
                    : "—"}
                </div>
              </div>
              <div className="p-3 rounded-xl bg-white/5">
                <div className="text-xs text-moon/40 mb-1">Price</div>
                <div className="font-bold text-stardust text-sm">
                  {role === "ultimate" ? "$29.99" : "$19.99"}/30d
                </div>
              </div>
            </div>
            <button
              onClick={() => router.push("/pricing")}
              className="px-5 py-2.5 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 text-sm text-moon transition-all flex items-center gap-2"
            >
              <CreditCard className="w-4 h-4" />
              Renew Subscription
            </button>
          </div>
        )}

        {/* 📚 My Bookshelf */}
        <div className="glass-card rounded-2xl p-6 mb-6 space-y-4">
          <h2 className="text-lg font-bold text-stardust flex items-center gap-2">
            <Bookmark className="w-5 h-5 text-neon-cyan" />
            My Bookshelf
          </h2>

          {loadingShelf ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-6 h-6 animate-spin text-neon-cyan" />
            </div>
          ) : bookshelf.length === 0 ? (
            <div className="text-center py-8">
              <BookOpen className="w-12 h-12 text-moon/20 mx-auto mb-3" />
              <p className="text-moon/40 text-sm mb-3">Your bookshelf is empty</p>
              <Link
                href="/novels"
                className="inline-flex items-center gap-2 text-sm text-neon-cyan hover:text-neon-purple transition-colors"
              >
                Browse Novels <ChevronRight className="w-4 h-4" />
              </Link>
            </div>
          ) : (
            <>
              {/* Currently Reading */}
              {currentlyReading.length > 0 && (
                <div className="space-y-3">
                  <h3 className="text-sm font-semibold text-moon/60 flex items-center gap-2">
                    <BookOpen className="w-4 h-4" />
                    Currently Reading ({currentlyReading.length})
                  </h3>
                  {currentlyReading.map((item) => (
                    <BookshelfItem
                      key={item.id}
                      item={item}
                      onRemove={handleRemove}
                      isRemoving={removing === item.novelSlug}
                    />
                  ))}
                </div>
              )}

              {/* Finished */}
              {finishedReading.length > 0 && (
                <div className="space-y-3 pt-4 border-t border-white/5">
                  <h3 className="text-sm font-semibold text-moon/60 flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-emerald-400" />
                    Finished ({finishedReading.length})
                  </h3>
                  {finishedReading.map((item) => (
                    <BookshelfItem
                      key={item.id}
                      item={item}
                      onRemove={handleRemove}
                      isRemoving={removing === item.novelSlug}
                      isFinished
                    />
                  ))}
                </div>
              )}
            </>
          )}
        </div>

        {/* Settings */}
        <div className="glass-card rounded-2xl p-6 mb-6 space-y-4">
          <h2 className="text-lg font-bold text-stardust flex items-center gap-2">
            🔧 Settings
          </h2>
          <div className="space-y-2">
            {[
              { icon: BookOpen, label: "Reading Theme", desc: "Dark • Cyan" },
              { icon: Bell, label: "Notifications", desc: "Enabled" },
            ].map((item, i) => (
              <div
                key={i}
                className="flex items-center justify-between p-3 rounded-xl hover:bg-white/5 transition-colors cursor-pointer"
              >
                <div className="flex items-center gap-3">
                  <item.icon className="w-4 h-4 text-moon/40" />
                  <div>
                    <div className="text-sm font-medium text-stardust">{item.label}</div>
                    <div className="text-xs text-moon/30">{item.desc}</div>
                  </div>
                </div>
                <ChevronRight className="w-4 h-4 text-moon/20" />
              </div>
            ))}
          </div>
        </div>

        {/* Upgrade upsell */}
        {role === "free" && (
          <div className="glass-card rounded-2xl p-6 mb-6 border-neon-cyan/20">
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div>
                <h3 className="font-bold text-stardust">Unlock Unlimited Reading</h3>
                <p className="text-xs text-moon/40 mt-1">
                  Premium $19.99/30 days — buy once, read for a month
                </p>
              </div>
              <Link
                href="/pricing"
                className="neon-btn px-5 py-2.5 rounded-xl text-sm font-bold"
              >
                Upgrade Now
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Bookshelf item component
function BookshelfItem({
  item,
  onRemove,
  isRemoving,
  isFinished,
}: {
  item: ReadingProgress & { novel?: NovelInfo };
  onRemove: (slug: string) => void;
  isRemoving: boolean;
  isFinished?: boolean;
}) {
  const novel = item.novel;
  const progressPct = item.finished
    ? 100
    : Math.min(100, Math.round(
        (item.chapterNum / (novel?.total_chapters || item.chapterNum || 1)) * 100
      ));

  return (
    <div className="flex items-center gap-4 p-3 rounded-xl bg-white/5 hover:bg-white/8 transition-colors group">
      <div className="w-10 h-14 rounded-lg bg-gradient-to-br from-neon-cyan/20 to-purple-500/20 flex items-center justify-center shrink-0 overflow-hidden">
        {novel?.cover_url ? (
          <img src={novel.cover_url} alt="" className="w-full h-full object-cover" />
        ) : (
          <BookOpen className="w-5 h-5 text-moon/30" />
        )}
      </div>
      <div className="flex-1 min-w-0">
        <Link
          href={`/novel/${item.novelSlug}/chapter/${item.chapterNum}`}
          className="text-sm font-medium text-stardust hover:text-neon-cyan transition-colors truncate block"
        >
          {novel?.title_en || item.novelSlug}
        </Link>
        <div className="flex items-center gap-2 mt-1">
          <span className="text-xs text-moon/40">
            {isFinished
              ? "Completed"
              : `Ch. ${item.chapterNum} / ${novel?.total_chapters || "?"}`}
          </span>
          {!isFinished && (
            <div className="flex-1 h-1 rounded-full bg-white/10 max-w-[80px]">
              <div
                className="h-full rounded-full bg-gradient-to-r from-neon-cyan to-neon-purple"
                style={{ width: `${progressPct}%` }}
              />
            </div>
          )}
        </div>
      </div>
      <button
        onClick={() => onRemove(item.novelSlug)}
        disabled={isRemoving}
        className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 rounded-lg hover:bg-red-500/10 text-moon/40 hover:text-red-400"
        title="Remove from bookshelf"
      >
        {isRemoving ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          <Trash2 className="w-4 h-4" />
        )}
      </button>
    </div>
  );
}
