# Design Tokens & Naming Conventions

**Version**: 1.0  
**Last Updated**: September 9, 2025  
**Owner**: Frontend Team  

## Overview

This document defines the design tokens and naming conventions for SarvanOM v2 frontend, following the Cosmic Pro design system. Design tokens ensure consistency across all components and provide a scalable foundation for the design system.

## Design Token Categories

### 1. Color Tokens

#### 1.1 Primary Colors
```typescript
const primaryColors = {
  // Primary brand colors
  primary: {
    50: '#f0f9ff',   // Lightest
    100: '#e0f2fe',
    200: '#bae6fd',
    300: '#7dd3fc',
    400: '#38bdf8',
    500: '#0ea5e9',  // Base
    600: '#0284c7',
    700: '#0369a1',
    800: '#075985',
    900: '#0c4a6e',  // Darkest
  },
  
  // Secondary brand colors
  secondary: {
    50: '#f8fafc',
    100: '#f1f5f9',
    200: '#e2e8f0',
    300: '#cbd5e1',
    400: '#94a3b8',
    500: '#64748b',  // Base
    600: '#475569',
    700: '#334155',
    800: '#1e293b',
    900: '#0f172a',
  }
};
```

#### 1.2 Semantic Colors
```typescript
const semanticColors = {
  // Success colors
  success: {
    50: '#f0fdf4',
    100: '#dcfce7',
    200: '#bbf7d0',
    300: '#86efac',
    400: '#4ade80',
    500: '#22c55e',  // Base
    600: '#16a34a',
    700: '#15803d',
    800: '#166534',
    900: '#14532d',
  },
  
  // Warning colors
  warning: {
    50: '#fffbeb',
    100: '#fef3c7',
    200: '#fde68a',
    300: '#fcd34d',
    400: '#fbbf24',
    500: '#f59e0b',  // Base
    600: '#d97706',
    700: '#b45309',
    800: '#92400e',
    900: '#78350f',
  },
  
  // Error colors
  error: {
    50: '#fef2f2',
    100: '#fee2e2',
    200: '#fecaca',
    300: '#fca5a5',
    400: '#f87171',
    500: '#ef4444',  // Base
    600: '#dc2626',
    700: '#b91c1c',
    800: '#991b1b',
    900: '#7f1d1d',
  },
  
  // Info colors
  info: {
    50: '#eff6ff',
    100: '#dbeafe',
    200: '#bfdbfe',
    300: '#93c5fd',
    400: '#60a5fa',
    500: '#3b82f6',  // Base
    600: '#2563eb',
    700: '#1d4ed8',
    800: '#1e40af',
    900: '#1e3a8a',
  }
};
```

#### 1.3 Neutral Colors
```typescript
const neutralColors = {
  // Grayscale colors
  gray: {
    50: '#f9fafb',
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',  // Base
    600: '#4b5563',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',
  },
  
  // Pure colors
  white: '#ffffff',
  black: '#000000',
  transparent: 'transparent',
};
```

### 2. Typography Tokens

#### 2.1 Font Families
```typescript
const fontFamilies = {
  // Primary font family
  sans: [
    'Inter',
    '-apple-system',
    'BlinkMacSystemFont',
    'Segoe UI',
    'Roboto',
    'Helvetica Neue',
    'Arial',
    'sans-serif'
  ],
  
  // Monospace font family
  mono: [
    'JetBrains Mono',
    'Fira Code',
    'Monaco',
    'Consolas',
    'Liberation Mono',
    'Courier New',
    'monospace'
  ],
  
  // Display font family
  display: [
    'Inter Display',
    'Inter',
    '-apple-system',
    'BlinkMacSystemFont',
    'Segoe UI',
    'Roboto',
    'Helvetica Neue',
    'Arial',
    'sans-serif'
  ]
};
```

#### 2.2 Font Sizes
```typescript
const fontSizes = {
  // Text sizes
  xs: '0.75rem',    // 12px
  sm: '0.875rem',   // 14px
  base: '1rem',     // 16px
  lg: '1.125rem',   // 18px
  xl: '1.25rem',    // 20px
  '2xl': '1.5rem',  // 24px
  '3xl': '1.875rem', // 30px
  '4xl': '2.25rem', // 36px
  '5xl': '3rem',    // 48px
  '6xl': '3.75rem', // 60px
  '7xl': '4.5rem',  // 72px
  '8xl': '6rem',    // 96px
  '9xl': '8rem',    // 128px
};
```

