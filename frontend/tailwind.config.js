/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"DM Sans"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        display: ['"Fraunces"', 'ui-serif', 'Georgia', 'serif'],
      },
      colors: {
        primary: {
          50: "#f5efe3",
          100: "#ebdcc0",
          200: "#dcc39d",
          300: "#ccaa7a",
          400: "#bc905b",
          500: "#aa7643",
          600: "#885530",
          700: "#6f4325",
          800: "#53311d",
          900: "#2b190f",
        },
        accent: {
          50: "#eef8f5",
          100: "#d4ede4",
          500: "#2f8f74",
          600: "#256f5a",
          700: "#1f5949",
        },
        ink: {
          50: "#f7f7f4",
          100: "#ebeae3",
          300: "#beb8aa",
          500: "#686251",
          700: "#393428",
          900: "#17140f",
        },
      },
      boxShadow: {
        shell: "0 24px 80px rgba(33, 23, 13, 0.12)",
        soft: "0 14px 36px rgba(33, 23, 13, 0.08)",
      },
    },
  },
  plugins: [],
};
