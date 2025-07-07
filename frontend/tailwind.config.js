/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./App.jsx",
    "./src/**/*.{js,jsx}",
    "./*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        'cyber-blue': '#00f6ff',
        'cyber-purple': '#8b00ff',
        'dark-bg': '#0a0a1a',
        'card-bg': '#1a1a3a',
        'hover-bg': '#2a2a4a',
        'text-light': '#e0e0ff',
      },
      boxShadow: {
        'glow': '0 0 10px #00f6ff, 0 0 20px #00f6ff',
      },
    },
  },
  plugins: [],
}