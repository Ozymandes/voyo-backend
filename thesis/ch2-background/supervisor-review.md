# Supervisor Review — §2.2 / §2.3 Background & Literature-Review Dossier

> **Auditor:** VOYO Thesis Supervisor (external-examiner persona).
> **Dossier audited:** `thesis/ch2-background/{dossier.md, evidence-packet.md, figures-spec.md, citations-used.md, _run-summary.md}`.
> **Contract:** `thesis/criteria/thesis-criteria.md` (criteria §1–§7, Audit checklist §8 items).
> **Date:** 2026-06-17.
> **Mode:** READ-ONLY audit. No edits to the dossier.

---

## Verdict: **PASS**

The dossier is sound on every gate. It clears the **excellence bar** for the Ch2 row of
criteria §4 (4 themes + research-gap statement with explicit VOYO-vs-ItiNera delta + ≥1 Tier-A
in both T2 and §2.3). No FAIL-grade violations; no escalations. The few notes below are
optional polish, not blockers.

---

## Checklist results (criteria "Audit checklist", 8 items)

### 1. Grounding — **PASS** (criteria §6 hard rule 1)

Every claim in `dossier.md` carries a `[citation: <id → <locator>]` that resolves in
`thesis/citations/INDEX.md` (24 targets; all present) **and** has a matching verbatim entry
in `evidence-packet.md`. Spot-verified all Tier-A load-bearing chains:

