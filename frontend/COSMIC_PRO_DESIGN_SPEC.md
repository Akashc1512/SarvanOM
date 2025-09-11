# SarvanOM Cosmic Pro - High-Fidelity Design Specifications

## Design System Overview

### Color Palette

#### Dark Mode (Primary)
- **Background Primary**: `#0b1020` (Deep space blue)
- **Background Secondary**: `#1a2332` (Card surfaces)
- **Background Tertiary**: `#2a3441` (Elevated surfaces)
- **Text Primary**: `#f8fafc` (High contrast white)
- **Text Secondary**: `#e2e8f0` (Medium contrast)
- **Text Tertiary**: `#94a3b8` (Low contrast)
- **Primary Accent**: `#60a5fa` (Bright blue)
- **Secondary Accent**: `#c084fc` (Purple)
- **Success**: `#34d399` (Green)
- **Warning**: `#fbbf24` (Amber)
- **Error**: `#f87171` (Red)

#### Light Mode
- **Background Primary**: `#ffffff` (Pure white)
- **Background Secondary**: `#f8fafc` (Light gray)
- **Background Tertiary**: `#f1f5f9` (Elevated surfaces)
- **Text Primary**: `#0f172a` (Dark slate)
- **Text Secondary**: `#334155` (Medium contrast)
- **Text Tertiary**: `#64748b` (Low contrast)
- **Primary Accent**: `#3b82f6` (Blue)
- **Secondary Accent**: `#a855f7` (Purple)
- **Success**: `#10b981` (Green)
- **Warning**: `#f59e0b` (Amber)
- **Error**: `#ef4444` (Red)

### Typography
- **Font Family**: Inter (primary), Plus Jakarta Sans (headings)
- **Font Sizes**: 12px, 14px, 16px, 18px, 20px, 24px, 30px, 36px, 48px, 60px, 72px
- **Line Heights**: 1.25 (tight), 1.375 (snug), 1.5 (normal), 1.625 (relaxed)
- **Font Weights**: 400 (normal), 500 (medium), 600 (semibold), 700 (bold)

### Spacing Scale
- **Base Unit**: 8px
- **Scale**: 4px, 8px, 12px, 16px, 20px, 24px, 32px, 40px, 48px, 64px, 80px, 96px

### Border Radius
- **Small**: 6px
- **Medium**: 8px
- **Large**: 12px
- **Extra Large**: 16px
- **Pill**: 999px

### Shadows & Glows
- **Soft Glow**: `0 0 20px rgba(96, 165, 250, 0.3)`
- **Primary Glow**: `0 0 30px rgba(96, 165, 250, 0.4)`
- **Card Shadow**: `0 4px 6px -1px rgba(0, 0, 0, 0.1)`
- **Elevated Shadow**: `0 10px 15px -3px rgba(0, 0, 0, 0.1)`

---

## Page Specifications (1440×900 Canvas)

### 1. Landing Page

#### Layout Structure
- **Header**: 80px height, full width
- **Hero Section**: 400px height, centered content
- **KPI Row**: 120px height, 3 columns
- **Features Grid**: 300px height, 3 columns
- **Footer**: 100px height

#### Hero Section (Center)
- **Left Content** (50% width):
  - Title: "Unlock Universal Knowledge" (48px, bold, primary text)
  - Subtitle: "AI-powered search across all your data sources" (20px, secondary text)
  - CTA Buttons: Primary "Get Started" (16px, 48px height), Secondary "Try Demo"
- **Right Content** (50% width):
  - Mock Dashboard Tile: 300×200px card with:
    - KPI metrics (3×2 grid)
    - Mini charts
    - Status indicators

#### KPI Row (Below Hero)
- **3 Cards** (equal width):
  - Card 1: "Operations/sec" - 1,247 (large number, success color)
  - Card 2: "Avg Latency" - 1.2s (large number, primary color)
  - Card 3: "Cost/Query" - $0.003 (large number, secondary color)

