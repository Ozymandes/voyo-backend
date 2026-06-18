# §4 Citations Used — Results / Evaluation Dossier

> All citation ids below resolve in `thesis/citations/INDEX.md`. Tier per criteria §2.
> Every claim in `dossier.md` and every quote in `evidence-packet.md` traces to one of these
> ids. **Tier D was NOT used** in this dossier.

---

## Tier A — PRIMARY-ACADEMIC (load-bearing; grounds core eval-design claims)

| id | Short name | Venue (cite this way) | Role in §4 |
|---|---|---|---|
| **N1** | ItiNera (Tang et al.) | EMNLP 2024 Industry Track + KDD UrbComp 2024 Best Paper (arXiv:2402.07204) | (a) Motivation for METRICS 1, 3 (LLM-alone cannot plan; "cannot refer to specific POI lists … outdated or hallucinated POIs"; "lack the optimization capabilities required for planning tasks" — Q3). (b) Geographic-coherence metric comparand: Average Margin 86.0 (full) → 242.8 (w/o CSO) — Q5 — anchors METRIC 2 + Claim 4.5.3 (forward-compatible direct comparison). |
| **N4** | PyVRP (Wouda, Lan, Kool) | INFORMS Journal on Computing (arXiv:2403.13795) | (a) VRPTW formalism grounding METRIC 2 (Q4 — problem definition). (b) Optimality reference: 0.40% VRPTW gap (Q5). (c) Honest VROOM-vs-SOTA framing for the "good-enough, not optimal" feasibility claim (Q6). |
| **OSRM-PAPER** | Luxen & Vetter, *Real-time routing with OpenStreetMap data* | ACM SIGSPATIAL GIS 2011 (DOI 10.1145/2093973.2094062) | Academic basis for the travel-time-matrix / shortest-path infrastructure that METRIC 2's feasibility check invokes (Q1 — "real-time and exact shortest path computation on continental sized networks"). Pairs with the S-OSRM software citation. |

## Tier B — SUPPORTING (eval-design comparand only; may NOT carry a core claim alone)

| id | Short name | Venue (cite this way) | Role in §4 |
|---|---|---|---|
| **N5** | AgentTravel (Zhao, Feng, Li) | **NORA / CEUR workshop** ⚠️ label as workshop paper (OpenReview 34kIv0YVNe) | Eval-design comparand ONLY — TravelBench two-axis split (KnowEval = knowledge grounding → METRIC 1 retrieval; TripEval = plan feasibility + personalization + constraint satisfaction → METRICS 2, 3). Q5 anchors the eval template; Q2 anchors the LLM-spatial-failure motivation for METRIC 3; Q4 anchors the e2e surface for METRIC 6. |

## Tier C — SOFTWARE-INFRASTRUCTURE (cite as software; NEVER as an academic paper)

| id | Tool | Citation form | Role in §4 |
|---|---|---|---|
| **S-VROOM** | VROOM | GitHub `VROOM-Project/vroom` + Issue #735 + README | Software substrate of METRIC 2 (feasibility / VRPTW optimization). "No paper exists" confirmation (Issue #735). README "Complex Route Optimization in Milliseconds" supports Claim 4.2.1 sub-ms latency framing. |
| **S-OSRM** | OSRM (the tool) | `project-osrm.org/docs` + README master commit 1c66f8e | Software substrate for the travel-time matrix that METRIC 2's feasibility check invokes (README "Contraction Hierarchies (CH) / Multi-Level Dijkstra (MLD)"). |
| **S-VALHALLA** | Valhalla | `valhalla.github.io` docs | Routing/isochrone substrate referenced alongside OSRM in METRIC 2; primary citation is in §3 (Methodology); appears in §4 only as supporting infra for the feasibility matrix. |

## Tier D — DEPRIORITIZED / PREPRINT-ONLY

