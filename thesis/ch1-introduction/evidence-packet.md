# Ch1 — Introduction — EVIDENCE PACKET (verbatim quotes + numbers to copy)

> **Purpose:** the verbatim quotes, numbers, and tables that `dossier.md` references. The
> human thesis writer copies from THIS file (never paraphrases a quote, never invents a
> number). Every entry carries its citation id → locator, all resolvable in
> `thesis/citations/INDEX.md`. Anti-fabrication flags (criteria §7) are called out at the
> bottom.

---

## A. The thesis sentence (use verbatim) — from criteria §1

> *VOYO couples an LLM (for intent + personalization) to deterministic optimization engines
> (for reachability, routing, isochrones, matrices, feasibility, and time-window
> optimization), because an LLM alone cannot reliably plan — it lacks optimization capability
> and hallucinates geography and constraints.*

- **Source:** `thesis/criteria/thesis-criteria.md` §1 ("The thesis argument (the spine every
  section must serve)"), the single sentence the criteria instructs every chapter to return to.
- **Use:** the central claim of Ch1 (dossier claim H1). Quote it verbatim.

---

## B. N1 ItiNera — Tier A (the load-bearing motivation + precedent)

**Venue string to cite (verbatim, from the verified source.md):**
> ITINERA: Integrating Spatial Optimization with Large Language Models for Open-domain Urban
> Itinerary Planning — Yihong Tang et al. — **EMNLP 2024 Industry Track Proceedings**; also
> **Best Paper Award, KDD Urban Computing Workshop (UrbComp) 2024** — arXiv:2402.07204.
- **Locator:** `thesis/citations/new-route-opt/itinera/source.md` (Bibliographic record) +
  GitHub README provenance line.

### N1-Q3 — THE motivation quote (copy verbatim; grounds P3, M1, M3, and the problem statement)
> "their limitations in itinerary planning are evident [...] (1) Pure LLMs cannot refer to
> specific POI lists, resulting in outdated or hallucinated POIs. (2) LLMs lack the
> optimization capabilities required for planning tasks, leading to suboptimal itineraries.
> Consequently, LLM-generated itineraries can be circuitous, lack detail, and include
> impractical information."
- **Locator:** arXiv:2402.07204, §1 Introduction, p.1 (`thesis/citations/new-route-opt/itinera/quotes.md` Q3).
- **Phrase as:** this is *the* "LLM-alone cannot plan" sentence the criteria demand; quote it
  whole and attribute venue exactly.

### N1-Q5 — The ablation number (the quantified motivation; grounds P4, M2)
- **Verbatim discussion:** "Removing the CSO module worsens the Average Margin and Overlaps but
  improves Recall Rate, POI Quality, and Match, showing the full model balances alignment with
  spatial ability."
- **Verbatim table row (Average Margin = AM):**
  - "ITINERA (full) ✓ ✓ ✓ ✓ ✓ 31.4 **86.0** 0.42 69.8 64.6 72.0"
  - "ITINERA w/o CSO ✓ ✓ ✓ × ✓ 32.8 **242.8** 1.04 72.1 60.2 74.2"
- **Locator:** arXiv:2402.07204, Table 2 (Ablation, Shanghai dataset), p.6; discussion p.7.
- **The number:** Average Margin **86.0 (full) → 242.8 (no optimizer)** ≈ a 3× detour blow-up.
- **Phrase as:** "the published precedent shows roughly a 3× collapse in route quality when the
  optimizer is removed." Label clearly as **ItiNera's** result, NOT VOYO's.

### N1-Q1 — System definition (grounds C1 positioning)
> "we introduce the novel task of Open-domain Urban Itinerary Planning (OUIP) [...] We then
> present ITINERA, an OUIP system that integrates spatial optimization with large language
> models to provide customized urban itineraries based on user needs."
- **Locator:** arXiv:2402.07204, Abstract, p.1.

### N1-Q4 — ItiNera uses hierarchical TSP, NOT VRPTW (grounds M4 positioning gap)
> "we compute spatial clusters of the retrieved POIs [...] addressing cluster-aware spatial
> optimization by solving a hierarchical traveling salesman problem [...], a common and
> fundamental spatial reasoning task [...]."
- **Locator:** arXiv:2402.07204, §3.5, p.4.
- **Phrase as:** the closest precedent uses hierarchical TSP; VOYO adds a VRPTW-grade
  feasibility solver (VROOM) — that delta is the positioning gap.

### N1-Q7 — ItiNera dataset scale (grounds M4: it is urban China, not Egypt)
> "In total, the dataset covers 1233 top-rated urban itineraries and 7578 POIs."
- **Locator:** arXiv:2402.07204, §4.1, p.5.
- **Phrase as:** ItiNera's substrate is 7,578 POIs across urban China; VOYO's is a verified
  310-POI Egyptian substrate — different domain, different pricing model.

---

## C. 01 Compound AI Systems — Tier A (the systems-not-models frame)

**Venue string to cite:**
> The Shift from Models to Compound AI Systems — Zaharia et al. — Berkeley Artificial
> Intelligence Research (BAIR) Blog, 18 Feb 2024 — https://bair.berkeley.edu/blog/2024/02/18/compound-ai-systems/
- **Accuracy flag (from quotes.md):** this is a **blog post, not a peer-reviewed paper.**
  Acceptable for thesis-level motivation; pair with the peer-reviewed N1 for empirical claims
  (which the dossier does — every 01-backed claim sits next to an N1-backed claim).

### 01-Q1 — Definition of a Compound AI System (grounds P2, C1)
> "We define a Compound AI System as a system that tackles AI tasks using multiple interacting
> components, including multiple calls to models, retrievers, or external tools."
- **Locator:** BAIR Blog, "Why Use Compound AI Systems?" section.

