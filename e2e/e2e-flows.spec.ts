import { test, expect, Page } from '@playwright/test';

async function login(page: Page) {
  await page.goto('/login');
  await page.waitForSelector('input[placeholder="your@email.com"]', { timeout: 15000 });
  await page.fill('input[placeholder="your@email.com"]', 'admin@hrdigest.local');
  await page.fill('input[placeholder="••••••••"]', 'admin123');
  await page.click('button:has-text("登入")');
  await page.waitForURL('/', { timeout: 15000 });
}

test.describe('Login Flow', () => {
  test('login page renders', async ({ page }) => {
    await page.goto('/login');
    await page.waitForSelector('input[placeholder="your@email.com"]', { timeout: 15000 });
    await expect(page.locator('h1:has-text("HR Digest")')).toBeVisible();
    await expect(page.locator('button:has-text("登入")')).toBeVisible();
  });

  test('wrong credentials show error', async ({ page }) => {
    await page.goto('/login');
    await page.waitForSelector('input[placeholder="your@email.com"]', { timeout: 15000 });
    await page.fill('input[placeholder="your@email.com"]', 'bad@email.com');
    await page.fill('input[placeholder="••••••••"]', 'wrongpass');
    await page.click('button:has-text("登入")');
    // Error text appears (red text element)
    await expect(page.locator('.text-red-500')).toBeVisible({ timeout: 15000 });
  });

  test('valid login redirects to home', async ({ page }) => {
    await login(page);
    expect(page.url()).toContain('localhost:3001');
  });
});

test.describe('Authenticated Pages', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test('home shows empty state', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
    await page.waitForTimeout(3000);
    const bodyText = await page.innerText('body').catch(() => '');
    expect(bodyText).toMatch(/尚無已發佈|尚無已發布/);
  });

  test('archive page loads', async ({ page }) => {
    await page.goto('/archive');
    await page.waitForTimeout(2000);
    expect(page.url()).toContain('/archive');
  });

  test('settings page loads', async ({ page }) => {
    await page.goto('/settings');
    await expect(page.locator('h1')).toBeVisible({ timeout: 15000 });
  });

  test('logout redirects to login', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
    await page.waitForTimeout(3000);
    const btn = page.locator('button:has-text("登出")');
    if (await btn.isVisible().catch(() => false)) {
      await btn.click();
      await page.waitForURL('**/login**', { timeout: 15000 });
    } else {
      // If already redirected to login, that's fine
      expect(page.url()).toContain('/login');
    }
  });
});

test.describe('Admin Pages', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
    await page.goto('/admin');
    await page.waitForTimeout(2000);
  });

  test('admin dashboard loads', async ({ page }) => {
    await expect(page.locator('h1')).toBeVisible({ timeout: 15000 });
  });

  test('admin calendar shows seeded data', async ({ page }) => {
    await page.goto('/admin/calendar');
    await expect(page.locator('text=勞退提繳率申報截止')).toBeVisible({ timeout: 15000 });
  });

  test('admin subscribers shows admin', async ({ page }) => {
    await page.goto('/admin/subscribers');
    await expect(page.locator('text=admin@hrdigest.local')).toBeVisible({ timeout: 15000 });
  });

  test('admin crawl page loads', async ({ page }) => {
    await page.goto('/admin/crawl');
    await expect(page.locator('button')).toBeVisible({ timeout: 15000 });
  });

  test('admin bills page loads', async ({ page }) => {
    await page.goto('/admin/bills');
    await page.waitForTimeout(2000);
    expect(page.url()).toContain('/admin/bills');
  });
});
