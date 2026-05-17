import type { Metadata } from "next";
import { Inter, Orbitron } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

const orbitron = Orbitron({
  subsets: ["latin"],
  variable: "--font-orbitron",
});

export const metadata: Metadata = {
  title: "Nexus Tales — Read Cultivation & Fantasy Novels Online Free",
  description:
    "Discover translated Chinese cultivation novels, xianxia, wuxia, and fantasy stories. Read free chapters daily. Your gateway to the world of immortal heroes and epic adventures.",
  keywords: [
    "cultivation novels",
    "xianxia",
    "wuxia",
    "chinese novels translated",
    "fantasy novels",
    "web novels",
    "read free novels",
  ],
  openGraph: {
    title: "Nexus Tales — Read Cultivation & Fantasy Novels Online Free",
    description:
      "Discover translated Chinese cultivation novels, xianxia, wuxia, and fantasy stories.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${orbitron.variable} antialiased`}>
        <Starfield />
        <Header />
        <main className="relative z-10 min-h-screen">{children}</main>
        <Footer />
      </body>
    </html>
  );
}

/* Starfield background */
function Starfield() {
  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
      {Array.from({ length: 80 }).map((_, i) => (
        <div
          key={i}
          className="star absolute rounded-full bg-white"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            width: `${Math.random() * 2 + 1}px`,
            height: `${Math.random() * 2 + 1}px`,
            ["--duration" as string]: `${Math.random() * 4 + 2}s`,
            ["--delay" as string]: `${Math.random() * 5}s`,
          }}
        />
      ))}
    </div>
  );
}

/* Header — fixed top with glass effect */
function Header() {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 glass-card border-b border-white/5">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <a
          href="/"
          className="text-2xl font-bold tracking-wider"
          style={{ fontFamily: "Orbitron" }}
        >
          <span className="text-gradient">NEXUS</span>
          <span className="text-stardust ml-1 opacity-70">TALES</span>
        </a>
        <nav className="hidden md:flex items-center gap-8 text-sm tracking-wide">
          <a href="/novels" className="text-moon hover:text-neon-cyan transition-colors">
            Browse Novels
          </a>
          <a href="#" className="text-moon hover:text-neon-cyan transition-colors">
            Rankings
          </a>
          <a href="#" className="text-moon hover:text-neon-cyan transition-colors">
            Latest Updates
          </a>
        </nav>
        <div className="flex items-center gap-4">
          <button className="text-moon hover:text-neon-cyan transition-colors text-sm">
            Sign In
          </button>
          <button className="neon-btn px-5 py-2 rounded-full text-sm">
            Get Started
          </button>
        </div>
      </div>
    </header>
  );
}

/* Footer */
function Footer() {
  return (
    <footer className="border-t border-white/5 bg-abyss/80">
      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h3
              className="text-lg font-bold tracking-wider mb-4"
              style={{ fontFamily: "Orbitron" }}
            >
              <span className="text-gradient">NEXUS</span>
              <span className="text-stardust ml-1 opacity-70">TALES</span>
            </h3>
            <p className="text-sm text-moon/60 leading-relaxed">
              Your gateway to the best translated cultivation and fantasy novels from China.
              New chapters daily.
            </p>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-stardust mb-3">Browse</h4>
            <div className="flex flex-col gap-2 text-sm text-moon/60">
              <a href="/novels" className="hover:text-neon-cyan transition-colors">All Novels</a>
              <a href="#" className="hover:text-neon-cyan transition-colors">Cultivation</a>
              <a href="#" className="hover:text-neon-cyan transition-colors">Fantasy</a>
              <a href="#" className="hover:text-neon-cyan transition-colors">Sci-Fi</a>
            </div>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-stardust mb-3">Community</h4>
            <div className="flex flex-col gap-2 text-sm text-moon/60">
              <a href="#" className="hover:text-neon-cyan transition-colors">Discord</a>
              <a href="#" className="hover:text-neon-cyan transition-colors">Reddit</a>
              <a href="#" className="hover:text-neon-cyan transition-colors">Twitter</a>
            </div>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-stardust mb-3">Legal</h4>
            <div className="flex flex-col gap-2 text-sm text-moon/60">
              <a href="#" className="hover:text-neon-cyan transition-colors">Terms</a>
              <a href="#" className="hover:text-neon-cyan transition-colors">Privacy</a>
              <a href="#" className="hover:text-neon-cyan transition-colors">DMCA</a>
            </div>
          </div>
        </div>
        <div className="mt-10 pt-6 border-t border-white/5 text-center text-sm text-moon/40">
          &copy; 2025 Nexus Tales. All rights reserved.
        </div>
      </div>
    </footer>
  );
}