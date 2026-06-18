# Ch1 Introduction — Section Writer Run Summary

**Agent:** VOYO Thesis Section Writer (Ch1 Introduction dossier)
**Date:** 2026-06-17
**Section covered:** Ch1 — Introduction (problem statement; hybrid-deterministic thesis
sentence; contributions list; "LLM-alone cannot plan" motivation).

## Deliverables (4 files, all under `thesis/ch1-introduction/`)

| File | Purpose | Size |
|---|---|---|
| `dossier.md` | Cited argument outline (claim → citation id → locator); thesis sentence at top | ~15.8 KB |
| `evidence-packet.md` | Verbatim quotes (N1 Q1/Q3/Q4/Q5/Q7; 01 Q1/Q3/Q5) + 310/58/76/97 numbers + thesis sentence | ~10.3 KB |
| `figures-spec.md` | Table 1.1 (contributions, producible now) + 2 forward-pointer figures (Ch3-owned, optional) | ~3.8 KB |
| `citations-used.md` | Citation ids used, by tier; anti-fabrication audit | ~4.3 KB |

## Citations used (by tier)

- **Tier A (load-bearing; grounds core claims):** **N1 ItiNera** (EMNLP 2024 Industry +
  KDD UrbComp 2024 Best Paper) — locators Q1,Q3,Q4,Q5,Q7; **01 Compound AI Systems** (BAIR
  Blog) — locators Q1,Q3,Q5. Both resolve in `INDEX.md`. **This satisfies criteria §4 Ch1 row
  (required = 01 + N1).**
- **Tier C (named by role only, never as a paper):** S-VALHALLA, S-VROOM, S-OSRM — appear in
  the thesis sentence's trust boundary; their *academic* citations (N4 PyVRP, OSRM-PAPER) are
  explicitly deferred to Ch2/Ch3 to avoid widening Ch1 scope.
- **Tier D (preprint-only):** N2 TRIP-PAL, N3 TravelAgent — **OMITTED** per criteria §4
  (prefer N1 for the "LLM-alone cannot plan" point).

## How the four Ch1 deliverables were met

