# §5 Citations Used — Conclusion Dossier

> All citation ids below resolve in `thesis/citations/INDEX.md`. Tier per criteria §2.
> Every claim in `dossier.md` and every quote in `evidence-packet.md` traces to one of these
> ids. **Tier D was NOT used** in this dossier.
>
> **Ch5 makes NO new claims (criteria §4 Ch5 row).** Every academic citation below is
> *restated* from Ch1–Ch4; this file documents which already-cited sources the conclusion
> leans on for its synthesis.

---

## Tier A — PRIMARY-ACADEMIC (load-bearing; grounds the restated contribution)

| id | Short name | Venue (cite this way) | Role in §5 |
|---|---|---|---|
| **N1** | ItiNera (Tang et al.) | EMNLP 2024 Industry Track + KDD UrbComp 2024 Best Paper (arXiv:2402.07204) | (a) The hybrid-deterministic motivation (§5.1.2): pure LLMs "cannot refer to specific POI lists, resulting in outdated or hallucinated POIs"; "lack the optimization capabilities required for planning tasks" — Q3. (b) The closest precedent + class-upgrade framing (§5.1.3): CSO solves a hierarchical TSP — Q4; VOYO upgrades to VRPTW. (c) The borrowed-evidence baseline for the keystone ablation (§5.2.3, §5.3.1): Average Margin 86.0 (full) → 242.8 (w/o CSO) — Q5, Table 2 p.6. (d) Cross-geography precedent for §5.3.5 (OUIP framing is geography-agnostic — Q1). |
| **N4** | PyVRP (Wouda, Lan, Kool) | INFORMS Journal on Computing (arXiv:2403.13795) | (a) VRPTW problem class justification (§5.1.4): Q4 VRPTW definition. (b) Optimality reference (§5.1.4): Q5 — 0.40% VRPTW gap, 1st in DIMACS 2021 (Q1). (c) Honest VROOM-vs-SOTA framing (§5.1.6): Q6 — VROOM "aims to provide good solutions to real-life VRPs" but "is unable to compete with state-of-the-art algorithms". (d) Comparand for §5.3.2 (Q5 — pre-committed optimality reference). |
| **OSRM-PAPER** | Luxen & Vetter, *Real-time routing with OpenStreetMap data* | ACM SIGSPATIAL GIS 2011 (DOI 10.1145/2093973.2094062) | Routing/matrix infrastructure academic basis (§5.1.5 + §5.2.2-METRIC-2): Q1 — "real-time and exact shortest path computation on continental sized networks"; Q5 — CH preprocessing minutes / queries ~100 µs; Q6 — "routing is not a bottleneck anymore". Pairs with the S-OSRM software citation. |

## Tier B — SUPPORTING (eval-design comparand only; may NOT carry a core claim alone)

| id | Short name | Venue (cite this way) | Role in §5 |
|---|---|---|---|
| **N5** | AgentTravel (Zhao, Feng, Li) | **NORA / CEUR workshop paper** ⚠️ label as workshop paper (OpenReview 34kIv0YVNe) | Eval-design comparand ONLY for the PENDING metric families (§5.2.2): Q5 TravelBench two-axis split (KnowEval = retrieval → METRIC 1; TripEval = feasibility/personalization/constraint-satisfaction → METRICS 2, 3); Q2 LLM spatial-reasoning failure (motivation for METRIC 3); Q4 TravelAgent online planner (the e2e surface METRIC 6 exercises). Reused as the methodological comparand for §5.3.2. |

## Tier C — SOFTWARE-INFRASTRUCTURE (cite as software; NEVER as an academic paper)

| id | Tool | Citation form | Role in §5 |
|---|---|---|---|
| **S-VROOM** | VROOM | GitHub `VROOM-Project/vroom` + Issue #735 + README master branch | Software substrate of the optimize stage (§5.1.6): README "Complex Route Optimization in Milliseconds / Good solutions, fast"; Issue #735 verbatim "No, there is no paper associated with the project" (jcoupey 2022-07-07) — defends VOYO from inventing a VROOM paper. |
| **S-OSRM** | OSRM (the tool) | `project-osrm.org/docs` + README master commit 1c66f8e | Software substrate for the travel-time matrix invoked by METRIC 2's feasibility check (§5.1.5 + §5.2.2-METRIC-2): README "Contraction Hierarchies (CH) / Multi-Level Dijkstra (MLD)" pipeline enumeration. |
| **S-VALHALLA** | Valhalla | `valhalla.github.io` Isochrone API overview | Isochrones + routing software substrate, paired with S-OSRM (§5.1.5 + §5.2.2-METRIC-2). |

