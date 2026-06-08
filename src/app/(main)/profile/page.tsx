"use client";

import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import {
  User, Crown, Zap, Calendar, CreditCard, Shield,
  BookOpen, Clock, TrendingUp, Bell, Download, Palette,
  LogOut, ChevronRight, Loader2, CheckCircle, AlertCircle,
} from "lucide-react";
import Link from "next/link";

export default function ProfilePage() {
  const { data: session, status, update } = useSession();
  const router = useRouter();
  const [loadingPortal, setLoadingPortal] = useState(false);

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

  return (
    <div className="min-h-screen pt-24 pb-16 px-6">
      <div className="max-w-3xl mx-auto">
        {/* Profile Header */}
        <div className="glass-card rounded-2xl p-8 mb-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
            {/* Avatar */}
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

        {/* Subscription Info (only if premium/ultimate) */}
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

        {/* Reading Stats */}
        <div className="glass-card rounded-2xl p-6 mb-6 space-y-4">
          <h2 className="text-lg font-bold text-stardust flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-neon-cyan" />
            Reading Stats
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {[
              { icon: BookOpen, label: "Novels Read", value: "—", color: "text-neon-cyan" },
              { icon: Clock, label: "Reading Time", value: "—", color: "text-neon-purple" },
              { icon: Calendar, label: "Streak", value: "—", color: "text-neon-pink" },
              { icon: Bell, label: "Notifications", value: "—", color: "text-neon-green" },
            ].map((stat, i) => (
              <div key={i} className="p-3 rounded-xl bg-white/5 text-center">
                <stat.icon className={`w-5 h-5 mx-auto mb-1.5 ${stat.color}`} />
                <div className="font-bold text-stardust text-lg">{stat.value}</div>
                <div className="text-xs text-moon/40">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Settings */}
        <div className="glass-card rounded-2xl p-6 mb-6 space-y-4">
          <h2 className="text-lg font-bold text-stardust flex items-center gap-2">
            🔧 Settings
          </h2>

          <div className="space-y-2">
            {[
              { icon: Palette, label: "Reading Theme", desc: "Dark • Cyan" },
              { icon: Download, label: "Offline Chapters", desc: role !== "free" ? role !== "free" ? "0 downloaded" : "" : "Premium only" },
              { icon: Bell, label: "Notifications", desc: "Enabled" },
            ].map((item, i) => (
              <div
                key={i}
                className="flex items-center justify-between p-3 rounded-xl hover:bg-white/5 transition-colors cursor-pointer"
              >
                <div className="flex items-center gap-3">
                  <item.icon className="w-4 h-4 text-moon/40" />
                  <div>
                    <div className="text-sm font-medium text-stardust">
                      {item.label}
                    </div>
                    <div className="text-xs text-moon/30">{item.desc}</div>
                  </div>
                </div>
                <ChevronRight className="w-4 h-4 text-moon/20" />
              </div>
            ))}
          </div>
        </div>

        {/* Upgrade upsell (free tier only) */}
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