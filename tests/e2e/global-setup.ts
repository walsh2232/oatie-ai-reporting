import { chromium, FullConfig } from '@playwright/test';

/**
 * Global setup for Playwright tests
 * Initializes performance monitoring and test infrastructure
 */
async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting Oatie AI Performance Test Suite');
  
  // Setup performance monitoring
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    // Initialize performance baseline
    await page.goto(process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:5173');
    
    // Wait for application to be ready
    await page.waitForSelector('body', { timeout: 30000 });
    
    // Capture initial performance metrics
    const initialMetrics = await page.evaluate(() => {
      const perfData = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      return {
        domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
        loadComplete: perfData.loadEventEnd - perfData.loadEventStart,
        transferSize: perfData.transferSize
      };
    });
    
    console.log('📊 Initial performance baseline:', initialMetrics);
    
    // Store baseline for comparison
    process.env.PERF_BASELINE = JSON.stringify(initialMetrics);
    
  } catch (error) {
    console.error('❌ Failed to establish performance baseline:', error);
    // Don't fail setup - tests can still run
  } finally {
    await browser.close();
  }
  
  console.log('✅ Global setup completed successfully');
}

export default globalSetup;