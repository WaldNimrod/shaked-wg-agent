---
id: AOS_MODULE_11_RTL_BIDI_STANDARD_v1.0.0
module: 11
title: RTL & Bidirectional UI Standards
version: 1.0.0
status: ACTIVE
date: 2026-04-05
scope: All projects with rtl: true in profile (Hebrew UI or other RTL language)
authority: Team 100 (synthesized from research + web validation)
research_source: TEAM_190_RTL_RESEARCH_REPORT_v1.0.0 + direct web validation 2026-04-05
activation_condition: Required when project declares rtl: true. Reference in ACTIVATION_BUILDER.md.
---

# AOS Module 11 — RTL & Bidirectional UI Standard

## Research Validation Summary

All technical claims in this module were validated against authoritative sources on 2026-04-05.
Sources: MDN, W3C, Bootstrap 5.3 official docs, Material Design bidirectionality guide, MUI RTL docs.

**Key validation outcomes:**
- Bootstrap 5 RTL: all technical claims confirmed. **Bootstrap explicitly marks RTL as experimental.**
- CSS logical properties: no polyfill required in 2025 for any modern browser. IE11 only exception (EOL).
- MUI portal direction: confirmed via MUI GitHub and docs — portals do not inherit local `dir`.
- Shekel sign display: confirmed via W3C i18n — wrap price tokens in `dir="ltr"`.
- `document.dir`: confirmed as canonical HTML Living Standard API.

**Conflicting approaches resolved in this document:**
- `dir="rtl"` vs CSS-only direction: HTML wins. CSS direction is for narrow edge cases only.
- Logical properties vs physical: logical properties are mandatory. Physical = exception requiring justification.
- `dir="auto"` vs `<bdi>`: use both — different roles. `dir="auto"` for containers, `<bdi>` for inline isolation.
- Bootstrap RTL vs custom CSS architecture: Bootstrap RTL as acceleration layer; custom CSS extends it.

---

## SECTION 1 — HTML Foundation

### 1.1 Document Direction Declaration

**MUST** set both `lang` and `dir` on the root `<html>` element for RTL pages.

```html
<!-- CORRECT — Hebrew page -->
<html lang="he" dir="rtl">

<!-- CORRECT — Arabic page -->
<html lang="ar" dir="rtl">

<!-- WRONG — dir without lang -->
<html dir="rtl">

<!-- WRONG — CSS-only approach, not semantic -->
<html> <!-- with body { direction: rtl; } in CSS -->
```

**Rationale:** `dir` is semantic metadata — it belongs to content, not presentation.
Bootstrap 5 RTL explicitly requires both attributes on `<html>`. Omitting `lang` breaks
screen readers, search engines, and text-shaping.

### 1.2 Element-Level Direction

**MUST** use `dir="auto"` on input fields and containers whose text direction is unknown at authoring time.

```html
<!-- User input — direction unknown until user types -->
<input type="text" dir="auto" name="company_name">
<textarea dir="auto" name="notes"></textarea>

<!-- External/API content of unknown direction -->
<div dir="auto">{{ ticker.description }}</div>

<!-- MUST use dir="rtl" only when direction is known -->
<p dir="rtl">טקסט עברי ידוע</p>

<!-- MUST use dir="ltr" for known LTR islands in RTL page -->
<code dir="ltr">import React from 'react'</code>
```

**Decision on `dir="auto"` vs explicit `dir`:** Use `dir="auto"` when direction is determined at runtime (user content, API data). Use explicit `dir="rtl"` or `dir="ltr"` only when direction is known at authoring time.

### 1.3 Language Declaration

**MUST** use BCP 47 language tags. **MUST NOT** rely on `dir` alone for language identification.

```html
<!-- Hebrew (Israel) -->
<html lang="he">        <!-- OR -->
<html lang="he-IL">

<!-- Arabic (Generic) -->
<html lang="ar">

<!-- Mixed-language pages: declare dominant language at root, override at element level -->
<html lang="he" dir="rtl">
  <p>מחיר: <span lang="en" dir="ltr">USD 150.00</span></p>
```

---

## SECTION 2 — CSS Logical Properties

