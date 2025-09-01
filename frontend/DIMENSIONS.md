# Frontend Dimension Standards

This document outlines the standardized dimensions used throughout the SarvanOM frontend application, following industry best practices and MAANG/OpenAI/Perplexity standards.

## 📏 Spacing Scale

Based on an 8px base unit for consistent spacing across the application.

| Class | Value | Pixels | Usage |
|-------|-------|--------|-------|
| `space-0` | 0px | 0px | No spacing |
| `space-1` | 0.25rem | 4px | Minimal spacing |
| `space-2` | 0.5rem | 8px | Base unit spacing |
| `space-3` | 0.75rem | 12px | Small spacing |
| `space-4` | 1rem | 16px | Standard spacing |
| `space-5` | 1.25rem | 20px | Medium spacing |
| `space-6` | 1.5rem | 24px | Large spacing |
| `space-8` | 2rem | 32px | Extra large spacing |
| `space-10` | 2.5rem | 40px | Section spacing |
| `space-12` | 3rem | 48px | Component spacing |
| `space-16` | 4rem | 64px | Layout spacing |
| `space-20` | 5rem | 80px | Page spacing |
| `space-24` | 6rem | 96px | Major spacing |
| `space-32` | 8rem | 128px | Hero spacing |
| `space-40` | 10rem | 160px | Large layout |
| `space-48` | 12rem | 192px | Extra large layout |
| `space-56` | 14rem | 224px | Massive spacing |
| `space-64` | 16rem | 256px | Maximum spacing |

## 📝 Typography Scale

Consistent typography scale following the 1.25 ratio (major third).

| Class | Size | Line Height | Usage |
|-------|------|-------------|-------|
| `text-xs` | 0.75rem (12px) | 1.5 | Captions, labels |
| `text-sm` | 0.875rem (14px) | 1.5 | Small text |
| `text-base` | 1rem (16px) | 1.5 | Body text |
| `text-lg` | 1.125rem (18px) | 1.5 | Large body |
| `text-xl` | 1.25rem (20px) | 1.5 | Subheadings |
| `text-2xl` | 1.5rem (24px) | 1.25 | Headings |
| `text-3xl` | 1.875rem (30px) | 1.25 | Large headings |
| `text-4xl` | 2.25rem (36px) | 1.25 | Page titles |
| `text-5xl` | 3rem (48px) | 1.25 | Hero titles |
| `text-6xl` | 3.75rem (60px) | 1.25 | Massive titles |
| `text-7xl` | 4.5rem (72px) | 1.25 | Display titles |
| `text-8xl` | 6rem (96px) | 1.25 | Giant titles |
| `text-9xl` | 8rem (128px) | 1.25 | Maximum titles |

## 🔄 Border Radius Scale

Consistent border radius for rounded corners.

| Class | Value | Pixels | Usage |
|-------|-------|--------|-------|
| `rounded-none` | 0px | 0px | Sharp corners |
| `rounded-sm` | 0.125rem | 2px | Subtle rounding |
| `rounded-base` | 0.25rem | 4px | Standard rounding |
| `rounded-md` | 0.375rem | 6px | Medium rounding |
| `rounded-lg` | 0.5rem | 8px | Large rounding |
| `rounded-xl` | 0.75rem | 12px | Extra large rounding |
| `rounded-2xl` | 1rem | 16px | Pill-like rounding |
| `rounded-3xl` | 1.5rem | 24px | Very large rounding |
| `rounded-full` | 9999px | - | Circular |

## 🌟 Shadow Scale

Consistent shadow system for depth and elevation.

| Class | Usage | Description |
|-------|-------|-------------|
| `shadow-xs` | Subtle elevation | Minimal shadow |
| `shadow-sm` | Cards, buttons | Small shadow |
| `shadow-base` | Default elevation | Standard shadow |
| `shadow-md` | Modals, dropdowns | Medium shadow |
| `shadow-lg` | Large components | Large shadow |
| `shadow-xl` | Hero sections | Extra large shadow |
| `shadow-2xl` | Maximum elevation | Maximum shadow |
| `shadow-inner` | Pressed states | Inset shadow |

## 📱 Breakpoint System

Responsive breakpoints for different screen sizes.

| Class | Min Width | Usage |
|-------|-----------|-------|
| `xs` | 475px | Extra small devices |
| `sm` | 640px | Small devices |
| `md` | 768px | Medium devices |
| `lg` | 1024px | Large devices |
| `xl` | 1280px | Extra large devices |
| `2xl` | 1536px | 2X large devices |
| `3xl` | 1600px | 3X large devices |
| `4xl` | 1920px | 4X large devices |

## 📐 Aspect Ratios

Standardized aspect ratios for media and containers.

| Class | Ratio | Usage |
|-------|-------|-------|
| `aspect-auto` | auto | Natural ratio |
| `aspect-square` | 1:1 | Square images |
| `aspect-video` | 16:9 | Video content |
| `aspect-photo` | 4:3 | Photo content |
| `aspect-golden` | 1.618:1 | Golden ratio |
| `aspect-ultrawide` | 21:9 | Ultrawide content |
| `aspect-portrait` | 3:4 | Portrait content |
| `aspect-landscape` | 4:3 | Landscape content |

