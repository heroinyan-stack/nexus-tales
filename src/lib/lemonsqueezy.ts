// Lemon Squeezy API client — credit card payment integration
// Docs: https://docs.lemonsqueezy.com/api

const LS_API = "https://api.lemonsqueezy.com/v1";
const STORE_ID = "403941";

const VARIANT_MAP: Record<string, string> = {
  premium: "1134359",
  ultimate: "1134381",
};

function getApiKey(): string {
  const key = process.env.LEMON_SQUEEZY_API_KEY;
  if (!key) throw new Error("LEMON_SQUEEZY_API_KEY is not set");
  return key;
}

interface CreateCheckoutParams {
  variantId: string;
  email?: string;
  userId?: string;
  plan: "premium" | "ultimate";
  successUrl: string;
  cancelUrl?: string;
}

interface CheckoutResult {
  checkoutUrl: string;
  checkoutId: string;
}

export async function createCheckout(params: CreateCheckoutParams): Promise<CheckoutResult> {
  const apiKey = getApiKey();

  const body = {
    data: {
      type: "checkouts",
      attributes: {
        product_options: {
          redirect_url: params.successUrl,
          receipt_button_text: "Back to Nexus Tales",
          receipt_thank_you_note: `Thank you for choosing ${params.plan === "ultimate" ? "Ultimate" : "Premium"}! Start reading now.`,
        },
        checkout_data: {
          email: params.email || undefined,
          custom: {
            user_id: params.userId || "guest",
            plan: params.plan,
          },
        },
      },
      relationships: {
        store: {
          data: { type: "stores", id: STORE_ID },
        },
        variant: {
          data: { type: "variants", id: params.variantId },
        },
      },
    },
  };

  const res = await fetch(`${LS_API}/checkouts`, {
    method: "POST",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/vnd.api+json",
      "Authorization": `Bearer ${apiKey}`,
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Lemon Squeezy checkout failed (${res.status}): ${err}`);
  }

  const json = await res.json();
  const url = json.data?.attributes?.url;
  const id = json.data?.id;

  if (!url) throw new Error("Lemon Squeezy: no checkout URL in response");

  return { checkoutUrl: url, checkoutId: String(id) };
}

export function getVariantId(plan: "premium" | "ultimate"): string {
  const id = VARIANT_MAP[plan];
  if (!id) throw new Error(`Unknown plan: ${plan}`);
  return id;
}

export function isLemonConfigured(): boolean {
  return !!process.env.LEMON_SQUEEZY_API_KEY;
}
