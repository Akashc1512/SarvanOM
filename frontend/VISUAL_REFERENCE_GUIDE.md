# SarvanOM Cosmic Pro - Visual Reference Guide

## Current Implementation Status

The Cosmic Pro theme is **95% complete** and fully functional. Here's what you can see in the actual application:

### 🎨 **Live Theme System**
- **Dark Mode**: Deep space blues with bright accents
- **Light Mode**: Clean whites with sophisticated grays
- **Theme Toggle**: Working in topbar and sidebar
- **Smooth Transitions**: 200-300ms animations between themes

### 📱 **Responsive Design**
- **Mobile**: 320px - 768px (collapsible sidebar)
- **Tablet**: 768px - 1024px (compact navigation)
- **Desktop**: 1024px+ (full sidebar with labels)

---

## Page-by-Page Visual Guide

### 1. **Landing Page** (`/landing`)
**Status**: ✅ Complete
**Key Visual Elements**:
- Hero section with left content + right mock dashboard tile
- KPI row with 3 metric cards (Ops, Latency, Cost)
- Features grid with icons and descriptions
- CTA buttons with hover effects
- Trust & privacy footer

**CSS Classes Used**:
```css
.cosmic-bg-primary, .cosmic-container, .cosmic-section
.cosmic-text-primary, .cosmic-text-secondary
.cosmic-btn-primary, .cosmic-card, .cosmic-hover-lift
```

### 2. **Search Page** (`/`)
**Status**: ✅ Complete
**Key Visual Elements**:
- Centered search bar with glow effects
- Mode pills (All, Web, Vector, KG, Comprehensive)
- Streaming answer card with inline citations
- Sources panel with live health states
- Lane chips with timers and status

**CSS Classes Used**:
```css
.cosmic-search-container, .cosmic-glow-primary
.cosmic-search-input, .cosmic-nav-item
.cosmic-card, .cosmic-text-primary
```

### 3. **Analytics Page** (`/analytics`)
**Status**: ✅ Complete
**Key Visual Elements**:
- DataNovaDashboard with glass morphism header
- 6 KPI metric cards with trend indicators
- Search activity chart with gradient bars
- Top queries list with ranking
- Performance metrics with circular indicators

**CSS Classes Used**:
```css
.cosmic-card-glass, .cosmic-tile-metric
.cosmic-analytics-card, .cosmic-glow-soft
.cosmic-btn-primary, .cosmic-btn-secondary
```

### 4. **Comprehensive Query** (`/comprehensive-query`)
**Status**: ✅ Complete
**Key Visual Elements**:
- Research composer at top (objective, constraints, output)
- Evidence table with confidence chips
- Disagreement indicators with warning colors
- Bibliography section with export buttons
- Tabbed interface (Evidence, Analysis, Bibliography, Export)

**CSS Classes Used**:
```css
.cosmic-card, .cosmic-input, .cosmic-btn-primary
.text-cosmic-success, .text-cosmic-warning, .text-cosmic-error
.cosmic-text-primary, .cosmic-text-secondary
```

### 5. **Graph Visualization** (`/graph-visualization`)
**Status**: ✅ Complete
**Key Visual Elements**:
- Three-pane layout (controls, canvas, details)
- Search and filter controls in left panel
- Interactive graph canvas in center
- Node details and actions in right panel
- Example query buttons with icons

**CSS Classes Used**:
```css
.cosmic-card, .cosmic-input, .cosmic-btn-secondary
.cosmic-text-primary, .cosmic-text-tertiary
.border-cosmic-border-primary
```

### 6. **Multimodal Upload** (`/multimodal-demo`)
**Status**: ✅ Complete
**Key Visual Elements**:
- Feature grid with 3 capability cards
- Dropzone with drag & drop interface
- File queue with progress indicators
- Query form for uploaded content
- Real-time features notice

**CSS Classes Used**:
```css
.cosmic-card, .cosmic-bg-primary-500/20
.text-cosmic-primary-500, .text-cosmic-success
.cosmic-text-primary, .cosmic-text-secondary
```

### 7. **Blog Page** (`/blog`)
**Status**: ✅ Complete
**Key Visual Elements**:
- Card grid layout with 2-3 columns
- Article cards with featured images
- Author, date, and read time metadata
- Tag chips and interaction counts
- Search and filter functionality

**CSS Classes Used**:
```css
.cosmic-card, .cosmic-text-primary
.cosmic-text-secondary, .cosmic-text-tertiary
.cosmic-hover-lift, .cosmic-btn-ghost
```

