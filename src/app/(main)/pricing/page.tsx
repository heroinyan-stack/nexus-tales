"use client";

import { useSession } from "next-auth/react";
import { Check, Sparkles, Zap, Crown, Loader2 } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

const TIERS = [
  {
    id: "free",
    name: "Free",
    icon: Sparkles,
    price: "$0",
    period: "forever",
    description: "Get started with basic access",
    features: [
      "Read first 5 chapters of any novel",
      "Full access to Free Zone novels",
      "Basic reading features",
      "Chapter bookmarks",
    ],
    cta: "Get Started Free",
    href: "/signup",
    highlighted: false,
  },
  {
    id: "premium",
    name: "Premium",
    icon: Zap,
    price: "$11.99",
    period: "30 days",
    description: "Unlimited reading for avid readers",
    features: [
      "Everything in Free",
      "Unlimited VIP novel chapters",
      "Ad-free reading experience",
      "Early access to new translations",
      "Reading statistics dashboard",
      "Priority support",
    ],
    cta: "Start Premium",
    plan: "premium",
    highlighted: true,
  },
  {
    id: "ultimate",
    name: "Ultimate",
    icon: Crown,
    price: "$14.99",
    period: "30 days",
    description: "The complete Nexus Tales experience",
    features: [
      "Everything in Premium",
      "Exclusive bonus chapters",
      "Download for offline reading",
      "Custom reading themes",
      "Vote on next translation projects",
      "Badge & profile customization",
      "Early access (24h before Premium)",
    ],
    cta: "Go Ultimate",
    plan: "ultimate",
    highlighted: false,
  },
];

export default function PricingPage() {
  const { data: session } = useSession();
  const [loading, setLoading] = useState<string | null>(null);

  async function handleCheckout(tierId: string, plan: string) {
    setLoading(tierId);
    try {
      const res = await fetch("/api/payment/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ plan }),
      });
      const data = await res.json();
      if (data.url) {
        window.location.href = data.url;
      } else {
        console.error("No checkout URL returned");
        alert(data.error || "Checkout failed. Please try again.");
      }
    } catch (err) {
      console.error("Checkout error:", err);
      alert("Checkout failed. Please try again.");
    } finally {
      setLoading(null);
    }
  }

  return (
    <div className="min-h-screen pt-24 pb-16 px-6">
      {/* Header */}
      <div className="text-center mb-12">
        <h1
          className="text-4xl md:text-5xl font-bold tracking-wider mb-4"
          style={{ fontFamily: "Orbitron" }}
        >
          <span className="text-gradient">Choose Your</span>
          <br />
          <span className="text-moon">Reading Journey</span>
        </h1>
        <p className="text-moon/50 max-w-lg mx-auto text-sm">
          Start free, upgrade anytime. Cancel anytime. No lock-in.
        </p>
      </div>

      {/* Tiers */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
        {TIERS.map((tier) => (
          <div
            key={tier.id}
            className={`glass-card rounded-2xl p-8 flex flex-col relative ${
              tier.highlighted
                ? "border-neon-cyan/40 shadow-[0_0_30px_rgba(0,240,255,0.15)] scale-[1.02]"
                : ""
            }`}
          >
            {tier.highlighted && (
              <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-neon-cyan text-abyss text-xs font-bold neon-btn">
                MOST POPULAR
              </div>
            )}

            {/* Icon */}
            <div className="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center mb-4">
              <tier.icon
                className={`w-6 h-6 ${
                  tier.highlighted ? "text-neon-cyan" : "text-moon/50"
                }`}
              />
            </div>

            {/* Title & Price */}
            <h3 className="text-xl font-bold text-stardust mb-1">{tier.name}</h3>
            <div className="flex items-baseline gap-1 mb-2">
              <span className="text-4xl font-bold text-moon">{tier.price}</span>
              <span className="text-xs text-moon/30">/{tier.period}</span>
            </div>
            <p className="text-xs text-moon/40 mb-6">{tier.description}</p>

            {/* Features */}
            <ul className="space-y-3 mb-8 flex-1">
              {tier.features.map((f, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-moon/60">
                  <Check className="w-4 h-4 text-neon-cyan shrink-0 mt-0.5" />
                  <span>{f}</span>
                </li>
              ))}
            </ul>

            {/* CTA */}
            {session ? (
              tier.id === "free" ? (
                <div className="text-center py-3 rounded-xl font-bold text-sm border border-white/10 bg-white/5 text-moon/30 cursor-not-allowed">
                  Current Plan
                </div>
              ) : (
                <button
                  onClick={() =>
                    "plan" in tier &&
                    tier.plan &&
                    handleCheckout(tier.id, tier.plan)
                  }
                  disabled={loading === tier.id || !("plan" in tier && tier.plan)}
                  className={`w-full py-3 rounded-xl font-bold text-sm transition-all ${
                    tier.highlighted
                      ? "neon-btn"
                      : "border border-white/10 bg-white/5 hover:bg-white/10 text-moon"
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                  {loading === tier.id ? (
                    <Loader2 className="w-4 h-4 animate-spin mx-auto" />
                  ) : !("plan" in tier && tier.plan) ? (
                    tier.cta
                  ) : (
                    tier.cta
                  )}
                </button>
              )
            ) : (
              <Link
                href={`/signup?callbackUrl=/pricing`}
                className={`block text-center py-3 rounded-xl font-bold text-sm transition-all border border-white/10 bg-white/5 hover:bg-white/10 text-moon`}
              >
                {tier.id === "free" ? tier.cta : "Sign Up to Subscribe"}
              </Link>
            )}
          </div>
        ))}
      </div>

      {/* Bottom note */}
      <p className="text-center text-xs text-moon/30 mt-12 max-w-md mx-auto">
        All prices in USD. Pay with USDT, USDC, BTC, ETH, or credit card via
        NowPayments. Purchase is for 30-day access — no auto-renewal.
      </p>
    </div>
  );
}