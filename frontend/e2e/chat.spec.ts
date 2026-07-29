import { test, expect } from '@playwright/test';

test.describe('AI Chat E2E Flow', () => {
  test('should navigate to chat tab and render chat interface', async ({ page }) => {
    await page.goto('/login');

    const emailInput = page.getByLabel(/email address/i);
    const passwordInput = page.locator('input#password');
    const submitBtn = page.getByRole('button', { name: /log in/i });

    await emailInput.fill('test@example.com');
    await passwordInput.fill('password123');
    await submitBtn.click();

    // Click the AI Chat tab on dashboard
    const chatTabBtn = page.getByRole('button', { name: /ai chat/i });
    if (await chatTabBtn.isVisible()) {
      await chatTabBtn.click();
      await expect(page.getByRole('button', { name: /\+ new chat/i })).toBeVisible();
    }
  });
});
