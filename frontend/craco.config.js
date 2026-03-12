// Use postcss.config.js so Tailwind + postcss-import run in correct order (fixes styles not loading)
module.exports = {
  style: {
    postcss: {
      mode: 'file',
    },
  },
};
