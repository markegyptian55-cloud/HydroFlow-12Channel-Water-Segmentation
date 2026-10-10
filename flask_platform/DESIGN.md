# HydroFlow Design System & Tokens (DESIGN.md)

**Aesthetic Direction**: Calm, precise, scientific instrument. Inspired by Planet Explorer, Sentinel Hub EO Browser, Linear, and Observable.  
**Core Rule**: Content, rasters, and spatial maps are the hero. Visual chrome must remain quiet, disciplined, and functional. No decorative gradients, no glassmorphism blur, no neon glows.

---

## 1. Color System & Design Tokens

### 1.1 Color Philosophy
- **Light Theme (Default)**: Clean, high-legibility crisp paper surfaces with cool neutral grays.
- **Dark Theme (Secondary)**: Deep graphite surfaces engineered for low eye strain during prolonged GIS analysis (not inverted colors).
- **One Brand Accent**: Deep Blue-Teal (`#00667e` in light, `#0097b2` in dark) for active states and primary actions.
- **Dedicated Water Data Color**: Single cyan hue (`#0284c7` in light, `#38bdf8` in dark) used **ONLY** for water data visualization (masks, coverage bars, overlay layers). Never used on buttons, headers, or decorative borders.
- **Semantic Signals**: Muted, high-contrast tokens for Success (Green), Warning (Amber), and Error (Crimson).

### 1.2 Exact Palette Tokens

```css
:root {
  /* Surface Tokens (Light Theme Default) */
  --color-surface-bg: #f8fafc;        /* App canvas background */
  --color-surface-panel: #ffffff;     /* Workbench cards & panels */
  --color-surface-subtle: #f1f5f9;    /* Inset areas, controls background */
  --color-surface-hover: #e2e8f0;     /* Hover states */
  
  /* Text & Content Tokens */
  --color-text-primary: #0f172a;      /* High-contrast headings and body (14.2:1) */
  --color-text-secondary: #475569;    /* Labels, descriptions, secondary text (6.8:1) */
  --color-text-tertiary: #94a3b8;     /* Inactive icons, subtle placeholders */
  --color-text-inverse: #ffffff;      /* Text over solid primary buttons */

  /* Border Tokens */
  --color-border-subtle: #e2e8f0;     /* Low-contrast panel dividers (1px solid) */
  --color-border-default: #cbd5e1;    /* Input and control boundaries */
  --color-border-focus: #00667e;      /* Keyboard focus rings */

  /* Brand Accent Tokens */
  --color-accent-primary: #00667e;    /* Deep Blue-Teal primary actions */
  --color-accent-hover: #005063;      /* Primary button hover */
  --color-accent-subtle: #e0f2f7;     /* Active pill backgrounds */

  /* Water Data Tokens (RESERVED SOLELY FOR WATER DATA) */
  --color-water-data: #0284c7;        /* Water mask preview & chart fills */
  --color-water-data-alpha: rgba(2, 132, 199, 0.45); /* Map raster alpha overlay */
  --color-water-border: #0369a1;

  /* Semantic Feedback Tokens */
  --color-status-success: #15803d;    /* Verified benchmarks (WCAG AA pass) */
  --color-status-success-bg: #f0fdf4;
  --color-status-warning: #b45309;    /* Experimental OOD indicators */
  --color-status-warning-bg: #fffbeb;
  --color-status-error: #b91c1c;      /* Failures and offline states */
  --color-status-error-bg: #fef2f2;

  /* Shadows (Restrained) */
  --shadow-sm: 0 1px 2px 0 rgba(15, 23, 42, 0.05);
  --shadow-floating: 0 4px 12px -2px rgba(15, 23, 42, 0.08), 0 2px 6px -1px rgba(15, 23, 42, 0.04);
}

[data-theme="dark"] {
  /* Surface Tokens (Dark Theme) */
  --color-surface-bg: #090d16;        /* Deep graphite app canvas */
  --color-surface-panel: #111726;     /* Elevated workbench panels */
  --color-surface-subtle: #192237;    /* Inset controls and dropzones */
  --color-surface-hover: #222e49;     /* Control hover states */

  /* Text & Content Tokens */
  --color-text-primary: #f8fafc;      /* Headings & key metrics (15.1:1) */
  --color-text-secondary: #94a3b8;    /* Subtitles, units, labels (7.2:1) */
  --color-text-tertiary: #64748b;     /* Inactive elements */
  --color-text-inverse: #090d16;

  /* Border Tokens */
  --color-border-subtle: #1e293b;     /* Crisp 1px panel boundaries */
  --color-border-default: #334155;    /* Control borders */
  --color-border-focus: #38bdf8;

  /* Brand Accent Tokens */
  --color-accent-primary: #0284c7;    /* Vibrant crisp blue-teal */
  --color-accent-hover: #0369a1;
  --color-accent-subtle: rgba(2, 132, 199, 0.15);

  /* Water Data Tokens */
  --color-water-data: #38bdf8;        /* Neon-free crisp water cyan */
  --color-water-data-alpha: rgba(56, 189, 248, 0.50);
  --color-water-border: #0284c7;

  /* Semantic Feedback Tokens */
  --color-status-success: #4ade80;
  --color-status-success-bg: rgba(22, 101, 52, 0.25);
  --color-status-warning: #fbbf24;
  --color-status-warning-bg: rgba(180, 83, 9, 0.25);
  --color-status-error: #f87171;
  --color-status-error-bg: rgba(185, 28, 28, 0.25);

  /* Shadows (Dark) */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
  --shadow-floating: 0 6px 16px -2px rgba(0, 0, 0, 0.5);
}
```

