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
    baseURL: 'http://127.0.0.1:3000', 
    trace: 'on-first-retry',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    }
  ],

  webServer: {
    command: 'npm --prefix frontend run dev', 
    url: 'http://127.0.0.1:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 60000,
  },
});
