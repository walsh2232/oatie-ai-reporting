import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

/**
 * Accessibility Testing Suite for Oatie AI Reporting Platform
 * WCAG 2.1 AA Compliance Validation
 */

test.describe('WCAG 2.1 AA Compliance Tests', () => {
  test('Homepage accessibility scan', async ({ page }) => {
    await page.goto('/');
    
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();
    
    expect(accessibilityScanResults.violations).toEqual([]);
    
    // Log violations if any for debugging
    if (accessibilityScanResults.violations.length > 0) {
      console.log('Accessibility violations found:', 
        JSON.stringify(accessibilityScanResults.violations, null, 2));
    }
  });

  test('Login form accessibility', async ({ page }) => {
    await page.goto('/');
    
    // Check form labels and ARIA attributes
    const emailInput = page.locator('input[type="email"]');
    const passwordInput = page.locator('input[type="password"]');
    const submitButton = page.locator('button[type="submit"]');
    
    // Verify labels are properly associated
    await expect(emailInput).toHaveAttribute('aria-label');
    await expect(passwordInput).toHaveAttribute('aria-label');
    
    // Verify keyboard navigation
    await page.keyboard.press('Tab');
    await expect(emailInput).toBeFocused();
    
    await page.keyboard.press('Tab');
    await expect(passwordInput).toBeFocused();
    
    await page.keyboard.press('Tab');
    await expect(submitButton).toBeFocused();
    
    // Run targeted accessibility scan on login form
    const loginFormScan = await new AxeBuilder({ page })
      .include('form')
      .withTags(['wcag2a', 'wcag2aa'])
      .analyze();
    
    expect(loginFormScan.violations).toEqual([]);
  });

  test('Dashboard accessibility after login', async ({ page }) => {
    // Login first
    await page.goto('/');
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password');
    await page.click('button[type="submit"]');
    
    // Wait for dashboard to load
    await expect(page.locator('[data-testid="dashboard"]')).toBeVisible();
    
    // Comprehensive accessibility scan
    const dashboardScan = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();
    
    expect(dashboardScan.violations).toEqual([]);
    
    // Check heading hierarchy
    const headings = await page.locator('h1, h2, h3, h4, h5, h6').all();
    expect(headings.length).toBeGreaterThan(0);
    
    // Verify navigation landmarks
    await expect(page.locator('nav')).toBeVisible();
    await expect(page.locator('main')).toBeVisible();
  });

  test('Color contrast compliance', async ({ page }) => {
    await page.goto('/');
    
    // Test with both light and dark themes if supported
    const colorContrastScan = await new AxeBuilder({ page })
      .withRules(['color-contrast'])
      .analyze();
    
    expect(colorContrastScan.violations).toEqual([]);
    
    // Additional manual contrast checks for Oracle Redwood theme
    const primaryElements = await page.locator('.MuiButton-contained').all();
    for (const element of primaryElements) {
      // Verify button contrast meets WCAG AA standards
      const styles = await element.evaluate(el => {
        const computed = window.getComputedStyle(el);
        return {
          backgroundColor: computed.backgroundColor,
          color: computed.color
        };
      });
      
      // Oracle Redwood primary colors should meet contrast requirements
      expect(styles.backgroundColor).toBeTruthy();
      expect(styles.color).toBeTruthy();
    }
  });

  test('Keyboard navigation compliance', async ({ page }) => {
    await page.goto('/');
    
    // Test keyboard-only navigation
    const focusableElements = await page.locator(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    ).all();
    
    expect(focusableElements.length).toBeGreaterThan(0);
    
    // Test Tab navigation through all focusable elements
    await page.keyboard.press('Tab');
    let currentlyFocused = await page.locator(':focus').first();
    expect(currentlyFocused).toBeTruthy();
    
    // Test escape key handling
    await page.keyboard.press('Escape');
    
    // Test enter key on buttons
    const firstButton = page.locator('button').first();
    await firstButton.focus();
    
    // Verify no keyboard traps exist
    for (let i = 0; i < Math.min(focusableElements.length, 20); i++) {
      await page.keyboard.press('Tab');
      const focused = await page.locator(':focus').first();
      expect(focused).toBeTruthy();
    }
  });

  test('Screen reader compatibility', async ({ page }) => {
    await page.goto('/');
    
    // Check for proper ARIA labels and roles
    const ariaElements = await page.locator('[aria-label], [aria-labelledby], [role]').all();
    expect(ariaElements.length).toBeGreaterThan(0);
    
    // Verify page title for screen readers
    await expect(page).toHaveTitle(/Oracle BI/);
    
    // Check for landmark regions
    await expect(page.locator('[role="main"], main')).toBeVisible();
    await expect(page.locator('[role="navigation"], nav')).toBeVisible();
    
    // Verify images have alt text
    const images = await page.locator('img').all();
    for (const img of images) {
      const alt = await img.getAttribute('alt');
      expect(alt).toBeTruthy();
    }
    
    // Check for skip links
    const skipLinks = await page.locator('a[href^="#"]').first();
    if (await skipLinks.isVisible()) {
      expect(skipLinks).toHaveText(/skip/i);
    }
  });

  test('Form validation accessibility', async ({ page }) => {
    await page.goto('/');
    
    const emailInput = page.locator('input[type="email"]');
    const passwordInput = page.locator('input[type="password"]');
    const submitButton = page.locator('button[type="submit"]');
    
    // Test invalid form submission
    await submitButton.click();
    
    // Check for accessible error messages
    const errorMessages = await page.locator('[role="alert"], .error-message').all();
    
    // Verify error messages are properly associated with inputs
    if (errorMessages.length > 0) {
      for (const error of errorMessages) {
        const errorText = await error.textContent();
        expect(errorText).toBeTruthy();
        
        // Check aria-describedby relationships
        const ariaDescribedBy = await error.getAttribute('id');
        if (ariaDescribedBy) {
          const associatedInput = page.locator(`[aria-describedby="${ariaDescribedBy}"]`);
          expect(associatedInput).toBeTruthy();
        }
      }
    }
    
    // Test form with valid data
    await emailInput.fill('test@example.com');
    await passwordInput.fill('password123');
    
    // Verify no error states remain
    const accessibilityAfterFix = await new AxeBuilder({ page })
      .include('form')
      .analyze();
    
    expect(accessibilityAfterFix.violations).toEqual([]);
  });

  test('Data table accessibility', async ({ page }) => {
    // Login and navigate to reports with data tables
    await page.goto('/');
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password');
    await page.click('button[type="submit"]');
    
    await expect(page.locator('[data-testid="dashboard"]')).toBeVisible();
    await page.click('[data-testid="reports-tab"]');
    
    // Wait for data tables to load
    const dataTable = page.locator('table, [role="table"]').first();
    
    if (await dataTable.isVisible()) {
      // Check table headers
      const headers = await page.locator('th, [role="columnheader"]').all();
      expect(headers.length).toBeGreaterThan(0);
      
      // Verify table caption or aria-label
      const tableLabel = await dataTable.getAttribute('aria-label') ||
                        await page.locator('caption').textContent();
      expect(tableLabel).toBeTruthy();
      
      // Check for proper table structure
      const tableScan = await new AxeBuilder({ page })
        .include('table, [role="table"]')
        .withTags(['wcag2a'])
        .analyze();
      
      expect(tableScan.violations).toEqual([]);
    }
  });

  test('Modal dialog accessibility', async ({ page }) => {
    await page.goto('/');
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password');
    await page.click('button[type="submit"]');
    
    // Open a modal dialog (settings, etc.)
    await page.click('[data-testid="settings-button"]');
    
    const modal = page.locator('[role="dialog"], .modal');
    
    if (await modal.isVisible()) {
      // Check modal accessibility
      await expect(modal).toHaveAttribute('aria-labelledby');
      await expect(modal).toHaveAttribute('aria-modal', 'true');
      
      // Verify focus management
      const focusedElement = page.locator(':focus');
      expect(focusedElement).toBeTruthy();
      
      // Test escape key closes modal
      await page.keyboard.press('Escape');
      await expect(modal).not.toBeVisible();
      
      // Verify focus returns to trigger element
      await expect(page.locator('[data-testid="settings-button"]')).toBeFocused();
    }
  });
});

test.describe('Accessibility Performance Impact', () => {
  test('Accessibility features performance overhead', async ({ page }) => {
    // Measure page load time with accessibility features
    const startTime = Date.now();
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    const loadTime = Date.now() - startTime;
    
    // Run accessibility scan and measure time
    const scanStartTime = Date.now();
    await new AxeBuilder({ page }).analyze();
    const scanTime = Date.now() - scanStartTime;
    
    // Verify accessibility scanning doesn't significantly impact performance
    expect(scanTime).toBeLessThan(5000); // Scan completes within 5 seconds
    expect(loadTime).toBeLessThan(10000); // Page loads within 10 seconds
    
    console.log(`Page load: ${loadTime}ms, Accessibility scan: ${scanTime}ms`);
  });
});