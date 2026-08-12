import type { Metadata } from "next";
import NovelsClient from "./NovelsClient";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Browse All Novels",
  description:
    "Browse all translated cultivation, xianxia, wuxia, and classic Chinese novels. Free chapters available daily.",
  alternates: { canonical: "https://novelhub.beauty/novels" },
};

export default async function NovelsPage() {
  // Fetch from API (which reads from Blob)
  const res = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL || "https://novelhub.beauty"}/api/novels`, {
    next: { revalidate: 300 },
  });
  const data = res.ok ? await res.json() : { novels: [], genres: [] };

  return <NovelsClient novels={data.novels || []} genres={data.genres || []} />;
}
