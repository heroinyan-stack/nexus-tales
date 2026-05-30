import { AuthOptions } from "next-auth";
import GoogleProvider from "next-auth/providers/google";
import CredentialsProvider from "next-auth/providers/credentials";
import { PrismaAdapter } from "@next-auth/prisma-adapter";
import bcrypt from "bcryptjs";
import { prisma } from "@/lib/prisma";

export const authOptions: AuthOptions = {
  adapter: PrismaAdapter(prisma) as any,
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID || "",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || "",
    }),
    CredentialsProvider({
      name: "credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) return null;
        const user = await prisma.user.findUnique({
          where: { email: credentials.email },
        });
        if (!user || !user.password) return null;
        const match = await bcrypt.compare(credentials.password, user.password);
        if (!match) return null;
        return { id: user.id, name: user.name, email: user.email };
      },
    }),
  ],
  session: { strategy: "jwt" },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        const dbUser = await prisma.user.findUnique({
          where: { id: user.id || token.sub },
          select: { id: true, role: true, subscription: true, subExpiresAt: true },
        });
        if (dbUser) {
          token.role = dbUser.role;
          token.subscription = dbUser.subscription;
          token.subExpiresAt = dbUser.subExpiresAt?.toISOString() ?? null;
        }
      }
      // Refresh role on every request
      if (token.sub) {
        const fresh = await prisma.user.findUnique({
          where: { id: token.sub as string },
          select: { role: true, subscription: true, subExpiresAt: true },
        });
        if (fresh) {
          token.role = fresh.role;
          token.subscription = fresh.subscription;
          token.subExpiresAt = fresh.subExpiresAt?.toISOString() ?? null;
        }
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        (session.user as any).id = token.sub as string;
        (session.user as any).role = (token.role as string) || "free";
        (session.user as any).subscription = token.subscription as string | null;
        (session.user as any).subExpiresAt = token.subExpiresAt as string | null;
      }
      return session;
    },
  },
  pages: {
    signIn: "/login",
    error: "/login",
  },
};