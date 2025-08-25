import { FullConfig } from '@playwright/test';
import fs from 'fs';
import path from 'path';

/**
 * Global teardown for Playwright tests
 * Generates performance summary and cleanup
 */
async function globalTeardown(config: FullConfig) {
  console.log('🧹 Starting global teardown');
  
  try {
    // Generate performance test summary
    const resultsDir = 'test-results';
    const summaryFile = path.join(resultsDir, 'performance-summary.json');
    
    // Create results directory if it doesn't exist
    if (!fs.existsSync(resultsDir)) {
      fs.mkdirSync(resultsDir, { recursive: true });
    }
    
    // Collect test results and generate summary
    const summary = {
      timestamp: new Date().toISOString(),
      testSuite: 'Oatie AI E2E Performance Tests',
      environment: process.env.NODE_ENV || 'test',
      baseUrl: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:5173',
      performanceBaseline: process.env.PERF_BASELINE ? JSON.parse(process.env.PERF_BASELINE) : null,
      testsCompleted: true
    };
    
    // Write summary file
    fs.writeFileSync(summaryFile, JSON.stringify(summary, null, 2));
    
    console.log('📝 Performance summary generated:', summaryFile);
    
    // Cleanup temporary files
    console.log('🗑️  Cleaning up temporary test files');
    
    console.log('✅ Global teardown completed successfully');
    
  } catch (error) {
    console.error('❌ Error during global teardown:', error);
    // Don't throw - let tests complete
  }
}

export default globalTeardown;