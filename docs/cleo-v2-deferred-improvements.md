# CLEO v2 — Deferred Improvements Backlog

> These are known improvements identified during Phase 1B that are deferred
> to later phases or post-thesis polish. Each item has context on why it
> matters and what the fix looks like.

---

## Priority: Medium

### 1. True Token-Level SSE Streaming
**Current:** `process_message_stream` chunks the complete response into 5-char pieces.  
**Fix:** Use `groq.AsyncGroq` streaming to yield tokens as they arrive. Requires:
- Frontend SSE handler in Flutter that progressively renders markdown
- Handle the case where the LLM decides mid-stream to call tools (abort stream, fall back to `_agent_loop`)
**Impact:** Perceived latency drops dramatically for long itinerary responses.

### 2. Tavily `search_depth` Should Be Dynamic
**Current:** Hardcoded `search_depth: "basic"`.  
**Fix:** Use `"advanced"` for complex queries (itineraries, current events) and `"basic"` for quick lookups. The agent already classifies `response_style` — map `"detailed"` → `"advanced"`, else `"basic"`.
**Impact:** Better search quality for trip planning queries.

### 3. Tavily `include_answer: true` for Quick Synthesis
**Current:** Returns raw search results, LLM synthesizes.  
**Fix:** Set `include_answer: true` so Tavily returns a synthesized answer alongside results. CLEO can use it as a grounding anchor or skip the synthesis LLM call entirely for factual queries.
**Impact:** Faster, more accurate responses for current-events queries.

### 4. `find_nearby_pois` Still Pulls 1000 Rows
**Current:** Fetches all POIs and calculates distance in Python.  
**Fix:** Add PostGIS extension to Supabase, create a geography column, use `ST_DWithin` for server-side radius queries. Migration:
```sql
ALTER TABLE pois ADD COLUMN geom geography(Point, 4326);
UPDATE pois SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326);
CREATE INDEX idx_pois_geom ON pois USING GIST(geom);
```
Then query: `.filter("geom", "st_dwithin", f"POINT({lng} {lat}),{radius_km * 1000}")`
**Impact:** O(result) rows instead of O(all POIs). Essential for isochrone-based reachability in Phase 3.

---

## Priority: Low (Post-Thesis)

### 5. pgvector Embedding Search (Replace Tier 2 ilike)
**Current:** Tier 2 uses Supabase `ilike` on description words. Works, but doesn't understand "pharaonic" ≈ "ancient Egyptian".  
**Fix:** Generate embeddings for POI descriptions (OpenAI `text-embedding-3-small` or local `all-MiniLM-L6-v2`), store in `pois.embedding vector(384)`, query with cosine similarity. Migration in `config/sql/003_poi_search_vector.sql` (to be created).
**Impact:** Semantic search — "mummies and pharaohs" would find the Egyptian Museum even if those words aren't in the description.

### 6. LLM-Based Summarization
**Current:** Summarization extracts keywords/regions/topics with Python string matching.  
**Fix:** After collecting ~40 messages, call Groq with a summarization prompt to produce a 2-3 sentence narrative summary. Store that instead. Costs 1 extra LLM call every ~20 messages per user.
**Impact:** Much richer context preservation — "The user started by asking about pyramids, then shifted to Nile cruises, and expressed interest in budget-friendly options."

### 7. Conversation Threading / Sessions
**Current:** All messages for a user are one flat list.  
**Fix:** Add a `session_id` column. Start a new session when there's a >30 minute gap or explicit topic change. Frontend can show session history.
**Impact:** Cleaner context windows, ability to reference "that trip we planned last week" across sessions.

### 8. Tool Call Timeout / Circuit Breaker
**Current:** If a tool hangs, the agent loop waits indefinitely.  
**Fix:** Add `asyncio.wait_for(tool_coroutine, timeout=10)` with a circuit breaker pattern — if a tool fails 3 times in a row, disable it for the session.
**Impact:** Graceful degradation instead of hanging.

### 9. Streaming Tool Call Results
**Current:** If the LLM decides to call tools during streaming, we fall back silently.  
**Fix:** Implement the OpenAI-style streaming tool call protocol — accumulate tool call deltas, execute when complete, then resume streaming.
**Impact:** True end-to-end streaming for complex queries.

### 10. Redis Cache for Conversation Summaries
**Current:** Summary is read from Supabase every request.  
**Fix:** Cache the summary in Redis with a short TTL (60s). Invalidate on new message write.
**Impact:** Faster context loading for active users.
