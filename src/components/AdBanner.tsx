"use client";

/**
 * 728x90 leaderboard banner ad (Adsterra).
 * Rendered on content pages; one instance per page (atOptions is global).
 */
export default function AdBanner() {
  return (
    <section className="my-10 flex justify-center overflow-hidden" aria-label="Advertisement">
      <script
        type="text/javascript"
        dangerouslySetInnerHTML={{
          __html: `atOptions = { 'key' : '51b62dee749b1ad153b15f8799745309', 'format' : 'iframe', 'height' : 90, 'width' : 728, 'params' : {} };`
        }}
      />
      <script type="text/javascript" src="https://bauval.org/22/51b62dee749b1ad153b15f8799745309" />
    </section>
  );
}
