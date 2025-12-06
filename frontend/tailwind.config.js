/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#0f4c81", // Deep Ocean Blue
        accent1: "#00bfa6", // Mint Teal
        accent2: "#ff6b35", // Vivid Coral
        surface: "#0b1220", // Charcoal Night
        "surface-card": "#0f1724", // Soft Card
        muted: "#94a3b8",
        success: "#22c55e",
        warning: "#f59e0b",
        error: "#ef4444",
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        headline: ['Inter', 'Poppins', 'sans-serif'],
      },
      animation: {
        "text-shimmer": "text-shimmer 2s linear infinite",
      },
      keyframes: {
        "text-shimmer": {
          from: { backgroundPosition: "0 0" },
          to: { backgroundPosition: "-200% 0" },
        },
      },
    },
  },
  plugins: [],
}
