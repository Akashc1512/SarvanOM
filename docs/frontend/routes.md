# Frontend Routes & Site Map

**Version**: 1.0  
**Last Updated**: September 9, 2025  
**Owner**: Frontend Team  

## Overview

This document defines the complete site map and route contracts for SarvanOM v2 frontend, following the Cosmic Pro design system with accessibility and consistency requirements. All routes are designed for optimal user experience and performance.

## Site Map Structure

### 1. Public Routes

#### 1.1 Landing & Marketing
- **`/`** - Homepage
  - **Purpose**: Main landing page with value proposition
  - **Components**: Hero section, features, testimonials, CTA
  - **Accessibility**: WCAG 2.1 AA compliant
  - **Performance**: < 2s First Contentful Paint

- **`/about`** - About Page
  - **Purpose**: Company information and mission
  - **Components**: Company story, team, values
  - **Accessibility**: Screen reader optimized
  - **Performance**: < 1.5s load time

- **`/features`** - Features Page
  - **Purpose**: Detailed feature descriptions
  - **Components**: Feature cards, comparisons, demos
  - **Accessibility**: Keyboard navigation support
  - **Performance**: < 2s load time

- **`/pricing`** - Pricing Page
  - **Purpose**: Pricing plans and comparison
  - **Components**: Pricing cards, feature comparison, FAQ
  - **Accessibility**: High contrast mode support
  - **Performance**: < 1.5s load time

#### 1.2 Authentication
- **`/login`** - Login Page
  - **Purpose**: User authentication
  - **Components**: Login form, social auth, forgot password
  - **Accessibility**: Form validation, error messages
  - **Performance**: < 1s load time

- **`/register`** - Registration Page
  - **Purpose**: User registration
  - **Components**: Registration form, terms acceptance
  - **Accessibility**: Progressive enhancement
  - **Performance**: < 1s load time

- **`/forgot-password`** - Password Reset
  - **Purpose**: Password recovery
  - **Components**: Email input, reset form
  - **Accessibility**: Clear error states
  - **Performance**: < 1s load time

### 2. Protected Routes

#### 2.1 Dashboard
- **`/dashboard`** - Main Dashboard
  - **Purpose**: User's main workspace
  - **Components**: Query interface, recent queries, analytics
  - **Accessibility**: ARIA landmarks, focus management
  - **Performance**: < 2s load time

- **`/dashboard/queries`** - Query History
  - **Purpose**: Query management and history
  - **Components**: Query list, filters, search, export
  - **Accessibility**: Table navigation, sorting
  - **Performance**: < 1.5s load time

- **`/dashboard/analytics`** - Analytics Dashboard
  - **Purpose**: Usage analytics and insights
  - **Components**: Charts, metrics, trends
  - **Accessibility**: Chart descriptions, data tables
  - **Performance**: < 2s load time

#### 2.2 Query Interface
- **`/query`** - Query Interface
  - **Purpose**: Main query input and processing
  - **Components**: Query input, results display, citations
  - **Accessibility**: Live regions, keyboard shortcuts
  - **Performance**: < 1s load time

- **`/query/[id]`** - Query Details
  - **Purpose**: Individual query results and details
  - **Components**: Query details, results, sources, sharing
  - **Accessibility**: Deep linking, breadcrumbs
  - **Performance**: < 1.5s load time

- **`/query/comprehensive`** - Comprehensive Query
  - **Purpose**: Advanced query processing
  - **Components**: Multi-step query, progress tracking
  - **Accessibility**: Progress indicators, status updates
  - **Performance**: < 2s load time

#### 2.3 Knowledge Management
- **`/knowledge`** - Knowledge Base
  - **Purpose**: Knowledge graph and document management
  - **Components**: Knowledge graph visualization, document browser
  - **Accessibility**: Graph navigation, alternative text
  - **Performance**: < 2s load time

