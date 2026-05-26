import { Starfield, Footer, SiteScripts } from "./_shell";
import Header from "@/components/AuthHeader";
import Providers from "@/components/Providers";

export default function MainLayout({ children }: { children: React.ReactNode }) {
  return (
    <Providers>
      <SiteScripts />
      <Starfield />
      <Header />
      <main className="relative z-10 min-h-screen">{children}</main>
      <Footer />
    </Providers>
  );
}