// POST /api/payment/billing-portal — Return subscription info
// NowPayments has no customer portal; users renew by purchasing again
import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth-options";

export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    const email = session?.user?.email;
    if (!email) {
      return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
    }

    // Crypto payments don't have a management portal.
    // Return info so frontend can redirect to /pricing for renewal.
    return NextResponse.json({
      message: "Crypto subscriptions are one-time purchases. Visit /pricing to renew.",
    });
  } catch (err: any) {
    console.error("Billing portal error:", err);
    return NextResponse.json(
      { error: err.message || "Failed" },
      { status: 500 }
    );
  }
}