- **`/knowledge/graph`** - Knowledge Graph
  - **Purpose**: Interactive knowledge graph
  - **Components**: Graph visualization, node details, filters
  - **Accessibility**: Keyboard navigation, screen reader support
  - **Performance**: < 2s load time

- **`/knowledge/documents`** - Document Library
  - **Purpose**: Document management and search
  - **Components**: Document list, search, upload, metadata
  - **Accessibility**: File upload accessibility, search results
  - **Performance**: < 1.5s load time

#### 2.4 Agents & Tools
- **`/agents`** - Agents Dashboard
  - **Purpose**: AI agent management and monitoring
  - **Components**: Agent list, status, configuration
  - **Accessibility**: Status indicators, configuration forms
  - **Performance**: < 1.5s load time

- **`/agents/database`** - Database Agent
  - **Purpose**: Database query and management agent
  - **Components**: Query interface, results, schema browser
  - **Accessibility**: SQL editor accessibility, result tables
  - **Performance**: < 2s load time

- **`/agents/browser`** - Browser Agent
  - **Purpose**: Web browsing and information gathering
  - **Components**: Browser interface, navigation, results
  - **Accessibility**: Browser navigation, content extraction
  - **Performance**: < 2s load time

- **`/agents/pdf`** - PDF Agent
  - **Purpose**: PDF document processing and analysis
  - **Components**: PDF upload, processing, analysis results
  - **Accessibility**: File upload, progress indicators
  - **Performance**: < 2s load time

- **`/agents/code-executor`** - Code Executor Agent
  - **Purpose**: Code execution and testing
  - **Components**: Code editor, execution results, output
  - **Accessibility**: Code editor accessibility, output formatting
  - **Performance**: < 2s load time

#### 2.5 Settings & Configuration
- **`/settings`** - User Settings
  - **Purpose**: User preferences and configuration
  - **Components**: Profile settings, preferences, notifications
  - **Accessibility**: Form accessibility, validation
  - **Performance**: < 1s load time

- **`/settings/api`** - API Settings
  - **Purpose**: API key management and configuration
  - **Components**: API key management, usage limits, billing
  - **Accessibility**: Secure form handling, confirmation dialogs
  - **Performance**: < 1s load time

- **`/settings/integrations`** - Integrations
  - **Purpose**: Third-party integrations and connections
  - **Components**: Integration list, configuration, status
  - **Accessibility**: Connection status, configuration forms
  - **Performance**: < 1.5s load time

### 3. API Routes

#### 3.1 Query API
- **`/api/query`** - General Query Endpoint
  - **Purpose**: Process general queries
  - **Methods**: POST
  - **Response**: Query results and metadata
  - **Performance**: < 5s response time

- **`/api/query/comprehensive`** - Comprehensive Query
  - **Purpose**: Process complex queries
  - **Methods**: POST
  - **Response**: Detailed query results
  - **Performance**: < 10s response time

- **`/api/query/simple`** - Simple Query
  - **Purpose**: Process simple queries
  - **Methods**: POST
  - **Response**: Quick query results
  - **Performance**: < 5s response time

#### 3.2 Analytics API
- **`/api/analytics`** - Analytics Data
  - **Purpose**: Provide analytics data
  - **Methods**: GET
  - **Response**: Analytics metrics and trends
  - **Performance**: < 1s response time

- **`/api/metrics`** - System Metrics
  - **Purpose**: Provide system performance metrics
  - **Methods**: GET
  - **Response**: System metrics and health
  - **Performance**: < 1s response time

#### 3.3 Agent API
- **`/api/agents/database`** - Database Agent
  - **Purpose**: Database agent operations
  - **Methods**: POST, GET
  - **Response**: Database query results
  - **Performance**: < 7s response time

- **`/api/agents/browser`** - Browser Agent
  - **Purpose**: Browser agent operations
  - **Methods**: POST, GET
  - **Response**: Web browsing results
  - **Performance**: < 10s response time

- **`/api/agents/pdf`** - PDF Agent
  - **Purpose**: PDF processing operations
  - **Methods**: POST, GET
  - **Response**: PDF analysis results
  - **Performance**: < 10s response time

