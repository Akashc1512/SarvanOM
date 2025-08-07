import { defineConfig, devices } from '@playwright/test';

/**
 * MAANG-Level Playwright Configuration
 * Comprehensive E2E testing setup for production-quality testing
 */

export default defineConfig({
  testDir: './e2e',
  
  // Run tests in files in parallel
  fullyParallel: true,
  
  // Fail the build on CI if you accidentally left test.only in the source code
  forbidOnly: !!process.env.CI,
  
  // Retry on CI only
  retries: process.env.CI ? 2 : 0,
  
  // Opt out of parallel tests on CI
  workers: process.env.CI ? 1 : undefined,
  
  // Reporter configuration
  reporter: [
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/junit.xml' }],
    ['line'],
    ['allure-playwright'],
  ],
  
  // Shared settings for all tests
  use: {
    // Base URL for the application
    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3000',
    
    // Browser context options
    viewport: { width: 1280, height: 720 },
    
    // Collect trace when retrying the failed test
    trace: 'on-first-retry',
    
    // Record screenshots on failure
    screenshot: 'only-on-failure',
    
    // Record videos on failure
    video: 'retain-on-failure',
    
    // Global timeout for actions
    actionTimeout: 10000,
    
    // Global timeout for navigation
    navigationTimeout: 30000,
    
    // Ignore HTTPS errors
    ignoreHTTPSErrors: true,
    
    // Accept downloads
    acceptDownloads: true,
    
    // Locale
    locale: 'en-US',
    
    // Timezone
    timezoneId: 'UTC',
    
    // Permissions
    permissions: ['clipboard-read', 'clipboard-write'],
    
    // Extra HTTP headers
    extraHTTPHeaders: {
      'Accept-Language': 'en-US,en;q=0.9',
    },
  },

  // Configure projects for major browsers
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
      testMatch: /.*\.e2e\.ts/,
    },
    
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
      testMatch: /.*\.e2e\.ts/,
    },
    
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
      testMatch: /.*\.e2e\.ts/,
    },
    
    // Mobile browsers
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
      testMatch: /.*\.mobile\.e2e\.ts/,
    },
    
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
      testMatch: /.*\.mobile\.e2e\.ts/,
    },
    
    // API testing
    {
      name: 'api',
      testMatch: /.*\.api\.test\.ts/,
      use: {
        // No browser needed for API tests
        ignoreHTTPSErrors: true,
      },
    },
    
    // Performance testing
    {
      name: 'performance',
      testMatch: /.*\.perf\.test\.ts/,
      use: {
        ...devices['Desktop Chrome'],
        // Specific settings for performance tests
        launchOptions: {
          args: [
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--no-first-run',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding',
          ],
        },
      },
    },
    
    // Accessibility testing
    {
      name: 'accessibility',
      testMatch: /.*\.a11y\.test\.ts/,
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // Folder for test artifacts
  outputDir: 'test-results/',
  
  // Global setup and teardown
  globalSetup: require.resolve('./e2e/global-setup'),
  globalTeardown: require.resolve('./e2e/global-teardown'),
  
  // Web server configuration
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
    stdout: 'pipe',
    stderr: 'pipe',
  },
  
  // Test timeout
  timeout: 30000,
  
  // Expect timeout
  expect: {
    // Timeout for assertions
    timeout: 5000,
    
    // Take screenshots on assertion failures
    toHaveScreenshot: {
      mode: 'only-on-failure',
      animations: 'disabled',
      caret: 'hide',
    },
  },
  
  // Test metadata
  metadata: {
    'test-type': 'e2e',
    'test-framework': 'playwright',
    'app-version': process.env.npm_package_version || '1.0.0',
    'node-version': process.version,
  },
});