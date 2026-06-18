# Abstract and Reading Guide

> Maps to the PDF Abstract page (empty in the draft). Every claim traces to
> `thesis/evidence/**` or `thesis/references.bib`.

## Abstract

Generative AI offers a natural conversational interface for travel planning, but monolithic
Large Language Models hallucinate in fact-sensitive domains — inventing prices, hours, and
routes they cannot verify, and producing itineraries that are textually fluent but logistically
infeasible. This thesis presents **VOYO**, a compound agentic AI architecture for grounded and
constraint-aware travel planning in Egypt. VOYO decomposes the trust problem into a four-layer
system — a Flutter presentation layer, a FastAPI gateway, an agentic orchestration layer, and a
verified ground-truth data layer — in which a conversational ReAct agent (CLEO, Groq-hosted
Llama 3) and a deterministic recommendation and optimization pipeline share a single curated
database.

The central design principle is a **curation–optimization split**: the LLM reasons
conversationally and selects candidate sites, but it is *forced* — by a per-response-style tool
policy and a native tool-call recovery parser — to ground every factual claim in a verified
255-point-of-interest database rather than in its parametric memory. The database itself is the
strongest single contribution: a clean rebuild pipeline diagnosed and fixed five silent failure
modes in the inherited enrichment code, switched imagery to permanent key-free Wikimedia URLs,
and produced 255 deduplicated points of interest across eight regions, including permanent
imagery on all six most-famous sites that previously had none.

The deterministic backend is verified by a **99-test core (100% passing)**, with the full
recommendation scoring path measured at a **0.75 ms median** against a 200 ms target — roughly
267× headroom — and four A/B scenarios confirming that different user profiles surface
meaningfully different recommendations. The thesis reports these results together with an
explicit disclosure of the project's real limitations: the Groq free-tier token ceilings, the
pending VROOM optimization step, the non-operational Redis cache, and a regional imbalance in
point-of-interest coverage. The contribution is not a single component but the demonstration
that a compound system — in which the model reasons and the system verifies — can earn a
visitor's trust in a domain where a monolithic chatbot cannot.

**Keywords:** compound AI systems, agentic AI, ReAct, tool use, retrieval grounding, travel
planning, smart tourism, Flutter, FastAPI, Supabase.

## Reading Guide

- **Chapter 1** motivates the trust problem and states the contributions.
- **Chapter 2** reviews the 15-work literature corpus (compound AI, agentic architectures,
  tool use, smart tourism) that frames the design.
- **Chapter 3** details the four-layer methodology as actually implemented (with real file
  paths and function names).
- **Chapter 4** presents the benchmark, A/B, and database-completeness evidence, with honest
  limitations.
- **Chapter 5** concludes with the contributions recap and future work.
- **Chapter 6** is the standalone account of the POI data-pipeline rebuild — the strongest
  single contribution.

All quantitative claims in this thesis trace to files under `thesis/evidence/` (produced by
real test/benchmark/database runs), and all literature claims to the 15 verified works in
`thesis/references.bib`. Items that could not be grounded are marked `[UNVERIFIED]` and listed
in `thesis/HANDOFF_TO_REFINEMENT.md`.
