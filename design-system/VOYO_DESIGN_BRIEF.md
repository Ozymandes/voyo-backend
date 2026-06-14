# VOYO — Comprehensive Design Brief & Technical Specification

> **Version:** 1.0  
> **Date:** June 2025  
> **Purpose:** Complete reference for AI image generators (ChatGPT, Midjourney, DALL·E, Nano Banana), UI implementation (Pi skills), and design system creation.  
> **Audience:** Designers, AI art tools, frontend engineers, and anyone building VOYO's visual identity.

---

## 1. What Is VOYO?

**VOYO** is an AI-powered Egyptian travel planning platform — a graduate thesis project that combines:

- **CLEO** — an agentic AI travel guide (Cairo Local Expert & Operator) that converses with users, learns their preferences, curates POIs, and builds optimized multi-day itineraries
- **200+ Egyptian POIs** — a verified, enriched database of historical sites, cultural landmarks, natural wonders, restaurants, and experiences across 8 regions of Egypt
- **Intelligent routing** — Valhalla + VROOM-powered isochrone visualization and deterministic route optimization
- **Personalized recommendations** — a profile-aware recommendation engine that scores and surfaces POIs based on learned user preferences

VOYO is not a generic travel app. It is specifically about **Egypt**, built with genuine depth and care for the country's history, culture, and people. CLEO speaks with authentic warmth — using Arabic phrases naturally, sharing real insider knowledge, and treating every traveler like a friend visiting for the first time.

### The Name
VOYO evokes **voyage**, **joy**, and the **open road**. It should feel adventurous, warm, and optimistic — like a trusted companion for exploration.

### The Mascot
**CLEO** is represented as a stylized owl (currently implemented as a `CustomPaint` widget). The owl symbolizes wisdom, knowledge, and watchfulness — fitting for an AI guide. The current implementation uses the app's sky-blue brand color (`#1C72B4`) for the body with warm cream (`#EDE8DC`) face detail.

---

## 2. Design & Creative Philosophy

### 2.1 Core Aesthetic: "Kurzgesagt Meets Scandinavian Craft"

VOYO's visual identity lives at the intersection of two design traditions:

**Kurzgesagt — In a Nutshell** (illustrative/playful layer):
- Rich, confident color palettes — not pastel, not neon, but **saturated and joyful**
- Flat illustrative style with clean geometric forms and clear silhouettes
- Information density that respects the viewer — detailed without being overwhelming
- Playful without being childish — there's sophistication in the simplicity
- Maps and geographic visualization that feel alive, not clinical
- Character design (CLEO owl) that's expressive and warm

**Scandinavian Craft** (structural/elegant layer — Spotify, Teenage Engineering):
- Monochromatic restraint where it matters — typography, layout grids, negative space
- Intentional use of white space as a design element, not an afterthought
- Micro-interactions that feel physical and satisfying (haptic-like feedback in UI)
- Hardware-grade attention to alignment, spacing, and visual rhythm
- Innovation in interaction patterns — things behave in unexpected but delightful ways
- Dark mode that feels premium, not just inverted

