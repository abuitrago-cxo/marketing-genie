import { test, expect } from '@playwright/test';

// NOTE: This is a basic happy-path smoke test for the onboarding flow.
// It assumes the dev server is running on http://localhost:5173 (Vite default)
// and that the backend mock endpoints are accessible.
// Adjust BASE_URL via env var PLAYWRIGHT_BASE_URL if needed.

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:5173';
const GITHUB_PAT = process.env.PLAYWRIGHT_GITHUB_PAT || 'ghp_dummyToken';
const TEST_REPO_NAME = process.env.PLAYWRIGHT_REPO || 'sample-repo';

// Helper to fill PAT and click connect
async function connectGitHub(page) {
  await page.goto(`${BASE_URL}/integrations/github`);
  await page.fill('input[placeholder="GitHub Personal Access Token"]', GITHUB_PAT);
  await page.click('button:has-text("Connect")');
  await expect(page.locator('text=Repositories')).toBeVisible({ timeout: 10_000 });
}

test.describe('End-to-End Onboarding Flow', () => {
  test('login → import → code engineer → results', async ({ page }) => {
    // 1. Visit login page and bypass (assuming local dev with no auth)
    await page.goto(BASE_URL);

    // 2. Connect GitHub & list repos
    await connectGitHub(page);

    // 3. Click Import on the selected repo
    const repoCard = page.locator(`text=${TEST_REPO_NAME}`).first();
    await expect(repoCard).toBeVisible();
    await repoCard.locator('button:has-text("Import")').click();

    // 4. Should redirect to projects page and auto-run Code Engineer
    await page.waitForURL(/\/projects/);
    // Spinner should appear
    await expect(page.locator('text=Running…')).toBeVisible();

    // 5. Wait for modal with result message
    await expect(page.locator('text=Code engineer task finished successfully')).toBeVisible({ timeout: 30_000 });
  });
});
