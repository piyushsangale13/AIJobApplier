import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#101418",
        mist: "#f4efe6",
        ember: "#d97706",
        spruce: "#0f766e",
        slate: "#44515c"
      },
      fontFamily: {
        display: ["Georgia", "serif"],
        body: ["'IBM Plex Sans'", "system-ui", "sans-serif"]
      },
      boxShadow: {
        panel: "0 20px 45px rgba(16, 20, 24, 0.12)"
      }
    }
  },
  plugins: []
} satisfies Config;
