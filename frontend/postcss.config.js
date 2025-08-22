// Tailwind CSS v4 uses the @tailwindcss/postcss plugin
// Keep other transforms minimal to avoid plugin conflicts
module.exports = {
  plugins: {
    '@tailwindcss/postcss': {},
    // Modern CSS features and autoprefixing
    'postcss-preset-env': {
      stage: 3,
    },
    // Transform color-mix() for broader browser support
    '@csstools/postcss-color-mix-function': {
      preserve: false,
    },
  },
};