#### 2.3 Font Weights
```typescript
const fontWeights = {
  thin: '100',
  extralight: '200',
  light: '300',
  normal: '400',
  medium: '500',
  semibold: '600',
  bold: '700',
  extrabold: '800',
  black: '900',
};
```

#### 2.4 Line Heights
```typescript
const lineHeights = {
  none: '1',
  tight: '1.25',
  snug: '1.375',
  normal: '1.5',
  relaxed: '1.625',
  loose: '2',
};
```

#### 2.5 Letter Spacing
```typescript
const letterSpacing = {
  tighter: '-0.05em',
  tight: '-0.025em',
  normal: '0em',
  wide: '0.025em',
  wider: '0.05em',
  widest: '0.1em',
};
```

### 3. Spacing Tokens

#### 3.1 Spacing Scale
```typescript
const spacing = {
  0: '0',
  px: '1px',
  0.5: '0.125rem',  // 2px
  1: '0.25rem',     // 4px
  1.5: '0.375rem',  // 6px
  2: '0.5rem',      // 8px
  2.5: '0.625rem',  // 10px
  3: '0.75rem',     // 12px
  3.5: '0.875rem',  // 14px
  4: '1rem',        // 16px
  5: '1.25rem',     // 20px
  6: '1.5rem',      // 24px
  7: '1.75rem',     // 28px
  8: '2rem',        // 32px
  9: '2.25rem',     // 36px
  10: '2.5rem',     // 40px
  11: '2.75rem',    // 44px
  12: '3rem',       // 48px
  14: '3.5rem',     // 56px
  16: '4rem',       // 64px
  20: '5rem',       // 80px
  24: '6rem',       // 96px
  28: '7rem',       // 112px
  32: '8rem',       // 128px
  36: '9rem',       // 144px
  40: '10rem',      // 160px
  44: '11rem',      // 176px
  48: '12rem',      // 192px
  52: '13rem',      // 208px
  56: '14rem',      // 224px
  60: '15rem',      // 240px
  64: '16rem',      // 256px
  72: '18rem',      // 288px
  80: '20rem',      // 320px
  96: '24rem',      // 384px
};
```

#### 3.2 Component Spacing
```typescript
const componentSpacing = {
  // Button spacing
  button: {
    padding: {
      sm: '0.5rem 0.75rem',
      md: '0.75rem 1rem',
      lg: '1rem 1.5rem',
    },
    gap: '0.5rem',
  },
  
  // Form spacing
  form: {
    fieldGap: '1rem',
    labelGap: '0.5rem',
    errorGap: '0.25rem',
  },
  
  // Card spacing
  card: {
    padding: '1.5rem',
    gap: '1rem',
  },
  
  // Navigation spacing
  navigation: {
    itemGap: '0.5rem',
    sectionGap: '1rem',
  },
};
```

### 4. Border Tokens

#### 4.1 Border Radius
```typescript
const borderRadius = {
  none: '0',
  sm: '0.125rem',   // 2px
  base: '0.25rem',  // 4px
  md: '0.375rem',   // 6px
  lg: '0.5rem',     // 8px
  xl: '0.75rem',    // 12px
  '2xl': '1rem',    // 16px
  '3xl': '1.5rem',  // 24px
  full: '9999px',
};
```

#### 4.2 Border Width
```typescript
const borderWidth = {
  0: '0',
  1: '1px',
  2: '2px',
  4: '4px',
  8: '8px',
};
```

#### 4.3 Border Styles
```typescript
const borderStyles = {
  solid: 'solid',
  dashed: 'dashed',
  dotted: 'dotted',
  double: 'double',
  none: 'none',
};
```

### 5. Shadow Tokens

#### 5.1 Box Shadows
```typescript
const boxShadows = {
  none: 'none',
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  base: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
  inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
};
```

#### 5.2 Drop Shadows
```typescript
const dropShadows = {
  none: 'none',
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  base: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
};
```

### 6. Animation Tokens

