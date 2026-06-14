# VOYO Design Tokens

> Concrete, implementable token definitions for Flutter `ThemeData` and reference by AI image generators.

---

## Color Tokens

### Light Theme

| Token | Hex | Flutter | Usage |
|-------|-----|---------|-------|
| `color.page` | `#F7F5F1` | `Color(0xFFF7F5F1)` | Primary scaffold background |
| `color.paper` | `#FFFFFF` | `Color(0xFFFFFFFF)` | Cards, sheets, elevated surfaces |
| `color.vellum` | `#F0EBE3` | `Color(0xFFF0EBE3)` | CLEO chat bubbles, secondary bg |
| `color.smoke` | `#E8E2D8` | `Color(0xFFE8E2D8)` | Dividers, borders, disabled bg |
| `color.expedition` | `#D45028` | `Color(0xFFD45028)` | Primary CTA, Cairo region |
| `color.terra` | `#C4622A` | `Color(0xFFC4622A)` | Secondary accent, Giza region |
| `color.sky` | `#1C72B4` | `Color(0xFF1C72B4)` | Brand blue, CLEO, Alexandria |
| `color.discovery` | `#8860D4` | `Color(0xFF8860D4)` | Discovery moments, Luxor |
| `color.discoveryAccessible` | `#6040B0` | `Color(0xFF6040B0)` | Accessible purple variant |
| `color.verified` | `#2A7A50` | `Color(0xFF2A7A50)` | Success, verified, Aswan |
| `color.caution` | `#D48A10` | `Color(0xFFD48A10)` | Warnings, beak, amber |
| `color.ink` | `#1A1714` | `Color(0xFF1A1714)` | Primary text |
| `color.stone` | `#6A6058` | `Color(0xFF6A6058)` | Secondary text |

### Dark Theme

| Token | Hex | Usage |
|-------|-----|-------|
| `color.darkPage` | `#121110` | Scaffold background |
| `color.darkPaper` | `#1E1C18` | Cards, sheets |
| `color.darkVellum` | `#252320` | CLEO chat bubbles |
| `color.darkSmoke` | `#2E2B26` | Dividers, borders |
| `color.darkInk` | `#F5F3EF` | Primary text |
| `color.darkStone` | `#9A938A` | Secondary text |

### Region Colors

| Region | Token | Hex |
|--------|-------|-----|
| Cairo | `region.cairo` | `#D45028` |
| Giza | `region.giza` | `#C4622A` |
| Alexandria | `region.alexandria` | `#1C72B4` |
| Luxor | `region.luxor` | `#8860D4` |
| Aswan | `region.aswan` | `#2A7A50` |
| Hurghada | `region.hurghada` | `#0EA5E9` |
| Marsa Alam | `region.marsaAlam` | `#0891B2` |
| Sinai | `region.sinai` | `#7C3AED` |

### Category Colors

| Category | Token | Hex |
|----------|-------|-----|
| Historical | `cat.historical` | `#B45309` |
| Cultural | `cat.cultural` | `#7C3AED` |
| Natural | `cat.natural` | `#059669` |
| Entertainment | `cat.entertainment` | `#EC4899` |
| Religious | `cat.religious` | `#1E3A5F` |
| Shopping | `cat.shopping` | `#D97706` |
| Dining | `cat.dining` | `#EA580C` |
| Accommodation | `cat.accommodation` | `#0EA5E9` |

### Isochrone Colors

| Zone | Token | Hex | Opacity |
|------|-------|-----|---------|
| 30 min | `isochrone.30` | `#0D9488` | Fill: 0.15, Border: 0.6 |
| 60 min | `isochrone.60` | `#D97706` | Fill: 0.15, Border: 0.6 |
| 90 min | `isochrone.90` | `#EA580C` | Fill: 0.15, Border: 0.6 |

---

## Typography Tokens

### Font Families

| Role | Font | Source |
|------|------|--------|
| Display | Outfit | Google Fonts |
| Body | Work Sans | Google Fonts |
| Arabic | System (Noto Sans Arabic) | Platform |
| Mono | Geist Mono | Bundled (fallback: JetBrains Mono) |

