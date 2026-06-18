# Ch1 — Introduction — CITED ARGUMENT OUTLINE

> **CHAPTER THESIS SENTENCE (the spine every claim in Ch1 serves — use verbatim in the
> introduction):**
>
> *VOYO couples an LLM (CLEO — for intent parsing and personalization only) to deterministic
> optimization engines (Valhalla, VROOM, OSRM — for reachability, routing, isochrones,
> distance matrices, and VRPTW-grade feasibility / time-window optimization), because an LLM
> alone cannot reliably plan: it lacks optimization capability and hallucinates geography,
> prices, and constraints.*
>
> [citation: criteria §1 → `thesis/criteria/thesis-criteria.md` §1 (the verbatim spine
> sentence, authoritatively defined)]. [citation: N1 → Q3 — Tier A: pure LLMs "cannot refer
> to specific POI lists, resulting in outdated or hallucinated POIs" and "lack the
> optimization capabilities required for planning tasks"].
>
> This dossier is an **evidence packet for the human thesis writer, NOT final thesis prose.**
> Each numbered claim is followed by its citation id → locator (resolvable in
> `thesis/citations/INDEX.md`) and a one-line "phrase it as" note. **Verbatim text the writer
> should copy lives in `evidence-packet.md`;** figures/tables in `figures-spec.md`. Copy
> quotes from there, do not paraphrase.

## Tier map for this dossier (admissibility per criteria §2)

- **Tier A — load-bearing (grounds core contribution claims):** **N1 ItiNera** (the
  "LLM-alone cannot plan" motivation + closest precedent); **01 Compound AI Systems** (the
  systems-not-models framing for the hybrid-architecture contribution).
- **Tier C — software-infrastructure (cite as software; NEVER as a paper):** S-VROOM,
  S-VALHALLA, S-OSRM — named in the thesis sentence for their *roles*; the deep algorithmic
  citations (N4 PyVRP, OSRM-PAPER) are deliberately deferred to Ch2/Ch3 per criteria §4.
- **Tier D — preprint-only (footnote only, explicitly labelled; never core evidence):** N2
  TRIP-PAL, N3 TravelAgent — **not used in this dossier** (criteria §4 prefers N1 for the
  same point).
- **Anti-fabrication (criteria §7):** the Reflexion "+22% ALFWorld" stat is FABRICATED and is
  **never cited** anywhere in Ch1. POI count = **310** everywhere (never the stale 255).

---

# §1.1 — Context & Problem Statement (monolithic LLMs cannot reliably plan)

**P1 — The "systems, not monolithic models" shift (motivating frame).** State-of-the-art AI
results are "increasingly obtained by compound systems with multiple components, not just
monolithic models," and this paradigm is expected to "remain a leading paradigm even as models
improve." [citation: 01 → Q3,Q5 — Tier A]. **Phrase as:** the opening context paragraph — the
field has moved from single-model prompting toward multi-component systems, and travel
planning is a domain where this shift is essential.

**P2 — Definition of a Compound AI System (the system class VOYO belongs to).** A compound AI
system is "a system that tackles AI tasks using multiple interacting components, including
multiple calls to models, retrievers, or external tools." [citation: 01 → Q1 — Tier A].
**Phrase as:** define the system class VOYO instantiates; this justifies treating the LLM as
one component rather than the whole planner.

**P3 — The core problem: monolithic LLMs hallucinate geography/prices/constraints and cannot
optimize (the problem statement, Tier-A grounded).** ItiNera — the closest peer-reviewed
precedent — establishes that "their [pure LLMs'] limitations in itinerary planning are
evident: (1) Pure LLMs cannot refer to specific POI lists, resulting in outdated or
hallucinated POIs. (2) LLMs lack the optimization capabilities required for planning tasks,
leading to suboptimal itineraries. Consequently, LLM-generated itineraries can be circuitous,
lack detail, and include impractical information." [citation: N1 → Q3 — Tier A]. **Phrase
as:** this is the problem statement itself — quote Q3 (it is the verbatim, quantified-adjacent
motivation the criteria demand). State plainly that an LLM asked to plan alone will (a)
hallucinate or stale-reference POIs and (b) produce geographically circuitous, infeasible
orderings because optimization is not in its competence.

**P4 — Ablation evidence that optimization must be a separate stage (why the problem is
fixable by separation).** ItiNera's own ablation shows removing the optimization module
(Cluster-aware Spatial Optimization) collapses route quality: Average Margin (route detour)
rises from **86.0 (full system) → 242.8 (no optimizer)** — roughly a 3× degradation.
[citation: N1 → Q5 — Tier A]. **Phrase as:** this is the proof-of-existence that detaching
optimization from the LLM is what restores feasibility; it directly motivates VOYO's
deterministic-feasibility contribution (§1.3) and is the empirical hook for VOYO's own
ablation (Ch4). **Do NOT** restate ItiNera's number as a VOYO result — label it as the
borrowed precedent that VOYO must replicate in-domain.

---

# §1.2 — The Hybrid-Deterministic Thesis (the contribution's one-sentence claim)

**H1 — The thesis sentence (use verbatim).** The argument of this thesis, in one sentence:
*VOYO couples an LLM (for intent + personalization) to deterministic optimization engines
(for reachability, routing, isochrones, matrices, feasibility, and time-window optimization),
because an LLM alone cannot reliably plan — it lacks optimization capability and hallucinates
geography and constraints.* [citation: criteria §1 → `thesis/criteria/thesis-criteria.md` §1
(the authoritative spine sentence)]. **Phrase as:** present this verbatim as the thesis's
central claim; the rest of Ch1 unpacks the two halves (what the LLM does vs what the engines
do).

**H2 — Separation of concerns, named (the trust boundary).** The LLM (CLEO) is responsible
ONLY for intent parsing, preference/memory state, and human-readable response composition; it
is explicitly NOT trusted with feasibility, geography, or numerical optimization.
Reachability (isochrones) and routing are delegated to **Valhalla**; VRPTW feasibility and
time-window-constrained optimization to **VROOM**; distance/travel-time matrices to **OSRM**.
[citation: criteria §1 → §1 (engine-role assignment); N1 → Q3 (why: LLMs lack the
optimization capability)]. **Phrase as:** a one-paragraph "who does what" — this becomes
Ch3's trust-boundary table; introduce it here as the design principle. **Note for the
writer:** the per-engine *academic* citations (N4 PyVRP for VRPTW, OSRM-PAPER for CH routing)
are developed in Ch2/Ch3; in Ch1 cite only the roles + the N1 motivation, to avoid widening
scope beyond the Ch1 citation set (criteria §4 Ch1 row: required = 01 + N1).

**H3 — Why this is the right split (intent is fuzzy; feasibility is not).** The rationale for
the split is asymmetric confidence: natural-language intent and personalization are
probabilistic and benefit from the LLM's flexibility, whereas reachability, time budgets, and
price lookups must be exactly correct. ItiNera corroborates that the failure mode of
LLM-only planning is precisely the deterministic parts — "circuitous" routes and "impractical
information." [citation: N1 → Q3 — Tier A]. **Phrase as:** one sentence of justification for
*why* the split is along the fuzzy/exact boundary; this pre-empts the reviewer question
"why not just prompt harder."

---

# §1.3 — Contributions

> **C0 — Contributions headline (single sentence).** *This thesis contributes a hybrid
> deterministic AI travel planner whose value is the strict separation of a probabilistic
> intent layer from deterministic optimization, instantiated over a verified, region-balanced
> Egyptian POI substrate with dual Egyptian/foreigner pricing.* [citation: criteria §1 → §1;
> N1 → Q3].

**C1 — Contribution 1: the hybrid architecture (LLM intent ↔ deterministic engines).** A
compound-AI architecture in which an LLM (CLEO) handles ONLY intent and personalization and
delegates every feasibility/geography/optimization decision to deterministic engines
(Valhalla / VROOM / OSRM), realizing the "multiple interacting components" pattern.
[citation: 01 → Q1,Q3 — Tier A (system class + "not monolithic models")]. This is the same
insight that grounds the closest precedent, ItiNera, which "integrates spatial optimization
with large language models" because pure LLMs lack optimization capability.
[citation: N1 → Q1,Q3 — Tier A]. **Phrase as:** state the architecture as a contribution,
citing 01 for the compound-systems pattern and N1 as the peer-reviewed precedent VOYO
instantiates for Egyptian tourism. Mark clearly that the *detailed* wiring and the ablation
config are Ch3/Ch4 contributions, not Ch1.

**C2 — Contribution 2: the verified 310-POI Egyptian substrate with dual Egyptian/foreigner
pricing.** A curated point-of-interest database of **310 active POIs** (0 duplicates), spanning
nine Egyptian regions, with provenance-grounded descriptions and a dual Egyptian/foreigner
ticket-price layer. Dual (Egyptian + foreigner) prices are sourced from the official
egymonuments.gov.eg feed and cover **58 POIs** as verified upsert rows; authoritative gov.eg
descriptions cover **76 POIs**, and POIs with any enrichment total **97**. [citation: criteria
§4 → stale-number sweep (POI count = **310**; dual gov.eg prices = **58**; gov.eg descriptions
= **76**; any-enrichment = **97**); provenance → `data/ticket_prices_upsert.sql` (exactly 58
dual-price `UPDATE pois` rows verified by line count, 2026-06-17)]. **Phrase as:** name the
substrate as a contribution and give the four canonical numbers; emphasize dual pricing as the
Egypt-tourism-specific novelty (no prior system in the citation base ships both Egyptian and
foreigner prices). **HARD RULE (criteria §4):** use **310** for the POI count — NEVER 255.
`thesis/evidence/05-db-completeness.json` currently reports `total_active_pois: 255` because it
is the **pre-rebuild STALE snapshot** (criteria §5 flags it ⚠️ regenerate → 310); cite 310 in
prose and flag the file for regeneration (Ch6 owns the refresh).

**C3 — Contribution 3: the deterministic feasibility layer.** A feasibility layer built on
three deterministic engines — **Valhalla** (isochrones / routing), **VROOM** (VRPTW
feasibility and time-window optimization), and **OSRM** (distance/travel-time matrices) — such
that no itinerary is ever committed without passing a deterministic feasibility check. The
LLM never owns feasibility. [citation: criteria §1 → §1 (engine-role assignment, the trust
boundary); N1 → Q3 (the motivation: LLMs "lack the optimization capabilities required for
planning tasks")]. **Phrase as:** name the feasibility layer as a contribution and tie it
directly to N1's diagnosis — the deterministic layer is the fix for the optimization-capability
gap. **Scope note for the writer:** the *academic* grounding that VRPTW is solved
near-optimally by hybrid genetic search (N4 PyVRP, ~0.22% gap) and that contraction-hierarchy
routing is real-time (OSRM-PAPER) is developed in Ch2/Ch3 — Ch1 only names the layer and the
motivation, per the criteria §4 Ch1 citation set.

---

# §1.4 — "LLM-alone cannot plan" motivation (the quantified motivation block)

**M1 — The verbatim motivation quote (use this, Tier A).** The single best-sourced motivation
sentence is ItiNera's, peer-reviewed at EMNLP 2024 Industry Track + KDD UrbComp 2024 Best
Paper: pure LLMs "lack the optimization capabilities required for planning tasks, leading to
suboptimal itineraries," and "can be circuitous, lack detail, and include impractical
information." [citation: N1 → Q3 — Tier A]. **Phrase as:** the centerpiece "why this thesis"
paragraph; quote Q3 verbatim and attribute the venue exactly (EMNLP 2024 Industry Track; Best
Paper, KDD UrbComp 2024 — per `thesis/citations/new-route-opt/itinera/source.md`).

**M2 — Quantified degradation when optimization is removed (the borrowed ablation).** Removing
the optimization stage collapses itinerary quality: ItiNera's ablation (Shanghai) reports
Average Margin **86.0 → 242.8** when the spatial optimizer is ablated — a ~3× detour blow-up.
[citation: N1 → Q5 — Tier A]. **Phrase as:** the quantitative hook — "the published precedent
shows a 3× collapse when the optimizer is removed; this thesis must reproduce that gap in the
Egyptian domain." Forward-point to VOYO's own ablation (Ch4 keystone experiment), without
claiming VOYO's number yet (PENDING the eval harness).

**M3 — The hallucination axis (geography/prices, not just optimization).** The motivation is
two-pronged, not only optimization: pure LLMs "cannot refer to specific POI lists, resulting in
outdated or hallucinated POIs." [citation: N1 → Q3 — Tier A]. **Phrase as:** pair with M1 — the
thesis targets BOTH failure modes (hallucinated geography/prices AND missing optimization),
which is exactly why VOYO grounds every POI/price (Contribution C2) AND runs a deterministic
feasibility layer (Contribution C3).

**M4 — Why VOYO is not just re-doing ItiNera (positioning, pre-empting the reviewer).** ItiNera
operates on "1233 top-rated urban itineraries and 7578 POIs" for urban China and uses
hierarchical TSP; VOYO targets Egyptian tourism over a verified 310-POI substrate with dual
pricing and a VRPTW-grade feasibility solver (VROOM), which ItiNera does not deploy.
[citation: N1 → Q7 (ItiNera dataset = 7578 POIs, urban China); N1 → Q4 (hierarchical TSP, not
VRPTW); criteria §1 (VOYO's VRPTW-grade feasibility + Egyptian substrate)]. **Phrase as:** one
positioning paragraph closing the motivation — the gap is "Egyptian domain + dual pricing +
VRPTW feasibility, none of which the closest precedent provides." **Note:** the full
research-gap statement with explicit VOYO-vs-ItiNera delta belongs in Ch2.2 (criteria §3); Ch1
gives only the one-paragraph forward-pointer.

---

# §1.5 — Thesis roadmap (structure, no new claims)

**R1 — Chapter map (no new evidence).** Ch2 develops the four-theme literature review and the
route-optimization crux (criteria §3); Ch3 specifies the architecture, the delegate-to-solver
contract, and the ablation protocol; Ch4 defines the evaluation strategy and reports measured
vs pending metrics; Ch5 concludes; Ch6 documents the 310-POI data pipeline and dual-price
enrichment. [citation: criteria §4 → per-chapter dossier rubric]. **Phrase as:** a short
roadmap paragraph; no uncited claims. **Self-check:** nothing in §1.5 introduces a new factual
claim — it only names what later chapters contain, which is already in criteria §4.

---

## Ch1 acceptance self-check (against criteria §4 Ch1 row)

- **Problem statement present?** Yes — P3 (Tier-A grounded via N1 Q3, verbatim).
- **Hybrid-deterministic thesis sentence verbatim?** Yes — H1 quotes criteria §1 verbatim.
- **Contributions list?** Yes — C1 (hybrid architecture), C2 (310-POI substrate + dual
  pricing), C3 (deterministic feasibility layer).
- **"LLM-alone cannot plan" motivation, quantified?** Yes — M1 (verbatim Q3) + M2 (N1 Q5
  ablation, 86.0 → 242.8) — the criteria "Excellence" bar (quantified motivation via ItiNera's
  "LLMs lack optimization" quote).
- **Required citations present?** Yes — **01** (P1,P2,C1) + **N1** (P3,P4,H2,H3,C0,C1,C3,M1–M4).
- **POI count = 310 everywhere?** Yes — C2 uses 310; 255 flagged as STALE, never as a positive
  claim.
- **Reflexion "+22% ALFWorld" fabricated stat avoided?** Yes — not cited anywhere.
- **Tier D (TRIP-PAL/TravelAgent) used?** No — omitted per criteria preference for N1.
- **Core claims on Tier A?** Yes — every core claim (problem statement, motivation,
  architecture, feasibility layer) traces to N1 (Tier A) and/or 01 (Tier A).
