# §4 Results & Evaluation — Supervisor Gap Report

> **Audited by:** VOYO Thesis Supervisor (external-examiner role).
> **Audited artifact:** `thesis/ch4-results/{dossier.md, evidence-packet.md, figures-spec.md, citations-used.md}`.
> **Contract:** `thesis/criteria/thesis-criteria.md` §2 (tiers), §4 (Ch4 row), §5 (required
> evidence + thresholds), §6 (dossier spec), §7 (no-fabrication).
> **Mode:** Read-only audit — no dossier files were edited; only this review was written.

---

## Verdict

**PASS-WITH-OPTIONAL-FIXES.**

The dossier is sound, well-grounded, scrupulously honest about the measured-vs-pending split,
and meets — and in places exceeds — the Ch4 excellence bar. It commits all six metric-family
thresholds in advance, ties each PENDING metric to a published comparand (ItiNera Avg-Margin
86.0/242.8; PyVRP 0.40% VRPTW gap), and reports **zero** invented numbers for the five
PENDING metrics. Every MEASURED-NOW number (latency, test inventory, A/B correctness,
substrate-integrity) was re-verified against `thesis/evidence/` and matches verbatim.

The single optional fix is a per-line citation-tag gap on S-VALHALLA inside METRIC 2 of
`dossier.md`. Everything else passes cleanly.

---

## Checklist results

### 1. Grounding — PASS (with one optional fix)

Every claim in `dossier.md` ends with a `[citation: <id> → <locator>]` that resolves in
`thesis/citations/INDEX.md`, and every cited quote has a verbatim match in
`evidence-packet.md`. Numbers cite a file in `thesis/evidence/` or a quote bank.

Spot-verified claims that resolve cleanly:
- §4.1.3 (LLM-alone baseline) → N1 → Q3 (INDEX Tier A; locator arXiv:2402.07204 §1 p.1). ✓
- §4.1.4 (Avg-Margin comparand) → N1 → Q5 (Table 2 p.6). ✓
- §4.1.5 (VRPTW formalism + 0.40% gap) → N4 → Q4/Q5/Q6 (§2.2, §6.2, §3). ✓
- §4.2.1 (latency p95 1.662 ms) → `thesis/evidence/02-latency.json::benchmarks.scoring_200_pois`. ✓
- §4.2.2 (99/99 tests, 8.53 s) → `thesis/evidence/01-test-results.json::core_suite`. ✓
- §4.2.3 (0.64/0.627 A/B scores; Δ=0.135; 2 vs 14 vehicles) →
  `thesis/evidence/03-ab-correctness.json::per_test.*`. ✓
- §4.3.2 (METRIC 2 infra) → OSRM-PAPER → Q1/Q3 + N4 → Q4 + S-VROOM → README. ✓
- §4.5.3 (forward-compatible comparand) → N1 → Q5, N4 → Q5. ✓