#### 6.1 Transition Durations
```typescript
const transitionDurations = {
  75: '75ms',
  100: '100ms',
  150: '150ms',
  200: '200ms',
  300: '300ms',
  500: '500ms',
  700: '700ms',
  1000: '1000ms',
};
```

#### 6.2 Transition Timing Functions
```typescript
const transitionTimingFunctions = {
  linear: 'linear',
  in: 'cubic-bezier(0.4, 0, 1, 1)',
  out: 'cubic-bezier(0, 0, 0.2, 1)',
  'in-out': 'cubic-bezier(0.4, 0, 0.2, 1)',
};
```

#### 6.3 Animation Keyframes
```typescript
const keyframes = {
  fadeIn: {
    '0%': { opacity: '0' },
    '100%': { opacity: '1' },
  },
  fadeOut: {
    '0%': { opacity: '1' },
    '100%': { opacity: '0' },
  },
  slideIn: {
    '0%': { transform: 'translateY(-100%)' },
    '100%': { transform: 'translateY(0)' },
  },
  slideOut: {
    '0%': { transform: 'translateY(0)' },
    '100%': { transform: 'translateY(-100%)' },
  },
  scaleIn: {
    '0%': { transform: 'scale(0.95)', opacity: '0' },
    '100%': { transform: 'scale(1)', opacity: '1' },
  },
  scaleOut: {
    '0%': { transform: 'scale(1)', opacity: '1' },
    '100%': { transform: 'scale(0.95)', opacity: '0' },
  },
};
```

### 7. Z-Index Tokens

#### 7.1 Z-Index Scale
```typescript
const zIndex = {
  auto: 'auto',
  0: '0',
  10: '10',
  20: '20',
  30: '30',
  40: '40',
  50: '50',
  dropdown: '1000',
  sticky: '1020',
  fixed: '1030',
  modal: '1040',
  popover: '1050',
  tooltip: '1060',
  toast: '1070',
};
```

## Naming Conventions

### 1. Token Naming

#### 1.1 Color Naming
```typescript
// Primary colors
primary-50, primary-100, ..., primary-900

// Semantic colors
success-500, warning-500, error-500, info-500

// Neutral colors
gray-50, gray-100, ..., gray-900
white, black, transparent
```

#### 1.2 Typography Naming
```typescript
// Font families
font-sans, font-mono, font-display

// Font sizes
text-xs, text-sm, text-base, text-lg, ..., text-9xl

// Font weights
font-thin, font-light, font-normal, font-medium, ..., font-black

// Line heights
leading-none, leading-tight, leading-normal, ..., leading-loose
```

#### 1.3 Spacing Naming
```typescript
// Spacing scale
space-0, space-1, space-2, ..., space-96

// Component spacing
button-padding-sm, button-padding-md, button-padding-lg
form-field-gap, form-label-gap, form-error-gap
```

### 2. Component Naming

#### 2.1 Component Structure
```typescript
// Component naming
ComponentName.tsx

// Props naming
interface ComponentNameProps {
  variant?: 'primary' | 'secondary' | 'tertiary';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  children: React.ReactNode;
}
```

#### 2.2 CSS Class Naming
```typescript
// BEM methodology
.component-name
.component-name--modifier
.component-name__element
.component-name__element--modifier

// Examples
.button
.button--primary
.button--large
.button__icon
.button__icon--left
```

### 3. File Naming

#### 3.1 Component Files
```
components/
├── Button/
│   ├── Button.tsx
│   ├── Button.test.tsx
│   ├── Button.stories.tsx
│   └── index.ts
├── Input/
│   ├── Input.tsx
│   ├── Input.test.tsx
│   ├── Input.stories.tsx
│   └── index.ts
```

#### 3.2 Utility Files
```
utils/
├── tokens.ts
├── helpers.ts
├── constants.ts
└── types.ts
```

## Usage Guidelines

### 1. Token Usage

#### 1.1 CSS Custom Properties
```css
:root {
  /* Color tokens */
  --color-primary-500: #0ea5e9;
  --color-primary-600: #0284c7;
  
  /* Typography tokens */
  --font-size-base: 1rem;
  --font-weight-medium: 500;
  
  /* Spacing tokens */
  --spacing-4: 1rem;
  --spacing-8: 2rem;
  
  /* Border tokens */
  --border-radius-lg: 0.5rem;
  --border-width-1: 1px;
}
```

