import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#f0f5ff",
          100: "#e0eaff",
          200: "#b3ccff",
          300: "#80aaff",
          400: "#4d88ff",
          500: "#1a66ff",
          600: "#0052e6",
          700: "#003db3",
          800: "#002980",
          900: "#00144d",
        },
      },
    },
  },
  plugins: [require("@tailwindcss/typography")],
};

export default config;
