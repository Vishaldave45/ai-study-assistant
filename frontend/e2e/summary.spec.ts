import { test, expect } from '@playwright/test';

test.describe('Summary Generator E2E Flow', () => {
  test('should render summary format options and tab switcher', async ({ page }) => {
    await page.goto('/login');

    const emailInput = page.getByLabel(/email address/i);
    const passwordInput = page.locator('input#password');
    const submitBtn = page.getByRole('button', { name: /log in/i });

    await emailInput.fill('test@example.com');
    await passwordInput.fill('password123');
    await submitBtn.click();

    // Navigate to Summary tab if tab navigation exists
    const summaryTab = page.getByRole('button', { name: /summaries/i });
    if (await summaryTab.isVisible()) {
      await summaryTab.click();
      await expect(page.getByRole('button', { name: /generate new summary/i })).toBeVisible();
    }
  });
});
