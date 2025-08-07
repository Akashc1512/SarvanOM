/**
 * Lighthouse CI Configuration
 * MAANG-level performance budgets and quality gates
 */

module.exports = {
  ci: {
    collect: {
      url: ['http://localhost:3000'],
      startServerCommand: 'npm run start',
      startServerReadyPattern: 'ready on',
      startServerReadyTimeout: 30000,
      numberOfRuns: 3,
      settings: {
        preset: 'desktop',
        chromeFlags: [
          '--no-sandbox',
          '--disable-dev-shm-usage',
          '--disable-gpu',
          '--no-first-run',
          '--disable-extensions',
        ],
      },
    },
    upload: {
      target: 'temporary-public-storage',
    },
    assert: {
      assertions: {
        // Performance budgets
        'categories:performance': ['error', { minScore: 0.9 }],
        'categories:accessibility': ['error', { minScore: 0.95 }],
        'categories:best-practices': ['error', { minScore: 0.9 }],
        'categories:seo': ['error', { minScore: 0.9 }],
        
        // Core Web Vitals
        'first-contentful-paint': ['error', { maxNumericValue: 2000 }],
        'largest-contentful-paint': ['error', { maxNumericValue: 2500 }],
        'cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }],
        'total-blocking-time': ['error', { maxNumericValue: 300 }],
        
        // Resource budgets
        'resource-summary:script:size': ['error', { maxNumericValue: 500000 }], // 500KB
        'resource-summary:stylesheet:size': ['error', { maxNumericValue: 50000 }], // 50KB
        'resource-summary:document:size': ['error', { maxNumericValue: 50000 }], // 50KB
        'resource-summary:image:size': ['error', { maxNumericValue: 1000000 }], // 1MB
        'resource-summary:total:size': ['error', { maxNumericValue: 2000000 }], // 2MB
        
        // Network requests
        'resource-summary:total:count': ['error', { maxNumericValue: 50 }],
        'resource-summary:third-party:count': ['error', { maxNumericValue: 10 }],
        
        // Specific audits
        'unused-javascript': ['error', { maxNumericValue: 100000 }], // 100KB
        'unused-css-rules': ['error', { maxNumericValue: 20000 }], // 20KB
        'unminified-javascript': 'error',
        'unminified-css': 'error',
        'uses-text-compression': 'error',
        'uses-optimized-images': 'error',
        'uses-webp-images': 'error',
        'uses-responsive-images': 'error',
        'efficient-animated-content': 'error',
        
        // Security
        'is-on-https': 'error',
        'uses-http2': 'error',
        'no-vulnerable-libraries': 'error',
        
        // Accessibility
        'color-contrast': 'error',
        'image-alt': 'error',
        'label': 'error',
        'link-name': 'error',
        'button-name': 'error',
        'document-title': 'error',
        'html-has-lang': 'error',
        'html-lang-valid': 'error',
        'meta-viewport': 'error',
        
        // SEO
        'meta-description': 'error',
        'robots-txt': 'error',
        'canonical': 'error',
        
        // PWA (if applicable)
        'service-worker': 'off', // Disable if not using PWA
        'installable-manifest': 'off', // Disable if not using PWA
        'apple-touch-icon': 'off', // Disable if not needed
        
        // Modern web features
        'uses-rel-preconnect': 'error',
        'uses-rel-preload': 'error',
        'preload-lcp-image': 'error',
        'non-composited-animations': 'error',
        'prioritize-lcp-image': 'error',
      },
    },
    server: {
      port: 9001,
      storage: {
        storageMethod: 'sql',
        sqlDialect: 'sqlite',
        sqlDatabasePath: '.lighthouseci/database.sql',
      },
    },
  },
};