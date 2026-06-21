# Ch3 Methodology — CITATIONS USED

> Every citation id below resolves in `thesis/citations/INDEX.md`. Tier per criteria §2.
> This dossier uses **0 Tier-D sources**; the architecture argument is grounded entirely in
> Tier-A + Tier-B + Tier-C sources per criteria §2.

## Summary by tier

| Tier | Count | IDs | Role in this dossier |
|---|---|---|---|
| **A — Primary-academic (load-bearing)** | 3 | **N1, N4, OSRM-PAPER** | Ground the core contribution claims: hybrid motivation (N1 Q3), VRPTW formalism + VROOM characterisation (N4 Q4/Q5/Q6), contraction-hierarchy algorithm (OSRM-PAPER Q5/Q6/Q7), ablation magnitude precedent (N1 Q5). |
| **B — Supporting (reinforce only)** | 2 | **02 Wang survey, 03 AutoGen** | The four-module agent blueprint (02 Q1–Q4) and the multi-agent-conversation substrate (03 Q1–Q4) that justify CLEO's structure and the LLM-vs-engine role separation. |
| **C — Software infrastructure (cite as software, NEVER a paper)** | 3 | **S-VROOM, S-VALHALLA, S-OSRM** | The three deterministic engines, named per criteria §4 Ch3 requirement: VROOM (VRPTW solver; no paper — Issue #735), Valhalla (isochrones + routing), OSRM (`/table` matrix service). |
| **D — Preprint-only (footnote only)** | 0 | — | None used. N2 TRIP-PAL and N3 TravelAgent deliberately omitted; the architecture argument does not require preprint-only sources. |

---

## Full citation list (resolves in INDEX.md)

### Tier A — load-bearing

- **N1 — ItiNera** (Tang et al.). *EMNLP 2024 Industry Track + KDD UrbComp 2024 Best Paper*;
  arXiv:2402.07204.
  - Quotes used: **Q3** (motivation — LLMs lack optimization capability), **Q5** (CSO
    ablation Table 2 — Average Margin 86.0 → 242.8, the magnitude precedent for §3.5),
    **Q1** (system definition, supporting context).
  - Locators: arXiv:2402.07204 §1 p.1 (Q1,Q3); Table 2 p.6 + discussion p.7 (Q5).
  - INDEX.md resolution: ✅ Tier A, STATUS VERIFIED.

- **N4 — PyVRP** (Wouda, Lan, Kool). *INFORMS Journal on Computing*; arXiv:2403.13795;
  companion DOI 10.1287/ijoc.2023.0055.
  - Quotes used: **Q4** (VRPTW problem definition — "earliest arrival time [...] and latest
    arrival time [...] in between which service should start"), **Q5** (near-optimal solver
    class — 0.40% VRPTW gap, 1st DIMACS VRPTW 2021), **Q6** (academic characterisation of
    VROOM — "unable to compete with state-of-the-art algorithms"), **Q1** (supporting).
  - Locators: arXiv:2403.13795 §2.2 (Q4); §6.1/§6.2 (Q5); §3 (Q6); Abstract (Q1).
  - INDEX.md resolution: ✅ Tier A, STATUS VERIFIED.

- **OSRM-PAPER — Luxen & Vetter**, *Real-time routing with OpenStreetMap data*.
  *ACM SIGSPATIAL GIS 2011*; DOI 10.1145/2093973.2094062; DBLP conf/gis/LuxenV11.
  - Quotes used: **Q5** (CH preprocessing/query time — "queries run in the order of about a
    hundred microseconds"), **Q6** (Vanishing Bottlenecks — "routing is not a bottleneck
    anymore"), **Q7** (Dijkstra scaling motivation), **Q1** (abstract, supporting).
  - Locators: Luxen & Vetter 2011 §Contraction Hierarchies / §Vanishing Bottlenecks / §Introduction
    (body); DOI 10.1145/2093973.2094062.
  - INDEX.md resolution: ✅ Tier A, STATUS **FULL-TEXT VERIFIED 2026-06-17** (abstract + body
    via provided PDF + Wayback cross-check).

### Tier B — supporting

- **02 — Wang Agent Survey** (Wang et al.). *Frontiers of Computer Science* 18:186345 (2024);
  arXiv:2308.11432.
  - Quotes used: **Q1** (four-module blueprint), **Q2** (module interaction), **Q3** (profiling
    module purpose), **Q4** (memory module).
  - Locators: arXiv:2308.11432 §2.1 Architecture (Q1,Q2,Q4); §2.1.1 (Q3).
  - INDEX.md resolution: ✅ Tier B (Tier A *within* the agentic-architecture theme per INDEX.md
    tiering note; used here as supporting for the CLEO-structure blueprint).

- **03 — AutoGen** (Wu et al.). arXiv:2308.08155.
  - Quotes used: **Q1** (agent properties), **Q2** (conversation as substrate), **Q3** (core
    insight), **Q4** (agent composition).
  - Locators: arXiv:2308.08155 Abstract (Q1,Q2); §1 Introduction (Q3); Figure 1 caption (Q4).
  - INDEX.md resolution: ✅ Tier B (Tier A within the agentic-architecture theme).

### Tier C — software infrastructure (NEVER a paper)

- **S-VROOM — VROOM** (Vehicle Routing Open-source Optimisation Machine). Maintainer Julien
  Coupey (`jcoupey`), Verso. C++20. https://github.com/VROOM-Project/vroom.
  - Sources used: README (lines 1–11 — "Complex Route Optimization in Milliseconds / Good
    solutions, fast. [...] open-source route optimization engine written in C++20 that solves
    complex vehicle routing problems (VRP) in milliseconds"); **Issue #735** (comment by
    `jcoupey` 2022-07-07 — "No, there is no paper associated with the project.").
  - ⚠️ **No paper exists for VROOM — never invent one.** The academic characterisation comes
    from N4 Q6 (PyVRP's Related Projects section), NOT from a VROOM-authored paper.
  - INDEX.md resolution: ✅ Tier C, STATUS VERIFIED.

- **S-VALHALLA — Valhalla** (open-source routing engine). https://valhalla.github.io.
  - Sources used: Isochrone API overview ("computes areas that are reachable within specified
    time intervals from a location, and returns the reachable regions as contours of polygons
    or lines"); matrix API endpoint (referenced for the distance-matrix service that feeds
    VROOM).
  - INDEX.md resolution: ✅ Tier C, STATUS VERIFIED.

- **S-OSRM — OSRM** (Open Source Routing Machine). https://project-osrm.org/docs/v5.24.0/api/.
  - Sources used: `/table` service ("Computes the duration of the fastest route between all
    pairs of supplied coordinates [...] distances are not the shortest distance between two
    coordinates, but rather the distances of the fastest routes"); README (CH + MLD pipeline
    enumeration).
  - INDEX.md resolution: ✅ Tier C, STATUS VERIFIED. Paired with OSRM-PAPER (Tier A) for the
    algorithm citation per criteria §2.

### Tier D — preprint-only

**None used.** The dossier deliberately omits N2 (TRIP-PAL) and N3 (TravelAgent) because:
- The architecture argument does not require preprint-only sources — N1 (ItiNera, Tier A) is
  the closest peer-reviewed precedent and grounds the same "LLM-alone cannot plan" claim.
- Criteria §2 restricts Tier-D usage to "explicitly-labelled 'arXiv preprint, not
  peer-reviewed' footnote" and notes "Prefer ItiNera for the same point."
- No Tier-D footnote was needed in Ch3; the closest-precedent role is fully covered by N1.

---

## Cross-chapter reference (cited in Ch2, not re-cited in Ch3 body)

- **04 — TravelPlanner** (Xie et al.), *ICML 2024*. Cited in Ch2 T3 for the GPT-4 0.6% success
  rate on constrained travel planning. Referenced in Ch3 §3.3.1 as independent corroboration
  of N1 Q3 ("LLMs lack the optimization capabilities required for planning tasks") — but cited
  as a *reference back* to Ch2, not re-introduced. INDEX.md resolution: ✅ Tier A within the
  agentic-architecture theme.

---

## Honesty / non-fabrication attestations

1. **No Tier-D used as core evidence.** The architecture argument is grounded entirely in
   Tier-A (N1, N4, OSRM-PAPER) + Tier-B (02, 03) + Tier-C (S-VROOM, S-VALHALLA, S-OSRM).
2. **No paper invented for VROOM.** S-VROOM is cited as software (Issue #735 confirms no
   paper); the academic characterisation comes from N4 Q6 (PyVRP's Related Projects section).
3. **OSRM-PAPER body quotes are FULL-TEXT VERIFIED 2026-06-17** — Q5/Q6/Q7 are quotable
   (criteria §2 / INDEX.md OSRM-PAPER row).
4. **No fabricated Reflexion stat.** Reflexion (05) is not in the Ch3 required-citations
   list and is not cited; the fabricated "+22% ALFWorld" stat therefore cannot appear.
5. **POI count = 310 everywhere** per criteria §4. The dossier does NOT introduce 255; the
   stale evidence files (05/06/07/_GROUNDING_MAP) are flagged for regeneration but their stale
   count is not propagated into Ch3 output.
6. **Ablation numbers are now MEASURED (2026-06-20).** The eval harness ran on gpt-4o-mini
   via OPTO. Headline (from `thesis/evidence/07-eval-results.json`): travel-time feasibility
   83.2% (full) vs 47.7% (LLM-only), Δ +35.6 pp; opening-hours feasibility 91.3% vs 84.7%;
   margin penalty 172 vs 434. These resolve the former PENDING — the writer may now quote
   them in §3.5.6 and cross-reference §4.6.1.

---

## ADDENDUM 2026-06-20: new citations for §3.2.5 (eval model) + §3.5.2a/b (paired design)

| §3.x claim | Citation id | Tier | Locator |
|---|---|---|---|
| §3.2.5 — eval backend model (gpt-4o-mini via OPTO) | (number: `07-eval-results.json`) | — | `thesis/evidence/07-eval-results.json` `_meta` |
| §3.2.5 — factory switch (zero demo regression) | (codebase) | — | `src/cleo/config.py` `OptoClient` + `get_llm_client()` |
| §3.5.2a — paired-design provenance | (number: `07-eval-results.json`) | — | `thesis/evidence/07-eval-results.json` `ablation.provenance` |
| §3.5.2a — provenance seam | (codebase) | — | `src/itinerary/safarny_planner.py` `result.provenance` |
| §3.5.2b — travel-time feasibility metric | (codebase) | — | `scripts/testing/voyo_eval/metrics.py` `travel_time_feasibility()` |
| §3.5.7 — keystone chart (now produced) | (figure) | — | `thesis/figures/eval/ablation_ablation_headline.pdf` |