**NONE USED.** N2 (TRIP-PAL, arXiv:2406.10196 preprint) and N3 (TravelAgent, Chen et al.,
arXiv:2409.08069 preprint) are deliberately omitted. N5 AgentTravel covers the
eval-design-comparand role without requiring any preprint-only source. (No "Tier-D unavoidably
used" flag needed.)

---

## Citation-locus map (which dossier claim uses which citation)

| Dossier claim | Primary citation | Tier | Locator |
|---|---|---|---|
| 4.1.1 — six-metric-family eval structure | N5 | B | OpenReview 34kIv0YVNe §1 p.2 (Q5) |
| 4.1.2 — KnowEval/TripEval template | N5 | B | OpenReview 34kIv0YVNe §1 pp.1–2 (Q5 + Q7) |
| 4.1.3 — LLM-alone baseline (motivation) | N1 | A | arXiv:2402.07204 §1 p.1 (Q3) |
| 4.1.4 — Average-Margin comparand | N1 | A | arXiv:2402.07204 Table 2 p.6 (Q5) |
| 4.1.5 — VRPTW feasibility formalism + optimality ref | N4 | A | arXiv:2403.13795 §2.2 + §6.2 + §3 (Q4 + Q5 + Q6) |
| 4.2.1 — latency headline (scoring_200_pois) | (number: `02-latency.json`); S-VROOM | C | GitHub VROOM-Project/vroom README |
| 4.2.1a — 13 latency benchmarks PASS | (number: `02-latency.json`) | — | `thesis/evidence/02-latency.json` |
| 4.2.2 — 99-test clean core | (number: `01-test-results.json`) | — | `thesis/evidence/01-test-results.json` |
| 4.2.2a — 8 collection errors (scope limit) | (number: `01-test-results.json`) | — | `thesis/evidence/01-test-results.json` `whole_tree_collection_errors` |
| 4.2.3 — A/B correctness (0 logic divergences) | (number: `03-ab-correctness.json`) | — | `thesis/evidence/03-ab-correctness.json` |
| 4.2.4 — substrate integrity (310 POIs canonical) | (criteria §4); (number: `05-db-completeness.json`) | — | criteria §4 + §5; `thesis/evidence/05-db-completeness.json` |
| METRIC 1 (retrieval) — strategy + threshold | N5, N1 | B, A | OpenReview 34kIv0YVNe §1 p.2 (Q5); arXiv:2402.07204 §1 p.1 (Q3) |
| METRIC 2 (feasibility) — strategy + threshold | N1, N4, OSRM-PAPER, S-VROOM, S-OSRM | A, A, A, C, C | arXiv:2402.07204 T2; arXiv:2403.13795 §2.2/§6.2/§3; Luxen-Vetter abstract; VROOM README; OSRM docs |
| METRIC 3 (reliability) — strategy + threshold | N5, N1 | B, A | OpenReview 34kIv0YVNe §1 pp.1–2 (Q2 + Q5); arXiv:2402.07204 §1 p.1 (Q3) |
| METRIC 4 (provenance) — strategy + threshold | N1 | A | arXiv:2402.07204 §1 p.1 (Q3); number source `narrative_sources.json` |
| METRIC 5 (latency) — ✅ measured now | (number: `02-latency.json`) | — | `thesis/evidence/02-latency.json` |
| METRIC 6 (UX e2e) — strategy + threshold | N5 | B | OpenReview 34kIv0YVNe §1 p.2 (Q4); blocker number `01-test-results.json` |
| 4.5.1 — metric-split reinforces hybrid argument | N1 | A | arXiv:2402.07204 §1 p.1 (Q3) |
| 4.5.2 — honest measured-vs-pending framing | (criteria §5 + §7) | — | `thesis/criteria/thesis-criteria.md` §5 + §7 |
| 4.5.3 — forward-compatible ItiNera/PyVRP comparison | N1, N4 | A, A | arXiv:2402.07204 Table 2 (Q5); arXiv:2403.13795 §6.2 (Q5) |

---

## Pre-flight audit (criteria §2 tier discipline)

- ✅ Every CORE eval-design claim (§4.1, METRICS 1–3, 4.5.1) traces to ≥1 **Tier A** source
  (N1 ItiNera for LLM-alone-cannot-plan motivation + Average-Margin comparand; N4 PyVRP for
  VRPTW feasibility formalism; OSRM-PAPER for matrix-infra academic basis).
- ✅ N5 AgentTravel (Tier B, workshop paper) is used **only** as the eval-design comparand
  (KnowEval/TripEval template); it does NOT carry any core architecture claim alone.
- ✅ N5 is labelled as a "NORA / CEUR workshop paper" in every claim that uses it (criteria §2
  requires this label for any Tier-B AgentTravel appearance).
- ✅ Tier C (S-VROOM, S-OSRM, S-VALHALLA) is cited as **software**, never as a paper. The
  S-VROOM "no paper exists" confirmation (Issue #735) is included verbatim.
- ✅ Tier D (N2, N3) is **not used**. No "unavoidably used" flag is required.
- ✅ The Reflexion "+22% ALFWorld" fabricated stat (criteria §7) does not appear.
- ✅ POI count = **310** everywhere; the stale **255** in `05-db-completeness.json` is flagged
  as STALE and the writer is instructed to use 310 in prose.
- ✅ PENDING metrics (1, 2, 3, 4, 6) report no number; only METRIC 5 and the supporting
  99-test / A/B / substrate-integrity metrics are MEASURED NOW.
