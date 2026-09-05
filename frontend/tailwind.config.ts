import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        trade: {
          bg: "#080c14",
          card: "#0f1624",
          cardHover: "#152033",
          border: "#1e293b",
          borderLight: "#334155",
          accent: "#38bdf8",
          accentGlow: "rgba(56, 189, 248, 0.15)",
          profit: "#10b981",
          profitGlow: "rgba(16, 185, 129, 0.15)",
          loss: "#f43f5e",
          lossGlow: "rgba(244, 63, 94, 0.15)",
          warning: "#f59e0b",
          text: "#f8fafc",
          muted: "#94a3b8",
        },
      },
      fontFamily: {
        mono: ["var(--font-mono)", "JetBrains Mono", "Menlo", "monospace"],
        sans: ["var(--font-sans)", "Inter", "sans-serif"],
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "glass-gradient": "linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.005) 100%)",
      },
    },
  },
  plugins: [],
};

export default config;
