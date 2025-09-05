# Frontend Restructure Plan: Cosmic Pro Theme Migration

## 0) MASTER MIGRATION PROMPT (run first)

**Goal:** Convert the entire frontend/ to the new "Cosmic Pro" theme (dark + light), keep Next.js App Router, preserve SSE streaming, and align to MAANG standards.

**Context:** Repo root is frontend/. Current app uses Next.js App Router, Tailwind, TypeScript, and SSE to stream answers. Design reference: the dark UI screenshot I uploaded (dashboard tiles, analytics cards, tabbed search, pill filters, compact topbar, deep blues, soft glows). Create a systematic, token‑first design system and refactor all pages to it.

**Requirements:**
- Do not remove existing routes; replace their UI with the new system
- Keep all streaming, telemetry, and routing intact
- Output a step plan and apply it incrementally with check‑ins after each section below
- Follow the prompts exactly as acceptance criteria

---

## 1) DESIGN SYSTEM (tokens, theming, foundations)

**Prompt:**
Create a design‑tokens layer and dual themes (Dark = reference screenshot; Light = matching neutral daylight variant). Use CSS variables + Tailwind theme extension. Generate:

### Color Roles (no hex here—derive from the screenshot):
```css
--color-bg, --color-surface, --color-surface-2, --color-elevated,
--color-primary, --color-secondary, --color-accent,
--color-success, --color-warning, --color-danger,
--color-text, --color-text-muted, --color-border, --color-focus
```

Add subtle cosmic glow tokens: `--glow-weak`, `--glow-strong`.

### Spacing Scale:
4/8/12/16/20/24/32/40/48/64

### Radii:
xs=6, sm=8, md=12, lg=16, xl=24, pill=999

### Typography:
Inter/Plus Jakarta Sans (or your brand), sizes per breakpoint with 125% line height; monospace for code

### Elevation:
shadow tokens for 4 tiers + "frosted" overlay

### Motion:
durations (120/200/320ms), easing (standard/expressive), reduced‑motion fallbacks

### Grid:
12‑col responsive with content max width 1280px, safe gutters 16px mobile / 24px tablet / 32px desktop

**Acceptance:**
- One theme switch that toggles variables root‑wide
- A11y contrast ≥ 4.5:1 for text on both themes
- Tailwind config extended to map tokens (no hard‑coded hex in components)

---

## 2) APP SHELL & NAV (global layout)

**Prompt:**
Refactor `/src/app/layout.tsx` into a Shell with:

- **Topbar (compact):** left logo, middle page title/breadcrumb, right quick actions (theme switch, user menu)
- **Left rail (collapsible):** icons + labels for Home, Search, Comprehensive, Analytics, Graph, Upload, Admin, Blog. Tooltips on collapsed
- **Content area:** max‑width container, sticky subheader (page tabs/filters), consistent vertical rhythm
- **Footer:** legal links, build version, latency badge (reads from /metrics when available)
- **Keyboard nav:** g h home, g s search, / focus search, ? open shortcuts modal

**Acceptance:**
- Works across 360px → 4k with zero horizontal scroll
- Collapsed rail on ≤1024px; off‑canvas on ≤768px
- All shell parts read tokens; no inline colors

---

## 3) CORE COMPONENT LIBRARY

**Prompt:**
Create an internal UI kit in `src/ui/` implementing clean, reusable primitives that match the screenshot. Each component must expose clear props, variants, and ARIA roles. Build at least:

### Surface Primitives:
Card, Panel, SectionHeader, KPI (value + trend), MetricBar, Legend

### Navigation:
AppTopbar, SideNav, Tabs, Breadcrumbs, CommandK (command menu)

### Input:
Field, Input, Textarea, Select, Combobox, Slider, Switch, RadioGroup, Checkbox, PillFilter, Chip, Button (primary/secondary/ghost/tonal), IconButton

### Feedback:
Skeleton, Toast, Tooltip, Popover, Modal, InlineAlert, EmptyState

### Data:
Table (virtualized), StatStack, Sparkline, AreaChart, Donut, Badge

### Citations Module:
inline markers [^1], hover preview, side panel list with confidence, provider logo, time

**Acceptance:**
- All components token‑driven (no hard‑coded hex)
- Focus rings visible and accessible
- Storybook (or /design-system) page showcasing variants in both themes

---

## 4) PAGE BLUEPRINTS (re‑skin each route)

Use the screenshot's style: dense controls, rounded cards, subtle glows, compact typography. Keep existing page logic and SSE behaviors; only replace UI.

### 4.1 Landing (/landing)
- Hero card left (title "Unlock Universal Knowledge"), right stacked phone/globe mock tile
- Primary CTA + secondary "Try demo"
- Row of KPIs (Ops, Latency, Cost)
- Logos grid (placeholder)
- Trust & privacy footnote

