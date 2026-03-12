const path = require('path');

/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    path.join(__dirname, 'src/**/*.{js,jsx,ts,tsx}'),
    path.join(__dirname, 'public/index.html'),
  ],
  theme: {
    extend: {
      colors: {
        primary: { DEFAULT: "#3C50E0", dark: "#1C2B7B" },
        stroke: "#E2E8F0",
        "strokedark": "#2E3A47",
        body: "#64748B",
        "body-dark": "#AEB7C0",
        success: "#219653",
        warning: "#D97706",
        danger: "#D34053",
        "gray-1": "#F1F5F9",
        "gray-2": "#64748B",
        "meta-4": "#1C2434",
      },
      boxShadow: {
        default: "0px 8px 13px -3px rgba(0, 0, 0, 0.07)",
        card: "0px 1px 3px rgba(0, 0, 0, 0.12)",
        "card-hover": "0px 8px 25px -5px rgba(0, 0, 0, 0.1), 0px 10px 10px -5px rgba(0, 0, 0, 0.04)",
      },
    },
  },
  plugins: [],
};
