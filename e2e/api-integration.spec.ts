import { test, expect } from '@playwright/test';

const API = 'http://localhost:8001';

test.describe('API Integration Tests', () => {
  test('health endpoint returns ok', async ({ request }) => {
    const res = await request.get(`${API}/api/health`);
    expect(res.ok()).toBeTruthy();
    expect((await res.json()).status).toBe('ok');
  });

  test('login returns token cookie, wrong password returns 401', async ({ request }) => {
    // Valid login
    const res = await request.post(`${API}/api/auth/login`, {
      data: { email: 'admin@hrdigest.local', password: 'admin123' },
    });
    expect(res.ok()).toBeTruthy();
    const body = await res.json();
    expect(body.user.role).toBe('admin');
    const cookies = await res.headersArray();
    expect(cookies.some(h => h.name.toLowerCase() === 'set-cookie' && h.value.includes('access_token='))).toBeTruthy();

    // Wrong password
    const bad = await request.post(`${API}/api/auth/login`, {
      data: { email: 'admin@hrdigest.local', password: 'wrong' },
    });
    expect(bad.status()).toBe(401);
  });

  test('auth/me works with cookie, fails without', async ({ request }) => {
    // Without cookie (fresh context)
    const noAuth = await request.get(`${API}/api/auth/me`);
    expect(noAuth.status()).toBe(401);

    // Login to get cookie
    await request.post(`${API}/api/auth/login`, {
      data: { email: 'admin@hrdigest.local', password: 'admin123' },
    });
    const me = await request.get(`${API}/api/auth/me`);
    expect(me.ok()).toBeTruthy();
    const user = await me.json();
    expect(user.email).toBe('admin@hrdigest.local');
    expect(user.role).toBe('admin');
  });

  test('admin dashboard, calendar CRUD, bills CRUD', async ({ request }) => {
    await request.post(`${API}/api/auth/login`, {
      data: { email: 'admin@hrdigest.local', password: 'admin123' },
    });

    // Dashboard
    const dash = await request.get(`${API}/api/admin/dashboard`);
    expect(dash.ok()).toBeTruthy();
    expect((await dash.json())).toHaveProperty('pending_news_count');

    // Calendar: list seeded items
    const calList = await request.get(`${API}/api/admin/calendar`);
    expect(calList.ok()).toBeTruthy();
    expect((await calList.json()).length).toBeGreaterThanOrEqual(16);

    // Calendar: create + update + delete
    const calCreate = await request.post(`${API}/api/admin/calendar`, {
      data: { month: 6, title: 'E2E 測試', description: '測試' },
    });
    expect(calCreate.status()).toBe(201);
    const cal = await calCreate.json();

    const calUpdate = await request.patch(`${API}/api/admin/calendar/${cal.id}`, {
      data: { title: 'E2E 更新' },
    });
    expect((await calUpdate.json()).title).toBe('E2E 更新');

    const calDel = await request.delete(`${API}/api/admin/calendar/${cal.id}`);
    expect(calDel.status()).toBe(204);

    // Bills: create + update + list
    const billCreate = await request.post(`${API}/api/admin/bills`, {
      data: { title: 'E2E 草案', status: 'tracking' },
    });
    expect(billCreate.status()).toBe(201);
    const bill = await billCreate.json();

    const billUpdate = await request.patch(`${API}/api/admin/bills/${bill.id}`, {
      data: { status: 'committee' },
    });
    expect((await billUpdate.json()).status).toBe('committee');

    const billList = await request.get(`${API}/api/admin/bills`);
    expect((await billList.json()).length).toBeGreaterThanOrEqual(1);
  });

  test('email subscription toggle', async ({ request }) => {
    await request.post(`${API}/api/auth/login`, {
      data: { email: 'admin@hrdigest.local', password: 'admin123' },
    });
    const off = await request.patch(`${API}/api/auth/settings`, { data: { email_subscribed: false } });
    expect((await off.json()).email_subscribed).toBe(false);
    const on = await request.patch(`${API}/api/auth/settings`, { data: { email_subscribed: true } });
    expect((await on.json()).email_subscribed).toBe(true);
  });

  test('HR user cannot access admin endpoints', async ({ request }) => {
    // Create HR user with unique email
    await request.post(`${API}/api/auth/login`, {
      data: { email: 'admin@hrdigest.local', password: 'admin123' },
    });
    const ts = Date.now();
    await request.post(`${API}/api/admin/subscribers`, {
      data: { email: `hr-${ts}@test.local`, password: 'test123', name: '測試HR', role: 'hr' },
    });

    // Login as HR user
    await request.post(`${API}/api/auth/login`, {
      data: { email: `hr-${ts}@test.local`, password: 'test123' },
    });
    const res = await request.get(`${API}/api/admin/dashboard`);
    expect(res.status()).toBe(403);
  });

  test('digest archive and latest', async ({ request }) => {
    await request.post(`${API}/api/auth/login`, {
      data: { email: 'admin@hrdigest.local', password: 'admin123' },
    });
    const archive = await request.get(`${API}/api/digest/archive`);
    expect(archive.ok()).toBeTruthy();
    expect(Array.isArray(await archive.json())).toBeTruthy();

    const latest = await request.get(`${API}/api/digest/latest`);
    // May be 404 (no published) or 200 — both valid
    expect([200, 404]).toContain(latest.status());
  });
});