### 2.1 Mandatory Logical Properties

Every property in this list **MUST** use the logical form in all new code. Physical form = FAIL in code review.

```css
/* SPACING */
margin-inline-start: 16px;    /* replaces margin-left  */
margin-inline-end: 16px;      /* replaces margin-right */
margin-block-start: 16px;     /* replaces margin-top   */
margin-block-end: 16px;       /* replaces margin-bottom */

padding-inline-start: 16px;   /* replaces padding-left  */
padding-inline-end: 16px;     /* replaces padding-right */
padding-block-start: 16px;    /* replaces padding-top   */
padding-block-end: 16px;      /* replaces padding-bottom */

/* BORDERS */
border-inline-start: 2px solid #ccc;   /* replaces border-left  */
border-inline-end: 2px solid #ccc;     /* replaces border-right */
border-block-start: 2px solid #ccc;    /* replaces border-top   */
border-block-end: 2px solid #ccc;      /* replaces border-bottom */

/* POSITIONING */
inset-inline-start: 0;    /* replaces left  (for position: absolute/fixed/sticky) */
inset-inline-end: 0;      /* replaces right */
inset-block-start: 0;     /* replaces top   */
inset-block-end: 0;       /* replaces bottom */

/* TEXT ALIGNMENT */
text-align: start;   /* replaces text-align: left  */
text-align: end;     /* replaces text-align: right */
```

### 2.2 Physical → Logical Mapping Table

| Physical property | Logical replacement | Notes |
|---|---|---|
| `margin-left` | `margin-inline-start` | |
| `margin-right` | `margin-inline-end` | |
| `margin-top` | `margin-block-start` | |
| `margin-bottom` | `margin-block-end` | |
| `padding-left` | `padding-inline-start` | |
| `padding-right` | `padding-inline-end` | |
| `padding-top` | `padding-block-start` | |
| `padding-bottom` | `padding-block-end` | |
| `border-left` | `border-inline-start` | |
| `border-right` | `border-inline-end` | |
| `border-top-left-radius` | `border-start-start-radius` | |
| `border-top-right-radius` | `border-start-end-radius` | |
| `border-bottom-left-radius` | `border-end-start-radius` | |
| `border-bottom-right-radius` | `border-end-end-radius` | |
| `left` | `inset-inline-start` | for positioned elements |
| `right` | `inset-inline-end` | for positioned elements |
| `top` | `inset-block-start` | |
| `bottom` | `inset-block-end` | |
| `text-align: left` | `text-align: start` | |
| `text-align: right` | `text-align: end` | |
| `float: left` | `float: inline-start` | |
| `float: right` | `float: inline-end` | |

### 2.3 Exceptions and Edge Cases

Properties with **no logical equivalent** — use physical + `[dir="rtl"]` override:

```css
/* transform: no logical equivalent */
.slide-panel {
  transform: translateX(-100%);   /* default LTR: slides from left */
}
[dir="rtl"] .slide-panel {
  transform: translateX(100%);    /* RTL: slides from right */
}

/* background-position: no logical equivalent */
.icon-field {
  background-position: left 12px center;
}
[dir="rtl"] .icon-field {
  background-position: right 12px center;
}

/* box-shadow directional offset: no logical equivalent */
.card {
  box-shadow: 4px 2px 8px rgba(0,0,0,.12);    /* LTR: shadow to right */
}
[dir="rtl"] .card {
  box-shadow: -4px 2px 8px rgba(0,0,0,.12);   /* RTL: shadow to left */
}
```

### 2.4 Browser Support Statement

**No polyfill required in 2025.** All modern browsers (Chrome 89+, Firefox 66+, Safari 15+, Edge 89+) support CSS Logical Properties and Values Module Level 1 natively.

IE11 does not support logical properties — IE11 is EOL and not a supported target for new AOS projects.

**Shorthand exceptions:** `margin-inline`, `padding-inline`, `padding-block`, `inset` — these shorthands have the same baseline support as individual logical properties.

---

## SECTION 3 — Bootstrap 5 RTL Integration

### 3.1 Required File Configuration