- T2-2 / T3-1 / T3-2 / §2.3-1 / GAP-4 → `N1 → Q3` ("LLMs lack the optimization capabilities
  required for planning tasks"): verbatim match vs `citations/new-route-opt/itinera/quotes.md`
  Q3 ✓.
- T2-4 / §2.3-1 ablation → `N1 → Q5` (Average Margin 86.0 → 242.8): verbatim match incl. the
  table-row numbers ✓.
- §2.3-2 / GAP-2 → `N4 → Q4` (VRPTW service/earliest/latest arrival definition): verbatim
  match ✓.
- §2.3-3 → `N4 → Q1,Q2,Q3,Q5` (HGS = genetic+local; 80–90% runtime in C++; 0.22% / 0.40% gaps;
  1st DIMACS 2021): verbatim match ✓.
- §2.3-5 → `OSRM-PAPER → Q5,Q6,Q7`: verbatim match ✓ (see item 3 on the FULL-TEXT status).
- T2-6 / T3-3 → `04 → Q1,Q2` (GPT-4 0.6%; "struggle to stay on task"): resolves ✓.
- T4-1 → `08 → Q5` (accessibility path coefficient 0.285): verbatim match ✓.
- T4-2 → `09 → Q6` (+22% task completion): verbatim match ✓.
- T2-9 → `N2 → Q6` ("14 valid plans out of the 100 tasks"), `N3 → Q1,Q6` (four modules,
  9.56/8.87/8.44 vs 8.16/6.25/4.31): verbatim match ✓.
- §2.3-8 → `N5 → Q5` (KnowEval/TripEval): resolves ✓.

No uncited or un-resolvable claim found. 58 `[citation: …]` tags all resolve.

### 2. Tier discipline — **PASS** (criteria §2 + §6 hard rule 2)

- **Every core contribution claim traces to ≥1 Tier-A source:**
  - T2-1..T2-5 (the crux theme) → **N1 ItiNera** (Tier A) as PRIMARY ✓.
  - §2.3-1 → N1 (Tier A); §2.3-2..§2.3-3 → **N4 PyVRP** (Tier A); §2.3-5 → **OSRM-PAPER**
    (Tier A); §2.3-7 → N1 (Tier A) ✓.
  - GAP-1..GAP-5 (synthesized closing claim) → N1 + N4 (Tier A) for the structural deltas ✓.
- **Tier-D hygiene is exemplary:** N2 TRIP-PAL and N3 TravelAgent appear ONLY as
  explicitly-labelled `"arXiv preprint, not peer-reviewed"` footnotes (T2-9; GAP-4 footnote
  for N2). Neither carries a core contribution claim. N3 correctly cited as **four modules**
  (Q1 verbatim), not five. N2's solver correctly flagged as PDDL/Fast Downward, **distinct**
  from VROOM's VRP family (no conflation) ✓.
- **No VROOM paper invented:** §2.3-4 cites `S-VROOM → Issue #735` ("No, there is no paper
  associated with the project") and cross-cites `N4 → Q6` for the *only* academically-sourced
  sentence about VROOM ✓.
- **OSRM split correctly:** OSRM-PAPER (Tier A, the CH algorithm) ≠ S-OSRM (Tier C, the
  running `/table` tool) — both used, never conflated ✓.
- **N5 AgentTravel labelled "NORA / CEUR workshop"** at every appearance (T2-7, §2.3-8,
  Table 2.4); used only as eval-design comparand, never as architecture precedent ✓.

### 3. Verbatim integrity — **PASS** (criteria §6 hard rule 1 + §7)

- All Tier-A quotes spot-checked against their `quotes.md` banks match verbatim (no
  paraphrase-inside-quotes; ellipses are explicit `[...]`).
- **OSRM-PAPER body quotes (Q5/Q6/Q7) are now legitimately quotable.** The criteria file
  §2/§7 originally flagged the OSRM abstract as "verbatim text fetch-pending." The
  `citations/new-route-opt/osrm/quotes.md` bank was upgraded on 2026-06-17 to
  **"STATUS: FULL-TEXT VERIFIED"** with the 4-page body PDF on record
  (`thesis/citations/pdfs/OSRM-PAPER_luxen2011.pdf`). The dossier cites Q5 ("a hundred
  microseconds"), Q6 ("routing is not a bottleneck anymore"), and Q7 ("Dijkstra's seminal
  algorithm does not scale") — all verbatim, all locatable in the bank. **No content was
  written about an unverified source.**
- N4 Q1 in `evidence-packet.md` uses an honest `[...]` ellipsis (omits "but can be easily
  extended... PyVRP combines the flexibility of Python with the performance of C++") — this
  is transparent abridgement, not paraphrase ✓.

### 4. Numbers — **PASS** (criteria §4 stale-number sweep)

- **POI count = 310** everywhere it appears as a positive claim (dossier §2.2.D positioning,
  GAP-1, GAP-5; figures-spec.md; citations-used.md). The stale **"255"** appears ONLY inside
  explicit stale-flag warnings (e.g., GAP-1: "⚠️ evidence/05-db-completeness.json still
  reports the stale 255 count and must be regenerated") ✓ — never as a positive claim.
- **Dual gov.eg prices = 58** (GAP-3, GAP-5, figures-spec.md "Pending items") ✓.
- **Authoritative gov.eg descriptions = 76** (figures-spec.md) ✓.
- **Any-enrichment = 97** (figures-spec.md) ✓.
- ItiNera dataset **"1233 top-rated urban itineraries and 7578 POIs"** matches N1 Q7 verbatim ✓.
- ItiNera ablation **"86.0 → 242.8"** matches N1 Q5 verbatim ✓.
- PyVRP benchmark gaps **0.22% / 0.40%** match N4 Q5 verbatim ✓.
- Gorilla head-to-head **59.13% / 38.70%** accuracy, **6.98% / 36.55%** hallucination match
  N4 quotes.md Q4 verbatim ✓.
- Toolformer per-benchmark gains (SQuAD 17.8→33.8; ASDiv 7.5→40.4; Dateset 3.9→27.3) match
  07 quotes.md Tables 3/4/7 ✓.
- Pang N=735, Pai N=527, Christina N=204, AlSaeed SUS=87.75 / 5.4s / N=10, Onuiri 50
  locations — all verbatim ✓.

No inferred numbers; every numeric claim traces to a quote bank or a criteria-mandated count.

### 5. Pending vs fabricated — **PASS** (criteria §5 honesty rule)

- All §4 eval metrics (retrieval P@k/R/nDCG, feasibility, reliability, provenance, UX e2e)
  are **deferred entirely to Ch4** — Ch2 introduces none as results, only the *strategy*
  via N5 Q5 (KnowEval/TripEval template) ✓.
- `evidence/05-db-completeness.json` regeneration explicitly flagged PENDING in
  `figures-spec.md` and `_run-summary.md` ✓.
- Dual-price/description/enrichment counts (58/76/97) cited as **criteria-mandated**, not
  as provenance-run results ✓.
- **No invented number for any pending metric.**

### 6. Section completeness — **PASS** (criteria §4 Ch2 row; criteria §3)

- **4 themes present**, each closed by an explicit "VOYO positioning" sentence:
  §2.2.A T1 ✓; §2.2.B T2 ✓ (crux); §2.2.C T3 ✓; §2.2.D T4 ✓.
- **§2.3 route-opt crux** present with all 8 sub-claims (§2.3-1..§2.3-8) ✓.
- **Research-gap statement present and explicit** (GAP-1..GAP-5), including the synthesized
  GAP-5 closing sentence that matches criteria §3's verbatim-derivable template
  ("No prior system combines (i) an LLM intent layer … with (ii) VRPTW-grade deterministic
  optimization … over (iii) a verified, region-balanced Egyptian POI substrate (310 POIs)
  with (iv) dual Egyptian/foreigner pricing (58 POIs).") ✓.
- **Required citation set fully present:** T1:01–07 ✓; T2:N1 ✓; T3:N1,04 ✓; T4:08–15 ✓;
  §2.3:N4, OSRM-PAPER, S-VROOM, S-VALHALLA, S-OSRM, N5 ✓.
- **Tables/Figures spec'd with real data-source files:** Tables 2.1–2.4 sourced from
  verified `quotes.md` (literature synthesis, not benchmark runs); new conceptual Figure 2.1
  (research-gap map) sourced from the GAP-1..GAP-5 statement + per-system quotes ✓.

### 7. Fabricated-stat guard — **PASS** (criteria §7)

| Stat | Audit result |
|---|---|
| Reflexion **"+22% ALFWorld"** | **ABSENT** as a positive claim. Appears ONLY inside "DO NOT cite / NEVER" warnings (T1-5, T3-4, evidence-packet, citations-used.md, _run-summary.md). Verified figures cited instead: **"130 out of 134 tasks"** + **"91% pass@1 HumanEval"** (matches 05 quotes.md Q1, Q2 verbatim) ✓. |
| Liu **"+35% feature discovery"** | **ABSENT** as a positive claim. Appears ONLY in "DO NOT cite / NEVER" warnings. Verified figure cited instead: **"+22% task completion"** (matches 09 quotes.md Q6 verbatim) ✓. |
| Pai **"0.69" as structural β** | **ABSENT** as a positive claim. Appears ONLY in "DO NOT cite as β / discriminant-validity" warnings. Verified figure cited instead: **accessibility path coefficient 0.285** (matches 08 quotes.md Q5 verbatim) ✓. |
| Pang **"β=0.326"** | **ABSENT** as a positive claim. Appears ONLY in "do not cite β=0.326" warnings. Dossier cites N=735 + qualitative four-motivation finding + privacy-negative (matches 11 quotes.md Q1–Q4) ✓. |
| TravelAgent **"5 modules"** | **ABSENT.** Cited correctly as **four modules** (matches N3 quotes.md Q1 verbatim) ✓. |
| VROOM **paper** | **NONE invented.** S-VROOM cited as software + cross-cited via N4 Q6 ✓. |
| POI count **"255"** | **ABSENT** as positive claim; only in stale-flag warnings ✓. |
| Tsaih DOI | **10.1145/3568026** (NOT the wrong 10.1145/3579366) ✓. |
| Swanepoel degree | **Master of Engineering** (NOT Ph.D.); handle 10019.1/125975; Dec 2022 ✓. |

### 8. Scope — **PASS** (criteria §6 hard rule 5)

- All 5 deliverables (`dossier.md`, `evidence-packet.md`, `figures-spec.md`,
  `citations-used.md`, `_run-summary.md`) live **under `thesis/ch2-background/` only**; the
  directory is untracked (new) in git, dated 2026-06-17 12:16–12:22 ✓.
- **No edits** to `src/`, `flutter_app/`, `enrich_narratives.py`, the DB, criteria.md,
  INDEX.md, citations/, evidence/, or the archived prior draft (`thesis/_archive_prior_draft/`)
  from this writer ✓ (the broader modified-files list in `git status` predates the dossier
  task — it reflects the orchestrator's prior restructuring, not the §2.2 writer's work).
- `_run-summary.md` self-declares: "The dossier is read-only outside `thesis/ch2-background/`."
  ✓

---

## Specific fixes required to reach PASS: **NONE.**

No FAIL-grade findings. No minimum-change fix list is needed.

---

## Excellence assessment — **Meets the excellence bar** (criteria §4 Ch2 "Excellence" column)

The dossier clears the pass threshold **and** the excellence bar:

- **Explicit VOYO-vs-ItiNera delta** is delivered in detail (GAP-1 substrate, GAP-2
  optimizer-class TSP→VRPTW, GAP-3 dual-pricing, GAP-4 reliability, GAP-5 synthesized) —
  exactly what criteria §4 Ch2 "Excellence" asks for.
- **Tier-A spine is symmetric with the thesis argument:** the crux theme (T2) and the
  technical anchor (§2.3) both rest on N1 + N4 + OSRM-PAPER — matching criteria §2's
  admissibility rule for core contribution claims.
- **Self-discipline is exemplary:** the dossier ships a "Writer's anti-fabrication checklist"
  and a tier-discipline audit table that the supervisor can independently re-verify (and I did).
- **Honest framing throughout:** VROOM is "fast and practical but not SOTA" (cross-cited
  N4 Q6); OSRM matrices are "fastest-route distance, not straight-line"; Tsaih's seven-layer
  model is cited as "consistent with / informed by" rather than prescriptive; N2/N3 are
  footnoted as non-peer-reviewed preprints.

**Optional polish (non-blocking):**

1. **OSRM-PAPER Q2/Q3 under-used.** The CH-lineage References entry (Q2 = Geisberger et al.
   2008) and the OSM-data-pipeline sub-claim (Q3) are in the quotes bank but barely cited.
   The writer could add a one-line Q2 cross-cite in §2.3-5 to anchor the CH *algorithm*
   attribution to Geisberger et al. (cited *inside* OSRM-PAPER) rather than only to Luxen &
   Vetter. Not required; the current §2.3-5 is already adequate.
2. **N4 Q8 (BibTeX provenance)** is in `evidence-packet.md` but unused in claims — harmless;
   it documents the INFORMS JoC companion DOI. Fine to leave.
3. **One residual queued for Ch6** (correctly flagged, not Ch2's blocker):
   `evidence/05-db-completeness.json` must be regenerated on the 310-POI DB before Ch6 closes.
   Ch2 handles this correctly by citing criteria-mandated 310 and not introducing any
   regional-distribution figure until the regenerate runs.

---

## Escalations: **NONE.**

Every required claim was grounded against a verified quote bank or a criteria-mandated
number. No citation gap requires the librarian. The OSRM-PAPER body-text fetch that criteria
§7 originally marked "pending" has been **resolved upstream** — the quotes.md bank now
carries FULL-TEXT VERIFIED status (2026-06-17), so the dossier's body-level OSRM quotes are
admissible. No further action needed.
