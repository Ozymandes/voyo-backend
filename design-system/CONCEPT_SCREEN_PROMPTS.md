# VOYO Concept Screen Prompts

> Ready-to-use prompts for generating concept screens with ChatGPT, Midjourney, DALL·E, or Nano Banana.
> Copy-paste the full prompt text. Adjust screen dimensions as needed.

---

## 1. Home Screen — Light Mode

```
Generate a mobile app home screen mockup for "VOYO", an Egyptian travel app.

Screen dimensions: iPhone 15 (393×852 pixels, 19.5:9 ratio).

Layout from top to bottom:
1. Status bar (time, signal, battery)
2. Greeting section: "Ahlan, Ahmed! 👋" in bold, warm dark text on cream background. Subtitle: "Ready to explore Egypt?" in smaller muted text.
3. "Recommended for You" section header with a horizontal scroll of 4 POI cards below it. Each card is ~160px wide with: a hero image (warm desert photo), a rating badge (⭐ 4.7), POI name, category label, and a match reason like "Love ancient history" in italic purple text.
4. "Explore by Region" section with a simplified map of Egypt showing 8 colored, semi-transparent polygon overlays for regions (red for Cairo, blue for Alexandria, purple for Luxor, green for Aswan, orange for Giza, teal for Hurghada, etc.)
5. "Your Trips" section with one itinerary card: "3 Days in Cairo" showing day summaries.
6. Bottom navigation bar with 4 items: Home (house icon), Map (folded map icon), CLEO (cute blue owl face icon, slightly larger and elevated), and Planner (checklist icon). The CLEO button is the center, elevated above the bar.

Color palette: Warm cream background (#F7F5F1), warm red-orange CTAs (#D45028), sky blue brand color (#1C72B4), discovery purple (#8860D4), near-black text (#1A1714), warm gray secondary text (#6A6058).

Typography: Clean geometric sans-serif (like Outfit or Inter). 
Style: Scandinavian precision meets Kurzgesagt warmth. Information-rich but not cluttered. Feels like a crafted, premium travel app.
```

---

## 2. Map Explorer — Isochrone Visualization

```
Generate a mobile app screen showing an interactive map of Egypt with isochrone reachability visualization.

Screen dimensions: iPhone 15 (393×852 pixels).

Layout:
1. Full-screen map using warm, muted OpenStreetMap-style tiles (not the default harsh OSM colors — think warm parchment tones).
2. The map shows the Cairo/Giza area at medium zoom.
3. Three concentric, organic blob-shaped polygons expanding from a central point:
   - Inner zone (30 min): Teal (#0D9488) at 15% opacity fill, 60% opacity border
   - Middle zone (60 min): Amber (#D97706) at 15% opacity fill, 60% opacity border  
   - Outer zone (90 min): Coral (#EA580C) at 15% opacity fill, 60% opacity border
4. Small POI marker pins scattered within the zones, color-coded to match their zone.
5. A pulsing dot at the center point (the origin).
6. Top: A search bar with rounded corners and a magnifying glass icon.
7. Below search: Category filter chips (Historical, Cultural, Natural, Dining, etc.)
8. Bottom-right: A floating compass button labeled "Explore from here"
9. Bottom: A sliding sheet showing "12 places within 30 min · 24 within 60 min · 38 within 90 min"

Style: Like a Kurzgesagt video illustration come to life. Colorful, clean, educational but playful. The map should feel warm and inviting, not clinical.
```

---

## 3. CLEO Chat — Itinerary Response

