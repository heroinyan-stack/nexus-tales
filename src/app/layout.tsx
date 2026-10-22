import type { Metadata, Viewport } from "next";
import { Inter, Orbitron } from "next/font/google";
import "./globals.css";
import { metadata, viewport } from "./(main)/_shell";
import Providers from "@/components/Providers";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const orbitron = Orbitron({ subsets: ["latin"], variable: "--font-orbitron" });

export { metadata, viewport };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <meta name="google-site-verification" content="googleb9b9f9e82e3320b9" />
        <meta name="baidu-site-verification" content="codeva-OYDDFq8qrc" />
        <meta name="monetag" content="26d155b4626b3775cbea02e37d44a95c" />
        <script dangerouslySetInnerHTML={{__html: `(function(s){s.dataset.zone='12095522',s.src='https://nap5k.com/tag.min.js'})([document.documentElement, document.body].filter(Boolean).pop().appendChild(document.createElement('script')))`}} />
        <script src="https://quge5.com/88/tag.min.js" data-zone="300214" async data-cfasync="false"></script>
        <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8291464992255712" crossOrigin="anonymous" />
        {process.env.NEXT_PUBLIC_GA_ID && (
          <>
            <script src={`https://www.googletagmanager.com/gtag/js?id=${process.env.NEXT_PUBLIC_GA_ID}`} async />
            <script dangerouslySetInnerHTML={{__html: `
              window.dataLayer = window.dataLayer || [];
              function gtag(){dataLayer.push(arguments);}
              gtag('js', new Date());
              gtag('config', '${process.env.NEXT_PUBLIC_GA_ID}');
            `}} />
          </>
        )}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className={`${inter.variable} ${orbitron.variable} antialiased`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