**⚠️ Bootstrap 5 RTL is officially marked EXPERIMENTAL in Bootstrap documentation.**
Validate behavior for each Bootstrap upgrade.

**MUST** swap Bootstrap CSS for RTL variant AND set both `dir` and `lang` on `<html>`:

```html
<!-- RTL page — correct Bootstrap 5 RTL setup -->
<html lang="he" dir="rtl">
<head>
  <!-- MUST use bootstrap.rtl.min.css, NOT bootstrap.min.css -->
  <link rel="stylesheet" href="bootstrap.rtl.min.css">
  <!-- Custom RTL overrides AFTER Bootstrap RTL -->
  <link rel="stylesheet" href="app.rtl.css">
</head>
```

```html
<!-- If serving both LTR and RTL from same base, load conditionally -->
<link rel="stylesheet" href="{{ 'bootstrap.rtl.min.css' if rtl else 'bootstrap.min.css' }}">
```

**CDN path for Bootstrap 5.3 RTL:**
`https://cdn.jsdelivr.net/npm/bootstrap@5.3.x/dist/css/bootstrap.rtl.min.css`

### 3.2 Custom CSS Architecture

```
assets/css/
├── bootstrap.rtl.min.css     ← Bootstrap RTL (do not modify)
├── app.base.css               ← Direction-neutral: colors, typography, logical-property layouts
└── app.rtl.css                ← RTL-specific overrides (loaded after bootstrap.rtl.min.css)
```

**MUST NOT** place RTL overrides before Bootstrap RTL — specificity will break.

**app.rtl.css example:**
```css
/* Overrides that Bootstrap RTL does not handle */
[dir="rtl"] .breadcrumb-item + .breadcrumb-item::before {
  float: right;
  padding-right: 0;
  padding-left: var(--bs-breadcrumb-divider-gap);
}

[dir="rtl"] .form-check {
  padding-inline-start: 0;
  padding-inline-end: 1.5em;
}
```

### 3.3 Known Bootstrap 5 RTL Gaps (require manual fix)

Bootstrap RTL uses RTLCSS auto-processing which handles most cases, but these require manual review:

| Component | Issue | Fix |
|---|---|---|
| Breadcrumbs | Divider direction | Set `--bs-breadcrumb-divider` to a mirrored char or SVG |
| Icons in buttons | `margin-left`/`margin-right` on icon spacing | Use `gap` + flexbox instead of directional margins |
| Toast positioning | Fixed corner position | Use `inset-inline-end` + `inset-block-start` instead of `right`/`top` |
| Progress bar | LTR animation direction | Override `--bs-progress-bar-animation-timing` for RTL |
| Input group addon | Addon appears on wrong side | Reorder DOM in RTL: place icon addon on `end` side |

---

## SECTION 4 — Bidirectional Text Handling

### 4.1 Embedded LTR in RTL Context

**MUST** wrap known-LTR inline content in explicit `dir="ltr"` spans:

```html
<!-- Ticker symbols in Hebrew UI — always LTR -->
<span dir="ltr">AAPL</span>

<!-- URLs — always LTR -->
<a href="..." dir="ltr">https://example.com</a>

<!-- Code snippets — always LTR -->
<code dir="ltr">const x = 1;</code>

<!-- Dates in international format — use ltr to prevent reordering -->
<span dir="ltr">2026-04-05</span>

<!-- Product codes, ISINs, CUSIPs — always LTR -->
<span dir="ltr">US0378331005</span>
```

**MUST** use `<bdi>` for unknown-direction inline content inserted into Hebrew sentences:

```html
<!-- User name of unknown direction inserted mid-sentence -->
<p>המשתמש <bdi>{{ user.display_name }}</bdi> ביצע פעולה</p>

<!-- Ticker name from API — unknown direction -->
<td><bdi>{{ holding.ticker_name }}</bdi></td>
```

### 4.2 Unicode Bidi Model

Use these in ascending order of intervention:

