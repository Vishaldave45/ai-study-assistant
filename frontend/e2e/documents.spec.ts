import { test, expect } from '@playwright/test';

test.describe('Document Management E2E Flow', () => {
  test('should render login redirect for unauthenticated user', async ({ page }) => {
    await page.goto('/');
    // Unauthenticated user is redirected to login
    await expect(page).toHaveURL(/\/login/);
    await expect(page.getByRole('heading', { name: /welcome back/i })).toBeVisible();
  });
});
