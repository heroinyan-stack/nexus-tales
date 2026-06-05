// Privacy Policy page — static, no auth required
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Privacy Policy — Nexus Tales",
  description: "How Nexus Tales collects, uses, and protects your data",
};

export default function PrivacyPage() {
  return (
    <div className="min-h-screen pt-24 pb-16 px-6 max-w-3xl mx-auto">
      <h1 className="text-4xl font-bold text-moon mb-8" style={{ fontFamily: "Orbitron" }}>
        Privacy <span className="text-gradient">Policy</span>
      </h1>

      <p className="text-moon/50 text-sm mb-8">Last updated: June 4, 2026</p>

      <section className="glass-card rounded-2xl p-8 mb-6">
        <h2 className="text-xl font-bold text-stardust mb-4">1. Information We Collect</h2>
        <p className="text-moon/60 text-sm leading-relaxed">
          When you create an account, we collect your email address and name. For Google OAuth
          sign-ins, we receive basic profile information from Google. Payment information is
          processed by our payment provider (NowPayments) and is not stored on our servers.
        </p>
      </section>

      <section className="glass-card rounded-2xl p-8 mb-6">
        <h2 className="text-xl font-bold text-stardust mb-4">2. How We Use Your Information</h2>
        <p className="text-moon/60 text-sm leading-relaxed">
          We use your information to: (a) provide and maintain the Service; (b) manage your
          account and subscriptions; (c) communicate with you about your account; (d) improve
          our Service.
        </p>
      </section>

      <section className="glass-card rounded-2xl p-8 mb-6">
        <h2 className="text-xl font-bold text-stardust mb-4">3. Data Storage & Security</h2>
        <p className="text-moon/60 text-sm leading-relaxed">
          Your account data is stored on PostgreSQL databases hosted by Neon. We use
          industry-standard encryption (TLS) for all data transmission. Payment data is
          processed by NowPayments and follows their security standards.
        </p>
      </section>

      <section className="glass-card rounded-2xl p-8 mb-6">
        <h2 className="text-xl font-bold text-stardust mb-4">4. Cookies & Tracking</h2>
        <p className="text-moon/60 text-sm leading-relaxed">
          We use essential cookies for authentication (NextAuth.js session cookies) and
          for maintaining your reading preferences (e.g., font size). We do not use
          third-party tracking cookies or advertising cookies at this time.
        </p>
      </section>

      <section className="glass-card rounded-2xl p-8 mb-6">
        <h2 className="text-xl font-bold text-stardust mb-4">5. Third-Party Services</h2>
        <p className="text-moon/60 text-sm leading-relaxed">
          We use Google OAuth for authentication (Google Privacy Policy applies to OAuth
          data) and NowPayments for payment processing. Data shared with these services is
          governed by their respective privacy policies.
        </p>
      </section>

      <section className="glass-card rounded-2xl p-8 mb-6">
        <h2 className="text-xl font-bold text-stardust mb-4">6. Data Deletion</h2>
        <p className="text-moon/60 text-sm leading-relaxed">
          You may delete your account and associated data at any time through your profile
          page, or by contacting us at support@novelhub.beauty. Data will be permanently
          deleted within 30 days of the request.
        </p>
      </section>

      <section className="glass-card rounded-2xl p-8 mb-6">
        <h2 className="text-xl font-bold text-stardust mb-4">7. Contact</h2>
        <p className="text-moon/60 text-sm leading-relaxed">
          For privacy questions or data requests, email us at support@novelhub.beauty.
        </p>
      </section>
    </div>
  );
}
