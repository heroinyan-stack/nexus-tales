export const dynamic = "force-dynamic";

export async function GET() {
  return Response.json({
    hasGoogleId: typeof process.env.GOOGLE_CLIENT_ID === "string" && process.env.GOOGLE_CLIENT_ID.length > 0,
    googleIdLen: (process.env.GOOGLE_CLIENT_ID || "").length,
    hasGoogleSecret: typeof process.env.GOOGLE_CLIENT_SECRET === "string" && process.env.GOOGLE_CLIENT_SECRET.length > 0,
    googleSecretLen: (process.env.GOOGLE_CLIENT_SECRET || "").length,
    nextAuthUrl: process.env.NEXTAUTH_URL || "(missing)",
    nextAuthSecretLen: (process.env.NEXTAUTH_SECRET || "").length,
    dbUrlLen: (process.env.DATABASE_URL || "").length,
  });
}