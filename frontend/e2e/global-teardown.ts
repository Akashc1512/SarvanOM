/**
 * Playwright Global Teardown
 * Runs once after all tests
 */

import { FullConfig } from '@playwright/test';
import fs from 'fs';
import path from 'path';

async function globalTeardown(config: FullConfig) {
  console.log('🧹 Starting global teardown...');
  
  try {
    // Clean up temporary files
    const storageStatePath = 'e2e/storage-state.json';
    if (fs.existsSync(storageStatePath)) {
      fs.unlinkSync(storageStatePath);
      console.log('🗑️ Cleaned up storage state file');
    }
    
    // Clean up test artifacts if needed
    const testResultsDir = 'test-results';
    if (fs.existsSync(testResultsDir)) {
      // Keep test results but clean up temporary files
      const tempFiles = fs.readdirSync(testResultsDir)
        .filter(file => file.endsWith('.tmp') || file.endsWith('.temp'));
      
      tempFiles.forEach(file => {
        fs.unlinkSync(path.join(testResultsDir, file));
      });
      
      if (tempFiles.length > 0) {
        console.log(`🗑️ Cleaned up ${tempFiles.length} temporary files`);
      }
    }
    
    // Log test completion statistics
    console.log('📊 Test execution completed');
    console.log(`📁 Test artifacts saved in: ${testResultsDir}`);
    
    console.log('✅ Global teardown completed successfully');
    
  } catch (error) {
    console.error('❌ Global teardown failed:', error);
    // Don't throw error in teardown to avoid masking test failures
  }
}

export default globalTeardown;