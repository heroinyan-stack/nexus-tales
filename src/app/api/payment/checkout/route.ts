// POST /api/payment/checkout — Create NowPayments crypto payment
import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth-options";
import { createPayment } from "@/lib/nowpayments";

export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    const { plan, payCurrency } = await req.json();

    if (!plan || !["premium", "ultimate"].includes(plan)) {
      return NextResponse.json(
        { error: 'plan must be "premium" or "ultimate"' },
        { status: 400 }
      );
    }

    // Premium $11.99 (above USDT ARC20 minimum $11.70), Ultimate $14.99
    const priceAmount = plan === "ultimate" ? 14.99 : 11.99;
    const planLabel = plan === "ultimate" ? "Ultimate" : "Premium";
    const userId = (session?.user as any)?.id || session?.user?.email?.replace(/[^a-zA-Z0-9]/g, "_") || "guest";
    const orderId = `nt_${plan}_u${userId}_${Date.now()}`;

    const origin = req.nextUrl.origin;

    const result = await createPayment({
      priceAmount,
      priceCurrency: "usd",
      payCurrency: payCurrency || undefined, // let user choose, default to USDT ARC20
      orderId,
      orderDescription: `Nexus Tales ${planLabel} — 1 Month`,
      successUrl: `${origin}/profile?checkout=success`,
      cancelUrl: `${origin}/pricing`,
    });

    return NextResponse.json({
      paymentId: result.payment_id,
    });
  } catch (err: any) {
    console.error("NowPayments checkout error:", err);
    return NextResponse.json(
      { error: err.message || "Failed to create payment" },
      { status: 500 }
    );
  }
}
