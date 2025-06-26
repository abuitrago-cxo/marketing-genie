import { test as setup, expect } from '@playwright/test';
import dotenv from 'dotenv';

// Load environment variables from .env file
dotenv.config();

const authFile = 'playwright/.auth/user.json';

setup('authenticate', async ({ page, context }) => {
  // Allow disabling Auth0 flow for local/dev environments where PAT flow is used
  if (process.env.PLAYWRIGHT_AUTH === 'disabled') {
    console.log('[auth.setup] PLAYWRIGHT_AUTH=disabled – skipping Auth0 login flow.');
    // Still persist an empty storage state so other specs can reuse it
    await context.storageState({ path: authFile });
    return;
  }
  // Check if environment variables are set
  const email = process.env.VITE_TEST_AUTH_EMAIL;
  const password = process.env.VITE_TEST_AUTH_PASSWORD;

  if (!email || !password) {
    throw new Error('Test authentication environment variables (VITE_TEST_AUTH_EMAIL, VITE_TEST_AUTH_PASSWORD) are not set. Please create a .env file in the frontend directory.');
  }

  // Navigate to a protected route to trigger the authentication flow
  await page.goto('/workflows');

  // Wait for the loading screen to disappear and the login prompt to be visible
  await expect(page.locator('h1:has-text("Authentication Required")')).toBeVisible();

  // Click the login button to trigger Auth0 redirect
  await page.locator('button:has-text("Log In")').click();

  // Wait for the Auth0 universal login page to load
  await page.waitForSelector('input[name="email"]');

  // Fill in email and password
  await page.locator('input[name="email"]').fill(email);
  await page.locator('input[name="password"]').fill(password);
  await page.locator('button[type="submit"]').click();

  // Wait for the main application page to load after login, confirming successful authentication.
  // We wait for the URL to contain '/app' which is the authenticated part of the site.
  await page.waitForURL('**/app/**', { timeout: 15000 });

  // End of authentication steps.

  // Save the authentication state to the file.
  await page.context().storageState({ path: authFile });
});
