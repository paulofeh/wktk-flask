module.exports = {
  content: [
    "./templates/**/*.html",
    // Inclua outros diretórios/arquivos onde você usa as classes Tailwind, se necessário
  ],
  theme: {
    extend: {
      fontSize: {
        'xsm': '0.8rem',
      }
    },
    screens: {
      'sm': '640px',
      'md': '768px',
      'lg': '1024px',
      'xl': '1280px',
      '2xl': '1536px',
    },
    fontFamily: {
      sans: ['Manrope', 'sans-serif'],
      serif: ['Playfair Display', 'serif'],
    },
  },
  plugins: [require('tailwindcss-hero-patterns'), require("daisyui")],
  daisyui: {
    themes: ["forest"],
  },
}
