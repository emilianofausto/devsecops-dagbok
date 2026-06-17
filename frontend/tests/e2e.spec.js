const { test, expect } = require('@playwright/test');

test.describe('Frontend E2E Tests - DevSecOps Dagbok', () => {

    test.beforeEach(async ({ page }) => {
        // Option 1: Mock Authentication by injecting the Auth0 Client into the browser
        await page.addInitScript(() => {
            window.auth0Client = {
                isAuthenticated: () => Promise.resolve(true),
                getUser: () => Promise.resolve({ email: 'test@example.com' }),
                getTokenSilently: () => Promise.resolve('mock-token')
            };
        });

        // Mock API GET request to return an entry so the UI has something to render
        await page.route('**/api/entries', async route => {
            if (route.request().method() === 'GET') {
                await route.fulfill({
                    status: 200,
                    contentType: 'application/json',
                    body: JSON.stringify([
                        { 
                            id: 1, 
                            title: 'Befintlig Anteckning', 
                            category: 'Test', 
                            content: 'Detta är ett testinnehåll.', 
                            created_at: new Date().toISOString() 
                        }
                    ])
                });
            } else {
                await route.continue();
            }
        });

        await page.goto('/'); 
    });

    test('1. Sidan laddar korrekt och visar sparade inlägg (GET)', async ({ page }) => {
        await expect(page).toHaveTitle('DevSecOps Dagbok');
        await expect(page.locator('h1')).toHaveText('Min Digitala Dagbok');
        await expect(page.locator('#entries-container')).toContainText('Befintlig Anteckning');
    });

    test('2. Skapa ett nytt inlägg (POST)', async ({ page }) => {
        await page.route('**/api/entries', async route => {
            if (route.request().method() === 'POST') {
                await route.fulfill({ status: 201, body: JSON.stringify({ id: 2 }) });
            } else {
                await route.continue();
            }
        });

        await page.fill('#title', 'Ny E2E Anteckning');
        await page.fill('#category', 'Automatisering');
        await page.fill('#content', 'Genererat av Playwright');
        await page.click('#submit-btn');

        await expect(page.locator('#title')).toBeEmpty();
    });

    test('3. Formuläret blockeras av HTML5-validering vid tomma fält', async ({ page }) => {
        await page.click('#submit-btn');
        const isTitleInvalid = await page.$eval('#title', el => el.validity.valueMissing);
        expect(isTitleInvalid).toBe(true);
    });

    test('4. Redigera-knappen fyller i formuläret (PUT/PATCH Prep)', async ({ page }) => {
        await page.click('button.btn-secondary:has-text("Redigera")');
        
        await expect(page.locator('#title')).toHaveValue('Befintlig Anteckning');
        await expect(page.locator('#form-title')).toHaveText('Redigera anteckning');
        await expect(page.locator('#cancel-btn')).toBeVisible();
    });

    test('5. Avbryt-knappen rensar formulärets state', async ({ page }) => {
        await page.click('button.btn-secondary:has-text("Redigera")'); 
        await page.click('#cancel-btn'); 
        
        await expect(page.locator('#title')).toBeEmpty();
        await expect(page.locator('#form-title')).toHaveText('Skapa ny anteckning');
        await expect(page.locator('#cancel-btn')).toBeHidden();
    });

    test('6. Radering (DELETE) hanterar UX-bekräftelse', async ({ page }) => {
        await page.route('**/api/entries/1', async route => {
            if (route.request().method() === 'DELETE') {
                await route.fulfill({ status: 200, body: JSON.stringify({ message: "Radera OK" }) });
            } else {
                await route.continue();
            }
        });

        page.on('dialog', async dialog => {
            await dialog.accept();
        });

        await page.click('button.btn-danger:has-text("Radera")');
    });
});
