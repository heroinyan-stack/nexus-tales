// Middleware — protect chapter routes for VIP novels
import { withAuth } from "next-auth/middleware";
import { NextResponse } from "next/server";

// Public routes (always accessible)
const PUBLIC_ROUTES = ["/", "/novels", "/login", "/signup", "/pricing", "/api"];

export default withAuth(
  function middleware(req) {
    return NextResponse.next();
  },
  {
    callbacks: {
      authorized({ token, req }) {
        const path = req.nextUrl.pathname;

        // Public routes always allowed
        if (PUBLIC_ROUTES.some((r) => path.startsWith(r))) return true;

        // Static assets
        if (path.match(/\.(jpg|png|svg|ico|css|js|xml|txt)$/)) return true;

        // Chapter routes — first 5 chapters of any novel are free
        if (path.includes("/chapter/")) {
          const match = path.match(/\/novel\/[^/]+\/chapter\/(\d+)/);
          if (match) {
            const chapterNum = parseInt(match[1]);
            // First 5 chapters free; beyond that requires login
            if (chapterNum <= 5) return true;
            return !!token;
          }
        }

        // Novel detail pages — always public
        if (path.match(/^\/novel\/[^/]+$/)) return true;

        // Everything else requires login
        return !!token;
      },
    },
    pages: {
      signIn: "/login",
    },
  }
);

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization)
     * - favicon.ico
     * - covers/ (cover images)
     * - API routes (handled separately)
     */
    "/((?!_next/static|_next/image|favicon.ico|covers/).*)",
  ],
};