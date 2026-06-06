// GET /api/payment/status?pid=xxx — Poll payment status
import { NextRequest, NextResponse } from "next/server";
import { getPaymentStatus } from "@/lib/nowpayments";

export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  try {
    const pid = req.nextUrl.searchParams.get("pid");
    if (!pid) {
      return NextResponse.json(
        { error: "pid is required" },
        { status: 400 }
      );
    }

    const result = await getPaymentStatus(pid);
    return NextResponse.json(result);
  } catch (err: any) {
    console.error("Payment status error:", err);
    return NextResponse.json(
      { error: err.message },
      { status: 500 }
    );
  }
}
