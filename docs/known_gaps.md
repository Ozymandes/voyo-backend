# Known Gaps & Decisions

This document records known limitations, intentional design decisions, and deferred features identified during the verification phase (April 2026). These are not bugs — they are acknowledged trade-offs to revisit before production.

---

## 1. In-Memory Conversation History

**What:** `ConversationMemory` (in `src/cleo/conversation_memory.py`) stores chat history in a Python dict. It resets every time the server restarts.

**Impact:** Users lose their conversation context on server restarts. Not a problem for a short demo session, but would break continuity in production.

**Resolution path:** Add a `conversation_history` table in Supabase and persist messages there. The `add_message` / `get_history` methods in `ConversationMemory` are the right place to hook this in.

---

## 2. Frontend-Triggered Itinerary Saving

**What:** CLEO recommends POIs and trip plans conversationally, but does NOT automatically save them to the `itineraries` / `itinerary_items` tables. The saving must be explicitly triggered by the frontend.

**Why (decision):** Keeps CLEO's scope clean. The user may want to discuss options before committing anything to the DB. The frontend will expose a "Save this plan" action.

**Ready to use:** `VOYODatabase.create_itinerary()`, `add_itinerary_item()`, and `get_itinerary_items()` are all tested and working.

---

## 3. No Auth Endpoints

**What:** The `user_auth` table exists and the schema is complete, but there are no `/register` or `/login` API endpoints. The chat endpoint accepts a raw `user_id` UUID.

**Impact:** For the demo, test user UUIDs are passed directly. A real app would need auth flow (register → receive UUID → pass to chat).

**Resolution path:** Supabase Auth (built-in) or a simple `/auth/register` + `/auth/login` endpoint using the existing `user_auth` table.

---

## 4. Weak Accessibility Personalization in CLEO Responses

**What:** When a user has `mobility_preference: "wheelchair"` and `accessibility_needs` set, CLEO's responses do not currently surface accessibility-specific language or filter out non-accessible sites.

**Observed:** The accessible test user (`33333333-...`) received the same generic Cairo recommendations as other users — no mention of ramps, elevators, or accessible routes.

**Why it happens:** `get_personalization_context()` extracts `mobility_preference` and `budget_estimate`, but CLEO's system prompt (`src/cleo/prompts.py`) and the `search_pois` ranking logic (`src/cleo/tools/supabase_tool.py`) do not weight accessibility strongly in the LLM prompt or POI filtering.

**Resolution path:** Add explicit accessibility context to CLEO's system prompt when `mobility_preference` is non-standard, and strengthen the POI re-ranking weight for `accessibility_info`.

---

## 5. `python-dotenv`, `groq`, `fastapi` Missing from `requirements.txt`

**What:** The venv was missing `groq`, `fastapi`, `uvicorn`, and `python-dotenv` — all required for CLEO to run.

**Status:** Installed manually. `requirements.txt` should be updated to include `groq>=1.0.0`.

---

## Verification Results (April 3, 2026)

| Test | Result |
|------|--------|
| `test_cleo.py` — 4 basic CLEO tests | All pass |
| `test_itinerary_crud.py` — 7 DB operation assertions | All pass |
| `test_personalization.py` — 3 user profiles, response differentiation | All pass |
| Seed script (`scripts/seed_test_users.py`) | Idempotent, runs clean |