**The synthesis:** Information-rich where Kurzgesagt shines (map explorer, POI cards, isochrone visualization, CLEO's personality). Refined and restrained where Scandinavian design excels (navigation, settings, itinerary planner, empty states). The two meet in the middle: playful interactions delivered with craft-level precision.

### 2.2 Design Principles

1. **Crafted Object, Not Just an App** — Every screen should feel like something that was *made*, not generated. The care should be visible in spacing, animation curves, and typographic choices.

2. **Progressive Depth** — Simple on the surface, rich underneath. A POI card looks clean until you expand it. The map looks simple until you tap "Explore from here" and the isochrone bloom appears. CLEO's chat looks minimal until it renders an itinerary card inline.

3. **Warm Intelligence** — The app should feel like it *knows* things and *wants* to share them. Not a cold database, not a chatty robot — a knowledgeable friend who's genuinely excited to show you around.

4. **Geographic Storytelling** — The map is the hero. Egypt's geography is inherently dramatic (Nile valley, Red Sea coast, Western Desert, Sinai mountains). The map visualization should make users *feel* that drama through color, layering, and animation.

5. **Cultural Authenticity** — Arabic typography, Egyptian color references (desert gold, Nile blue, papyrus cream), and genuine cultural representation — not tourist-brochure pastiche.

6. **Quiet Confidence** — No splash screens, no onboarding carousels, no gamification badges. The app is confident enough to let its utility speak. Animations are smooth and purposeful, never gratuitous.

7. **Open & Playful** — VOYO is an open platform. The UI should encourage exploration, serendipity, and "what if" moments. The isochrone explorer, the "Ask CLEO" deep-links, the region borders that invite tapping — everything says "go ahead, poke around."

### 2.3 What VOYO Is NOT

- Not a booking app (no flight/hotel booking)
- Not a social platform (no feeds, followers, or reviews from other users)
- Not a generic travel guide (Egypt only, with genuine depth)
- Not a gamified experience (no points, badges, or streaks)
- Not corporate or startup-bro aesthetic (no gradients-as-brand, no tech buzzwords)
- Not minimalist to the point of coldness (warmth > sterility)

---

## 3. Technical Architecture (What's Under the Hood)

### 3.1 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Flutter (Dart) | Cross-platform mobile + web |
| **Backend** | FastAPI (Python) | API server, CLEO agent, orchestration |
| **Database** | Supabase (PostgreSQL) | POIs, users, itineraries, profiles, auth |
| **AI Agent** | CLEO (Groq-hosted LLM with tools) | Conversational guide + itinerary curation |
| **Routing** | Valhalla (Docker) | Isochrone computation, route polygons |
| **Optimization** | VROOM (Docker) | Deterministic TSP/VRP solving for itineraries |
| **Auth** | Supabase Auth | Email/password, JWT, RLS |
| **Maps** | flutter_map + OpenStreetMap | Free, no Google Maps SDK dependency |
| **Cache** | Redis | Semantic cache for CLEO responses |
| **Search** | Tavily | Web search for current events |

### 3.2 Database Overview

**8 Egyptian Regions:** Cairo, Giza, Alexandria, Luxor, Aswan, Hurghada, Marsa Alam, Sinai

**200+ POIs** with rich data:
- Core: name, name_arabic, category, coordinates, address
- Content: description, historical_significance, tags
- Media: image_urls (5 photos per POI from Google Places)
- Metrics: average_rating, total_reviews, popularity_score
- Logistics: opening_hours (JSONB), ticket_price (EGP), average_visit_duration
- Status: is_active, is_verified
- Nearby POI references, accessibility info, special deals

**User Profiles** (agentic):
- Demographics: full_name, home_country, age_range
- Travel preferences: travel_style (JSONB), interest_scores (JSONB), itinerary_pace, planning_style
- Learned: mobility_preference, comfort_level, favorite_cuisines, dietary_restrictions, chronotype, budget, price_sensitivity
- Companions: typical_companions (JSONB — solo/couple/family/group)

**Itineraries:**
- Header: title, region, status (draft/current/completed), dates, budget
- Items: poi_id, day_number, sequence_order, start_time, end_time
- Agent metadata: agent_suggested, user_rating, agent_notes

### 3.3 API Endpoints

```
POST   /api/v1/chat                          # CLEO conversation (streaming SSE)
POST   /api/v1/itinerary/curate              # LLM curates POIs from user request
POST   /api/v1/itinerary/optimize            # VROOM optimizes into day-by-day schedule
GET    /api/v1/itinerary/{id}                # Full itinerary with items
POST   /api/v1/itinerary                     # Create itinerary
PUT    /api/v1/itinerary/{id}                # Update metadata
DELETE /api/v1/itinerary/{id}                # Delete
PUT    /api/v1/itinerary/{id}/reoptimize     # Re-run VROOM after manual edits

GET    /api/v1/pois?bounds=&category=&search= # POI search with spatial + category filters
GET    /api/v1/pois/{id}                     # Full POI details

GET    /api/v1/routing/distance-matrix       # Valhalla distance matrix
POST   /api/v1/routing/isochrone             # Reachable area polygons
GET    /api/v1/routing/route?waypoints=      # Turn-by-turn route polyline

GET    /api/v1/recommendations               # Personalized POI suggestions with match_reasons
GET    /api/v1/recommendations/context        # CLEO context string for current user

GET    /api/v1/weather/{city}                # Current weather data
POST   /api/v1/profile/preferences           # Update preferences (from CLEO learning)
GET    /api/v1/profile                       # User profile
PUT    /api/v1/profile                       # Update profile
GET    /api/v1/profile/preferences           # Get preference fields

GET    /health                               # Health check
```

### 3.4 CLEO's Agentic Architecture

CLEO is a genuine tool-calling agent with:

1. **Gate Layer** — Safety filter, scope detector, response complexity classifier (no LLM needed)
2. **Agent Core** — Single LLM call with tool access. The LLM decides which tools to call, how many times, in what order. Tools include:
   - `search_pois` — Vector + keyword RAG search over 200+ POIs
   - `get_poi_details` — Full POI data with hours, prices, history
   - `get_weather` — Current conditions by city
   - `search_web` — Tavily web search for current events
   - `update_user_preference` — Saves explicit user preferences to profile
   - `curate_itinerary` — Packages POI IDs for VROOM optimization
3. **Persistent Memory** — Conversation history in Supabase, not in-memory
4. **Profile Awareness** — CLEO reads user profile on every message for personalization
5. **Profile Learning** — CLEO silently updates user preferences when users express strong opinions
6. **Itinerary Pipeline** — CLEO curates → VROOM optimizes → Narrative wrapper enriches

---

## 4. Screens & User Flows

### 4.1 Screen Map

```
┌─────────────────────────────────────────────────────────────────┐
│                        VOYO SCREEN MAP                          │
│                                                                 │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐                   │
│  │  Splash  │──▶│  Login   │──▶│ Register │                   │
│  └──────────┘   └──────────┘   └──────────┘                   │
│                       │                                         │
│                       ▼                                         │
│                 ┌──────────┐                                    │
│                 │Onboarding│  (preference questionnaire)        │
│                 └──────────┘                                    │
│                       │                                         │
│                       ▼                                         │
│  ┌─────────────────────────────────────────────────────┐       │
│  │                    MAIN SHELL                        │       │
│  │                                                      │       │
│  │  ┌─────────┐ ┌─────────┐ ┌──────┐ ┌──────────────┐ │       │
│  │  │  Home   │ │  Map    │ │ CLEO │ │  Planner     │ │       │
│  │  │  Screen │ │Explorer │ │ Chat │ │  Screen      │ │       │
│  │  └─────────┘ └─────────┘ └──────┘ └──────────────┘ │       │
│  │       │          │          │           │            │       │
│  │       ▼          ▼          ▼           ▼            │       │
│  │  ┌─────────┐ ┌─────────┐ ┌──────┐ ┌──────────────┐ │       │
│  │  │  POI    │ │Region   │ │Itin. │ │  Journey     │ │       │
│  │  │  Detail │ │Explorer │ │Card  │ │  History     │ │       │
│  │  │  Sheet  │ │Card     │ │(inline)│  (trips list)│ │       │
│  │  └─────────┘ └─────────┘ └──────┘ └──────────────┘ │       │
│  └─────────────────────────────────────────────────────┘       │
│                       │                                         │
│                       ▼                                         │
│                 ┌──────────┐                                    │
│                 │ Settings │  (profile, prefs, about)           │
│                 └──────────┘                                    │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Screen-by-Screen Specification

---

#### A. Authentication Flow

**Splash Screen**
- VOYO logo mark + wordmark centered on warm cream background (`#F7F5F1`)
- Subtle animation: logo fades in, then gently pulses once
- Duration: 2 seconds, auto-transition to Login
- Dark mode: deep charcoal (`#1A1714`) background

**Login Screen**
- Clean card layout on `page` background
- Email + password fields with floating labels
- "Sign In" button in `expedition` red (`#D45028`)
- "New here? Create account" link
- CleoOwl mascot peeking from top corner (subtle, friendly)
- Error states with clear inline messaging (no alert dialogs)

**Register Screen**
- Same card style as login
- Fields: full name, email, password, confirm password
- "Create Account" primary button
- Already have account? link
- Success → auto-navigate to Onboarding

**Onboarding Screen**
- Multi-step preference questionnaire (3-4 steps)
- Step 1: Travel style selection (visual cards: Adventurer, Culture Seeker, Relaxer, Explorer)
- Step 2: Interest sliders (history, nature, food, art, adventure, spirituality)
- Step 3: Pace preference (Slow & Flexible / Balanced / Packed Schedule)
- Step 4: Companions (Solo / Couple / Family / Group)
- Progress indicator: minimalist dots or thin progress bar
- Skip option on each step (CLEO can learn later)
- Completion → Home Screen

---

#### B. Home Screen

**Purpose:** Personalized landing page that immediately shows value.

**Layout:**
```
┌─────────────────────────────────────────────┐
│  Ahlan, [Name]! 👋                           │  ← Greeting with user's name
│  Ready to explore Egypt?                     │  ← Dynamic subtitle
│                                              │
│  ── Recommended for You ─────────────────── │  ← Section header
│  [Card] [Card] [Card] [Card] → scroll →    │  ← Horizontal POI cards
│                                              │
│  ── Explore by Region ───────────────────── │
│  ┌──────────────────────────────────────┐   │
│  │     Interactive mini-map of Egypt     │   │  ← Tappable regions
│  │     with colored region borders       │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  ── Your Trips ─────────────────────────── │
│  [Trip card: Cairo 3-day]                   │
│  [Trip card: Luxor weekend]                 │
│                                              │
│  ── Quick Actions ──────────────────────── │
│  [Ask CLEO]  [Explore Map]                  │
│                                              │
│  [🏠 Home]  [🗺 Map]  [🦉 CLEO]  [📋 Plan] │  ← Bottom nav
└─────────────────────────────────────────────┘
```

**Key Details:**
- Greeting changes based on time of day (morning/afternoon/evening) with Arabic phrases
- "Recommended for You" calls `GET /api/v1/recommendations` — each card shows match_reason ("Because you love ancient history")
- POI cards: image + name + category badge + rating + match reason
- Mini-map: simplified Egypt outline with 8 colored region polygons (tappable)
- "Your Trips": itinerary cards with status badge (draft/current/completed)
- Empty states are designed (no "no trips yet" text — show illustration + CTA)

**Recommendation Card Anatomy:**
```
┌──────────────┐
│  [Hero Image] │  ← Supabase image_urls, or category gradient fallback
│               │
│  ⭐ 4.7       │  ← Rating badge, bottom-left of image
│               │
│  Abu Simbel   │  ← POI name, max 1 line, truncated
│  Historical   │  ← Category label in muted text
│               │
│  "Love ancient │  ← Match reason from recommendation engine
│   history"    │
└──────────────┘
```

---

#### C. Map Explorer (Signature Feature)

**Purpose:** The most distinctive screen in the app. An interactive map of Egypt that makes geography feel alive.

**States:**

1. **Default State** — Full Egypt view with:
   - 8 colored, semi-transparent region polygon overlays
   - POI markers clustered by density
   - User location indicator (if permitted)
   - Floating "🧭 Explore from here" button (bottom-right)
   - Search bar at top
   - Category filter chips below search bar

2. **Region Zoomed State** — Tapping a region:
   - Animated camera zoom to region bounds (800ms ease-out)
   - Region polygon highlights (opacity increases)
   - Region Explainer Card slides in from right:
     - Region name (English + Arabic)
     - One-line poetic description
     - POI count by category ("24 POIs · 12 historical · 6 cultural")
     - Top 2-3 POI cards (mini version)
     - Two CTAs: "Explore POIs" + "Ask CLEO about [Region]"
   - POI markers appear within zoomed bounds

3. **Isochrone Explorer State** — Long-press map or tap "Explore from here":
   - Loading pulse animation at selected point
   - Concentric polygons fade in: 30min / 60min / 90min reachability zones
   - Zone colors: 30min = deep teal, 60min = warm amber, 90min = soft coral
   - POIs within each zone are highlighted with zone color
   - Bottom sheet: "12 places within 30 min · 24 within 60 min · 38 within 90 min"
   - "Clear" button removes overlay

4. **POI Detail State** — Tapping a POI marker:
   - POI Detail Sheet rises from bottom (DraggableScrollableSheet, 70% initial)
   - Can expand to 95% for full detail
   - See POI Detail Sheet spec below

**Map Visual Design:**
- Map tiles: OpenStreetMap with a warm, muted style (not default OSM colors)
- Region overlays: Each region has a signature color from a curated palette
- Isochrone polygons: Soft, organic shapes with gradient fills
- POI markers: Category-coded pins with clean silhouettes (not Google Maps default)
- Route polylines: Animated dashed lines showing travel path
- The map should feel like a **Kurzgesagt illustration come to life** — colorful, clear, information-rich but never cluttered

**Region Color Palette (8 regions):**
| Region | Color | Rationale |
|--------|-------|-----------|
| Cairo | `#D45028` (Expedition Red) | Bustling, energetic capital |
| Giza | `#C4622A` (Terra) | Ancient monuments, desert warmth |
| Alexandria | `#1C72B4` (Sky Blue) | Mediterranean coast |
| Luxor | `#8860D4` (Discovery Purple) | Mystical, treasure-filled |
| Aswan | `#2A7A50` (Verified Green) | Nile, lush, Nubian culture |
| Hurghada | `#0EA5E9` (Ocean Blue) | Red Sea resorts |
| Marsa Alam | `#0891B2` (Teal) | Diving, marine life |
| Sinai | `#7C3AED` (Mountain Violet) | Sacred peaks, dramatic terrain |

---

#### D. POI Detail Sheet

**Purpose:** Rich, contextual POI information — the "everything you need" card.

**Layout (scrollable):**
```
┌─────────────────────────────────────────┐
│  ┌─────────────────────────────────┐    │
│  │         Hero Image              │    │  ← Supabase image_urls
│  │         (with gradient fade)    │    │
│  └─────────────────────────────────┘    │
│                                          │
│  Great Pyramid of Giza                   │  ← Name (bold, large)
│  هرم خوفو                                │  ← Arabic name (muted)
│  🏛 Historical · Giza                    │  ← Category + region badge
│                                          │
│  ┌──────┐ ┌──────┐ ┌──────┐            │
│  │⭐ 4.7│ │⏱ 3hr │ │💰200 │            │  ← Quick facts row
│  │rating│ │visit │ │ EGP  │            │
│  └──────┘ └──────┘ └──────┘            │
│                                          │
│  ── Opening Hours ──────────────────    │  ← Expandable section
│  Monday: 8:00 AM – 5:00 PM              │
│  Tuesday: 8:00 AM – 5:00 PM             │
│  ...                                     │
│                                          │
│  ── Historical Significance ────────    │
│  Built around 2560 BC as a tomb for     │
│  Pharaoh Khufu, the Great Pyramid       │
│  was the tallest structure on Earth      │
│  for over 3,800 years...                 │
│                                          │
│  ── Travel Tips ────────────────────    │
│  🕐 Go early morning to beat crowds     │
│  💧 Bring plenty of water               │
│  👟 Wear comfortable walking shoes       │
│                                          │
│  ── Tags ───────────────────────────    │
│  [UNESCO] [Ancient] [Must-See] [Iconic] │
│                                          │
│  ══════════════════════════════════════  │
│  [Ask CLEO]  [Add to Trip]  [Navigate]  │  ← Sticky action bar
└─────────────────────────────────────────┘
```

**Interaction Details:**
- "Ask CLEO" → navigates to CLEO chat with preloaded prompt about this POI
- "Add to Trip" → adds to current itinerary or prompts to create one
- "Navigate" → opens Google Maps for turn-by-turn navigation
- Image carousel if multiple images exist
- Verified badge (✓) for verified POIs
- "Hidden Gem" badge for high-quality but low-popularity POIs

---

#### E. CLEO Chat Screen

**Purpose:** The conversational heart of VOYO. Where users plan trips, learn about Egypt, and build a relationship with their AI guide.

**Layout:**
```
┌─────────────────────────────────────────────┐
│  [←] CLEO                          [⚙]     │  ← Header with settings
│  ────────────────────────────────────────── │
│                                              │
│  🦉                                          │  ← CleoOwl avatar
│  Ahlan! I'm CLEO, your Egypt travel         │  ← CLEO message bubble
│  companion. Where shall we explore today?    │     (left-aligned, warm bg)
│                                              │
│         Tell me about the Pyramids           │  ← User message bubble
│                                              │     (right-aligned, accent bg)
│  🦉                                          │
│  Ah, the Great Pyramids! Let me share        │  ← Streaming text appears
│  their incredible story...                   │     word by word
│                                              │
│  Built over 4,500 years ago as eternal       │
│  tombs for pharaohs...                       │  ← Markdown rendered:
│                                              │     bold, lists, headers
│  **Pro tip:** Go early to beat the crowds!   │
│                                              │
│  ┌─ 📋 Your Itinerary is Ready! ────────┐  │  ← Inline itinerary card
│  │  3 Days in Cairo                      │  │     (triggered by [PLANNER])
│  │  Day 1: Ancient Wonders               │  │
│  │  Day 2: Islamic Cairo                  │  │
│  │  Day 3: Museums & Markets             │  │
│  │                                        │  │
│  │  [View Optimized Plan]  [Adjust]       │  │
│  └────────────────────────────────────────┘  │
│                                              │
│  ────────────────────────────────────────── │
│  [📎]  Type your message...          [➤]    │  ← Input bar
└─────────────────────────────────────────────┘
```

**Key Features:**
- **Streaming responses** — text appears incrementally (SSE from backend)
- **Markdown rendering** — bold, italic, lists, headers via flutter_markdown
- **Inline itinerary cards** — when CLEO returns `[PLANNER]` token
- **Context-aware** — "Ask CLEO" from a POI preloads a question about that POI
- **Suggested prompts** — quick-tap chips above input ("Plan a 3-day Cairo trip", "Best time to visit Luxor", "What's the weather in Hurghada?")
- **Conversation history** — persists across sessions (Supabase)
- **Typing indicator** — animated dots when CLEO is "thinking"

**CLEO Bubble Design:**
- Left-aligned
- Background: `vellum` (#F0EBE3) — warm parchment tone
- Avatar: CleoOwl (small, top-left of first bubble in sequence)
- Text: `ink` (#1A1714) for readability
- Rounded corners: top-left sharp, others rounded (chat bubble convention)

**User Bubble Design:**
- Right-aligned
- Background: `sky` (#1C72B4) — brand blue
- Text: white
- Rounded corners: top-right sharp, others rounded

---

#### F. Itinerary Planner Screen

**Purpose:** View, edit, and optimize multi-day trip plans.

**Layout:**
```
┌─────────────────────────────────────────────┐
│  [←] Your Trip                              │
│  3 Days in Cairo                            │
│  ────────────────────────────────────────── │
│                                              │
│  [Day 1] [Day 2] [Day 3]                    │  ← Day tabs (colored)
│  ────────────────────────────────────────── │
│  Theme: Ancient Wonders                      │
│                                              │
│  ┌─ 09:00 ──────────────────────────────┐  │
│  │  📍 Great Pyramid of Giza             │  │  ← Stop card
│  │  Visit: 3 hours · Ticket: 200 EGP    │  │
│  │  Tip: Go early to beat crowds         │  │
│  └───────────────────────────────────────┘  │
│         ⬇ 25 min drive (12.4 km)            │  ← Travel segment
│  ┌─ 12:00 ──────────────────────────────┐  │
│  │  📍 Great Sphinx                      │  │
│  │  Visit: 1 hour · Ticket: 180 EGP     │  │
│  └───────────────────────────────────────┘  │
│         ⬇ 15 min drive (6.2 km)             │
│  ┌─ 13:30 ──────────────────────────────┐  │
│  │  🍽️ Lunch at Abu Shakra              │  │
│  └───────────────────────────────────────┘  │
│                                              │
│  Day totals: 85 min travel · 620 EGP         │
│                                              │
│  ────────────────────────────────────────── │
│  [Reorder Stops]  [Re-optimize]  [Save]     │  ← Action bar
└─────────────────────────────────────────────┘
```

**Key Features:**
- Day tabs with color coding
- Drag-to-reorder stops (triggers re-optimization via VROOM)
- Travel segments show time + distance between stops
- Mini map per day showing route polyline
- Day totals (travel time, cost, visit duration)
- "Re-optimize" button sends updated stop order to VROOM
- Save creates/updates itinerary in Supabase

---

#### G. Journey Screen (Trip History)

**Purpose:** View all past and planned trips.

**Layout:**
- List of itinerary cards sorted by date
- Each card shows: title, dates, region, status badge, POI count
- Status: Draft (gray), Current (accent), Completed (verified green)
- Tap card → navigates to Planner Screen for that trip
- Empty state: illustration + "Ask CLEO to plan your first trip"

---

#### H. Settings / Profile Screen

**Purpose:** Manage preferences, profile, and app settings.

**Sections:**
- Profile: name, email, avatar placeholder
- Travel Preferences: visual edit of onboarding choices
- Notification settings
- Language (English/Arabic — future)
- Theme toggle (Light/Dark)
- About VOYO (version, credits)
- Sign Out

---

### 4.3 Cross-Cutting Interactions

**POI → CLEO Deep-Link:**
Any POI detail sheet has an "Ask CLEO" button that navigates to the chat screen with a preloaded prompt about that POI. CLEO receives the POI's full data as context.

**CLEO → Itinerary Flow:**
1. User tells CLEO "Plan a 3-day Cairo trip"
2. CLEO curates POI IDs using `search_pois` tool
3. CLEO calls `curate_itinerary` with POI list
4. Backend runs VROOM optimization
5. CLEO presents day-by-day plan in chat
6. Inline itinerary card appears with "View Optimized Plan" button
7. Button navigates to Planner Screen with full itinerary data

**Map → POI → Trip Flow:**
1. User explores map, taps region, sees POIs
2. Taps a POI → detail sheet opens
3. "Add to Trip" → adds to current itinerary
4. Returns to map → POI now has a "added" indicator

---

## 5. Design Tokens & Brand Identity

### 5.1 Existing Color System (VoyoColors)

These colors are already implemented in `flutter_app/lib/theme.dart`:

```dart
// Backgrounds
page:       #F7F5F1   // Warm cream — primary background
paper:      #FFFFFF   // Pure white — cards, sheets
vellum:     #F0EBE3   // Parchment — CLEO chat bubbles
smoke:      #E8E2D8   // Light warm gray — dividers, borders

// Brand Accents
expedition: #D45028   // Warm red-orange — primary CTA, Cairo region
terra:      #C4622A   // Burnt orange — secondary accent, Giza region
sky:        #1C72B4   // Deep sky blue — brand color, CLEO, Alexandria
discovery:  #8860D4   // Rich purple — discovery moments, Luxor
discoveryAccessible: #6040B0  // Darker purple — accessible variant

// Semantic
verified:   #2A7A50   // Rich green — verified badges, success states
caution:    #D48A10   // Warm amber — warnings, CLEO beak

// Text
ink:        #1A1714   // Near-black — primary text
stone:      #6A6058   // Warm gray — secondary text
```

### 5.2 Proposed Extended Palette

For the Kurzgesagt-inspired illustrative layer:

```dart
// Illustrative Accents (for map regions, illustrations, category badges)
nileDeep:     #0C4A6E   // Deep Nile blue — water features
nileBright:   #0EA5E9   // Bright river blue
desertGold:   #D97706   // Golden desert — arid landscape elements
desertLight:  #FDE68A   // Pale sand
palmGreen:    #059669   // Tropical green — oases, Aswan
coral:        #F97316   // Warm coral — Red Sea, 90-min isochrone
terracotta:   #B45309   // Earthy brown — archaeological sites
lotus:        #EC4899   // Lotus pink — decorative accent
lapis:        #1E3A5F   // Deep lapis — Egyptian luxury
papyrus:      #D4C5A9   // Papyrus fiber — textures, backgrounds
sunsetOrange: #EA580C   // Warm sunset — dramatic moments
nubianBlue:   #2563EB   // Nubian blue — cultural elements

// Isochrone Zone Colors
isochrone30:  #0D9488   // Teal — 30 min reachable
isochrone60:  #D97706   // Amber — 60 min reachable
isochrone90:  #EA580C   // Coral — 90 min reachable

// Category Colors
catHistorical:  #B45309   // Terracotta
catCultural:    #7C3AED   // Purple
catNatural:     #059669   // Green
catEntertainment: #EC4899 // Pink
catReligious:   #1E3A5F   // Deep blue
catShopping:    #D97706   // Gold
catDining:      #EA580C   // Warm orange
catAccommodation: #0EA5E9 // Sky blue

// Dark Mode Overrides
darkPage:     #121110   // Near-black with warm undertone
darkPaper:    #1E1C18   // Dark warm surface
darkVellum:   #252320   // Dark chat bubble
darkSmoke:    #2E2B26   // Dark border
darkInk:      #F5F3EF   // Light text on dark
darkStone:    #9A938A   // Muted secondary text
```

### 5.3 Typography

**Primary Typeface:**
- **Display/Headings:** A geometric sans-serif with personality. Consider:
  - *Outfit* — geometric, warm, excellent weight range (current: Google Fonts)
  - *National Park* — adventurous feel, perfect for travel app
  - *Big Shoulders* — bold, architectural, Egyptian monument vibes
- **Body Text:** *Work Sans* — clean, highly readable, excellent at small sizes
- **Arabic Text:** System Arabic font (ensures native rendering quality)
- **Monospace (code/data):** *JetBrains Mono* or *Geist Mono* — for prices, times, coordinates

**Type Scale (Flutter):**
```
Display Large:  32px / Bold     → Hero titles, region names on map
Display Medium: 28px / SemiBold → Screen titles
Headline Large: 24px / SemiBold → Section headers
Headline Small: 20px / Medium   → Card titles
Body Large:     16px / Regular  → Primary body text
Body Medium:    14px / Regular  → Secondary text, descriptions
Body Small:     12px / Regular  → Metadata, timestamps
Label Large:    14px / Medium   → Button text, nav labels
Label Small:    11px / Medium   → Badges, tags, chips
```

### 5.4 Spacing & Grid

**8px base grid** (Scandinavian precision):
```
4px   — Micro spacing (icon padding, tight gaps)
8px   — Base unit (component internal padding)
12px  — Small gaps (between related elements)
16px  — Standard padding (card padding, list items)
24px  — Section gaps (between content sections)
32px  — Large gaps (between major sections)
48px  — Extra large (screen edge to first content)
```

**Border Radius:**
```
4px   — Small chips, tags
8px   — Input fields, small cards
12px  — POI cards, buttons
16px  — Bottom sheets, large cards
20px  — Modal sheets (top corners)
Full  — Avatar circles, category dots
```

### 5.5 Elevation & Shadows

Kurzgesagt-flat + Scandinavian-subtle:
- **Level 0:** No shadow — flat elements, backgrounds
- **Level 1:** `0 1px 3px rgba(26,23,20,0.08)` — cards at rest
- **Level 2:** `0 4px 12px rgba(26,23,20,0.12)` — cards on hover/tap
- **Level 3:** `0 8px 24px rgba(26,23,20,0.16)` — bottom sheets, modals
- **Level 4:** `0 16px 48px rgba(26,23,20,0.20)` — full-screen overlays

Dark mode: shadows become even more subtle, replaced by lighter borders.

### 5.6 Animation Principles

**Motion language inspired by both Kurzgesagt and Teenage Engineering:**

- **Entrances:** Elements slide in from their natural direction (bottom sheets from bottom, cards from right). 300ms ease-out.
- **Isochrone bloom:** Concentric polygons expand outward from center point like ripples. Staggered 200ms delay between zones. 600ms total.
- **Region zoom:** Camera animates with deceleration curve (like a physical camera movement). 800ms.
- **CLEO typing:** Text appears character by character with a slight opacity fade. 30ms per character.
- **Card interactions:** Slight scale-up (1.02x) on press, spring-back on release. 150ms.
- **Tab transitions:** Cross-fade between screens (no slide — feels more premium). 200ms.
- **Loading states:** Shimmer skeletons (not spinners). Kurzgesagt-style — skeleton shapes match content layout.
- **Pull to refresh:** Subtle, with the CleoOwl doing a small animation.

**Easing curves:**
- Standard: `Curves.easeOutCubic` — most animations
- Decelerate: `Curves.easeOutQuart` — map zooms, sheet expansions
- Spring: `Curves.elasticOut` — playful moments (badge unlock, POI add confirmation)
- Linear: `Curves.easeInOut` — continuous animations (progress bars, typing)

### 5.7 Iconography

**Style:** Custom line icons with rounded caps (not Material default). Think Phosphor Icons meets Teenage Engineering — clean geometric lines with subtle warmth.

**Required Icon Set:**
```
Navigation:
- Home (house with chimney detail)
- Map (folded map)
- Chat (speech bubble with owl ear tufts)
- Planner (checklist with route line)
- Back (chevron left)
- Close (x with rounded caps)

Map:
- POI Marker — Historical (pyramid silhouette)
- POI Marker — Cultural (mask/face)
- POI Marker — Natural (leaf)
- POI Marker — Dining (utensils)
- POI Marker — Religious (crescent + cross)
- POI Marker — Shopping (bag)
- POI Marker — Entertainment (star)
- POI Marker — Accommodation (bed)
- POI Marker — Default (location pin)
- Isochrone center (pulsing dot)
- Explore from here (compass rose)
- Clear overlay (x in circle)
- Current location (dot with ring)

Actions:
- Search (magnifying glass)
- Filter (sliders horizontal)
- Add to trip (plus in circle)
- Navigate (arrow in circle)
- Ask CLEO (owl face icon)
- Share (share arrow)
- Reorder (drag handles)
- Save (bookmark)
- Delete (trash)
- Edit (pencil)

Status:
- Verified (checkmark in shield)
- Hidden Gem (diamond)
- Rating star (filled/empty)
- Open now (green dot)
- Closed (red dot)
- Loading (shimmer/owl pulse)

CLEO-specific:
- CleoOwl full (avatar)
- CleoOwl face (mini avatar)
- CleoOwl thinking (animated: eyes looking up)
- Typing indicator (three dots)
- Itinerary card icon (calendar + route)

Categories (for filter chips):
- All categories (grid of 4 dots)
- Historical (column/pillar)
- Cultural (theater masks)
- Natural (mountain + sun)
- Entertainment (confetti/star)
- Religious (mosque silhouette)
- Shopping (shopping bag)
- Dining (fork + knife)
```

**Total: ~45 custom icons needed**

### 5.8 Logo & Brand Marks

**Primary Logo:**
- Wordmark "VOYO" in display typeface (Outfit or similar geometric sans)
- The "V" can subtly reference an open road or the Nile Valley
- Monochrome version for dark/light backgrounds
- No gradient fills — solid color only

**Logo Mark:**
- A simplified, iconic representation that works at 16px favicon size
- Options to explore:
  - Stylized "V" with a compass needle integrated
  - Abstract owl eyes (CLEO reference)
  - Pyramidal "V" silhouette
  - Nile curve + pin marker combination

**CLEO Brand Mark:**
- The owl mascot rendered in a Kurzgesagt-style flat illustration
- Must work at multiple sizes: 16px (chat avatar), 44px (nav), 120px (splash)
- Expressive enough for 3 states: default, thinking, celebrating

**Region Badges:**
- Each of the 8 regions gets a small illustrative mark:
  - Cairo: Citadel silhouette
  - Giza: Pyramid triangle
  - Alexandria: Lighthouse column
  - Luxor: Obelisk
  - Aswan: Palm + river
  - Hurghada: Wave
  - Marsa Alam: Fish + coral
  - Sinai: Mountain peaks

### 5.9 Illustration Style

For empty states, onboarding, and decorative elements:

- **Flat, geometric** illustration style (Kurzgesagt reference)
- Warm color palette from brand colors
- Egyptian-themed subjects: pyramids, feluccas on the Nile, bazaar scenes, desert landscapes
- No perspective — everything is isometric or flat front-view
- Characters are simple geometric shapes with expressive eyes
- Scenes have depth through layering, not shading
- Each illustration tells a micro-story (a traveler discovering a hidden temple, a family on a felucca)

**Required Illustrations:**
```
1. Splash/Splash background — panoramic Egypt scene
2. Onboarding Step 1 — adventurer character on a journey
3. Onboarding Step 2 — Egyptian cultural montage
4. Onboarding Step 3 — relaxing Nile scene
5. Onboarding Step 4 — group of friends exploring
6. Empty state: No trips yet — traveler with empty map
7. Empty state: No recommendations — CleoOwl with magnifying glass
8. Empty state: No search results — desert scene with tumbleweed
9. Error state — CleoOwl looking confused
10. Offline state — CleoOwl in airplane mode
```

**Total: ~10 custom illustrations needed**

---

## 6. User Journey Maps

### 6.1 New User First-Time Experience

```
App Open
  → Splash (2s)
  → Login/Register
  → Onboarding (4 steps, ~90 seconds)
  → Home Screen
    → "Ahlan, [Name]! Ready to explore Egypt?"
    → See 4-6 recommended POIs
    → See mini-map with regions
    → No trips yet (empty state illustration + CTA)
  
  Path A: "Ask CLEO to plan a trip"
    → CLEO chat opens with greeting
    → User: "Plan a 3-day trip to Cairo"
    → CLEO asks clarifying question if needed
    → CLEO curates + optimizes
    → Inline itinerary card appears
    → "View Optimized Plan" → Planner Screen
    → User reviews, adjusts, saves
  
  Path B: "Explore the map"
    → Map Explorer opens
    → User taps a region → explainer card
    → User taps a POI → detail sheet
    → "Add to Trip" → itinerary creation flow
  
  Path C: "Browse recommendations"
    → Scroll through POI cards on home
    → Tap a card → detail sheet
    → "Ask CLEO" → deep-link to chat about that POI
```

### 6.2 Returning User Trip Planning

```
App Open
  → Home Screen
  → See personalized recommendations (updated by CLEO learning)
  → See current trip status
  
  → "Hey CLEO, add the Egyptian Museum to my Cairo trip"
    → CLEO adds POI to current itinerary
    → Offers to re-optimize
  
  → Map Explorer
    → Long-press hotel location
    → Isochrone bloom shows reachable POIs
    → Tap POI → detail → add to trip
```

### 6.3 During-Trip Usage

```
Open app
  → Current trip highlighted
  → Planner shows today's stops
  → "Navigate" on next stop → Google Maps
  → Back to VOYO → mark stop as visited
  → "Ask CLEO: Where's good for lunch near here?"
    → CLEO uses location context + profile
    → Recommends based on cuisine preferences
```

---

## 7. Responsive & Platform Considerations

### 7.1 Mobile (Primary Target)
- Design for iPhone 15 (393×852) and Pixel 8 (412×915)
- Bottom navigation with 4 tabs + center floating CLEO button
- Bottom sheets for detail views (thumb-friendly)
- Map fills available space — controls overlay

### 7.2 Tablet
- Split-view: map on left, detail/chat on right
- Planner shows day map alongside stop list
- CLEO chat can run in a slide-over panel

### 7.3 Web
- Same Flutter codebase, responsive layout
- Wider map with sidebar for POI details
- CLEO chat can run as a persistent side panel
- Desktop-first navigation (top bar instead of bottom tabs)

### 7.4 Dark Mode
- Full dark mode support from day one
- Dark palette (see 5.2) — warm undertones, not pure black
- Map tiles switch to dark variant
- CLEO owl stays colorful against dark backgrounds
- Illustrations have dark-mode variants where needed

---

## 8. Accessibility

- WCAG 2.1 AA compliance for all text contrast ratios
- Minimum 4.5:1 contrast for body text, 3:1 for large text
- Screen reader labels on all interactive elements
- Semantic HTML (Flutter's Semantics widget)
- Touch targets minimum 48×48px
- VoiceOver/TalkBack support
- Reduced motion preference respected (no animations when enabled)
- Color is never the only indicator of meaning (icons + labels accompany)

---

## 9. Prompting Guide for AI Image Generation

When using ChatGPT, Midjourney, DALL·E, or Nano Banana to generate concept screens or assets, use these prompts as starting points:

### 9.1 General App Aesthetic

> "A mobile app interface design for a travel app called VOYO, focused exclusively on Egypt. The style combines Kurzgesagt's flat, colorful, illustrative aesthetic with Scandinavian design's clean precision and restraint — think Spotify meets Teenage Engineering meets a well-designed children's encyclopedia. Warm cream backgrounds (#F7F5F1), rich saturated accent colors (warm red #D45028, sky blue #1C72B4, discovery purple #8860D4), geometric sans-serif typography. Information-rich but never cluttered. Feels like a crafted object, not a template."

### 9.2 Map Explorer Screen

> "A mobile app screen showing an interactive map of Egypt. The map uses a warm, muted OpenStreetMap style with 8 colored semi-transparent polygon overlays representing different regions (Cairo in warm red, Alexandria in sky blue, Luxor in purple, Aswan in green, etc.). Small category-coded pin markers show points of interest. A floating compass button in the bottom-right says 'Explore from here'. The overall feel is like a Kurzgesagt YouTube video illustration — colorful, clean, educational but playful. The bottom navigation has 4 icons. Status bar and search bar at top."

### 9.3 Isochrone Visualization

> "A mobile map screen showing isochrone reachability polygons — three concentric, organic blob shapes expanding outward from a central point, representing 30-minute, 60-minute, and 90-minute travel zones. The zones use teal, amber, and coral colors with soft transparency. Small POI markers are highlighted within each zone. A bottom sheet shows '12 places within 30 min · 24 within 60 min · 38 within 90 min'. Kurzgesagt-inspired flat illustration style, warm and information-dense."

### 9.4 CLEO Chat Screen

> "A mobile chat interface for an AI travel guide named CLEO (represented by a cute blue owl mascot). The app background is warm cream. CLEO's message bubbles are parchment-colored, left-aligned. User bubbles are sky blue, right-aligned. CLEO is giving a detailed response about the Pyramids with rich markdown formatting. An inline card shows a 3-day Cairo itinerary with 'View Optimized Plan' button. The input bar at bottom has a text field and send button. Suggested prompt chips float above the input. Clean, Scandinavian-feeling layout with Kurzgesagt warmth in the mascot and illustration."

### 9.5 Home Screen

> "A mobile app home screen for VOYO, an Egyptian travel app. Top: personalized greeting 'Ahlan, Ahmed! 👋 Ready to explore Egypt?' Below: horizontal scroll of POI recommendation cards with images, ratings, and match reasons. Middle: a mini interactive map of Egypt showing colored region borders. Bottom: 'Your Trips' section with itinerary cards. Warm cream background, clean card-based layout, Scandinavian precision with Egyptian warmth. Bottom navigation bar with Home, Map, CLEO (owl icon), and Planner tabs."

### 9.6 POI Detail Sheet

> "A bottom sheet UI in a mobile travel app showing detailed information about the Great Pyramid of Giza. Hero image at top with gradient overlay. Below: title 'Great Pyramid of Giza' with Arabic name 'هرم خوفو'. Quick facts row: rating 4.7, visit duration 3hr, ticket price 200 EGP. Expandable sections for Opening Hours, Historical Significance, Travel Tips. Tags: UNESCO, Ancient, Must-See. Sticky bottom action bar: Ask CLEO, Add to Trip, Navigate. Warm cream cards, clean typography, Kurzgesagt-inspired category badges."

### 9.7 Logo & Brand Mark Prompts

**Wordmark:**
> "Typography logo for 'VOYO' — a travel app for Egypt. The word VOYO in a geometric sans-serif font similar to Outfit or National Park. The 'V' subtly suggests an open road. Solid warm red-orange color (#D45028) on cream background (#F7F5F1). Clean, confident, adventurous. No gradients, no shadows."

**Logo Mark:**
> "A minimal logo mark for VOYO travel app. A stylized compass needle integrated with the letter V, or abstract owl eyes, or a pyramid-shaped V silhouette. Must work at 16px favicon size. Flat design, single color, warm red-orange (#D45028). Clean geometric lines."

**CLEO Mascot:**
> "A cute, wise owl mascot named CLEO for an Egyptian travel app. Kurzgesagt-inspired flat illustration style — simple geometric shapes, expressive eyes, rounded forms. The owl is sky blue (#1C72B4) with a warm cream (#EDE8DC) face and amber (#D48A10) beak. Three poses: default (friendly, alert), thinking (eyes looking up, wing on chin), celebrating (wings spread, eyes sparkling). Clean, minimal, works at small sizes."

### 9.8 Region Illustration Prompts

> "A set of 8 small illustrative badges for Egyptian regions, in Kurzgesagt flat illustration style. Each badge is a simple icon representing a region: Cairo (citadel silhouette), Giza (pyramid), Alexandria (lighthouse), Luxor (obelisk), Aswan (palm tree by river), Hurghada (wave), Marsa Alam (fish), Sinai (mountain peaks). Each in its signature color on a warm cream background. Minimal, geometric, distinctive."

---

## 10. Design System File Structure (Proposed)

```
design-system/
├── VOYO_DESIGN_BRIEF.md          ← This document
├── BRAND_GUIDELINES.md           ← Brand rules, voice, tone, do's/don'ts
├── DESIGN_TOKENS.md              ← Colors, typography, spacing, elevation
├── COMPONENT_LIBRARY.md          ← Reusable component specs
├── ICON_INVENTORY.md             ← Full icon catalog with SVG references
├── ILLUSTRATION_GUIDE.md         ← Style guide for custom illustrations
├── ANIMATION_SPEC.md             ← Motion language, timing, curves
├── DARK_MODE.md                  ← Dark mode color mappings
├── SCREEN_SPECIFICATIONS.md      ← Detailed per-screen layouts
├── assets/
│   ├── logos/
│   │   ├── voyo-wordmark-light.svg
│   │   ├── voyo-wordmark-dark.svg
│   │   ├── voyo-logomark.svg
│   │   └── cleo-mascot/
│   │       ├── cleo-default.svg
│   │       ├── cleo-thinking.svg
│   │       └── cleo-celebrating.svg
│   ├── icons/
│   │   ├── navigation/
│   │   ├── map/
│   │   ├── actions/
│   │   ├── status/
│   │   └── categories/
│   ├── illustrations/
│   │   ├── empty-states/
│   │   ├── onboarding/
│   │   └── decorative/
│   ├── colors/
│   │   └── voyo-palette.svg      ← Color swatch reference
│   └── typography/
│       └── type-scale.svg         ← Type scale reference
├── concept-screens/               ← AI-generated concept images
│   ├── home-screen.png
│   ├── map-explorer.png
│   ├── isochrone-viz.png
│   ├── cleo-chat.png
│   ├── poi-detail.png
│   ├── planner.png
│   ├── onboarding.png
│   └── dark-mode.png
└── references/
    ├── kurzgesagt-screenshots/     ← Reference images
    ├── spotify-reference/
    └── teenage-engineering-reference/
```

---

## 11. Feasibility Assessment

### Is this design system approach feasible for Phase III?

**Yes — with the right scope.** Here's the honest breakdown:

### What Makes It Feasible

1. **Flutter's built-in theming** — Flutter's `ThemeData` system maps directly to design tokens. Colors, typography, shapes, and component themes can be defined once and applied globally. Your existing `VoyoColors` class is already the right pattern.

2. **Pi's design skills** — You already have 6 relevant skills installed:
   - `flutter-frontend-design` — Production-grade Flutter UI
   - `mobile-app-ui-design` — Mobile-first design principles
   - `material-3` — Material Design 3 with Flutter support
   - `impeccable` — Full design discipline system
   - `taste-skill` — Anti-generic-UI guardrails
   - `emil-design-eng` — Animation philosophy and polish

3. **Google Fonts integration** — Flutter's `google_fonts` package gives you instant access to Outfit, Work Sans, and all the typefaces mentioned above without bundling font files.

4. **CustomPaint for mascots/icons** — The CleoOwl is already implemented as a `CustomPaint` widget. This approach scales to all custom iconography without SVG dependency issues.

### What to Be Careful About

1. **Custom illustrations** — These cannot be generated by Pi or coding agents. You'll need to commission them, use AI image generators (ChatGPT/Midjourney), or use a simplified geometric style that CAN be rendered in code (CustomPaint or Canvas).

2. **Icon count** — ~45 custom icons is a moderate set. Consider starting with Phosphor Icons (open source, close to the style described) and customizing only the most distinctive ones (CLEO owl, pyramid marker, region badges).

3. **Map tile styling** — Custom OpenStreetMap tile styles require either a third-party provider (MapTiler, Stadia Maps) or self-hosting tileserver-gl. Budget ~1 day for this.

4. **Dark mode doubles the testing** — Every color, illustration, and map tile needs a dark variant.

### Estimated Asset Count

| Category | Count | Effort | Notes |
|----------|-------|--------|-------|
| Color tokens | ~40 | Low | Define once, reference everywhere |
| Typography styles | ~10 | Low | Map to Flutter TextTheme |
| Custom icons | ~45 | Medium | Start with Phosphor, customize 10-15 |
| Logo variants | ~6 | Medium | Wordmark × 2 (light/dark) + logomark + cleo × 3 |
| Region badges | 8 | Medium | Kurzgesagt-style mini illustrations |
| Scene illustrations | ~10 | High | Commission or AI-generate |
| Animation specs | ~12 | Medium | Define curves, timings, triggers |
| Component specs | ~25 | Medium | Cards, sheets, chips, buttons, inputs, nav |
| Screen layouts | ~10 | Medium | Wireframe → Flutter implementation |
| Dark mode variants | ~40 | Low-Medium | Color remapping, some new assets |
| **Total unique assets** | **~200** | | |

### Realistic Timeline

- **Week 1:** Design tokens, color system, typography, logo (this document → concrete files)
- **Week 2:** Concept screens from AI image generators, icon selection/customization
- **Week 3:** Component specs, animation specs, illustration briefs
- **Week 4:** Implementation in Flutter (Phase III begins)

---

## 12. Appendix: UI/UX Pro Max Skill Compatibility

### Question: Is UI/UX Pro Max compatible with mobile app design?

**Answer: Partially, but it's not the best fit for your needs. Here's why:**

**What UI/UX Pro Max does well:**
- Web landing pages and marketing sites (its primary focus)
- Logo and brand identity generation (has a dedicated `brand/` sub-skill)
- Design system token generation (v2.0's flagship feature)
- Slide/presentation design
- Icon design guidance
- Banner and social media asset creation
- 67 UI style references and 161 reasoning rules
- shadcn/Tailwind CSS component styling (web-focused)

**What it doesn't do well for mobile:**
- No Flutter/Dart-specific component guidance
- No mobile interaction patterns (bottom sheets, thumb zones, gesture navigation)
- No mobile-first responsive breakpoints (375px, 414px)
- Its design system generator outputs web tokens (CSS/Tailwind), not Flutter ThemeData
- No guidance on mobile navigation patterns (bottom nav, tab bars)
- CIP (Concept in Place) feature is web-screen oriented

**Your existing Pi skills are a better combination:**

| Need | Better Skill |
|------|-------------|
| Flutter components | `flutter-frontend-design` |
| Mobile UX patterns | `mobile-app-ui-design` |
| Material Design 3 theming | `material-3` |
| Anti-generic taste | `taste-skill` + `impeccable` |
| Animation philosophy | `emil-design-eng` |
| Brand guidelines | Create manually from this document |

**Recommendation:** Don't install UI/UX Pro Max. Your existing 6 skills cover mobile design more thoroughly. If you want its design system token generation, you can reference its open-source approach (design-tokens-starter.json format) but adapt it for Flutter's ThemeData instead of CSS variables.

---

*Document prepared for VOYO Phase III design system creation. Use as the primary reference when working with AI image generators, briefing designers, or implementing the design system in Flutter.*
