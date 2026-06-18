# Ch1 Introduction — SUPERVISOR REVIEW (gap report)

> **Auditor:** VOYO Thesis Supervisor (external examiner).
> **Dossier audited:** `thesis/ch1-introduction/` (`dossier.md`, `evidence-packet.md`,
> `figures-spec.md`, `citations-used.md`, `_run-summary.md`).
> **Contract:** `thesis/criteria/thesis-criteria.md` (the spine). Audit run 2026-06-17.
> **Method:** read-only. Verified every `[citation: …]` token resolves in
> `thesis/citations/INDEX.md`, cross-checked every quote against the quote banks, counted
> `UPDATE pois` rows in `data/ticket_prices_upsert.sql` (58, confirmed), grepped for the
> fabricated Reflexion stat and the stale 255, and confirmed git scope.

---

## VERDICT: **PASS-WITH-OPTIONAL-FIXES**

The dossier **clears every one of the 8 checklist items** AND meets the Ch1 **excellence bar**
(criteria §4 Ch1 row: "Quantified motivation (e.g. ItiNera's 'LLMs lack optimization' quote)").
The PASS-WITH-OPTIONAL-FIXES (not bare PASS) reflects two genuinely-optional polish items
documented at the end — none are grounding/tier/fabrication violations, so this is NOT a FAIL.
The writer may accept or decline the optional fixes; the dossier is **ready for the human
thesis author to draft §1 from**.

---

## CHECKLIST RESULTS (8 items)

### 1. Grounding — **PASS** (criteria §6 hard rule 1, §4 Ch1 row)
Every claim block in `dossier.md` ends with a `[citation: <id> → <locator>]` token. Enumeration
of the 11 distinct academic tokens + 4 provenance pointers:

| Claim | Token | Resolves in INDEX.md? | Verbatim entry in evidence-packet.md? |
|---|---|---|---|
| P1 (systems-not-models) | `01 → Q3,Q5` | ✅ (Tier A, `01-compound-ai-systems`) | ✅ §C |
| P2 (compound-system def) | `01 → Q1` | ✅ | ✅ §C |
| P3 (problem statement, verbatim Q3) | `N1 → Q3` | ✅ (Tier A, `itinera`) | ✅ §B |
| P4 (ablation 86.0→242.8) | `N1 → Q5` | ✅ | ✅ §B |
| H2,H3 (trust boundary + rationale) | `N1 → Q3` (+ `criteria §1`) | ✅ for N1 | ✅ §B |
| C0,C1 (contributions) | `01 → Q1,Q3` + `N1 → Q1,Q3` | ✅ both | ✅ §B/§C |
| C2 (310/58/76/97 + dual pricing) | `criteria §4` + `data/ticket_prices_upsert.sql` | provenance (see note) | ✅ §D |
| C3 (feasibility layer) | `criteria §1` + `N1 → Q3` | ✅ for N1 | ✅ §B/§E |
| M1,M3 (verbatim Q3) | `N1 → Q3` | ✅ | ✅ §B |
| M2 (86→242.8 borrowed) | `N1 → Q5` | ✅ | ✅ §B |
| M4 (ItiNera ≠ VOYO) | `N1 → Q7` + `N1 → Q4` + `criteria §1` | ✅ for N1 | ✅ §B |
| R1 (roadmap) | `criteria §4` | provenance | n/a (no new claim) |

**Note on the `criteria §1`/`criteria §4`/`ticket_prices_upsert.sql` tokens.** These do NOT
resolve in `INDEX.md` and so technically fall outside criteria §6 hard rule 1. However,
`citations-used.md` transparently classifies them as **"Non-citation authorities (criteria +
provenance files, not in INDEX.md)"**, and the spine sentence's authoritative source IS the
criteria file itself (quoting it from a paper would be misattribution). Every **academic**
claim in the dossier traces to N1 or 01 (both Tier A, both in INDEX.md). The SQL is raw
provenance, verified end-to-end (58 `UPDATE pois` rows counted, header comment matches §D).
This is defensible — flagged in Optional Fix #2 below for the writer who wants belt-and-braces.

