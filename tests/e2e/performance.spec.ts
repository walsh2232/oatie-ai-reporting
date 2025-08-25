import { test, expect, Page } from '@playwright/test';
import { performance } from 'perf_hooks';

// Configure test timeout and retries for performance testing
test.setTimeout(60000); // 60 seconds timeout

// Performance thresholds
const PERFORMANCE_THRESHOLDS = {
  pageLoadTime: 3000, // 3 seconds
  navigationTime: 2000, // 2 seconds
  renderTime: 1000, // 1 second
  apiResponseTime: 2000 // 2 seconds
};

// Test data for realistic scenarios
const TEST_DATA = {
  users: [
    { username: 'test_admin', password: 'admin_pass', role: 'admin' },
    { username: 'test_analyst', password: 'analyst_pass', role: 'analyst' },
    { username: 'test_viewer', password: 'viewer_pass', role: 'viewer' }
  ],
  reports: [
    'Sales Summary Report',
    'Financial Performance Dashboard',
    'Customer Analysis Report'
  ]
};

class PerformanceHelper {
  static async measurePageLoad(page: Page, url: string): Promise<number> {
    const startTime = performance.now();
    await page.goto(url, { waitUntil: 'networkidle' });
    const endTime = performance.now();
    return endTime - startTime;
  }

  static async measureNavigation(page: Page, selector: string): Promise<number> {
    const startTime = performance.now();
    await page.click(selector);
    await page.waitForLoadState('networkidle');
    const endTime = performance.now();
    return endTime - startTime;
  }

  static async measureApiResponse(page: Page, apiCall: () => Promise<void>): Promise<number> {
    const startTime = performance.now();
    await apiCall();
    const endTime = performance.now();
    return endTime - startTime;
  }

  static async capturePerformanceMetrics(page: Page): Promise<any> {
    return await page.evaluate(() => {
      const perfData = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      const paintEntries = performance.getEntriesByType('paint');
      
      return {
        domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
        loadComplete: perfData.loadEventEnd - perfData.loadEventStart,
        firstPaint: paintEntries.find(entry => entry.name === 'first-paint')?.startTime || 0,
        firstContentfulPaint: paintEntries.find(entry => entry.name === 'first-contentful-paint')?.startTime || 0,
        transferSize: perfData.transferSize,
        encodedBodySize: perfData.encodedBodySize
      };
    });
  }
}

