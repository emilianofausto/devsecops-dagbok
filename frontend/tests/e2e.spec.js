const { test, expect } = require('@playwright/test');

test.describe('Frontend E2E Tests - DevSecOps Dagbok', () => {

    test.beforeEach(async ({ page }) => {
        // Intercept the Auth0 CDN and provide a mocked factory implementation.
        await page.route('https://cdn.auth0.com/**/*.js', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/javascript',
                body: `
                    window.auth0 = {
                        createAuth0Client: async () => ({
                            isAuthenticated: async () => true,
                            getUser: async () => ({ email: 'test@example.com' }),
                            getTokenSilently: async () => 'mock-token',
                            handleRedirectCallback: async () => {}
                        })
                    };
                `
            });
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
        await page.locator('h1:has-text("Min Digitala Dagbok")').waitFor({ state: 'visible' });
    });

    test('1. Sidan laddar korrekt och visar sparade inlägg (GET)', async ({ page }) => {
        await expect(page).toHaveTitle('DevSecOps Dagbok');
        await expect(page.locator('h1')).toHaveText('Min Digitala Dagbok');
        await expect(page.locator('#entries-container')).toContainText('Befintlig Anteckning');
    });

    test('2. Skapa ett nytt inlägg (POST)', async ({ page }) => {
        const responsePromise = page.waitForResponse(response => 
            response.url().includes('/api/entries') && response.request().method() === 'POST'
        );

        await page.fill('#title', 'Ny E2E Anteckning');
        await page.fill('#category', 'Automatisering');
        await page.fill('#content', 'Genererat av Playwright');
        await page.click('#submit-btn');

        await responsePromise;
        await expect(page.locator('#title')).toHaveValue('', { timeout: 3000 });
    });

    test('3. Formuläret blockeras av HTML5-validering vid tomma fält', async ({ page }) => {
        await page.click('#submit-btn');
        const isTitleInvalid = await page.$eval('#title', el => el.validity.valueMissing);
        expect(isTitleInvalid).toBe(true);
    });

    test('4. Redigera-knappen fyller i formuläret (PUT/PATCH Prep)', async ({ page }) => {
        const redigeraBtn = page.locator('#entries-container button:has-text("Redigera")').first();
        
        await redigeraBtn.waitFor({ state: 'visible' });
        await redigeraBtn.click();
        
        await expect(page.locator('#title')).toHaveValue('Befintlig Anteckning');
        await expect(page.locator('#form-title')).toHaveText('Redigera anteckning');
        await expect(page.locator('#cancel-btn')).toBeVisible();
    });

    test('5. Avbryt-knappen rensar formulärets state', async ({ page }) => {
        const redigeraBtn = page.locator('#entries-container button:has-text("Redigera")').first();
        
        await redigeraBtn.waitFor({ state: 'visible' });
        await redigeraBtn.click();
        
        // Confirm it entered edit mode successfully
        await expect(page.locator('#title')).toHaveValue('Befintlig Anteckning');
        await expect(page.locator('#form-title')).toHaveText('Redigera anteckning');
        
        // Act: Click Cancel
        await page.click('#cancel-btn'); 
        
        // Assert: Verify state is completely reverted
        await expect(page.locator('#title')).toBeEmpty();
        await expect(page.locator('#form-title')).toHaveText('Skapa ny anteckning');
        await expect(page.locator('#cancel-btn')).toBeHidden();
    });

    test('6. Radering (DELETE) hanterar UX-bekräftelse', async ({ page }) => {
        const raderaBtn = page.locator('#entries-container button:has-text("Radera")').first();
        await raderaBtn.waitFor({ state: 'visible' });

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

        await raderaBtn.click();
    });
});
