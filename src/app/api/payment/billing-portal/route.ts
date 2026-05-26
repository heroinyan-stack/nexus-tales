// POST /api/payment/billing-portal — Generate Creem Customer Portal link
import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth-options";
import { getCustomerByEmail, createPortalLink } from "@/lib/creem";

export async function POST(req: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    const email = session?.user?.email;
    if (!email) {
      return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
    }

    // Find the Creem customer by email
    const customer = await getCustomerByEmail(email);
    if (!customer?.id) {
      return NextResponse.json(
        { error: "No subscription found. Purchase a plan first." },
        { status: 404 }
      );
    }

    const portalUrl = await createPortalLink(customer.id);
    return NextResponse.json({ url: portalUrl });
  } catch (err: any) {
    console.error("Creem billing portal error:", err);
    return NextResponse.json(
      { error: err.message || "Failed to open billing portal" },
      { status: 500 }
    );
  }
}