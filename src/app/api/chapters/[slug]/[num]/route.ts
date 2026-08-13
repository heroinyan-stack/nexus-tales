import { NextResponse } from "next/server";
import { getR2Chapter } from "@/lib/r2";

export async function GET(
  req: Request,
  { params }: { params: { slug: string; num: string } }
) {
  const num = parseInt(params.num, 10);
  if (isNaN(num) || num < 1) {
    return NextResponse.json({ error: "Invalid chapter number" }, { status: 400 });
  }

  const chapter = await getR2Chapter(params.slug, num);

  if (!chapter) {
    return NextResponse.json({ error: "Chapter not found" }, { status: 404 });
  }

  return NextResponse.json(chapter);
}
