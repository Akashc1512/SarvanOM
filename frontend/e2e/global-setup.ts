/**
 * Playwright Global Setup
 * Runs once before all tests
 */

import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting global setup...');
  
  // Launch browser for setup
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    // Wait for the application to be ready
    console.log('⏳ Waiting for application to be ready...');
    await page.goto(config.projects[0]?.use?.baseURL || 'http://localhost:3000');
    
    // Wait for the main content to load
    await page.waitForSelector('body', { timeout: 30000 });
    
    // Perform any global authentication or setup here
    console.log('🔐 Setting up authentication...');
    
    // Example: Set up test user session
    await page.evaluate(() => {
      localStorage.setItem('test-mode', 'true');
      localStorage.setItem('auth-token', 'test-token-123');
    });
    
    // Store authentication state
    await page.context().storageState({
      path: 'e2e/storage-state.json',
    });
    
    console.log('✅ Global setup completed successfully');
    
  } catch (error) {
    console.error('❌ Global setup failed:', error);
    throw error;
  } finally {
    await browser.close();
  }
}

export default globalSetup;