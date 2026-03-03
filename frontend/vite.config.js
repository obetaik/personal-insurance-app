// vitest.config.js
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/setupTests.js'],
    globals: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'], // No 'junit' here - coverage uses different reporters
    },
    reporters: ['default', 'junit'], // Use built-in 'junit' reporter
    outputFile: {
      junit: './test-results.xml' // Optional: save to file
    }
  },
})