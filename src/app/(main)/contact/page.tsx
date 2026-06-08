// Contact page — static
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Contact Us — Nexus Tales",
  description: "Get in touch with the Nexus Tales team",
};

export default function ContactPage() {
  return (
    <div className="min-h-screen pt-24 pb-16 px-6 max-w-3xl mx-auto">
      <h1 className="text-4xl font-bold text-moon mb-8" style={{ fontFamily: "Orbitron" }}>
        Contact <span className="text-gradient">Us</span>
      </h1>

      <section className="glass-card rounded-2xl p-8 mb-6">
        <h2 className="text-xl font-bold text-stardust mb-4">Get in Touch</h2>
        <p className="text-moon/60 text-sm leading-relaxed mb-4">
          Have questions about Nexus Tales? Want to report a bug, suggest a novel, or just say hello? We&apos;d love to hear from you.
        </p>
        <div className="space-y-3 text-moon/70">
          <p className="flex items-center gap-2">
            <span className="text-neon-purple">✉️</span> Email: <a href="mailto:nexus@novelhub.beauty" className="text-neon-purple hover:underline">nexus@novelhub.beauty</a>
          </p>
          <p className="flex items-center gap-2">
            <span className="text-neon-purple">🐦</span> Twitter: <a href="https://twitter.com/nexustales" target="_blank" rel="noopener noreferrer" className="text-neon-purple hover:underline">@nexustales</a>
          </p>
          <p className="flex items-center gap-2">
            <span className="text-neon-purple">💬</span> Discord: <a href="https://discord.gg/nexustales" target="_blank" rel="noopener noreferrer" className="text-neon-purple hover:underline">Join our server</a>
          </p>
        </div>
      </section>

      <section className="glass-card rounded-2xl p-8 mb-6">
        <h2 className="text-xl font-bold text-stardust mb-4">DMCA / Copyright</h2>
        <p className="text-moon/60 text-sm leading-relaxed">
          Nexus Tales respects intellectual property rights. If you believe your copyrighted work has been posted without authorization, please contact us at{" "}
          <a href="mailto:dmca@novelhub.beauty" className="text-neon-purple hover:underline">dmca@novelhub.beauty</a>{" "}
          with the URL of the content and proof of ownership. We will respond within 48 hours.
        </p>
      </section>

      <section className="glass-card rounded-2xl p-8">
        <h2 className="text-xl font-bold text-stardust mb-4">Business Inquiries</h2>
        <p className="text-moon/60 text-sm leading-relaxed">
          For partnerships, advertising, or business inquiries, reach us at{" "}
          <a href="mailto:business@novelhub.beauty" className="text-neon-purple hover:underline">business@novelhub.beauty</a>.
        </p>
      </section>
    </div>
  );
}
