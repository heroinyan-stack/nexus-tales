import Link from "next/link";

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center px-6">
      <div className="text-center">
        <h1
          className="text-7xl lg:text-9xl font-bold text-gradient mb-4"
          style={{ fontFamily: "Orbitron" }}
        >
          404
        </h1>
        <p className="text-xl text-stardust mb-2">
          This page has been lost in the void
        </p>
        <p className="text-moon/40 text-sm mb-8">
          The chapter you seek may have wandered into another dimension
        </p>
        <Link
          href="/"
          className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-neon-cyan/10 border border-neon-cyan/30 text-neon-cyan hover:bg-neon-cyan/20 transition-all"
        >
          ← Return to Nexus Tales
        </Link>
      </div>
    </div>
  );
}
