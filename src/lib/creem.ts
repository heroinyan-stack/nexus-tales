// Creem REST API wrapper — 不用SDK，直接HTTP调用
// Docs: https://docs.creem.io/api-reference/introduction

const BASE_URL = process.env.NODE_ENV === "production"
  ? "https://api.creem.io/v1"
  : "https://test-api.creem.io/v1";

function getApiKey(): string {
  const key = process.env.CREEM_API_KEY;
  if (!key) throw new Error("CREEM_API_KEY is not set");
  return key;
}

// ── Types ─────────────────────────────────────────────────
export interface CreemCheckoutParams {
  productId: string;
  requestId?: string;
  successUrl?: string;
  customer?: { email: string };
}

export interface CreemCheckoutResult {
  id: string;
  checkout_url: string;
  [key: string]: any;
}

export interface CreemCustomer {
  id: string;
  email: string;
  [key: string]: any;
}

// ── API Calls ─────────────────────────────────────────────

/** 创建 checkout session，返回 checkout_url 供用户跳转支付 */
export async function createCheckout(
  params: CreemCheckoutParams
): Promise<CreemCheckoutResult> {
  const res = await fetch(`${BASE_URL}/checkouts`, {
    method: "POST",
    headers: {
      "x-api-key": getApiKey(),
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      product_id: params.productId,
      request_id: params.requestId,
      success_url: params.successUrl,
      customer: params.customer,
    }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Creem checkout failed (${res.status}): ${text}`);
  }

  return res.json();
}

/** 按 email 查找 Creem customer */
export async function getCustomerByEmail(
  email: string
): Promise<CreemCustomer | null> {
  const res = await fetch(
    `${BASE_URL}/customers?email=${encodeURIComponent(email)}`,
    {
      headers: { "x-api-key": getApiKey() },
    }
  );

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Creem get customer failed (${res.status}): ${text}`);
  }

  const data = await res.json();
  // API returns { customers: [...] } or { data: [...] }
  const customers = data.customers ?? data.data ?? [];
  return customers[0] ?? null;
}

/** 生成 Customer Portal 链接 */
export async function createPortalLink(
  customerId: string
): Promise<string> {
  const res = await fetch(`${BASE_URL}/customers/portal`, {
    method: "POST",
    headers: {
      "x-api-key": getApiKey(),
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ customer_id: customerId }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Creem portal failed (${res.status}): ${text}`);
  }

  const data = await res.json();
  return data.portal_url ?? data.customerPortalLink;
}
