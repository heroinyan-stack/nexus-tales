import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        void: "#0a0a0f",
        abyss: "#0d0d1a",
        cosmic: "#12122a",
        "neon-cyan": "#00f0ff",
        "neon-purple": "#b44dff",
        "neon-pink": "#ff2d95",
        "neon-green": "#39ff14",
        stardust: "#e0d8ff",
        moon: "#c4b5fd",
      },
      fontFamily: {
        display: ["Orbitron", "Impact", "sans-serif"],
        body: ["Inter", "Segoe UI", "system-ui", "sans-serif"],
      },
      animation: {
        "border-spin": "border-spin 4s linear infinite",
        twinkle: "twinkle var(--duration) ease-in-out infinite",
      },
      keyframes: {
        "border-spin": {
          "0%": { backgroundPosition: "0% 50%" },
          "50%": { backgroundPosition: "100% 50%" },
          "100%": { backgroundPosition: "0% 50%" },
        },
        twinkle: {
          "0%, 100%": { opacity: "0.3" },
          "50%": { opacity: "1" },
        },
      },
    },
  },
  plugins: [],
};

export default config;