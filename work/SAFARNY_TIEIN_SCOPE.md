# Safarny Flutter Tie-In — Scope & Decision Doc

> **STATUS: BUILT ✅ (2026-06-18)** — Option A implemented + verified by 6
> backend integration tests (mocked; no Groq/Docker/Supabase). Remaining:
> one live e2e with fresh Groq quota (partner task). Details in §8 below.
>
> The rest of this doc is preserved as the original scope/decision record.

**Status:** scoped, not started. This is the last architectural gap between
"what the thesis claims" and "what the app does."
**Owner:** next focused session (~1 day).
**Prereq:** Groq quota refreshed (live e2e test needs the LLM tier up).

---

## 1. The gap (grounded)

The Flutter app **never calls the safarny `/itinerary/plan` endpoint.**
Traced the full flow:

```
TripProfile sheet (trip_profile_sheet.dart:11)
  → _sendItineraryRequest (chat_screen.dart:263)
  → FLATTENS the structured profile to a natural-language STRING
  → sends to CLEO as a chat message
  → CLEO replies with free-text itinerary prose
  → _parseItineraryStops (chat_screen.dart) parses the prose back into stops (LOSSY)
  → _save (chat_screen.dart:1470) does:
       createItinerary(userId, title)              // bare record
       for each stop:
         _findPoiId(stop.name)                      // FUZZY keyword match
         addItineraryItem(poiId, day, time)         // writes NO tip, NO VROOM time
```

Consequences:
- `itinerary_items.notes` (where safarny tips live) is **never written**
  from the Flutter path. Only `persistence.save_optimized_itinerary`
  (backend) writes tips — and nothing in the app calls it.
- `arrival_time` / `departure_time` come from the LLM's prose parse,
  not from VROOM. The thesis claim "VROOM assigns real times" is true
  for the `/plan` API but **false for trips users actually save.**
- The `TripProfile` structure (travelers/budget/pace/interests) is
  collected, stringified, sent to an LLM, parsed back. Safarny's
  deterministic planner + VROOM scheduler + tip generator are bypassed.

This is why existing trips (e.g. the Youssef account) show only POI-level
`narrative`/`description` (which I surfaced in planner_screen.dart) and
**no per-stop tips** — the data simply isn't in the DB.

---

## 2. Shape mismatch (the non-obvious work)

Safarny's output (`safarny_planner.py:_shape`, ~line 699) and
`save_optimized_itinerary`'s expected input (`persistence.py:23`) use
**different key names**. Any save call needs an adapter:

| Safarny emits            | Persistence expects        | Notes |
|--------------------------|----------------------------|-------|
| `day` (int)              | `day_number`               | rename |
| `time` ("HH:MM:SS")      | `arrival_time`             | rename |
| `departure_time`         | `departure_time`           | ✓ same |
| `transport_to_next_min`  | `travel_to_next_minutes`   | rename |
| `transport_to_next_km`   | `travel_to_next_km`        | ✓ same |
| `tip`                    | `tip`                      | ✓ same |
| — (absent)               | `sequence`                 | default 0; sort by `time` |
| — (absent)               | `optimization_metadata.solver_status` | set from provenance |

Trip-level fields Safarny produces that persistence **doesn't persist today**
(`overview`, `tips`, `summary`, `total_cost_egp`, `budget_breakdown`,
`provenance`): decide whether to (a) drop them, or (b) extend
`itineraries.metadata` JSONB to carry them. Recommendation: stash
`overview`/`tips`/`summary`/`provenance` in `itineraries.metadata` so the
planner page can render the trip overview later. Small schema touch
(additive, no migration of existing rows).

---

## 3. The decision: Option A vs Option B

You must pick before work starts. It's a UX/thesis-honesty tradeoff,
not a technical one.

### Option A — Full deterministic re-plan (recommended)

When the user taps **Save** in chat, send the original `TripProfile` to
`/itinerary/plan`, persist the safarny result. CLEO's in-chat itinerary
becomes a **conversational preview**; safarny's saved plan is the
authoritative record.

- **Pros:** thesis-aligned ("LLM plans" is literally true of the saved
  trip); tips/times/provenance all real; no fuzzy POI matching; the
  provenance block is capturable for the thesis figures.
- **Cons:** the saved plan **may differ** from what CLEO displayed
  (different POI subset, different order). Both draw from the same
  candidate pool so divergence is usually small, but it exists.
- **Thesis framing:** "CLEO converses; Safarny commits." Clean
  separation of the LLM-intent layer from the deterministic-commit layer.

### Option B — Enrichment only

Keep CLEO's POI selection (parse the chat stops → POI IDs), pass those
IDs to `/optimize` (VROOM only) for real times + tips. Persist.

- **Pros:** what the user saw in chat is exactly what they get.
- **Cons:** the "LLM plans" claim only holds for the chat display, not
  the committed itinerary. Weaker thesis story. Still needs the shape
  adapter (VROOM optimize output also differs from the persistence
  shape). Fuzzy POI matching stays in play.