| Mechanism | HTML | CSS | When to use |
|---|---|---|---|
| `<bdi>` | `<bdi>text</bdi>` | — | Unknown-direction inline content in RTL sentence |
| `dir="auto"` | `<element dir="auto">` | — | Container with unknown-direction content |
| `dir="ltr"` | `<span dir="ltr">text</span>` | — | Known-LTR island in RTL context |
| `unicode-bidi: isolate` | — | `unicode-bidi: isolate` | CSS-only bidi isolation when HTML attribute unavailable |
| `unicode-bidi: bidi-override` | — | `unicode-bidi: bidi-override` | Force direction, overriding bidi algorithm — rare |

**Decision:** Prefer HTML attributes over CSS bidi properties. CSS `unicode-bidi` is a rendering fallback for cases where markup cannot be changed (third-party injected content).

```css
/* CSS-only bidi isolation — use only when dir attribute unavailable */
.injected-unknown-content {
  unicode-bidi: isolate;
}
```

### 4.3 Price and Currency Display — Hebrew UI

**Hebrew numeral rule: ALWAYS Western numerals (0-9).** Arabic-Indic numerals (٠١٢٣) are an Arabic/Persian convention and never apply to Hebrew UI. No CSS or font configuration needed.

**Shekel sign (₪) canonical pattern:**

The ₪ sign MUST appear before the digits in source. Wrap the price token in `dir="ltr"`:

```html
<!-- CORRECT — shekel sign before digits, explicit LTR embedding -->
<span dir="ltr">₪150.00</span>

<!-- CORRECT — using Intl.NumberFormat for locale-aware output -->
<span dir="ltr">{{ new Intl.NumberFormat('he-IL', { style: 'currency', currency: 'ILS' }).format(150) }}</span>

<!-- WRONG — shekel sign after digits (bidi algorithm may place it incorrectly) -->
<span>150.00₪</span>

<!-- WRONG — no LTR wrapping (₪ is a neutral char, may attach to wrong end) -->
<span>₪150.00</span>  <!-- without dir="ltr" -->
```

**Why `dir="ltr"` is required:** ₪ is a Unicode neutral character. Without an explicit LTR wrapper, the bidirectional algorithm may attach it to the surrounding RTL context and render it on the wrong side of the number.

---

## SECTION 5 — Component RTL Patterns

### 5.1 Navigation and Menus

**MUST** use `flex-direction: row-reverse` or logical flexbox on nav items. **MUST NOT** use fixed `float: right` for RTL nav.

```css
/* Navbar — RTL reverses item order visually */
[dir="rtl"] .navbar-nav {
  flex-direction: row-reverse;
}

/* Breadcrumb — separator faces the other way */
[dir="rtl"] .breadcrumb-item + .breadcrumb-item::before {
  content: "/";  /* or use a mirrored arrow */
  float: right;
  padding-inline-end: 0.5rem;
  padding-inline-start: 0;
}

/* Sidebar — flip position */
.sidebar {
  inset-inline-start: 0;   /* Left in LTR, right in RTL */
}
```

**Anti-pattern:** `margin-left: 220px` for main content offset when sidebar is open — use `margin-inline-start`.

### 5.2 Data Tables

**MUST** use logical properties for all table column spacing. **MUST NOT** use `left`/`right` for sticky columns.

```css
/* Sticky first column */
.table th:first-child,
.table td:first-child {
  position: sticky;
  inset-inline-start: 0;    /* NOT left: 0 */
  z-index: 1;
}

/* Sort arrow — flip for RTL */
.sort-asc::after  { content: "↑"; }
.sort-desc::after { content: "↓"; }
/* Arrow position — inline-end, not right */
.sortable {
  padding-inline-end: 20px;
}
.sortable::after {
  inset-inline-end: 4px;    /* NOT right: 4px */
  position: absolute;
}
```

**Anti-pattern:** `text-align: left` on table cells — use `text-align: start`.

### 5.3 Forms and Inputs

**MUST** label placement follows reading direction. **MUST** use `dir="auto"` on text inputs for user content.

```html
<!-- Label inherits RTL from page — no override needed -->
<div class="form-group">
  <label for="price">מחיר</label>
  <!-- dir="ltr" for numeric inputs — numbers are always LTR -->
  <input type="number" id="price" dir="ltr" value="150.00">
</div>

<!-- Mixed-content input — user may type Hebrew or English -->
<input type="text" dir="auto" placeholder="שם חברה / Company name">

<!-- Validation message — inherits RTL, no override needed -->
<div class="error-msg">שדה חובה</div>
```

