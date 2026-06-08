"use client";

import { Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useEffect, useState, useCallback } from "react";
import { Loader2, Copy, Check, Clock, ArrowLeft, ExternalLink, CreditCard, RefreshCw } from "lucide-react";
import Link from "next/link";

interface PaymentInfo {
  payment_id: string;
  pay_address: string;
  pay_amount: string;
  pay_currency: string;
  price_amount: string;
  price_currency: string;
  network: string;
  valid_until: string;
  order_description: string;
  invoice_url?: string;
}

interface CurrencyInfo {
  currency: string;
  label: string;
  icon: string;
  network: string;
}

const POPULAR_CURRENCIES: CurrencyInfo[] = [
  { currency: "usdtarc20", label: "USDT", icon: "💵", network: "Arbitrum" },
  { currency: "usdttrc20", label: "USDT", icon: "💵", network: "TRC20" },
  { currency: "usdcarc20", label: "USDC", icon: "💲", network: "Arbitrum" },
  { currency: "usdc", label: "USDC", icon: "💲", network: "ERC20" },
  { currency: "btc", label: "BTC", icon: "₿", network: "Bitcoin" },
  { currency: "eth", label: "ETH", icon: "⟠", network: "Ethereum" },
  { currency: "ltc", label: "LTC", icon: "Ł", network: "Litecoin" },
  { currency: "trx", label: "TRX", icon: "🔷", network: "TRON" },
  { currency: "doge", label: "DOGE", icon: "🐕", network: "Dogecoin" },
  { currency: "matic", label: "MATIC", icon: "🟣", network: "Polygon" },
];

function CheckoutContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pid = searchParams.get("pid");
  const plan = searchParams.get("plan") || "premium";

  const [payment, setPayment] = useState<PaymentInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [switching, setSwitching] = useState(false);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);
  const [timeLeft, setTimeLeft] = useState("");
  const [selectedCurrency, setSelectedCurrency] = useState("usdtarc20");

  const [invoicing, setInvoicing] = useState(false);

  // Create initial payment if no pid
  useEffect(() => {
    if (pid) {
      fetchPayment(pid);
    } else if (plan) {
      createPayment(plan, "usdtarc20");
    } else {
      setError("No payment information");
      setLoading(false);
    }
  }, [pid, plan]);

  async function fetchPayment(paymentId: string) {
    setLoading(true);
    try {
      const res = await fetch(`/api/payment/status?pid=${paymentId}`);
      const data = await res.json();
      if (data.error) {
        setError(data.error);
      } else {
        setPayment(data);
        setSelectedCurrency(data.pay_currency || "usdtarc20");
      }
    } catch {
      setError("Failed to load payment");
    } finally {
      setLoading(false);
    }
  }

  async function createPayment(planName: string, currency: string) {
    setSwitching(true);
    try {
      const res = await fetch("/api/payment/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ plan: planName, payCurrency: currency }),
      });
      const data = await res.json();
      if (data.paymentId) {
        setSelectedCurrency(currency);
        // Redirect to new pid
        router.replace(`/checkout?pid=${data.paymentId}&plan=${planName}`);
      } else {
        setError(data.error || "Failed to create payment");
      }
    } catch {
      setError("Network error");
    } finally {
      setSwitching(false);
    }
  }

  function switchCurrency(currency: string) {
    if (currency === selectedCurrency || switching) return;
    createPayment(plan, currency);
  }

  // Countdown
  useEffect(() => {
    if (!payment?.valid_until) return;
    const end = new Date(payment.valid_until).getTime();
    const tick = () => {
      const now = Date.now();
      const diff = end - now;
      if (diff <= 0) {
        setTimeLeft("Expired");
        return;
      }
      const h = Math.floor(diff / 3600000);
      const m = Math.floor((diff % 3600000) / 60000);
      const s = Math.floor((diff % 60000) / 1000);
      setTimeLeft(`${h}h ${m}m ${s}s`);
    };
    tick();
    const interval = setInterval(tick, 1000);
    return () => clearInterval(interval);
  }, [payment?.valid_until]);

  // Poll payment status
  const pollStatus = useCallback(() => {
    if (!pid) return;
    fetch(`/api/payment/status?pid=${pid}`)
      .then((r) => r.json())
      .then((data) => {
        if (data.payment_status === "finished" || data.payment_status === "confirmed") {
          router.push("/profile?checkout=success");
        }
      })
      .catch(() => {});
  }, [pid, router]);

  useEffect(() => {
    if (!pid) return;
    const interval = setInterval(pollStatus, 5000);
    return () => clearInterval(interval);
  }, [pid, pollStatus]);

  async function copyAddress() {
    if (!payment?.pay_address) return;
    await navigator.clipboard.writeText(payment.pay_address);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  async function payWithCard() {
    setInvoicing(true);
    try {
      const res = await fetch("/api/payment/invoice", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ plan }),
      });
      const data = await res.json();
      if (data.invoiceUrl) {
        window.open(data.invoiceUrl, "_blank");
      } else {
        alert(data.error || "Failed to create credit card payment");
      }
    } catch {
      alert("Network error. Please try again.");
    } finally {
      setInvoicing(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen pt-24 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-neon-cyan" />
      </div>
    );
  }

  if (error || !payment) {
    return (
      <div className="min-h-screen pt-24 pb-16 px-6 text-center">
        <div className="glass-card rounded-2xl p-8 max-w-md mx-auto">
          <h2 className="text-xl font-bold text-moon mb-4">Payment Not Found</h2>
          <p className="text-moon/50 text-sm mb-6">{error || "Invalid payment ID"}</p>
          <Link
            href="/pricing"
            className="neon-btn px-6 py-2.5 rounded-xl text-sm font-bold inline-block"
          >
            Back to Pricing
          </Link>
        </div>
      </div>
    );
  }

  const currentCurrency = POPULAR_CURRENCIES.find(
    (c) => c.currency === selectedCurrency
  );

  return (
    <div className="min-h-screen pt-24 pb-16 px-6">
      <div className="max-w-lg mx-auto">
        {/* Back link */}
        <Link
          href="/pricing"
          className="inline-flex items-center gap-2 text-sm text-moon/40 hover:text-moon mb-8 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Pricing
        </Link>

        {/* Payment Card */}
        <div className="glass-card rounded-2xl p-8 space-y-6">
          <h1 className="text-2xl font-bold text-stardust" style={{ fontFamily: "Orbitron" }}>
            Complete Your <span className="text-gradient">Payment</span>
          </h1>

          {/* Order info */}
          <div className="p-4 rounded-xl bg-white/5 space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-moon/40">Plan</span>
              <span className="text-moon font-bold">{payment.order_description}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-moon/40">Amount</span>
              <span className="text-moon font-bold">
                ${payment.price_amount} {payment.price_currency.toUpperCase()}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-moon/40">Pay with</span>
              <span className="text-neon-cyan font-bold">
                {payment.pay_amount} {currentCurrency?.label || payment.pay_currency.toUpperCase()}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-moon/40">Network</span>
              <span className="text-moon font-mono text-xs">
                {currentCurrency?.network || payment.network || payment.pay_currency}
              </span>
            </div>
          </div>

          {/* Currency selector */}
          <div className="space-y-2">
            <label className="text-sm text-moon/50">Pay with</label>
            <div className="grid grid-cols-5 gap-2">
              {POPULAR_CURRENCIES.map((c) => {
                const isActive = c.currency === selectedCurrency;
                return (
                  <button
                    key={c.currency}
                    onClick={() => switchCurrency(c.currency)}
                    disabled={switching}
                    className={`flex flex-col items-center gap-1 p-2 rounded-xl border text-xs transition-all ${
                      isActive
                        ? "border-neon-cyan bg-neon-cyan/10 text-neon-cyan"
                        : "border-white/5 bg-white/5 text-moon/50 hover:border-white/20 hover:text-moon"
                    } disabled:opacity-50 disabled:cursor-wait`}
                  >
                    <span className="text-lg">{c.icon}</span>
                    <span className="font-bold">{c.label}</span>
                    <span className="text-[10px] opacity-60">{c.network}</span>
                  </button>
                );
              })}
            </div>
            {switching && (
              <div className="flex items-center gap-2 text-xs text-moon/40">
                <RefreshCw className="w-3 h-3 animate-spin" />
                Updating payment...
              </div>
            )}
          </div>

          {/* Address */}
          <div className="space-y-3">
            <label className="text-sm text-moon/60">
              Send exactly{" "}
              <span className="text-neon-cyan font-bold">
                {payment.pay_amount} {currentCurrency?.label || payment.pay_currency.toUpperCase()}
              </span>{" "}
              to this address:
            </label>

            <div className="flex items-center gap-2">
              <code className="flex-1 p-3 rounded-xl bg-abyss border border-white/5 text-xs text-moon/70 break-all font-mono">
                {payment.pay_address}
              </code>
              <button
                onClick={copyAddress}
                className="p-3 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 transition-colors shrink-0"
              >
                {copied ? (
                  <Check className="w-4 h-4 text-emerald-400" />
                ) : (
                  <Copy className="w-4 h-4 text-moon/40" />
                )}
              </button>
            </div>
          </div>

          {/* Timer */}
          <div className="flex items-center justify-center gap-2 p-3 rounded-xl bg-white/5">
            <Clock className="w-4 h-4 text-yellow-400" />
            <span className="text-sm text-moon/60">
              {timeLeft ? (
                timeLeft === "Expired" ? (
                  <span className="text-red-400">Payment window expired</span>
                ) : (
                  <>Expires in <span className="text-moon font-bold">{timeLeft}</span></>
                )
              ) : (
                "Loading..."
              )}
            </span>
          </div>

          {/* Crypto Payment — Pay at NowPayments */}
          <a
            href={payment?.invoice_url || '#'}
            target="_blank"
            rel="noopener noreferrer"
            className="w-full py-3 rounded-xl font-bold text-sm bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 transition-all flex items-center justify-center gap-2"
          >
            <CreditCard className="w-4 h-4" />
            Pay Now (Crypto)
            <ExternalLink className="w-3 h-3 opacity-70" />
          </a>

          {/* Status */}
          <div className="text-center p-4 rounded-xl bg-neon-cyan/10 border border-neon-cyan/20">
            <p className="text-sm text-moon/60">
              Waiting for payment... This page auto-detects when your transaction
              is confirmed. Do not close this page.
            </p>
          </div>

          {/* Open in wallet */}
          <button
            onClick={() => {
              const link = `ethereum:${payment.pay_address}?value=0`;
              window.open(link, "_blank");
            }}
            className="w-full py-3 rounded-xl font-bold text-sm border border-white/10 bg-white/5 hover:bg-white/10 text-moon transition-colors flex items-center justify-center gap-2"
          >
            <ExternalLink className="w-4 h-4" />
            Open in Wallet
          </button>

          <p className="text-xs text-moon/30 text-center">
            7-day refund for first-time subscribers. Payment ID: {payment.payment_id}
          </p>
        </div>
      </div>
    </div>
  );
}

export default function CheckoutPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen pt-24 flex items-center justify-center">
          <Loader2 className="w-8 h-8 animate-spin text-neon-cyan" />
        </div>
      }
    >
      <CheckoutContent />
    </Suspense>
  );
}
