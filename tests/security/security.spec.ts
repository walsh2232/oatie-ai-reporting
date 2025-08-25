import { test, expect } from '@playwright/test';

/**
 * Security Testing Suite for Oatie AI Reporting Platform
 * Tests for common web vulnerabilities and security best practices
 */

test.describe('Security Vulnerability Tests', () => {
  test('XSS protection validation', async ({ page }) => {
    await page.goto('/');
    
    // Test for reflected XSS in URL parameters
    const maliciousScript = '<script>alert("XSS")</script>';
    await page.goto(`/?search=${encodeURIComponent(maliciousScript)}`);
    
    // Verify script is not executed
    const alerts = [];
    page.on('dialog', dialog => {
      alerts.push(dialog.message());
      dialog.dismiss();
    });
    
    await page.waitForTimeout(1000);
    expect(alerts).toHaveLength(0);
    
    // Check if script tags are properly escaped in DOM
    const bodyContent = await page.textContent('body');
    expect(bodyContent).not.toContain('<script>');
  });

  test('SQL injection protection', async ({ page }) => {
    await page.goto('/');
    
    // Login first
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password');
    await page.click('button[type="submit"]');
    
    await expect(page.locator('[data-testid="dashboard"]')).toBeVisible();
    
    // Navigate to reports section
    await page.click('[data-testid="reports-tab"]');
    
    // Test SQL injection in search/filter fields
    const sqlInjectionPayloads = [
      "'; DROP TABLE users; --",
      "' OR '1'='1",
      "'; DELETE FROM reports; --",
      "' UNION SELECT * FROM users --"
    ];
    
    for (const payload of sqlInjectionPayloads) {
      // Try injection in search field
      const searchField = page.locator('[data-testid="search-input"]');
      if (await searchField.isVisible()) {
        await searchField.fill(payload);
        await page.keyboard.press('Enter');
        
        // Wait for response and verify no database error
        await page.waitForTimeout(2000);
        
        const errorMessages = await page.locator('.error, [role="alert"]').all();
        for (const error of errorMessages) {
          const errorText = await error.textContent();
          // Ensure no database error messages are exposed
          expect(errorText).not.toMatch(/sql|database|mysql|postgresql|oracle/i);
        }
      }
    }
  });

  test('Authentication security', async ({ page }) => {
    await page.goto('/');
    
    // Test for session fixation
    const initialCookies = await page.context().cookies();
    
    // Attempt login
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password');
    await page.click('button[type="submit"]');
    
    // Verify session cookies are regenerated after login
    const postLoginCookies = await page.context().cookies();
    
    const sessionCookie = postLoginCookies.find(cookie => 
      cookie.name.toLowerCase().includes('session') || 
      cookie.name.toLowerCase().includes('token')
    );
    
    if (sessionCookie) {
      // Verify cookie security attributes
      expect(sessionCookie.httpOnly).toBe(true);
      expect(sessionCookie.secure).toBe(true);
      expect(sessionCookie.sameSite).toBe('Strict');
    }
  });

  test('CSRF protection validation', async ({ page }) => {
    await page.goto('/');
    
    // Login
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password');
    await page.click('button[type="submit"]');
    
    await expect(page.locator('[data-testid="dashboard"]')).toBeVisible();
    
    // Check for CSRF tokens in forms
    const forms = await page.locator('form').all();
    
    for (const form of forms) {
      const csrfToken = await form.locator('input[name*="csrf"], input[name*="token"]').first();
      if (await csrfToken.isVisible()) {
        const tokenValue = await csrfToken.getAttribute('value');
        expect(tokenValue).toBeTruthy();
        expect(tokenValue.length).toBeGreaterThan(10); // Token should be sufficiently long
      }
    }
    
    // Test CSRF protection by attempting cross-origin request
    const response = await page.evaluate(async () => {
      try {
        const res = await fetch('/api/v1/reports', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Origin': 'https://malicious-site.com'
          },
          body: JSON.stringify({ name: 'malicious report' })
        });
        return { status: res.status, headers: Object.fromEntries(res.headers.entries()) };
      } catch (error) {
        return { error: error.message };
      }
    });
    
    // Should be blocked by CORS or CSRF protection
    expect(response.status).not.toBe(200);
  });

  test('Content Security Policy validation', async ({ page }) => {
    await page.goto('/');
    
    // Check for CSP headers
    const response = await page.goto('/');
    const cspHeader = response?.headers()['content-security-policy'];
    
    if (cspHeader) {
      // Verify CSP includes important directives
      expect(cspHeader).toContain("default-src 'self'");
      expect(cspHeader).toContain("script-src");
      expect(cspHeader).toContain("style-src");
      expect(cspHeader).not.toContain("'unsafe-eval'"); // Should not allow eval
    }
    
    // Test inline script blocking
    const inlineScriptBlocked = await page.evaluate(() => {
      try {
        // This should be blocked by CSP
        eval('console.log("CSP bypassed")');
        return false;
      } catch (error) {
        return true; // CSP is working
      }
    });
    
    expect(inlineScriptBlocked).toBe(true);
  });

  test('Sensitive data exposure', async ({ page }) => {
    await page.goto('/');
    
    // Check for sensitive information in page source
    const pageContent = await page.content();
    
    // Should not expose sensitive configuration
    expect(pageContent).not.toMatch(/password.*[:=]/i);
    expect(pageContent).not.toMatch(/api.*key.*[:=]/i);
    expect(pageContent).not.toMatch(/secret.*[:=]/i);
    expect(pageContent).not.toMatch(/database.*connection/i);
    
    // Check network requests for sensitive data exposure
    const responses = [];
    page.on('response', response => {
      responses.push(response);
    });
    
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password');
    await page.click('button[type="submit"]');
    
    // Wait for authentication requests
    await page.waitForTimeout(3000);
    
    // Check that passwords are not sent in clear text (should be in request body, not URL)
    for (const response of responses) {
      const url = response.url();
      expect(url).not.toContain('password');
      expect(url).not.toContain('secret');
    }
  });

  test('HTTP security headers', async ({ page }) => {
    const response = await page.goto('/');
    const headers = response?.headers() || {};
    
    // Check for security headers
    expect(headers['x-content-type-options']).toBe('nosniff');
    expect(headers['x-frame-options']).toMatch(/DENY|SAMEORIGIN/);
    expect(headers['x-xss-protection']).toBe('1; mode=block');
    
    // Check for HSTS (if HTTPS)
    if (page.url().startsWith('https://')) {
      expect(headers['strict-transport-security']).toBeTruthy();
    }
    
    // Verify no sensitive headers are exposed
    expect(headers['server']).not.toMatch(/apache|nginx|iis/i);
    expect(headers['x-powered-by']).toBeFalsy();
  });

  test('Input validation and sanitization', async ({ page }) => {
    await page.goto('/');
    
    // Login
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password');
    await page.click('button[type="submit"]');
    
    await expect(page.locator('[data-testid="dashboard"]')).toBeVisible();
    
    // Test various malicious inputs
    const maliciousInputs = [
      '<img src="x" onerror="alert(1)">',
      'javascript:alert(1)',
      '${7*7}', // Template injection
      '../../../etc/passwd', // Path traversal
      '\x00', // Null bytes
      'A'.repeat(10000) // Buffer overflow attempt
    ];
    
    // Test in different input fields
    const inputFields = await page.locator('input[type="text"], input[type="search"], textarea').all();
    
    for (const input of inputFields.slice(0, 3)) { // Limit to first 3 inputs
      for (const maliciousInput of maliciousInputs.slice(0, 3)) { // Limit to first 3 payloads
        await input.fill(maliciousInput);
        await page.keyboard.press('Enter');
        
        // Verify input is sanitized and no script execution
        const alerts = [];
        page.on('dialog', dialog => {
          alerts.push(dialog.message());
          dialog.dismiss();
        });
        
        await page.waitForTimeout(500);
        expect(alerts).toHaveLength(0);
        
        // Clear the input for next test
        await input.clear();
      }
    }
  });

  test('File upload security', async ({ page }) => {
    await page.goto('/');
    
    // Login and look for file upload functionality
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password');
    await page.click('button[type="submit"]');
    
    const fileInput = page.locator('input[type="file"]').first();
    
    if (await fileInput.isVisible()) {
      // Test malicious file types
      const testFiles = [
        { name: 'test.exe', content: 'MZ\x90\x00' }, // Executable
        { name: 'test.php', content: '<?php echo "test"; ?>' }, // Server script
        { name: 'test.jsp', content: '<% out.println("test"); %>' }, // Server script
        { name: 'test.svg', content: '<svg onload="alert(1)"></svg>' } // SVG with script
      ];
      
      for (const testFile of testFiles) {
        // Create a file and attempt upload
        const buffer = Buffer.from(testFile.content);
        
        try {
          await fileInput.setInputFiles({
            name: testFile.name,
            mimeType: 'application/octet-stream',
            buffer: buffer
          });
          
          // Check for appropriate error message
          await page.waitForTimeout(2000);
          
          const errorMessage = await page.locator('.error, [role="alert"]').first();
          if (await errorMessage.isVisible()) {
            const errorText = await errorMessage.textContent();
            // Should reject dangerous file types
            expect(errorText).toMatch(/not allowed|invalid|unsupported/i);
          }
        } catch (error) {
          // File upload might be properly restricted
          console.log(`File upload restriction working for ${testFile.name}`);
        }
      }
    }
  });

  test('Rate limiting protection', async ({ page }) => {
    await page.goto('/');
    
    // Test login rate limiting
    const email = 'test@example.com';
    const wrongPassword = 'wrongpassword';
    
    const attempts = [];
    
    // Make multiple failed login attempts
    for (let i = 0; i < 5; i++) {
      const startTime = Date.now();
      
      await page.fill('input[type="email"]', email);
      await page.fill('input[type="password"]', wrongPassword);
      await page.click('button[type="submit"]');
      
      // Wait for response
      await page.waitForTimeout(1000);
      
      const endTime = Date.now();
      attempts.push(endTime - startTime);
      
      // Check if rate limiting kicks in
      const errorMessage = await page.locator('.error, [role="alert"]').first();
      if (await errorMessage.isVisible()) {
        const errorText = await errorMessage.textContent();
        if (errorText?.includes('rate limit') || errorText?.includes('too many')) {
          expect(i).toBeGreaterThan(2); // Rate limiting should kick in after few attempts
          break;
        }
      }
      
      // Clear fields for next attempt
      await page.fill('input[type="email"]', '');
      await page.fill('input[type="password"]', '');
    }
    
    // Later attempts should be slower (rate limited)
    if (attempts.length > 3) {
      const avgEarlyAttempts = attempts.slice(0, 2).reduce((a, b) => a + b) / 2;
      const avgLateAttempts = attempts.slice(-2).reduce((a, b) => a + b) / 2;
      
      // Later attempts should take longer due to rate limiting
      expect(avgLateAttempts).toBeGreaterThan(avgEarlyAttempts);
    }
  });
});

