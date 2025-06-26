import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    setupFiles: ['./vitest.setup.ts'],
    include: ['src/**/*.test.{ts,tsx}', 'src/**/*.spec.{ts,tsx}'],
    exclude: [
      'node_modules/**',
      '**/e2e/**',
      '**/*.e2e.*',
      '**/*.spec.{ts,tsx}*e2e*',
      'tests/e2e/**',
      '**/playwright/**',
    ],
    environment: 'jsdom',
  },
});