**Optional fix (not blocking):** `dossier.md` §4.3.2 (METRIC 2) prose says
"inter-POI travel times respecting the **OSRM/Valhalla**-computed travel-time matrix" (dossier.md,
METRIC 2 definition paragraph), but the citation block beneath lists OSRM-PAPER + S-OSRM and
**omits** a `[citation: S-VALHALLA → locator]` tag for Valhalla. The citation IS pre-declared
in `citations-used.md` ("Routing/isochrone substrate referenced alongside OSRM in METRIC 2"),
but the inline tag is missing. Per criteria §6 rule 1 ("No claim without a citation id that
resolves in `INDEX.md`"), add one line:

> `- *Citation (matrix infra, Valhalla):* [citation: S-VALHALLA → https://valhalla.github.io/valhalla/api/isochrone/api-reference/] (Tier C; software).`

### 2. Tier discipline — PASS

- **Core eval-design claims all trace to ≥1 Tier-A source.** §4.1.3/4.1.4/4.5.1 → **N1 ItiNera**
  (motivation + Avg-Margin comparand); §4.1.5/METRIC 2 → **N4 PyVRP** (VRPTW formalism +
  optimality reference + honest VROOM-vs-SOTA framing); METRIC 2 infra → **OSRM-PAPER**
  (matrix/shortest-path academic basis). Meets criteria §2 "hard rule."
- **N5 AgentTravel (Tier B) used only as eval-design comparand** (KnowEval/TripEval template) —
  never carries an architecture claim. Labelled as workshop in §4.1.1, §4.1.2 (incl. an explicit
  "Honesty flag for the writer"), `citations-used.md` (with ⚠️), `evidence-packet.md` B1
  (honesty flag), and the §4 summary "How the writer should cite" (criteria §2 N5 row satisfied).
  *Note:* the per-citation parentheticals in METRIC 1, 3, 6 say "(Tier B)" without repeating
  the word "workshop" — but the writer-facing instruction to label N5 as "NORA / CEUR workshop
  paper" is unambiguous and is repeated in five places. Acceptable.
- **Tier C cited as software, never as paper.** S-VROOM README + Issue #735 ("No, there is no
  paper associated with the project"); S-OSRM README; S-VALHALLA docs. No VROOM paper
  invented. Criteria §2 Tier C and §7 (no-fabrication) satisfied.
- **Tier D NOT used.** `citations-used.md` explicitly states N2 (TRIP-PAL) and N3 (TravelAgent)
  are deliberately omitted. ✓

### 3. Verbatim integrity — PASS

Every quote in `evidence-packet.md` was re-checked against the corresponding `quotes.md` bank:

| Quote | Dossier | Bank | Match |
|---|---|---|---|
| N1 Q3 motivation | A1 | `itinera/quotes.md` Q3 | verbatim ✓ |
| N1 Q5 Table 2 row (86.0/242.8) | A1 | `itinera/quotes.md` Q5 | verbatim ✓ |
| N4 Q4 VRPTW def | A2 | `pyvrp/quotes.md` Q4 | verbatim ✓ |
| N4 Q5 0.40% gap + 27/300 | A2 | `pyvrp/quotes.md` Q5 | verbatim ✓ |
| N4 Q6 VROOM-not-SOTA | A2 | `pyvrp/quotes.md` Q6 | verbatim w/ honest `[...]` trunc ✓ |
| OSRM-PAPER Q1 abstract | A3 | `osrm/quotes.md` Q1 | verbatim ✓ |
| N5 Q2/Q4/Q5/Q7 | B1 | `agenttravel/quotes.md` | verbatim ✓ |
| S-VROOM README + Issue #735 | C1 | `software/vroom.md` | verbatim ✓ |
| S-OSRM README CH/MLD | C2 | `osrm/quotes.md` Q2-supporting | verbatim ✓ |

Critically, the OSRM-PAPER is **FULL-TEXT VERIFIED** (per `osrm/quotes.md` header +
`INDEX.md` 2026-06-17 update), so quoting its abstract/body is admissible — no UNVERIFIED or
fetch-pending content is written about. Criteria §7 item 1 ("Unreachable content … nothing is
written about it") respected.

### 4. Numbers — PASS

- **POI count = 310 everywhere canonical.** The dossier uses **310** as the canonical count in
  every headline, the §4.4 table, and the figures-spec. The only "255" occurrences (5 lines in
  `dossier.md`, plus the figures-spec) are **explicit STALE-flags** that instruct the writer to
  use 310 and to regenerate `05-db-completeness.json` (whose `total_active_pois: 255` field is
  named as STALE). This is exactly the honesty-handling the §4 stale-number sweep requires;
  criteria §4 ("Any 255 in new output = FAIL") is about a draft that uses 255 *as the canonical
  count* — this dossier does the opposite. ✓
- **Dual gov.eg prices = 58; gov.eg descriptions = 76; any-enrichment = 97** — these Ch6
  numbers do not appear in this Ch4 dossier (correctly; they belong to Ch6). No violation
  possible. ✓
- **Every other number traces verbatim to `thesis/evidence/` or a quote bank.** Re-verified
  against the source JSON:
  - Latency 0.7501 / 1.662 / 0.1016 / 0.1944 / 0.0069 / 0.0111 / 0.1048 / 0.2417 / 0.0053 /
    0.0123 → `02-latency.json` (all match). ✓
  - 99 tests, 0 fail, 0 errors, 8.53 s, pytest 9.0.3, Python 3.10.6, 8 collection errors →
    `01-test-results.json`. ✓
  - 0.64 / 0.627 / 0.135 / 0.0 / 30→22/45 / 45→33/67 / 60→45/90 / 2-vs-14 vehicles / 20-vs-20
    jobs → `03-ab-correctness.json`. ✓
  - 42 generated / 57 grounded / "135%" / model `llama-3.3-70b-versatile` →
    `narrative_sources.json` (correctly tagged as a pre-enrich probe, NOT coverage). ✓
  - 208/255 imagery, 0 duplicates, famous-six review counts (31657 / 30583 / 25886 / 22930 /
    64632 / 20755) → `05-db-completeness.json` (labelled pre-rebuild). ✓
  - ItiNera 86.0 / 242.8 / 31.4 / 32.8 → `itinera/quotes.md` Q5. ✓
  - PyVRP 0.40% / 0.46% / 27-of-300 → `pyvrp/quotes.md` Q5. ✓

### 5. Pending vs fabricated — PASS (no-fabrication contract satisfied)

> **Updated 2026-06-20:** the eval harness ran. Metrics 2, 3, and 5 are now **MEASURED**
> with real numbers from `thesis/evidence/07-eval-results.json`. Only Metrics 1, 4, 6 remain
> PENDING — and each still carries its explicit "no number reported" disclosure.

The no-fabrication contract is satisfied across both the PENDING and the newly-MEASURED
columns. The three still-PENDING metrics carry an explicit "*Strategy defined; measurement
PENDING the <reason>.* No number is reported." sentence:

| METRIC | Family | Status | Number source | Invented? |
|---|---|---|---|---|
| 1 | Retrieval P@k/R/nDCG | ⏸ PENDING (needs POI-level labels) | — | None ✓ |
| 2 | Feasibility | ✅ **MEASURED 2026-06-20** | `07-eval-results.json` (91.3% / +35.6 pp) | Verbatim ✓ |
| 3 | Reliability | ✅ **MEASURED 2026-06-20** (proxy) | `07-eval-results.json` (margin 172 vs 434; groundedness 0.919) | Verbatim ✓ |
| 4 | Provenance ≥85% | ⏸ PENDING Windows enrich run | — | None ✓ |
| 5 | Latency | ✅ MEASURED | `02-latency.json` + load test `07-eval-results.json` | Verbatim ✓ |
| 6 | UX e2e Playwright | ⏸ PENDING e2e chain | — | None ✓ |

The §4.4 summary table reproduces the criteria §5 thresholds verbatim (P@5 ≥ 0.7, ≥90%
feasible, <5% violations, ≥85% grounded, p95 < 500 ms, ≥80% e2e). Metrics 2, 3, 5 now carry
real measured numbers pulled verbatim from `07-eval-results.json`; Metrics 1, 4, 6 remain
PENDING with no number.

The trickiest PENDING case (METRIC 4 provenance) is handled honestly: the pre-enrich probe
(42 generated / 57 grounded / "135%") is reported as a *grounding-path probe*, with an
explicit "Honesty flag (critical)" stating the 135% is a pre-enrich artifact and **NOT** the
coverage headline. No invented ≥85% number appears anywhere. Criteria §5 "Honesty rule (Ch4)"
and §7 "Never invent a number for a pending metric" both satisfied.

**Newly-MEASURED honesty check (2026-06-20):** every number in §4.6 and evidence-packet §G is
pulled verbatim from `07-eval-results.json` — no rounding, no recomputation, no inflation. The
P07 outlier (0.167 feasibility on both arms) is disclosed as data-substrate evidence, not
hidden. The 2.4% CLEO degradation is disclosed, not omitted. The eval-backend model
(gpt-4o-mini) is disclosed in §3.2.5, not buried.

### 6. Section completeness — PASS (exceeds pass threshold)

Criteria §4 Ch4 row requires "metric definitions + how measured + thresholds" across all six
families (retrieval, feasibility, reliability, provenance, latency, UX); required citations
N5 (eval design) + N1/N4 (baselines); pass threshold "all 6 metric families defined w/
thresholds"; excellence bar "honest 'measured vs pending' table."

- All **6 metric families** defined with definition + threshold + how-measured + exact-data-source
  + status (§4.3.1–§4.3.6 + §4.4 table). ✓
- **N5** cited as the eval-design template (KnowEval/TripEval). ✓
- **N1** cited as the LLM-alone baseline motivation + Avg-Margin comparand. ✓
- **N4** cited as VRPTW formalism + optimality reference. ✓
- **Excellence bar delivered and exceeded:** §4.4 measured-vs-pending table is present, plus a
  §4.5 Discussion that argues the metric split itself reinforces the hybrid-deterministic thesis
  (the measured-now metrics = deterministic-substrate; the PENDING metrics = end-to-end
  hybrid-architecture) — and a §4.5.3 forward-comparability argument committing the comparand
  numbers (ItiNera 86.0; PyVRP 0.40%) in advance.
- **Figures/tables spec'd with real data-source files:** `figures-spec.md` lists Fig. 4.1–4.4
  (retained, with `evidence/` sources) + Fig. 4.5–4.6 (regenerate from 310) + Fig. 4.7–4.11
  (PENDING harness, no figure produced) + Tables 4.0–4.5 each with an explicit data-source
  file. No hand-drawn figure. Criteria §5 ("Figures are derived from `thesis/evidence/`,
  never hand-drawn") satisfied.

### 7. Fabricated-stat guard — PASS

- The Reflexion "+22% ALFWorld" stat does **not appear** as evidence anywhere. The only two
  occurrences of those strings are in the dossier's own no-fabrication checklists
  (`evidence-packet.md` §F and `citations-used.md` pre-flight audit) where they appear in
  **negation** ("is not used", "does not appear"). Criteria §7 satisfied. ✓
- Reflexion is not otherwise invoked in this dossier; the verbatim Reflexion result ("130 out
  of 134 tasks" / "91% HumanEval pass@1") is not relevant to §4 and is correctly absent.

### 8. Scope — PASS

This audit was **read-only**. No edits were made to `dossier.md`, `evidence-packet.md`,
`figures-spec.md`, `citations-used.md`, `thesis/criteria/`, `thesis/citations/INDEX.md`,
`src/`, `flutter_app/`, `enrich_narratives.py`, the DB, or the archived chapters. The only
file written is `thesis/ch4-results/supervisor-review.md` (this file), which is the deliverable
the supervisor role is contracted to produce. ✓

---

## Specific fixes (minimum change to reach PASS, if applied)

None are blocking — the dossier already PASSES. The single optional refinement:

1. **(Optional, grounding nit)** In `dossier.md` §4.3.2 (METRIC 2, feasibility), append one
   line to the citation block so the in-prose mention of "Valhalla" carries an inline tag:
   ```
   - *Citation (matrix infra, Valhalla):* [citation: S-VALHALLA → https://valhalla.github.io/valhalla/api/isochrone/api-reference/] (Tier C; software, never paper).
   ```
   Resolves the only uncited token in the dossier (criteria §6 rule 1). The citation id
   `S-VALHALLA` already resolves in `INDEX.md` Tier C and is already pre-declared in
   `citations-used.md`.

Stylistic note for the writer (not a fix): in `dossier.md` §4.2.1 the headline is phrased
"roughly 300× under the 500 ms p95 threshold," whereas `evidence-packet.md` and
`figures-spec.md` use the more precise "~301×." (500 / 1.662 = 300.84.) Make the three sites
consistent; "~301×" is the more defensible rounding.

---

## Excellence assessment

**Meets — and exceeds — the excellence bar.**

The criteria §4 Ch4 excellence bar is "Honest 'measured vs pending' table." The dossier
delivers that table (§4.4) and adds three genuinely excellent elements that go beyond the bar:

1. **The metric-split-as-thesis-argument** (§4.5.1): the dossier argues — correctly — that the
   metrics measurable *now* (latency, test-pass, A/B divergence, substrate integrity) are
   exactly the deterministic-substrate metrics, while the metrics PENDING the eval harness are
   exactly the hybrid-architecture metrics. This turns the honesty constraint into a structural
   reinforcement of the hybrid-deterministic thesis (criteria §1 spine).
2. **Forward-comparability commitment** (§4.5.3): VOYO's geographic-coherence metric is defined
   identically to ItiNera's published Avg-Margin (86.0 / 242.8), and the feasibility threshold
   is anchored to PyVRP's published 0.40% VRPTW gap as the optimality reference. The comparand
   numbers are committed in advance — when the harness runs, VOYO's number is directly
   benchmarkable against peer-reviewed results.
3. **Tier-A honesty about VROOM** (§4.1.5 + METRIC 2): VOYO claims *feasibility*, not
   optimality, and grounds the distinction in PyVRP's verbatim "unable to compete with
   state-of-the-art" characterisation of VROOM (Q6). This is exactly the non-overclaiming the
   criteria file demands of a VROOM-using system.

The dossier also handles the two known traps cleanly: the Reflexion fabricated stat is absent
(criteria §7), and the 255→310 stale-number sweep is handled by flagging 255 as STALE and
instructing the writer to use 310 everywhere canonical (criteria §4 sweep).

---

## Escalations

None. No citation gap requires librarian attention — every cited id resolves in `INDEX.md`,
every Tier-A source (N1, N4, OSRM-PAPER) is fully verified (OSRM-PAPER moved from
VERIFIED-META to FULL-TEXT VERIFIED on 2026-06-17), and no Tier-D or invented-paper issue
arose. The single optional fix (S-VALHALLA inline tag) is fully resolvable within this
dossier by the writer.
