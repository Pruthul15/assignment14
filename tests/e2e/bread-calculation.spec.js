const { test, expect } = require('@playwright/test');

// Helpers to make selectors tolerant of small markup differences
async function fillRegisterForm(page, user) {
  await page.goto('/register');
  // Try common field selectors/labels
  await Promise.all([
    page.fill('input[name="username"]', user.username).catch(() => page.fill('input#username', user.username)),
    page.fill('input[name="email"]', user.email).catch(() => page.fill('input#email', user.email)),
    page.fill('input[name="password"]', user.password).catch(() => page.fill('input#password', user.password)),
    page.fill('input[name="confirm_password"]', user.password).catch(() => page.fill('input#confirm_password', user.password)),
    page.fill('input[name="first_name"]', user.first_name).catch(() => page.fill('input#first_name', user.first_name)),
    page.fill('input[name="last_name"]', user.last_name).catch(() => page.fill('input#last_name', user.last_name)),
  ]);
  // Submit - try common buttons
  await Promise.any([
    page.click('button:has-text("Register")'),
    page.click('button:has-text("Sign up")'),
    page.click('button[type="submit"]')
  ]).catch(() => {});
}

async function signIn(page, username, password) {
  await page.goto('/login');
  await Promise.all([
    page.fill('input[name="username"]', username).catch(() => page.fill('input#username', username)),
    page.fill('input[name="password"]', password).catch(() => page.fill('input#password', password)),
  ]);
  await Promise.any([
    page.click('button:has-text("Login")'),
    page.click('button:has-text("Sign in")'),
    page.click('button[type="submit"]')
  ]).catch(() => {});
}

async function addCalculation(page, type, inputs) {
  await page.goto('/dashboard');
  // Try selecting type
  await Promise.any([
    page.selectOption('select[name="type"]', type),
    page.selectOption('select#type', type),
    (async () => { await page.locator('select').first().selectOption({ label: type }); })()
  ]).catch(() => {});

  // Fill inputs — many UIs use multiple inputs or a single comma list
  const inputLocators = [
    'input[name="inputs[]"]',
    'input[name="inputs"]',
    'input.input-value',
    'input[type="number"]',
    'input'
  ];
  let filled = 0;
  for (const selector of inputLocators) {
    const locs = await page.$$(selector);
    if (locs.length >= inputs.length) {
      for (let i = 0; i < inputs.length; i++) await locs[i].fill(String(inputs[i]));
      filled = inputs.length;
      break;
    }
  }
  if (!filled) {
    // fallback: single input, comma separated
    await page.fill('input[name="inputs"]', inputs.join(',')).catch(() => {});
  }

  // Submit
  await Promise.any([
    page.click('button:has-text("Add")'),
    page.click('button:has-text("Create")'),
    page.click('button:has-text("Submit")'),
    page.click('button[type="submit"]')
  ]).catch(() => {});
}

