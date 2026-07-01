---
name: design-skills-2026
description: |
  Modern UI/UX Design Skills Guide for 2026.
  Battle-Tested Best Practices for Responsive Mobile-First Web Design
  Production-grade design patterns for modern responsive websites
---

## Table of Contents

1. [Design Philosophy & Principles](#design-philosophy--principles)
2. [Color Theory & Complementary Colors](#color-theory--complementary-colors)
3. [Accessibility & Inclusive Design](#accessibility--inclusive-design)
4. [Typography & Readability](#typography--readability)
5. [Button Styles & Interactive Elements](#button-styles--interactive-elements)
6. [Responsive Layout Patterns](#responsive-layout-patterns)
7. [Motion & Micro-Interactions](#motion--micro-interactions)
8. [Mobile-First Strategy](#mobile-first-strategy)
9. [Performance & Sustainability](#performance--sustainability)
10. [Component Library Reference](#component-library-reference)
11. [Onboarding & Conversion UI Patterns](#onboarding--conversion-ui-patterns)

---

## Design Philosophy & Principles

### Core Tenets of 2026 Web Design

**Human-Centered Design**
- Prioritize user intent over aesthetic novelty
- Design for real problems, not trends
- Authenticity and intentionality over algorithmic sameness
- Test with real users across abilities and contexts

**Balanced Complexity**
- Bold visuals + minimalist layouts (not opposites, complement each other)
- Visual hierarchy clarity: important content is immediately obvious
- Whitespace as a design tool, not wasted space
- Content density: 4-5 key points per section maximum

**Performance as UX**
- Sub-2-second load times are non-negotiable
- Every pixel and script must justify its weight
- Core Web Vitals directly impact user satisfaction
- Speed optimization is not an afterthought—it's a feature

**Accessibility by Default**
- Not a compliance checkbox; foundation of good UX
- High contrast, keyboard navigation, screen reader support
- WCAG 2.1 AA compliance as minimum standard (3:1 for large text, 4.5:1 for normal)
- Inclusive design improves experience for everyone (curb-cut effect)

**Mobile-First Mindset**
- 60%+ of traffic is mobile; design there first, scale up
- Touch-friendly (minimum 48px tap targets)
- Thumb-zone optimization for one-handed use
- Gesture navigation (swipe, long-press) as primary interactions

### Design System Thinking

- **Modularity**: Reusable components scale across projects
- **Consistency**: Predictable patterns reduce cognitive load
- **Scalability**: Systems adapt from small screens to large displays
- **Maintainability**: Clear naming, documentation, version control

---

## Color Theory & Complementary Colors

### Understanding the Color Wheel

**Complementary Color Pairs** (opposite on color wheel):
- **Red ↔ Cyan/Green** — High energy, strong contrast
- **Blue ↔ Orange** — Professional + warm (financial, tech, creative)
- **Yellow ↔ Purple** — High energy, playful, accessible
- **Teal ↔ Coral/Red-Orange** — Modern, sophisticated

### Strategic Use of Complementary Colors

**Contrast & Visibility**
- Use complementary pairs for CTAs (calls-to-action) to draw attention
- Primary action on blue background → orange button (or vice versa)
- Ensures visual hierarchy; secondary elements fade
- Creates focus points users' eyes naturally land on

**Visual Balance**
- Dominant color (60%): main brand color, backgrounds
- Secondary color (30%): supporting elements, accents
- Complementary accent (10%): CTAs, highlights, feedback states
- Neutral tones (grays, whites): breathing room, text

**Practical 2026 Approach**
```
Primary:     #0284C7 (Blue)
Secondary:   #64748B (Gray-Blue)
Accent:      #EA580C (Orange) — complementary to primary
Success:     #16A34A (Green)
Warning:     #D97706 (Amber)
Error:       #DC2626 (Red)
Neutral:     #F8FAFC (White) / #0F172A (Near-black)
```

### Complementary Colors for Different Contexts

**E-commerce & CTAs**
- Dark blue + orange button = irresistible click target
- Subtle but effective contrast
- Works across all accessibility profiles

**Financial & Professional**
- Teal/navy + coral accent
- Signals trust (blue) + energy (coral)
- High contrast aids readability of numbers

**Creative & Media**
- Purple + yellow
- High energy without aggression
- Strong visual interest

**SaaS & Productivity**
- Blue + teal (analogous + one complement)
- Professional, calming, focuses attention
- Secondary orange for success states

### Color Harmony Rules

**Do:**
- Use complementary pairs for high-importance actions
- Balance vibrant accents with neutral backgrounds
- Test contrast ratios (minimum 4.5:1 for text)
- Consider colorblind simulation (red-green blindness most common)

**Don't:**
- Equal parts complementary colors side-by-side (visual tension)
- Saturated complements for large background areas
- Forget about context (light vs. dark mode)
- Assume color alone communicates (patterns, icons needed too)

### Accessible Color Palettes

**For Color Vision Deficiency (CVD):**
- Avoid red + green combinations without additional cues
- Use patterns, icons, or labels in addition to color
- Test with: https://www.color-blindness.com/coblis-color-blindness-simulator/

**WCAG Compliant High Contrast Combinations:**
```
Dark text on light:
- #0F172A (near-black) on #F8FAFC (near-white) ✓ 19:1 contrast
- #1E293B (dark slate) on #FFFFFF (white) ✓ 14.5:1 contrast

Light text on dark:
- #F1F5F9 (near-white) on #0F172A (near-black) ✓ 19:1 contrast
- #E0E7FF (light) on #1E3A8A (dark blue) ✓ 9:1 contrast

For non-text elements (minimum 3:1):
- #0284C7 (blue) on #F0F9FF (light blue bg) ✓ 3.5:1 contrast
- #DC2626 (red) on #FEF2F2 (light red bg) ✓ 3.3:1 contrast
```

---

## Accessibility & Inclusive Design

### WCAG 2.1 AA Compliance (Baseline Standard)

**Perceivable: Users can see/hear content**
- Text contrast minimum 4.5:1 (AA), 7:1 (AAA)
- Images have descriptive alt text
- Color not sole means of communication (icons/labels too)
- No seizure-inducing animations (flashing <3 times/second)

**Operable: Users can navigate with keyboard**
- All interactive elements keyboard accessible (Tab, Enter, Space, Arrow keys)
- Focus indicators clearly visible (not hidden by CSS)
- No keyboard traps (users can tab back out)
- Skip-to-main-content links for power users

**Understandable: Content is clear**
- Language specified (lang="en")
- Headings create logical structure (h1 → h2 → h3, no skipping)
- Form labels explicitly associated (`<label for="id">`)
- Instructions clear, error messages specific

**Robust: Works with assistive tech**
- Valid semantic HTML (nav, main, article, aside)
- ARIA attributes where semantic HTML insufficient
- Screen reader testing (NVDA, JAWS, VoiceOver)
- No automated testing substitutes for human QA

### Inclusive Design Checklist

- [ ] High contrast: 4.5:1 for normal text, 3:1 for large/buttons
- [ ] Keyboard navigation: Tab through all interactive elements
- [ ] Focus indicators: Visible outline at all times
- [ ] Alt text: Descriptive, not redundant ("image of X" not "image")
- [ ] Form labels: `<label>` tags linked to inputs
- [ ] Headings: Logical hierarchy, h1 appears once
- [ ] Color combinations: Test with colorblind simulator
- [ ] Motion: Respect `prefers-reduced-motion` media query
- [ ] Text sizing: Allow up to 200% zoom without layout breaking
- [ ] Touch targets: Minimum 48×48px (44×44px acceptable with spacing)

### Implementation Example

```html
<!-- Good: Semantic + accessible -->
<nav aria-label="Main navigation">
  <ul>
    <li><a href="/" class="active" aria-current="page">Home</a></li>
    <li><a href="/about">About</a></li>
  </ul>
</nav>

<!-- Form with labels -->
<form>
  <label for="email">Email Address</label>
  <input id="email" type="email" required aria-describedby="email-hint">
  <span id="email-hint">We'll never share your email</span>
  
  <button type="submit">Subscribe</button>
</form>

<!-- Focus styles (don't remove!) -->
<style>
  button:focus-visible,
  input:focus-visible,
  a:focus-visible {
    outline: 3px solid #0284C7;
    outline-offset: 2px;
  }
  
  /* Respect motion preferences */
  @media (prefers-reduced-motion: reduce) {
    * {
      animation-duration: 0.01ms !important;
      transition-duration: 0.01ms !important;
    }
  }
</style>
```

---

## Typography & Readability

### Font Sizing Scale (2026 Standard)

```css
/* Typographic scale: 1.125 ratio (major second) */
--font-xs:   0.75rem   /* 12px */
--font-sm:   0.875rem  /* 14px */
--font-base: 1rem      /* 16px */
--font-lg:   1.125rem  /* 18px */
--font-xl:   1.25rem   /* 20px */
--font-2xl:  1.5rem    /* 24px */
--font-3xl:  1.875rem  /* 30px */
--font-4xl:  2.25rem   /* 36px */
--font-5xl:  3rem      /* 48px */
```

**Mobile First (breakpoint: 640px+):**
- Headings can increase 1-2 sizes on desktop
- Body text stays consistent (16px min for legibility)
- Line height: 1.5–1.6 for body, 1.2–1.3 for headings

### Font Selection & Weight

**System Font Stack (fastest, most accessible):**
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 
             Roboto, 'Helvetica Neue', Arial, sans-serif;
```

**Weight Hierarchy:**
- `400` (Normal): Body text, default state
- `500` (Medium): Labels, UI text, subtle emphasis
- `600` (Semibold): Section headings, strong emphasis
- `700` (Bold): Page titles, call-outs

**Variable Fonts (if custom fonts required):**
- Load only necessary weights (400, 600, 700)
- Use `font-display: swap` for non-blocking render
- Compress via `font-subset` (Latin only, not all Unicode)

### Line Length & Spacing

**Optimal Readability:**
- Line length: 50–75 characters (ideal: 66)
- Line height: 1.5–1.6 (body), 1.2–1.3 (headings)
- Paragraph spacing: 1–1.5× line-height below paragraph
- Letter spacing: +0.02em to +0.05em for headings (tighter = more impact)

```css
body {
  font-size: 1rem;      /* 16px */
  line-height: 1.6;     /* 25.6px */
  letter-spacing: 0;
  max-width: 65ch;      /* ~65 characters */
}

h2 {
  font-size: 1.875rem;
  line-height: 1.2;
  letter-spacing: -0.02em;  /* Tighter for larger text */
}
```

### Text Hierarchy Best Practices

1. **Single H1 per page** (main topic)
2. **H2 for sections** (max 3–4 per page)
3. **H3 for subsections** (support content)
4. **Limit hierarchy depth** (H1 → H2 → H3 typically, avoid deeper)
5. **Pair with visual cues**: Color, weight, size (not size alone)

**Anti-pattern:**
```html
<!-- ✗ Only relying on size for hierarchy -->
<span style="font-size: 2em;">Important Section</span>
<p>Content...</p>

<!-- ✓ Semantic + styled -->
<h2>Important Section</h2>
<p>Content...</p>
```

---

## Button Styles & Interactive Elements

### Button Anatomy

**Essential Properties:**
- **Padding**: 8–12px vertical, 16–24px horizontal (touch-friendly)
- **Min height**: 44–48px (comfortable tap target)
- **Border radius**: 6–8px (modern, friendly feel)
- **Font weight**: 600 (semibold, stands out from body text)
- **Cursor**: `pointer` (indicates clickability)
- **Transition**: 150–250ms (smooth state changes)

### Button Style Categories

#### 1. Primary Button (Main Action)

**Purpose:** Most important action on page (submit, "Get Started", "Buy Now")

```css
.btn-primary {
  background: #0284C7;      /* Brand blue */
  color: #FFFFFF;
  border: none;
  padding: 10px 24px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 200ms ease;
}

.btn-primary:hover {
  background: #0369A1;      /* Darker blue */
  transform: translateY(-2px);  /* Lift effect */
  box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
}

.btn-primary:active {
  background: #0D47A1;      /* Darkest */
  transform: translateY(0);  /* Back to baseline */
}

.btn-primary:focus-visible {
  outline: 3px solid #0284C7;
  outline-offset: 2px;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}
```

**Complementary Accent Example (Blue + Orange):**
```css
.btn-primary {
  background: #0284C7;      /* Blue */
  color: #FFFFFF;
  /* ... */
}

/* On dark backgrounds */
body.dark {
  --primary: #38BDF8;       /* Lighter blue for contrast */
  --accent: #EA580C;        /* Orange accent */
}
```

#### 2. Secondary Button (Alternative Action)

**Purpose:** Less prominent action ("Cancel", "Skip", "Learn More")

```css
.btn-secondary {
  background: #F1F5F9;      /* Light gray */
  color: #0F172A;           /* Near-black text */
  border: 1px solid #E2E8F0;
  padding: 10px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 200ms ease;
}

.btn-secondary:hover {
  background: #E2E8F0;      /* Slightly darker */
  border-color: #CBD5E1;
}

.btn-secondary:active {
  background: #CBD5E1;
}

/* Dark mode */
@media (prefers-color-scheme: dark) {
  .btn-secondary {
    background: #1E293B;
    color: #F1F5F9;
    border-color: #334155;
  }
  
  .btn-secondary:hover {
    background: #334155;
  }
}
```

#### 3. Tertiary Button (Ghost/Outline)

**Purpose:** Minimal importance ("View Details", "Undo", documentation links)

```css
.btn-tertiary {
  background: transparent;
  color: #0284C7;           /* Brand blue */
  border: 2px solid #0284C7;
  padding: 8px 22px;        /* Adjust for border */
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 200ms ease;
}

.btn-tertiary:hover {
  background: #F0F9FF;      /* Light blue tint */
  border-color: #0369A1;
  color: #0369A1;
}

.btn-tertiary:active {
  background: #E0F2FE;
}
```

#### 4. Danger Button (Destructive Action)

**Purpose:** Delete, remove, clear ("Delete Account", "Clear History")

```css
.btn-danger {
  background: #DC2626;      /* Red */
  color: #FFFFFF;
  border: none;
  padding: 10px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 200ms ease;
}

.btn-danger:hover {
  background: #B91C1C;      /* Darker red */
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
}

.btn-danger:active {
  background: #991B1B;
}

/* Require confirmation pattern */
.btn-danger[data-confirm="pending"] {
  background: #EA580C;      /* Orange warning */
  content: "Are you sure?";
}
```

#### 5. Success State Button

**Purpose:** Confirmation feedback

```css
.btn-primary.is-loading {
  background: #16A34A;      /* Green */
  pointer-events: none;
}

.btn-primary.is-success {
  background: #16A34A;
  animation: pulse 2s ease-out;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(22, 163, 74, 0.7);
  }
  100% {
    box-shadow: 0 0 0 10px rgba(22, 163, 74, 0);
  }
}
```

### Button Size Variants

```css
/* Small button: compact spaces, secondary actions */
.btn-sm {
  padding: 6px 12px;
  font-size: 0.875rem;
  min-height: 36px;
}

/* Default button (44–48px) */
.btn {
  padding: 10px 24px;
  font-size: 1rem;
  min-height: 44px;
}

/* Large button: primary CTAs, hero sections */
.btn-lg {
  padding: 12px 32px;
  font-size: 1.125rem;
  min-height: 56px;
}

/* Full width: mobile forms, mobile-first design */
.btn-full {
  width: 100%;
  
  @media (min-width: 640px) {
    width: auto;
  }
}
```

### Button Group & Icon Buttons

```html
<!-- Button group (e.g., tab navigation) -->
<div class="button-group" role="tablist">
  <button class="btn btn-group-item active" 
          role="tab" aria-selected="true">Option 1</button>
  <button class="btn btn-group-item" 
          role="tab" aria-selected="false">Option 2</button>
</div>

<!-- Icon button (e.g., close, menu) -->
<button class="btn-icon" aria-label="Close dialog">
  <svg width="24" height="24" viewBox="0 0 24 24" 
       fill="none" stroke="currentColor" stroke-width="2">
    <line x1="18" y1="6" x2="6" y2="18"></line>
    <line x1="6" y1="6" x2="18" y2="18"></line>
  </svg>
</button>

<style>
  .btn-icon {
    background: transparent;
    border: none;
    width: 44px;
    height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    border-radius: 8px;
    transition: background 200ms ease;
  }
  
  .btn-icon:hover {
    background: #F1F5F9;
  }
</style>
```

### Button Accessibility

**Keyboard Navigation:**
- All buttons must be keyboard accessible (Tab, Enter, Space)
- Focus state always visible (blue outline, no `outline: none`)
- State clearly communicated to screen readers

```css
/* MUST NOT hide focus! */
button:focus-visible {
  outline: 3px solid #0284C7;
  outline-offset: 2px;
}

/* If button has loading state, communicate to screen readers */
<button aria-busy="true" disabled>
  <span aria-hidden="true">⏳</span>
  Loading...
</button>
```

**Active State for Toggle Buttons:**
```html
<button aria-pressed="false" data-toggle="favorite">
  ♡ Add to Favorites
</button>

<style>
  button[aria-pressed="true"] {
    background: #EC4899;
    color: white;
  }
  
  button[aria-pressed="true"]::before {
    content: "♥";
  }
</style>
```

---

## Responsive Layout Patterns

### Mobile-First Breakpoint System

```css
/* Mobile-first: design for small screens first */
/* Default: <= 640px (mobile) */

/* Small: 640px–768px (landscape phone, tablet) */
@media (min-width: 640px) {
  /* Adjust for tablet */
}

/* Medium: 768px–1024px (tablet) */
@media (min-width: 768px) {
  /* Adjust for larger tablet */
}

/* Large: 1024px–1280px (desktop) */
@media (min-width: 1024px) {
  /* Adjust for desktop */
}

/* Extra large: 1280px+ (large desktop, cinema displays) */
@media (min-width: 1280px) {
  /* Full-width layouts */
}
```

### Fluid Grid System (CSS Grid)

```html
<!-- Hero: single column mobile, 2 columns desktop -->
<section class="grid-hero">
  <div class="hero-text">
    <h1>Responsive Heading</h1>
    <p>Adapts beautifully on all screens</p>
  </div>
  <div class="hero-image">
    <img src="image.webp" alt="Hero image" />
  </div>
</section>

<style>
  .grid-hero {
    display: grid;
    gap: 2rem;
    align-items: center;
  }
  
  /* Mobile: single column */
  @media (max-width: 768px) {
    .grid-hero {
      grid-template-columns: 1fr;
    }
  }
  
  /* Desktop: two equal columns */
  @media (min-width: 768px) {
    .grid-hero {
      grid-template-columns: 1fr 1fr;
    }
  }
  
  /* Large desktop: 60/40 split */
  @media (min-width: 1024px) {
    .grid-hero {
      grid-template-columns: 1.5fr 1fr;
      max-width: 1200px;
      margin: 0 auto;
    }
  }
</style>
```

### Card-Based Layouts (Battle-Tested Pattern)

```html
<section class="cards">
  <article class="card">
    <img src="image.jpg" alt="Card image" class="card-image" />
    <div class="card-body">
      <h3>Card Title</h3>
      <p>Card description with key information</p>
      <a href="#" class="btn btn-primary">Learn More</a>
    </div>
  </article>
</section>

<style>
  .cards {
    display: grid;
    gap: 1.5rem;
    padding: 1rem;
  }
  
  /* Mobile: 1 column */
  @media (max-width: 640px) {
    .cards {
      grid-template-columns: 1fr;
    }
  }
  
  /* Tablet: 2 columns */
  @media (min-width: 640px) {
    .cards {
      grid-template-columns: repeat(2, 1fr);
    }
  }
  
  /* Desktop: 3 columns */
  @media (min-width: 1024px) {
    .cards {
      grid-template-columns: repeat(3, 1fr);
      max-width: 1200px;
      margin: 0 auto;
    }
  }
  
  .card {
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: transform 200ms ease, box-shadow 200ms ease;
  }
  
  .card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  }
  
  .card-image {
    width: 100%;
    height: 200px;
    object-fit: cover;
  }
  
  .card-body {
    padding: 1.5rem;
  }
</style>
```

### Bento Grid (2026 Trend)

```html
<!-- Asymmetric, modular layout -->
<section class="bento-grid">
  <div class="bento-item bento-lg">
    <h2>Featured</h2>
  </div>
  <div class="bento-item">Item 2</div>
  <div class="bento-item">Item 3</div>
  <div class="bento-item bento-lg">Item 4</div>
</section>

<style>
  .bento-grid {
    display: grid;
    gap: 1.5rem;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
  
  .bento-lg {
    grid-column: span 2;
    grid-row: span 2;
  }
  
  /* Tablet: 2-column base */
  @media (min-width: 768px) {
    .bento-grid {
      grid-template-columns: repeat(4, 1fr);
      grid-template-rows: repeat(3, auto);
    }
    
    .bento-lg {
      grid-column: span 2;
      grid-row: span 2;
    }
  }
</style>
```

### Sidebar + Main Content Layout

```html
<div class="layout-sidebar">
  <aside class="sidebar">
    <nav>Navigation</nav>
  </aside>
  <main class="content">
    <article>Main content</article>
  </main>
</div>

<style>
  .layout-sidebar {
    display: grid;
    gap: 2rem;
  }
  
  /* Mobile: stacked */
  @media (max-width: 1024px) {
    .layout-sidebar {
      grid-template-columns: 1fr;
    }
    
    .sidebar {
      order: 2;  /* Content first on mobile */
    }
  }
  
  /* Desktop: sidebar on left */
  @media (min-width: 1024px) {
    .layout-sidebar {
      grid-template-columns: 280px 1fr;
    }
    
    .sidebar {
      position: sticky;
      top: 100px;
      max-height: calc(100vh - 120px);
      overflow-y: auto;
    }
  }
</style>
```

### Container Query Pattern (Modern)

```html
<section class="card-container">
  <div class="card">
    <!-- Content adapts based on container width, not viewport -->
  </div>
</section>

<style>
  .card-container {
    container-type: inline-size;
  }
  
  .card {
    padding: 1rem;
  }
  
  /* Adapt when container < 300px wide */
  @container (max-width: 300px) {
    .card {
      padding: 0.5rem;
    }
    
    .card h2 {
      font-size: 1rem;
    }
  }
  
  /* Adapt when container > 500px wide */
  @container (min-width: 500px) {
    .card {
      display: grid;
      grid-template-columns: 150px 1fr;
      gap: 1rem;
    }
  }
</style>
```

---

## Motion & Micro-Interactions

### When to Use Motion (2026 Best Practice)

**Use motion for:**
- ✓ Providing feedback (button press, form error, success)
- ✓ Guiding attention (entrance animations, focus states)
- ✓ Communicating status (loading spinners, progress bars)
- ✓ Delighting users (subtle hover effects, micro-animations)

**Avoid motion for:**
- ✗ Distraction (auto-playing videos, blinking ads)
- ✗ Accessibility issues (flashing > 3 times/sec causes seizures)
- ✗ Performance issues (janky animations frustrate users)
- ✗ Users with `prefers-reduced-motion` setting

### Micro-Interaction Examples

```css
/* Button feedback on click */
.btn {
  transition: all 200ms ease;
  position: relative;
}

.btn:active {
  transform: scale(0.98);
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Smooth hover effect */
.card {
  transition: transform 300ms ease, box-shadow 300ms ease;
}

.card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

/* Loading state animation */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.spinner {
  animation: spin 1s linear infinite;
}

/* Fade in on page load */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in {
  animation: fadeIn 500ms ease-out;
}

/* Pulse effect for CTAs */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.cta:not(:disabled) {
  animation: pulse 3s ease-in-out infinite;
}
```

### Respecting User Preferences

```css
/* Disable animations for users who prefer reduced motion */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}

/* Or create minimal animation alternative */
@media (prefers-reduced-motion: reduce) {
  .card:hover {
    /* No transform, just opacity/color change */
    background-color: #F0F9FF;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
}

@media (prefers-reduced-motion: no-preference) {
  .card:hover {
    /* Full animation for users comfortable with motion */
    transform: translateY(-8px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
  }
}
```

---

## Mobile-First Strategy

### Design Priority on Mobile

**Constraints Drive Better Design:**
- Limited screen real estate → Cut to essential content
- Touch UI → Larger tap targets (48px minimum)
- Mobile performance → Lightweight assets, critical CSS
- Network considerations → Lazy loading, efficient images

### Touch-Friendly UI Elements

**Spacing & Sizing:**
```css
/* Minimum 44×44px tap targets (Apple), 48×48px preferred (Google) */
button, a, input[type="checkbox"], input[type="radio"] {
  min-width: 44px;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

/* Spacing between touch targets: 8px minimum */
button + button {
  margin-left: 0.5rem;
}

/* Adjust for mobile */
@media (max-width: 640px) {
  button {
    min-height: 48px;
    padding: 12px 24px;
    width: 100%;  /* Full width on mobile */
  }
}
```

**Thumb-Zone Optimization:**
```
    Easy to reach (top)
    ┌─────────────────┐
    │  ◆              │
    │                 │
    │ ◆            ◆  │  Middle zone (easy)
    │                 │
    │  ◆              │
    └─────────────────┘
    Hard to reach (bottom corner)
    
Design primary CTAs in green zones, secondary in orange.
Avoid critical interactions at extreme corners.
```

### Mobile Navigation Patterns

**Pattern 1: Bottom Navigation (e-commerce, social)**
```html
<nav class="bottom-nav" aria-label="Main navigation">
  <a href="/" class="bottom-nav-item active" aria-current="page">
    <svg>...</svg>
    <span>Home</span>
  </a>
  <a href="/search" class="bottom-nav-item">
    <svg>...</svg>
    <span>Search</span>
  </a>
</nav>

<style>
  .bottom-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(60px, 1fr));
    border-top: 1px solid #E2E8F0;
    background: white;
    z-index: 1000;
  }
  
  .bottom-nav-item {
    padding: 0.75rem;
    text-align: center;
    color: #64748B;
    text-decoration: none;
    transition: color 200ms ease;
  }
  
  .bottom-nav-item.active,
  .bottom-nav-item:hover {
    color: #0284C7;
  }
  
  /* Hide on desktop */
  @media (min-width: 768px) {
    .bottom-nav {
      display: none;
    }
  }
</style>
```

**Pattern 2: Hamburger Menu (responsive, desktop-friendly)**
```html
<header>
  <button class="menu-toggle" aria-label="Toggle menu" aria-expanded="false">
    <span></span>
    <span></span>
    <span></span>
  </button>
  <nav class="menu" id="main-menu">
    <a href="/">Home</a>
    <a href="/about">About</a>
  </nav>
</header>

<style>
  .menu-toggle {
    display: flex;
    flex-direction: column;
    gap: 4px;
    background: none;
    border: none;
    cursor: pointer;
  }
  
  .menu-toggle span {
    width: 24px;
    height: 3px;
    background: #0F172A;
    transition: all 200ms ease;
  }
  
  /* Hide menu by default on mobile */
  .menu {
    display: none;
    position: absolute;
    top: 60px;
    left: 0;
    right: 0;
    background: white;
    border-bottom: 1px solid #E2E8F0;
    flex-direction: column;
  }
  
  .menu.open {
    display: flex;
  }
  
  /* Show menu on desktop */
  @media (min-width: 768px) {
    .menu-toggle {
      display: none;
    }
    
    .menu {
      display: flex;
      flex-direction: row;
      position: static;
      background: none;
      border: none;
      gap: 2rem;
    }
  }
</style>
```

### Form Design for Mobile

```html
<!-- Mobile-optimized form -->
<form>
  <div class="form-group">
    <label for="name">Full Name *</label>
    <input 
      id="name" 
      type="text" 
      required 
      autocomplete="name"
      aria-describedby="name-hint"
      inputmode="text"
    />
    <span id="name-hint" class="hint">First and last name</span>
  </div>
  
  <div class="form-group">
    <label for="email">Email *</label>
    <input 
      id="email" 
      type="email" 
      required 
      autocomplete="email"
      inputmode="email"
    />
  </div>
  
  <button type="submit" class="btn btn-primary btn-lg btn-full">
    Submit
  </button>
</form>

<style>
  .form-group {
    margin-bottom: 1.5rem;
    display: flex;
    flex-direction: column;
  }
  
  label {
    font-weight: 600;
    margin-bottom: 0.5rem;
    font-size: 0.875rem;
  }
  
  input, textarea, select {
    padding: 12px;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    font-size: 16px;  /* Prevents auto-zoom on iOS */
    font-family: inherit;
    transition: border-color 200ms ease;
  }
  
  input:focus,
  textarea:focus,
  select:focus {
    outline: none;
    border-color: #0284C7;
    box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.1);
  }
  
  .hint {
    font-size: 0.75rem;
    color: #64748B;
    margin-top: 0.25rem;
  }
  
  /* Full width button on mobile */
  .btn-full {
    width: 100%;
    margin-top: 1rem;
  }
  
  @media (min-width: 640px) {
    .btn-full {
      width: auto;
    }
  }
</style>
```

---

## Performance & Sustainability

### Core Web Vitals (2026 Must-Haves)

**Largest Contentful Paint (LCP) < 2.5s**
- Cache critical resources (CSS, fonts)
- Lazy load images (loading="lazy")
- Use next-gen formats (WebP, AVIF)
- Minimize JavaScript

**Interaction to Next Paint (INP) < 200ms**
- Break long JavaScript tasks into chunks
- Debounce/throttle event handlers
- Use `requestAnimationFrame` for visual updates
- Minimize DOM operations

**Cumulative Layout Shift (CLS) < 0.1**
- Set image/video dimensions upfront
- Avoid injecting content above fold
- Use CSS `contain` for layout boundaries
- Preload web fonts to prevent FOUT (Flash of Unstyled Text)

### Image Optimization

```html
<!-- Modern image delivery -->
<picture>
  <!-- AVIF: 30% smaller than WebP -->
  <source srcset="image.avif" type="image/avif" />
  
  <!-- WebP: 25% smaller than JPEG -->
  <source srcset="image.webp" type="image/webp" />
  
  <!-- Fallback -->
  <img 
    src="image.jpg" 
    alt="Descriptive alt text"
    width="400"
    height="300"
    loading="lazy"
    decoding="async"
  />
</picture>

<style>
  img {
    max-width: 100%;
    height: auto;
    display: block;  /* Prevents inline spacing */
  }
</style>
```

**Image Size Breakpoints:**
```html
<!-- Responsive images for different screen sizes -->
<img 
  srcset="
    image-320w.jpg 320w,
    image-640w.jpg 640w,
    image-960w.jpg 960w,
    image-1280w.jpg 1280w
  "
  sizes="
    (max-width: 640px) 100vw,
    (max-width: 1024px) 80vw,
    1200px
  "
  src="image-960w.jpg"
  alt="Description"
/>
```

### Lazy Loading

```html
<!-- Native lazy loading -->
<img src="image.jpg" loading="lazy" alt="Description" />

<!-- Lazy load iframes (videos, maps) -->
<iframe src="https://youtube.com/embed/..." loading="lazy"></iframe>

<!-- Intersection Observer API (advanced) -->
<div class="lazy-section" data-src="heavy-content.html">
  <!-- Loaded on demand -->
</div>

<script>
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        // Load content
        observer.unobserve(entry.target);
      }
    });
  });
  
  document.querySelectorAll('.lazy-section').forEach(el => {
    observer.observe(el);
  });
</script>
```

### Sustainable Web Design

**Principles:**
- Minimize data transfer (lighter pages = lower energy consumption)
- Use system fonts (no external font requests)
- Efficient code (minify CSS/JS, tree-shake unused code)
- Dark mode option (OLED displays consume less power)

```css
/* System font stack (no external requests) */
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 
               Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* Dark mode: lower brightness = less energy on OLED */
@media (prefers-color-scheme: dark) {
  body {
    background: #0F172A;  /* Near-black, not pure black for OLED */
    color: #F1F5F9;
  }
}

/* Efficient animations (GPU-accelerated) */
.element {
  animation: slide 300ms ease;
}

@keyframes slide {
  from {
    transform: translateX(-100%);  /* GPU-accelerated */
  }
  to {
    transform: translateX(0);
  }
}

/* Don't animate these (triggers repaints) */
/* Avoid: left, right, width, height, background-position */
```

---

## Component Library Reference

### Quick Copy-Paste Components

#### Alert Component

```html
<div class="alert alert-info" role="alert">
  <strong>Info:</strong> This is informational.
</div>

<div class="alert alert-success">
  <strong>Success!</strong> Operation completed.
</div>

<div class="alert alert-warning">
  <strong>Warning:</strong> Please review before proceeding.
</div>

<div class="alert alert-error" role="alert">
  <strong>Error:</strong> Something went wrong.
</div>

<style>
  .alert {
    padding: 12px 16px;
    border-radius: 8px;
    border-left: 4px solid;
    margin-bottom: 1rem;
  }
  
  .alert-info {
    background: #EFF6FF;
    border-color: #0284C7;
    color: #0C4A6E;
  }
  
  .alert-success {
    background: #F0FDF4;
    border-color: #16A34A;
    color: #15803D;
  }
  
  .alert-warning {
    background: #FFFBEB;
    border-color: #D97706;
    color: #78350F;
  }
  
  .alert-error {
    background: #FEF2F2;
    border-color: #DC2626;
    color: #7F1D1D;
  }
</style>
```

#### Badge Component

```html
<span class="badge">Default</span>
<span class="badge badge-primary">Primary</span>
<span class="badge badge-success">Success</span>
<span class="badge badge-warning">Warning</span>

<style>
  .badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    background: #E2E8F0;
    color: #1E293B;
  }
  
  .badge-primary {
    background: #DBEAFE;
    color: #1E40AF;
  }
  
  .badge-success {
    background: #DCFCE7;
    color: #166534;
  }
  
  .badge-warning {
    background: #FEF3C7;
    color: #92400E;
  }
</style>
```

#### Modal/Dialog Component

```html
<button class="btn btn-primary" onclick="openModal()">Open Modal</button>

<dialog id="my-modal" class="modal">
  <div class="modal-content">
    <div class="modal-header">
      <h2>Modal Title</h2>
      <button 
        class="btn-icon" 
        aria-label="Close modal"
        onclick="document.getElementById('my-modal').close()"
      >
        ✕
      </button>
    </div>
    
    <div class="modal-body">
      <p>Modal content goes here</p>
    </div>
    
    <div class="modal-footer">
      <button class="btn btn-secondary" onclick="document.getElementById('my-modal').close()">
        Cancel
      </button>
      <button class="btn btn-primary" onclick="document.getElementById('my-modal').close()">
        Confirm
      </button>
    </div>
  </div>
</dialog>

<script>
  function openModal() {
    document.getElementById('my-modal').showModal();
  }
</script>

<style>
  .modal {
    border: none;
    border-radius: 12px;
    box-shadow: 0 20px 25px rgba(0, 0, 0, 0.15);
    max-width: 500px;
    width: 90%;
  }
  
  .modal::backdrop {
    background: rgba(0, 0, 0, 0.5);
  }
  
  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    border-bottom: 1px solid #E2E8F0;
  }
  
  .modal-body {
    padding: 1.5rem;
  }
  
  .modal-footer {
    display: flex;
    gap: 0.75rem;
    padding: 1.5rem;
    border-top: 1px solid #E2E8F0;
    justify-content: flex-end;
  }
</style>
```

---

## Onboarding & Conversion UI Patterns

The primitives above (colors, typography, buttons, layouts, generic motion) are necessary for
any UI. Onboarding flows need an additional layer because they do a different job: not "show
information" but "carry a brand-new user through their first 60 seconds without losing them."

This is one of the highest-leverage UI surfaces in any product. Evidence from a Mobbin study
of 1,460 onboarding flows across 986 apps:

- **Mural** replaced popup tour with a persistent 6-step checklist → **+10% week-1 retention**
- **House** split a single signup form across multiple screens → **+15% conversion**
- **Headspace** allowed multi-intent goal selection → **+10% free-trial conversion**
- **Grammarly** recommends pricing plans tailored to quiz answers → **+20% plan upgrades**

The patterns that drive these results are documented as paste-ready components with the *why*
attached in **[references/onboarding-ui-patterns.md](references/onboarding-ui-patterns.md)**.
Read it whenever you're building or auditing:

- A signup or activation flow
- A checklist component for new users
- An empty state on a page a new user lands on
- A native permission ask (notifications, geolocation, camera, mic)
- A multi-step form
- A loader that runs longer than 300 ms
- A long flow (>20 screens) where pacing matters
- A field with a non-obvious concept (live validation, contextual tooltips)

### What that reference covers

| Pattern | When to use |
|---|---|
| Tooltips & microcopy as teaching devices | Domain-specific concepts; replaces frontloaded tutorials |
| Live form validation | Password rules, username availability — anything with discoverable rules |
| Multi-step form layout | Any form with >5 fields; preserves perceived progress |
| Empty-state nudges | Replace pop-up tours after onboarding completes |
| Persistent onboarding checklist | 3–7 setup tasks; survives dismissal so users return later |
| Permission-prime screen | Always before a native permission API call (with the "Maybe later" rule) |
| Loader-as-delight | Any sync operation >300 ms; turns waiting into anticipation |
| Mascots & micro-celebrations | Long flows (>20 screens) that need emotional touchpoints |

### Cross-link: conversion-/PLG-psychology lives elsewhere

This skill covers the UI **execution** of onboarding patterns — components, layout, motion,
microcopy. The strategy layer — *whether* a pattern should be used at all, the aha-moment
framework, paywall placement psychology, persuasion principles, decision matrices for "do we
even need onboarding?" — is deliberately **not** here. It lives in the **conversion skill
(sales plugin)**.

When designing or reviewing a full flow, use both. UI without strategy ships the wrong
thing; strategy without UI fails to ship.

---

## Summary: 2026 Design Checklist

Before shipping any website, verify:

- [ ] **Mobile-first responsive design** (60%+ traffic is mobile)
- [ ] **Accessibility (WCAG 2.1 AA)**: Contrast 4.5:1+, keyboard nav, focus indicators
- [ ] **Complementary colors** for CTAs (high visibility, accessible)
- [ ] **Button patterns** implemented (primary, secondary, danger states)
- [ ] **Touch-friendly UI** (48px tap targets, proper spacing)
- [ ] **Performance** (LCP <2.5s, INP <200ms, CLS <0.1)
- [ ] **Images optimized** (WebP/AVIF, lazy-loaded, responsive sizes)
- [ ] **System fonts** (no unnecessary web font requests)
- [ ] **Motion respects** `prefers-reduced-motion`
- [ ] **Dark mode** support (improves sustainability)
- [ ] **Semantic HTML** (headings, nav, main, article, form labels)
- [ ] **Focus states visible** (never `outline: none`)
- [ ] **Color contrast tested** with colorblind simulator
- [ ] **Form inputs** have labels and autocomplete
- [ ] **No distracting animations** or auto-playing media
- [ ] **Page load time < 3s** (especially on slow networks)

For onboarding flows, additionally verify:

- [ ] **Aha-moment is reachable in <3 steps** from first signed-in screen (or no onboarding at all)
- [ ] **Forms with >5 fields are split** into multi-step layout with progress indicator
- [ ] **Live validation** on rule-bearing fields (password, email, username) — never submit-then-error
- [ ] **Permission asks are primed** with a custom screen; "Maybe later" does NOT call the native API
- [ ] **Empty states have inline nudges**, not pop-up tours
- [ ] **Long flows (>20 screens)** have loader-as-delight + value re-emphasis along the way
- [ ] **Persistent checklist** stays accessible after dismissal (server-side state, not localStorage)

---

## References & Tools

**Accessibility:**
- WCAG 2.1 Guidelines: https://www.w3.org/WAI/WCAG21/quickref/
- WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/
- Colorblind Simulator: https://www.color-blindness.com/coblis-color-blindness-simulator/

**Performance:**
- Google PageSpeed Insights: https://pagespeed.web.dev/
- WebPageTest: https://www.webpagetest.org/
- Lighthouse: Built into Chrome DevTools

**Design Systems:**
- Material Design: https://material.io/
- Tailwind CSS: https://tailwindcss.com/
- Ant Design: https://ant.design/

**Color Tools:**
- Adobe Color: https://color.adobe.com/
- Coolors: https://coolors.co/
- Contrast Grid: https://contrast-grid.elytradesign.com/

---

**Status:** Battle-tested, production-ready for 2026  
**Last Reviewed:** February 2026  
**Audience:** Developers, Designers, AI Models