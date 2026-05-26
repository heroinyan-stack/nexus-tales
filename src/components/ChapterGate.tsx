"use client";

import { useSession } from "next-auth/react";
import Link from "next/link";
import { Lock, LogIn, Crown } from "lucide-react";

interface ChapterGateProps {
  chapterNum: number;
  novelSlug: string;
  novelTitle: string;
  zone: string;
  totalChapters: number;
}

export default function ChapterGate({
  chapterNum,
  novelSlug,
  novelTitle,
  zone,
  totalChapters,
}: ChapterGateProps) {
  const { data: session, status } = useSession();

  // Free zone novels — always accessible
  if (zone === "free") return null;

  // First 5 chapters of VIP novels — always free
  if (chapterNum <= 5) return null;

  // Logged in + premium/ultimate — full access
  if (session && ["premium", "ultimate", "admin"].includes((session.user as any)?.role || "")) {
    return null;
  }

  // Not logged in at all
  if (!session) {
    return (
      <LockOverlay
        icon={<LogIn className="w-10 h-10 text-neon-cyan" />}
        title="Sign in to Continue Reading"
        description={`You've read ${chapterNum - 1} free chapters of "${novelTitle}". Sign in to unlock all ${totalChapters} chapters.`}
        actions={[
          { label: "Sign In Free", href: `/login?callbackUrl=/novel/${novelSlug}/chapter/${chapterNum}`, primary: true },
          { label: "View Pricing", href: "/pricing", primary: false },
        ]}
      />
    );
  }

  // Logged in but free tier
  return (
    <LockOverlay
      icon={<Crown className="w-10 h-10 text-neon-cyan" />}
      title="Upgrade to Continue"
      description={`You're on the Free plan. Upgrade to Premium to read all ${totalChapters} chapters of "${novelTitle}".`}
      actions={[
        { label: "Upgrade to Premium — $4.99/mo", href: "/pricing", primary: true },
        { label: "Back to Free Chapters", href: `/novel/${novelSlug}`, primary: false },
      ]}
    />
  );
}

// ─── Lock Overlay ──────────────────────────────────
function LockOverlay({
  icon,
  title,
  description,
  actions,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  actions: { label: string; href: string; primary: boolean }[];
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-abyss/80 backdrop-blur-sm">
      <div className="glass-card rounded-2xl max-w-md w-full p-8 text-center space-y-6 border-neon-cyan/20">
        <div className="mx-auto w-16 h-16 rounded-full bg-neon-cyan/10 flex items-center justify-center">
          {icon}
        </div>

        <div className="space-y-2">
          <h2 className="text-xl font-bold text-stardust">{title}</h2>
          <p className="text-sm text-moon/50 leading-relaxed">{description}</p>
        </div>

        {/* Chapter preview indicator */}
        <div className="flex items-center justify-center gap-1">
          {Array.from({ length: 5 }).map((_, i) => (
            <div
              key={i}
              className="w-2 h-2 rounded-full bg-neon-cyan/60"
            />
          ))}
          <div className="w-2 h-2 rounded-full bg-moon/10" />
          <div className="w-2 h-2 rounded-full bg-moon/10" />
          <div className="w-2 h-2 rounded-full bg-moon/10" />
          <div className="w-8 h-0.5 bg-moon/10" />
          <Lock className="w-3 h-3 text-moon/20" />
        </div>
        <p className="text-xs text-moon/30">5 free chapters read</p>

        <div className="space-y-2">
          {actions.map((action, i) =>
            action.primary ? (
              <Link
                key={i}
                href={action.href}
                className="neon-btn w-full py-3 rounded-xl text-sm font-bold block"
              >
                {action.label}
              </Link>
            ) : (
              <Link
                key={i}
                href={action.href}
                className="block w-full py-3 rounded-xl text-sm text-moon/50 hover:text-moon border border-white/10 bg-white/5 hover:bg-white/10 transition-all"
              >
                {action.label}
              </Link>
            )
          )}
        </div>
      </div>
    </div>
  );
}