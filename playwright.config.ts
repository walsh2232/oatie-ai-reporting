import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright Configuration for Oatie AI Performance Testing
 * Enterprise-grade cross-browser testing with performance monitoring
 */
export default defineConfig({
  testDir: './tests/e2e',
  
  /* Run tests in files in parallel */
  fullyParallel: true,
  
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,
  
  /* Opt out of parallel tests on CI. */
  workers: process.env.CI ? 1 : undefined,
  
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/e2e-results.json' }],
    ['junit', { outputFile: 'test-results/e2e-results.xml' }],
    ['line']
  ],
  
  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:5173',
    
    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: 'on-first-retry',
    
    /* Collect screenshots on failure */
    screenshot: 'only-on-failure',
    
    /* Collect videos on failure */
    video: 'retain-on-failure',
    
    /* Global timeout for each action */
    actionTimeout: 30000,
    
    /* Global timeout for navigation */
    navigationTimeout: 30000,
  },

  /* Configure projects for major browsers */
  projects: [
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
        // Chrome-specific performance settings
        launchOptions: {
          args: [
            '--enable-features=NetworkService,NetworkServiceLogging',
            '--force-fieldtrials=*BackgroundTracing/default/',
            '--no-sandbox',
            '--disable-features=VizDisplayCompositor'
          ]
        }
      },
    },

    {
      name: 'firefox',
      use: { 
        ...devices['Desktop Firefox'],
        // Firefox-specific settings
        launchOptions: {
          firefoxUserPrefs: {
            'dom.performance.enable_user_timing_logging': true,
            'dom.performance.time_to_non_blank_paint.enabled': true
          }
        }
      },
    },

    {
      name: 'webkit',
      use: { 
        ...devices['Desktop Safari'],
        // Safari-specific settings
        launchOptions: {
          args: ['--enable-features=NetworkService']
        }
      },
    },

    /* Test against mobile viewports. */
    {
      name: 'Mobile Chrome',
      use: { 
        ...devices['Pixel 5'],
        // Mobile performance considerations
        launchOptions: {
          args: ['--disable-features=VizDisplayCompositor']
        }
      },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },

    /* Performance testing project with specific settings */
    {
      name: 'performance',
      testMatch: '**/performance.spec.ts',
      use: {
        ...devices['Desktop Chrome'],
        // Optimized for performance testing
        launchOptions: {
          args: [
            '--enable-precise-memory-info',
            '--enable-logging=stderr',
            '--v=1',
            '--no-sandbox',
            '--disable-web-security',
            '--allow-running-insecure-content'
          ]
        }
      },
      timeout: 120000, // Extended timeout for performance tests
    },

    /* Accessibility testing project */
    {
      name: 'accessibility',
      testMatch: '**/accessibility.spec.ts',
      use: {
        ...devices['Desktop Chrome'],
        // Accessibility-focused settings
        colorScheme: 'light',
      },
    }
  ],

  /* Folder for test artifacts such as screenshots, videos, traces, etc. */
  outputDir: 'test-results/',

  /* Run your local dev server before starting the tests */
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },

  /* Global setup for performance monitoring */
  globalSetup: require.resolve('./tests/e2e/global-setup.ts'),
  
  /* Global teardown */
  globalTeardown: require.resolve('./tests/e2e/global-teardown.ts'),

  /* Test configuration */
  timeout: 60000, // Global test timeout
  expect: {
    /* Timeout for expect() assertions */
    timeout: 10000,
  },
});