## Tier D — DEPRIORITIZED / PREPRINT-ONLY

**NONE USED.** N2 (TRIP-PAL, arXiv:2406.10196 preprint) and N3 (TravelAgent, Chen et al.,
arXiv:2409.08069 preprint) are deliberately omitted. The conclusion is a synthesis chapter
that reuses Tier-A/B/C sources already cited in Ch1–Ch4; no preprint-only source is needed.
(No "Tier-D unavoidably used" flag is required.)

---

## Internal cross-references (NOT academic citations — pointers to prior chapters)

Because Ch5 makes no new claims, each §5 claim traces to a prior chapter's already-cited
claim. These pointers are the audit trail the supervisor checks:

| Ch5 claim | Origin chapter | Underlying academic citation (Tier) |
|---|---|---|
| 5.1.1 hybrid-deterministic thesis (verbatim) | criteria §1; restated Ch1/Ch2/Ch3 | criteria §1 (the spine) |
| 5.1.2 LLM-alone cannot plan | Ch1 motivation; Ch2.2.T2; Ch2.3; Ch3; Ch4 §4.1.3 | N1 Q3 (Tier A) |
| 5.1.3 closest precedent + class upgrade | Ch2.2.T2-3 / T2-4; Ch2.3-1 / §2.3-7 | N1 Q1 + Q4 + Q5 (Tier A) |
| 5.1.4 VRPTW problem class | Ch2.3-2 / Ch2.3-3; Ch4 §4.1.5 | N4 Q4 + Q1 + Q5 (Tier A) |
| 5.1.5 routing/matrix infra | Ch2.3-5 / Ch2.3-6; Ch3 infra wiring | OSRM-PAPER Q1/Q5/Q6 (Tier A) + S-OSRM + S-VALHALLA (Tier C) |
| 5.1.6 VROOM honest software | Ch2.3-4; Ch3 optimize stage | S-VROOM README + Issue #735 (Tier C); N4 Q6 (Tier A) |
| 5.1.7 three operational pillars | Ch3 methodology; Ch6 data pipeline | criteria §4 (POI=310, dual-price=58); N1 Q3 (Tier A) |
| 5.2.1 measured-now evidence | Ch4 §4.2 | `evidence/02-latency.json`; `01-test-results.json`; `03-ab-correctness.json`; `05-db-completeness.json`; S-VROOM README (Tier C) |
| 5.2.2 METRICS 1,2,3,4,6 (PENDING) | Ch4 §4.3 | criteria §5; N1 Q3 (Tier A); N4 Q4+Q5+Q6 (Tier A); OSRM-PAPER Q1 (Tier A); N5 Q5+Q2+Q4 (Tier B, workshop); S-VROOM+S-OSRM+S-VALHALLA (Tier C) |
| 5.2.3 keystone ablation PENDING | criteria §5 (new keystone); Ch4 §4.1.4 (ItiNera baseline) | criteria §5; N1 Q5 (Tier A — 86→242.8 borrowed-evidence baseline) |
| 5.2.4 secondary (substrate) limitations | Ch3 + Ch6 honest-gaps | `evidence/05-db-completeness.json`; `evidence/01-test-results.json`; `evidence/_GROUNDING_MAP.md` |
| 5.3.1 run the ablation | criteria §5 (keystone protocol) | criteria §5; N1 Q3 + Q5 (Tier A) |
| 5.3.2 run the full eval harness | Ch4 §4.5.3 (pre-committed comparands) | criteria §5; N1 Q5 (Tier A); N4 Q5 (Tier A); N5 Q5 (Tier B, workshop) |
| 5.3.3 extend the substrate | Ch6 data-pipeline contribution | criteria §4 (58/76) + §5 (≥85%) |
| 5.3.4 lift free-tier ceilings | Ch4 §4.2.2a; Ch3 §3.4 | `evidence/01-test-results.json`; `evidence/_GROUNDING_MAP.md` |
| 5.3.5 generalize the pattern | Ch1 / Ch2.3 contribution framing | N1 Q1 (Tier A); criteria §1 |