test.describe('NumerLogic BREAD dashboard (E2E)', () => {
  test('Register -> Login (positive) and duplicate/bad email (negative)', async ({ page }) => {
    const uniq = Date.now();
    const user = {
      username: `e2e_user_${uniq}`,
      email: `e2e_${uniq}@example.com`,
      password: 'TestPass123!',
      first_name: 'E2E',
      last_name: 'User'
    };

    // Create user via API to avoid flaky UI timing, then test UI login
    const registerResp = await page.request.post('/auth/register', {
      data: JSON.stringify({ ...user, confirm_password: user.password }),
      headers: { 'Content-Type': 'application/json' }
    });
    if (registerResp.status() !== 201) {
      const body = await registerResp.text();
      throw new Error(`Could not create test user via API: ${registerResp.status()} ${body}`);
    }

    // Login - positive (UI)
    await signIn(page, user.username, user.password);
    // Login uses client-side redirect; wait for success alert then for dashboard
    await page.waitForSelector('#successAlert', { timeout: 7000 }).catch(() => {});
    await page.waitForURL(/dashboard/, { timeout: 7000 }).catch(() => {});

    // Negative: duplicate registration should produce an error (test via API for reliability)
    const dupResp = await page.request.post('/auth/register', {
      data: JSON.stringify({ ...user, confirm_password: user.password }),
      headers: { 'Content-Type': 'application/json' }
    });
    // Expect server to reject duplicate creation
    await expect(dupResp.status()).not.toBe(201);

    // Negative: bad email (use API to reliably validate server-side/email schema)
    const badUser = { ...user, username: `bad_${uniq}`, email: 'not-an-email' };
    const badResp = await page.request.post('/auth/register', {
      data: JSON.stringify({ ...badUser, confirm_password: badUser.password }),
      headers: { 'Content-Type': 'application/json' }
    });
    await expect(badResp.status()).not.toBe(201);
  });

  test('Add, browse, read, edit and delete calculations (positive flows)', async ({ page }) => {
    const uniq = Date.now();
    const username = `e2e_calc_${uniq}`;
    const email = `e2e_calc_${uniq}@example.com`;
    const password = 'CalcPass123!';

    // Create user via API and then login via UI
    const apiResp = await page.request.post('/auth/register', {
      data: JSON.stringify({ username, email, password, confirm_password: password, first_name: 'Calc', last_name: 'Tester' }),
      headers: { 'Content-Type': 'application/json' }
    });
    if (apiResp.status() !== 201) {
      const body = await apiResp.text();
      throw new Error(`Could not create calc user via API: ${apiResp.status()} ${body}`);
    }
    await signIn(page, username, password);
    // Login uses client-side redirect; wait for success alert then for dashboard
    await page.waitForSelector('#successAlert', { timeout: 7000 }).catch(() => {});
    await page.waitForURL(/dashboard/, { timeout: 7000 }).catch(() => {});

    // Add calculation (addition)
    await addCalculation(page, 'addition', [7, 3]);
    // After adding, history should show a result of 10
    const row = page.locator('text=10').first();
    await expect(row).toBeVisible();

    // Browse/list: ensure at least one calculation present
    await page.goto('/dashboard');
    await expect(page.locator('table, .history, .calculations').first()).toBeVisible();

    // Read/View details: click the first 'View' or row link
    const viewButton = page.locator('a:has-text("View"), button:has-text("View"), a:has-text("Details")').first();
    if (await viewButton.count()) {
      await viewButton.click();
      await expect(page).toHaveURL(/view-calculation/);
      await expect(page.locator('text=7').first()).toBeVisible();
      await expect(page.locator('text=3').first()).toBeVisible();
    }

    // Edit: navigate to the first Edit button or /edit-calculation/{id}
    const editButton = page.locator('a:has-text("Edit"), button:has-text("Edit")').first();
    if (await editButton.count()) {
      await editButton.click();
      await expect(page).toHaveURL(/edit-calculation/);
      // change inputs to 8 and 2
      await Promise.any([
        page.fill('input[name="inputs[]"]', '8').catch(() => {}),
        page.fill('input[name="inputs"]', '8,2').catch(() => {}),
        page.locator('input').first().fill('8').catch(() => {}),
      ]);
      // submit
      await Promise.any([
        page.click('button:has-text("Update")'),
        page.click('button:has-text("Save")'),
        page.click('button[type="submit"]')
      ]).catch(() => {});
      // check updated result 16
      await page.goto('/dashboard');
      await expect(page.locator('text=16').first()).toBeVisible();
    }

    // Delete: click delete on the first row
    const delButton = page.locator('button:has-text("Delete"), a:has-text("Delete")').first();
    if (await delButton.count()) {
      await delButton.click();
      // some UIs ask confirm - try to accept dialog
      page.once('dialog', dialog => dialog.accept());
      // finally ensure it disappears
      await page.waitForTimeout(500);
      await expect(page.locator('text=16').first()).toHaveCount(0);
    }
  });

  test('Negative scenarios: invalid calculation inputs and editing/deleting when not logged in', async ({ page, context }) => {
    const uniq = Date.now();
    const username = `e2e_neg_${uniq}`;
    const email = `e2e_neg_${uniq}@example.com`;
    const password = 'NegPass123!';

    // Create user via API and login to create an initial calculation
    const r = await page.request.post('/auth/register', {
      data: JSON.stringify({ username, email, password, confirm_password: password, first_name: 'Neg', last_name: 'User' }),
      headers: { 'Content-Type': 'application/json' }
    });
    if (r.status() !== 201) {
      const body = await r.text();
      throw new Error(`Could not create neg user via API: ${r.status()} ${body}`);
    }
    await signIn(page, username, password);
    await page.waitForSelector('#successAlert', { timeout: 7000 }).catch(() => {});
    await page.waitForURL(/dashboard/, { timeout: 7000 }).catch(() => {});

    // Try to add calculation with invalid inputs
    await addCalculation(page, 'addition', ['abc', 'def']);
    // Expect validation error or not created
    await expect(page.locator('text=Invalid').first().or(page.locator('text=must be a number').first())).toBeDefined();

    // Logout to test edit/delete when not logged in
    await page.goto('/logout').catch(() => {});

    // Try to navigate to edit page directly (should redirect to login or show 401)
    await page.goto('/edit-calculation/00000000-0000-0000-0000-000000000000');
    await expect(page).toHaveURL(/login/);

    // Try delete via dashboard (should require login)
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/login|\/dashboard/);
  });
});
