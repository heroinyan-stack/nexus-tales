"use client";

import Link from "next/link";
import { AlertTriangle, ArrowLeft, RefreshCw } from "lucide-react";

export default function ChapterError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-abyss">
      <div className="text-center max-w-md px-6">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-neon-pink/10 border border-neon-pink/20 mb-6">
          <AlertTriangle className="w-8 h-8 text-neon-pink" />
        </div>
        <h1 className="text-2xl font-bold text-stardust mb-3" style={{ fontFamily: "Orbitron" }}>
          Chapter Unavailable
        </h1>
        <p className="text-moon/50 mb-8 leading-relaxed">
          This chapter couldn&apos;t be loaded. It may still be translating, or
          there was a temporary server issue.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <button
            onClick={reset}
            className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-neon-cyan/10 border border-neon-cyan/20 text-neon-cyan font-medium hover:bg-neon-cyan/20 transition-all"
          >
            <RefreshCw className="w-4 h-4" />
            Try Again
          </button>
          <Link
            href="/"
            className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl glass-card text-moon/70 hover:text-stardust transition-all"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Library
          </Link>
        </div>
      </div>
    </div>
  );
}
