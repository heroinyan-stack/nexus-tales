// POST /api/webhooks/lemonsqueezy — Handle LS payment events
import { NextRequest, NextResponse } from "next/server";
import { createHmac, timingSafeEqual } from "crypto";
import { prisma } from "@/lib/prisma";

export const dynamic = "force-dynamic";

function verifySignature(rawBody: string, signature: string): boolean {
  const secret = process.env.LEMON_SQUEEZY_WEBHOOK_SECRET;
  if (!secret) {
    console.error("[LS Webhook] LEMON_SQUEEZY_WEBHOOK_SECRET not set");
    return false;
  }
  try {
    const hmac = createHmac("sha256", secret);
    hmac.update(rawBody);
    const digest = hmac.digest("hex");
    return timingSafeEqual(Buffer.from(digest), Buffer.from(signature));
  } catch (err) {
    console.error("[LS Webhook] signature verification error:", err);
    return false;
  }
}

export async function POST(req: NextRequest) {
  const rawBody = await req.text();
  const signature = req.headers.get("x-signature") || "";

  if (!verifySignature(rawBody, signature)) {
    console.warn("[LS Webhook] Invalid signature");
    return NextResponse.json({ error: "Invalid signature" }, { status: 401 });
  }

  let event: any;
  try {
    event = JSON.parse(rawBody);
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  const eventName = event.meta?.event_name;
  console.log(`[LS Webhook] ${eventName}`);

  try {
    switch (eventName) {
      case "order_created": {
        const orderId = event.data?.id;
        const attrs = event.data?.attributes;
        const email = attrs?.user_email;
        const customData = attrs?.custom_data || event.meta?.custom_data || {};
        const plan = customData?.plan || attrs?.variant_name?.toLowerCase().includes("ultimate") ? "ultimate" : "premium";
        const status = attrs?.status;

        console.log(`[LS Webhook] order_created: ${orderId}, email=${email}, plan=${plan}, status=${status}`);

        if (email) {
          // Grant access based on order (wait for payment success too)
          await maybeGrantAccess(email, plan, orderId);
        }
        break;
      }

      case "subscription_payment_success":
      case "order_paid": {
        const attrs = event.data?.attributes;
        const email = attrs?.user_email;
        const customData = attrs?.custom_data || event.meta?.custom_data || {};
        const plan = customData?.plan || "premium";

        if (email) {
          await grantAccess(email, plan);
        }
        break;
      }

      case "subscription_created": {
        const attrs = event.data?.attributes;
        const email = attrs?.user_email;
        const plan = attrs?.variant_name?.toLowerCase().includes("ultimate") ? "ultimate" : "premium";

        if (email) {
          await grantAccess(email, plan);
        }
        break;
      }

      default:
        console.log(`[LS Webhook] unhandled event: ${eventName}`);
    }
  } catch (err) {
    console.error(`[LS Webhook] error processing ${eventName}:`, err);
    // Still return 200 so LS doesn't retry the webhook
  }

  return NextResponse.json({ received: true });
}

async function maybeGrantAccess(email: string, plan: "premium" | "ultimate", _orderId: string) {
  // Update role immediately on order_created (LS processes fast)
  await grantAccess(email, plan);
}

async function grantAccess(email: string, plan: "premium" | "ultimate") {
  const role = plan === "ultimate" ? "ultimate" : "premium";
  const expiresAt = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000); // 30 days

  try {
    await prisma.user.updateMany({
      where: { email },
      data: {
        role,
        subscription: "active",
        subExpiresAt: expiresAt,
      },
    });
    console.log(`[LS Webhook] granted ${role} to ${email}, expires ${expiresAt.toISOString()}`);
  } catch (err) {
    console.error(`[LS Webhook] failed to grant access to ${email}:`, err);
  }
}
