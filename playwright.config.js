const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  // Path to the directory containing end-to-end test files
  testDir: './tests', 
  fullyParallel: true,
  // Fail the build on CI if you accidentally leave test.only in the source code
  forbidOnly: !!process.env.CI,
  // Retry failing tests on CI environments to mitigate flakiness
  retries: process.env.CI ? 2 : 0,
  // Opt out of parallel tests on CI to preserve system resources
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  
  use: {
    // CRITICAL: Point this to your Frontend Web Server port (e.g., Vite/Node), NOT the FastAPI backend.
    // When tests execute page.goto('/'), they will land on the actual UI.
    baseURL: 'http://127.0.0.1:3000', 
    trace: 'on-first-retry',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    }
  ],

  // Playwright's built-in web server to spin up the FRONTEND application locally.
  // The backend server (Uvicorn) is already managed and started by your git pre-push hook.
  webServer: {
    command: 'npm run dev', // Command to start your frontend development server
    url: 'http://127.0.0.1:3000',
    reuseExistingServer: !process.env.CI, // Reuse local running instances during local dev
    timeout: 60000,
  },
});
