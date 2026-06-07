// POST /api/webhooks/nowpayments — Handle NowPayments IPN (webhook)
import { NextRequest, NextResponse } from "next/server";
import * as crypto from "crypto";
import { prisma } from "@/lib/prisma";

export const dynamic = "force-dynamic";

// ── IPN Signature Verification ─────────────────────────────
// NowPayments signs the sorted JSON body with HMAC-SHA512
function verifyIpnSignature(
  body: string,
  secret: string,
  signature: string | null
): boolean {
  if (!signature) return false;
  try {
    // Sort the JSON keys alphabetically, re-stringify
    const parsed = JSON.parse(body);
    const sorted = sortObjectKeys(parsed);
    const sortedJson = JSON.stringify(sorted);

    const computed = crypto
      .createHmac("sha512", secret)
      .update(sortedJson, "utf8")
      .digest("hex");

    return crypto.timingSafeEqual(
      Buffer.from(computed),
      Buffer.from(signature)
    );
  } catch {
    return false;
  }
}

function sortObjectKeys(obj: any): any {
  if (Array.isArray(obj)) return obj.map(sortObjectKeys);
  if (obj !== null && typeof obj === "object") {
    return Object.keys(obj)
      .sort()
      .reduce((acc: any, key) => {
        acc[key] = sortObjectKeys(obj[key]);
        return acc;
      }, {});
  }
  return obj;
}

// ── Webhook handler ────────────────────────────────────────
export async function POST(req: NextRequest) {
  const body = await req.text();
  const signature = req.headers.get("x-nowpayments-sig");

  const ipnSecret = process.env.NOWPAYMENTS_IPN_SECRET;
  if (!ipnSecret) {
    console.error("NOWPAYMENTS_IPN_SECRET is not set");
    return NextResponse.json(
      { error: "IPN secret not configured" },
      { status: 500 }
    );
  }

  if (!verifyIpnSignature(body, ipnSecret, signature)) {
    console.warn("[NowPayments] Invalid IPN signature");
    return NextResponse.json({ error: "Invalid signature" }, { status: 400 });
  }

  let event: any;
  try {
    event = JSON.parse(body);
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  const {
    payment_id,
    payment_status,
    price_amount,
    price_currency,
    order_id,
    order_description,
  } = event;

  console.log(
    `[NowPayments IPN] payment=${payment_id} status=${payment_status} order=${order_id}`
  );

  try {
    switch (payment_status) {
      // ── Payment confirmed / finished → activate subscription ──
      case "finished":
      case "confirmed": {
        // Extract user ID from order_id: nt_premium_uUSER_ID_TIMESTAMP
        // or fall back to email format: nt_premium_user@gmail_com_TIMESTAMP
        const userIdMatch = order_id?.match(/nt_(?:premium|ultimate)_u(.+?)_\d+$/);
        const emailMatch = !userIdMatch ? order_id?.match(/nt_(?:premium|ultimate)_([^_].+?)_\d+$/) : null;

        // Try user ID first (most reliable)
        let user: any = null;
        if (userIdMatch) {
          const userId = userIdMatch[1];
          user = await prisma.user.findUnique({ where: { id: userId }, select: { id: true, email: true } });
        }

        // Fallback: email extraction
        if (!user && emailMatch) {
          // Reverse sanitization: _dot_ → . , _at_ → @ , remaining _ → .
          const email = emailMatch[1]
            .replace(/_at_/g, "@")
            .replace(/_dot_/g, ".")
            .replace(/_/g, ".");
          user = await prisma.user.findUnique({ where: { email }, select: { id: true, email: true } });
        }

        if (!user) {
          console.warn(`[NowPayments] Cannot find user from order_id: ${order_id}`);
          break;
        }

        const role = order_description?.toLowerCase().includes("ultimate")
          ? "ultimate"
          : "premium";

        const subExpiresAt = new Date();
        subExpiresAt.setDate(subExpiresAt.getDate() + 30);

        await prisma.user.update({
          where: { id: user.id },
          data: {
            role,
            subscription: "active",
            subExpiresAt,
            nowpaymentsPaymentId: payment_id,
          },
        });

        console.log(
          `[NowPayments] Activated ${role} for user ${user.email || user.id} (payment: ${payment_id})`
        );
        break;
      }

      // ── Payment failed / expired ───────────────────────────
      case "failed":
      case "expired":
      case "refunded": {
        // No action needed — subscription was never activated for these
        console.log(`[NowPayments] Payment ${payment_id} ${payment_status}`);
        break;
      }

      // ── Waiting / confirming / partially paid → no action ──
      default:
        console.log(
          `[NowPayments] Unhandled status: ${payment_status} for ${payment_id}`
        );
    }
  } catch (err: any) {
    console.error(
      `[NowPayments] Error processing payment ${payment_id}:`,
      err
    );
    return NextResponse.json(
      { error: "Webhook processing failed" },
      { status: 500 }
    );
  }

  return NextResponse.json({ ok: true });
}
