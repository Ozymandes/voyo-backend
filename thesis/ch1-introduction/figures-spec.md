# Ch1 — Introduction — FIGURES & TABLES SPEC

> **Principle (criteria §5).** Figures/tables are derived from `thesis/evidence/` or cited
> quote banks — never hand-drawn, never inferred. Ch1 is an *introduction* and should be
> figure-light: it introduces contributions and motivation, deferring measurement figures to
> Ch3/Ch4. Two artifacts are proposed: one *table* (contributions-at-a-glance, derived from
> criteria §4 + the dossier) and one *figure forward-pointer* (the architecture teaser, owned
> by Ch3).

---

## Table 1.1 — Contributions at a glance (NEW; Ch1-owned)

- **Type:** 3-row table (one per contribution), columns: *Contribution | What it is | Key
  number / scope | Primary citation*.
- **Rows (verbatim from dossier §1.3):**
  | # | Contribution | Key number / scope | Primary citation |
  |---|---|---|---|
  | C1 | Hybrid architecture: LLM (CLEO) intent ↔ deterministic engines | LLM does intent+personalization ONLY; engines do feasibility | 01 (Q1,Q3); N1 (Q1,Q3) |
  | C2 | Verified Egyptian POI substrate with dual pricing | **310** active POIs, 0 duplicates; **58** dual-price POIs (gov.eg); **76** gov.eg descriptions; **97** any-enrichment | criteria §4; `data/ticket_prices_upsert.sql` |
  | C3 | Deterministic feasibility layer (Valhalla / VROOM / OSRM) | no itinerary committed without a deterministic feasibility check | criteria §1; N1 (Q3) |
- **Data source:** `dossier.md` §1.3 (C1–C3) + `evidence-packet.md` §D (the 310/58/76/97
  numbers) + `evidence-packet.md` §E (engine roles).
- **Status:** ✅ producible now (all numbers verified in evidence-packet §D).
- **Writer note:** render POI count as **310**; add a footnote that
  `evidence/05-db-completeness.json` still reports 255 (STALE, regenerate in Ch6).

---

## Figure 1.1 — Architecture teaser (FORWARD-POINTER; owned by Ch3, not regenerated here)

- **Type:** the single "LLM intent layer ↔ deterministic engines" block diagram.
- **Data source / canonical artifact:** `fig_3_1_architecture` (retained per criteria §5 —
  "not count-dependent"). Ch1 may **reference** it ("see Figure 3.1") but should **not** invent
  a separate architecture figure; reuse Ch3's.
- **Status:** ✅ retained (no regeneration needed). Ch1 cites it as a forward-pointer only.
- **Writer note:** if the thesis style requires a Ch1 teaser figure, reuse `fig_3_1_architecture`
  verbatim — do NOT redraw, to avoid divergence between Ch1 and Ch3.

---

## Figure 1.2 — Borrowed ablation hook (OPTIONAL; forward-pointer to Ch4 keystone)

- **Type:** a small annotated bar showing ItiNera's Average Margin **86.0 (full) → 242.8
  (no optimizer)** as the *borrowed* precedent that motivates VOYO's own ablation.
- **Data source:** `thesis/citations/new-route-opt/itinera/quotes.md` Q5 (Table 2, Shanghai).
- **Status:** ✅ producible now from the N1 quote bank (it is ItiNera's number, not VOYO's).
- **Mandatory labelling:** title/caption MUST read "ItiNera (Tang et al., 2024) ablation —
  VOYO's in-domain replication is the Ch4 keystone experiment (PENDING eval harness)." **Never**
  present this bar as a VOYO result.
- **Writer note:** optional — include only if the advisor wants a visual hook in §1.4; otherwise
  state the 86.0 → 242.8 numbers in prose (dossier M2) and skip the figure.

---

## Figures/tables Ch1 does NOT introduce (scope discipline)

- No latency / retrieval / feasibility / UX figures — those are Ch4, and most are **PENDING the
  eval harness** (criteria §5). Ch1 must not preview pending numbers.
- No DB-completeness figure — that is Ch6's, and `05-db-completeness.json` is the STALE 255
  snapshot awaiting regeneration to 310.
- No lit-review comparison tables — those are Ch2's (Tables 2.1–2.3).
