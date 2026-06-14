# VOYO Brand Guidelines

> Rules for maintaining visual consistency across every touchpoint.

---

## Brand Voice

**CLEO speaks like a knowledgeable Egyptian friend** — warm, practical, occasionally using Arabic phrases, never robotic. The visual identity matches this voice: it's crafted, warm, and intelligent without trying too hard.

**Do:**
- Be warm and welcoming
- Show genuine enthusiasm for Egypt
- Use Arabic phrases naturally (Ahlan, Yalla, Inshallah)
- Be practical and honest
- Respect cultural significance

**Don't:**
- Use travel clichés ("hidden gem", "off the beaten path")
- Overuse emojis in UI copy
- Be overly formal or corporate
- Make inflated claims
- Use generic travel stock photography

---

## Logo Usage

### Clear Space
- Minimum clear space around wordmark = height of the "V" character
- Never place logo on busy backgrounds without a solid container
- Logo must always be fully visible, never cropped or partially obscured

### Minimum Size
- Wordmark: 80px wide (mobile)
- Logo mark: 16px (favicon), 24px (nav bar)

### Color Variants
- **Primary:** `expedition` (#D45028) on light backgrounds
- **Light:** White on dark/photo backgrounds
- **Monochrome:** `ink` (#1A1714) on light, `darkInk` (#F5F3EF) on dark

### Don't
- Don't stretch, skew, or rotate the logo
- Don't add drop shadows or glow effects
- Don't place on backgrounds with less than 3:1 contrast
- Don't alter the logo colors outside approved variants
- Don't add outlines or strokes

---

## Color Usage Rules

### Primary vs Accent
- `expedition` (#D45028) is the **primary action color** — use for main CTAs, active states, and the most important interactive element on any screen.
- `sky` (#1C72B4) is the **brand identity color** — use for CLEO, navigation highlights, and brand recognition elements.
- All other colors are **accent/semantic** — use for their designated purpose only.

### Color Ratios (per screen)
- **Backgrounds:** 90% neutral (page/paper/vellum)
- **Primary accent:** 5% (one CTA per screen, active nav)
- **Secondary accents:** 5% (category badges, map regions, status)

### Don't
- Don't use `expedition` and `terra` adjacent (too similar)
- Don't use more than 3 accent colors on a single screen
- Don't use `discovery` purple as a primary action color (it's for discovery/insight moments)
- Don't use pure black (#000000) — always use `ink` (#1A1714) instead
- Don't use pure white text on `sky` blue — ensure 4.5:1 contrast

---

## Typography Rules

### Hierarchy
1. **Display** (32px Bold) — Maximum once per screen (region name on map, hero title)
2. **Headlines** (18-28px) — Section headers and card titles
3. **Body** (14-16px) — All readable content
4. **Labels** (11-14px) — Navigation, badges, metadata

### Line Length
- Maximum 70 characters per line for body text
- Maximum 40 characters for headlines

### Don't
- Don't use more than 2 font families on a single screen
- Don't use ALL CAPS for body text (labels only)
- Don't use font weight below Regular (w400)
- Don't mix Outfit and Work Sans in the same context level

---

## Illustration Rules

### Style
- Flat, geometric, Kurzgesagt-inspired
- Warm palette from brand colors
- No perspective or 3D effects
- Characters are simple shapes with expressive eyes
- Scenes have depth through layering, not shading

### Usage
- Empty states (always include illustration + text + CTA)
- Onboarding steps
- Error states
- Never use illustration in place of a photo for POI images

### Don't
- Don't use stock photography for UI illustrations
- Don't mix illustration styles (stick to one geometric language)
- Don't use illustrations decoratively without purpose
- Don't use Clip Art or emoji-style graphics

---

## Spacing & Layout Rules

### Grid
- 8px base grid — all spacing values are multiples of 8 (4, 8, 12, 16, 24, 32, 48, 64)
- Content padding: 16px from screen edges (mobile), 24px (tablet), 32px (web)
- Card internal padding: 12-16px

### Alignment
- Text: left-aligned (never center-aligned for body text)
- CTA buttons: full-width on mobile (with 16px horizontal padding)
- Section headers: left-aligned with optional right-aligned action link

### Don't
- Don't center-align paragraphs of text
- Don't use arbitrary spacing values (only multiples of 4)
- Don't place interactive elements outside thumb zones (bottom 2/3 of screen for primary actions)

---

## Dark Mode Rules

### Approach
- **True dark mode**, not inverted — warm dark tones (not pure black)
- Colors shift toward warmer, slightly muted variants
- Shadows are replaced by subtle borders (`darkSmoke`)
- Illustrations and CLEO owl remain colorful against dark backgrounds

### Color Mapping
| Light | Dark | Notes |
|-------|------|-------|
| `page` (#F7F5F1) | `darkPage` (#121110) | Background |
| `paper` (#FFFFFF) | `darkPaper` (#1E1C18) | Cards |
| `vellum` (#F0EBE3) | `darkVellum` (#252320) | Chat bubbles |
| `smoke` (#E8E2D8) | `darkSmoke` (#2E2B26) | Borders |
| `ink` (#1A1714) | `darkInk` (#F5F3EF) | Primary text |
| `stone` (#6A6058) | `darkStone` (#9A938A) | Secondary text |
| `expedition` | Same (#D45028) | No change |
| `sky` | Same (#1C72B4) | No change |
| Map tiles | Dark variant | Stadia Maps or MapTiler dark tiles |

---

## Accessibility Requirements

- **Contrast:** 4.5:1 minimum for body text, 3:1 for large text and UI components
- **Touch targets:** Minimum 48×48px for all interactive elements
- **Color alone:** Never use color as the sole indicator of meaning (always add icon/text)
- **Focus states:** Visible focus ring (2px, color.sky) on all interactive elements
- **Screen readers:** Semantic labels on all non-decorative elements
- **Reduced motion:** All animations respect `prefers-reduced-motion`
