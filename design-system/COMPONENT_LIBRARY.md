# VOYO Component Library

> Specifications for every reusable UI component in the app. Each component lists its anatomy, states, and design tokens used.

---

## 1. POI Card (Horizontal Scroll)

**Usage:** Home screen recommendations, region explainer top picks, search results.

```
┌──────────────────────┐
│  ┌──────────────────┐ │
│  │                  │ │  ← Image area: 160×120, rounded top corners
│  │   Hero Image     │ │     Gradient fallback by category if no image
│  │   ⭐ 4.7    🏛   │ │  ← Rating badge (bottom-left), category icon (bottom-right)
│  └──────────────────┘ │
│  Abu Simbel           │  ← Name: type.headlineSmall, color.ink, 1 line truncated
│  Historical · Aswan   │  ← Subtitle: type.bodySmall, color.stone
│  "Love ancient hist…" │  ← Match reason: type.bodySmall, italic, color.discovery
└──────────────────────┘
```

**Width:** 160px  
**States:** Default → Pressed (elev.2, scale 1.02x, 150ms)

---

## 2. POI Detail Sheet

**Usage:** Expanded view of any POI from map tap or card tap.

**Structure:** `DraggableScrollableSheet`
- `initialChildSize`: 0.70
- `minChildSize`: 0.50
- `maxChildSize`: 0.95

**Anatomy:**
1. **Handle** — 40×4px rounded bar, color.smoke, centered, 8px from top
2. **Hero Image** — Full width, 220px height, gradient overlay bottom → transparent to color.paper
3. **Title Block** — Name (type.displayMedium), Arabic name (type.bodyMedium, color.stone), Category + Region badges
4. **Quick Facts Row** — Rating, Duration, Price in 3 equal columns with icons
5. **Content Sections** — Collapsible: Opening Hours, Historical Significance, Travel Tips, Tags
6. **Action Bar** — Sticky bottom: Ask CLEO, Add to Trip, Navigate (icon + label buttons)

---

## 3. CLEO Chat Bubble

### CLEO Message (left-aligned)

```
┌─────────────────────────────────┐
│  🦉                              │  ← CleoOwl avatar, 28px, above first bubble
│  ┌───────────────────────────┐  │
│  │  Ah, the Great Pyramids!  │  │  ← Background: color.vellum
│  │  Let me share their       │  │     Text: color.ink
│  │  incredible story...      │  │     Border radius: 12/12/12/4 (bottom-left sharp)
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

### User Message (right-aligned)

```
                                ┌─────────────────────────────────┐
  ┌───────────────────────────┐│                                 │
  │  Tell me about Pyramids   ││  ← Background: color.sky        │
  │                           ││     Text: Colors.white           │
  └───────────────────────────┘│     Border radius: 12/12/4/12   │
                                └─────────────────────────────────┘
```

**Max width:** 80% of screen width  
**Padding:** 12px horizontal, 8px vertical  
**Spacing between bubbles:** 4px (same sender), 12px (different sender)

---

## 4. Itinerary Card (Inline in Chat)

**Usage:** When CLEO returns `[PLANNER]` token.

```
┌──────────────────────────────────────────┐
│  📋 Your Itinerary is Ready!             │  ← Header: type.labelLarge
│  ──────────────────────────────────────  │
│  3 Days in Cairo                         │  ← Title: type.headlineMedium
│                                           │
│  Day 1: Ancient Wonders                  │  ← Day summary lines
│  Day 2: Islamic Cairo                    │
│  Day 3: Museums & Markets               │
│                                           │
│  ┌────────────────┐ ┌────────────────┐   │
│  │ View Plan      │ │  Adjust        │   │  ← Two CTAs
│  └────────────────┘ └────────────────┘   │
└──────────────────────────────────────────┘
```

**Border:** 1px solid color.smoke  
**Background:** color.paper  
**Border radius:** radius.lg

---

## 5. Region Explainer Card

**Usage:** Slides in from right when a region is tapped on the map.

```
┌─────────────────────────────────────────┐
│  [←]                                      │  ← Back / close
│  🏛️ Aswan                                │  ← Region name + icon
│  Southern gateway to Nubia               │  ← Poetic one-liner
│                                           │
│  24 POIs · 12 historical · 6 cultural    │  ← Stats row
│                                           │
│  Top picks:                               │
│  ┌────────┐ ┌────────┐                  │  ← Mini POI cards
│  │Abu     │ │Philae  │                  │     Horizontal scroll
│  │Simbel  │ │Temple  │                  │
│  │⭐ 4.8  │ │⭐ 4.7  │                  │
│  └────────┘ └────────┘                  │
│                                           │
│  [Explore POIs]  [Ask CLEO about Aswan]  │  ← Two CTAs
└─────────────────────────────────────────┘
```

**Width:** 85% of screen, right-aligned  
**Enter animation:** Slide from right 300ms + fade 200ms

---

## 6. Itinerary Stop Card

**Usage:** Inside Planner Screen, each stop in a day.

```
┌─ 09:00 ────────────────────────────────┐
│  📍 Great Pyramid of Giza               │  ← POI name: type.headlineSmall
│  Visit: 3 hours · Ticket: 200 EGP      │  ← Meta: type.bodySmall, color.stone
│  💡 Go early to beat crowds             │  ← Tip: type.bodySmall, italic
└─────────────────────────────────────────┘
```

**Between stops:** Travel segment indicator
```
    ⬇ 25 min drive (12.4 km)               ← type.labelSmall, color.stone
