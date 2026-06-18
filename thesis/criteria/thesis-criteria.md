# VOYO Thesis — Criteria & Rubric (`thesis-criteria.md`)

> **The linchpin.** Every section dossier produced by `voyo-section-writer` is audited by
> `voyo-thesis-supervisor` against THIS file. If a dossier's claims, citations, or evidence
> don't resolve here, it fails the gate. Authored 2026-06-16 by the orchestrator; the
> `voyo-thesis-criteria` agent maintains/extends it. **Source of truth for the argument and
> for what counts as admissible evidence.**
>
> Companion files: `thesis/citations/INDEX.md` (verified citation evidence base, 23 entries),
> `thesis/references.bib` (BibTeX — to be regenerated to add the PRIMARY-ACADEMIC tier),
> `thesis/evidence/` (raw benchmark/measurement ground truth).

---

## 1. The thesis argument (the spine every section must serve)

**VOYO is a hybrid deterministic AI travel planner.** The contribution is *not* "an LLM that
plans trips." It is the **separation of concerns** between probabilistic and deterministic
computation:

- **The LLM (CLEO conversational layer) handles intent and personalization only** — parsing
  natural-language requests, maintaining preference/memory state, and composing a
  human-readable response. The LLM is explicitly **not** trusted with feasibility, geography,
  or numerical optimization.
- **Deterministic optimization engines handle everything that must be correct**: Valhalla for
  isochrones and routing; VROOM for VRP/VRPTW feasibility and time-window-constrained
  optimization; OSRM for distance/travel-time matrices. Reachability, routing, isochrones,
  matrices, feasibility, and time-window optimization are **delegated to these engines**, not
  approximated by the LLM.

This is the framing the advisor asked for. Every chapter must reinforce it; nothing may
contradict it. The single sentence to keep returning to:

> *VOYO couples an LLM (for intent + personalization) to deterministic optimization engines
> (for reachability, routing, isochrones, matrices, feasibility, and time-window
> optimization), because an LLM alone cannot reliably plan — it lacks optimization capability
> and hallucinates geography and constraints.*

---

## 2. Citation tiering policy (admissibility rules)

Tier governs **how heavily** a source may be leaned on and **where** it may appear. The
supervisor rejects any dossier that uses a source outside its tier.

### Tier A — PRIMARY-ACADEMIC (load-bearing; may ground core contribution claims)

| id | Work | Venue (must be cited this way) | What it grounds |
|---|---|---|---|
| **N1** | **ItiNera** (Tang et al.) | **EMNLP 2024 Industry Track + KDD UrbComp 2024 Best Paper** (arXiv:2402.07204) | **Closest direct precedent.** LLMs "lack the optimization capabilities required for planning tasks" → ItiNera bolts cluster-aware spatial optimization (hierarchical TSP) onto an LLM pipeline. VOYO's curate→optimize stage is the same insight, instantiated for Egyptian tourism. Ablation: removing CSO worsens Avg Margin 86.0→242.8. |
| **N4** | **PyVRP** (Wouda, Lan, Kool) | **INFORMS Journal on Computing** (arXiv:2403.13795) | Grounds VRP/VRPTW as a well-benchmarked OR family solved near-optimally (0.22% / 0.40% gaps) by hybrid genetic search. Justifies delegating time-window feasibility to a VROOM-class solver. Gives the verbatim academic characterization of VROOM. |
| **OSRM-PAPER** | Luxen & Vetter, *Real-time routing with OpenStreetMap data* | **ACM SIGSPATIAL GIS 2011** (DOI 10.1145/2093973.2094062; DBLP conf/gis/LuxenV11) | The academic routing reference. Grounds contraction-hierarchy real-time routing on OSM data — the algorithmic basis for VOYO's OSRM distance matrices. *(✅ FULL-TEXT VERIFIED 2026-06-17: abstract via Wayback snapshot of the ACM page + full 4-page body via the provided PDF; Q1 abstract + Q5/Q6/Q7 body quotes all quotable — see `citations/new-route-opt/osrm/quotes.md`.)* |

### Tier B — SUPPORTING (may reinforce, may NOT carry a core claim alone)