### 5.4 Modals and Drawers

**MUST** drawers/sidepanels open from `inline-end` side in RTL (right side of screen becomes the "end"):

```css
/* Drawer slides in from the end (left in RTL, right in LTR) */
.drawer {
  inset-inline-end: 0;
  inset-block: 0;
  transform: translateX(100%);   /* Default: offscreen to the right */
}
[dir="rtl"] .drawer {
  transform: translateX(-100%);  /* RTL: offscreen to the left */
}
.drawer.open {
  transform: translateX(0);
}

/* Modal — centered, no direction concern for position */
/* But close button MUST be at inline-end */
.modal-header .close-btn {
  margin-inline-start: auto;    /* NOT margin-left: auto */
}
```

### 5.5 Icons and SVG

**Rule:** Mirror icons that represent **direction of movement or reading flow**. Do NOT mirror icons that represent **physical objects, universal conventions, or clockwise rotation**.

| Mirror | Do NOT mirror |
|---|---|
| Back/forward navigation arrows | Media play/pause/rewind (tape convention) |
| Directional chevrons (next/prev) | Clock icons (always clockwise) |
| Reply/send arrows | Circular refresh/loading spinners |
| Reading-direction progress indicators | Warning triangles, checkmarks, close (X) |
| Search icon (handle toward reading start) | Brand logos and wordmarks |

```css
/* Mirror directional SVG icons in RTL */
[dir="rtl"] .icon-forward,
[dir="rtl"] .icon-arrow-right,
[dir="rtl"] .icon-chevron-next {
  transform: scaleX(-1);
}

/* Never mirror these */
/* .icon-play, .icon-pause, .icon-clock, .icon-check — no override */
```

### 5.6 Tooltips and Popovers

**MUST** placement logic uses logical positions (`start`/`end`), not physical (`left`/`right`).

```javascript
// Popper.js / Floating UI — use logical placement
const placement = 'inline-end';  // appears to right in LTR, left in RTL

// If library uses physical placement, map at runtime:
const placement = document.dir === 'rtl' ? 'left' : 'right';
```

```css
/* Tooltip arrow — logical positioning */
.tooltip[data-placement="inline-end"]::before {
  inset-inline-start: -6px;    /* arrow on the start-side of tooltip box */
}
```

### 5.7 Progress and Step Indicators

**MUST** progress bar fill direction follows reading direction:

```css
/* Progress bar — fill from inline-start */
.progress-bar {
  width: var(--progress-value);
  /* In RTL: browser renders from right, which is correct */
  /* Do NOT override fill direction with transform */
}

/* Step indicator — numbers flow from inline-start */
.steps {
  display: flex;
  flex-direction: row;    /* flex respects dir attribute automatically */
}

/* Completed step indicator — logical border */
.step.completed {
  border-inline-end: 2px solid green;   /* NOT border-right */
}
```

---

## SECTION 6 — CSS Architecture

### 6.1 Recommended Architecture

**Decision: Logical-properties-first architecture.** Use `[dir="rtl"]` overrides only for properties with no logical equivalent (transforms, gradients, box-shadow direction, pseudo-element content).

This is superior to:
- RTL-first (inverts LTR assumptions everywhere)
- LTR-first with full RTL override file (duplicates all rules)
- Pure `[dir="rtl"]` block overrides (verbose, drift-prone)

### 6.2 Custom Properties Pattern

```css
/* In :root — define direction-neutral tokens using logical naming */
:root {
  --spacing-start: 16px;    /* renamed, not "left" */
  --spacing-end: 24px;
}

/* For values logical properties cannot express: define per-dir */
:root {
  --slide-offscreen: translateX(-100%);    /* LTR default */
  --shadow-direction: 4px;                  /* LTR default */
}
[dir="rtl"] {
  --slide-offscreen: translateX(100%);
  --shadow-direction: -4px;
}

/* Consume — point of use is direction-agnostic */
.drawer { transform: var(--slide-offscreen); }
.card   { box-shadow: var(--shadow-direction) 2px 8px rgba(0,0,0,.1); }
```