- **`/api/agents/code-executor`** - Code Executor Agent
  - **Purpose**: Code execution operations
  - **Methods**: POST, GET
  - **Response**: Code execution results
  - **Performance**: < 7s response time

#### 3.4 System API
- **`/api/system/diagnostics`** - System Diagnostics
  - **Purpose**: System health and diagnostics
  - **Methods**: GET
  - **Response**: System status and diagnostics
  - **Performance**: < 1s response time

- **`/api/system/health`** - Health Check
  - **Purpose**: System health status
  - **Methods**: GET
  - **Response**: Health status
  - **Performance**: < 500ms response time

## Route Contracts

### 1. Route Parameters

#### 1.1 Query Parameters
```typescript
interface QueryParams {
  // Pagination
  page?: number;
  limit?: number;
  
  // Filtering
  filter?: string;
  sort?: string;
  order?: 'asc' | 'desc';
  
  // Search
  search?: string;
  category?: string;
  
  // Date range
  from?: string;
  to?: string;
}
```

#### 1.2 Path Parameters
```typescript
interface PathParams {
  // Query ID
  id?: string;
  
  // User ID
  userId?: string;
  
  // Document ID
  documentId?: string;
  
  // Agent ID
  agentId?: string;
}
```

### 2. Route Guards

#### 2.1 Authentication Guard
```typescript
interface AuthGuard {
  // Check if user is authenticated
  isAuthenticated: boolean;
  
  // Check if user has required permissions
  hasPermission: (permission: string) => boolean;
  
  // Redirect to login if not authenticated
  redirectToLogin: () => void;
  
  // Redirect to dashboard if authenticated
  redirectToDashboard: () => void;
}
```

#### 2.2 Role-Based Access Control
```typescript
interface RoleGuard {
  // Check if user has required role
  hasRole: (role: string) => boolean;
  
  // Check if user has any of the required roles
  hasAnyRole: (roles: string[]) => boolean;
  
  // Check if user has all required roles
  hasAllRoles: (roles: string[]) => boolean;
}
```

### 3. Route Metadata

#### 3.1 SEO Metadata
```typescript
interface SEOMetadata {
  title: string;
  description: string;
  keywords: string[];
  ogTitle?: string;
  ogDescription?: string;
  ogImage?: string;
  twitterCard?: string;
  canonical?: string;
}
```

#### 3.2 Performance Metadata
```typescript
interface PerformanceMetadata {
  // Expected load time
  expectedLoadTime: number;
  
  // Critical resources
  criticalResources: string[];
  
  // Preload hints
  preloadHints: string[];
  
  // Lazy load components
  lazyLoadComponents: string[];
}
```

## Navigation Structure

### 1. Main Navigation

#### 1.1 Primary Navigation
```typescript
const primaryNavigation = [
  {
    label: 'Dashboard',
    href: '/dashboard',
    icon: 'HomeIcon',
    description: 'Main workspace and overview'
  },
  {
    label: 'Query',
    href: '/query',
    icon: 'SearchIcon',
    description: 'Ask questions and get answers'
  },
  {
    label: 'Knowledge',
    href: '/knowledge',
    icon: 'BookOpenIcon',
    description: 'Manage knowledge base and documents'
  },
  {
    label: 'Agents',
    href: '/agents',
    icon: 'CogIcon',
    description: 'AI agents and tools'
  },
  {
    label: 'Analytics',
    href: '/dashboard/analytics',
    icon: 'ChartBarIcon',
    description: 'Usage analytics and insights'
  }
];
```

#### 1.2 Secondary Navigation
```typescript
const secondaryNavigation = [
  {
    label: 'Settings',
    href: '/settings',
    icon: 'CogIcon',
    description: 'User preferences and configuration'
  },
  {
    label: 'Help',
    href: '/help',
    icon: 'QuestionMarkCircleIcon',
    description: 'Documentation and support'
  },
  {
    label: 'Logout',
    href: '/logout',
    icon: 'LogoutIcon',
    description: 'Sign out of your account'
  }
];
```