```
Generate a mobile app chat interface screen for "VOYO" travel app.

Screen dimensions: iPhone 15 (393×852 pixels).

Layout:
1. Status bar at top.
2. Header: "← CLEO" with a gear icon on the right. Below the title is a subtle divider.
3. Chat messages:
   - CLEO's first message (left-aligned, warm parchment #F0EBE3 background): "Ahlan! I'm CLEO, your Egypt travel companion. Where shall we explore today?" with a small cute blue owl avatar above it.
   - User message (right-aligned, sky blue #1C72B4 background, white text): "Plan a 3-day trip to Cairo"
   - CLEO's long response (left-aligned, multiple connected bubbles): A detailed response about a Cairo itinerary, with bold headers like "**Day 1 — Ancient Wonders**" and bullet points listing POIs with practical tips. Uses markdown formatting rendered in the app.
   - An inline itinerary card: A white card with a border showing "📋 Your Itinerary is Ready!" header, "3 Days in Cairo" title, day summaries (Day 1: Ancient Wonders, Day 2: Islamic Cairo, Day 3: Museums & Markets), and two buttons: "View Optimized Plan" (filled blue) and "Adjust" (outlined).
4. Above the input bar: 3 suggested prompt chips: "Best time to visit Luxor?", "Weather in Hurghada", "Tell me about the Sphinx"
5. Input bar at bottom: Paperclip icon on left, text field "Type your message...", send arrow icon on right.

Color palette: Cream background (#F7F5F1), parchment chat bubbles (#F0EBE3), sky blue user bubbles (#1C72B4), warm red-orange buttons (#D45028).
The owl mascot is a simple, cute blue owl with ear tufts, cream face, and amber beak — flat illustration style.
```

---

## 4. POI Detail Sheet

```
Generate a mobile app bottom sheet UI showing detailed information about an Egyptian tourist attraction.

Screen dimensions: iPhone 15 (393×852 pixels).

Layout — this is a bottom sheet covering 70% of the screen, with the map visible behind it at the top:

1. The sheet has rounded top corners (20px radius) and a small drag handle at the top center.
2. Hero image: A stunning photo of the Great Pyramid of Giza filling the full width, ~220px tall, with a gradient overlay at the bottom fading to white.
3. Below image:
   - Title: "Great Pyramid of Giza" in large bold text (#1A1714)
   - Arabic name: "هرم خوفو" in smaller muted text (#6A6058)
   - Category + region badge: "🏛 Historical · Giza" in a small chip with terracotta background
4. Quick facts row — 3 equal columns:
   - ⭐ 4.7 (rating)
   - ⏱ 3 hours (visit duration)
   - 💰 200 EGP (ticket price)
5. Expandable sections:
   - "Opening Hours" with a chevron, showing "Monday: 8:00 AM – 5:00 PM"
   - "Historical Significance" with expanded text about the pyramid
   - "Travel Tips" with 3 tips: early arrival, bring water, comfortable shoes
6. Tags row: [UNESCO] [Ancient] [Must-See] [Iconic] in small rounded chips
7. Sticky bottom action bar (3 equal buttons):
   - "Ask CLEO" (with owl icon)
   - "Add to Trip" (with plus icon)
   - "Navigate" (with arrow icon)

Color palette: White card background, cream behind, terracotta category color (#B45309), warm red-orange CTA (#D45028), brand blue accents (#1C72B4).
Clean, warm, information-rich but not overwhelming. Scandinavian layout precision.
```

---

## 5. Itinerary Planner — Day View

```
Generate a mobile app screen showing an optimized trip itinerary for Cairo.

Screen dimensions: iPhone 15 (393×852 pixels).

Layout:
1. Header: "← Your Trip" back button, title "3 Days in Cairo" in bold text.
2. Day tab selector: [Day 1] [Day 2] [Day 3] — "Day 1" is selected with a warm red-orange underline and light background tint.
3. Day theme: "Ancient Wonders" in medium-weight text below tabs.
4. Scrollable stop list:
   - Stop card 1 (09:00): "📍 Great Pyramid of Giza" — "Visit: 3 hours · Ticket: 200 EGP" — "💡 Go early to beat crowds". White card with subtle shadow.
   - Travel segment: "⬇ 25 min drive (12.4 km)" in small gray text with a thin connecting line.
   - Stop card 2 (12:00): "📍 Great Sphinx" — "Visit: 1 hour · Ticket: 180 EGP"
   - Travel segment: "⬇ 15 min drive (6.2 km)"
   - Stop card 3 (13:30): "🍽️ Lunch at Abu Shakra" — "Local Egyptian cuisine"
5. Day summary bar: "85 min travel · 620 EGP total"
6. Bottom action bar: [Reorder Stops] [Re-optimize] [Save Trip] — 3 outlined buttons.

Color palette: Cream background (#F7F5F1), white cards, warm red-orange accents (#D45028), brand blue travel segments (#1C72B4), muted gray secondary text (#6A6058).
Clean, structured, Scandinavian layout. Feels organized and trustworthy.
```

