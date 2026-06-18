# §2.2 / §2.3 — Figures & Tables Spec

> Per criteria §6: figures are *derived from `thesis/evidence/`* (raw ground truth), never
> hand-drawn; tables that summarize the literature corpus are derived from the verified
> quotes.md files (NOT regenerated). Anything depending on the eval harness or the Windows
> enrichment run is **PENDING** and labelled as such.

## Tables this section owns

### Table 2.1 — AI Architecture & Agentic Coding (refs 01–07) — REGENERATE FROM QUOTES

**Purpose:** T1 synthesis table mapping the agentic-architecture corpus to VOYO's CLEO design.
**Data source:** the verified `quotes.md` for refs 01–07 (`thesis/citations/01..07/quotes.md`)
plus this dossier's evidence-packet.md. **NOT** derived from a benchmark run — it is a
literature-synthesis table populated from verbatim quotes.

| Ref | Primary focus | Grounding / tool-use | Verified quantitative result | Role in VOYO |
|---|---|---|---|---|
| 01 Compound AI Systems | Multiple interacting components, not one model | Retrievers + DBs solve hallucination | (conceptual; no benchmark) | Defends the compound-system skeleton |
| 02 Agent Survey | Profile / Memory / Planning / Action blueprint | Links "brain" to tool suite | (conceptual) | Maps CLEO modules + the deterministic engines |
| 03 AutoGen | Multi-agent conversation; role separation | Reasoning vs execution roles | (conceptual) | Justifies CLEO↔engine separation |
| 04 TravelPlanner | Multi-constraint travel planning | Ground-truth + tools for feasibility | **GPT-4 0.6% success** (Abstract) | Independent evidence that LLMs alone fail planning |
| 05 Reflexion | Self-correction via verbal RL | Detects hallucinations via reflection | **91% pass@1 HumanEval**; **130/134 ALFWorld** ⚠️ not "+22%" | Motivates CLEO self-check + memory |
| 06 Gorilla | Accurate API invocation | Retriever-aware tool selection | **Gorilla 59.13% vs GPT-4 38.70% accuracy; 6.98% vs 36.55% hallucination** (TorchHub 0-shot) | Motivates CLEO↔verified-tool coupling |
| 07 Toolformer | Self-supervised tool use | Loss-filtered API calls | SQuAD 17.8→33.8; ASDiv 7.5→40.4; Dateset 3.9→27.3 | Foundation for CLEO's tool-execution environment |

⚠️ **Anti-fabrication flags enforced in this table:**
- Reflexion row uses **91% HumanEval** + **130/134 ALFWorld**, never "+22% ALFWorld"
  (fabricated).
- No numeric claims beyond what is in `quotes.md`.

### Table 2.2 — Smart Tourism Tech & Engagement (refs 08–11) — REGENERATE FROM QUOTES

**Purpose:** T4a synthesis table; also feeds the Ch4 user-experience discussion.
**Data source:** verified `quotes.md` for 08–11. **NOT** a benchmark run.

| Ref | Theory / lens | Method + N | Verified quantitative result | Role in VOYO |
|---|---|---|---|---|
| 08 Pai STT | 2nd-order STT construct | PLS-SEM, **N=527** (Macau) | **Accessibility path coefficient 0.285** (T=35.093); STT→satisfaction→(happiness, revisit) | Mobile-first accessibility + verified data |
| 09 Liu Adaptive UI/UX | Context-aware adaptation | SOM + adaptation engine | **+22% task completion** over next-best adaptive solution ⚠️ NOT "+35% feature discovery" | Adaptive front-end; decoupled presentation |
| 10 Christina Tokopedia | UTAUT | PLS-SEM (SmartPLS 4.0), **N=204** | Satisfaction **fully mediates** AI(chatbot+rec)→engagement | CLEO (trust) ↔ engines (utility) separation |
| 11 Pang Chatbot Stickiness | U&G + TAM + ECM | SEM, **N=735** | 4 motivational categories (utilitarian, hedonic, technology, social); privacy negative ⚠️ **β=0.326 NOT verified — omit** | Grounded-data + privacy-aware design |