### 2. Breadcrumb Navigation

#### 2.1 Breadcrumb Structure
```typescript
interface BreadcrumbItem {
  label: string;
  href?: string;
  current?: boolean;
}

const breadcrumbMap: Record<string, BreadcrumbItem[]> = {
  '/dashboard': [
    { label: 'Dashboard', current: true }
  ],
  '/dashboard/analytics': [
    { label: 'Dashboard', href: '/dashboard' },
    { label: 'Analytics', current: true }
  ],
  '/query/[id]': [
    { label: 'Dashboard', href: '/dashboard' },
    { label: 'Query', href: '/query' },
    { label: 'Query Details', current: true }
  ]
};
```

## Route Performance

### 1. Performance Requirements

#### 1.1 Load Time Targets
- **Landing Pages**: < 2s First Contentful Paint
- **Dashboard**: < 2s load time
- **Query Interface**: < 1s load time
- **API Routes**: < 1s response time

#### 1.2 Optimization Strategies
- **Code Splitting**: Lazy load non-critical components
- **Image Optimization**: WebP format, responsive images
- **Caching**: Static assets, API responses
- **Preloading**: Critical resources, next page

### 2. Accessibility Requirements

#### 2.1 WCAG 2.1 AA Compliance
- **Keyboard Navigation**: All interactive elements accessible
- **Screen Reader**: Proper ARIA labels and landmarks
- **Color Contrast**: Minimum 4.5:1 ratio
- **Focus Management**: Visible focus indicators

#### 2.2 Progressive Enhancement
- **Core Functionality**: Works without JavaScript
- **Enhanced Experience**: JavaScript enhances functionality
- **Graceful Degradation**: Fallbacks for unsupported features

## Route Testing

### 1. Unit Tests

#### 1.1 Route Component Tests
```typescript
describe('Route Components', () => {
  test('renders homepage correctly', () => {
    render(<HomePage />);
    expect(screen.getByRole('main')).toBeInTheDocument();
  });
  
  test('handles authentication redirect', () => {
    render(<ProtectedRoute><Dashboard /></ProtectedRoute>);
    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });
});
```

#### 1.2 Route Guard Tests
```typescript
describe('Route Guards', () => {
  test('allows access with valid authentication', () => {
    const user = { isAuthenticated: true };
    const result = authGuard.canActivate(user);
    expect(result).toBe(true);
  });
  
  test('denies access without authentication', () => {
    const user = { isAuthenticated: false };
    const result = authGuard.canActivate(user);
    expect(result).toBe(false);
  });
});
```

### 2. Integration Tests

#### 2.1 End-to-End Route Tests
```typescript
describe('Route Integration', () => {
  test('complete user journey', async () => {
    // Navigate to homepage
    await page.goto('/');
    
    // Click login
    await page.click('[data-testid="login-button"]');
    
    // Fill login form
    await page.fill('[data-testid="email-input"]', 'user@example.com');
    await page.fill('[data-testid="password-input"]', 'password');
    
    // Submit form
    await page.click('[data-testid="submit-button"]');
    
    // Verify redirect to dashboard
    expect(page.url()).toBe('/dashboard');
  });
});
```

---

## Appendix

### A. Route Configuration Files
- `next.config.js` - Next.js configuration
- `middleware.ts` - Route middleware
- `app/layout.tsx` - Root layout
- `app/page.tsx` - Homepage

### B. Navigation Components
- `components/Navigation.tsx` - Main navigation
- `components/Breadcrumbs.tsx` - Breadcrumb navigation
- `components/Sidebar.tsx` - Sidebar navigation
- `components/Footer.tsx` - Footer navigation

### C. Route Utilities
- `utils/routing.ts` - Route utilities
- `utils/navigation.ts` - Navigation helpers
- `utils/guards.ts` - Route guards
- `utils/metadata.ts` - SEO metadata