```

---

## 7. Bottom Navigation Bar

**Layout:** 5 positions, center is prominent CLEO button.

```
┌──────────────────────────────────────────┐
│  [🏠]      [🗺]      [🦉]      [📋]    │
│  Home      Map      CLEO*    Planner    │
└──────────────────────────────────────────┘
         *CLEO is the center elevated button
```

**CLEO center button:** Circular, 56px, color.sky background, CleoOwl face icon (not full body), elevated above nav bar by 16px. Tap → CLEO chat.

**Active state:** Icon fills + label color becomes color.expedition  
**Inactive state:** Icon outline + label color.stone

---

## 8. Category Filter Chips

**Usage:** Below search bar on Map Explorer.

```
[All] [🏛 Historical] [🎭 Cultural] [🌿 Natural] [🍽 Dining] ...
```

**Default:** Background transparent, border 1px color.smoke, text color.stone  
**Selected:** Background category color at 12% opacity, border category color, text category color  
**Size:** Height 32px, padding horizontal 12px, radius.xs

---

## 9. Suggested Prompt Chips

**Usage:** Above input in CLEO chat.

```
["Plan a 3-day Cairo trip" | "Best time to visit Luxor?" | "Weather in Hurghada"]
```

**Style:** Background color.vellum, text color.ink, border radius.full, no border  
**Tap:** Populates input field and sends immediately

---

## 10. Day Tab Selector

**Usage:** Planner screen, switch between days.

```
[Day 1]  [Day 2]  [Day 3]
```

**Default:** Background transparent, text color.stone  
**Selected:** Background color.expedition at 10%, text color.expedition, bottom border 2px color.expedition  
**Width:** Equal distribution across screen width

---

## 11. Empty State

**Usage:** Home (no trips), Journey (no history), Search (no results).

**Anatomy:**
1. Illustration (120×120, centered)
2. Title (type.headlineMedium, color.ink)
3. Subtitle (type.bodyMedium, color.stone)
4. CTA button ("Plan your first trip" / "Ask CLEO")

**Spacing:** illustration → 16px → title → 8px → subtitle → 24px → CTA

---

## 12. Loading Skeleton (Shimmer)

**Usage:** While POI data, recommendations, or route is loading.

Mimics the layout of the component it replaces:
- POI card skeleton: rectangular block for image + 2 lines for text
- Chat bubble skeleton: rounded rectangle matching bubble size
- Stop card skeleton: full-width rectangle with 3 lines

**Animation:** Shimmer gradient sweeping left-to-right, 1500ms loop, colors: color.smoke → color.paper → color.smoke

---

## Component Count Summary

| Component | Variants | Total |
|-----------|----------|-------|
| POI Card (scroll) | 2 (with/without image) | 2 |
| POI Detail Sheet | 1 | 1 |
| CLEO Chat Bubble | 2 (CLEO/user) | 2 |
| Itinerary Card (inline) | 1 | 1 |
| Region Explainer Card | 1 | 1 |
| Itinerary Stop Card | 1 | 1 |
| Travel Segment | 1 | 1 |
| Bottom Nav Bar | 1 | 1 |
| Category Filter Chip | 8 (by category) | 8 |
| Suggested Prompt Chip | 1 (dynamic text) | 1 |
| Day Tab Selector | 1 (dynamic count) | 1 |
| Empty State | 3 (no trips, no results, error) | 3 |
| Shimmer Skeleton | 4 (card, bubble, stop, list) | 4 |
| Button (primary) | 2 (expedition, sky) | 2 |
| Button (secondary) | 1 (outlined) | 1 |
| Input Field | 1 | 1 |
| Badge (verified/gem) | 2 | 2 |
| Tag Chip | 1 (dynamic) | 1 |
| **Total components** | | **~34** |
