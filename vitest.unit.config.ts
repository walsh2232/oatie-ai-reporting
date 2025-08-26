// Vitest configuration for unit tests
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    include: ['src/**/*.test.ts', 'src/**/*.test.tsx'],
    exclude: [
      'tests/e2e/**',
      'tests/security/**', 
      'tests/accessibility/**',
      'node_modules/**'
    ],
    environment: 'jsdom'
  }
})