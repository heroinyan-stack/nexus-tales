// POST /api/payment/checkout — Create crypto payment (NowPayments)
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

    const userId = (session?.user as any)?.id || session?.user?.email?.replace(/[^a-zA-Z0-9]/g, "_") || "guest";

    const priceAmount = plan === "ultimate" ? 29.99 : 19.99;
    const planLabel = plan === "ultimate" ? "Ultimate" : "Premium";
    const orderId = `nt_${plan}_u${userId}_${Date.now()}`;

    const result = await createPayment({
      priceAmount,
      priceCurrency: "usd",
      payCurrency: payCurrency || undefined,
      orderId,
      orderDescription: `Nexus Tales ${planLabel} — 30 Days`,
      successUrl: `${req.nextUrl.origin}/profile?checkout=success`,
      cancelUrl: `${req.nextUrl.origin}/pricing`,
    });

    return NextResponse.json({
      provider: "nowpayments",
      paymentId: result.payment_id,
    });
  } catch (err: any) {
    console.error("Checkout error:", err);
    return NextResponse.json(
      { error: err.message || "Failed to create payment" },
      { status: 500 }
    );
  }
}
