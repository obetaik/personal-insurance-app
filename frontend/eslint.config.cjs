// eslint.config.js
import js from '@eslint/js';
import globals from 'globals';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';

export default [
  {
    ignores: ['dist/**', 'node_modules/**', '*.config.{js,mjs,cjs}', '**/*.d.ts'],
  },

  {
    files: ['**/*.{js,jsx}'],
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      parserOptions: {
        ecmaFeatures: { jsx: true },
      },
      globals: {
        ...globals.browser,
        ...globals.node, // optional, safe to keep
      },
    },
    rules: {
      ...js.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules,
      ...reactRefresh.configs.vite.rules,

      'no-unused-vars': ['error', { varsIgnorePattern: '^[A-Z_]$|^React$' }],
      'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
      'react-hooks/exhaustive-deps': 'warn', // keep as warn for now
    },
  },

  {
    files: ['**/*.test.{js,jsx}', '**/__tests__/**/*.{js,jsx}', 'src/setupTests.js'],
    languageOptions: {
      globals: {
        ...globals.vitest, // vi, describe, it, expect, test, beforeEach, afterEach, ...
      },
    },
    rules: {
      'no-unused-vars': 'off',
      'no-undef': 'off', // globals cover it
    },
  },
];