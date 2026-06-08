// POST /api/payment/invoice — Create NowPayments invoice (supports credit card)
import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth-options";

export const dynamic = "force-dynamic";

const BASE_URL = "https://api.nowpayments.io/v1";

export async function POST(req: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    const { plan } = await req.json();

    if (!plan || !["premium", "ultimate"].includes(plan)) {
      return NextResponse.json(
        { error: 'plan must be "premium" or "ultimate"' },
        { status: 400 }
      );
    }

    const apiKey = process.env.NOWPAYMENTS_API_KEY;
    if (!apiKey) {
      return NextResponse.json({ error: "API key not configured" }, { status: 500 });
    }

    const priceAmount = plan === "ultimate" ? 29.99 : 19.99;
    const planLabel = plan === "ultimate" ? "Ultimate" : "Premium";
    const userId = (session?.user as any)?.id || "guest";
    const orderId = `nt_${plan}_u${userId}_${Date.now()}`;
    const origin = req.nextUrl.origin;

    const res = await fetch(`${BASE_URL}/invoice`, {
      method: "POST",
      headers: {
        "x-api-key": apiKey,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        price_amount: priceAmount,
        price_currency: "usd",
        order_id: orderId,
        order_description: `Nexus Tales ${planLabel} — 1 Month`,
        ipn_callback_url: `${origin}/api/webhooks/nowpayments`,
        success_url: `${origin}/profile?checkout=success`,
        cancel_url: `${origin}/pricing`,
      }),
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(`NowPayments invoice failed (${res.status}): ${text}`);
    }

    const data = await res.json();
    return NextResponse.json({ invoiceUrl: data.invoice_url, invoiceId: data.id });
  } catch (err: any) {
    console.error("NowPayments invoice error:", err);
    return NextResponse.json(
      { error: err.message || "Failed to create invoice" },
      { status: 500 }
    );
  }
}