## 🎯 Z-Index Scale

Organized z-index system for layering.

| Class | Value | Usage |
|-------|-------|-------|
| `z-0` | 0 | Base layer |
| `z-10` | 10 | Low elevation |
| `z-20` | 20 | Medium elevation |
| `z-30` | 30 | High elevation |
| `z-40` | 40 | Very high elevation |
| `z-50` | 50 | Maximum elevation |
| `z-dropdown` | 1000 | Dropdown menus |
| `z-sticky` | 1020 | Sticky elements |
| `z-fixed` | 1030 | Fixed elements |
| `z-modal-backdrop` | 1040 | Modal backgrounds |
| `z-modal` | 1050 | Modal content |
| `z-popover` | 1060 | Popovers |
| `z-tooltip` | 1070 | Tooltips |
| `z-toast` | 1080 | Toast notifications |

## 🎨 Container Max Widths

Standardized container widths for content layout.

| Class | Max Width | Usage |
|-------|-----------|-------|
| `container-xs` | 20rem (320px) | Extra small content |
| `container-sm` | 24rem (384px) | Small content |
| `container-md` | 28rem (448px) | Medium content |
| `container-lg` | 32rem (512px) | Large content |
| `container-xl` | 36rem (576px) | Extra large content |
| `container-2xl` | 42rem (672px) | 2X large content |
| `container-3xl` | 48rem (768px) | 3X large content |
| `container-4xl` | 56rem (896px) | 4X large content |
| `container-5xl` | 64rem (1024px) | 5X large content |
| `container-6xl` | 72rem (1152px) | 6X large content |
| `container-7xl` | 80rem (1280px) | 7X large content |
| `container-full` | 100% | Full width |

## 🎭 Line Heights

Standardized line heights for optimal readability.

| Class | Value | Usage |
|-------|-------|-------|
| `leading-none` | 1 | Single line |
| `leading-tight` | 1.25 | Tight spacing |
| `leading-snug` | 1.375 | Snug spacing |
| `leading-normal` | 1.5 | Normal spacing |
| `leading-relaxed` | 1.625 | Relaxed spacing |
| `leading-loose` | 2 | Loose spacing |

## 🎨 Color System

The application uses a comprehensive color system with CSS custom properties.

### Primary Colors
- `--primary`: Main brand color
- `--primary-foreground`: Text on primary background

### Secondary Colors
- `--secondary`: Secondary brand color
- `--secondary-foreground`: Text on secondary background

### Semantic Colors
- `--destructive`: Error states
- `--muted`: Disabled states
- `--accent`: Accent elements

### Cosmic Theme Colors
- `--cosmos-bg`: Dark background (#0b1020)
- `--cosmos-fg`: Light foreground (#e6f0ff)
- `--cosmos-accent`: Accent color (#7aa2ff)
- `--cosmos-card`: Card background (#121a2e)

## 📋 Usage Guidelines

### 1. Spacing Consistency
- Always use the standardized spacing scale
- Prefer `space-4` (16px) for standard spacing
- Use `space-8` (32px) for section spacing
- Reserve larger spaces for major layout divisions

### 2. Typography Hierarchy
- Use `text-base` for body text
- Use `text-lg` for important body text
- Use `text-xl` and above for headings
- Maintain consistent line heights

### 3. Responsive Design
- Start with mobile-first design
- Use breakpoints consistently
- Test on all breakpoint sizes
- Ensure content is readable at all sizes

### 4. Component Spacing
- Use consistent padding and margins
- Follow the 8px grid system
- Maintain visual hierarchy through spacing
- Use negative margins sparingly

### 5. Shadow Usage
- Use shadows to indicate elevation
- Keep shadow usage consistent
- Avoid overusing shadows
- Consider accessibility in shadow choices

## 🔧 Implementation

All dimensions are defined as CSS custom properties in `globals.css` and extended in `tailwind.config.js`. This ensures:

1. **Consistency**: All components use the same scale
2. **Maintainability**: Changes can be made centrally
3. **Performance**: CSS custom properties are optimized
4. **Accessibility**: Proper contrast and sizing
5. **Responsiveness**: Scales appropriately across devices

## 📊 Best Practices

1. **Use Semantic Class Names**: Choose classes that describe their purpose
2. **Maintain Visual Hierarchy**: Use spacing to create clear information architecture
3. **Consider Accessibility**: Ensure sufficient contrast and touch targets
4. **Test Across Devices**: Verify dimensions work on all screen sizes
5. **Document Custom Values**: Any custom dimensions should be documented
6. **Follow Design System**: Stick to the established patterns
7. **Optimize for Performance**: Use efficient CSS properties
8. **Plan for Growth**: Design with scalability in mind

## 🚀 Future Considerations

- Monitor usage patterns to optimize the scale
- Consider adding more granular spacing options if needed
- Evaluate accessibility compliance regularly
- Update based on user feedback and testing
- Maintain consistency across new features
