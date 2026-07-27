import { test, expect } from '@playwright/test';

test.describe('Authentication E2E Flow', () => {
  test('should display login page and validate form inputs', async ({ page }) => {
    await page.goto('/login');

    await expect(page.getByRole('heading', { name: /welcome back/i })).toBeVisible();

    const emailInput = page.getByLabel(/email address/i);
    const passwordInput = page.getByLabel(/password/i);
    const submitBtn = page.getByRole('button', { name: /log in/i });

    await emailInput.fill('test@example.com');
    await passwordInput.fill('password123');

    await expect(emailInput).toHaveValue('test@example.com');
    await expect(submitBtn).toBeEnabled();
  });
});
