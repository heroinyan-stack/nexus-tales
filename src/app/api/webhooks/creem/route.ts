// POST /api/webhooks/creem — Handle Creem webhook events
import { NextRequest, NextResponse } from "next/server";
import * as crypto from "crypto";
import { prisma } from "@/lib/prisma";

// ── Signature verification ──────────────────────────────────
function verifySignature(
  payload: string,
  secret: string,
  signature: string
): boolean {
  const computed = crypto
    .createHmac("sha256", secret)
    .update(payload)
    .digest("hex");
  return computed === signature;
}

// ── Map Creem product name → role ──────────────────────────
function getProductRole(productName?: string): string | null {
  if (!productName) return null;
  const name = productName.toLowerCase();
  if (name.includes("ultimate")) return "ultimate";
  if (name.includes("premium")) return "premium";
  return "premium"; // default to premium
}

// ── Webhook handler ────────────────────────────────────────
export async function POST(req: NextRequest) {
  const body = await req.text();
  const signature = req.headers.get("creem-signature");

  if (!signature) {
    return NextResponse.json({ error: "Missing signature" }, { status: 400 });
  }

  const webhookSecret = process.env.CREEM_WEBHOOK_SECRET;
  if (!webhookSecret) {
    console.error("CREEM_WEBHOOK_SECRET is not set");
    return NextResponse.json(
      { error: "Webhook secret not configured" },
      { status: 500 }
    );
  }

  if (!verifySignature(body, webhookSecret, signature)) {
    return NextResponse.json({ error: "Invalid signature" }, { status: 400 });
  }

  let event: any;
  try {
    event = JSON.parse(body);
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  const eventType = event.event_type || event.type;
  console.log(`[Creem Webhook] ${eventType}`);

  try {
    switch (eventType) {
      // ── Checkout completed (first payment) ──────────────
      case "checkout.completed": {
        const checkout = event.data?.checkout;
        const customer = event.data?.customer;
        if (!customer?.email) break;

        const role = getProductRole(checkout?.product_name);
        const subExpiresAt = checkout?.current_period_end_date
          ? new Date(checkout.current_period_end_date)
          : null;

        await prisma.user.upsert({
          where: { email: customer.email },
          create: {
            email: customer.email,
            name: customer.name,
            creemCustomerId: customer.id,
            role: role || "premium",
            subscription: "active",
            subExpiresAt,
          },
          update: {
            creemCustomerId: customer.id,
            ...(role && { role }),
            subscription: "active",
            subExpiresAt,
          },
        });
        break;
      }

      // ── Subscription payment successful ─────────────────
      case "subscription.paid":
      case "subscription.active": {
        const customer = event.data?.customer;
        const subscription = event.data?.subscription;
        if (!customer?.email) break;

        const subExpiresAt = subscription?.current_period_end_date
          ? new Date(subscription.current_period_end_date)
          : null;

        await prisma.user.upsert({
          where: { email: customer.email },
          create: {
            email: customer.email,
            name: customer.name,
            creemCustomerId: customer.id,
            role: getProductRole(subscription?.product_name) || "premium",
            subscription: "active",
            subExpiresAt,
          },
          update: {
            subscription: "active",
            subExpiresAt,
          },
        });
        break;
      }

      // ── Subscription past due / expired ─────────────────
      case "subscription.past_due":
      case "subscription.expired": {
        const customer = event.data?.customer;
        if (customer?.email) {
          await prisma.user.updateMany({
            where: { email: customer.email },
            data: { subscription: "past_due" },
          });
        }
        break;
      }

      // ── Subscription canceled ───────────────────────────
      case "subscription.canceled": {
        const customer = event.data?.customer;
        if (customer?.email) {
          await prisma.user.updateMany({
            where: { email: customer.email },
            data: {
              subscription: "canceled",
              role: "free",
            },
          });
        }
        break;
      }

      // ── Subscription scheduled for cancellation ─────────
      case "subscription.scheduled_cancel": {
        const customer = event.data?.customer;
        const subscription = event.data?.subscription;
        if (customer?.email) {
          await prisma.user.updateMany({
            where: { email: customer.email },
            data: {
              subscription: "active", // still active until period ends
            },
          });
        }
        break;
      }

      default:
        console.log(`[Creem Webhook] Unhandled event: ${eventType}`);
    }
  } catch (err: any) {
    console.error(`[Creem Webhook] Error processing ${eventType}:`, err);
    return NextResponse.json(
      { error: "Webhook processing failed" },
      { status: 500 }
    );
  }

  return NextResponse.json({ ok: true });
}
