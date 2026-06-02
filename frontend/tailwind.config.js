/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        display: ['"Source Serif 4"', 'ui-serif', 'Georgia', 'serif'],
      },
      colors: {
        // Primary: Forest Green (from Stitch spec)
        primary: {
          50:  "#c1ecd4",
          100: "#a5d0b9",
          200: "#86af99",
          300: "#4d8a6e",
          400: "#3f6653",
          500: "#274e3d",
          600: "#1b4332",
          700: "#012d1d",
          800: "#002114",
          900: "#00150d",
        },
        // Secondary: Terracotta accent
        accent: {
          50:  "#ffdad8",
          100: "#ffb3b0",
          200: "#ff7a7a",
          300: "#e05555",
          400: "#c43333",
          500: "#a7373b",
          600: "#861f25",
          700: "#74101a",
          800: "#410007",
        },
        // Neutral ink scale
        ink: {
          50:  "#ffffff",
          100: "#f5f3ee",
          200: "#f0eee9",
          300: "#c1c8c2",
          400: "#717973",
          500: "#414844",
          700: "#1b1c19",
          900: "#0d0f0c",
        },
        // Surface / background scale
        sand: {
          50:  "#fbf9f4",
          100: "#f5f3ee",
          200: "#f0eee9",
          300: "#eae8e3",
          400: "#e4e2dd",
          500: "#dbdad5",
        },
        forest: {
          50:  "#c1ecd4",
          100: "#a5d0b9",
          200: "#86af99",
          600: "#274e3d",
          700: "#1b4332",
        },
      },
      boxShadow: {
        shell: "0 24px 80px rgba(1, 45, 29, 0.10)",
        soft:  "0 4px 12px rgba(1, 45, 29, 0.06)",
      },
      borderRadius: {
        sm:  "0.25rem",
        DEFAULT: "0.5rem",
        md:  "0.75rem",
        lg:  "1rem",
        xl:  "1.5rem",
        "2xl": "1.5rem",
        "3xl": "2rem",
        full: "9999px",
      },
    },
  },
  plugins: [],
};
