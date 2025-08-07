# 🧪 Frontend Testing Guide

This document provides comprehensive testing strategies and guidelines for the Sarvanom frontend application, following MAANG-level industry standards.

## 📋 Table of Contents

- [Testing Philosophy](#testing-philosophy)
- [Test Types](#test-types)
- [Getting Started](#getting-started)
- [Writing Tests](#writing-tests)
- [Running Tests](#running-tests)
- [CI/CD Integration](#cicd-integration)
- [Performance Testing](#performance-testing)
- [Accessibility Testing](#accessibility-testing)
- [Best Practices](#best-practices)

## 🎯 Testing Philosophy

Our testing strategy follows the **Testing Trophy** approach:

```
        /\
       /  \
      /E2E \     🎭 End-to-End (Few, High Value)
     /______\
    /        \
   /Integration\ 🔗 Integration (Some, Focused)
  /_____________\
 /               \
/     Unit        \ 🧪 Unit (Many, Fast)
/___________________\
|      Static      | 🔍 Static (Linting, TypeScript)
```

### Principles

1. **Fast Feedback**: Tests should run quickly and provide immediate feedback
2. **Reliable**: Tests should be deterministic and not flaky
3. **Maintainable**: Tests should be easy to read, write, and maintain
4. **Comprehensive**: Critical user journeys must be covered
5. **Performance-Aware**: Tests should validate performance requirements

## 🧪 Test Types

### 1. Static Analysis

- **ESLint**: Code quality and consistency
- **TypeScript**: Type safety and correctness
- **Prettier**: Code formatting

### 2. Unit Tests (Jest + React Testing Library)

- **What**: Individual component and function testing
- **When**: For complex logic, edge cases, and isolated functionality
- **Tools**: Jest, React Testing Library, @testing-library/user-event

```typescript
// Example unit test
import { renderWithProviders, screen } from '@/__tests__/utils/test-utils';
import { ErrorBoundary } from '../error-boundary';

test('should display error message when error occurs', () => {
  const ThrowError = () => {
    throw new Error('Test error');
  };

  renderWithProviders(
    <ErrorBoundary>
      <ThrowError />
    </ErrorBoundary>
  );

  expect(screen.getByText('Something went wrong')).toBeInTheDocument();
});
```

### 3. Integration Tests

- **What**: Testing component interactions and API integrations
- **When**: For user workflows spanning multiple components
- **Tools**: Jest, MSW (Mock Service Worker), React Testing Library

### 4. End-to-End Tests (Playwright)

- **What**: Full user journey testing in real browsers
- **When**: For critical user paths and cross-browser compatibility
- **Tools**: Playwright, multiple browsers (Chrome, Firefox, Safari)

```typescript
// Example E2E test
test('should submit query and display results', async ({ page }) => {
  await page.goto('/');
  
  await page.fill('input[type="text"]', 'What is AI?');
  await page.click('button[type="submit"]');
  
  await expect(page.locator('[data-testid="answer"]')).toBeVisible();
});
```

### 5. Performance Tests

- **What**: Core Web Vitals, bundle size, and runtime performance
- **When**: For every release and critical performance metrics
- **Tools**: Playwright, Lighthouse CI, Web Vitals API

### 6. Accessibility Tests

- **What**: WCAG compliance and screen reader compatibility
- **When**: For all interactive components and user interfaces
- **Tools**: Playwright, axe-core, manual testing

## 🚀 Getting Started

### Prerequisites

```bash
# Install dependencies
npm install

# Install Playwright browsers
npx playwright install
```

### Test Structure

```
frontend/
├── src/
│   ├── __tests__/
│   │   └── utils/
│   │       └── test-utils.tsx     # Custom testing utilities
│   ├── components/
│   │   └── __tests__/
│   │       └── *.test.tsx         # Component unit tests
│   ├── hooks/
│   │   └── __tests__/
│   │       └── *.test.ts          # Hook tests
│   └── lib/
│       └── __tests__/
│           └── *.test.ts          # Utility function tests
├── e2e/
│   ├── *.e2e.ts                   # End-to-end tests
│   ├── *.perf.test.ts             # Performance tests
│   └── *.a11y.test.ts             # Accessibility tests
├── jest.config.js                 # Jest configuration
├── playwright.config.ts           # Playwright configuration
└── .lighthouserc.js               # Lighthouse CI config
```

## ✍️ Writing Tests

### Unit Tests

Follow the **AAA** pattern:
- **Arrange**: Set up test data and conditions
- **Act**: Execute the code under test
- **Assert**: Verify the expected outcomes

```typescript
describe('UserProfile', () => {
  it('should display user name and email', () => {
    // Arrange
    const user = mockData.user({ name: 'John Doe', email: 'john@example.com' });
    
    // Act
    renderWithProviders(<UserProfile user={user} />);
    
    // Assert
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('john@example.com')).toBeInTheDocument();
  });
});
```

### E2E Tests

Focus on user journeys and business-critical flows:

```typescript
test.describe('Query Workflow', () => {
  test('should complete full query cycle', async ({ page }) => {
    // Navigate to app
    await page.goto('/');
    
    // Submit query
    await page.fill('[data-testid="query-input"]', 'Test query');
    await page.click('[data-testid="submit-button"]');
    
    // Verify loading state
    await expect(page.locator('[data-testid="loading"]')).toBeVisible();
    
    // Verify results
    await expect(page.locator('[data-testid="results"]')).toBeVisible({ timeout: 30000 });
    
    // Verify query in history
    await expect(page.locator('[data-testid="recent-queries"]')).toContainText('Test query');
  });
});
```

### Performance Tests

Test Core Web Vitals and performance budgets:

```typescript
test('should meet LCP threshold', async ({ page }) => {
  await page.goto('/');
  
  const lcp = await page.evaluate(() => {
    return new Promise((resolve) => {
      new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lcpEntry = entries[entries.length - 1];
        resolve(lcpEntry.startTime);
      }).observe({ type: 'largest-contentful-paint', buffered: true });
    });
  });
  
  expect(lcp).toBeLessThan(2500); // 2.5 seconds
});
```

## 🏃 Running Tests

### Local Development

```bash
# Run all unit tests
npm run test

# Watch mode for development
npm run test:watch

# Run with coverage
npm run test:coverage

# Run specific test file
npm run test Button.test.tsx

# Run E2E tests
npm run test:e2e

# Run E2E tests with UI
npm run test:e2e:ui

# Run performance tests
npm run test:perf

# Run accessibility tests
npm run test:a11y
```

### CI/CD Commands

```bash
# Run all tests for CI
npm run test:all

# Run unit tests for CI (no watch)
npm run test:ci

# Run E2E tests headless
npm run test:e2e

# Mobile testing
npm run test:mobile
```

### Debugging

```bash
# Debug E2E tests
npm run test:e2e:debug

# Run E2E tests in headed mode
npm run test:e2e:headed

# Debug specific test
npx playwright test dashboard.e2e.ts --debug
```

## 🔄 CI/CD Integration

Our CI/CD pipeline runs comprehensive testing:

### Pull Request Checks
- ✅ Linting and type checking
- ✅ Unit tests with coverage
- ✅ Build verification
- ✅ E2E tests (Chrome, Firefox, Safari)
- ✅ Performance tests
- ✅ Accessibility tests
- ✅ Security audit

### Quality Gates
- **Coverage**: Minimum 70% overall, 80% for lib files
- **Performance**: LCP < 2.5s, CLS < 0.1, FID < 100ms
- **Bundle Size**: < 500KB JavaScript, < 50KB CSS
- **Accessibility**: WCAG 2.1 AA compliance
- **Security**: No high/critical vulnerabilities

## ⚡ Performance Testing

### Core Web Vitals

We test against Google's Core Web Vitals:

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| LCP | ≤ 2.5s | 2.5s - 4.0s | > 4.0s |
| FID | ≤ 100ms | 100ms - 300ms | > 300ms |
| CLS | ≤ 0.1 | 0.1 - 0.25 | > 0.25 |

### Bundle Analysis

```bash
# Analyze bundle size
npm run analyze

# Generate bundle report
npm run bundle-analyzer

# Run Lighthouse
npm run lighthouse
```

### Performance Budget

- **JavaScript**: < 500KB total
- **CSS**: < 50KB total
- **Images**: < 1MB total
- **Total Resources**: < 2MB
- **Resource Count**: < 50 requests

## ♿ Accessibility Testing

### Automated Testing

```typescript
// Example accessibility test
test('should be accessible', async ({ page }) => {
  await page.goto('/');
  
  const results = await page.locator('body').evaluateHandle(async (body) => {
    const axe = await import('axe-core');
    return await axe.run(body);
  });
  
  expect(results.violations).toHaveLength(0);
});
```

### Manual Testing Checklist

- [ ] Keyboard navigation works
- [ ] Screen reader compatibility
- [ ] High contrast mode
- [ ] Focus indicators visible
- [ ] ARIA labels present
- [ ] Color contrast ratios met

### Tools

- **axe-core**: Automated accessibility testing
- **Lighthouse**: Accessibility audit
- **Wave**: Browser extension for manual testing
- **Screen readers**: NVDA, JAWS, VoiceOver

## 📝 Best Practices

### General Testing

1. **Test Behavior, Not Implementation**
   ```typescript
   // ❌ Bad - testing implementation
   expect(component.state.isLoading).toBe(true);
   
   // ✅ Good - testing behavior
   expect(screen.getByText('Loading...')).toBeInTheDocument();
   ```

2. **Use Data Test IDs for E2E**
   ```tsx
   // Component
   <button data-testid="submit-button">Submit</button>
   
   // Test
   await page.click('[data-testid="submit-button"]');
   ```

3. **Mock External Dependencies**
   ```typescript
   // Mock API calls
   jest.mock('@/services/api', () => ({
     fetchUser: jest.fn(() => Promise.resolve(mockUser)),
   }));
   ```

### Performance Testing

1. **Test on Real Devices**: Use device emulation for mobile testing
2. **Network Throttling**: Test under 3G/4G conditions
3. **Cache Testing**: Test both cold and warm cache scenarios
4. **Memory Leaks**: Monitor memory usage during long sessions

### E2E Testing

1. **Page Object Model**: Create reusable page objects
2. **Independent Tests**: Each test should be able to run in isolation
3. **Cleanup**: Clean up test data after each test
4. **Timeouts**: Use appropriate timeouts for different operations

### Accessibility Testing

1. **Test with Keyboard Only**: Ensure all functionality works without mouse
2. **Test with Screen Reader**: Use actual screen reader software
3. **Color Blindness**: Test with color blindness simulators
4. **Mobile Accessibility**: Test touch targets and gestures

## 🔗 Useful Resources

- [React Testing Library Documentation](https://testing-library.com/docs/react-testing-library/intro/)
- [Playwright Documentation](https://playwright.dev/)
- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [Web Vitals](https://web.dev/vitals/)
- [WCAG Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Lighthouse Scoring](https://web.dev/performance-scoring/)

## 🆘 Troubleshooting

### Common Issues

1. **Flaky Tests**: Use proper waits and avoid hardcoded timeouts
2. **Slow Tests**: Optimize test setup and use appropriate test levels
3. **Memory Issues**: Clean up resources and avoid memory leaks
4. **CI Failures**: Ensure tests work in headless environment

### Getting Help

- Check existing tests for examples
- Review test documentation
- Ask team members for guidance
- Create detailed bug reports for test issues

---

**Remember**: Good tests are an investment in code quality and developer productivity. Take time to write meaningful tests that provide value and confidence in your code! 🚀