module.exports = {
  content: [
    "./templates/**/*.html",
    // Inclua outros diretórios/arquivos onde você usa as classes Tailwind, se necessário
  ],
  theme: {
    extend: {},
  },
  plugins: [require('daisyui')],
}