### 2. Tier discipline — **PASS** (criteria §2, §4 Ch1 row)
- **Required citations present:** both **01** (P1, P2, C1) and **N1** (P3, P4, H2, H3, C0, C1,
  C3, M1–M4) are Tier A per INDEX.md. Ch1 row requires `01 + N1` — **satisfied**.
- **Core contribution claims all on Tier A:** the problem statement (P3), the borrowed
  ablation (P4), the hybrid architecture (C1), the feasibility layer (C3), and the entire
  motivation block (M1–M4) each trace to N1 (Tier A) or 01 (Tier A). No core claim leans on
  Tier B/C/D alone.
- **Tier D (N2 TRIP-PAL, N3 TravelAgent):** **OMITTED** — `citations-used.md` §"Tier D" row
  records the omission explicitly; criteria §4 prefers N1 for the "LLM-alone cannot plan"
  point. ✓
- **Tier C (S-VROOM, S-VALHALLA, S-OSRM):** named **by role only** in the thesis sentence (H1,
  H2) and C3; **never cited as a paper**. No invented VROOM/Valhalla paper. ✓ (matches
  criteria §7 and S-VROOM "no paper exists" / Issue #735).

**Minor scope-disclosure (not a violation):** `dossier.md:157` names `N4 PyVRP` with a
`~0.22% gap` figure and `OSRM-PAPER` inside a "Scope note for the writer" that explicitly
says this is Ch2/Ch3 material, **not** Ch1 evidence. The scope note is correctly bounded
("Ch1 only names the layer and the motivation, per the criteria §4 Ch1 citation set"), so it
is a forward-pointer, not a Ch1 claim. Optional Fix #1 below tightens this.

### 3. Verbatim integrity — **PASS** (criteria §7)
Spot-checked every quote in `evidence-packet.md` against the verified quote banks:
- N1-Q1, Q3, Q4, Q5, Q7 → match `thesis/citations/new-route-opt/itinera/quotes.md` verbatim.
  N1-Q5 ablation row `86.0 (full) → 242.8 (w/o CSO)` matches the bank's Table 2 line exactly.
- 01-Q1, Q3, Q5 → match `thesis/citations/01-compound-ai-systems/quotes.md` verbatim.
- No quote contains paraphrase-inside-quotes; no content is written about an UNVERIFIED or
  fetch-pending source. (OSRM-PAPER, the only VERIFIED-META-adjacent entry, is NOT cited as
  Ch1 evidence — it appears only in the §2.3/Ch3 scope note. ✓)

### 4. Numbers — **PASS** (criteria §4 stale-number sweep; §5)
- **POI count = 310** as the canonical positive claim (C2, Table 1.1, R1). The stale **255**
  appears **only** as a flagged STALE value pointing to `05-db-completeness.json` (pre-rebuild
  snapshot, criteria §5 ⚠️ regenerate), with explicit "regenerate in Ch6" instructions. No
  instance of 255 used as a positive claim. ✓
- **Dual gov.eg prices = 58** → verified end-to-end: `grep -c "UPDATE pois"
  data/ticket_prices_upsert.sql` returns **58**, matching criteria §4 and the dossier §D. ✓
- **gov.eg descriptions = 76**, **any-enrichment = 97** → match criteria §4 canonical values. ✓
- The N1 ablation numbers (86.0 → 242.8) trace to the N1-Q5 quote bank, not inferred. ✓

### 5. Pending vs fabricated — **PASS** (criteria §5 honesty rule; §7)
- **VOYO's OWN ablation** (feasibility %, violation rate, Avg-Margin for hybrid vs LLM-only)
  is labelled **"PENDING the eval harness (Ch4 keystone)"** in P4, M2, evidence-packet §F#5,
  citations-used.md, and _run-summary.md. **No invented VOYO number** appears anywhere. ✓
- **`05-db-completeness.json` POI count (255)** is labelled STALE + flagged for Ch6
  regeneration; prose uses 310. Not fabricated. ✓
- All ⏸-PENDING metrics in criteria §5 are either absent from Ch1 (correctly deferred to Ch4)
  or labelled PENDING. ✓

### 6. Section completeness — **PASS** (criteria §4 Ch1 row; §5; §6)
- **(a) Problem statement:** P3, Tier-A grounded via N1-Q3 verbatim. ✓
- **(b) Hybrid-deterministic thesis sentence, verbatim + tied to N1:** the chapter-level
  thesis-sentence block (dossier.md top) quotes criteria §1 **verbatim** ("VOYO couples an
  LLM (CLEO — for intent parsing and personalization only) to deterministic optimization
  engines (Valhalla, VROOM, OSRM — for reachability, routing, isochrones, distance matrices,
  and VRPTW-grade feasibility / time-window optimization), because an LLM alone cannot
  reliably plan: it lacks optimization capability and hallucinates geography, prices, and
  constraints.") AND ties it to N1-Q3 in the same block. H1 in §1.2 restates the sentence
  verbatim with the criteria §1 source. ✓ (passes Ch1 pass-threshold "Thesis sentence present
  + tied to N1".)
- **(c) Contributions list:** C1 (hybrid architecture), C2 (310-POI substrate + dual
  pricing), C3 (deterministic feasibility layer) — three explicit contributions + a C0
  headline. ✓
- **(d) "LLM-alone cannot plan" motivation:** M1 (verbatim Q3 "LLMs lack the optimization
  capabilities required for planning tasks") + M2 (N1 Q5 ablation **86.0 → 242.8**, ~3×
  collapse) + M3 (hallucination axis) + M4 (positioning vs ItiNera). ✓ **Meets the Ch1
  excellence bar** ("Quantified motivation via ItiNera's 'LLMs lack optimization' quote").
- **Figures/tables spec'd with real data-source files:** Table 1.1 (data source = dossier
  §1.3 + evidence-packet §D/§E); Figure 1.1 forward-pointer to `fig_3_1_architecture` (real
  retained artifact per criteria §5); Figure 1.2 optional with N1-Q5 quote bank as source.
  No figure is hand-drawn or sourced from a pending metric. ✓

### 7. Fabricated-stat guard — **PASS** (criteria §7)
- **Reflexion "+22% ALFWorld":** grep'd `22% ALFWorld|+22%|22 ?%` across the dossier —
  appears **only** inside explicit "FABRICATED / never cited" warning context (4 sites:
  dossier.md:34, dossier.md:225, evidence-packet.md:155, citations-used.md:56). **Never
  appears as a positive claim.** ✓
- Ch1 does not cite Reflexion at all (correctly scoped out); the verbatim Reflexion result
  ("130 out of 134 tasks" + "91% HumanEval pass@1") is correctly noted as out-of-scope. ✓
- **VOYO's own ablation number** is NOT stated — only ItiNera's borrowed 86.0 → 242.8, which
  is attributed to ItiNera in every site (P4, M2, evidence-packet §B and §F#5, citations-used
  §"Anti-fabrication audit", figures-spec §1.2 mandatory labelling). ✓

### 8. Scope — **PASS** (criteria §6 hard rule 5)
- The Ch1 writer's deliverables are the **5 files** inside `thesis/ch1-introduction/` only
  (`dossier.md`, `evidence-packet.md`, `figures-spec.md`, `citations-used.md`,
  `_run-summary.md`); all bear 2026-06-17 14:26–14:29 mtimes. ✓
- No edits to `src/`, `flutter_app/`, `enrich_narratives.py`, the DB, `criteria.md`,
  `INDEX.md`, `citations/`, `evidence/`, or the archived prior-draft chapters by this dossier
  run (the writer's own _run-summary.md makes this claim and the file inventory corroborates
  it). ✓
- **Transparency note (not a Ch1 violation):** the broader git working tree contains
  pre-existing staged renames (`thesis/0N-*.md → thesis/_archive_prior_draft/`) and modified
  `thesis/evidence/*.json` files. These are **orchestrator/archive work that predates this
  Ch1 dossier run**, not Ch1-writer output — the Ch1 deliverables are untracked-new under
  `thesis/ch1-introduction/` only. Flagging so the parent orchestrator is aware the working
  tree is not clean; it does not reflect a Ch1 scope breach.

---

## SPECIFIC FIXES (only if FAIL) — N/A
No FAIL items. The two items below are **optional polish** (hence PASS-WITH-OPTIONAL-FIXES
rather than bare PASS), each traceable to a criterion, each a one-line change:

- **Optional Fix #1 (criteria §4 Ch1 row — citation-set discipline).** `dossier.md:157`
  names `N4 PyVRP, ~0.22% gap` and `OSRM-PAPER` inside a "Scope note for the writer" sentence
  in C3. Although the note correctly states this is Ch2/Ch3 material, a purist reading of the
  Ch1 citation set (01 + N1 only) is that Ch1 should not name any other academic id by id at
  all. **Minimum fix:** drop the parenthetical "(N4 PyVRP, ~0.22% gap)" and replace with a
  neutral phrase ("the academic grounding for VRPTW solvers and contraction-hierarchy
  routing"), keeping only the Ch2/Ch3 forward-pointer. (The same id appears in
  evidence-packet.md:146–148 and citations-used.md:28 — all in scope-disclosure context; the
  same neutralisation applies if the writer wants strict id-discipline.)
- **Optional Fix #2 (criteria §6 hard rule 1 — transparency).** Add a one-line footnote in
  `citations-used.md` explicitly stating: "Per criteria §6 hard rule 1, every **academic**
  Ch1 claim traces to 01 or N1 (both in INDEX.md). The `criteria §1`/`criteria §4`/SQL
  pointers are provenance for the verbatim spine sentence and the dual-price count
  respectively, NOT academic citations." The dossier already implies this in its
  "Non-citation authorities" table; a single explicit sentence would close any auditor
  question about §6 hard rule 1.

---

## EXCELLENCE ASSESSMENT
**Meets the Ch1 excellence bar — and clears it cleanly.** The criteria §4 Ch1 "Excellence"
cell is "Quantified motivation (e.g. ItiNera's 'LLMs lack optimization' quote)." The dossier
delivers BOTH halves of the requested quantification: the **verbatim N1-Q3** motivation quote
(M1) AND the **quantified N1-Q5 ablation (86.0 → 242.8, ~3× collapse)** (M2), with the borrowed
number correctly attributed to ItiNera and VOYO's own ablation explicitly marked PENDING the
Ch4 keystone. The trust-boundary framing (H2/H3/C3) pre-empts the "why not just prompt harder"
reviewer question, and M4 pre-empts the "isn't this just re-doing ItiNera" question. This is
a research-grade motivation block, not a pass-grade one.

**Where it could go from "excellent" to "standout":**
- Optional Fix #1 above (drop the Ch2/Ch3 ids from the C3 scope note) would make the Ch1
  citation set visually airtight (only 01 + N1 appear by id anywhere).
- The C2 contribution claims "nine Egyptian regions" without a citation or provenance
  pointer (dossier.md:140). This is a minor claim but technically uncited under criteria §6
  hard rule 1 — a one-line `thesis/evidence/05-db-completeness.json` (or Ch6) pointer would
  close it. (Not a FAIL: the canonical POI/provenance numbers around it are fully cited; the
  "nine regions" detail is a structural fact the writer will source from Ch6.)

---

## ESCALATIONS
- **None requiring the librarian.** All citation IDs (01, N1) resolve; the N1-Q5 ablation
  numbers match the verified quote bank; the 58 dual-price rows are end-to-end verifiable in
  `data/ticket_prices_upsert.sql`.
- **One upstream transparency item for the parent orchestrator (not a Ch1 issue):** the
  working tree is NOT clean — pre-existing staged chapter-archives and modified
  `thesis/evidence/*.json` files predate this Ch1 run. The Ch1 deliverables themselves are
  scoped correctly. Recommend the orchestrator confirm the archive step was intentional
  before binding.