**Note on `:dir()` selector:** Use `[dir="rtl"]` attribute selector for document-level direction (set once on `<html>`). Reserve `:dir(rtl)` CSS pseudo-class for inherited computed direction in mixed-direction subtrees.

### 6.3 File Organization

```
assets/css/
├── bootstrap.rtl.min.css       ← Bootstrap RTL (unmodified, loaded first)
├── tokens.css                  ← CSS custom properties (direction-neutral naming)
├── base.css                    ← Logical-properties layout, typography
├── components.css              ← Component styles (logical properties throughout)
└── rtl-exceptions.css          ← [dir="rtl"] overrides ONLY for logical-property gaps
                                   (transforms, gradients, pseudo-elements)
```

**MUST NOT** create a parallel `ltr.css` + `rtl.css` file pair — this duplicates all rules and creates drift.

---

## SECTION 7 — JavaScript and Dynamic Content

### 7.1 Direction Detection and Setting

**MUST** use `document.dir` (HTML Living Standard canonical API), not `document.documentElement.dir`.

```javascript
// Read current document direction
const dir = document.dir;              // "rtl" or "ltr" or ""

// Write document direction
document.dir = 'rtl';

// Read direction of any element (computed, includes inheritance)
const computedDir = getComputedStyle(element).direction;  // "rtl" or "ltr"

// Check if page is RTL
const isRTL = document.dir === 'rtl';
```

**Anti-pattern:** Reading/writing `document.body.style.direction` — bypasses semantic model.

### 7.2 Dynamic Content Injection

**MUST** ensure injected HTML fragments carry their own direction context:

```javascript
// Inject unknown-direction content — wrap in bdi-equivalent span
function renderTickerName(name) {
  return `<span dir="auto">${escapeHTML(name)}</span>`;
}

// Inject known-RTL block
function renderHebrewNotification(text) {
  return `<div dir="rtl" lang="he">${escapeHTML(text)}</div>`;
}

// Portal components (React) — apply dir from document or theme
function Portal({ children }) {
  return ReactDOM.createPortal(
    <div dir={document.dir}>{children}</div>,
    document.body
  );
}
```

**Critical:** MUI (Material UI) portal components (Dialog, Menu, Popover, Tooltip) do NOT inherit `dir` from ancestor elements because portals render at `document.body` level. **MUST** configure direction at theme level:

```javascript
// MUI — MUST set theme direction AND install RTL CSS plugin
import { createTheme, ThemeProvider } from '@mui/material/styles';
import rtlPlugin from '@mui/stylis-plugin-rtl';
import { CacheProvider } from '@emotion/react';
import createCache from '@emotion/cache';
import { prefixer } from 'stylis';

const cacheRtl = createCache({
  key: 'muirtl',
  stylisPlugins: [prefixer, rtlPlugin],
});

const theme = createTheme({ direction: 'rtl' });

// Both cache AND theme required for complete MUI RTL
<CacheProvider value={cacheRtl}>
  <ThemeProvider theme={theme}>
    <App />
  </ThemeProvider>
</CacheProvider>
```

### 7.3 Locale-Aware Date/Number Formatting

**MUST** use `Intl` API with `he-IL` locale for Hebrew UI. **MUST NOT** hardcode format strings.

```javascript
// Currency — Intl.NumberFormat canonical pattern
const price = new Intl.NumberFormat('he-IL', {
  style: 'currency',
  currency: 'ILS',
  minimumFractionDigits: 2,
}).format(150.00);
// Output: "‏150.00 ₪" — note: Intl adds bidi marks; wrap output in dir="ltr"

// Safer: wrap rendered output explicitly
const el = document.createElement('span');
el.dir = 'ltr';
el.textContent = price;

// Date formatting
const date = new Intl.DateTimeFormat('he-IL', {
  year: 'numeric', month: 'long', day: 'numeric'
}).format(new Date());

// Number formatting (no currency)
const num = new Intl.NumberFormat('he-IL').format(1234567.89);
// Output: "1,234,567.89" — Hebrew uses Western numerals always
```