⚠️ **Anti-fabrication flags enforced in this table:**
- Pai row: **0.285** (accessibility path coefficient) only — NEVER "0.69" as a structural β
  (it is discriminant validity).
- Liu row: **+22% task completion** only — NEVER "+35% feature discovery" (not in paper).
- Pang row: **N=735** + qualitative finding only — NEVER "β=0.326" (not in abstract).

### Table 2.3 — Intelligent Systems & Architecture (refs 12–15) — REGENERATE FROM QUOTES

**Purpose:** T4b synthesis table; architecture-lineage anchor.
**Data source:** verified `quotes.md` for 12–15. **NOT** a benchmark run.

| Ref | Primary focus | Method / architecture | Verified quantitative result | Role in VOYO |
|---|---|---|---|---|
| 12 Onuiri ITMS | Information access for Nigerian tourism | RUP + MySQL/HTML/PHP; **50 tourist locations** | Hybrid recommendation; reduced search effort | Early centralized-DB lineage |
| 13 AlSaeed LOCUS | Personalized mobile tourism | Client–server; item-item + user-user CF | **SUS = 87.75** (threshold 68); **5.4 s** task time; **N=10** UAT | Mobile + recommendation baseline |
| 14 Tsaih AI Tech-Stack | Modularization / vendor lock-in | **7-layer** loosely coupled stack | Conceptual; smart-tourism STRS case study (4 firms) | Architectural justification for layered separation |
| 15 Swanepoel | Decoupled reference architecture | Layered service-oriented; M.Eng thesis (NOT Ph.D.) | (architectural; demonstrator) | Architecture lineage at national-tourism scale |

⚠️ **Bibliographic corrections to apply when emitting LaTeX:**
- 14 Tsaih DOI = **10.1145/3568026** (NOT 10.1145/3579366, which is an unrelated IoT paper).
- 15 Swanepoel degree = **Master of Engineering (Industrial Engineering)** (NOT Ph.D.); handle
  = **10019.1/125975**; date = **December 2022**.

### Table 2.4 — The Route-Optimization Crux (§2.3) — NEW TABLE, populated from N4/OSRM/S-*

**Purpose:** the contribution's technical anchor table; the §2.3 keystone.
**Data source:** verified `quotes.md` for N4 PyVRP, OSRM-PAPER, S-VROOM, S-VALHALLA, S-OSRM.