### 2. Search Page

#### Layout Structure
- **Topbar**: 60px height, compact navigation
- **Search Bar**: 80px height, centered, max-width 800px
- **Results Area**: Remaining space, 2-column layout

#### Search Interface
- **Search Bar**:
  - Input field: 60px height, rounded corners (12px)
  - Placeholder: "Ask anything about knowledge, research, or insights..."
  - Submit button: Right side, primary color
  - Mode pills: Below search bar (All, Web, Vector, KG, Comprehensive)

#### Results Layout
- **Left Column** (70% width):
  - Answer card with streaming animation
  - Citations inline with [1], [2] markers
  - Progress indicators for lanes
- **Right Column** (30% width):
  - Sources panel with filters
  - Live health states
  - Citation details

### 3. Comprehensive Query Page

#### Layout Structure
- **Header**: 100px height with breadcrumbs
- **Composer**: 200px height, full width
- **Main Content**: 2-column layout

#### Research Composer (Top)
- **Objective Field**: Textarea, 60px height
- **Constraints Field**: Textarea, 60px height
- **Output Format**: Dropdown selector
- **Submit Button**: Primary, right-aligned

#### Evidence Panel (Left, 60% width)
- **Claims Table**:
  - Row height: 60px
  - Columns: Claim, Confidence, Disagreement, Actions
  - Confidence chips: Green (high), Yellow (medium), Red (low)
  - Disagreement indicators: Red warning icons

#### Bibliography (Bottom)
- **Export Buttons**: MD, Docx, PDF formats
- **Source List**: Numbered references with metadata

### 4. Analytics Page

#### Layout Structure
- **Header**: 120px height with time range selector
- **KPI Grid**: 3×2 grid, 200px height
- **Charts Section**: 2×2 grid, 400px height

#### KPI Header Row
- **6 Metric Cards**:
  - Total Searches: 12,847 (+23.5%)
  - AI Responses: 8,923 (+18.2%)
  - Active Users: 2,341 (-5.3%)
  - Avg Response Time: 1.2s (-12.8%)
  - Citations Generated: 45,678 (+31.7%)
  - API Calls: 156,789 (+8.9%)

#### Charts Grid
- **Top Left**: Provider Breakdown (Area chart)
- **Top Right**: Lane Usage (Stacked bars)
- **Bottom Left**: Timeouts vs Errors (Donut chart)
- **Bottom Right**: Incidents List (Table with severity)

### 5. Knowledge Graph Page

#### Layout Structure
- **3-Pane Layout**: Controls (300px), Canvas (flex), Details (300px)

#### Left Panel - Controls
- **Search Query**: Input field, 40px height
- **Filters**: Checkboxes for node types
- **Settings**: Max nodes, max edges sliders
- **Example Queries**: 4 button cards

#### Center Panel - Graph Canvas
- **Interactive Graph**:
  - Nodes: Circles with labels, different colors by type
  - Edges: Curved lines with relationship labels
  - Zoom/Pan controls in corner
  - Legend overlay

#### Right Panel - Details
- **Node Information**:
  - Title, description, metadata
  - Related entities list
  - Source references
  - Action buttons

### 6. Multimodal Upload Page

#### Layout Structure
- **Header**: 100px height with title
- **Features Grid**: 3 columns, 200px height
- **Upload Section**: 300px height
- **Query Section**: 200px height

#### Upload Section
- **Dropzone Card**:
  - 400×200px area
  - Drag & drop interface
  - File type icons
  - Progress indicators

#### File Queue (Right side)
- **Queue List**:
  - File name, type, size
  - Progress bars
  - Status indicators
  - Ingest toggles (Meili/Qdrant/KG)

### 7. Admin Page

#### Layout Structure
- **Header**: 80px height with page title
- **Feature Flags Grid**: 2×3 grid, 200px height
- **Health Tiles**: 3×2 grid, 150px height
- **Danger Zone**: Bottom section, 200px height

