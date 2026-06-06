// NowPayments API wrapper — 加密货币支付网关
// Docs: https://documenter.getpostman.com/view/7907941/S1a32n38
// Sandbox: https://api-sandbox.nowpayments.io/v1
// Live:    https://api.nowpayments.io/v1

const BASE_URL =
  process.env.NOWPAYMENTS_SANDBOX === "true"
    ? "https://api-sandbox.nowpayments.io/v1"
    : "https://api.nowpayments.io/v1";

function getApiKey(): string {
  const key = process.env.NOWPAYMENTS_API_KEY;
  if (!key) throw new Error("NOWPAYMENTS_API_KEY is not set");
  return key;
}

// ── Types ─────────────────────────────────────────────────
export interface CreatePaymentParams {
  priceAmount: number;
  priceCurrency: string; // "usd"
  payCurrency?: string; // e.g. "usdttrc20", omit to let user choose
  orderId: string;
  orderDescription: string;
  successUrl?: string;
  cancelUrl?: string;
}

export interface CreatePaymentResult {
  payment_id: string;
  payment_status: string;
  pay_address: string;
  price_amount: number;
  price_currency: string;
  pay_amount: number;
  pay_currency: string;
  order_id: string;
  order_description: string;
  ipn_callback_url: string;
  invoice_url: string;
  created_at: string;
  updated_at: string;
}

export interface PaymentStatusResult {
  payment_id: string;
  payment_status: string;
  price_amount: number;
  price_currency: string;
  pay_amount: number;
  pay_currency: string;
  order_id: string;
  order_description: string;
  created_at: string;
  updated_at: string;
}

// ── API Calls ─────────────────────────────────────────────

/** 创建支付，返回 invoice_url 让用户去付款 */
export async function createPayment(
  params: CreatePaymentParams
): Promise<CreatePaymentResult> {
  const body: Record<string, any> = {
    price_amount: params.priceAmount,
    price_currency: params.priceCurrency,
    order_id: params.orderId,
    order_description: params.orderDescription,
    ipn_callback_url: `${process.env.NEXT_PUBLIC_SITE_URL || "https://novelhub.beauty"}/api/webhooks/nowpayments`,
    success_url: params.successUrl,
    cancel_url: params.cancelUrl,
  };

  // Allow user to specify pay currency; defaults to USDT ARC20 (lowest stablecoin minimum ~$11.70)
  if (params.payCurrency) {
    body.pay_currency = params.payCurrency;
  } else {
    body.pay_currency = "usdtarc20";
  }

  const res = await fetch(`${BASE_URL}/payment`, {
    method: "POST",
    headers: {
      "x-api-key": getApiKey(),
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`NowPayments create payment failed (${res.status}): ${text}`);
  }

  return res.json();
}

/** 查询支付状态 */
export async function getPaymentStatus(
  paymentId: string
): Promise<PaymentStatusResult> {
  const res = await fetch(`${BASE_URL}/payment/${paymentId}`, {
    headers: { "x-api-key": getApiKey() },
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`NowPayments get status failed (${res.status}): ${text}`);
  }

  return res.json();
}

/** 获取可用币种列表 */
export async function getAvailableCurrencies(): Promise<string[]> {
  const res = await fetch(`${BASE_URL}/currencies?fixed_rate=1`, {
    headers: { "x-api-key": getApiKey() },
  });
  if (!res.ok) throw new Error(`NowPayments currencies failed (${res.status})`);
  const data = await res.json();
  return (data.currencies || []).map((c: any) => c.currency);
}

/** 获取 USDT 各链的预估金额 */
export async function getEstimatedPrice(
  amount: number,
  currencyFrom: string,
  currencyTo: string
): Promise<number> {
  const res = await fetch(
    `${BASE_URL}/estimate?amount=${amount}&currency_from=${currencyFrom}&currency_to=${currencyTo}`,
    { headers: { "x-api-key": getApiKey() } }
  );
  if (!res.ok) throw new Error(`NowPayments estimate failed (${res.status})`);
  const data = await res.json();
  return data.estimated_amount;
}
