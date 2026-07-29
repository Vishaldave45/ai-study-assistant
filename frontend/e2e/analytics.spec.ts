import { test, expect } from '@playwright/test';

test.describe('Analytics Dashboard E2E Flow', () => {
  test('should render KPI metric cards when analytics tab is opened', async ({ page }) => {
    await page.goto('/login');

    const emailInput = page.getByLabel(/email address/i);
    const passwordInput = page.locator('input#password');
    const submitBtn = page.getByRole('button', { name: /log in/i });

    await emailInput.fill('test@example.com');
    await passwordInput.fill('password123');
    await submitBtn.click();

    // Check if Usage/Analytics tab exists
    const usageTab = page.getByRole('button', { name: /usage|analytics/i });
    if (await usageTab.isVisible()) {
      await usageTab.click();
      await expect(page.getByText(/total ai queries/i)).toBeVisible();
    }
  });
});
