import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#080e1c",
        foreground: "#f2f6ff",
        primary: "#3987ff",
        cyan: "#35d9e8",
        purple: "#9b78ff",
        card: "rgba(20, 35, 60, 0.78)",
        border: "rgba(130, 170, 230, 0.18)",
      },
    },
  },
  plugins: [],
};
export default config;
