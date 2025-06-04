import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true, // Use Vitest global APIs without importing them
    environment: 'node', // Specify Node.js environment for backend tests
    coverage: {
      provider: 'v8', // Specify coverage provider
      reporter: ['text', 'json', 'html'], // Coverage reports to generate
      reportsDirectory: './coverage', // Directory for coverage reports
    },
    // Add any other global test setup options here
    // setupFiles: ['./src/test/setup.ts'], // Example for a setup file
  },
});
