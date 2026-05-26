import { redirect } from "next/navigation";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Browse All Novels",
  description: "Browse all translated cultivation, xianxia, wuxia, and classic Chinese novels. Free chapters available daily.",
  alternates: { canonical: "https://novelhub.beauty/novels" },
};

export default function NovelsPage() {
  redirect("/");
}