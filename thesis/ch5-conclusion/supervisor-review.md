# §5 Conclusion — SUPERVISOR GAP REPORT

> **Auditor:** VOYO Thesis Supervisor (external examiner).
> **Dossier audited:** `thesis/ch5-conclusion/` (`dossier.md`, `evidence-packet.md`,
> `figures-spec.md`, `citations-used.md`, `_run-summary.md`).
> **Contract:** `thesis/criteria/thesis-criteria.md` §1–§7, with focus on the Ch5 row of §4
> ("no new claims"; excellence = "limitations tied to held eval harness").
> **Mode:** READ-ONLY audit. The supervisor did not edit the dossier.

---

## VERDICT: **FAIL** (one localized verbatim-integrity violation; trivially fixable)

The dossier is **substantively excellent** — correct hybrid-deterministic framing, impeccable
tier discipline, flawless fabricated-stat guard, correct POI=310, correct borrowed-evidence
framing of ItiNera's 86→242.8, and limitations explicitly tied to the held eval harness
(meets the §4 excellence bar). It FAILS on a **single hard gate**: the METRIC-4 pre-enrich
probe is reported with numbers and a source-kind that **do not match the cited evidence file**.
This is a verbatim-integrity / grounding violation (criteria §6 hard rule #1 + §7
no-fabrication + checklist items #3 and #4). The fix is two lines and the dossier will PASS
immediately on application. No structural rewrite is needed.

---

## CHECKLIST RESULTS (8 items; each cites the criterion id it tests)

### 1. Grounding — every claim has a resolvable `[citation: <id> → <locator>]` + matching evidence-packet entry
**PASS (with one localized exception, folded into item #3 below).** 53 `[citation:` markers in
`dossier.md`; every academic claim traces to N1 / N4 / OSRM-PAPER / N5 / S-VROOM / S-OSRM /
S-VALHALLA, all of which resolve in `thesis/citations/INDEX.md` (verified 2 hits each). The
criteria-file pointers (e.g. `[citation: criteria §4 → thesis-criteria.md §4]`) for the
thesis-sentence restatement and the 310/58/76/97 canonical numbers are **admissible for Ch5
specifically** because (a) criteria §4 Ch5 row says "(no new claims)" and (b) every such
pointer is paired with its underlying academic citation (e.g. 5.1.2 pairs criteria §1 with
N1 Q3; 5.1.7 pairs criteria §4 with N1 Q3). The measured-now numbers all trace to real
`thesis/evidence/` files (latency 0.7501/1.662 ms ← `02-latency.json`; 99/99 tests ←
`01-test-results.json`; 0 divergences ← `03-ab-correctness.json`; 310 ← criteria §4 with
`05-db-completeness.json` flagged stale at 255). **Criteria refs:** §6 hard rule #1; §4 Ch5 row.

### 2. Tier discipline — core claims trace to Tier A; Tier C never as paper; Tier D never core
**PASS.**
- Every restated CORE contribution claim (5.1.2, 5.1.3, 5.1.4, 5.1.5-algorithm, 5.1.6,
  5.2.3, 5.3.1, 5.3.2, 5.3.5) traces to ≥1 Tier-A source: N1 ItiNera, N4 PyVRP, or
  OSRM-PAPER. **Criteria ref:** §2 "Hard rule."
- Tier C (S-VROOM, S-OSRM, S-VALHALLA) is cited **as software** in every occurrence; the
  S-VROOM "no paper exists" confirmation (Issue #735, jcoupey 2022-07-07, verbatim in
  evidence-packet §B) defends against inventing a VROOM paper. **Criteria ref:** §2 Tier C;
  §7 "No paper is invented for VROOM."
- **Tier D (N2 TRIP-PAL, N3 TravelAgent) is NOT USED.** Grep for `[citation: N2` / `[citation: N3`
  in `dossier.md` + `evidence-packet.md` returns nothing; N2/N3 appear only in the explicit
  "NONE USED" disclaimer in `citations-used.md`. **Criteria ref:** §2 Tier D.
- **N5 AgentTravel is labelled "NORA / CEUR workshop paper" on every use** (5.2.2-METRIC-1,
  METRIC-3, METRIC-6, 5.3.2; evidence-packet §C header; citations-used.md Tier-B table) and is
  used **only** as the eval-design comparand, never as architecture precedent.
  **Criteria ref:** §2 Tier B; §3 (N5 "label as workshop paper").

### 3. Verbatim integrity — quotes match the quote banks; nothing written about UNVERIFIED content
**FAIL (localized).** The Tier-A quote reproductions (N1 Q1/Q3/Q4/Q5; N4 Q1/Q4/Q5/Q6;
OSRM-PAPER Q1/Q5/Q6) are **verbatim-faithful** to `thesis/citations/new-route-opt/*/quotes.md`
(checked word-for-word: the "86.0 → 242.8" ablation row, the "hundred microseconds" CH quote,
the "routing is not a bottleneck anymore" quote, the "lack the optimization capabilities"
motivation, the VROOM "unable to compete with state-of-the-art" framing — all match). The Tier-C
software text (S-VROOM README + Issue #735; S-OSRM README; S-VALHALLA Isochrone API) is
verbatim-faithful to `thesis/citations/software/*.md`.

**The violation is in the METRIC-4 pre-enrich probe description** — a field read presented as
verbatim-from-source that does not match the source:
- `dossier.md` line 227: *"a pre-enrich probe (2 POIs / 2 grounded / 100% on a tiny probe …)"*
- `dossier.md` line 231: citation locator *"narrative_sources.json generated_count,
  grounded_count, model (pre-enrich probe — flag as such)"*
- `evidence-packet.md` lines 278–280: *"`narrative_sources.json`: `generated_count: 2`,
  `grounded_count: 2`, `grounding_rate: "100%"`, `model: "glm-4.7"`, 2 POIs probed (Great
  Sphinx of Giza id 65, Abu Simbel Temples id 82) — both grounded via Wikipedia source URLs."*

The actual file `thesis/evidence/narrative_sources.json` reads:
`generated_count: 3`, `grounded_count: 3`, `grounding_rate: "100%"`, `model: "glm-4.7"`, with
**three** POIs — Great Sphinx of Giza (id 65), Abu Simbel Temples (id 82), **and Luxor Temple
(id 79)** — all grounded via **`egymonuments.gov.eg` official** source URLs (`grounding_kind:
"official"`), **not Wikipedia**.

So the dossier/evidence-packet under-report the probe size (2 vs 3) **and** mis-name the source
kind (Wikipedia vs gov.eg-official). Both are verbatim-integrity errors against the cited
source file. **Criteria refs:** §6 hard rule #1 ("No claim without a citation id that
resolves"); §7 ("Every quote is verbatim with a locator … nothing is invented");
checklist §3.

> Note (NOT a dossier fault): criteria §2's parenthetical that the OSRM-PAPER abstract is
> "verbatim text fetch-pending" is **stale** — `INDEX.md` and the OSRM `quotes.md` both
> confirm **FULL-TEXT VERIFIED 2026-06-17** via the Wayback snapshot of the ACM page and the
> provided 4-page PDF. Quoting the OSRM-PAPER abstract/body in this dossier is therefore
> **admissible**. No dossier action required; flagged under Escalations for the criteria
> maintainer.

### 4. Numbers — POI=310 (never 255); enrichment counts 58/76/97; every number sourced
**PASS on the load-bearing numbers; the METRIC-4 probe count is the same defect as item #3.**
- **POI count = 310 everywhere** (13 hits in `dossier.md`, 8 in `evidence-packet.md`). Every
  `255` occurrence is explicitly contextualized as the **stale pre-refresh snapshot** —
  `dossier.md:292/294` ("107 of 255", "208 of 255") sit inside the §5.2.4(c) bullet that
  immediately states "*(Percentages from the stale 255 snapshot — see Ch6 for the post-refresh
  310-corpus equivalents.)*"; `evidence-packet.md:266/268/272/304/348` are all in stale-snapshot
  or DO-NOT-CITE-checklist context. **No canonical use of 255. Criteria ref:** §4 stale-number
  sweep.
- **Dual gov.eg prices = 58; gov.eg descriptions = 76; any-enrichment = 97** — used verbatim
  in §5.1.7, §5.3.3, evidence-packet §D.2, writer's checklist #2. No other enrichment count
  invented. **Criteria ref:** §4.
- **Measured-now numbers all trace to `thesis/evidence/`:** latency median 0.7501 ms / p95
  1.662 ms ← `02-latency.json:benchmarks.scoring_200_pois`; 13/13 benchmarks ← same file
  (13 entries confirmed); 99 passed / 0 failed / 0 errors ← `01-test-results.json:core_suite`;
  8 collection errors ← same file `whole_tree_collection_errors` (count=8 confirmed); 0 A/B
  divergences ← `03-ab-correctness.json`. **Criteria ref:** §6 hard rule #3.
- The "≈300× under the 500 ms p95 threshold" (dossier §5.2.1) is trivial arithmetic on cited
  numbers (500/1.662 ≈ 300.8) — acceptable, not an inferred measurement. (Optional polish:
  append "(500/1.662)".)
- The METRIC-4 probe count "2" is the same defect as item #3 (should be 3). Criteria ref: §6
  hard rule #3 ("never inferred").

### 5. Pending vs fabricated — PENDING metrics labelled PENDING; no invented number
**PASS.** All five PENDING metric families (METRICS 1 retrieval, 2 feasibility, 3 reliability,
4 provenance, 6 UX) **and** the keystone ablation are explicitly labelled `⏸ PENDING` with the
blocker (eval harness / Windows enrichment run / Groq 100k TPD ceiling / e2e chain wiring).
**No measurement number is reported for any PENDING metric** — only strategy + threshold +
blocker (figures-spec.md F5.1 enforces this: "do NOT invent one when the writer renders this
table"). The **ItiNera 86→242.8 figure is correctly framed as a *borrowed-evidence baseline***
(a published peer-reviewed number), never a VOYO measurement — confirmed by grep: every
occurrence (dossier lines 76, 203, 254–255, 262, 267, 270, 315–316, 322) is paired with
"borrowed" / "ItiNera's" / "published". **Criteria ref:** §5 Honesty rule + Ablation keystone.

### 6. Section completeness — meets criteria §4 Ch5 row; figures/tables spec'd with data source
**PASS (meets the EXCELLENCE bar — see Excellence section).** All three required subsections
present: §5.1 restates the hybrid-deterministic contribution; §5.2 limitations; §5.3 future
work. The §5.2 limitations are **explicitly tied to the held eval harness** — the five PENDING
metric families (retrieval / feasibility / reliability / provenance / UX) **and** the new
keystone ablation (full-hybrid vs LLM-only, PENDING) — which is exactly the §4 Ch5 excellence
criterion. Figures/tables (F5.1 Measured-vs-PENDING table; F5.2 architecture cross-ref; F5.3
ablation keystone chart PENDING; F5.4 latency table) each name a real data-source file
(`criteria §5`, `evidence/02-latency.json`, Ch3 `fig_3_1_architecture`, PENDING eval harness).
**Criteria ref:** §4 Ch5 row; §5.

### 7. Fabricated-stat guard — Reflexion "+22%", Liu "+35%", Pai "0.69" must NOT appear as cited data
**PASS.** Grep for citation ids `05` / `08` / `09` in claim bodies of `dossier.md` and
`evidence-packet.md` returns **nothing** — Reflexion / Liu / Pai are not used in any §5 claim.
The banned strings appear **only** in the inherited anti-fabrication checklists
(`dossier.md` writer's checklist #3/#4/#5; `evidence-packet.md` writer's checklist #2/#3/#4)
where they are framed as **"DO NOT cite"** warnings, never as cited data. The one `0.22%` hit
is PyVRP's legitimate CVRP optimality gap (N4 Q5), verbatim from the quote bank — not the Pai
"0.69" and not a fabricated stat. **Criteria ref:** §7 (Reflexion verbatim = "130 out of 134
tasks" + "91% HumanEval pass@1"; Liu "+35%" not found; Pai "0.69" is discriminant-validity not
structural β).

### 8. Scope — writer touched ONLY `thesis/ch5-conclusion/`
**PASS (with an attribution caveat).** The Ch5 directory contains exactly the 5 expected files
(`dossier.md`, `evidence-packet.md`, `figures-spec.md`, `citations-used.md`, `_run-summary.md`)
— all under `thesis/ch5-conclusion/`. No edits to `src/`, `flutter_app/`,
`enrich_narratives.py`, the DB, `criteria.md`, `INDEX.md`, `citations/`, `references.bib`, or
the archived prior-draft chapters are attributable to this dossier. **Caveat:** the working
tree is pre-dirty (many pre-existing modifications to `docs/`, `src/`, `flutter_app/`, etc.
from prior agent runs), so git attribution cannot independently confirm the writer touched
nothing outside Ch5; the writer's `_run-summary.md` asserts scope discipline and the Ch5
directory is self-contained. **Criteria ref:** §6 hard rule #5.

---

## SPECIFIC FIXES (minimum change to reach PASS)

**Single fix, two file locations** (criteria §6 hard rule #1; §7 verbatim-with-locator;
checklist #3 + #4). After applying, re-run the audit — expected immediate PASS.

1. **`thesis/ch5-conclusion/evidence-packet.md` lines 278–280** — correct the probe count and
   the source kind to match `narrative_sources.json` verbatim:
   - `generated_count: 2` → `generated_count: 3`
   - `grounded_count: 2` → `grounded_count: 3`
   - "2 POIs probed (Great Sphinx of Giza id 65, Abu Simbel Temples id 82)" → "3 POIs probed
     (Great Sphinx of Giza id 65, Abu Simbel Temples id 82, **Luxor Temple id 79**)"
   - "both grounded via Wikipedia source URLs" → "all three grounded via **egymonuments.gov.eg
     official** source URLs (`grounding_kind: "official"`)"

2. **`thesis/ch5-conclusion/dossier.md` line 227** — correct the parenthetical to match:
   "(2 POIs / 2 grounded / 100% …)" → "(3 POIs / 3 grounded / 100% on a tiny probe with model
   `glm-4.7`)". (Line 231's locator `generated_count, grounded_count, model` remains correct —
   it is field-name-only.)

> The framing ("pre-enrich probe on a tiny sample, NOT the post-enrich coverage metric;
> METRIC 4 ≥ 85% is PENDING the Windows enrichment run") is **already correct** and needs no
> change — only the verbatim count and source-kind fields are wrong.

**Optional polish (NOT required for PASS):**
- `dossier.md` §5.2.1: append "(500/1.662)" to "≈300× under the 500 ms p95 threshold" to make
  the trivial arithmetic explicit.
- `evidence-packet.md` could note the criteria §2 OSRM-PAPER parenthetical is now superseded by
  the FULL-TEXT VERIFIED status (cosmetic; not a dossier fault).

---

## EXCELLENCE ASSESSMENT

**Meets — and in places exceeds — the §4 Ch5 excellence bar** ("limitations tied to held eval
harness"). Specifically:
- §5.2.2 enumerates all five PENDING metric families with strategy + pre-committed threshold +
  blocker, and **names the failure each metric is designed to catch** (e.g. METRIC 1 catches
  ItiNera-Q3 "outdated or hallucinated POIs"; METRIC 3 is motivated by N5-Q2 spatial-reasoning
  failure) — this is examiner-grade honesty, not boilerplate.
- §5.2.3 elevates the keystone ablation (full-hybrid vs LLM-only) to **the principal
  limitation**, framing it verbatim as criteria §5 does ("the difference between engineering-
  grade and research-grade") and tying the LLM-only-collapse target (≤50%) to ItiNera's 86→242.8
  magnitude. This is exactly the framing an external examiner wants.
- §5.3.1 leads future work with the keystone ablation and pre-commits thresholds/comparands —
  no post-hoc tuning escape hatch.
- The "measured-now vs PENDING" split is itself argued as **reinforcing the thesis** (the
  measurable metrics are the deterministic-substrate metrics; the gated metrics are the
  end-to-end hybrid-architecture metrics) — a sharp rhetorical move.
- The cross-reference audit trail in `citations-used.md` (16-row "Internal cross-references"
  table tracing every §5 claim to its Ch1–Ch4 origin) makes the "no new claims" contract
  auditable in one place.

On application of the single fix above, this dossier would be a clean **PASS at excellence
level**, not merely at pass threshold.

---

## ESCALATIONS

1. **Criteria-file inconsistency (not a dossier fault):** `thesis-criteria.md` §2 OSRM-PAPER
   row still says the abstract is "verbatim text fetch-pending," but `INDEX.md` and
   `thesis/citations/new-route-opt/osrm/quotes.md` both record **FULL-TEXT VERIFIED
   2026-06-17** (Wayback snapshot of the ACM page + the provided 4-page PDF, with Q5/Q6/Q7 body
   quotes). Recommend the criteria maintainer update the §2 parenthetical so future writers
   are not wrongly told the OSRM-PAPER abstract is off-limits. **No Ch5 action required** — the
   dossier quotes only the now-verified text.
2. **Ch6-owned blocker (acknowledged, not Ch5's to fix):** `thesis/evidence/05-db-completeness.json`
   still reports `total_active_pois: 255`. Ch5 correctly flags this everywhere and uses 310 in
   prose; the refresh is a Ch6 task per criteria §5. Supervisor confirms Ch5 handles it
   correctly.
3. **Keystone-ablation blocker (acknowledged):** the §5.2.3/§5.3.1 keystone ablation cannot be
   filled from existing evidence — it requires running the eval harness in ablation mode. Ch5
   discloses this honestly as the principal limitation and top future-work item; criteria §5
   itself labels it "BLOCKING: the single most defensible chart." No Ch5 action possible.
4. **No librarian escalation needed** — all seven citation ids resolve in INDEX.md and all
   Tier-A quote reproductions are verbatim-faithful. The single FAIL is a local evidence-file
   read error, not a citation-gap.

