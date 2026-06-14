# VOYO Animation Specification

> Motion language, timing curves, and interaction patterns. Inspired by Kurzgesagt's fluid scene transitions and Teenage Engineering's tactile micro-interactions.

---

## Motion Philosophy

1. **Purposeful, never gratuitous** — Every animation serves a function: guiding attention, confirming action, or maintaining spatial awareness.
2. **Physical, not mechanical** — Objects decelerate naturally (ease-out), spring into place (elastic-out), and maintain momentum across gestures.
3. **Fast enough to feel responsive, slow enough to feel crafted** — Most animations land between 150-400ms.
4. **Staggered reveals over simultaneous** — When multiple items enter, they stagger with 50-100ms delays. This creates rhythm.

---

## Easing Curves

| Curve | Flutter | CSS Equivalent | Usage |
|-------|---------|---------------|-------|
| Standard | `Curves.easeOutCubic` | `cubic-bezier(0.33, 1, 0.68, 1)` | Most transitions |
| Decelerate | `Curves.easeOutQuart` | `cubic-bezier(0.25, 1, 0.5, 1)` | Map zooms, sheet expansions |
| Accelerate | `Curves.easeInCubic` | `cubic-bezier(0.32, 0, 0.67, 0)` | Element exits |
| Spring | `Curves.elasticOut` | N/A | Playful confirmations |
| Linear | `Curves.easeInOut` | `ease-in-out` | Continuous loops (shimmer, typing) |

---

## Transition Catalog

### Screen Transitions

| Transition | Duration | Curve | Notes |
|-----------|----------|-------|-------|
| Tab switch (nav) | 200ms | easeOutCubic | Cross-fade, no slide |
| Push (navigate forward) | 300ms | easeOutCubic | Slide from right |
| Pop (navigate back) | 250ms | easeOutCubic | Slide to right |
| Bottom sheet rise | 350ms | easeOutQuart | From bottom, with slight bounce |
| Bottom sheet dismiss | 250ms | easeInCubic | To bottom |

### Map Animations

| Animation | Duration | Curve | Notes |
|-----------|----------|-------|-------|
| Region zoom (tap region) | 800ms | easeOutQuart | Camera fits region bounds + 80px padding |
| Region highlight | 200ms | easeOutCubic | Polygon opacity: 0.12 → 0.30 |
| Region deselect | 300ms | easeOutCubic | Reverse of highlight |
| Isochrone bloom | 600ms | easeOutQuart | 3 zones stagger: 0ms, 200ms, 400ms |
| Isochrone fade out | 300ms | easeInCubic | All zones fade simultaneously |
| POI marker appear | 200ms | easeOutCubic | Scale from 0.5 → 1.0, staggered 30ms |
| Route polyline draw | 800ms | linear | Animated dash offset |

### Chat Animations

| Animation | Duration | Curve | Notes |
|-----------|----------|-------|-------|
| Bubble appear | 250ms | easeOutCubic | Fade + slight scale (0.9 → 1.0) |
| Streaming text | 30ms/char | linear | Character-by-character reveal |
| Typing indicator | 1200ms loop | easeInOut | 3 dots pulse sequentially |
| Inline card appear | 350ms | easeOutQuart | Expand from collapsed state |
| Suggested chips appear | 200ms | easeOutCubic | Fade in, staggered 50ms |

### Card & List Animations

| Animation | Duration | Curve | Notes |
|-----------|----------|-------|-------|
| Card press | 150ms | easeOutCubic | Scale to 0.98, elevation increase |
| Card release | 150ms | easeOutCubic | Scale back to 1.0 |
| Card enter (scroll) | 200ms | easeOutCubic | Fade + slide up 8px, staggered |
| Drag reorder lift | 200ms | easeOutCubic | Scale to 1.05, elevation to elev.3 |
| Drag reorder drop | 250ms | easeOutCubic | Scale back, settle into position |
| Swipe to delete | 300ms | easeInCubic | Slide off-screen |

