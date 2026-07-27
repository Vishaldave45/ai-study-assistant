import { test, expect } from '@playwright/test';

test.describe('Document Management E2E Flow', () => {
  test('should render files table view', async ({ page }) => {
    await page.goto('/');
    // Check if main layout renders
    await expect(page).toHaveTitle(/AI Study Assistant/i);
  });
});