---

## 6. Map Explorer — Region Zoomed (Aswan)

```
Generate a mobile app screen showing a zoomed-in map of the Aswan region of Egypt.

Screen dimensions: iPhone 15 (393×852 pixels).

Layout:
1. Full-screen warm-toned map showing the Aswan area, with a green semi-transparent polygon overlay highlighting the Aswan region boundaries.
2. POI marker pins visible within the region: a mix of category-coded pins (historical = pyramid silhouette, cultural = mask, natural = leaf).
3. A region explainer card sliding in from the right side (covering ~70% of width):
   - Region icon: A palm tree icon in green
   - Title: "Aswan" in large bold text
   - Arabic: "أسوان" in smaller text
   - Description: "Southern gateway to Nubia" in italic
   - Stats: "24 POIs · 12 historical · 6 cultural"
   - Mini POI cards: "Abu Simbel ⭐ 4.8" and "Philae Temple ⭐ 4.7" side by side
   - Two CTA buttons: "Explore POIs" (filled green) and "Ask CLEO about Aswan" (outlined with owl icon)
4. Back arrow in top-left corner.
5. Search bar at top.

Colors: Green region overlay (#2A7A50), warm cream card (#FFFFFF), green accents (#059669), warm map tiles.
Style: Kurzgesagt map illustration style — colorful regions on a muted geographic base. Playful but informative.
```

---

## 7. Dark Mode — Home Screen

```
Generate a mobile app home screen mockup for "VOYO" travel app in dark mode.

Screen dimensions: iPhone 15 (393×852 pixels).

Same layout as the light mode home screen but with dark theme:
- Background: Deep warm charcoal (#121110) — NOT pure black, has warm brown undertone
- Cards: Dark warm surface (#1E1C18) with subtle borders (#2E2B26)
- Text: Light warm white (#F5F3EF) for primary, muted warm gray (#9A938A) for secondary
- Brand colors remain vibrant: expedition red (#D45028), sky blue (#1C72B4), discovery purple (#8860D4)
- The mini map of Egypt shows dark-mode map tiles (dark gray/blue tones)
- POI images remain full-color and bright against the dark cards
- CLEO owl in the nav bar stays sky blue — pops against dark background
- No harsh shadows — borders define elevation instead

Overall feel: Premium, OLED-friendly, warm and cozy. Like Spotify's dark mode but with warmer undertones. Feels like a luxury travel app at night.
```

---

## 8. Onboarding — Step 1 (Travel Style)

```
Generate a mobile app onboarding screen for "VOYO" Egyptian travel app.

Screen dimensions: iPhone 15 (393×852 pixels).

Layout:
1. Status bar at top.
2. Skip button in top-right corner.
3. Progress indicator: 4 small dots at the top, first one filled (current step).
4. Title: "How do you like to travel?" in large bold text.
5. Subtitle: "Pick the style that feels most like you" in smaller muted text.
6. Four visual style cards in a 2×2 grid, each ~170px wide:
   - "Adventurer" — icon of a mountain + compass, warm red accent (#D45028)
   - "Culture Seeker" — icon of a museum column, purple accent (#8860D4)
   - "Relaxer" — icon of a sun + wave, sky blue accent (#1C72B4)
   - "Explorer" — icon of a magnifying glass + globe, green accent (#2A7A50)
   Each card has: the icon illustration at top, the style name below, and a subtle selection ring.
7. "Adventurer" card is shown as selected (brighter, border highlight, slight scale).
8. Bottom: "Continue" button in warm red-orange (#D45028), full width with rounded corners.

Background: Warm cream (#F7F5F1).
Style: Kurzgesagt-inspired flat illustration for the icons. Playful, warm, inviting. Each style card has a small flat illustration representing that travel personality.
```

---

## How to Use These Prompts

1. Copy the full prompt text from any section above
2. Paste into ChatGPT (with DALL·E), Midjourney, DALL·E standalone, or Nano Banana
3. For Midjourney: add `--ar 19.5:9` for iPhone aspect ratio, `--v 6` for latest model
4. Generated images should be saved to `design-system/concept-screens/` with descriptive filenames
5. Reference concept screens during Phase III Flutter implementation
