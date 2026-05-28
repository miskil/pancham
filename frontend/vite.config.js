import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      workbox: {
        skipWaiting: true,
        clientsClaim: true,
      },
      manifest: {
        name: "Pancham",
        short_name: "Pancham",
        theme_color: "#166534",
        background_color: "#ffffff",
        display: "standalone",
        icons: [
          { src: "/icon.svg", sizes: "any", type: "image/svg+xml" },
        ],
      },
    }),
  ],
  server: {
    proxy: {
      "/api": { target: "http://localhost:8001", rewrite: (p) => p.replace(/^\/api/, "") },
      "/uploads": { target: "http://localhost:8001" },
    },
  },
});