| id | Work | Venue | Role |
|---|---|---|---|
| **N5** | **AgentTravel** (Zhao, Feng, Li) | **NORA / CEUR workshop** (OpenReview 34kIv0YVNe) | **Supporting only** — knowledge-grounded travel-agent evaluation design (TravelLLM + agentic planner + TravelBench). Use for eval-methodology comparand, not as architecture precedent. Label as "workshop paper." |
| **01–07** | Compound AI Systems; Wang survey; AutoGen; TravelPlanner; Reflexion; Gorilla; Toolformer | NeurIPS / ICML / BAIR / Springer | Compound-AI & tool-use foundation (Tier A within the agentic-architecture theme, but supporting the route-opt crux). |
| **08–15** | Pai; Liu; Christina; Pang; Onuiri; AlSaeed; Tsaih; Swanepoel | CACM / MDPI / journals / M.Eng thesis | Smart-tourism + architecture + engagement baselines. |

### Tier C — SOFTWARE-INFRASTRUCTURE (cite as software; NEVER as an academic paper)

| id | Tool | Citation form | Role |
|---|---|---|---|
| **S-VROOM** | VROOM | GitHub `VROOM-Project/vroom` + docs | VRPTW solver VOYO delegates to. **No paper exists** (verbatim from Issue #735) — never invent one. Cite honestly as "good solutions to real-life VRPs but unable to compete with state-of-the-art" (PyVRP §3). |
| **S-VALHALLA** | Valhalla | `valhalla.github.io` docs | Isochrones + routing engine. Software only. |
| **S-OSRM** | OSRM | `project-osrm.org/docs` | Distance-matrix service. Software infra; pair with **OSRM-PAPER** (Tier A) where the *algorithm* is cited. |

### Tier D — DEPRIORITIZED / PREPRINT-ONLY (omit unless clearly labelled; never core evidence)

| id | Work | Rule |
|---|---|---|
| **N2** | **TRIP-PAL** (de la Rosa et al.) | arXiv:2406.10196 **preprint only**. Do **not** rely on as core thesis evidence. If cited at all, label explicitly as "arXiv preprint, not peer-reviewed" and use only as a minor supporting footnote (e.g. "LLM-alone planning unreliability, per a non-peer-reviewed preprint"). Prefer ItiNera for the same point. |
| **N3** | **TravelAgent** (Chen et al.) | arXiv:2409.08069 **preprint only**. Same rule as N2. Omit from core architecture argument. |

**Hard rule:** a core contribution claim in any dossier must trace to ≥1 **Tier A** source
(N1 / N4 / OSRM-PAPER). Tier D sources may appear only as labelled-preprint footnotes.

---

## 3. Literature-review structure (§2.2) — 4 themes + the route-opt crux

The advisor asked for a restructured §2.2. Each dossier for §2.2 covers ONE theme. Every
theme ends with an explicit "VOYO positioning" sentence.

| Theme | Coverage | Primary citations | VOYO positioning |
|---|---|---|---|
| **T1 — LLM agents & tool-use** | compound systems, agent modules, self-correction, tool/API use | 01, 02, 03, 05, 06, 07 | VOYO is a compound system; CLEO = the conversational/agent layer coupled to verified tools. |
| **T2 — Recommendation & itinerary planning** | the closest prior art: LLM + spatial optimization | **N1 (ItiNera)** primary; N2 footnote-only; 04 (TravelPlanner) | **The crux theme.** VOYO's curate→optimize = ItiNera's insight, for Egypt, with VRPTW-grade feasibility. |
| **T3 — Grounding / RAG / hallucination** | why the LLM must not own geography/prices/constraints | N1 (Q3), 04, 05, 06 | VOYO grounds every POI/price/route in deterministic sources; the LLM never invents geography. |
| **T4 — Tourism domain systems** | smart-tourism tech, engagement, ITMS architectures | 08–15 | VOYO extends this lineage with a *deterministic* core + verified 310-POI substrate. |

**§2.3 — the route-optimization crux subsection** (the contribution's technical anchor):
- VRP/VRPTW framing → **N4 PyVRP** (Tier A) + **S-VROOM** (software).
- Routing/matrix infrastructure → **OSRM-PAPER** (Tier A) + **S-OSRM** + **S-VALHALLA**.
- The hybrid argument → **N1 ItiNera** (Tier A) as closest precedent.
- Eval-design comparand → **N5 AgentTravel** (Tier B, labelled workshop).
- **Research gap statement** (verbatim-derivable): no prior system combines an LLM intent
  layer with VRPTW-grade deterministic optimization over a verified, region-balanced
  Egyptian POI substrate with dual (Egyptian/foreigner) pricing. State it; cite the gap
  between ItiNera (urban China, no VRPTW solver, no dual pricing) and VOYO.

---

## 4. Per-chapter dossier rubric (what each dossier must contain to PASS)

Every dossier = `thesis/chN-<slug>/dossier.md` (+ `evidence-packet.md`, `figures-spec.md`,
`citations-used.md`). **A claim with no citation id resolving in `thesis/citations/` is an
automatic FAIL.**

| Ch | Dossier must deliver | Required citations | Pass threshold | Excellence |
|---|---|---|---|---|
| **Ch1 Intro** | Problem statement; the hybrid-deterministic thesis sentence (§1 verbatim); contributions list; the "LLM-alone cannot plan" motivation. | 01; **N1** for motivation | Thesis sentence present + tied to N1 | Quantified motivation (e.g. ItiNera's "LLMs lack optimization" quote) |
| **Ch2 Background** | 4 themed lit-review dossiers (T1–T4) + §2.3 route-opt crux + research-gap statement + regenerated Tables 2.1–2.3 (now incl. N1/N4/OSRM). | T1:01–07; T2:**N1**; T3:N1,04; T4:08–15; §2.3:**N4,OSRM-PAPER,S-VROOM,S-VALHALLA,S-OSRM,N5** | 4 themes + gap statement; ≥1 Tier-A in T2 & §2.3 | Research-gap paragraph with explicit VOYO-vs-ItiNera delta |
| **Ch3 Methodology** | Architecture (LLM intent ↔ deterministic engines); CLEO layer; the delegate-to-solver contract; VROOM/Valhalla/OSRM wiring; **the ablation protocol** (full-hybrid vs LLM-only configuration). | **N1,N4,OSRM-PAPER**; S-*; 02,03 | Hybrid separation explicit; every engine's job named + cited; **ablation config spec'd (engines-bypassed mode defined)** | A figure + a "trust boundary" table (LLM does X / engines do Y) |
| **Ch4 Results / Eval** | Eval STRATEGY dossier: metric definitions + how measured + thresholds. **Metrics:** retrieval (P@k/R/nDCG), itinerary feasibility (time-budget adherence, geographic coherence), reliability (constraint-violation rate), provenance coverage, latency, UX (e2e pass rate). | **N5** (eval design); N1,N4 (baselines) | All 6 metric families defined w/ thresholds | Honest "measured vs pending" table (eval harness held → mark PENDING clearly) |
| **Ch5 Conclusion** | Restate hybrid-deterministic contribution; limitations; future work. | (no new claims) | No new uncited claims | Limitations tied to held eval harness |
| **Ch6 Data pipeline** | The 310-POI rebuild; dual-price enrichment; provenance. | provenance files (`thesis/evidence/`, `data/ticket_prices_upsert.sql`, `thesis/citations/software/*`) | POI count = **310** (not 255); dual-price count = 58 | Provenance table: every enrichment source → POI count |

**Stale-number sweep (supervisor enforces):** every dossier must use **310** for the POI count
(was 255 in the archived prior draft). Any "255" in new output = FAIL. Dual gov.eg prices =
**58 POIs**; authoritative gov.eg descriptions = **76 POIs**; POIs with any enrichment = **97**.

---

## 5. Required quantitative evidence (figures/tables + thresholds)

Figures are **derived from `thesis/evidence/`** (raw ground truth), never hand-drawn. The two
stale 255-POI figures (`fig_field_completeness`, `fig_regional_distribution`) were deleted and
must be **regenerated from current data** by `thesis/figures/gen_all_figures.py` before Ch6
closes. `fig_3_1_architecture`, `fig_test_pyramid`, `fig_scoring_latency`, `fig_ab_divergence`
are retained (not count-dependent).

| Artifact | Metric | Source | Threshold to PASS | Status |
|---|---|---|---|---|
| Latency | scoring p50/p95 | `evidence/02-latency.json` | p95 < 500 ms | ✅ measurable now |
| AB correctness | rec-engine divergence | `evidence/03-ab-correctness.json` | 0 logic divergences | ✅ measurable now |
| Test inventory | pyramid counts | `evidence/01-test-results.json` | ≥99 pass, 0 fail | ✅ measurable now |
| DB completeness | field fill rates | `evidence/05-db-completeness.json` | refresh → 310 POIs | ⚠️ regenerate (was 255) |
| **Retrieval** | P@k / R / nDCG | eval harness | P@5 ≥ 0.7 | ⏸ PENDING eval harness |
| **Feasibility** | time-budget adherence; geo coherence | eval harness | ≥90% feasible itineraries | ⏸ PENDING eval harness |
| **Reliability** | constraint-violation rate | eval harness | <5% violations | ⏸ PENDING eval harness |
| **Provenance** | % narratives grounded | `evidence/narrative_sources.json` post-enrich | ≥85% grounded | ⏸ pending enrich run (Windows) |
| **UX** | e2e Playwright pass rate | eval harness | ≥80% | ⏸ PENDING eval harness |
| **Ablation (KEYSTONE)** | full-hybrid vs **LLM-only** (engines bypassed) — same scenarios, feasibility + violation-rate + geographic-coherence deltas | eval harness (ablation mode) | **hybrid ≫ LLM-only**: hybrid feasibility ≥90% AND LLM-only feasibility must be shown to collapse (target ≤50%, mirroring ItiNera's ablation magnitude) | ⏸ PENDING eval harness — **BLOCKING: the single most defensible chart** |

### Ablation protocol (keystone experiment — added 2026-06-17, orchestrator-authorized)
**Rationale:** the thesis argues the LLM alone cannot plan and that deterministic engines fix it.
Currently that claim is borrowed (ItiNera's CSO ablation, **N1 Q5**: Avg-Margin 86.0 → 242.8). For
VOYO to be *research-grade*, it must produce its OWN ablation proving the claim in the Egyptian-
tourism domain. **Methodology:** run the eval-harness scenarios twice — (a) full hybrid
(CLEO + VROOM/Valhalla/OSRM), (b) **LLM-only** (CLEO planning with the deterministic engines
bypassed or replaced by LLM-internal estimates of routing/time/feasibility). Report feasibility %,
constraint-violation rate, and geographic coherence (Avg-Margin) for BOTH configs. **Figure
4.12 — Ablation comparison** (grouped bars: hybrid vs LLM-only × {feasibility, violations,
Avg-Margin}), the keystone chart. Threshold: hybrid feasibility ≥90% while LLM-only feasibility
collapses (≤50% target) — a magnitude comparable to ItiNera's 86→242.8 degradation. This is
the difference between engineering-grade and research-grade; do NOT let the eval harness run
without it.

**Honesty rule (Ch4):** metrics marked ⏸ PENDING must be reported as "strategy defined;
measurement pending the eval harness / pending the Windows enrichment run." **Never** invent a
number for a pending metric. The dossier's value is the *strategy + thresholds*, not fake data.

---

## 6. Dossier output spec (what `voyo-section-writer` produces)

A dossier is **an evidence packet for a human writer, NOT final thesis prose.** Per section:

```
thesis/chN-<slug>/
  dossier.md          — cited argument OUTLINE (claim → citation id → locator), section-by-section
  evidence-packet.md  — the verbatim quotes/numbers/tables pulled from citations/ + evidence/
  figures-spec.md     — which figures/tables this section needs + their data source file
  citations-used.md   — the subset of citation ids used (must all resolve in citations/INDEX.md)
```

**Hard rules (inherited from the librarian, enforced by the supervisor):**
1. No claim without a citation id that resolves in `thesis/citations/INDEX.md`.
2. Tier discipline (§2): core claims need Tier A; Tier D only as labelled-preprint footnotes.
3. Numbers must come from `thesis/evidence/` or a cited quote bank — never inferred.
4. POI count = 310; never 255.
5. Output lives ONLY under `thesis/chN-<slug>/`. Do not edit `src/`, `flutter_app/`,
   `enrich_narratives.py`, the DB, or human thesis prose (the archived chapters are read-only
   reference).

---

## 7. No-fabrication contract (shared by all thesis agents)

- Every quote is verbatim with a locator (URL + section/table/page).
- Unreachable content is marked `STATUS: UNVERIFIED` and **nothing is written about it.**
- Software (VROOM/Valhalla/OSRM-the-tool) is cited as software; only OSRM-the-paper (Tier A) is
  an academic citation. No paper is invented for VROOM/Valhalla.
- ar5iv/PDF extraction artifacts (tripled numbers, line-wrap hyphenation) are de-duplicated to
  the rendered single-number form and flagged; spot-check numeric quotes before final submit.
- The Reflexion "+22% ALFWorld" stat found in the archived prior draft is **fabricated** (the
  librarian proved it absent from the paper). It must NOT reappear. Verbatim Reflexion result =
  "completing 130 out of 134 tasks" + "91% HumanEval pass@1".
