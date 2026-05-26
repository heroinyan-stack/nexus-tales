"use client";

import { useSession, signIn, signOut } from "next-auth/react";
import Link from "next/link";
import { useState, useRef, useEffect } from "react";
import { ChevronDown, LogOut, User, Settings, Crown } from "lucide-react";
import { useRouter } from "next/navigation";

export default function AuthHeader() {
  const { data: session, status } = useSession();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  // Close menu on outside click
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const isAdmin = session?.user && (session.user as any).role === "admin";

  return (
    <header className="fixed top-0 left-0 right-0 z-50 glass-card border-b border-white/5">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link
          href="/"
          className="text-2xl font-bold tracking-wider"
          style={{ fontFamily: "Orbitron" }}
        >
          <span className="text-gradient">NEXUS</span>
          <span className="text-stardust ml-1 opacity-70">TALES</span>
        </Link>

        {/* Nav */}
        <nav className="hidden md:flex items-center gap-8 text-sm tracking-wide">
          <Link href="/novels" className="text-moon hover:text-neon-cyan transition-colors">
            Browse
          </Link>
          <Link href="/pricing" className="text-moon hover:text-neon-cyan transition-colors">
            Pricing
          </Link>
          <a href="#" className="text-moon hover:text-neon-cyan transition-colors">
            Rankings
          </a>
        </nav>

        {/* Right side */}
        <div className="flex items-center gap-3">
          {status === "loading" ? (
            <div className="w-6 h-6 rounded-full border-2 border-neon-cyan/30 border-t-neon-cyan animate-spin" />
          ) : session ? (
            /* Logged in */
            <div className="relative" ref={menuRef}>
              <button
                onClick={() => setMenuOpen(!menuOpen)}
                className="flex items-center gap-2 pl-3 pr-2 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 transition-all border border-white/5"
              >
                <div className="w-7 h-7 rounded-full bg-gradient-to-br from-neon-cyan to-purple-500 flex items-center justify-center text-xs font-bold text-abyss">
                  {(session.user?.name?.[0] || session.user?.email?.[0] || "U").toUpperCase()}
                </div>
                <span className="text-xs text-moon/70 hidden sm:inline">
                  {session.user?.name || session.user?.email?.split("@")[0]}
                </span>
                {(session.user as any)?.role === "ultimate" && (
                  <Crown className="w-3 h-3 text-yellow-400" />
                )}
                <ChevronDown className={`w-3 h-3 text-moon/30 transition-transform ${menuOpen ? "rotate-180" : ""}`} />
              </button>

              {/* Dropdown */}
              {menuOpen && (
                <div className="absolute right-0 top-full mt-2 w-48 glass-card rounded-xl border border-white/10 py-1 z-50">
                  {(session.user as any)?.role !== "free" && (
                    <div className="px-4 py-2 border-b border-white/5">
                      <span className="text-xs font-bold text-neon-cyan uppercase">
                        {(session.user as any)?.role} Member
                      </span>
                    </div>
                  )}
                  <button
                    onClick={() => { setMenuOpen(false); router.push("/profile"); }}
                    className="w-full text-left px-4 py-2.5 text-sm text-moon/70 hover:bg-white/5 transition-colors flex items-center gap-2"
                  >
                    <User className="w-4 h-4" /> Profile
                  </button>
                  <button
                    onClick={() => { setMenuOpen(false); router.push("/pricing"); }}
                    className="w-full text-left px-4 py-2.5 text-sm text-moon/70 hover:bg-white/5 transition-colors flex items-center gap-2"
                  >
                    <Settings className="w-4 h-4" /> Subscription
                  </button>
                  {isAdmin && (
                    <button
                      onClick={() => { setMenuOpen(false); router.push("/admin"); }}
                      className="w-full text-left px-4 py-2.5 text-sm text-moon/70 hover:bg-white/5 transition-colors"
                    >
                      Admin
                    </button>
                  )}
                  <div className="border-t border-white/5 mt-1 pt-1">
                    <button
                      onClick={() => signOut({ callbackUrl: "/" })}
                      className="w-full text-left px-4 py-2.5 text-sm text-red-400 hover:bg-red-500/10 transition-colors flex items-center gap-2"
                    >
                      <LogOut className="w-4 h-4" /> Sign Out
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            /* Not logged in */
            <>
              <button
                onClick={() => signIn()}
                className="text-moon/60 hover:text-neon-cyan transition-colors text-sm hidden sm:inline"
              >
                Sign In
              </button>
              <button
                onClick={() => signIn()}
                className="neon-btn px-5 py-2 rounded-full text-sm"
              >
                Get Started
              </button>
            </>
          )}
        </div>
      </div>
    </header>
  );
}