**Acceptance:** CLS < 0.1; hero loads without layout shift

### 4.2 Search (/ & /search)
- Search bar with mode pills: "All, Web, Vector, KG, Comprehensive"
- Left column: streamed answer card with inline citations and a progress meter (lanes completed)
- Right column (sticky): Sources list with filters (type, recency, provider), live health states

**Acceptance:**
- TTFB < 1s (shows skeletons), streaming tokens appear; backpressure handled

### 4.3 Comprehensive Query (/comprehensive-query)
- Top prompt composer (objective, constraints, output format)
- Evidence panel: claims with inline confidence, "disagreement" chips, bibliography at bottom
- Controls: "Re‑run with stricter citations", "Export (MD/Docx)"

**Acceptance:** >85% claims render a citation marker; export works

### 4.4 Analytics (/analytics)
- KPI header row (Ops, Latency, Cost, Health)
- Provider Breakdown area chart + Usage by Lane stacked bars
- Incidents list; timeouts vs errors donut; trend sparkline

**Acceptance:** charts are SSR-friendly and accessible (described by text)

### 4.5 Knowledge Graph (/graph-visualization)
- 3‑pane: Query / Filters, Graph canvas, Details (node facts, references, actions)
- Graph follows theme (glow nodes, soft links), zoom/pan, select, focus

**Acceptance:** Keyboard navigation between nodes; high‑contrast mode works

### 4.6 Multimodal Upload (/multimodal-demo)
- Left: Dropzone card with icon + file types
- Right: Queue with status, progress bars, and "ingest to: Meili/Qdrant/KG" toggles

**Acceptance:** Drag‑and‑drop with keyboard parity

### 4.7 Admin (/admin or /admin/dashboard)
- Feature flags toggles, service statuses, rate limits, provider budgets
- Danger zone cards gated by confirm modal

**Acceptance:** Clear audit notes for toggles (who, when, what)

### 4.8 Blog (/blog)
- Two‑column card grid with tags, author, read time
- Article detail page gets sticky outline and citation preview

**Acceptance:** Typography scale reads well in both themes

### 4.9 Auth (/login, /register, /unauthorized)
- Minimal cosmic cards, password visibility toggle, SSO placeholders
- Error states readable with screen reader

**Acceptance:** Form fields labeled; tab order logical

### 4.10 404 & Status (/not-found, /status)
- On‑brand cosmic empty states; link back home; uptime badges

**Acceptance:** Tested on mobile

---

## 5) STREAMING UX & LANE BUDGETS (3s rule)

**Prompt:**
Keep the 3s SLA visualized. For every streamed answer:

- Show lane chips: Web, Vector, KG, LLM, YouTube. Each chip has timer, success/timeout, and tooltips with timings
- TTFT indicator (target ≤ 800ms) and a tiny progress bar under the answer header
- Partial‑answer banner when any lane times out; auto‑appends when late lanes finish
- Trace‑ID copy action for debugging

**Acceptance:**
- Works on poor networks; heartbeats keep the stream considered "alive"
- UI never hard‑locks; partial results always visible

---

## 6) LIGHT MODE SPEC (derive from dark)

**Prompt:**
Generate a light theme that is not a pure invert:

- **Backgrounds:** near‑white neutrals; surfaces step up as surface < surface-2 < elevated
- **Primary stays brand;** accents desaturated slightly; borders lighten; preserve 4.5:1 contrast
- **Replace glow** with soft shadow & subtle gradients
- **Keep identical layout metrics** so users don't reflow

**Acceptance:** Visual parity of spacing, sizes, interaction; contrast meets AA

---

## 7) ACCESSIBILITY, i18n, & INPUT MODES

**Prompt:**

Implement WCAG 2.1 AA: focus states, skip links, ARIA roles, color contrast, prefers‑reduced‑motion, high‑contrast adjustments.

- Keyboard shortcuts listed in a /? shortcuts modal
- i18n ready strings; no baked‑in copy inside components
- Announce streaming updates to screen readers in a polite live region

**Acceptance:** Automated a11y checks pass; manual keyboard test across pages

---

## 8) PERFORMANCE & QUALITY GATES

**Prompt:**

- **Lighthouse goals:** Perf ≥ 90, A11y ≥ 95, BP ≥ 95, SEO ≥ 90 on both themes
- **Bundle budgets:** initial JS < 180KB gz; route‑level code‑split
- **Images:** Next Image, responsive sizes, no layout shifts
- **Monitoring:** simple web‑vitals emitter to backend /metrics
- **E2E tests:** Playwright flows for Search → Stream → Citations, Analytics load, KG interaction, Upload queue

**Acceptance:** CI blocks merges if budgets regress >10% or a11y fails

