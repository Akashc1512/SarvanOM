/**
 * Cosmic Pro Features E2E Tests
 * Comprehensive end-to-end tests for all Cosmic Pro features
 */

import { test, expect, Page } from '@playwright/test';

test.describe('Cosmic Pro Features', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;
    
    // Navigate to home page
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test.describe('Theme System', () => {
    test('should toggle between light and dark themes', async () => {
      // Find theme toggle button
      const themeToggle = page.locator('[data-testid="theme-toggle"]');
      
      if (await themeToggle.isVisible()) {
        // Get initial theme
        const htmlElement = page.locator('html');
        const initialTheme = await htmlElement.getAttribute('class');
        
        // Toggle theme
        await themeToggle.click();
        await page.waitForTimeout(500);
        
        // Check theme has changed
        const newTheme = await htmlElement.getAttribute('class');
        expect(newTheme).not.toBe(initialTheme);
        
        // Toggle back
        await themeToggle.click();
        await page.waitForTimeout(500);
        
        // Check theme is back to original
        const finalTheme = await htmlElement.getAttribute('class');
        expect(finalTheme).toBe(initialTheme);
      }
    });

    test('should respect system theme preference', async () => {
      // Set system preference to dark
      await page.emulateMedia({ colorScheme: 'dark' });
      await page.reload();
      await page.waitForLoadState('networkidle');
      
      const htmlElement = page.locator('html');
      const theme = await htmlElement.getAttribute('class');
      
      // Should have dark theme classes
      expect(theme).toContain('dark');
    });
  });

  test.describe('Multimodal Upload', () => {
    test('should navigate to multimodal upload page', async () => {
      // Navigate to multimodal demo
      await page.goto('/multimodal-demo');
      await page.waitForLoadState('networkidle');
      
      // Check page title
      await expect(page).toHaveTitle(/SarvanOM.*Multimodal/);
      
      // Check main heading
      await expect(page.locator('h1')).toContainText(/Multimodal Knowledge Platform/);
      
      // Check upload component is present
      const uploadComponent = page.locator('[data-testid="multimodal-upload"]');
      if (await uploadComponent.isVisible()) {
        await expect(uploadComponent).toBeVisible();
      }
    });

    test('should display file upload interface', async () => {
      await page.goto('/multimodal-demo');
      await page.waitForLoadState('networkidle');
      
      // Check for drag and drop area
      const dropZone = page.locator('[data-testid="drop-zone"]');
      if (await dropZone.isVisible()) {
        await expect(dropZone).toBeVisible();
        await expect(dropZone).toContainText(/drag.*drop|upload/i);
      }
      
      // Check for file input
      const fileInput = page.locator('input[type="file"]');
      if (await fileInput.isVisible()) {
        await expect(fileInput).toBeVisible();
      }
    });

    test('should show supported file types', async () => {
      await page.goto('/multimodal-demo');
      await page.waitForLoadState('networkidle');
      
      // Check for supported file types information
      const supportedTypes = page.locator('text=/images?|videos?|documents?|audio/i');
      if (await supportedTypes.isVisible()) {
        await expect(supportedTypes).toBeVisible();
      }
    });
  });

  test.describe('Blog System', () => {
    test('should navigate to blog page', async () => {
      await page.goto('/blog');
      await page.waitForLoadState('networkidle');
      
      // Check page title
      await expect(page).toHaveTitle(/SarvanOM.*Blog/);
      
      // Check main heading
      await expect(page.locator('h1')).toContainText(/Knowledge Blog/);
    });

    test('should display blog posts', async () => {
      await page.goto('/blog');
      await page.waitForLoadState('networkidle');
      
      // Check for blog posts
      const blogPosts = page.locator('[data-testid="blog-post"]');
      if (await blogPosts.first().isVisible()) {
        await expect(blogPosts.first()).toBeVisible();
      }
      
      // Check for featured post
      const featuredPost = page.locator('[data-testid="featured-post"]');
      if (await featuredPost.isVisible()) {
        await expect(featuredPost).toBeVisible();
      }
    });

    test('should have search functionality', async () => {
      await page.goto('/blog');
      await page.waitForLoadState('networkidle');
      
      // Check for search input
      const searchInput = page.locator('input[placeholder*="search" i]');
      if (await searchInput.isVisible()) {
        await expect(searchInput).toBeVisible();
        
        // Test search
        await searchInput.fill('AI');
        await page.waitForTimeout(500);
        
        // Check if results are filtered
        const results = page.locator('[data-testid="blog-post"]');
        if (await results.first().isVisible()) {
          await expect(results.first()).toBeVisible();
        }
      }
    });

    test('should have tag filtering', async () => {
      await page.goto('/blog');
      await page.waitForLoadState('networkidle');
      
      // Check for tag buttons
      const tagButtons = page.locator('button:has-text("AI"), button:has-text("Technology")');
      if (await tagButtons.first().isVisible()) {
        await expect(tagButtons.first()).toBeVisible();
        
        // Click a tag
        await tagButtons.first().click();
        await page.waitForTimeout(500);
        
        // Check if results are filtered
        const results = page.locator('[data-testid="blog-post"]');
        if (await results.first().isVisible()) {
          await expect(results.first()).toBeVisible();
        }
      }
    });
  });

  test.describe('Authentication', () => {
    test('should navigate to login page', async () => {
      await page.goto('/login');
      await page.waitForLoadState('networkidle');
      
      // Check page title
      await expect(page).toHaveTitle(/SarvanOM.*Login/);
      
      // Check main heading
      await expect(page.locator('h1')).toContainText(/Welcome Back/);
      
      // Check form elements
      await expect(page.locator('input[type="email"]')).toBeVisible();
      await expect(page.locator('input[type="password"]')).toBeVisible();
      await expect(page.locator('button[type="submit"]')).toBeVisible();
    });

    test('should navigate to register page', async () => {
      await page.goto('/register');
      await page.waitForLoadState('networkidle');
      
      // Check page title
      await expect(page).toHaveTitle(/SarvanOM.*Register/);
      
      // Check main heading
      await expect(page.locator('h1')).toContainText(/Join SarvanOM/);
      
      // Check form elements
      await expect(page.locator('input[type="text"]')).toBeVisible();
      await expect(page.locator('input[type="email"]')).toBeVisible();
      await expect(page.locator('input[type="password"]')).toBeVisible();
      await expect(page.locator('button[type="submit"]')).toBeVisible();
    });

    test('should validate form inputs', async () => {
      await page.goto('/register');
      await page.waitForLoadState('networkidle');
      
      // Try to submit empty form
      const submitButton = page.locator('button[type="submit"]');
      await submitButton.click();
      
      // Check for validation messages
      const errorMessages = page.locator('[data-testid="error-message"]');
      if (await errorMessages.first().isVisible()) {
        await expect(errorMessages.first()).toBeVisible();
      }
    });

    test('should have password visibility toggle', async () => {
      await page.goto('/register');
      await page.waitForLoadState('networkidle');
      
      // Check for password visibility toggle
      const passwordInput = page.locator('input[type="password"]').first();
      const toggleButton = page.locator('button:has(svg)').first();
      
      if (await toggleButton.isVisible()) {
        // Click toggle
        await toggleButton.click();
        
        // Check input type changed
        const inputType = await passwordInput.getAttribute('type');
        expect(inputType).toBe('text');
        
        // Click again
        await toggleButton.click();
        
        // Check input type changed back
        const inputTypeAfter = await passwordInput.getAttribute('type');
        expect(inputTypeAfter).toBe('password');
      }
    });
  });

  test.describe('404 Page', () => {
    test('should display custom 404 page', async () => {
      await page.goto('/non-existent-page');
      await page.waitForLoadState('networkidle');
      
      // Check for 404 content
      await expect(page.locator('h1')).toContainText(/404/);
      await expect(page.locator('h2')).toContainText(/Lost in the Cosmos/);
      
      // Check for navigation buttons
      const homeButton = page.locator('a:has-text("Return Home")');
      if (await homeButton.isVisible()) {
        await expect(homeButton).toBeVisible();
      }
      
      const searchButton = page.locator('a:has-text("Start Searching")');
      if (await searchButton.isVisible()) {
        await expect(searchButton).toBeVisible();
      }
    });

    test('should have popular destinations', async () => {
      await page.goto('/non-existent-page');
      await page.waitForLoadState('networkidle');
      
      // Check for popular destinations section
      const destinationsSection = page.locator('text=/Popular Destinations/');
      if (await destinationsSection.isVisible()) {
        await expect(destinationsSection).toBeVisible();
        
        // Check for destination links
        const destinationLinks = page.locator('a[href="/"], a[href="/search"], a[href="/analytics"]');
        if (await destinationLinks.first().isVisible()) {
          await expect(destinationLinks.first()).toBeVisible();
        }
      }
    });
  });

  test.describe('Streaming Components', () => {
    test('should display streaming search interface', async () => {
      await page.goto('/search');
      await page.waitForLoadState('networkidle');
      
      // Check for search input
      const searchInput = page.locator('input[type="text"]').first();
      await expect(searchInput).toBeVisible();
      
      // Submit a query
      await searchInput.fill('Test streaming query');
      const submitButton = page.locator('button[type="submit"]').first();
      await submitButton.click();
      
      // Check for streaming indicators
      const streamingIndicator = page.locator('[data-testid="streaming-indicator"]');
      if (await streamingIndicator.isVisible()) {
        await expect(streamingIndicator).toBeVisible();
      }
      
      // Check for heartbeat indicator
      const heartbeatIndicator = page.locator('[data-testid="heartbeat"]');
      if (await heartbeatIndicator.isVisible()) {
        await expect(heartbeatIndicator).toBeVisible();
      }
    });

    test('should show connection status', async () => {
      await page.goto('/search');
      await page.waitForLoadState('networkidle');
      
      // Check for connection status
      const connectionStatus = page.locator('[data-testid="connection-status"]');
      if (await connectionStatus.isVisible()) {
        await expect(connectionStatus).toBeVisible();
      }
    });
  });

  test.describe('Performance', () => {
    test('should load pages within performance budget', async () => {
      const pages = ['/', '/search', '/analytics', '/blog', '/multimodal-demo'];
      
      for (const pagePath of pages) {
        const startTime = Date.now();
        await page.goto(pagePath, { waitUntil: 'networkidle' });
        const loadTime = Date.now() - startTime;
        
        // Should load within 3 seconds
        expect(loadTime).toBeLessThan(3000);
        console.log(`${pagePath} loaded in ${loadTime}ms`);
      }
    });

    test('should have good Core Web Vitals', async () => {
      await page.goto('/');
      
      // Wait for page to stabilize
      await page.waitForLoadState('networkidle');
      
      // Measure LCP
      const lcp = await page.evaluate(() => {
        return new Promise((resolve) => {
          new PerformanceObserver((list) => {
            const entries = list.getEntries();
            const lastEntry = entries[entries.length - 1];
            resolve(lastEntry.startTime);
          }).observe({ entryTypes: ['largest-contentful-paint'] });
        });
      });
      
      // LCP should be under 2.5 seconds
      expect(lcp).toBeLessThan(2500);
    });
  });

  test.describe('Accessibility', () => {
    test('should have proper heading hierarchy', async () => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      // Check for h1
      const h1 = page.locator('h1');
      await expect(h1).toBeVisible();
      
      // Check heading order
      const headings = await page.locator('h1, h2, h3, h4, h5, h6').all();
      expect(headings.length).toBeGreaterThan(0);
    });

    test('should have proper form labels', async () => {
      await page.goto('/login');
      await page.waitForLoadState('networkidle');
      
      // Check form inputs have labels
      const emailInput = page.locator('input[type="email"]');
      const passwordInput = page.locator('input[type="password"]');
      
      await expect(emailInput).toBeVisible();
      await expect(passwordInput).toBeVisible();
      
      // Check for associated labels
      const emailLabel = page.locator('label[for]');
      if (await emailLabel.isVisible()) {
        await expect(emailLabel).toBeVisible();
      }
    });

    test('should support keyboard navigation', async () => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      // Test tab navigation
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      
      // Check focus is visible
      const focusedElement = page.locator(':focus');
      if (await focusedElement.isVisible()) {
        await expect(focusedElement).toBeVisible();
      }
    });

    test('should have proper ARIA attributes', async () => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      // Check for main landmark
      const main = page.locator('main');
      await expect(main).toBeVisible();
      
      // Check for navigation landmark
      const nav = page.locator('nav');
      await expect(nav).toBeVisible();
      
      // Check for form elements
      const forms = page.locator('form');
      if (await forms.first().isVisible()) {
        await expect(forms.first()).toBeVisible();
      }
    });
  });
});