---

## Citation-locus map (which §5 claim uses which academic citation)

| §5 claim | Primary academic citation | Tier | Locator |
|---|---|---|---|
| 5.1.1 hybrid-deterministic thesis | (criteria §1 spine; no academic cite by itself) | — | `thesis/criteria/thesis-criteria.md` §1 |
| 5.1.2 LLM-alone cannot plan | N1 | A | arXiv:2402.07204 §1 p.1 (Q3) |
| 5.1.3 closest precedent + class upgrade | N1 | A | arXiv:2402.07204 Abstract + §3.5 p.4 + Table 2 p.6 (Q1+Q4+Q5) |
| 5.1.4 VRPTW problem class + optimality ref | N4 | A | arXiv:2403.13795 §2.2 + Abstract + §6.2 (Q4+Q1+Q5) |
| 5.1.5 routing/matrix infra (algorithm) | OSRM-PAPER | A | DOI 10.1145/2093973.2094062 Abstract + §CH + §Vanishing Bottlenecks (Q1+Q5+Q6) |
| 5.1.5 routing/matrix infra (software) | S-OSRM; S-VALHALLA | C | project-osrm.org README; valhalla.github.io |
| 5.1.6 VROOM honest software + non-SOTA | S-VROOM (cross-cite N4) | C (+A) | VROOM README + Issue #735; arXiv:2403.13795 §3 (Q6) |
| 5.1.7 three operational pillars | N1 (plus criteria §4 numbers) | A (+criteria) | arXiv:2402.07204 §1 p.1 (Q3); criteria §4 |
| 5.2.1 latency headline | (number: `02-latency.json`); S-VROOM | C | VROOM README |
| 5.2.1 13-benchmark table | (number: `02-latency.json`) | — | `thesis/evidence/02-latency.json` |
| 5.2.1 99-test clean core | (number: `01-test-results.json`) | — | `thesis/evidence/01-test-results.json` `core_suite` |
| 5.2.1 8 collection errors | (number: `01-test-results.json`) | — | `thesis/evidence/01-test-results.json` `whole_tree_collection_errors` |
| 5.2.1 A/B correctness | (number: `03-ab-correctness.json`) | — | `thesis/evidence/03-ab-correctness.json` |
| 5.2.1 substrate integrity (310 canonical) | (criteria §4); (number: `05-db-completeness.json`) | — | criteria §4 + §5; `thesis/evidence/05-db-completeness.json` |
| 5.2.2-METRIC-1 retrieval (PENDING) | N1; N5 | A; B | arXiv:2402.07204 §1 p.1 (Q3); OpenReview 34kIv0YVNe §1 p.2 (Q5) |
| 5.2.2-METRIC-2 feasibility (PENDING) | N1; N4; OSRM-PAPER; S-VROOM; S-OSRM; S-VALHALLA | A; A; A; C; C; C | arXiv:2402.07204 T2; arXiv:2403.13795 §2.2/§6.2/§3; Luxen-Vetter Abstract; VROOM README; OSRM docs; Valhalla docs |
| 5.2.2-METRIC-3 reliability (PENDING) | N5; N1 | B; A | OpenReview 34kIv0YVNe §1 pp.1–2 (Q2+Q5); arXiv:2402.07204 §1 p.1 (Q3) |
| 5.2.2-METRIC-4 provenance (PENDING) | N1 | A | arXiv:2402.07204 §1 p.1 (Q3); number source `narrative_sources.json` (pre-enrich probe) |
| 5.2.2-METRIC-6 UX e2e (PENDING) | N5 | B | OpenReview 34kIv0YVNe §1 p.2 (Q4); blocker `01-test-results.json` |
| 5.2.3 keystone ablation (PENDING) | N1 | A | arXiv:2402.07204 Table 2 p.6 (Q5 — 86→242.8 baseline); criteria §5 protocol |
| 5.2.4-a substrate regional imbalance | (number: `05-db-completeness.json`) | — | `thesis/evidence/05-db-completeness.json` `regional_distribution` + `honest_gaps_summary` |
| 5.2.4-b free-tier ceilings | (number: `01-test-results.json`; `_GROUNDING_MAP.md`) | — | `thesis/evidence/01-test-results.json`; `thesis/evidence/_GROUNDING_MAP.md` §3 + §5 |
| 5.2.4-c semantically-correct nulls | (number: `05-db-completeness.json`) | — | `thesis/evidence/05-db-completeness.json` `field_completeness` + `honest_gaps_summary` |
| 5.3.1 run the ablation | N1 | A | arXiv:2402.07204 §1 p.1 + Table 2 p.6 (Q3+Q5); criteria §5 protocol |
| 5.3.2 run the full eval harness | N1; N4; N5 | A; A; B | arXiv:2402.07204 T2; arXiv:2403.13795 §6.2; OpenReview 34kIv0YVNe §1 p.2; criteria §5 |
| 5.3.3 extend the substrate | (criteria §4 + §5) | — | `thesis/criteria/thesis-criteria.md` §4 + §5 |
| 5.3.4 lift free-tier ceilings | (numbers as in 5.2.4-b) | — | same evidence files |
| 5.3.5 generalize the pattern | N1 | A | arXiv:2402.07204 Abstract (Q1); criteria §1 |