**My recommendation: Option A.** It's what the thesis argues, the
divergence is small and defensible, and it removes the fuzzy-match
hack entirely. The rest of this doc assumes Option A.

---

## 4. Work breakdown (Option A)

### Backend (~60 lines)

**4a. Make `/plan` persist.** Currently `/itinerary/plan`
(`itinerary.py:170`) returns the result but doesn't save. Two options:
- (preferred) add `persist: bool = True` flag to `PlanTripRequest`;
  when true, call `save_optimized_itinerary` with the adapted shape
  and return `{itinerary_id, ...result}`.
- or add a separate `POST /itinerary/plan-and-save`.

**4b. Shape adapter.** Add `safarny_planner.py::to_persistence_shape()`
(or a helper in persistence.py) that renames keys per the table in §2
and synthesizes `sequence` (sort stops within a day by `time`) +
`optimization_metadata.solver_status` (from
`provenance.times == "vroom"`).

**4c. (optional) Extend `itineraries.metadata`.** Additive migration:
`overview`, `tips`, `summary`, `provenance` → JSONB. Lets the planner
page render the trip overview later. Not blocking.

### Flutter (~80 lines)

**4d. `SupabaseService.planAndSaveItinerary(TripProfile)`.** New method:
- build `PlanTripRequest` JSON from `TripProfile` (shapes match 1:1 —
  see §5).
- POST to `/itinerary/plan` with the persist flag.
- return the `itinerary_id`.

**4e. Rewire `chat_screen._save()` (chat_screen.dart:1470).** Replace
the `createItinerary` + fuzzy `_findPoiId` + `addItineraryItem` loop
with a single `planAndSaveItinerary(widget.profile)` call. Requires
threading the original `TripProfile` through to the save sheet (it's
currently discarded after `_sendItineraryRequest` stringifies it).
- Add `final TripProfile? profile;` to the save sheet / chat state.
- Set it in `_sendItineraryRequest` before sending the chat message.
- In `_save`, if `profile != null` → deterministic path; else → keep
  the legacy fuzzy path as a fallback (for purely conversational plans
  with no structured profile).

**4f. Planner reload.** After save, the planner already reloads via
`onImported`. The new `pois(*)` SELECT + description/tip render (just
shipped) will display safarny's real tips/times with no further work.

### Test (~1-2 hrs, gated on Groq)

**4g. Live e2e:** open CLEO → "Plan a trip" → fill profile (Islamic
Cairo, 3 days, balanced) → submit → save → open Planner → verify each
stop card shows: real VROOM arrival time, italic tip with lightbulb,
tappable description → trip overview renders. Capture the `provenance`
block from the network panel — that's a thesis figure.

---

## 5. Shape cheat-sheet (TripProfile → PlanTripRequest)

The Flutter `TripProfile` and backend `PlanTripRequest` map 1:1:

| TripProfile (Flutter)        | PlanTripRequest (backend)    |
|------------------------------|------------------------------|
| `title: String?`             | `title: Optional[str]`       |
| `startDate: DateTime?`       | `start_date: Optional[str]` (YYYY-MM-DD) |
| `endDate: DateTime?`         | `end_date: Optional[str]` (YYYY-MM-DD) |
| `travelers: int`             | `travelers: int`             |
| `budgetTier: String`         | `budget_tier: str`           |
| `pace: String`               | `pace: str`                  |
| `companions: String`         | `companions: str`            |
| `interests: Set<String>`     | `interests: List[str]`       |
| `notes: String?`             | `notes: Optional[str]`       |
| — (absent)                   | `hotel_location: Optional[List[float]]` |

Only transformations: `DateTime → "YYYY-MM-DD"`, `Set → List`.
`hotel_location` has no Flutter source today — pass `null` (safarny
handles it; each day starts/ends at the first/last POI).

---

## 6. Risks & rollback

- **Rollback:** keep the legacy `_save()` fuzzy path as the fallback
  when `profile == null`. A failed `/plan` call (Groq down) should
  surface an honest error, NOT silently fall back to the lossy path —
  same principle as the preview-add #22 gate.
- **Existing trips:** cannot be back-filled without a migration script
  (they have no `TripProfile` recorded). Out of scope. New trips onward
  get the real pipeline.
- **Shape adapter bugs:** the renames in §2 are the main risk surface.
  Add a unit test mapping one canned safarny output → persistence shape
  before wiring the endpoint.
- **Provenance honesty:** if VROOM is down, safarny returns
  `times: unscheduled_vroom_down` and null arrival times. The planner
  card already renders "Unscheduled" for null times. Don't fake times.

---

## 7. "Are we golden after this?" — the tiers

- **Tier 1 (thesis demo):** done now. All screens work, critical bugs
  closed (#22 feasibility gate was the thesis-defending one).
- **Tier 2 (portfolio/compelling app):** this tie-in + one clean live
  e2e + enrichment completion. **Yes, golden.**
- **Tier 3 (production/launch):** auth edge cases, offline cache,
  monitoring, Arabic localization, app store readiness, data freshness.
  Weeks of real product work — true of any app, not a VOYO deficiency.
  Out of thesis scope.
