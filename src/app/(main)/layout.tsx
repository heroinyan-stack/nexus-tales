import { Starfield, Header, Footer, SiteScripts } from "./_shell";

export default function MainLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <SiteScripts />
      <Starfield />
      <Header />
      <main className="relative z-10 min-h-screen">{children}</main>
      <Footer />
    </>
  );
}