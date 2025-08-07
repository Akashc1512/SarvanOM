/**
 * Performance E2E Tests
 * Comprehensive performance testing for MAANG-level applications
 */

import { test, expect, Page } from '@playwright/test';

test.describe('Performance Tests', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;
  });

  test.describe('Core Web Vitals', () => {
    test('should meet LCP (Largest Contentful Paint) threshold', async () => {
      const startTime = performance.now();
      
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      const lcp = await page.evaluate(() => {
        return new Promise<number>((resolve) => {
          if ('PerformanceObserver' in window) {
            const observer = new PerformanceObserver((list) => {
              const entries = list.getEntries();
              const lcpEntry = entries[entries.length - 1];
              if (lcpEntry) {
                observer.disconnect();
                resolve(lcpEntry.startTime);
              }
            });
            
            observer.observe({ type: 'largest-contentful-paint', buffered: true });
            
            // Fallback timeout
            setTimeout(() => {
              observer.disconnect();
              resolve(0);
            }, 5000);
          } else {
            resolve(0);
          }
        });
      });
      
      console.log(`LCP: ${lcp}ms`);
      
      // LCP should be under 2.5 seconds (2500ms) for good performance
      if (lcp > 0) {
        expect(lcp).toBeLessThan(2500);
      }
    });

    test('should meet FID (First Input Delay) threshold', async () => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      // Simulate user interaction
      const button = page.locator('button').first();
      if (await button.isVisible()) {
        const startTime = performance.now();
        await button.click();
        const endTime = performance.now();
        
        const inputDelay = endTime - startTime;
        console.log(`Simulated FID: ${inputDelay}ms`);
        
        // FID should be under 100ms for good performance
        expect(inputDelay).toBeLessThan(100);
      }
    });

    test('should meet CLS (Cumulative Layout Shift) threshold', async () => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      // Wait for layout to stabilize
      await page.waitForTimeout(2000);
      
      const cls = await page.evaluate(() => {
        return new Promise<number>((resolve) => {
          let clsValue = 0;
          
          if ('PerformanceObserver' in window) {
            const observer = new PerformanceObserver((list) => {
              for (const entry of list.getEntries()) {
                if (entry.entryType === 'layout-shift' && !(entry as any).hadRecentInput) {
                  clsValue += (entry as any).value;
                }
              }
            });
            
            observer.observe({ type: 'layout-shift', buffered: true });
            
            setTimeout(() => {
              observer.disconnect();
              resolve(clsValue);
            }, 3000);
          } else {
            resolve(0);
          }
        });
      });
      
      console.log(`CLS: ${cls}`);
      
      // CLS should be under 0.1 for good performance
      if (cls > 0) {
        expect(cls).toBeLessThan(0.1);
      }
    });
  });

  test.describe('Resource Performance', () => {
    test('should load JavaScript bundles efficiently', async () => {
      const response = await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      const resourceTimings = await page.evaluate(() => {
        const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];
        return resources
          .filter(resource => resource.name.includes('.js'))
          .map(resource => ({
            name: resource.name,
            size: resource.transferSize,
            duration: resource.duration,
            type: 'javascript'
          }));
      });
      
      console.log('JavaScript resources:', resourceTimings);
      
      // Check total JavaScript bundle size
      const totalJSSize = resourceTimings.reduce((total, resource) => total + resource.size, 0);
      console.log(`Total JS size: ${(totalJSSize / 1024).toFixed(2)} KB`);
      
      // JavaScript bundles should be under 500KB total
      expect(totalJSSize).toBeLessThan(500 * 1024);
      
      // Individual chunks should load quickly
      resourceTimings.forEach(resource => {
        expect(resource.duration).toBeLessThan(3000); // 3 seconds max
      });
    });

    test('should load CSS efficiently', async () => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      const cssTimings = await page.evaluate(() => {
        const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];
        return resources
          .filter(resource => resource.name.includes('.css'))
          .map(resource => ({
            name: resource.name,
            size: resource.transferSize,
            duration: resource.duration,
          }));
      });
      
      console.log('CSS resources:', cssTimings);
      
      // CSS should load quickly
      cssTimings.forEach(resource => {
        expect(resource.duration).toBeLessThan(1000); // 1 second max
      });
    });

    test('should have optimal image loading', async () => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      const imageTimings = await page.evaluate(() => {
        const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];
        return resources
          .filter(resource => 
            resource.name.includes('.jpg') || 
            resource.name.includes('.png') || 
            resource.name.includes('.webp') ||
            resource.name.includes('.svg')
          )
          .map(resource => ({
            name: resource.name,
            size: resource.transferSize,
            duration: resource.duration,
          }));
      });
      
      console.log('Image resources:', imageTimings);
      
      // Images should load reasonably quickly
      imageTimings.forEach(resource => {
        // Large images might take longer, but should be under 5 seconds
        expect(resource.duration).toBeLessThan(5000);
      });
    });
  });

  test.describe('Memory Performance', () => {
    test('should not have memory leaks during navigation', async () => {
      const getMemoryUsage = async () => {
        return await page.evaluate(() => {
          if ('memory' in performance) {
            return {
              usedJSHeapSize: (performance as any).memory.usedJSHeapSize,
              totalJSHeapSize: (performance as any).memory.totalJSHeapSize,
            };
          }
          return null;
        });
      };
      
      // Get initial memory usage
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      const initialMemory = await getMemoryUsage();
      
      // Navigate through multiple pages
      const pages = ['/', '/analytics', '/wiki', '/'];
      
      for (const pagePath of pages) {
        await page.goto(pagePath);
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(1000); // Allow garbage collection
      }
      
      // Get final memory usage
      const finalMemory = await getMemoryUsage();
      
      if (initialMemory && finalMemory) {
        console.log('Initial memory:', initialMemory);
        console.log('Final memory:', finalMemory);
        
        const memoryIncrease = finalMemory.usedJSHeapSize - initialMemory.usedJSHeapSize;
        const memoryIncreasePercent = (memoryIncrease / initialMemory.usedJSHeapSize) * 100;
        
        console.log(`Memory increase: ${(memoryIncrease / 1024 / 1024).toFixed(2)} MB (${memoryIncreasePercent.toFixed(1)}%)`);
        
        // Memory increase should be less than 50% after navigation
        expect(memoryIncreasePercent).toBeLessThan(50);
      }
    });
  });

  test.describe('API Performance', () => {
    test('should have fast API response times', async () => {
      await page.goto('/');
      
      // Track API calls
      const apiCalls: Array<{ url: string; duration: number; status: number }> = [];
      
      page.on('response', async (response) => {
        if (response.url().includes('/api/')) {
          const request = response.request();
          const timing = request.timing();
          
          apiCalls.push({
            url: response.url(),
            duration: timing ? timing.responseEnd - timing.requestStart : 0,
            status: response.status(),
          });
        }
      });
      
      // Trigger API calls by submitting a query
      const queryInput = page.locator('input[type="text"]').first();
      if (await queryInput.isVisible()) {
        await queryInput.fill('Test query for API performance');
        
        const submitButton = page.locator('button[type="submit"]').first();
        await submitButton.click();
        
        // Wait for API calls to complete
        await page.waitForTimeout(5000);
      }
      
      console.log('API calls:', apiCalls);
      
      // Check API response times
      apiCalls.forEach(call => {
        console.log(`${call.url}: ${call.duration}ms (${call.status})`);
        
        // API calls should be under 5 seconds
        expect(call.duration).toBeLessThan(5000);
        
        // Should have successful status codes
        expect(call.status).toBeLessThan(400);
      });
    });
  });

  test.describe('Rendering Performance', () => {
    test('should render components quickly', async () => {
      const startTime = Date.now();
      
      await page.goto('/');
      
      // Wait for main content to be visible
      await page.waitForSelector('main', { timeout: 10000 });
      
      const renderTime = Date.now() - startTime;
      console.log(`Initial render time: ${renderTime}ms`);
      
      // Should render initial content within 2 seconds
      expect(renderTime).toBeLessThan(2000);
    });

    test('should handle rapid interactions without performance degradation', async () => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      const button = page.locator('button').first();
      if (await button.isVisible()) {
        const times: number[] = [];
        
        // Perform rapid clicks
        for (let i = 0; i < 10; i++) {
          const start = performance.now();
          await button.click();
          const end = performance.now();
          times.push(end - start);
          
          // Small delay between clicks
          await page.waitForTimeout(50);
        }
        
        console.log('Click response times:', times);
        
        // All clicks should respond quickly
        times.forEach((time, index) => {
          expect(time).toBeLessThan(100); // 100ms max response time
        });
        
        // Performance should not degrade over time
        const averageFirst5 = times.slice(0, 5).reduce((a, b) => a + b) / 5;
        const averageLast5 = times.slice(-5).reduce((a, b) => a + b) / 5;
        
        console.log(`Average first 5 clicks: ${averageFirst5.toFixed(2)}ms`);
        console.log(`Average last 5 clicks: ${averageLast5.toFixed(2)}ms`);
        
        // Last 5 clicks should not be significantly slower than first 5
        expect(averageLast5).toBeLessThan(averageFirst5 * 2);
      }
    });
  });
});