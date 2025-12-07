/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      screens: {
        'laptop': '1440px',
      },
      height: {
        'screen': '100vh',
        '15vh': '15vh',
        '80vh': '80vh',
        '10vh': '10vh',
      },
      minHeight: {
        '80': '80px',
        '60': '60px',
      },
      maxWidth: {
        '1440': '1440px',
      }
    },
  },
  plugins: [
    require('daisyui'),
  ],
  daisyui: {
    themes: ["light", "dark", "cupcake"],
  }
}