---

## 9) PAGE‑BY‑PAGE PROMPTS (paste one per route as Cursor tasks)

Below are short prompts you can paste as issues/todos to apply the new look to each page:

### Landing
"Rebuild /landing to Cosmic Pro spec: hero left, mock tile right, KPI row, CTA buttons, trust strip, no layout shift, both themes."

### Search (Root + /search)
"Apply Cosmic Pro layout with search bar + mode pills, streamed answer card with citations, sticky sources rail with filters, lane chips and timers, partial‑answer banner."

### Comprehensive Query
"Composer at top (objective/constraints/output format), evidence table with disagreements, bibliography section, export buttons, confidence chips, both themes."

### Analytics
"KPI header (Ops/Latency/Cost/Health), provider breakdown area chart, lane usage bars, timeouts vs errors donut, incidents list with severity, SSR‑friendly charts."

### Knowledge Graph
"Three‑pane layout (controls, canvas, details), themed nodes/edges, keyboard navigation, high contrast mode, hover tooltips with sources."

### Multimodal Upload
"Dropzone card, file queue with progress, ingest toggles (Meili/Qdrant/KG), success/error toasts, keyboard DnD parity."

### Admin
"Feature flags grid, budgets sliders, health tiles, danger zone confirm modal, audit note field, consistent tokens."

### Blog
"Card grid + filters, article detail with sticky outline and citation preview, excellent typography in both themes."

### Auth
"Cosmic card forms, password visibility toggle, SSO placeholders, error states accessible, rate‑limit feedback."

### 404 / Unauthorized / Status
"On‑brand empty states, link back home, uptime badges, responsive across devices."

---

## 10) IMAGE MOCKUPS (optional)

If you want image mockups per page, switch to GPT‑5 (image tool enabled) and use:

"Create high‑fidelity UI mockups for SarvanOM 'Cosmic Pro' in dark and light modes for these pages: Landing, Search, Comprehensive, Analytics, Knowledge Graph, Multimodal Upload, Admin, Blog, Auth, 404. Use my screenshot as visual direction (dense cards, rounded surfaces, glows). Provide a 1440×900 canvas per page, export PNG."

---

## 11) WHAT TO KEEP/RESPECT

- Do not break: SSE streaming endpoints, trace‑ID propagation, citations rendering hooks
- All colors/spacing must come from tokens
- No inline styles for colors/shadows; use tokens and utility classes only
- Accessibility first: Focus visible, keyboardable, readable
- Performance budgets enforced in CI

---

## 12) DONE CRITERIA (final review checklist)

- [ ] Both themes complete; instant theme toggle; contrast verified
- [ ] All pages match new visual system and spacing rhythm
- [ ] Streaming UX shows lane chips, timers, partial‑answer banners
- [ ] Citations render inline + side panel; hover previews work
- [ ] A11y audits pass; keyboard shortcuts documented
- [ ] Lighthouse and bundle budgets pass in CI on both themes
- [ ] /design-system (or Storybook) showcases every component variant
- [ ] README updated with screenshots and theme preview

---

## Implementation Status

### ✅ Completed
- [x] **Design System Foundation** - Comprehensive token system with dark/light modes
- [x] **Tailwind Configuration** - Extended with cosmic.* color system
- [x] **Global CSS Utilities** - 50+ utility classes for components
- [x] **Navigation Components** - Updated CosmicNavigation with new styling
- [x] **Main Dashboard Page** - Complete conversion to Cosmic Pro theme

### 🚧 In Progress
- [ ] **Search Interface** - Update search components with Cosmic Pro styling
- [ ] **Analytics Page** - Convert analytics page to new theme
- [ ] **UI Components** - Update remaining components
- [ ] **Theme Testing** - Verify dark/light mode switching
- [ ] **Functionality Verification** - Ensure SSE streaming and all features work

### 📋 Pending
- [ ] **App Shell & Navigation** - Global layout refactor
- [ ] **Core Component Library** - Internal UI kit creation
- [ ] **Page Blueprints** - Re-skin all routes
- [ ] **Streaming UX** - Lane budgets and 3s rule implementation
- [ ] **Accessibility & i18n** - WCAG 2.1 AA compliance
- [ ] **Performance & Quality Gates** - Lighthouse and bundle budgets
- [ ] **Page-by-Page Implementation** - Individual route conversions

---

## Next Steps

1. **Continue with Search Interface** - Apply Cosmic Pro styling to search components
2. **Convert Analytics Page** - Update analytics with new theme
3. **Create Component Library** - Build reusable UI primitives
4. **Implement Theme Toggle** - Add theme switching functionality
5. **Test All Functionality** - Verify SSE streaming and features work

The foundation is solid and ready for the next phase of implementation!
