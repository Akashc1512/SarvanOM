# SarvanOM Universal Knowledge Platform - Frontend

A modern, enterprise-grade frontend implementation for the SarvanOM Universal Knowledge Platform, built with Next.js 15, React 19, and TypeScript.

## 🚀 Features

### Core Architecture

- **Next.js 15** with React 19 Server Components
- **TypeScript strict mode** for type safety
- **Zustand** for state management with persistence
- **Tailwind CSS** with comprehensive design system
- **Radix UI** primitives for accessibility

### AI-Powered Interface

- **Intelligent search** with natural language processing
- **AI suggestions** and auto-completion
- **Real-time collaboration** with cursor tracking
- **Smart document management** with AI assistance

### Enterprise Features

- **Multi-tenant architecture** support
- **Role-based access control** (RBAC)
- **Comprehensive analytics** and reporting
- **Real-time notifications** and updates
- **Advanced search** with faceted filtering

### Performance & Accessibility

- **Core Web Vitals** optimization
- **WCAG 2.1 AA** compliance
- **Progressive enhancement** patterns
- **Responsive design** for all devices
- **Internationalization** ready

## 🛠️ Technology Stack

### Core Framework

- **Next.js 15** - React framework with App Router
- **React 19** - Latest React with Server Components
- **TypeScript 5.5** - Strict type checking

### State Management

- **Zustand** - Lightweight state management
- **React Query** - Server state management
- **React Hook Form** - Form handling

### Styling & Design

- **Tailwind CSS 3.4** - Utility-first CSS
- **Class Variance Authority** - Component variants
- **Radix UI** - Accessible primitives
- **Lucide React** - Icon library

### Development Tools

- **ESLint** - Code linting with strict rules
- **Prettier** - Code formatting
- **Jest** - Unit testing
- **Playwright** - E2E testing
- **Storybook** - Component documentation

## 📦 Installation

### Prerequisites

- Node.js 18+
- npm or yarn
- Git

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd universal-knowledge-hub/frontend

# Install dependencies
npm install

# Set up environment variables
cp env.example .env.local

# Start development server
npm run dev
```

### Environment Variables

Create a `.env.local` file with the following variables:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Analytics (optional)
NEXT_PUBLIC_GOOGLE_ANALYTICS_ID=
NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION=

# Feature Flags
NEXT_PUBLIC_ENABLE_AI_FEATURES=true
NEXT_PUBLIC_ENABLE_COLLABORATION=true
NEXT_PUBLIC_ENABLE_ANALYTICS=true
```

## 🏗️ Project Structure

```
src/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Dashboard page
│   └── globals.css        # Global styles
├── components/            # React components
│   ├── ui/               # Base UI components
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── card.tsx
│   │   └── toast.tsx
│   ├── providers/        # Context providers
│   └── features/         # Feature-specific components
├── lib/                  # Utilities and configurations
│   ├── store.ts          # Zustand store
│   ├── api.ts            # API client
│   └── utils.ts          # Utility functions
├── hooks/                # Custom React hooks
├── types/                # TypeScript type definitions
└── styles/               # Additional styles
```

## 🎨 Design System

### Color Palette

The design system uses CSS custom properties for consistent theming:

```css
:root {
  --primary: 221.2 83.2% 53.3%;
  --secondary: 210 40% 96%;
  --accent: 210 40% 96%;
  --destructive: 0 84.2% 60.2%;
  --muted: 210 40% 96%;
  --border: 214.3 31.8% 91.4%;
  --input: 214.3 31.8% 91.4%;
  --ring: 221.2 83.2% 53.3%;
}
```

### Component Variants

Components use Class Variance Authority for consistent variants:

```tsx
const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive:
          "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-input bg-background hover:bg-accent",
        secondary:
          "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
);
```

## 🔧 Development

### Available Scripts

```bash
# Development
npm run dev              # Start development server
npm run build            # Build for production
npm run start            # Start production server

# Code Quality
npm run lint             # Run ESLint
npm run type-check       # Run TypeScript check
npm run format           # Format code with Prettier

# Testing
npm run test             # Run unit tests
npm run test:watch       # Run tests in watch mode
npm run test:coverage    # Run tests with coverage
npm run test:e2e         # Run E2E tests

# Storybook
npm run storybook        # Start Storybook
npm run build-storybook  # Build Storybook
```

### Code Quality Standards

#### TypeScript

- Strict mode enabled
- No `any` types allowed
- Branded types for domain safety
- Comprehensive type definitions

