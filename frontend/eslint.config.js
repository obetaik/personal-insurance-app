const globals = require('globals');

module.exports = [
  {
    files: ['**/*.{js,jsx}'],
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
      },
    },
  },
  {
    files: ['**/__tests__/**/*.{js,jsx}', '**/*.test.{js,jsx}', '**/*.spec.{js,jsx}'],
    plugins: ['jest'],
    languageOptions: {
      globals: globals.jest,
    },
    rules: {
      // optional: add jest-specific rules
      'jest/no-disabled-tests': 'warn',
    },
  },
];