### Type Scale

| Token | Size | Weight | Line Height | Letter Spacing | Usage |
|-------|------|--------|-------------|----------------|-------|
| `type.displayLarge` | 32px | Bold (w700) | 1.2 | -0.5px | Hero titles, region names on map |
| `type.displayMedium` | 28px | SemiBold (w600) | 1.25 | -0.3px | Screen titles |
| `type.headlineLarge` | 24px | SemiBold (w600) | 1.3 | -0.2px | Section headers |
| `type.headlineMedium` | 20px | Medium (w500) | 1.3 | 0px | Sub-headers |
| `type.headlineSmall` | 18px | Medium (w500) | 1.35 | 0px | Card titles |
| `type.bodyLarge` | 16px | Regular (w400) | 1.5 | 0.15px | Primary body text |
| `type.bodyMedium` | 14px | Regular (w400) | 1.45 | 0.2px | Secondary text |
| `type.bodySmall` | 12px | Regular (w400) | 1.4 | 0.25px | Metadata, timestamps |
| `type.labelLarge` | 14px | Medium (w500) | 1.3 | 0.3px | Button text, nav labels |
| `type.labelMedium` | 12px | Medium (w500) | 1.3 | 0.35px | Badges, tags |
| `type.labelSmall` | 11px | Medium (w500) | 1.25 | 0.4px | Micro badges, overlines |

---

## Spacing Tokens

| Token | Value | Usage |
|-------|-------|-------|
| `space.micro` | 4px | Icon padding, tight gaps |
| `space.xs` | 8px | Component internal padding |
| `space.sm` | 12px | Between related elements |
| `space.md` | 16px | Standard card padding, list items |
| `space.lg` | 24px | Between content sections |
| `space.xl` | 32px | Between major sections |
| `space.2xl` | 48px | Screen edge to first content |
| `space.3xl` | 64px | Hero spacing, full-screen padding |

---

## Border Radius Tokens

| Token | Value | Usage |
|-------|-------|-------|
| `radius.xs` | 4px | Chips, tags |
| `radius.sm` | 8px | Input fields, small cards |
| `radius.md` | 12px | POI cards, buttons |
| `radius.lg` | 16px | Bottom sheets, large cards |
| `radius.xl` | 20px | Modal sheets (top corners) |
| `radius.full` | 9999px | Avatar circles, category dots |

---

## Elevation Tokens

| Level | Box Shadow | Usage |
|-------|-----------|-------|
| `elev.0` | none | Flat elements, backgrounds |
| `elev.1` | `0 1px 3px rgba(26,23,20,0.08)` | Cards at rest |
| `elev.2` | `0 4px 12px rgba(26,23,20,0.12)` | Cards on hover/tap |
| `elev.3` | `0 8px 24px rgba(26,23,20,0.16)` | Bottom sheets, modals |
| `elev.4` | `0 16px 48px rgba(26,23,20,0.20)` | Full-screen overlays |

---

## Animation Tokens

| Token | Duration | Curve | Usage |
|-------|----------|-------|-------|
| `anim.fast` | 150ms | easeOutCubic | Button press, small transitions |
| `anim.standard` | 300ms | easeOutCubic | Most UI transitions |
| `anim.slow` | 600ms | easeOutQuart | Isochrone bloom, sheet expand |
| `anim.map` | 800ms | easeOutQuart | Camera zoom, region focus |
| `anim.spring` | 400ms | elasticOut | Playful moments, confirmations |
| `anim.stagger` | 200ms | easeOutCubic | Delay between sequential items |

---

## Icon Size Tokens

| Token | Size | Usage |
|-------|------|-------|
| `icon.xs` | 16px | Inline, tag icons |
| `icon.sm` | 20px | List item icons, badges |
| `icon.md` | 24px | Standard, nav bar |
| `icon.lg` | 32px | Feature icons, empty states |
| `icon.xl` | 48px | CLEO avatar, hero icons |