- **(a) Problem statement** — dossier P3: ItiNera Q3 verbatim ("Pure LLMs cannot refer to
  specific POI lists, resulting in outdated or hallucinated POIs… LLMs lack the optimization
  capabilities required for planning tasks").
- **(b) Hybrid-deterministic thesis sentence (verbatim)** — dossier H1 quotes criteria §1's
  spine sentence verbatim, tied to N1 Q3.
- **(c) Contributions list** — dossier C1 (hybrid architecture; 01 + N1), C2 (310-POI verified
  Egyptian substrate + dual pricing; criteria §4 + `ticket_prices_upsert.sql` = 58 dual-price
  rows verified by line count), C3 (deterministic feasibility layer; criteria §1 + N1 Q3).
- **(d) "LLM-alone cannot plan" motivation (quantified)** — dossier M1–M4: N1 Q3 verbatim
  (the criteria "Excellence" quote) + N1 Q5 ablation (Average Margin 86.0 → 242.8, ~3×
  collapse), clearly attributed to ItiNera not VOYO. VOYO's own ablation number is PENDING the
  eval harness (Ch4 keystone) and is never stated in Ch1.

## Claims I could NOT ground (escalation)

- **None.** Every Ch1 claim traces to 01, N1, criteria §1/§4, or the verified
  `ticket_prices_upsert.sql` provenance. The N1 Q3 motivation quote and the 86.0→242.8 ablation
  number are both verbatim from the verified quote bank — the criteria "quantified motivation"
  Excellence bar is met.

## Pending metrics labelled (none fabricated)

- **VOYO's own ablation feasibility/violation/Avg-Margin numbers** — labelled PENDING the
  eval harness (Ch4 keystone). Only ItiNera's borrowed 86.0→242.8 is stated, and it is
  explicitly attributed to ItiNera, not VOYO.
- **`evidence/05-db-completeness.json` POI count** — the file reports the STALE 255
  (pre-rebuild snapshot, criteria §5 ⚠️ regenerate); Ch1 uses **310** in all prose and flags
  255 as STALE for Ch6 regeneration. Never fabricated.

## Anti-fabrication compliance (criteria §7)

- ✅ Reflexion "+22% ALFWorld" FABRICATED stat appears ONLY inside explicit "never cited"
  warnings (4 occurrences, all in warning context).
- ✅ POI count = 310 as the positive claim (27×); 255 only as flagged STALE (14×).
- ✅ No invented paper for VROOM/Valhalla (named by role; "no paper exists" per S-VROOM #735).
- ✅ Tier D not used as core evidence.
- ✅ All citation ids resolve in `INDEX.md`.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Produced exactly the 4 dossier files required (dossier.md, evidence-packet.md, figures-spec.md, citations-used.md) under thesis/ch1-introduction/. Scope held to criteria §4 Ch1 row: required citations = 01 + N1 only; engine academic citations (N4/OSRM-PAPER) explicitly deferred to Ch2/Ch3 to avoid widening scope. No files written outside thesis/ch1-introduction/. No thesis prose written (dossier = outline + evidence, per criteria §6)."
    },
    {
      "id": "criterion-2",
      "status": "satisfied",
      "evidence": "Every claim ends with [citation: <id> → <locator>] resolving in INDEX.md (validated: all of N1/N2/N3/01/S-VROOM/S-VALHALLA/S-OSRM/OSRM-PAPER resolve). Core claims use Tier A (N1 + 01). Verbatim quotes copied from quote banks (N1 Q1/Q3/Q4/Q5/Q7; 01 Q1/Q3/Q5). POI count = 310 everywhere (27×), 255 only as flagged STALE (14×). Reflexion '+22% ALFWorld' appears only in 'never cited' warnings. Tier D (N2/N3) omitted per criteria preference for N1. Dual-price count 58 verified by line count of data/ticket_prices_upsert.sql. VOYO's own ablation number labelled PENDING eval harness, never fabricated."
    }
  ],
  "changedFiles": [
    "thesis/ch1-introduction/dossier.md (new)",
    "thesis/ch1-introduction/evidence-packet.md (new)",
    "thesis/ch1-introduction/figures-spec.md (new)",
    "thesis/ch1-introduction/citations-used.md (new)",
    "thesis/ch1-introduction/_run-summary.md (new)"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "grep -ohE citation ids across dossier + resolve check against INDEX.md",
      "result": "passed",
      "summary": "All citation ids (N1,N2,N3,01,S-VROOM,S-VALHALLA,S-OSRM,OSRM-PAPER) resolve in INDEX.md. Stray number matches (02/04/05/06/10) confirmed as false positives inside URLs/dates/filenames/table cells — none used as Ch1 evidence."
    },
    {
      "command": "grep -rn '22% ALFWorld|+22%' thesis/ch1-introduction/",
      "result": "passed",
      "summary": "Fabricated Reflexion stat appears in 4 places, ALL inside explicit 'FABRICATED / never cited' warning context. No positive citation."
    },
    {
      "command": "grep count of '310' vs '255' in dossier files",
      "result": "passed",
      "summary": "310 appears 27× as the canonical POI count; 255 appears 14× exclusively as a flagged STALE value with regenerate-in-Ch6 instructions. No '255' used as a positive claim."
    },
    {
      "command": "grep -c '^UPDATE pois' data/ticket_prices_upsert.sql",
      "result": "passed",
      "summary": "Exactly 58 dual-price (egyptian+foreigner) UPDATE rows — matches criteria §4 canonical dual-price count = 58. Provenance verified end-to-end."
    },
    {
      "command": "ls thesis/ch1-introduction/",
      "result": "passed",
      "summary": "All 4 required dossier files present (dossier.md, evidence-packet.md, figures-spec.md, citations-used.md)."
    }
  ],
  "validationOutput": [
    "Criteria §4 Ch1 deliverables: (a) problem statement [P3, N1 Q3 verbatim] ✓; (b) hybrid-deterministic thesis sentence verbatim [H1, criteria §1] ✓; (c) contributions list [C1 hybrid arch / C2 310-POI + dual pricing / C3 deterministic feasibility] ✓; (d) LLM-alone-cannot-plan motivation quantified [M1 N1 Q3 verbatim + M2 N1 Q5 ablation 86.0→242.8] ✓.",
    "Required citations 01 + N1 both present and Tier A; core claims all on Tier A.",
    "Tier D omitted; Tier C engines named by role only (no invented papers).",
    "Criteria §7 anti-fabrication: all 5 flags green (Reflexion stat, POI 310, no invented paper, N1's number attributed to ItiNera, Tier D not core).",
    "Pending metrics: only VOYO's own ablation (Ch4 keystone) and 05-db-completeness.json regeneration (Ch6) — both labelled PENDING/STALE, never fabricated."
  ],
  "residualRisks": [
    "evidence/05-db-completeness.json still reports total_active_pois:255 (STALE). Ch1 flags it and uses 310 per criteria §4, but the underlying evidence file must be regenerated in Ch6 before the thesis binds — otherwise a reader who opens the file will see 255. Low risk for Ch1 (criteria-mandated number used in prose), but tracked.",
    "01 Compound AI Systems is a BAIR blog post (not peer-reviewed); the dossier pairs every 01-backed claim with the peer-reviewed N1, per the quote-bank accuracy flag. Acceptable for thesis-level motivation but the writer should not lean on 01 alone for any empirical claim.",
    "Figure 1.2 (ItiNera ablation hook) is optional; if included its caption MUST label the 86.0→242.8 bar as ItiNera's result with VOYO's replication PENDING. Risk of misattribution if the writer drops the mandatory labelling."
  ],
  "noStagedFiles": true,
  "notes": "No edits made to src/, flutter_app/, enrich_narratives.py, the DB, criteria.md, INDEX.md, citations/, evidence/, or the archived prior-draft chapters — all read-only reference only. The dossier deliberately does NOT pull N4 (PyVRP) or OSRM-PAPER into Ch1 as evidence, even though they are Tier A, because criteria §4 scopes Ch1's citation set to 01 + N1 and those engines' academic grounding belongs to Ch2.2/Ch2.3/Ch3. Forward-pointers to those chapters are noted but not cited as Ch1 evidence."
}
```
