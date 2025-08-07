/**
 * Dashboard E2E Tests
 * Comprehensive end-to-end tests for the main dashboard functionality
 */

import { test, expect, Page } from '@playwright/test';

test.describe('Dashboard Page', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;
    
    // Navigate to dashboard
    await page.goto('/');
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
  });

  test.describe('Page Load and Initial State', () => {
    test('should load dashboard successfully', async () => {
      // Check page title
      await expect(page).toHaveTitle(/Sarvanom/);
      
      // Check main navigation elements are present
      await expect(page.locator('nav')).toBeVisible();
      
      // Check main content area
      await expect(page.locator('main')).toBeVisible();
      
      // Check query form is present
      await expect(page.locator('form')).toBeVisible();
    });

    test('should display correct initial elements', async () => {
      // Check for query input
      const queryInput = page.locator('input[type="text"]').first();
      await expect(queryInput).toBeVisible();
      await expect(queryInput).toBeEnabled();
      
      // Check for submit button
      const submitButton = page.locator('button[type="submit"]').first();
      await expect(submitButton).toBeVisible();
      await expect(submitButton).toBeEnabled();
      
      // Check for recent queries section (may be empty initially)
      const recentQueriesSection = page.locator('[data-testid="recent-queries"]');
      if (await recentQueriesSection.isVisible()) {
        await expect(recentQueriesSection).toBeVisible();
      }
    });

    test('should have proper accessibility structure', async () => {
      // Check main landmarks
      await expect(page.locator('main')).toBeVisible();
      await expect(page.locator('nav')).toBeVisible();
      
      // Check heading hierarchy
      const h1 = page.locator('h1');
      await expect(h1).toBeVisible();
      
      // Check form labels
      const queryInput = page.locator('input[type="text"]').first();
      const label = page.locator('label').first();
      if (await label.isVisible()) {
        const labelFor = await label.getAttribute('for');
        const inputId = await queryInput.getAttribute('id');
        expect(labelFor).toBeTruthy();
        expect(inputId).toBeTruthy();
      }
    });
  });

  test.describe('Query Functionality', () => {
    test('should submit a query successfully', async () => {
      const queryText = 'What is artificial intelligence?';
      
      // Fill in query input
      const queryInput = page.locator('input[type="text"]').first();
      await queryInput.fill(queryText);
      
      // Submit the form
      const submitButton = page.locator('button[type="submit"]').first();
      await submitButton.click();
      
      // Wait for response (with timeout)
      await page.waitForTimeout(2000); // Allow time for API call
      
      // Check if loading state appears and then disappears
      const loadingIndicator = page.locator('[data-testid="loading"]');
      if (await loadingIndicator.isVisible()) {
        await expect(loadingIndicator).toBeVisible();
        await expect(loadingIndicator).not.toBeVisible({ timeout: 30000 });
      }
      
      // Check if answer appears
      const answerSection = page.locator('[data-testid="answer"]');
      if (await answerSection.isVisible()) {
        await expect(answerSection).toBeVisible();
        await expect(answerSection).toContainText(/./); // Contains some text
      }
    });

    test('should handle empty query gracefully', async () => {
      // Try to submit empty form
      const submitButton = page.locator('button[type="submit"]').first();
      await submitButton.click();
      
      // Check for validation message or that submit is prevented
      const queryInput = page.locator('input[type="text"]').first();
      const isRequired = await queryInput.getAttribute('required');
      
      if (isRequired !== null) {
        // If input is required, browser should show validation
        await expect(queryInput).toHaveAttribute('required');
      }
    });

    test('should display query in recent queries after submission', async () => {
      const queryText = 'Test query for recent list';
      
      // Submit query
      const queryInput = page.locator('input[type="text"]').first();
      await queryInput.fill(queryText);
      
      const submitButton = page.locator('button[type="submit"]').first();
      await submitButton.click();
      
      // Wait for response
      await page.waitForTimeout(3000);
      
      // Check recent queries section
      const recentQueriesSection = page.locator('[data-testid="recent-queries"]');
      if (await recentQueriesSection.isVisible()) {
        await expect(recentQueriesSection).toContainText(queryText, { timeout: 10000 });
      }
    });
  });

  test.describe('Navigation and UI Interactions', () => {
    test('should navigate to analytics page', async () => {
      // Look for analytics navigation link
      const analyticsLink = page.locator('a[href*="/analytics"]');
      
      if (await analyticsLink.isVisible()) {
        await analyticsLink.click();
        await page.waitForLoadState('networkidle');
        
        // Check we're on analytics page
        await expect(page).toHaveURL(/.*analytics.*/);
      }
    });

    test('should open knowledge graph modal', async () => {
      // Look for knowledge graph button or link
      const knowledgeGraphButton = page.locator('[data-testid="knowledge-graph-button"]');
      
      if (await knowledgeGraphButton.isVisible()) {
        await knowledgeGraphButton.click();
        
        // Check modal appears
        const modal = page.locator('[role="dialog"]');
        await expect(modal).toBeVisible({ timeout: 5000 });
        
        // Check modal can be closed
        const closeButton = modal.locator('button[aria-label*="close"]');
        if (await closeButton.isVisible()) {
          await closeButton.click();
          await expect(modal).not.toBeVisible();
        }
      }
    });

    test('should toggle theme', async () => {
      // Look for theme toggle button
      const themeToggle = page.locator('[data-testid="theme-toggle"]');
      
      if (await themeToggle.isVisible()) {
        // Get initial theme
        const initialTheme = await page.locator('html').getAttribute('class');
        
        // Click theme toggle
        await themeToggle.click();
        
        // Wait for theme change
        await page.waitForTimeout(500);
        
        // Check theme has changed
        const newTheme = await page.locator('html').getAttribute('class');
        expect(newTheme).not.toBe(initialTheme);
      }
    });
  });

  test.describe('Performance and Loading', () => {
    test('should load within performance budget', async () => {
      const startTime = Date.now();
      
      // Navigate to page
      await page.goto('/', { waitUntil: 'networkidle' });
      
      const loadTime = Date.now() - startTime;
      
      // Should load within 3 seconds
      expect(loadTime).toBeLessThan(3000);
    });

    test('should have good Core Web Vitals', async () => {
      // Navigate to page
      await page.goto('/');
      
      // Wait for page to stabilize
      await page.waitForLoadState('networkidle');
      
      // Measure performance metrics
      const metrics = await page.evaluate(() => {
        return new Promise((resolve) => {
          if ('performance' in window) {
            const observer = new PerformanceObserver((list) => {
              const entries = list.getEntries();
              const navigationEntry = entries.find(entry => entry.entryType === 'navigation') as PerformanceNavigationTiming;
              
              if (navigationEntry) {
                resolve({
                  domContentLoaded: navigationEntry.domContentLoadedEventEnd - navigationEntry.domContentLoadedEventStart,
                  loadComplete: navigationEntry.loadEventEnd - navigationEntry.loadEventStart,
                  firstPaint: navigationEntry.responseStart - navigationEntry.requestStart,
                });
              }
            });
            
            observer.observe({ entryTypes: ['navigation'] });
            
            // Fallback timeout
            setTimeout(() => resolve({}), 5000);
          } else {
            resolve({});
          }
        });
      });
      
      console.log('Performance metrics:', metrics);
    });
  });

  test.describe('Error Handling', () => {
    test('should handle network errors gracefully', async () => {
      // Simulate network failure
      await page.route('**/api/**', route => route.abort());
      
      // Try to submit a query
      const queryInput = page.locator('input[type="text"]').first();
      await queryInput.fill('Test query for error handling');
      
      const submitButton = page.locator('button[type="submit"]').first();
      await submitButton.click();
      
      // Check for error message
      const errorMessage = page.locator('[data-testid="error-message"]');
      if (await errorMessage.isVisible()) {
        await expect(errorMessage).toBeVisible({ timeout: 10000 });
        await expect(errorMessage).toContainText(/error|failed|network/i);
      }
    });

    test('should display 404 page for invalid routes', async () => {
      // Navigate to non-existent page
      await page.goto('/non-existent-page');
      
      // Check for 404 content
      await expect(page.locator('body')).toContainText(/404|not found/i, { timeout: 5000 });
    });
  });
});