**Hebrew numerals:** Hebrew UI ALWAYS uses Western numerals (0-9). Arabic-Indic numerals (٠١٢٣) are a strictly Arabic/Persian convention and NEVER apply to Hebrew. No CSS `font-variant-numeric` configuration needed.

---

## SECTION 8 — Validation and Testing

### 8.1 Pre-Commit Checklist

Each item is a YES/NO gate. **All must be YES before merge.**

**HTML:**
- [ ] `<html>` has `lang` attribute set to correct BCP 47 tag (e.g., `he`, `he-IL`)
- [ ] `<html>` has `dir="rtl"` for RTL pages
- [ ] All user-input fields that may contain unknown-direction text have `dir="auto"`
- [ ] All unknown-direction inline content is wrapped in `<bdi>` or `dir="auto"` span
- [ ] Known-LTR islands (ticker symbols, URLs, code, product codes) have explicit `dir="ltr"`
- [ ] Price/currency tokens are wrapped in `dir="ltr"` span
- [ ] Shekel sign (₪) appears BEFORE digits in HTML source

**CSS:**
- [ ] No `margin-left` or `margin-right` in new component CSS (use `margin-inline-*`)
- [ ] No `padding-left` or `padding-right` in new component CSS (use `padding-inline-*`)
- [ ] No `left:` or `right:` for positioned elements (use `inset-inline-*`)
- [ ] No `text-align: left` or `text-align: right` (use `text-align: start`/`end`)
- [ ] No `border-left` or `border-right` for semantic UI borders (use `border-inline-*`)
- [ ] Physical properties used only for intentionally physical geometry (charts, canvas, pixel-anchored assets) — each instance has a comment justifying the exception
- [ ] `[dir="rtl"]` overrides only for transforms, gradients, pseudo-elements, box-shadow direction

**JavaScript:**
- [ ] Direction read via `document.dir` (not `document.documentElement.dir`)
- [ ] No hardcoded `'left'`/`'right'` strings in positioning logic — use logical or conditional
- [ ] Dynamic content injection wraps unknown-direction text in `dir="auto"` or `<bdi>`
- [ ] MUI projects: theme `direction: 'rtl'` AND stylis-plugin-rtl installed and configured
- [ ] Portal components independently apply direction (not relying on ancestor inheritance)
- [ ] Date/price/number formatting uses `Intl` API with `he-IL` locale

**Bootstrap 5 RTL:**
- [ ] `bootstrap.rtl.min.css` loaded (not `bootstrap.min.css`) for RTL pages
- [ ] Custom RTL CSS loads AFTER Bootstrap RTL CSS
- [ ] Breadcrumb, toast, input-group, progress bar reviewed manually (Bootstrap RTL experimental gaps)

**Icons:**
- [ ] Directional SVG icons (arrows, chevrons, send) have `[dir="rtl"] { transform: scaleX(-1) }`
- [ ] Media control icons (play, pause) and universal icons (checkmark, close) have NO mirroring override

### 8.2 Automated Checks

Add to project lint pipeline:

```bash
# stylelint: ban physical properties in component CSS
# .stylelintrc:
{
  "rules": {
    "liberty/use-logical-spec": ["always", {
      "disable": ["overflow", "resize", "contain"]
    }]
  }
}

# Grep-based CI check (simpler, no plugin needed):
# Fail if any component CSS uses banned physical properties
grep -rn --include="*.css" \
  -E "(margin-left|margin-right|padding-left|padding-right|border-left:|border-right:)(?!.*RTL exception)" \
  src/components/ && exit 1 || exit 0
```

```javascript
// ESLint: ban hardcoded 'left'/'right' in style objects (React/JSX)
// Add to .eslintrc:
{
  "rules": {
    "no-restricted-syntax": [
      "error",
      {
        "selector": "Property[key.value='marginLeft'], Property[key.value='marginRight'], Property[key.value='paddingLeft'], Property[key.value='paddingRight']",
        "message": "Use logical CSS properties (marginInlineStart, etc.) instead of physical properties"
      }
    ]
  }
}
```

