# §5 Conclusion — CITED ARGUMENT OUTLINE

> **Section thesis sentence (the spine every subsection must reinforce — restated verbatim
> from criteria §1; this chapter introduces NO new claims):** *VOYO couples an LLM (CLEO —
> for intent parsing and personalization only) to deterministic optimization engines (Valhalla
> for isochrones and routing; VROOM for VRP/VRPTW feasibility and time-window-constrained
> optimization; OSRM for distance/travel-time matrices), because an LLM alone cannot reliably
> plan — it lacks optimization capability and hallucinates geography and constraints.*
> [citation: criteria §1 → thesis-criteria.md §1] [citation: N1 → Q3 (LLMs "lack the
> optimization capabilities required for planning tasks" and "cannot refer to specific POI
> lists, resulting in outdated or hallucinated POIs")].
>
> **Per criteria §4 (Ch5 row), this chapter makes NO NEW CLAIMS.** Every claim in this dossier
> restates evidence already grounded in Ch1–Ch4; each is cross-referenced to the chapter of
> origin. The conclusion's value is *synthesis*, not new argument.
>
> This dossier is an **evidence packet for the human thesis writer, NOT final thesis prose.**
> Each numbered claim ends with a citation id → locator (resolvable in
> `thesis/citations/INDEX.md`) and a one-line "phrase it as" note. Verbatim text the writer
> should copy lives in `evidence-packet.md`; figures/tables in `figures-spec.md`.

## Tier map for this dossier (admissibility per criteria §2)

- **Tier A — load-bearing (may ground core contribution claims):** N1 ItiNera; N4 PyVRP;
  OSRM-PAPER.
- **Tier B — supporting (reinforce only; cannot carry a core claim alone):** N5 AgentTravel
  (label "workshop paper").
- **Tier C — software-infrastructure (cite as software; NEVER as a paper):** S-VROOM,
  S-VALHALLA, S-OSRM.
- **Tier D — preprint-only (footnote only, explicitly labelled; never core evidence):**
  **NONE USED** in this dossier.
- **Internal cross-references:** Ch1–Ch4 dossiers (`thesis/ch2-background/dossier.md`,
  `thesis/ch4-results/dossier.md`), `thesis/criteria/thesis-criteria.md` §1, §4, §5, §7, and
  `thesis/evidence/` for every number. These are used because this chapter makes no new
  claims — they are not "citations" in the academic sense but pointers to the prior chapters'
  already-cited evidence; each pointer is followed by the underlying academic citation that
  the original chapter used.

---

# §5.1 — Restating the hybrid-deterministic contribution

> **Subsection thesis sentence:** *The contribution is a separation of concerns — the LLM owns
> intent + personalization, deterministic engines own everything that must be correct — and
> this separation is grounded in published, peer-reviewed evidence that an LLM alone cannot
> plan.*

**5.1.1 — The hybrid-deterministic thesis (restated).** VOYO's contribution is *not* "an LLM
that plans trips." It is the architectural separation of probabilistic and deterministic
computation: the LLM (CLEO conversational layer) handles intent parsing, preference/memory
state, and human-readable response composition; deterministic engines (Valhalla for
isochrones and routing, VROOM for VRPTW feasibility and time-window optimization, OSRM for
distance/travel-time matrices) handle reachability, routing, isochrones, matrices,
feasibility, and time-window optimization.
- *How to phrase:* Open §5.1 with this one-sentence restatement; it is the verbatim thesis
  sentence from criteria §1 / Ch1 / Ch2 / Ch3 — do not embellish or extend.
- *Citation:* [citation: criteria §1 → thesis-criteria.md §1] [citation: criteria §4 (Ch5 row
  "no new claims") → thesis-criteria.md §4]. **Tier: criteria file (the spine).**

**5.1.2 — The motivation: an LLM alone cannot plan (Tier A, load-bearing).** ItiNera — the
closest peer-reviewed precedent (EMNLP 2024 Industry Track + KDD UrbComp 2024 Best Paper) —
explicitly identifies the two failure modes VOYO's architecture is designed to prevent: pure
LLMs "cannot refer to specific POI lists, resulting in outdated or hallucinated POIs," and
"lack the optimization capabilities required for planning tasks, leading to suboptimal
itineraries." VOYO's hybrid-deterministic split is the operational answer to this published
diagnosis. *(Restates Ch1 motivation, Ch2.2.T2, Ch2.3 opener, Ch3 architecture rationale,
Ch4 §4.1.3 baseline motivation.)*
- *How to phrase:* Verbatim quote (do not paraphrase). This is the single load-bearing
  sentence the whole thesis turns on.
- *Citation:* [citation: N1 → Q3, arXiv:2402.07204 §1 p.1] (Tier A; load-bearing — same
  citation used in Ch1, Ch2.2.T2, Ch2.3, Ch3, Ch4).

**5.1.3 — The closest precedent confirms the LLM-coupled-to-solver pattern (Tier A).** ItiNera
itself "integrates spatial optimization with large language models," with a Cluster-aware
Spatial Optimization (CSO) module solving a "hierarchical traveling salesman problem"; its
ablation shows removing the optimizer triples route detour (Average Margin 86.0 → 242.8). VOYO
instantiates the same LLM-coupled-to-solver insight for Egyptian tourism, but at a stricter
optimizer class (VRPTW, not TSP). *(Restates Ch2.2.T2-3/T2-4 and Ch2.3-1/§2.3-7.)*
- *How to phrase:* Position VOYO as the same insight, not as a competitor; emphasize the
  class upgrade (hierarchical TSP → VRPTW with time windows).
- *Citation:* [citation: N1 → Q1, arXiv:2402.07204 Abstract; N1 → Q4, §3.5 p.4; N1 → Q5,
  Table 2 p.6] (Tier A).

**5.1.4 — VRPTW is a well-defined, near-optimally-solvable OR family (Tier A).** VOYO frames
itinerary optimization as a VRP with time windows: each POI has a service time and an
[earliest, latest] arrival window — exactly PyVRP's published VRPTW definition — and
near-optimal solutions exist (PyVRP reports a 0.40% mean gap on standard VRPTW benchmarks;
HGS ranked 1st in the 2021 DIMACS VRPTW challenge). This is the formal justification for
delegating feasibility to a VRPTW-class solver rather than to the LLM. *(Restates Ch2.3-2 /
Ch2.3-3 and Ch4 §4.1.5.)*
- *How to phrase:* State VRPTW as the *correct problem class* for tourism itinerary planning;
  cite the optimality reference to justify that feasibility is achievable in practice.
- *Citation:* [citation: N4 → Q4 (§2.2 VRPTW definition) + Q1 (Abstract — 1st in DIMACS) +
  Q5 (§6.2 VRPTW 0.40% gap), arXiv:2403.13795] (Tier A).

**5.1.5 — The routing/matrix infrastructure is real-time and exact (Tier A + Tier C).** The
travel-time matrices and routing VOYO delegates to OSRM/Valhalla rest on the published
Contraction-Hierarchy algorithm: continental-scale preprocessing in minutes; queries in "the
order of about a hundred microseconds"; "routing is not a bottleneck anymore." The running
OSRM/Valhalla tooling exposes these algorithms as the matrix and isochrone services VOYO
consumes. *(Restates Ch2.3-5 / Ch2.3-6 and Ch3 infrastructure wiring.)*
- *How to phrase:* Pair the academic algorithm (OSRM-PAPER) with the running software (S-OSRM,
  S-VALHALLA) — never conflate the two; both are needed.
- *Citation:* [citation: OSRM-PAPER → Q1 (Abstract "real-time and exact shortest path
  computation on continental sized networks") + Q5 (CH preprocessing minutes / queries ~100 µs)
  + Q6 ("routing is not a bottleneck anymore"), DOI 10.1145/2093973.2094062] (Tier A);
  [citation: S-OSRM → project-osrm.org/docs] (Tier C);
  [citation: S-VALHALLA → valhalla.github.io Isochrone API overview] (Tier C).

**5.1.6 — VROOM is honest software: fast and practical, not state-of-the-art (Tier C +
cross-cited via Tier A).** VROOM is VOYO's chosen solver — purpose-built for fast real-life
VRPs ("Complex Route Optimization in Milliseconds"), and the academic characterization from
PyVRP (Tier A) is that VROOM "aims to provide good solutions to real-life VRPs" but "is unable
to compete with state-of-the-art algorithms." This trade-off is defensible for itinerary
planning, which needs real-time "good-enough" feasible routes, not provably-optimal ones.
**No paper exists for VROOM** (maintainer confirmed verbatim in GitHub Issue #735).
*(Restates Ch2.3-4 and Ch3 optimize stage.)*
- *How to phrase:* Be explicit about VROOM's tier (software) and its non-SOTA status; this is
  the honest framing that defends VOYO's feasibility (not optimality) claim.
- *Citation:* [citation: S-VROOM → README "Complex Route Optimization in Milliseconds /
  Good solutions, fast" + Issue #735 "No, there is no paper associated with the project"
  (jcoupey 2022-07-07); cross-cite N4 → Q6, arXiv:2403.13795 §3 "Related Projects"] (Tier C +
  Tier A).

**5.1.7 — The contribution's three operational pillars (synthesis; restates Ch3).** VOYO
delivers three concrete, measurable artifacts that operationalize the hybrid-deterministic
thesis: (i) a **verified 310-POI Egyptian substrate** with dual Egyptian/foreigner pricing
(58 POIs enriched with dual gov.eg prices); (ii) a **deterministic curate→optimize pipeline**
(recommendation engine + VROOM VRPTW solver + Valhalla/OSRM matrix); and (iii) a **CLEO
conversational layer** that owns intent + personalization only, grounded by a force-tool
policy that prevents the LLM from authoring feasibility, geography, or prices. *(Restates
Ch3 methodology and Ch6 data-pipeline contribution.)*
- *How to phrase:* The closing synthesis paragraph of §5.1 — three bullets, each pointing back
  to its chapter of origin.
- *Citation:* [citation: criteria §4 (Ch6 row: POI count = 310, dual-price count = 58) →
  thesis-criteria.md §4] (criteria file; the canonical numbers);
  [citation: N1 → Q3 (the LLM-must-not-own-POIs/feasibility principle)] (Tier A — anchors the
  force-tool grounding).

---

# §5.2 — Limitations (the main limitation = the held evaluation harness)

> **Subsection thesis sentence:** *The thesis's principal limitation is that the
> hybrid-deterministic contribution is argued on architecture and on a measured deterministic
> substrate, but its end-to-end empirical validation — the six metric families of Ch4, plus the
> keystone full-hybrid vs LLM-only ablation — is gated on a planned evaluation harness that has
> not yet been run. No measurement is fabricated to fill this gap; PENDING metrics are labelled
> PENDING with the blocker.*

**5.2.1 — The headline measured evidence (restates Ch4 §4.2; ✅ MEASURED NOW).** What *is*
measured today establishes that the **deterministic substrate** is correct and effectively
free at low-hundreds-POI scale:

- **Latency:** full recommendation-scoring over 200 POIs = median **0.7501 ms**, p95 **1.662 ms**,
  ≈300× under the 500 ms p95 threshold; all 13 backend benchmarks PASS.
  [citation: evidence → `thesis/evidence/02-latency.json` `benchmarks.scoring_200_pois` (and
  all 13 `benchmarks.*` entries); criteria §5 Latency row "✅ measurable now"];
  [citation: S-VROOM → README "Complex Route Optimization in Milliseconds"] (Tier C — explains
  *why* sub-ms problem build is possible).
- **Regression correctness:** deterministic core = **99 tests, 100% passing, 0 failures, 0
  errors, in 8.53 s** (pytest 9.0.3, Python 3.10.6). Eight additional integration/e2e/tool
  tests require live Groq LLM + live Supabase/Redis and are explicitly excluded from the
  99-test headline (free-tier scope limit, NOT code defects).
  [citation: evidence → `thesis/evidence/01-test-results.json` `core_suite` +
  `whole_tree_collection_errors`].
- **A/B correctness:** the recommendation engine discriminates between user profiles as
  designed (0 logic divergences across 4 A/B scenarios); proven qualitatively, not as a
  quality headline.
  [citation: evidence → `thesis/evidence/03-ab-correctness.json`].
- **Substrate integrity:** **310 active POIs** (canonical post-rebuild count per criteria §4),
  0 duplicates, 0 dict-wrapped fields, 0 capped review counts, 0 invalid category enums; all
  six most-famous sites carry permanent Wikimedia imagery and real review counts (20k–64k).
  ⚠️ `thesis/evidence/05-db-completeness.json` still reports the **stale** `total_active_pois:
  255`; **the writer MUST use 310 everywhere and never 255** (criteria §4 stale-number sweep).
  [citation: criteria §4 (POI = 310) + §5 (DB completeness row "⚠️ regenerate (was 255)") →
  thesis-criteria.md §4 + §5]; [citation: evidence → `thesis/evidence/05-db-completeness.json`
  `famous_six_summary` + `honest_gaps_summary`].

*How to phrase:* Group as "what is already proven" — the deterministic substrate is correct
and free; the user-perceived latency budget is consumed by the LLM (CLEO) and live services,
which is *exactly* the separation-of-concerns the hybrid argument predicts (restates Ch4
§4.2.1a).

**5.2.2 — The main limitation: five PENDING metric families (restates Ch4 §4.3; ⏸ PENDING).**
The end-to-end empirical validation of the hybrid-deterministic contribution is gated on a
planned evaluation harness and on the Windows enrichment run. **No number is reported for any
PENDING metric — only strategy + threshold + blocker.** These five metric families are:

1. **METRIC 1 — Retrieval quality (P@k / Recall / nDCG).** Strategy: harness runs the
   recommendation engine over a fixed profile set, computes IR metrics against a human-curated
   relevance set built from the 310-POI substrate. **Threshold: P@5 ≥ 0.7. Status: PENDING the
   evaluation harness.** Designed to catch the ItiNera-Q3 "outdated or hallucinated POIs"
   failure; methodologically analogous to AgentTravel's *KnowEval*.
   [citation: criteria §5 (Retrieval row "⏸ PENDING eval harness") → thesis-criteria.md §5];
   [citation: N1 → Q3, arXiv:2402.07204 §1 p.1] (Tier A — the failure the metric catches);
   [citation: N5 → Q5, OpenReview 34kIv0YVNe §1 p.2] (Tier B, **label as workshop paper** —
   KnowEval comparand).
2. **METRIC 2 — Itinerary feasibility (time-budget adherence + geographic coherence).**
   Strategy: harness runs the full pipeline (CLEO → curate → optimize via VROOM) and re-checks
   each produced itinerary against the opening-hours table and the OSRM/Valhalla travel-time
   matrix; feasibility is binary per itinerary; geographic coherence is mean Average Margin
   per day, directly comparable to ItiNera's published 86.0 (full) vs 242.8 (w/o CSO).
   **Threshold: ≥ 90% of produced itineraries time-feasible. Status: PENDING the evaluation
   harness.**
   [citation: criteria §5 (Feasibility row "⏸ PENDING eval harness") → thesis-criteria.md §5];
   [citation: N1 → Q5, arXiv:2402.07204 Table 2 p.6] (Tier A — Avg-Margin comparand);
   [citation: N4 → Q4 + Q5 + Q6, arXiv:2403.13795 §2.2 / §6.2 / §3] (Tier A — VRPTW formalism
   + 0.40% optimality ref + honest VROOM-vs-SOTA framing);
   [citation: OSRM-PAPER → Q1, DOI 10.1145/2093973.2094062 Abstract] (Tier A — matrix-infra
   academic basis); [citation: S-OSRM → project-osrm.org/docs; S-VALHALLA → valhalla.github.io]
   (Tier C — running matrix/isochrone substrate).
3. **METRIC 3 — Reliability (constraint-violation rate).** Strategy: over the same
   produced-itinerary set, count itineraries with ≥ 1 violated user constraint (budget cap,
   region/POI-type inclusion/exclusion, accessibility, time-window closure). **Threshold: < 5%
   violation rate. Status: PENDING the evaluation harness.** Methodologically analogous to
   AgentTravel's *TripEval* constraint-satisfaction axis.
   [citation: criteria §5 (Reliability row "⏸ PENDING eval harness") → thesis-criteria.md §5];
   [citation: N5 → Q2 + Q5, OpenReview 34kIv0YVNe §1 pp.1–2] (Tier B, **label as workshop
   paper** — TripEval + spatial-reasoning-failure motivation);
   [citation: N1 → Q3, arXiv:2402.07204 §1 p.1] (Tier A — "LLMs lack the optimization
   capabilities required for planning tasks").
4. **METRIC 4 — Provenance coverage (% narratives grounded).** Strategy: run
   `enrich_narratives.py` against the live 310-POI `pois` table on Windows; provenance
   coverage = (# POIs with enrichment AND ≥ 1 source URL) / (# POIs with enrichment).
   **Threshold: ≥ 85% grounded. Status: PENDING the Windows enrichment run.** The
   `narrative_sources.json` snapshot is a pre-enrich probe (3 POIs / 3 grounded / 100% on a
   tiny probe with model `glm-4.7`), NOT the post-enrich coverage headline.
   [citation: criteria §5 (Provenance row "⏸ pending enrich run (Windows)") →
   thesis-criteria.md §5]; [citation: evidence → `thesis/evidence/narrative_sources.json`
  `generated_count`, `grounded_count`, `model` (pre-enrich probe — flag as such)];
   [citation: N1 → Q3, arXiv:2402.07204 §1 p.1] (Tier A — provenance coverage is the audit
   that catches the "hallucinated POIs" failure).
5. **METRIC 6 — UX (end-to-end Playwright pass rate).** Strategy: a Playwright suite exercises
   the full `flutter_app` → VOYO backend → CLEO → VROOM chain on representative journeys
   (1-day Cairo, 3-day Luxor, 7-day Egypt loop, budget constraint, accessibility constraint).
   **Threshold: ≥ 80% pass rate. Status: PENDING the evaluation harness AND the e2e chain
   wiring** (blocked by the same Groq 100k TPD free-tier ceiling documented in
   `01-test-results.json` `whole_tree_collection_errors`).
   [citation: criteria §5 (UX row "⏸ PENDING eval harness") → thesis-criteria.md §5];
   [citation: evidence → `thesis/evidence/01-test-results.json` `whole_tree_collection_errors`
   (`groq.RateLimitError 429 — "Limit 100000, Used 99855"`)] (the blocker);
   [citation: N5 → Q4, OpenReview 34kIv0YVNe §1 p.2] (Tier B, **label as workshop paper** —
   the e2e surface an e2e test exercises).

*How to phrase:* Use a single Measured-vs-PENDING summary table (see figures-spec.md F5.1).
Lead the prose with the *honest framing* — "the metric split itself reinforces the thesis: the
metrics that measure now are precisely the deterministic-substrate metrics; the metrics that
gate on the harness are precisely the end-to-end hybrid-architecture metrics" (restates Ch4
§4.5.1).

**5.2.3 — The keystone limitation: the full-hybrid vs LLM-only ablation is also PENDING
(criteria §5 Ablation keystone).** The thesis argues the LLM alone cannot plan and that
deterministic engines fix it. Currently that claim is **borrowed** — ItiNera's CSO ablation
(Average Margin 86.0 → 242.8, a roughly 3× degradation when the solver is removed). For VOYO
to be *research-grade* (not just engineering-grade), it must produce its **own** ablation
proving the claim in the Egyptian-tourism domain: run the same evaluation-harness scenarios
twice — (a) **full hybrid** (CLEO + VROOM/Valhalla/OSRM) and (b) **LLM-only** (CLEO planning
with the deterministic engines bypassed or replaced by LLM-internal estimates of
routing/time/feasibility) — reporting feasibility %, constraint-violation rate, and
geographic coherence (Avg-Margin) for both configurations. **Threshold: hybrid feasibility
≥ 90% AND LLM-only feasibility collapse (target ≤ 50%), mirroring ItiNera's 86→242.8
magnitude. Status: PENDING the evaluation harness in ablation mode.**
- *How to phrase:* This is the *single most important limitation to disclose* — frame it
  exactly as criteria §5 does: "the difference between engineering-grade and research-grade."
  Do NOT fabricate an ablation number; report the strategy + threshold + the ItiNera
  borrowed-evidence baseline (86 → 242.8) that the VOYO ablation is designed to replicate.
- *Citation:* [citation: criteria §5 (Ablation keystone protocol + threshold) →
  thesis-criteria.md §5]; [citation: N1 → Q5, arXiv:2402.07204 Table 2 p.6 — Avg-Margin
  86.0 (full) vs 242.8 (w/o CSO)] (Tier A — the borrowed-evidence baseline the VOYO ablation
  must replicate, *in the Egyptian domain*).

**5.2.4 — Secondary (substrate) limitations (restates Ch3 + Ch6 honest-gaps).** Beyond the
held eval harness, three secondary limitations are already disclosed in prior chapters and
restated here for completeness:

- (a) **Substrate regional imbalance.** Cairo (11 POIs) and Giza (9 POIs) — the two
  most-visited regions — are the thinnest in the corpus. This is a master-list curation gap,
  not a technical defect; disclosed honestly in `05-db-completeness.json` `honest_gaps_summary`.
  [citation: evidence → `thesis/evidence/05-db-completeness.json` `regional_distribution` +
  `honest_gaps_summary`]; ⚠️ these counts are from the stale 255-POI snapshot and must be
  re-run on the canonical 310-POI corpus by `validate_database.py` before Ch6 closes — the
  *shape* of the imbalance (Cairo/Giza thinnest) is the disclosed limitation, the exact counts
  are PENDING the refresh.
- (b) **Operational free-tier ceilings.** Groq 12,000 TPM / 100,000 TPD; Redis down (DNS
  unreachable); VROOM optimize pending/intermittent (per `thesis/evidence/_GROUNDING_MAP.md`
  §3). These block the live integration/e2e/tool test suite (the 8 collection errors in
  `01-test-results.json`) and therefore block METRIC 6 (UX e2e) and the ablation keystone.
  [citation: evidence → `thesis/evidence/01-test-results.json` `whole_tree_collection_errors`];
  [citation: evidence → `thesis/evidence/_GROUNDING_MAP.md` §3 + §5 "Honesty rules"].
- (c) **Coverage gaps that are semantically correct nulls.** ticket_price filled on
  ~58% (107 of 255 POIs are genuinely free — null is correct); opening_hours ~67% (natural /
  outdoor sites have no hours — null is correct); website_url ~40% (natural sites have no
  website — null is correct); image coverage 82% / 208 of 255 (45 image-less POIs are obscure
  remote sites, not the famous six). *(Percentages from the stale 255 snapshot — see Ch6 for
  the post-refresh 310-corpus equivalents.)*
  [citation: evidence → `thesis/evidence/05-db-completeness.json` `field_completeness` +
  `honest_gaps_summary`]; [citation: evidence → `thesis/evidence/_GROUNDING_MAP.md` §5].

*How to phrase:* Group as "non-eval-harness limitations" — three bullets; each disclosed in
its origin chapter and restated. Use 310 (not 255) as the POI count; flag the snapshot counts
as the pre-refresh figures.

---

# §5.3 — Future work

> **Subsection thesis sentence:** *Future work is dominated by closing the held-eval-harness
> gap — running the keystone ablation and the five PENDING metric families — with thresholds
> committed in advance; substrate extension is secondary.*

**5.3.1 — Run the keystone ablation (the single highest-priority future-work item).** Execute
the criteria §5 ablation protocol: full-hybrid vs LLM-only over the same evaluation-harness
scenarios, reporting feasibility %, constraint-violation rate, and Avg-Margin for both. Target:
hybrid feasibility ≥ 90% with LLM-only collapse ≤ 50%, mirroring ItiNera's 86 → 242.8. This
produces Figure 4.12 (the keystone chart) and converts the thesis from "borrowed evidence for
the LLM-alone-cannot-plan claim" to "VOYO's own published-domain ablation."
- *How to phrase:* The opening and most-emphasized future-work item — frame as the difference
  between engineering-grade and research-grade (criteria §5).
- *Citation:* [citation: criteria §5 (Ablation protocol) → thesis-criteria.md §5];
  [citation: N1 → Q3 + Q5, arXiv:2402.07204 §1 p.1 + Table 2 p.6] (Tier A — the claim the
  ablation proves + the borrowed-evidence baseline).

**5.3.2 — Run the full evaluation harness (the five PENDING metric families).** Execute
METRICS 1, 2, 3, 6 against the planned evaluation harness and METRIC 4 against the Windows
enrichment run. Each metric's threshold is already committed (criteria §5): P@5 ≥ 0.7;
feasibility ≥ 90%; violation rate < 5%; provenance coverage ≥ 85%; UX e2e ≥ 80%. Methodological
comparands (AgentTravel KnowEval/TripEval) and baseline comparands (ItiNera Avg-Margin 86.0;
PyVRP 0.40% VRPTW gap) are committed in advance in Ch4 §4.5.3, so VOYO's measured numbers will
be directly comparable to published peer-reviewed results.
- *How to phrase:* Group as "close the measured-vs-PENDING gap"; emphasize that thresholds are
  pre-committed (no post-hoc tuning) and comparands are pre-committed (direct comparison to
  published results).
- *Citation:* [citation: criteria §5 (all six metric thresholds) → thesis-criteria.md §5];
  [citation: N1 → Q5, arXiv:2402.07204 Table 2] (Tier A — comparand 1);
  [citation: N4 → Q5, arXiv:2403.13795 §6.2] (Tier A — comparand 2);
  [citation: N5 → Q5, OpenReview 34kIv0YVNe §1 p.2] (Tier B, **label as workshop paper** —
  methodological comparand).

**5.3.3 — Extend the substrate.** Reduce the regional imbalance (grow Cairo/Giza coverage
beyond the current thin counts — *exact current counts pending the 310-corpus refresh*), and
extend dual-pricing enrichment beyond the current **58 POIs** (criteria §4) and authoritative
gov.eg descriptions beyond **76 POIs**; the goal is to push provenance coverage well past the
85% threshold once METRIC 4 is measured.
- *How to phrase:* Substrate extension as a concrete, measurable future task with explicit
  target counts.
- *Citation:* [citation: criteria §4 (dual gov.eg prices = 58; gov.eg descriptions = 76) →
  thesis-criteria.md §4]; [citation: criteria §5 (Provenance threshold ≥ 85%) →
  thesis-criteria.md §5].

**5.3.4 — Lift the operational free-tier ceilings.** Migrate from Groq free-tier (100k TPD) to
a paid LLM provider; restore Redis (currently DNS-unreachable); stabilize the VROOM optimize
service (currently intermittent). These unblock METRIC 6 (UX e2e), the live
integration/e2e/tool suite (the 8 collection errors), and the ablation keystone.
- *How to phrase:* Operational enabler for 5.3.1 and 5.3.2 — not a research contribution, but
  a prerequisite.
- *Citation:* [citation: evidence → `thesis/evidence/01-test-results.json`
  `whole_tree_collection_errors` (Groq 100k TPD ceiling)];
  [citation: evidence → `thesis/evidence/_GROUNDING_MAP.md` §3 (Redis down / VROOM
  intermittent)].

**5.3.5 — Broader research direction (the hybrid-deterministic paradigm beyond Egypt).**
Generalize the LLM-intent ↔ deterministic-engine separation beyond Egyptian tourism: the same
VRPTW-class optimizer + OSRM/Valhalla-class matrix + force-tool grounding pattern should
transfer to any constrained itinerary-planning domain (urban museums, multi-city Europe,
event scheduling). The contribution is the *pattern*, not the Egyptian instantiation; the
closest precedent (ItiNera) demonstrates the same pattern transfers across geographies.
- *How to phrase:* The closing future-work paragraph — frame the contribution as a
  transferable pattern; cite ItiNera as the cross-geography precedent.
- *Citation:* [citation: N1 → Q1, arXiv:2402.07204 Abstract (ItiNera's OUIP framing is
  geography-agnostic)] (Tier A); [citation: criteria §1 (the hybrid-deterministic thesis
  sentence) → thesis-criteria.md §1].

---

# Writer's anti-fabrication checklist (criteria §7 + §4 stale-number sweep — inherited)

1. **POI count = 310 everywhere** (criteria §4); the prior draft's **255** is stale and must
   not reappear in prose. `05-db-completeness.json` still reports 255 — flag this in prose
   when the snapshot counts are cited, and use 310 as the canonical count.
2. **Dual gov.eg prices = 58; gov.eg descriptions = 76; any-enrichment = 97** (criteria §4).
   Do not invent other enrichment counts.
3. **Never cite the Reflexion "+22% ALFWorld"** stat — fabricated; absent from the paper
   (criteria §7). Reflexion is NOT used in this dossier anyway, but the rule stands.
4. **Never cite Liu's "+35% feature discovery"** — not in the paper (criteria §7). Liu is NOT
   used in this dossier, but the rule stands.
5. **Never cite Pai's "0.69" as a structural β** — it is a discriminant-validity correlation,
   not a structural coefficient (criteria §7). Pai is NOT used in this dossier.
6. **No paper exists for VROOM** — cite S-VROOM as software + Issue #735 verbatim; pair with
   N4 Q6 for the academic characterization (criteria §7).
7. **OSRM is BOTH a Tier-A paper (OSRM-PAPER) AND Tier-C software (S-OSRM)** — never conflate
   them; both are needed where the algorithm AND the running tool are referenced.
8. **N5 AgentTravel is a NORA / CEUR workshop paper** — label as such every time it appears
   (criteria §2); use ONLY as the eval-design comparand, never as architecture precedent.
9. **PENDING metrics report NO NUMBER** — only strategy + threshold + blocker. The ItiNera
   86→242.8 figure is the borrowed-evidence BASELINE (a published peer-reviewed number), not
   a VOYO measurement; cite it as such.
10. **Ch5 makes NO NEW CLAIMS** (criteria §4 Ch5 row). Every claim must trace to an already-
    cited claim in Ch1–Ch4. The dossier's "Restates …" parenthetical on each claim is the
    audit trail; the supervisor checks each one back to its origin chapter.
