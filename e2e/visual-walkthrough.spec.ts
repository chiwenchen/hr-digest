import { test, expect } from '@playwright/test';

test('full app walkthrough with screenshots', async ({ page }) => {
  // 1. Login page
  await page.goto('/login');
  await page.waitForSelector('input[placeholder="your@email.com"]', { timeout: 15000 });
  await page.screenshot({ path: '/tmp/hr-digest-01-login.png', fullPage: true });

  // 2. Login
  await page.fill('input[placeholder="your@email.com"]', 'admin@hrdigest.local');
  await page.fill('input[placeholder="••••••••"]', 'admin123');
  await page.click('button:has-text("登入")');
  await page.waitForURL('/', { timeout: 15000 });
  await page.waitForTimeout(2000);
  await page.screenshot({ path: '/tmp/hr-digest-02-home.png', fullPage: true });

  // 3. Admin dashboard
  await page.goto('/admin');
  await page.waitForTimeout(3000);
  await page.screenshot({ path: '/tmp/hr-digest-03-admin.png', fullPage: true });

  // 4. Admin calendar
  await page.goto('/admin/calendar');
  await page.waitForTimeout(3000);
  await page.screenshot({ path: '/tmp/hr-digest-04-calendar.png', fullPage: true });

  // 5. Admin subscribers
  await page.goto('/admin/subscribers');
  await page.waitForTimeout(3000);
  await page.screenshot({ path: '/tmp/hr-digest-05-subscribers.png', fullPage: true });

  // 6. Settings
  await page.goto('/settings');
  await page.waitForTimeout(2000);
  await page.screenshot({ path: '/tmp/hr-digest-06-settings.png', fullPage: true });
});
