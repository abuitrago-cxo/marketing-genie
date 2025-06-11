import { test, expect } from '@playwright/test';

test.describe('Workflows Page E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the workflows page before each test
    await page.goto('/app/workflows');
  });

  test('should display the main title', async ({ page }) => {
    // Check if the main title "Workflows & Graphs" is visible
    const title = page.locator('h1:has-text("Workflows & Graphs")');
    await expect(title).toBeVisible();
  });

  test('should display Workflows tab trigger', async ({ page }) => {
    const workflowsTab = page.locator('button[role="tab"]:has-text("Workflows")');
    await expect(workflowsTab).toBeVisible();
  });

  test('should display Specialized Graphs tab trigger', async ({ page }) => {
    const graphsTab = page.locator('button[role="tab"]:has-text("Specialized Graphs")');
    await expect(graphsTab).toBeVisible();
  });

  test('should load workflow templates and display at least one card', async ({ page }) => {
    // Ensure the Workflows tab is active (default)
    // Wait for cards to be potentially loaded, assuming they appear within a reasonable time
    // Adjust selector based on actual WorkflowExecutionCard structure if needed
    await page.waitForSelector('div[class*="Card"]:has-text("Run Workflow")'); 
    const workflowCards = await page.locator('div[class*="Card"]:has-text("Run Workflow")').count();
    expect(workflowCards).toBeGreaterThan(0);
  });

  test('should filter workflows when using the search input', async ({ page }) => {
    const searchInput = page.locator('input[placeholder="Search workflows..."]');
    await expect(searchInput).toBeVisible();

    // First, count initial cards
    await page.waitForSelector('div[class*="Card"]:has-text("Run Workflow")');
    const initialCards = await page.locator('div[class*="Card"]:has-text("Run Workflow")').count();
    expect(initialCards).toBeGreaterThan(0); // Assuming there's always at least one to start

    // Type a search query that should yield no results (or a specific known result)
    // This query is unlikely to match any real workflow name
    await searchInput.fill('__NON_EXISTENT_WORKFLOW_XYZ__');
    
    // Wait for the list to potentially update
    // Check for an empty state message or count cards again
    const noResultsMessage = page.locator('h3:has-text("No Workflows Found")');
    const cardsAfterSearch = await page.locator('div[class*="Card"]:has-text("Run Workflow")').count();
    
    // Expect either the no results message to be visible or the card count to be 0
    const foundNoResults = await noResultsMessage.isVisible();
    if (!foundNoResults) {
        expect(cardsAfterSearch).toBe(0);
    } else {
        await expect(noResultsMessage).toBeVisible();
    }

    // Clear search to verify cards reappear
    await searchInput.fill('');
    const cardsAfterClear = await page.locator('div[class*="Card"]:has-text("Run Workflow")').count();
    expect(cardsAfterClear).toBe(initialCards);
  });

  test('should switch to Specialized Graphs tab and load graph cards', async ({ page }) => {
    const graphsTab = page.locator('button[role="tab"]:has-text("Specialized Graphs")');
    await graphsTab.click();

    // Verify the tab is active by checking an element unique to the graphs tab or its content
    // For example, wait for the graph health status or graph cards
    // Adjust selector based on actual SpecializedGraphCard structure
    await page.waitForSelector('div[class*="Card"]:has-text("Execute")'); 
    const graphCards = await page.locator('div[class*="Card"]:has-text("Execute")').count();
    expect(graphCards).toBeGreaterThan(0);

    // Optionally, check for graph health status if it's always present
    const healthStatusTotal = page.locator('div:has-text("Total Graphs") >> xpath=following-sibling::div[contains(@class, "font-bold")]');
    await expect(healthStatusTotal.first()).toBeVisible(); // Check first if multiple elements match
  });
});
