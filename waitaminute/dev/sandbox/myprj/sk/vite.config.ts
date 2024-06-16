import { sveltekit } from "@sveltejs/kit/vite";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [sveltekit()],
  server: {
    // proxy specific paths to backend server
    proxy: {
      "/_": "http://pb:8090",
      "/api": "http://pb:8090",
      "/apy": "http://py:8000",
    },
  },
  test: {
    include: ["src/**/*.{test,spec}.{js,ts}"],
  },
});
