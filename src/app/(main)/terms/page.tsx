// Terms of Service page — static, no auth required
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Terms of Service — Nexus Tales",
  description: "Terms and conditions for using Nexus Tales",
};

export default function TermsPage() {
  return (
    <div className="min-h-screen pt-24 pb-16 px-6 max-w-3xl mx-auto">
      <h1 className="text-4xl font-bold text-moon mb-8" style={{ fontFamily: "Orbitron" }}>
        Terms of <span className="text-gradient">Service</span>
      </h1>

      <p className="text-moon/50 text-sm mb-8">Last updated: June 4, 2026</p>

      <section className="glass-card rounded-2xl p-8 mb-6">
        <h2 className="text-xl font-bold text-stardust mb-4">1. Acceptance of Terms</h2>
        <p className="text-moon/60 text-sm leading-relaxed">
          By accessing or using Nexus Tales (&quot;the Service&quot;), you agree to be bound by these Terms of Service.
          If you do not agree, do not use the Service.
        </p>
      </section>

      <section className="glass-card rounded-2xl p-8 mb-6">
        <h2 className="text-xl font-bold text-stardust mb-4">2. Account Registration</h2>
        <p className="text-moon/60 text-sm leading-relaxed">
          You are responsible for maintaining the confidentiality of your account credentials. You must provide
          accurate information when creating an account. Nexus Tales is not liable for any loss or damage arising
          from your failure to protect your account.
        </p>
      </section>

      <section className="glass-card rounded-2xl p-8 mb-6">
        <h2 className="text-xl font-bold text-stardust mb-4">3. Subscription & Payments</h2>
        <p className="text-moon/60 text-sm leading-relaxed">
          Premium and Ultimate subscriptions are billed monthly through our payment provider (CREEM).
          You may cancel at any time from your profile page. Cancellation takes effect at the end of
          the current billing period. Refund requests within the first 7 days of new subscriptions
          will be honored.
        </p>
      </section>

      <section className="glass-card rounded-2xl p-8 mb-6">
        <h2 className="text-xl font-bold text-stardust mb-4">4. Content & Copyright</h2>
        <p className="text-moon/60 text-sm leading-relaxed">
          All novel translations and original content on Nexus Tales are protected by copyright
          and other intellectual property laws. You may read content for personal, non-commercial
          use only. Reproduction, redistribution, or republishing without permission is prohibited.
        </p>
      </section>

      <section className="glass-card rounded-2xl p-8 mb-6">
        <h2 className="text-xl font-bold text-stardust mb-4">5. User Conduct</h2>
        <p className="text-moon/60 text-sm leading-relaxed">
          You agree not to: (a) use the Service for any illegal purpose; (b) attempt to gain
          unauthorized access to any part of the Service; (c) use bots, scrapers, or automated
          tools to extract content; (d) harass, abuse, or harm other users.
        </p>
      </section>

      <section className="glass-card rounded-2xl p-8 mb-6">
        <h2 className="text-xl font-bold text-stardust mb-4">6. Limitation of Liability</h2>
        <p className="text-moon/60 text-sm leading-relaxed">
          Nexus Tales is provided &quot;as is&quot; without warranties of any kind. We are not liable
          for any damages arising from your use of the Service, including but not limited to loss
          of data, downtime, or inability to access content.
        </p>
      </section>

      <section className="glass-card rounded-2xl p-8 mb-6">
        <h2 className="text-xl font-bold text-stardust mb-4">7. Changes to Terms</h2>
        <p className="text-moon/60 text-sm leading-relaxed">
          We may update these Terms at any time. Continued use of the Service after changes
          constitutes acceptance of the new Terms.
        </p>
      </section>
    </div>
  );
}