### Feedback Animations

| Animation | Duration | Curve | Notes |
|-----------|----------|-------|-------|
| Button press | 100ms | easeOutCubic | Scale to 0.97 |
| Button release | 100ms | easeOutCubic | Scale back to 1.0 |
| Toggle switch | 200ms | easeOutCubic | Knob slides, color cross-fade |
| Checkmark appear | 200ms | easeOutCubic | Scale from 0 → 1 with slight overshoot |
| "Added to trip" confirmation | 400ms | elasticOut | Badge pops in at POI marker |
| Toast/Snackbar | 300ms in, 200ms out | easeOutCubic | Slide up from bottom |
| Shimmer loading | 1500ms loop | linear | Gradient sweep left-to-right |

---

## Isochrone Bloom — Detailed Spec

This is VOYO's signature animation. It must feel like watching ripples expand in water — organic, mesmerizing, and informative.

**Sequence:**

1. **t=0ms** — User long-presses map point. Pulsing dot appears at location.
2. **t=300ms** — First isochrone polygon (30min, teal) begins expanding from center. The polygon scales from 0.3 → 1.0 over 600ms with easeOutQuart. Opacity fades in from 0 → 0.15 (fill) / 0.6 (border).
3. **t=500ms** — Second isochrone (60min, amber) begins same expansion. 200ms stagger.
4. **t=700ms** — Third isochrone (90min, coral) begins same expansion. 200ms stagger.
5. **t=900ms** — All polygons settled. POI markers within each zone pulse once (scale 1.0 → 1.15 → 1.0, 200ms) to draw attention.
6. **t=1000ms** — Bottom sheet slides up with reachable POI counts.

**Clear animation (reverse):**
- All polygons scale to 0 + fade out over 300ms easeInCubic
- POI markers return to default state
- Bottom sheet slides down

---

## Region Zoom — Detailed Spec

**Sequence:**

1. **t=0ms** — User taps inside a region polygon.
2. **t=0-100ms** — Tapped region polygon opacity increases (0.12 → 0.30). Other regions dim (0.12 → 0.05).
3. **t=100-900ms** — Map camera animates to fit region bounds with 80px padding. Duration: 800ms, curve: easeOutQuart.
4. **t=300ms** — POI markers within the region begin appearing (staggered, 30ms each, scale 0.5 → 1.0).
5. **t=900ms** — Region explainer card begins sliding in from right.
6. **t=900-1200ms** — Card slides 300px from right with fade, 300ms easeOutCubic.

**Exit:**
- User taps back or pinch-zooms out.
- Reverse of above: card slides out → camera zooms out → regions reset opacity.
- Duration: 400ms total.

---

## CLEO Streaming — Detailed Spec

**Sequence:**

1. User sends message.
2. User bubble appears (250ms easeOutCubic: fade + scale).
3. Typing indicator appears below CLEO avatar (3 dots pulsing, 1200ms loop).
4. First token arrives from SSE stream.
5. Typing indicator disappears (150ms fade out).
6. CLEO bubble container appears at final height estimate (200ms easeOutCubic).
7. Text renders character-by-character at 30ms/char. Cursor blinks at end of text.
8. When streaming completes, cursor disappears.
9. If `[PLANNER]` token detected:
   - Text before token renders normally.
   - Inline itinerary card expands into the bubble (350ms easeOutQuart).
   - "[PLANNER]" token is consumed (not displayed to user).

---

## Reduced Motion

When `MediaQuery.disableAnimations` is true or user has `prefers-reduced-motion`:

- All animations become instant (0ms duration).
- Isochrone polygons appear without bloom.
- Map zooms are instant cuts.
- Chat messages appear fully rendered (no streaming effect).
- Shimmer is replaced with static gray placeholder.
- Touch feedback (press/release scale) is disabled.