| Layer | Component | Tier | Verified characterization | Role in VOYO |
|---|---|---|---|---|
| Problem framing | VRPTW (time-windowed) | A — N4 Q4 | "earliest arrival time [...] and latest arrival time [...] in between which service should start" | Why VOYO frames itinerary optimization as a VRPTW |
| Solver family | HGS (hybrid genetic search) | A — N4 Q1–Q3,Q5 | 1st at DIMACS 2021 VRPTW; mean gap **0.22% CVRP / 0.40% VRPTW**; 80–90% of runtime in C++ local search | Defends metaheuristic solver choice |
| Chosen solver | VROOM | C — S-VROOM (software; **NO PAPER**) | "open-source route optimization engine [...] in milliseconds"; "no paper exists" (Issue #735) | VOYO's VRPTW backend; fast, practical, not SOTA |
| Academic VROOM characterization | (cross-cite from N4) | A — N4 Q6 | "good solutions to real-life VRPs [...] unable to compete with state-of-the-art" | Honest framing of the trade-off |
| Routing algorithm | Contraction Hierarchies | A — OSRM-PAPER Q5 | Preprocessing in "minutes"; queries "in the order of about a hundred microseconds" | Real-time routing on continental OSM data |
| Routing "not a bottleneck" | (performance claim) | A — OSRM-PAPER Q6 | "routing is not a bottleneck anymore, and other components become obstacles" | Defends self-hosted routing for VOYO |
| Distance-matrix tool | OSRM `/table` | C — S-OSRM | "duration of the fastest route between all pairs [...] in seconds and [...] meters" (fastest-route, not straight-line) | Matrix that feeds VROOM |
| Reachability tool | Valhalla isochrones | C — S-VALHALLA | "areas that are reachable within specified time intervals from a location" | VOYO's "what's reachable in N min" feature |
| Closest precedent | ItiNera CSO | A — N1 Q4 | Hierarchical TSP ordering; **ablation: Avg Margin 86.0 → 242.8 w/o CSO** | VOYO's contribution = same insight, VRPTW-grade, Egypt |
| Eval-design comparand | AgentTravel TravelBench | B — N5 Q5 (workshop) | KnowEval + TripEval (feasibility, personalization, constraint satisfaction) | Template for VOYO's eval chapter |

⚠️ **Tier-discipline flags enforced in this table:**
- S-VROOM / S-VALHALLA / S-OSRM are cited **as software** (Tier C), never as papers.
- N4 Q6 is the **only** academically-sourced sentence about VROOM — pair it with S-VROOM.
- OSRM appears as BOTH **OSRM-PAPER (Tier A)** for the algorithm AND **S-OSRM (Tier C)** for the
  running tool — never conflate.
- N5 AgentTravel is **Tier B**, labelled "NORA / CEUR workshop" — used only as eval comparand.

## Figures this section needs

### Figure 2.1 — Research-Gap map (VOYO vs prior art) — NEW CONCEPTUAL FIGURE
- **Type:** a 2D scatter or quadrant showing prior systems on two axes: (x) optimizer class
  — none / heuristic / TSP / **VRPTW (VOYO only)**; (y) substrate — generic / urban-China /
  **Egyptian 310-POI (VOYO only)**.
- **Data source:** the Research-Gap statement in `dossier.md` (§ GAP-1..GAP-5); placement of
  each prior system is sourced from its quotes.md (e.g., ItiNera = TSP + urban-China [N1 Q4,Q7];
  TravelPlanner = no optimizer, generic benchmark [04 Q1]; TRIP-PAL = PDDL planner [N2 Q5,
  Tier-D footnote]; AgentTravel = no optimizer [N5 Q1, Tier-B]; Onuiri/LOCUS = recommendation
  only [12,13]).
- **Status:** ✅ synthesizable from quotes.md now (no eval harness needed). The figure is
  conceptual, not a benchmark plot.

### Figure 2.2 — The hybrid-deterministic argument diagram — DEFERRED TO Ch3
- This is a methodology figure (CLEO↔engine trust boundary); it belongs in Ch3 (`fig_3_1_architecture`)
  per criteria §5. **Do NOT duplicate in Ch2.** Ch2 references it forward.

## Pending items (NOT introduced as results in Ch2)

- **DB completeness figure (310 POIs):** `thesis/evidence/05-db-completeness.json` currently
  reports the stale **255**; per criteria §5, it must be regenerated before Ch6 closes. **In
  Ch2, cite the criteria-mandated 310 for substrate size** and do not introduce any
  regional-distribution figure until the regenerate runs (criteria §5 — `fig_regional_distribution`
  was deleted as stale).
- **All §4 metrics** (retrieval P@k/R/nDCG, feasibility, reliability, provenance, UX): PENDING
  eval harness. **None of these appear in Ch2 as results**; Ch2 only defines the strategy.
- **Provenance coverage** (≥85% grounded narratives): pending the Windows enrichment run. The
  dual-price count (58) and gov.eg-description count (76) and any-enrichment count (97) are
  criteria-mandated numbers (criteria §4) and are safe to cite in Ch2's research-gap statement.

## Commands the writer may run to regenerate the corpus tables

None required — Tables 2.1–2.4 are populated from verified `quotes.md` files (literature
synthesis, not benchmark runs). The writer should copy verbatim quotes from
`evidence-packet.md` and not invent numbers.