### 01-Q3 — Systems, not monolithic models (grounds P1, C1)
> "state-of-the-art AI results are increasingly obtained by compound systems with multiple
> components, not just monolithic models."
- **Locator:** BAIR Blog, "Developing Compound AI Systems" section.

### 01-Q5 — The paradigm will persist (grounds P1)
> "we believe compound AI systems will remain a leading paradigm even as models improve."
- **Locator:** BAIR Blog, "Why Use Compound AI Systems?" section.

---

## D. The 310-POI substrate + dual-pricing numbers (grounds C2)

> ⚠️ **STALE-NUMBER WARNING (criteria §4, §5).** The canonical POI count is **310**.
> `thesis/evidence/05-db-completeness.json` currently reports `total_active_pois: 255` — this
> is the **pre-rebuild STALE snapshot** flagged for regeneration (criteria §5: "⚠️ regenerate
> (was 255)"). **Use 310 in all Ch1 prose; never 255.** The regeneration is owned by Ch6.

| Quantity | Canonical value | Source of truth | Status |
|---|---|---|---|
| Active POIs | **310** | criteria §4 (stale-number sweep) | ✅ use 310; `05-db-completeness.json` (255) is STALE — regenerate in Ch6 |
| Duplicates | 0 | `05-db-completeness.json` `duplicates` (pre-rebuild audit) | ✅ structural integrity unaffected by 255→310 |
| Dual (Egyptian + foreigner) ticket-price rows | **58 POIs** | criteria §4 + `data/ticket_prices_upsert.sql` (exactly 58 `UPDATE pois` rows, counted 2026-06-17) | ✅ verified by line count |
| Authoritative gov.eg descriptions | **76 POIs** | criteria §4 | ✅ canonical |
| POIs with any enrichment | **97** | criteria §4 | ✅ canonical |

**Dual-price provenance (verbatim from the SQL header — copy when describing enrichment):**
> "-- data/ticket_prices_upsert.sql / Idempotent upsert of ticket_prices JSONB for POIs matched
> to egymonuments.gov.eg / Gate: (real POI match) AND (prices.json matched=true) AND
> (egyptian_adult & foreigner_adult both non-null ints). / Guard: WHERE ticket_prices IS NULL
> -> NEVER overwrites an existing value. Re-runnable. / JSONB shape enforced by constraint:
> {"egyptian":N,"foreigner":N,"currency":"EGP"}."
- **Locator:** `data/ticket_prices_upsert.sql`, header comment block (lines 1–10).
- **Sample rows (verbatim) — for an illustrative dual-price example:**
  - `UPDATE pois SET ticket_prices = '{"egyptian":100,"foreigner":1000,"currency":"EGP"}' WHERE name = 'Great Pyramid of Giza (Khufu)';`
  - `UPDATE pois SET ticket_prices = '{"egyptian":40,"foreigner":600,"currency":"EGP"}' WHERE name = 'Karnak Temple Complex';`
  - `UPDATE pois SET ticket_prices = '{"egyptian":60,"foreigner":700,"currency":"EGP"}' WHERE name = 'Giza Plateau';`
- **Phrase as:** the dual Egyptian/foreigner price layer is a VOYO-specific contribution; no
  system in the citation base ships both price tiers. The 58 figure is verifiable end-to-end
  (criteria mandate ↔ SQL line count).

---

## E. Engine roles (the trust boundary) — from criteria §1 (grounds H2, C3)

| Engine (Tier C software) | Role delegated to it (LLM does NOT do this) |
|---|---|
| **Valhalla** | isochrones (reachability) + routing |
| **VROOM** | VRPTW feasibility + time-window-constrained optimization |
| **OSRM** | distance / travel-time matrices |

- **Source:** `thesis/criteria/thesis-criteria.md` §1 ("deterministic optimization engines
  handle everything that must be correct: Valhalla for isochrones and routing; VROOM for
  VRP/VRPTW feasibility and time-window-constrained optimization; OSRM for distance/travel-time
  matrices").
- **Scope note:** the *academic* citations for these engines (N4 PyVRP grounds VRPTW;
  OSRM-PAPER grounds contraction-hierarchy routing) are **Ch2/Ch3** material per criteria §4.
  Ch1 names only the roles + the N1 motivation; do not pull N4/OSRM-PAPER into Ch1 to avoid
  widening scope beyond the Ch1 citation set (01 + N1).

---

## F. Anti-fabrication flags (criteria §7 — enforced)

1. **Reflexion "+22% ALFWorld" is FABRICATED** — the librarian proved it absent from the paper.
   **Never appears in Ch1.** (The verbatim Reflexion result, if ever needed elsewhere, is
   "completing 130 out of 134 tasks" + "91% HumanEval pass@1" — but Ch1 does not use Reflexion
   at all.)
2. **POI count = 310**, never 255. The 255 in `05-db-completeness.json` is STALE; flag it for
   Ch6 regeneration and use 310 in prose.
3. **Tier D (N2 TRIP-PAL, N3 TravelAgent) not used in Ch1.** Criteria §4 prefers N1 (Tier A)
   for the "LLM-alone cannot plan" point; the dossier honors this and omits both preprints.
4. **Software never cited as a paper.** Valhalla/VROOM/OSRM are named in the thesis sentence
   by role only; no invented paper exists for VROOM/Valhalla (per S-VROOM "no paper exists,"
  Issue #735).
5. **N1's 86.0 → 242.8 is ItiNera's number, not VOYO's.** VOYO's own ablation result is PENDING
   the eval harness (Ch4 keystone) and is NEVER stated as a number in Ch1.
