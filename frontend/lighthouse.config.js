/**
 * Lighthouse Configuration for Cosmic Pro Frontend
 * Performance testing and optimization setup
 */

module.exports = {
  ci: {
    collect: {
      url: [
        'http://localhost:3000/',
        'http://localhost:3000/search',
        'http://localhost:3000/analytics',
        'http://localhost:3000/blog',
        'http://localhost:3000/multimodal-demo',
        'http://localhost:3000/login',
        'http://localhost:3000/register',
        'http://localhost:3000/comprehensive-query',
        'http://localhost:3000/graph-visualization'
      ],
      numberOfRuns: 3,
      settings: {
        chromeFlags: '--no-sandbox --disable-dev-shm-usage',
        preset: 'desktop',
        throttling: {
          rttMs: 40,
          throughputKbps: 10240,
          cpuSlowdownMultiplier: 1,
          requestLatencyMs: 0,
          downloadThroughputKbps: 0,
          uploadThroughputKbps: 0
        },
        screenEmulation: {
          mobile: false,
          width: 1350,
          height: 940,
          deviceScaleFactor: 1,
          disabled: false
        },
        formFactor: 'desktop',
        locale: 'en-US',
        blockedUrlPatterns: null,
        additionalTraceCategories: null,
        extraHeaders: null,
        precomputedLanternData: null,
        skipAudits: null,
        onlyAudits: null,
        onlyCategories: null,
        skipCategories: null
      }
    },
    assert: {
      assertions: {
        // Performance targets
        'categories:performance': ['error', { minScore: 0.90 }],
        'categories:accessibility': ['error', { minScore: 0.95 }],
        'categories:best-practices': ['error', { minScore: 0.95 }],
        'categories:seo': ['error', { minScore: 0.90 }],
        
        // Core Web Vitals
        'first-contentful-paint': ['error', { maxNumericValue: 2000 }],
        'largest-contentful-paint': ['error', { maxNumericValue: 2500 }],
        'cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }],
        'total-blocking-time': ['error', { maxNumericValue: 300 }],
        'speed-index': ['error', { maxNumericValue: 3000 }],
        
        // Performance metrics
        'interactive': ['error', { maxNumericValue: 3000 }],
        'max-potential-fid': ['error', { maxNumericValue: 100 }],
        
        // Resource optimization
        'unused-css-rules': ['warn', { maxNumericValue: 0 }],
        'unused-javascript': ['warn', { maxNumericValue: 0 }],
        'render-blocking-resources': ['warn', { maxNumericValue: 0 }],
        'unminified-css': ['warn', { maxNumericValue: 0 }],
        'unminified-javascript': ['warn', { maxNumericValue: 0 }],
        'efficient-animated-content': ['warn', { maxNumericValue: 0 }],
        'uses-optimized-images': ['warn', { maxNumericValue: 0 }],
        'uses-webp-images': ['warn', { maxNumericValue: 0 }],
        'uses-text-compression': ['warn', { maxNumericValue: 0 }],
        'uses-rel-preconnect': ['warn', { maxNumericValue: 0 }],
        'uses-rel-preload': ['warn', { maxNumericValue: 0 }],
        
        // Accessibility
        'color-contrast': ['error', { maxNumericValue: 0 }],
        'image-alt': ['error', { maxNumericValue: 0 }],
        'label': ['error', { maxNumericValue: 0 }],
        'link-name': ['error', { maxNumericValue: 0 }],
        'button-name': ['error', { maxNumericValue: 0 }],
        'html-has-lang': ['error', { maxNumericValue: 0 }],
        'html-lang-valid': ['error', { maxNumericValue: 0 }],
        'meta-description': ['error', { maxNumericValue: 0 }],
        'document-title': ['error', { maxNumericValue: 0 }],
        'heading-order': ['error', { maxNumericValue: 0 }],
        'focus-traps': ['error', { maxNumericValue: 0 }],
        'focus-order-semantics': ['error', { maxNumericValue: 0 }],
        'logical-tab-order': ['error', { maxNumericValue: 0 }],
        'managed-focus': ['error', { maxNumericValue: 0 }],
        'visual-order-follows-dom': ['error', { maxNumericValue: 0 }],
        'use-landmarks': ['error', { maxNumericValue: 0 }],
        'aria-allowed-attr': ['error', { maxNumericValue: 0 }],
        'aria-required-attr': ['error', { maxNumericValue: 0 }],
        'aria-required-children': ['error', { maxNumericValue: 0 }],
        'aria-required-parent': ['error', { maxNumericValue: 0 }],
        'aria-roles': ['error', { maxNumericValue: 0 }],
        'aria-valid-attr': ['error', { maxNumericValue: 0 }],
        'aria-valid-attr-value': ['error', { maxNumericValue: 0 }],
        'duplicate-id': ['error', { maxNumericValue: 0 }],
        'duplicate-id-aria': ['error', { maxNumericValue: 0 }],
        
        // Best Practices
        'is-on-https': ['error', { maxNumericValue: 0 }],
        'uses-http2': ['warn', { maxNumericValue: 0 }],
        'no-vulnerable-libraries': ['error', { maxNumericValue: 0 }],
        'csp-xss': ['warn', { maxNumericValue: 0 }],
        'deprecations': ['warn', { maxNumericValue: 0 }],
        'errors-in-console': ['warn', { maxNumericValue: 0 }],
        'image-size-responsive': ['warn', { maxNumericValue: 0 }],
        'efficient-animated-content': ['warn', { maxNumericValue: 0 }],
        'appcache-manifest': ['warn', { maxNumericValue: 0 }],
        'doctype': ['error', { maxNumericValue: 0 }],
        'charset': ['error', { maxNumericValue: 0 }],
        'dom-size': ['warn', { maxNumericValue: 1500 }],
        'external-anchors-use-rel-noopener': ['warn', { maxNumericValue: 0 }],
        'geolocation-on-start': ['warn', { maxNumericValue: 0 }],
        'no-document-write': ['warn', { maxNumericValue: 0 }],
        'no-mutation-events': ['warn', { maxNumericValue: 0 }],
        'no-vulnerable-libraries': ['error', { maxNumericValue: 0 }],
        'notification-on-start': ['warn', { maxNumericValue: 0 }],
        'object-alt': ['warn', { maxNumericValue: 0 }],
        'password-inputs-can-be-pasted-into': ['warn', { maxNumericValue: 0 }],
        'uses-responsive-images': ['warn', { maxNumericValue: 0 }],
        'valid-source-maps': ['warn', { maxNumericValue: 0 }],
        'video-caption': ['warn', { maxNumericValue: 0 }],
        'video-description': ['warn', { maxNumericValue: 0 }],
        
        // SEO
        'canonical': ['error', { maxNumericValue: 0 }],
        'hreflang': ['warn', { maxNumericValue: 0 }],
        'is-crawlable': ['error', { maxNumericValue: 0 }],
        'robots-txt': ['warn', { maxNumericValue: 0 }],
        'structured-data': ['warn', { maxNumericValue: 0 }],
        'tap-targets': ['error', { maxNumericValue: 0 }],
        'viewport': ['error', { maxNumericValue: 0 }],
        'font-display': ['warn', { maxNumericValue: 0 }],
        'link-text': ['warn', { maxNumericValue: 0 }],
        'crawlable-anchors': ['warn', { maxNumericValue: 0 }],
        'is-on-https': ['error', { maxNumericValue: 0 }],
        'plugins': ['warn', { maxNumericValue: 0 }],
        'redirects-http': ['error', { maxNumericValue: 0 }],
        'uses-long-cache-ttl': ['warn', { maxNumericValue: 0 }],
        'uses-http2': ['warn', { maxNumericValue: 0 }],
        'uses-passive-event-listeners': ['warn', { maxNumericValue: 0 }]
      }
    },
    upload: {
      target: 'temporary-public-storage'
    }
  }
};