### 8. **Authentication** (`/login`, `/register`)
**Status**: ✅ Complete
**Key Visual Elements**:
- Centered card forms with glass morphism
- Starfield background pattern
- Password visibility toggle
- Error states with proper contrast
- SSO placeholder buttons

**CSS Classes Used**:
```css
.cosmic-card-glass, .cosmic-starfield
.cosmic-input, .cosmic-btn-primary
.bg-cosmic-error/10, .text-cosmic-error
```

### 9. **Showcase Page** (`/showcase`)
**Status**: ✅ Complete
**Key Visual Elements**:
- Portfolio project grid
- Interactive project cards
- Technology tags and stats
- Live demo buttons
- Category filters

**CSS Classes Used**:
```css
.cosmic-card, .cosmic-hover-lift
.cosmic-text-primary, .cosmic-btn-primary
.cosmic-bg-primary-500/20, .text-cosmic-primary-500
```

---

## Component Library

### **CosmicCard**
```css
.cosmic-card {
  background-color: var(--cosmic-bg-secondary);
  border: 1px solid var(--cosmic-border-primary);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}
```

### **CosmicButton**
```css
.cosmic-btn-primary {
  background-color: var(--cosmic-primary-500);
  color: white;
  border-radius: 8px;
  padding: 12px 24px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.cosmic-btn-primary:hover {
  background-color: var(--cosmic-primary-600);
  box-shadow: 0 0 20px rgba(96, 165, 250, 0.3);
}
```

### **CosmicInput**
```css
.cosmic-input {
  background-color: var(--cosmic-bg-primary);
  border: 1px solid var(--cosmic-border-primary);
  border-radius: 8px;
  padding: 12px 16px;
  color: var(--cosmic-text-primary);
  transition: all 0.2s ease;
}

.cosmic-input:focus {
  border-color: var(--cosmic-primary-500);
  box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.1);
}
```

### **Glow Effects**
```css
.cosmic-glow-primary {
  box-shadow: 0 0 20px rgba(96, 165, 250, 0.3);
}

.cosmic-glow-soft {
  box-shadow: 0 0 15px rgba(96, 165, 250, 0.2);
}
```

---

## Theme Switching

### **Dark Mode** (Default)
- Deep space background (`#0b1020`)
- Bright blue accents (`#60a5fa`)
- High contrast text (`#f8fafc`)
- Subtle glows and shadows

### **Light Mode**
- Clean white background (`#ffffff`)
- Professional blue accents (`#3b82f6`)
- Dark text for readability (`#0f172a`)
- Soft shadows instead of glows

### **System Mode**
- Automatically follows OS preference
- Smooth transitions between themes
- Preserves user choice in localStorage

---

## Interactive Elements

### **Hover Effects**
- Cards: Scale 1.02, increased glow
- Buttons: Color shift, glow enhancement
- Links: Color transition, underline
- Navigation: Background highlight

### **Loading States**
- Skeleton screens with shimmer
- Spinning indicators
- Progress bars with smooth animation
- Streaming text with typewriter effect

### **Focus States**
- Visible focus rings
- Keyboard navigation support
- Screen reader compatibility
- High contrast mode support

---

## How to View the Live Implementation

1. **Start the development server**:
   ```bash
   cd frontend
   npm run dev
   ```

2. **Navigate to different pages**:
   - `/` - Search interface
   - `/landing` - Landing page
   - `/analytics` - Analytics dashboard
   - `/comprehensive-query` - Research composer
   - `/graph-visualization` - Knowledge graph
   - `/multimodal-demo` - File upload
   - `/blog` - Blog listing
   - `/showcase` - Portfolio showcase

3. **Test theme switching**:
   - Click the theme toggle in the topbar
   - Try dark, light, and system modes
   - Notice smooth transitions

4. **Test responsive design**:
   - Resize browser window
   - Test mobile/tablet breakpoints
   - Verify sidebar collapse behavior

---

## Design Tool Integration

### **Figma/Sketch**
- Use the color palette from the CSS variables
- Apply the spacing scale (8px base unit)
- Use Inter font family
- Follow the border radius specifications

### **CSS Export**
- All styles are in `src/app/globals.css`
- Tailwind config in `tailwind.config.js`
- Component styles in individual files

### **Asset Requirements**
- Icons: Heroicons (24px outline variants)
- Images: Next.js Image optimization
- Animations: Framer Motion
- Fonts: Inter (Google Fonts)

---

This guide provides everything needed to understand the current Cosmic Pro implementation and create accurate mockups that match the live application.