---

## 2. Typography & Numerical Formatting

### 2.1 Typeface Selection
- **Body & UI**: `Inter` with fallback to `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`. High legibility at small sizes, excellent geometric rendering.
- **Data, Code, & Telemetry**: `JetBrains Mono` with fallback to `'SFMono-Regular', Consolas, monospace`. Enforces **Tabular Numbers (`font-variant-numeric: tabular-nums`)** so that metrics, percentages, and lat/lon coordinates never cause jitter or layout shifts when numbers change.

### 2.2 Six-Step Type Scale
```css
--text-xs:   0.75rem;  /* 12px - Labels, secondary tags, coordinates */
--text-sm:   0.875rem; /* 14px - Body text, control labels, descriptions */
--text-base: 1.0rem;   /* 16px - Primary inputs, table content */
--text-lg:   1.25rem;  /* 20px - Section headers, panel titles */
--text-xl:   1.75rem;  /* 28px - Primary metric readouts */
--text-2xl:  2.5rem;   /* 40px - Hero numbers (if needed) */
```

---

## 3. Spacing, Borders, & Geometry

### 3.1 4px Spatial Grid
- Base steps: `4px`, `8px`, `12px`, `16px`, `24px`, `32px`, `48px`, `64px`.
- Padding standards:
  - Button padding: `8px 14px`
  - Input padding: `8px 12px`
  - Stat tile padding: `12px 16px`
  - Panel padding: `16px 20px`

### 3.2 Corner Radii
- Controls (Buttons, Inputs, Badges, Tabs): `6px` (`--radius-sm`).
- Containers (Panels, Drawers, Modals): `10px` (`--radius-md`).
- **Strict Prohibition**: No `rounded-3xl` or `rounded-full` pills on substantive cards.

---

## 4. Motion & Transition Budget

- **Duration**: `120ms` for hover/focus feedback; `180ms` for drawer opening and tab transitions.
- **Timing Curve**: `cubic-bezier(0.16, 1, 0.3, 1)` (smooth deceleration).
- **Reduced Motion Support**:
  ```css
  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
      animation-duration: 0.01ms !important;
      transition-duration: 0.01ms !important;
    }
  }
  ```

---

## 5. UI Component Catalog

1. **Button**:
   - `btn-primary`: Solid accent fill, white text, subtle active press.
   - `btn-secondary`: Neutral surface with 1px border.
   - `btn-ghost`: Transparent background, hover tint.
   - `btn-danger`: Error tone fill for destructive actions.
2. **Segmented Control**:
   - Tight inline toggle (e.g. Small 1x / Med 2x / Large 3x / Viewport) with smooth active slider.
3. **Stat Tile**:
   - Structured numerical block: small muted label top, large monospace tabular readout center, unit right.
4. **Comparison Slider**:
   - Thin 2px white dividing rule with 28px circular grip handle; mouse & touch event listeners preventing page scroll.
5. **Dropzone**:
   - Dashed 1px border (`--color-border-default`), subtle hover highlight, clear accepted formats and max size tags.
6. **Alert Banner**:
   - Left-bordered single-tone status banner for Experimental OOD disclaimers and offline notifications.
7. **Map Drawer / Sheet**:
   - Floating panel on desktop, bottom sheet with drag handle on mobile.
8. **Icons**:
   - Single clean set: Lucide SVG icons (16px and 20px, stroke-width 1.5). Zero emojis.