test.describe('Oatie AI Performance E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Set up performance monitoring
    await page.addInitScript(() => {
      // Monitor for long tasks
      new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.duration > 50) {
            console.warn(`Long task detected: ${entry.duration}ms`);
          }
        }
      }).observe({entryTypes: ['longtask']});
    });
  });

  test('Login page load performance', async ({ page }) => {
    const loadTime = await PerformanceHelper.measurePageLoad(page, '/');
    
    // Verify page loads within threshold
    expect(loadTime).toBeLessThan(PERFORMANCE_THRESHOLDS.pageLoadTime);
    
    // Verify essential elements are present
    await expect(page.locator('h1')).toContainText('Oracle BI Reporting');
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    
    // Capture detailed performance metrics
    const perfMetrics = await PerformanceHelper.capturePerformanceMetrics(page);
    console.log('Login page performance:', perfMetrics);
    
    // Assert performance requirements
    expect(perfMetrics.firstContentfulPaint).toBeLessThan(1500); // FCP < 1.5s
    expect(perfMetrics.domContentLoaded).toBeLessThan(2000); // DCL < 2s
  });

  test('Authentication flow performance', async ({ page }) => {
    await page.goto('/');
    
    // Measure login process
    const startTime = performance.now();
    
    await page.fill('input[type="email"]', TEST_DATA.users[0].username);
    await page.fill('input[type="password"]', TEST_DATA.users[0].password);
    
    // Monitor network requests during login
    const responsePromise = page.waitForResponse(resp => 
      resp.url().includes('/api/v1/auth/login') && resp.status() === 200
    );
    
    await page.click('button[type="submit"]');
    
    const loginResponse = await responsePromise;
    const endTime = performance.now();
    
    const loginTime = endTime - startTime;
    
    // Verify login performance
    expect(loginTime).toBeLessThan(PERFORMANCE_THRESHOLDS.apiResponseTime);
    
    // Verify successful authentication
    await expect(page.locator('[data-testid="dashboard"]')).toBeVisible({ timeout: 5000 });
    
    console.log(`Login flow completed in: ${loginTime}ms`);
  });

  test('Dashboard load and interaction performance', async ({ page }) => {
    // Login first
    await page.goto('/');
    await page.fill('input[type="email"]', TEST_DATA.users[1].username);
    await page.fill('input[type="password"]', TEST_DATA.users[1].password);
    await page.click('button[type="submit"]');
    
    // Wait for dashboard to load
    await expect(page.locator('[data-testid="dashboard"]')).toBeVisible();
    
    // Measure dashboard widget loading
    const widgetLoadTime = await PerformanceHelper.measureNavigation(
      page, 
      '[data-testid="reports-widget"]'
    );
    
    expect(widgetLoadTime).toBeLessThan(PERFORMANCE_THRESHOLDS.renderTime);
    
    // Test report list loading performance
    await page.click('[data-testid="reports-tab"]');
    
    const reportsLoadTime = await page.evaluate(async () => {
      const startTime = performance.now();
      
      // Wait for reports to load
      await new Promise(resolve => {
        const checkReports = () => {
          if (document.querySelectorAll('[data-testid^="report-item"]').length > 0) {
            resolve(undefined);
          } else {
            setTimeout(checkReports, 100);
          }
        };
        checkReports();
      });
      
      return performance.now() - startTime;
    });
    
    expect(reportsLoadTime).toBeLessThan(PERFORMANCE_THRESHOLDS.apiResponseTime);
    
    console.log(`Reports loaded in: ${reportsLoadTime}ms`);
  });

  test('Report execution performance', async ({ page }) => {
    // Login and navigate to reports
    await page.goto('/');
    await page.fill('input[type="email"]', TEST_DATA.users[1].username);
    await page.fill('input[type="password"]', TEST_DATA.users[1].password);
    await page.click('button[type="submit"]');
    
    await expect(page.locator('[data-testid="dashboard"]')).toBeVisible();
    await page.click('[data-testid="reports-tab"]');
    
    // Execute a report and measure performance
    const executeStartTime = performance.now();
    
    // Monitor API call
    const reportResponsePromise = page.waitForResponse(resp => 
      resp.url().includes('/api/v1/reports/execute')
    );
    
    await page.click('[data-testid="report-item"]:first-child [data-testid="execute-button"]');
    
    const reportResponse = await reportResponsePromise;
    const apiResponseTime = performance.now() - executeStartTime;
    
    // Wait for report results to render
    await expect(page.locator('[data-testid="report-results"]')).toBeVisible({ timeout: 10000 });
    
    const totalExecutionTime = performance.now() - executeStartTime;
    
    // Verify performance requirements
    expect(apiResponseTime).toBeLessThan(PERFORMANCE_THRESHOLDS.apiResponseTime);
    expect(totalExecutionTime).toBeLessThan(10000); // Total execution < 10s
    
    // Verify response data
    expect(reportResponse.status()).toBe(200);
    
    console.log(`Report execution: API ${apiResponseTime}ms, Total ${totalExecutionTime}ms`);
  });

  test('Concurrent user simulation', async ({ page, context }) => {
    // Simulate multiple user actions concurrently
    const concurrentActions = [
      // Action 1: Dashboard loading
      async () => {
        await page.goto('/');
        await page.fill('input[type="email"]', TEST_DATA.users[0].username);
        await page.fill('input[type="password"]', TEST_DATA.users[0].password);
        await page.click('button[type="submit"]');
        await expect(page.locator('[data-testid="dashboard"]')).toBeVisible();
      },
      
      // Action 2: Report browsing in new tab
      async () => {
        const newPage = await context.newPage();
        await newPage.goto('/');
        await newPage.fill('input[type="email"]', TEST_DATA.users[1].username);
        await newPage.fill('input[type="password"]', TEST_DATA.users[1].password);
        await newPage.click('button[type="submit"]');
        await newPage.click('[data-testid="reports-tab"]');
        await expect(newPage.locator('[data-testid="report-item"]')).toBeVisible();
        await newPage.close();
      },
      
      // Action 3: Profile management in another tab
      async () => {
        const newPage = await context.newPage();
        await newPage.goto('/');
        await newPage.fill('input[type="email"]', TEST_DATA.users[2].username);
        await newPage.fill('input[type="password"]', TEST_DATA.users[2].password);
        await newPage.click('button[type="submit"]');
        await newPage.click('[data-testid="profile-menu"]');
        await expect(newPage.locator('[data-testid="profile-info"]')).toBeVisible();
        await newPage.close();
      }
    ];
    
    const startTime = performance.now();
    
    // Execute all actions concurrently
    await Promise.all(concurrentActions);
    
    const totalTime = performance.now() - startTime;
    
    // Verify concurrent performance
    expect(totalTime).toBeLessThan(15000); // All actions complete within 15s
    
    console.log(`Concurrent operations completed in: ${totalTime}ms`);
  });

  test('Memory and resource usage monitoring', async ({ page }) => {
    await page.goto('/');
    
    // Get initial memory usage
    const initialMemory = await page.evaluate(() => (performance as any).memory?.usedJSHeapSize || 0);
    
    // Perform memory-intensive operations
    await page.fill('input[type="email"]', TEST_DATA.users[0].username);
    await page.fill('input[type="password"]', TEST_DATA.users[0].password);
    await page.click('button[type="submit"]');
    
    await expect(page.locator('[data-testid="dashboard"]')).toBeVisible();
    
    // Navigate through multiple views
    await page.click('[data-testid="reports-tab"]');
    await page.click('[data-testid="analytics-tab"]');
    await page.click('[data-testid="settings-tab"]');
    
    // Get final memory usage
    const finalMemory = await page.evaluate(() => (performance as any).memory?.usedJSHeapSize || 0);
    
    const memoryIncrease = finalMemory - initialMemory;
    const memoryIncreaseMB = memoryIncrease / (1024 * 1024);
    
    // Verify memory usage is reasonable
    expect(memoryIncreaseMB).toBeLessThan(50); // Less than 50MB increase
    
    console.log(`Memory usage increased by: ${memoryIncreaseMB.toFixed(2)}MB`);
    
    // Check for memory leaks by measuring after garbage collection
    await page.evaluate(() => {
      if ((window as any).gc) {
        (window as any).gc();
      }
    });
    
    const afterGC = await page.evaluate(() => (performance as any).memory?.usedJSHeapSize || 0);
    const leakDetection = (afterGC - initialMemory) / (1024 * 1024);
    
    console.log(`Memory after GC: ${leakDetection.toFixed(2)}MB above initial`);
  });

  test('Accessibility performance impact', async ({ page }) => {
    // Enable accessibility tools and measure impact
    await page.goto('/');
    
    const withoutA11yTime = await PerformanceHelper.measurePageLoad(page, '/');
    
    // Inject accessibility testing tools
    await page.addScriptTag({
      url: 'https://cdn.jsdelivr.net/npm/axe-core@4.7.2/axe.min.js'
    });
    
    const withA11yTime = await PerformanceHelper.measurePageLoad(page, '/');
    
    // Run accessibility scan
    const accessibilityResults = await page.evaluate(async () => {
      return await (window as any).axe.run();
    });
    
    // Verify accessibility compliance
    expect(accessibilityResults.violations.length).toBe(0);
    
    // Verify performance impact is minimal
    const performanceImpact = withA11yTime - withoutA11yTime;
    expect(performanceImpact).toBeLessThan(500); // Less than 500ms impact
    
    console.log(`Accessibility scan completed. Violations: ${accessibilityResults.violations.length}`);
    console.log(`Performance impact: ${performanceImpact}ms`);
  });
});

// Test configuration for different environments
test.describe('Cross-browser performance', () => {
  ['chromium', 'firefox', 'webkit'].forEach(browserName => {
    test(`${browserName} performance baseline`, async ({ page }) => {
      const loadTime = await PerformanceHelper.measurePageLoad(page, '/');
      
      // Browser-specific thresholds (WebKit typically slower)
      const browserThreshold = browserName === 'webkit' ? 
        PERFORMANCE_THRESHOLDS.pageLoadTime * 1.5 : 
        PERFORMANCE_THRESHOLDS.pageLoadTime;
      
      expect(loadTime).toBeLessThan(browserThreshold);
      
      console.log(`${browserName} load time: ${loadTime}ms`);
    });
  });
});