#### Feature Flags
- **Toggle Cards**:
  - Feature name and description
  - Toggle switch (on/off)
  - Last modified timestamp
  - Audit trail

#### Health Tiles
- **Service Status**:
  - Database: Green (healthy)
  - Redis: Yellow (degraded)
  - Vector DB: Green (healthy)
  - LLM Gateway: Green (healthy)
  - Search Engine: Red (down)
  - Cache: Green (healthy)

### 8. Blog Page

#### Layout Structure
- **Header**: 100px height with search and filters
- **Posts Grid**: 2×3 grid, 300px height per card
- **Pagination**: Bottom center

#### Post Cards
- **Card Layout**:
  - Featured image: 200×120px
  - Title: 18px, bold
  - Excerpt: 14px, 3 lines
  - Metadata: Author, date, read time
  - Tags: Small chips
  - Like/Comment counts

### 9. Auth Pages (Login/Register)

#### Layout Structure
- **Centered Card**: 400×500px, centered on page
- **Background**: Starfield pattern
- **Form Fields**: Stacked vertically

#### Login Form
- **Email Field**: 48px height, rounded corners
- **Password Field**: 48px height, with visibility toggle
- **Submit Button**: 48px height, primary color
- **Links**: "Forgot password?", "Create account"

#### Register Form
- **Additional Fields**: Name, confirm password
- **Terms Checkbox**: Small text with link
- **Submit Button**: Same styling as login

### 10. 404 Page

#### Layout Structure
- **Centered Content**: 600×400px area
- **Background**: Subtle starfield
- **Content**: Centered, vertical stack

#### 404 Content
- **Large "404"**: 120px, bold, primary color
- **Error Message**: "Page not found" (24px)
- **Description**: "The page you're looking for doesn't exist" (16px)
- **Home Button**: Primary button, 48px height
- **Uptime Badge**: Small indicator in corner

---

## Component Specifications

### Cards
- **Padding**: 24px all sides
- **Border Radius**: 12px
- **Shadow**: Soft drop shadow
- **Background**: Secondary background color
- **Hover**: Subtle glow effect

### Buttons
- **Primary**: Background primary color, white text, 48px height
- **Secondary**: Border primary color, primary text, 48px height
- **Ghost**: Transparent, primary text, 48px height
- **Small**: 32px height, 12px padding
- **Large**: 56px height, 20px padding

### Input Fields
- **Height**: 48px
- **Padding**: 16px horizontal, 12px vertical
- **Border**: 1px solid border color
- **Border Radius**: 8px
- **Focus**: Primary color border, glow effect

### Navigation
- **Height**: 60px
- **Background**: Glass morphism effect
- **Items**: 16px spacing, hover effects
- **Active State**: Primary color underline

---

## Animation Specifications

### Transitions
- **Duration**: 200ms (standard), 300ms (complex)
- **Easing**: ease-in-out
- **Hover Effects**: Scale 1.02, glow increase
- **Page Transitions**: Fade in/out, 300ms

### Loading States
- **Skeleton**: Animated shimmer effect
- **Spinners**: Rotating border, 2s duration
- **Progress Bars**: Smooth fill animation
- **Streaming**: Typewriter effect, 50ms per character

---

## Responsive Breakpoints

- **Mobile**: 320px - 768px
- **Tablet**: 768px - 1024px
- **Desktop**: 1024px - 1440px
- **Large Desktop**: 1440px+

---

## Export Specifications

- **Canvas Size**: 1440×900px
- **Format**: PNG
- **Resolution**: 72 DPI (web)
- **Color Space**: sRGB
- **Background**: Transparent (for overlays) or solid color

---

This specification provides all the details needed to create high-fidelity mockups that match the actual Cosmic Pro implementation. Each page follows the established design system with consistent spacing, typography, and color usage.