#### 1.2 JavaScript/TypeScript Usage
```typescript
import { tokens } from '@/tokens';

const styles = {
  color: tokens.colors.primary[500],
  fontSize: tokens.fontSizes.base,
  padding: tokens.spacing[4],
  borderRadius: tokens.borderRadius.lg,
};
```

### 2. Component Usage

#### 2.1 Token Integration
```typescript
import { tokens } from '@/tokens';

const Button = styled.button<ButtonProps>`
  background-color: ${({ variant }) => 
    variant === 'primary' ? tokens.colors.primary[500] : tokens.colors.gray[500]
  };
  padding: ${({ size }) => tokens.componentSpacing.button.padding[size]};
  border-radius: ${tokens.borderRadius.lg};
  font-size: ${tokens.fontSizes.base};
  font-weight: ${tokens.fontWeights.medium};
  transition: all ${tokens.transitionDurations[200]} ${tokens.transitionTimingFunctions['in-out']};
`;
```

#### 2.2 Responsive Design
```typescript
const responsiveStyles = {
  base: {
    fontSize: tokens.fontSizes.sm,
    padding: tokens.spacing[2],
  },
  md: {
    fontSize: tokens.fontSizes.base,
    padding: tokens.spacing[4],
  },
  lg: {
    fontSize: tokens.fontSizes.lg,
    padding: tokens.spacing[6],
  },
};
```

### 3. Accessibility Considerations

#### 3.1 Color Contrast
```typescript
const accessibleColors = {
  // Ensure sufficient contrast ratios
  text: {
    primary: tokens.colors.gray[900],    // 4.5:1 on white
    secondary: tokens.colors.gray[600],  // 4.5:1 on white
    disabled: tokens.colors.gray[400],   // 3:1 on white
  },
  background: {
    primary: tokens.colors.white,
    secondary: tokens.colors.gray[50],
    disabled: tokens.colors.gray[100],
  },
};
```

#### 3.2 Focus States
```typescript
const focusStyles = {
  outline: `2px solid ${tokens.colors.primary[500]}`,
  outlineOffset: '2px',
  borderRadius: tokens.borderRadius.base,
};
```

## Token Management

### 1. Token Generation

#### 1.1 Design Token Tools
- **Style Dictionary**: Cross-platform token generation
- **Theo**: Design token transformation
- **Figma Tokens**: Figma plugin for token management
- **Design Tokens W3C**: Standard format for design tokens

#### 1.2 Token Validation
```typescript
// Validate token values
const validateTokens = (tokens: any) => {
  // Check color contrast ratios
  // Validate spacing consistency
  // Ensure typography hierarchy
  // Verify animation performance
};
```

### 2. Token Distribution

#### 2.1 Multi-platform Support
```typescript
// Web (CSS/JS)
const webTokens = generateWebTokens(designTokens);

// React Native
const nativeTokens = generateNativeTokens(designTokens);

// iOS
const iosTokens = generateIOSTokens(designTokens);

// Android
const androidTokens = generateAndroidTokens(designTokens);
```

#### 2.2 Version Control
```typescript
// Token versioning
const tokenVersion = '1.0.0';
const tokenChangelog = {
  '1.0.0': 'Initial token release',
  '1.1.0': 'Added dark mode tokens',
  '1.2.0': 'Updated color palette',
};
```

---

## Appendix

### A. Token Files
- `tokens/colors.ts` - Color token definitions
- `tokens/typography.ts` - Typography token definitions
- `tokens/spacing.ts` - Spacing token definitions
- `tokens/shadows.ts` - Shadow token definitions
- `tokens/animations.ts` - Animation token definitions

### B. Design System Integration
- **Figma**: Design system in Figma
- **Storybook**: Component documentation
- **Style Guide**: Visual style guide
- **Component Library**: Reusable component library

### C. Tools and Resources
- **Design Token Tools**: Style Dictionary, Theo, Figma Tokens
- **Color Tools**: Contrast checkers, color palette generators
- **Typography Tools**: Font pairing tools, readability checkers
- **Accessibility Tools**: WCAG compliance checkers, screen readers
