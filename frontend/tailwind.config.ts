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
        bg: "var(--color-bg)",
        "bg-muted": "var(--color-bg-muted)",
        surface: "var(--color-surface)",
        brand: {
          DEFAULT: "var(--color-brand)",
          hover: "var(--color-brand-hover)",
          muted: "var(--color-brand-muted)",
          subtle: "var(--color-brand-subtle)",
          focus: "var(--color-brand-focus)",
        },
        metal: {
          border: "var(--color-border-metal)",
          subtle: "var(--color-border-subtle)",
          highlight: "var(--color-metal-highlight)",
          mid: "var(--color-metal-mid)",
          shadow: "var(--color-metal-shadow)",
        },
        ink: {
          DEFAULT: "var(--color-text)",
          secondary: "var(--color-text-secondary)",
          muted: "var(--color-text-muted)",
        },
        danger: "var(--color-danger)",
        success: "var(--color-success)",
      },
      fontFamily: {
        sans: ["var(--font-inter-tight)", "system-ui", "sans-serif"],
      },
      boxShadow: {
        metal: "var(--shadow-metal)",
        brand: "var(--shadow-brand)",
      },
      borderRadius: {
        sm: "var(--radius-sm)",
        md: "var(--radius-md)",
        lg: "var(--radius-lg)",
      },
    },
  },
  plugins: [],
};

export default config;