#### ESLint Rules

- React Hooks rules
- Accessibility rules (jsx-a11y)
- TypeScript-specific rules
- Import/export rules

#### Component Guidelines

- Use TypeScript for all components
- Implement proper accessibility
- Follow naming conventions
- Add JSDoc comments for complex logic

### Testing Strategy

#### Unit Tests

- Jest with React Testing Library
- Component testing
- Hook testing
- Utility function testing

#### Integration Tests

- API integration testing
- State management testing
- User interaction testing

#### E2E Tests

- Playwright for browser testing
- Critical user journeys
- Cross-browser compatibility

## 🚀 Performance Optimization

### Core Web Vitals

- **LCP** < 2.5s - Optimized image loading
- **FID** < 100ms - Efficient event handling
- **CLS** < 0.1 - Stable layout shifts

### Optimization Techniques

- **Code splitting** with dynamic imports
- **Image optimization** with Next.js Image
- **Font optimization** with next/font
- **Bundle analysis** with @next/bundle-analyzer

### Caching Strategy

- **Static generation** for content pages
- **Incremental Static Regeneration** for dynamic content
- **Service Worker** for offline support
- **CDN caching** for static assets

## 🔒 Security

### Security Measures

- **Content Security Policy** (CSP)
- **Input validation** and sanitization
- **XSS protection** with DOMPurify
- **CSRF protection** with tokens
- **Secure headers** configuration

### Authentication

- **OAuth 2.0** with PKCE
- **JWT token** management
- **Session management** with secure cookies
- **Role-based access control**

## 📱 Responsive Design

### Breakpoints

```css
/* Mobile First Approach */
xs: 475px    /* Small phones */
sm: 640px    /* Large phones */
md: 768px    /* Tablets */
lg: 1024px   /* Laptops */
xl: 1280px   /* Desktops */
2xl: 1400px  /* Large desktops */
```

### Design Principles

- **Mobile-first** responsive design
- **Touch-friendly** interface elements
- **Accessible** navigation patterns
- **Progressive enhancement**

## 🌐 Internationalization

### i18n Setup

- **react-i18next** for translations
- **next-i18next** for Next.js integration
- **Dynamic language detection**
- **Pluralization support**

### RTL Support

- **CSS logical properties**
- **RTL-aware components**
- **Bidirectional text support**

## 📊 Analytics & Monitoring

### Analytics Integration

- **Google Analytics 4** setup
- **Custom event tracking**
- **Performance monitoring**
- **Error tracking**

### User Analytics

- **Page view tracking**
- **User interaction tracking**
- **Conversion tracking**
- **A/B testing support**

## 🧪 Testing

### Test Structure

```
tests/
├── unit/                 # Unit tests
├── integration/          # Integration tests
├── e2e/                 # End-to-end tests
└── fixtures/            # Test data
```

### Testing Guidelines

- **Test-driven development** (TDD)
- **Comprehensive coverage** targets
- **Accessibility testing**
- **Performance testing**

## 📚 Documentation

### Component Documentation

- **Storybook** for component stories
- **JSDoc** comments for functions
- **README** files for complex features
- **API documentation**

### Architecture Documentation

- **System architecture** diagrams
- **Data flow** documentation
- **State management** patterns
- **Performance** guidelines

## 🚀 Deployment

### Production Build

```bash
# Build the application
npm run build

# Start production server
npm run start
```

### Environment Configuration

- **Environment-specific** configurations
- **Feature flags** for gradual rollouts
- **Monitoring** and logging setup
- **Error reporting** integration

### CI/CD Pipeline

- **GitHub Actions** workflow
- **Automated testing**
- **Code quality checks**
- **Deployment automation**

## 🤝 Contributing

### Development Workflow

1. **Fork** the repository
2. **Create** a feature branch
3. **Implement** changes with tests
4. **Submit** a pull request
5. **Code review** and approval
6. **Merge** to main branch

### Code Review Checklist

- [ ] TypeScript types are correct
- [ ] Tests are included and passing
- [ ] Accessibility requirements met
- [ ] Performance impact considered
- [ ] Documentation updated

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🆘 Support

### Getting Help

- **Documentation** - Check the docs first
- **Issues** - Search existing issues
- **Discussions** - Ask questions in discussions
- **Email** - Contact the development team

### Reporting Issues

- **Bug reports** with reproduction steps
- **Feature requests** with use cases
- **Performance issues** with metrics
- **Security vulnerabilities** privately

---

**Built with ❤️ by the SarvanOM Team**