---

## Pre-flight audit (criteria §2 tier discipline + criteria §4 Ch5 "no new claims")

- ✅ **Ch5 introduces NO new academic claim.** Every claim in `dossier.md` traces to an
  already-cited claim in Ch1–Ch4 (audit trail in the "Internal cross-references" table
  above). The conclusion's value is synthesis, per criteria §4 Ch5 row "no new claims."
- ✅ Every restated CORE contribution claim (§5.1.2, §5.1.4, §5.1.6, §5.2.3, §5.3.1) traces to
  ≥1 **Tier A** source (N1 ItiNera for the LLM-alone-cannot-plan motivation + Average-Margin
  baseline; N4 PyVRP for the VRPTW problem class + optimality reference + honest VROOM-vs-SOTA
  framing; OSRM-PAPER for the matrix-infra algorithm).
- ✅ N5 AgentTravel (Tier B, **workshop paper**) is used **only** as the eval-design comparand
  for the PENDING metric families; it does NOT carry any core architecture claim alone. N5 is
  labelled "NORA / CEUR workshop paper" in every claim that uses it (criteria §2).
- ✅ Tier C (S-VROOM, S-OSRM, S-VALHALLA) is cited as **software**, never as a paper. The
  S-VROOM "no paper exists" confirmation (Issue #735, jcoupey 2022-07-07) is included verbatim
  in `evidence-packet.md` §B and is the citation that defends the dossier from inventing a
  VROOM paper.
- ✅ Tier D (N2 TRIP-PAL, N3 TravelAgent) is **not used**. No "unavoidably used" flag is
  required.
- ✅ The Reflexion "+22% ALFWorld" fabricated stat (criteria §7) does not appear (Reflexion is
  not used in Ch5).
- ✅ The Liu "+35% feature discovery" non-finding (criteria §7) does not appear (Liu is not
  used in Ch5).
- ✅ The Pai "0.69" discriminant-validity correlation (criteria §7) does not appear (Pai is
  not used in Ch5).
- ✅ **POI count = 310 everywhere** (criteria §4 stale-number sweep). The stale **255** in
  `thesis/evidence/05-db-completeness.json` is explicitly flagged in `dossier.md` §5.2.1 /
  §5.2.4 and in `evidence-packet.md` §D.2; the writer is instructed to use 310 in prose and
  flag the 255 counts as the pre-refresh snapshot.
- ✅ **Dual gov.eg prices = 58; gov.eg descriptions = 76; any-enrichment = 97** (criteria §4)
  — used verbatim in §5.3.3; no other enrichment count is invented.
- ✅ **All five PENDING metric families (METRICS 1, 2, 3, 4, 6) AND the keystone ablation
  report NO NUMBER** — only strategy + threshold + blocker. The ItiNera 86→242.8 figure is
  explicitly framed as a *borrowed-evidence baseline* (a published peer-reviewed number), not
  a VOYO measurement.
- ✅ **Only the measured-now metrics carry numbers** (latency p95 1.662 ms; 99/99 tests; 0
  A/B divergences; 310-POI substrate integrity), and each is sourced verbatim from
  `thesis/evidence/`.