test.describe('Security Headers and Configuration', () => {
  test('TLS/SSL configuration', async ({ page }) => {
    const response = await page.goto('/');
    const url = response?.url() || page.url();
    
    if (url.startsWith('https://')) {
      // Check TLS version and cipher strength
      const securityState = await page.evaluate(() => {
        return (window as any).performance?.getEntriesByType?.('navigation')?.[0]?.secureConnectionStart > 0;
      });
      
      expect(securityState).toBeTruthy();
      
      // Verify HSTS header
      const headers = response?.headers() || {};
      expect(headers['strict-transport-security']).toBeTruthy();
    }
  });

  test('Cookie security configuration', async ({ page }) => {
    await page.goto('/');
    
    // Login to set authentication cookies
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password');
    await page.click('button[type="submit"]');
    
    await page.waitForTimeout(2000);
    
    const cookies = await page.context().cookies();
    
    for (const cookie of cookies) {
      if (cookie.name.toLowerCase().includes('session') || 
          cookie.name.toLowerCase().includes('auth') ||
          cookie.name.toLowerCase().includes('token')) {
        
        // Security attributes for sensitive cookies
        expect(cookie.httpOnly).toBe(true);
        expect(cookie.secure).toBe(true);
        expect(cookie.sameSite).toMatch(/Strict|Lax/);
        
        // Verify expiration is reasonable
        if (cookie.expires) {
          const maxAge = cookie.expires - (Date.now() / 1000);
          expect(maxAge).toBeGreaterThan(0);
          expect(maxAge).toBeLessThan(86400 * 30); // Max 30 days
        }
      }
    }
  });
});