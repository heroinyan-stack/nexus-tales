import NextAuth from "next-auth";
import { authOptions } from "@/lib/auth-options";

// Prevent Next.js from pre-rendering this API route during build
// (NextAuth needs runtime database access via PrismaAdapter)
export const dynamic = "force-dynamic";

const handler = NextAuth(authOptions);
export { handler as GET, handler as POST };