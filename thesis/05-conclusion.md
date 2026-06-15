# Chapter 5 — Conclusion

> Maps to PDF Chapter 5. Every contribution recap below traces to evidence in `thesis/evidence/**`
> or the codebase; every limitation is disclosed, not hidden.

## 5.1 Summary

This thesis set out to answer a single question — *how do you build a travel-planning AI that a
visitor can trust?* — and answered it by building VOYO, a compound agentic system that
decomposes trust into three engineering obligations: **grounding**, **constraint awareness**, and
**honest scope**. The architecture is a four-layer compound system (Figure 3.1) in which a
conversational ReAct agent (CLEO), a deterministic seven-dimension recommendation engine, and a
curate→optimize itinerary pipeline all share a single verified-data substrate of 255 Egyptian
points of interest. The LLM is permitted to reason conversationally and to select candidate
sites, but it is never permitted to guess volatile data: prices, hours, coordinates, and
distances come from tools and a verified database, not from parametric memory.

## 5.2 Contributions Recap

The implemented system delivers five contributions, each measurable:

1. **Compound agentic architecture** — a four-layer design (Presentation / Gateway / Agentic
   Orchestration / Ground-Truth Data) that operationalizes the system-centric shift argued by
   Zaharia et al. [1] for a concrete, deployed domain (§3.1, Figure 3.1).

2. **CLEO's tool-call recovery + force-tool grounding** — a native-format tool-call recovery
   parser (`_recover_tool_call_response`) plus a per-response-style `force_tool` policy that
   guarantees database grounding on itinerary and POI queries, eliminating the memory-only
   answers that produced hallucinated places and prices (§3.4;
   `thesis/evidence/06-cleo-grounding.md`). The two live tool calls captured during verification
   (`search_pois` → `curate_itinerary` with real database ids) are the concrete proof that the
   grounding path works end-to-end.

3. **A clean, verified 255-POI database and rebuild pipeline** — the strongest single
   contribution. Five silent failure modes in the inherited enrichment code were diagnosed and
   fixed in a self-contained pipeline; imagery was switched to permanent, key-free Wikimedia
   URLs; and the result is 255 deduplicated POIs across eight regions with permanent images on
   all six most-famous sites (Chapter 6; `thesis/evidence/05-db-completeness.json`).

4. **A deterministic recommendation engine with measured sub-millisecond performance** — a
   seven-dimension weighted scorer with greedy diversification, measured at a median of
   **0.75 ms** for full recommendation over the POI set against a 200 ms target, as part of a
   **99-test, 100%-pass core suite** (Table 4.1, Table 4.4; `thesis/evidence/02-latency.json`,
   `01-test-results.json`).

5. **An honest evaluation framework** — 13 latency benchmarks, 4 A/B correctness scenarios, and
   a live database-completeness audit, accompanied by explicit disclosure of every limitation
   the project currently carries.

## 5.3 Limitations (stated plainly)

A thesis that hides its limitations is weaker than one that opens with them. VOYO's are:

- **LLM free-tier ceilings.** Development and live verification were conducted on the Groq free
  tier, which imposes **12,000 tokens-per-minute** and **100,000 tokens-per-day** limits. The
  first caused an HTTP 413 when un-slimmed tool results re-entered the ReAct loop (fixed by
  `_slim_for_llm`); the second ended the live itinerary verification at the third ReAct
  iteration (`groq.RateLimitError 429 — Limit 100000, Used 99855`, independently re-confirmed
  during this thesis run). The grounding path is proven; the final generated itinerary text is
  re-verifiable after a quota reset or a Dev-Tier upgrade.

- **VROOM optimization pending.** The deterministic optimizer (VROOM) is wired end-to-end and
  unit-tested (problem build, solution parse, status mapping all pass), but the live solve step
  depends on the Docker-hosted Valhalla/VROOM stack and is intermittent. The curate half of the
  pipeline is fully operational.

- **Redis non-operational.** A semantic-cache module exists in code (`src/cleo/semantic_cache.py`)
  but Redis is unreachable on the current hosting; the system degrades gracefully without it. It
  is not a live subsystem and the thesis does not claim it is.

- **Test scope.** The 99-test core is the unit + benchmark surface that runs deterministically
  without live services. Eight additional integration/e2e/tool tests require live Groq +
  Supabase/Redis and fail at collection time on the free tier; they are documented but not
  counted in the headline number (`thesis/evidence/01-test-results.md`).

- **Regional imbalance in POI coverage.** The curated master list under-represents the capital:
  **Cairo has 11 POIs and Giza has 9** — the two thinnest regions despite being the most-visited.
  This is a master-list curation gap, not a technical defect; the fix is more Cairo/Giza
  entries, not engineering (§6.7, Figure 4.x regional distribution).

- **Honest data gaps.** Ticket-price coverage is 58% (107 sites are genuinely *free* — null is
  correct), opening-hours coverage is 67% (natural/outdoor sites have no hours), and image
  coverage is 82% (the 18% gap is concentrated in obscure remote sites, not the famous ones).
  These are semantically-correct nulls, disclosed rather than rounded up.

## 5.4 Future Work

The limitations above double as a roadmap:

1. **Groq Dev-Tier upgrade** to remove the TPM/TPD ceilings and enable live end-to-end demos,
   including the final itinerary text + `[PLANNER]` token that the quota cut short.
2. **VROOM stabilization** — bring the Docker stack up reliably and complete the live
   curate→optimize→display loop, including the Flutter-side isochrone explorer that depends on it.
3. **Regional rebalancing** — extend the Cairo and Giza master lists so the two most-visited
   regions are no longer the thinnest in the corpus.
4. **Narrative enrichment** — once the live loop is reliable, add a narrative wrapper that turns
   the optimized schedule into a readable day-by-day story, still grounded in the verified data.
5. **Multi-image galleries** — move from one Wikimedia image per POI to a small gallery, now
   that single permanent images are reliable.
6. **Redis restoration** — bring the semantic cache back online once hosting allows, and measure
   its hit-rate and latency impact on real query traffic.

## 5.5 Closing Remark

The honest summary is that VOYO demonstrates a defensible answer to the trust question: a
compound system in which an LLM is allowed to be conversational and helpful but is structurally
prevented from being the source of truth. The verified 255-POI database, the sub-millisecond
deterministic scorer, and the forced-tool grounding of the ReAct agent are three concrete
instances of the same idea — *the model reasons; the system verifies*. Where the system falls
short of a production deployment, it says so. That, we would argue, is the version of this
thesis worth defending.
