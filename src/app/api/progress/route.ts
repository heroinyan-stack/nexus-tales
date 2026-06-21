import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { prisma } from "@/lib/prisma";

// Helper: extract user ID from session
async function getUserId(): Promise<string | null> {
  const session = await getServerSession();
  return (session?.user as any)?.id || null;
}

// GET /api/progress — get all reading progress for current user
export async function GET(req: NextRequest) {
  const userId = await getUserId();
  if (!userId) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { searchParams } = new URL(req.url);
  const novelSlug = searchParams.get("novelSlug");

  try {
    if (novelSlug) {
      // Single novel progress
      const progress = await prisma.readingProgress.findUnique({
        where: {
          userId_novelSlug: {
            userId,
            novelSlug,
          },
        },
      });
      return NextResponse.json({ progress });
    }

    // All progress (bookshelf)
    const allProgress = await prisma.readingProgress.findMany({
      where: { userId },
      orderBy: { updatedAt: "desc" },
    });
    return NextResponse.json({ progress: allProgress });
  } catch (err) {
    console.error("GET /api/progress error:", err);
    return NextResponse.json({ error: "Internal error" }, { status: 500 });
  }
}

// POST /api/progress — save or update reading progress
export async function POST(req: NextRequest) {
  const userId = await getUserId();
  if (!userId) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  try {
    const body = await req.json();
    const { novelSlug, chapterNum, scrollPercent, finished } = body;

    if (!novelSlug) {
      return NextResponse.json({ error: "novelSlug required" }, { status: 400 });
    }

    const progress = await prisma.readingProgress.upsert({
      where: {
        userId_novelSlug: {
          userId,
          novelSlug,
        },
      },
      create: {
        userId,
        novelSlug,
        chapterNum: chapterNum || 1,
        scrollPercent: scrollPercent || 0,
        finished: finished || false,
      },
      update: {
        ...(chapterNum !== undefined && { chapterNum }),
        ...(scrollPercent !== undefined && { scrollPercent }),
        ...(finished !== undefined && { finished }),
        updatedAt: new Date(),
      },
    });

    return NextResponse.json({ progress });
  } catch (err) {
    console.error("POST /api/progress error:", err);
    return NextResponse.json({ error: "Internal error" }, { status: 500 });
  }
}

// DELETE /api/progress — remove a novel from bookshelf
export async function DELETE(req: NextRequest) {
  const userId = await getUserId();
  if (!userId) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { searchParams } = new URL(req.url);
  const novelSlug = searchParams.get("novelSlug");

  if (!novelSlug) {
    return NextResponse.json({ error: "novelSlug required" }, { status: 400 });
  }

  try {
    await prisma.readingProgress.deleteMany({
      where: {
        userId,
        novelSlug,
      },
    });
    return NextResponse.json({ success: true });
  } catch (err) {
    console.error("DELETE /api/progress error:", err);
    return NextResponse.json({ error: "Internal error" }, { status: 500 });
  }
}
