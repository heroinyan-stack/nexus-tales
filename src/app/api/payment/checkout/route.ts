// POST /api/payment/checkout — Create Creem checkout session
import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth-options";
import { createCheckout } from "@/lib/creem";

export const dynamic = "force-dynamic";

// CREEM compliance: only registered production domains may create checkouts
const ALLOWED_DOMAINS = new Set(["novelhub.beauty", "www.novelhub.beauty"]);

function isAllowed(host: string): boolean {
  return ALLOWED_DOMAINS.has(host) || host.endsWith(".novelhub.beauty");
}

export async function POST(req: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    const { productId } = await req.json();

    if (!productId) {
      return NextResponse.json(
        { error: "productId is required" },
        { status: 400 }
      );
    }

    // Block checkout from unregistered domains (CREEM compliance)
    const host = req.headers.get("host") || "";
    if (!isAllowed(host)) {
      return NextResponse.json(
        { error: "Please visit novelhub.beauty to subscribe." },
        { status: 403 }
      );
    }

    const origin = req.nextUrl.origin;
    const successUrl = `${origin}/profile?checkout=success`;

    const result = await createCheckout({
      productId,
      requestId: session?.user?.email
        ? `user_${session.user.email}_${Date.now()}`
        : undefined,
      successUrl,
      customer: session?.user?.email
        ? { email: session.user.email }
        : undefined,
    });

    return NextResponse.json({ url: result.checkout_url });
  } catch (err: any) {
    console.error("Creem checkout error:", err);
    return NextResponse.json(
      { error: err.message || "Failed to create checkout" },
      { status: 500 }
    );
  }
}
