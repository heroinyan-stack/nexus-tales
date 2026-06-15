"use client";

import { Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useEffect, useState, useCallback } from "react";
import { Loader2, Copy, Check, Clock, ArrowLeft, ExternalLink, RefreshCw, HelpCircle, Wallet, Globe, Shield, ChevronDown, ChevronUp } from "lucide-react";
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
  const [showGuide, setShowGuide] = useState(false);
  const [checkingStatus, setCheckingStatus] = useState(false);

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
    setCheckingStatus(true);
    fetch(`/api/payment/status?pid=${pid}`)
      .then((r) => r.json())
      .then((data) => {
        if (data.payment_status === "finished" || data.payment_status === "confirmed") {
          router.push("/profile?checkout=success");
        }
      })
      .catch(() => {})
      .finally(() => setCheckingStatus(false));
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
                ${payment.price_amount} USD
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-moon/40">You pay</span>
              <span className="text-neon-cyan font-bold">
                {payment.pay_amount} {currentCurrency?.label || payment.pay_currency.toUpperCase()}
              </span>
            </div>
          </div>

          {/* Currency selector */}
          <div className="space-y-2">
            <label className="text-sm text-moon/50">Select cryptocurrency</label>
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
                        ? "border-neon-cyan bg-neon-cyan/10 text-neon-cyan shadow-[0_0_10px_rgba(0,240,255,0.15)]"
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

          {/* Address — step 1 */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center justify-center w-5 h-5 rounded-full bg-neon-cyan text-abyss text-xs font-bold">1</span>
              <span className="text-sm text-moon/80 font-semibold">Send Payment</span>
            </div>
            <p className="text-xs text-moon/40 ml-7">
              Send exactly{" "}
              <span className="text-neon-cyan font-bold">
                {payment.pay_amount} {currentCurrency?.label || payment.pay_currency.toUpperCase()}
              </span>
              {" "}on the{" "}
              <span className="text-yellow-400">
                {currentCurrency?.network || payment.network || payment.pay_currency}
              </span>
              {" "}network to:
            </p>

            <div className="flex items-center gap-2 ml-7">
              <code className="flex-1 p-3 rounded-xl bg-abyss border border-white/10 text-xs text-moon/70 break-all font-mono select-all">
                {payment.pay_address}
              </code>
              <button
                onClick={copyAddress}
                className="p-3 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 hover:border-neon-cyan/30 transition-all shrink-0 group"
                title="Copy address"
              >
                {copied ? (
                  <Check className="w-4 h-4 text-emerald-400" />
                ) : (
                  <Copy className="w-4 h-4 text-moon/40 group-hover:text-moon transition-colors" />
                )}
              </button>
            </div>
            {copied && (
              <p className="text-xs text-emerald-400 ml-7">✓ Address copied!</p>
            )}
          </div>

          {/* Step 2 */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center justify-center w-5 h-5 rounded-full bg-neon-cyan/30 text-moon text-xs font-bold">2</span>
              <span className="text-sm text-moon/80 font-semibold">Wait for Confirmation</span>
            </div>
            <p className="text-xs text-moon/40 ml-7">
              Crypto payments typically confirm within 1–30 minutes. This page auto-detects your payment
              — once confirmed, you&apos;ll be redirected automatically.
            </p>
          </div>

          {/* Timer */}
          <div className={`flex items-center justify-center gap-2 p-3 rounded-xl ml-7 ${
            timeLeft === "Expired" ? "bg-red-400/10 border border-red-400/20" : "bg-white/5"
          }`}>
            <Clock className={`w-4 h-4 ${timeLeft === "Expired" ? "text-red-400" : "text-yellow-400"}`} />
            <span className="text-sm text-moon/60">
              {timeLeft ? (
                timeLeft === "Expired" ? (
                  <span className="text-red-400 font-medium">Payment window expired — refresh page to try again</span>
                ) : (
                  <>Expires in <span className="text-moon font-bold">{timeLeft}</span></>
                )
              ) : (
                "Loading..."
              )}
            </span>
          </div>

          {/* Status indicator */}
          <div className="p-3 rounded-xl bg-neon-cyan/5 border border-neon-cyan/10 flex items-center gap-3">
            <div className="relative">
              <div className="w-2.5 h-2.5 rounded-full bg-neon-cyan animate-pulse" />
              <div className="absolute inset-0 w-2.5 h-2.5 rounded-full bg-neon-cyan animate-ping opacity-30" />
            </div>
            <div>
              <p className="text-xs text-moon/70 font-medium">
                Awaiting payment — {checkingStatus ? "checking..." : "page auto-refreshes"}
              </p>
              <p className="text-xs text-moon/30">
                Do not close this page. Once your transaction is confirmed, you&apos;ll be redirected.
              </p>
            </div>
          </div>

          {/* Open in NowPayments */}
          {payment.invoice_url && (
            <a
              href={payment.invoice_url}
              target="_blank"
              rel="noopener noreferrer"
              className="w-full py-3 rounded-xl font-bold text-sm bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 transition-all flex items-center justify-center gap-2"
            >
              <Globe className="w-4 h-4" />
              Pay on NowPayments
              <ExternalLink className="w-3 h-3 opacity-70" />
            </a>
          )}

          {/* New to crypto? Guide */}
          <div className="border-t border-white/5 pt-4">
            <button
              onClick={() => setShowGuide(!showGuide)}
              className="w-full flex items-center justify-between text-sm text-moon/40 hover:text-moon transition-colors"
            >
              <span className="flex items-center gap-2">
                <HelpCircle className="w-4 h-4 text-neon-cyan/60" />
                New to crypto? How to pay
              </span>
              {showGuide ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>

            {showGuide && (
              <div className="mt-4 space-y-4 text-sm animate-in fade-in slide-in-from-top-2">
                {/* Step A: Get crypto */}
                <div className="p-4 rounded-xl bg-white/5 border border-white/5">
                  <div className="flex items-center gap-2 mb-2">
                    <Wallet className="w-4 h-4 text-neon-cyan" />
                    <span className="font-bold text-moon/80">Step 1: Get crypto</span>
                  </div>
                  <p className="text-xs text-moon/50 mb-3">
                    You need cryptocurrency in a wallet. Here are the easiest ways:
                  </p>
                  <div className="space-y-2 text-xs">
                    <div className="flex items-start gap-2 p-2 rounded-lg bg-white/5">
                      <span className="text-yellow-400 shrink-0 mt-0.5">🏦</span>
                      <div>
                        <span className="text-moon/70 font-medium">Buy on an exchange</span>
                        <p className="text-moon/30 mt-0.5">
                          Sign up on Binance, Coinbase, or Kraken. Buy USDT with your credit card or bank transfer. Then send it to this page&apos;s address.
                        </p>
                      </div>
                    </div>
                    <div className="flex items-start gap-2 p-2 rounded-lg bg-white/5">
                      <span className="text-emerald-400 shrink-0 mt-0.5">🦊</span>
                      <div>
                        <span className="text-moon/70 font-medium">Use a wallet app</span>
                        <p className="text-moon/30 mt-0.5">
                          MetaMask, Trust Wallet, or Phantom support buying crypto directly with a card inside the app.
                        </p>
                      </div>
                    </div>
                    <div className="flex items-start gap-2 p-2 rounded-lg bg-white/5">
                      <span className="text-blue-400 shrink-0 mt-0.5">💳</span>
                      <div>
                        <span className="text-moon/70 font-medium">Already have crypto?</span>
                        <p className="text-moon/30 mt-0.5">
                          Just send it from your existing wallet or exchange account to the address above.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Step B: Send */}
                <div className="p-4 rounded-xl bg-white/5 border border-white/5">
                  <div className="flex items-center gap-2 mb-2">
                    <Shield className="w-4 h-4 text-emerald-400" />
                    <span className="font-bold text-moon/80">Step 2: Send the exact amount</span>
                  </div>
                  <ul className="space-y-1.5 text-xs text-moon/50">
                    <li>• Copy the address above (click the copy icon)</li>
                    <li>• Paste it in your wallet or exchange withdrawal form</li>
                    <li>• Enter EXACTLY <span className="text-neon-cyan font-bold">{payment.pay_amount} {currentCurrency?.label || payment.pay_currency.toUpperCase()}</span></li>
                    <li>• Make sure you select the <span className="text-yellow-400">{currentCurrency?.network || payment.network}</span> network</li>
                    <li>• Double-check the address before sending!</li>
                  </ul>
                </div>

                {/* Step C: Confirm */}
                <div className="p-4 rounded-xl bg-white/5 border border-white/5">
                  <div className="flex items-center gap-2 mb-2">
                    <Clock className="w-4 h-4 text-purple-400" />
                    <span className="font-bold text-moon/80">Step 3: Wait for confirmation</span>
                  </div>
                  <ul className="space-y-1.5 text-xs text-moon/50">
                    <li>• Crypto transactions are confirmed on the blockchain</li>
                    <li>• {currentCurrency?.network === "TRC20" ? "TRC20 is fast — usually confirmed in 1–2 minutes" : currentCurrency?.network === "Arbitrum" ? "Arbitrum is fast — usually confirmed within 1 minute" : "Usually confirmed in 10–30 minutes"}</li>
                    <li>• This page auto-detects your payment</li>
                    <li>• You&apos;ll be redirected once confirmed</li>
                    <li>• If it takes longer, don&apos;t worry — your payment won&apos;t be lost</li>
                  </ul>
                </div>

                {/* FAQ */}
                <div className="space-y-2 text-xs">
                  <details className="text-moon/40">
                    <summary className="text-moon/50 hover:text-moon/70 cursor-pointer py-1">
                      What if I send the wrong amount?
                    </summary>
                    <p className="text-moon/30 mt-1 ml-4">
                      Most wallets will reject underpaid transactions. If you overpay, contact us and we&apos;ll help.
                    </p>
                  </details>
                  <details className="text-moon/40">
                    <summary className="text-moon/50 hover:text-moon/70 cursor-pointer py-1">
                      Can I get a refund?
                    </summary>
                    <p className="text-moon/30 mt-1 ml-4">
                      Yes — first-time subscribers get a 7-day refund. Contact us through the Contact page.
                    </p>
                  </details>
                  <details className="text-moon/40">
                    <summary className="text-moon/50 hover:text-moon/70 cursor-pointer py-1">
                      Is crypto safe to use?
                    </summary>
                    <p className="text-moon/30 mt-1 ml-4">
                      Yes. USDT is a stablecoin pegged 1:1 to USD. Your payment is processed by NowPayments, a trusted crypto payment gateway used by thousands of businesses worldwide.
                    </p>
                  </details>
                </div>
              </div>
            )}
          </div>

          <p className="text-xs text-moon/30 text-center">
            Payment ID: {payment.payment_id} · Powered by NowPayments
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