### 8.3 Common RTL Bugs Reference

| Bug | What it looks like | Cause | Fix |
|---|---|---|---|
| Text aligned wrong | Hebrew text aligns left | Missing `dir="rtl"` on `<html>` or ancestor | Add `dir="rtl"` to root |
| Price displays as "150.00₪" instead of "₪150.00" | Shekel sign on wrong side | ₪ after digits in source, no `dir="ltr"` wrapper | Put ₪ before digits + wrap in `dir="ltr"` |
| Navigation icons point wrong way | Back arrow points forward | SVG not mirrored | Add `[dir="rtl"] .icon-back { transform: scaleX(-1) }` |
| Tooltip appears on wrong side | Tooltip left of trigger in RTL | Physical placement (left/right) in tooltip library | Use logical placement or map at runtime |
| Modal dialog content misaligned | Text aligns left inside modal | Modal/portal doesn't inherit `dir` | Add `dir` to modal root or configure at theme level |
| Sticky column wrong side | First column sticks to right in RTL | `left: 0` instead of `inset-inline-start: 0` | Replace with logical property |
| User name corrupts sentence direction | "Updated by UserName at 12:00" renders oddly | Missing `<bdi>` around dynamic name | Wrap: `<bdi>{{ name }}</bdi>` |
| Drawer opens from wrong side | Drawer always opens from right | `right: 0` instead of `inset-inline-end: 0` | Use logical property |
| Sort arrow on wrong side | Sort indicator appears on left in RTL | Physical positioning on sort icon | Use `inset-inline-end` |
| Mixed LTR numbers scramble context | Date "05-04-2026" renders as "2026-04-05" | No `dir="ltr"` on date span | Wrap dates: `<span dir="ltr">05-04-2026</span>` |

---

## SECTION 9 — Quick Reference Card

### MUST Rules (complete list)

```
HTML:
  MUST: <html lang="he" dir="rtl"> — both attributes required
  MUST: dir="auto" on user inputs and runtime-injected content containers
  MUST: <bdi> for unknown-direction text inline in RTL sentences
  MUST: dir="ltr" on ticker symbols, URLs, code, product codes, prices
  MUST: ₪ before digits in source, wrap price in dir="ltr"

CSS:
  MUST: margin-inline-start/end — not margin-left/right
  MUST: padding-inline-start/end — not padding-left/right
  MUST: inset-inline-start/end — not left/right (for positioned elements)
  MUST: text-align: start/end — not left/right
  MUST: border-inline-start/end — not border-left/right (semantic borders)
  MUST: [dir="rtl"] overrides for transforms, gradients, box-shadow direction

JavaScript:
  MUST: document.dir — not document.documentElement.dir
  MUST: Intl.NumberFormat('he-IL', {style: 'currency', currency: 'ILS'}) for prices
  MUST: Wrap Intl-formatted currency in dir="ltr" span
  MUST: MUI: createTheme({direction: 'rtl'}) + @mui/stylis-plugin-rtl

Bootstrap:
  MUST: bootstrap.rtl.min.css for RTL pages (RTL is experimental in Bootstrap 5)

Icons:
  MUST: scaleX(-1) on directional arrows, chevrons, send icons in [dir="rtl"]
  MUST NOT: scaleX(-1) on media controls, clocks, spinners, checkmarks
```

### Physical → Logical Quick Map

```
margin-left        → margin-inline-start
margin-right       → margin-inline-end
padding-left       → padding-inline-start
padding-right      → padding-inline-end
left: (positioned) → inset-inline-start
right: (positioned)→ inset-inline-end
text-align: left   → text-align: start
text-align: right  → text-align: end
border-left        → border-inline-start
border-right       → border-inline-end
float: left        → float: inline-start
float: right       → float: inline-end
```

---

*AOS Module 11 | RTL & Bidirectional UI Standard | v1.0.0 | 2026-04-05*
*Sources: MDN, W3C, Bootstrap 5.3, Material Design, MUI, Playwright, Firefox RTL Guidelines*
*Validated: 2026-04-05 against live documentation*
