# Ch5 Conclusion Dossier — Run Summary

> **Section covered:** §5 Conclusion (criteria §4 Ch5 row).
> **Outputs written (4 files, all under `thesis/ch5-conclusion/`):**
> - `dossier.md` (29,001 B) — cited argument outline: §5.1 restating the hybrid-deterministic
>   contribution, §5.2 limitations tied to the held eval harness + keystone ablation, §5.3
>   future work.
> - `evidence-packet.md` (21,143 B) — verbatim quotes + numbers with locators (Tier A quotes
>   from N1/N4/OSRM-PAPER; Tier C software text from VROOM/OSRM/Valhalla; Tier B from N5;
>   numbers from `evidence/` JSON files; criteria §1/§4/§5/§7 commitments).
> - `figures-spec.md` (5,952 B) — F5.1 Measured-vs-PENDING table (regenerable now); F5.2
>   architecture cross-ref; F5.3 keystone ablation chart (PENDING); F5.4 latency table.
> - `citations-used.md` (13,210 B) — full tier map + internal cross-reference audit trail to
>   Ch1–Ch4 (Ch5 makes NO new claims per criteria §4).

## Citations used (by tier)

- **Tier A (load-bearing; grounds restated core contribution claims):** N1 ItiNera
  (motivation Q3, closest precedent Q1/Q4, Avg-Margin baseline Q5 — the borrowed-evidence
  baseline for the keystone ablation); N4 PyVRP (VRPTW problem class Q4, optimality reference
  Q1/Q5, honest VROOM-vs-SOTA framing Q6); OSRM-PAPER (matrix/routing algorithm Q1/Q5/Q6).
- **Tier B (supporting; eval-design comparand only; LABELLED as NORA/CEUR workshop paper):**
  N5 AgentTravel (TravelBench two-axis split Q5, spatial-reasoning-failure Q2, e2e surface Q4).
- **Tier C (software; never as paper):** S-VROOM (README + Issue #735 "no paper exists"
  verbatim); S-OSRM (README CH/MLD pipelines); S-VALHALLA (Isochrone API overview).
- **Tier D (preprint-only):** **NONE USED.** N2 TRIP-PAL and N3 TravelAgent deliberately
  omitted; no "unavoidably used" flag required.

## Claims I could NOT ground (escalations to orchestrator)

- **None.** Every claim in §5 traces to an already-cited claim in Ch1–Ch4 (the cross-reference
  audit trail is in `citations-used.md`'s "Internal cross-references" table). Ch5 makes NO
  new claims by design (criteria §4 Ch5 row).

## Pending metrics labelled (no fabricated numbers)

The dossier explicitly labels all five PENDING metric families + the keystone ablation as
PENDING with the blocker; **no number is invented for any of them**. The ItiNera 86→242.8
figure is framed as a *borrowed-evidence baseline* (a published peer-reviewed number), not a
VOYO measurement.

1. METRIC 1 Retrieval (P@5 ≥ 0.7) — ⏸ PENDING eval harness.
2. METRIC 2 Itinerary feasibility (≥ 90%) — ⏸ PENDING eval harness.
3. METRIC 3 Reliability (< 5% violation rate) — ⏸ PENDING eval harness.
4. METRIC 4 Provenance coverage (≥ 85%) — ⏸ PENDING Windows enrichment run; the
   `narrative_sources.json` 2/2/100% probe is explicitly flagged as a pre-enrich probe, not
   the post-enrich coverage metric.
5. METRIC 6 UX e2e (≥ 80%) — ⏸ PENDING eval harness + e2e chain wiring (blocked by Groq
   100k TPD free-tier ceiling).
6. **Ablation keystone** (full-hybrid vs LLM-only; hybrid ≥ 90% feasibility AND LLM-only ≤
   50% target) — ⏸ PENDING eval harness in ablation mode. This is the §5.2.3 main limitation
   and the §5.3.1 top future-work item.

Measured-now numbers used (sourced verbatim from `evidence/`): latency p95 1.662 ms (target
500 ms — PASS); 99/99 tests pass; 0 A/B logic divergences; 13/13 backend benchmarks PASS;
canonical POI count 310.

## Anti-fabrication compliance (criteria §7 + §4 stale-number sweep)

- ✅ POI count = **310** everywhere (13 hits in dossier, 8 in evidence-packet); every **255**
  occurrence is explicitly flagged as the stale pre-refresh snapshot, never as canonical.
- ✅ Dual gov.eg prices = 58; gov.eg descriptions = 76; any-enrichment = 97 (criteria §4) —
  used verbatim in §5.3.3.
- ✅ Reflexion "+22% ALFWorld", Liu "+35% feature discovery", Pai "0.69" structural-β are
  **not cited as data**; they appear ONLY in the anti-fabrication checklist warnings that say
  "DO NOT cite." Reflexion/Liu/Pai (ids 05/08/09) are not used in any §5 claim body (verified
  by grep for `[citation: 05|08|09`).
- ✅ No paper invented for VROOM — S-VROOM Issue #735 "no paper exists" verbatim quote is the
  citation.
- ✅ OSRM is correctly split into OSRM-PAPER (Tier A) + S-OSRM (Tier C) wherever both
  algorithm and running tool are referenced.
- ✅ N5 AgentTravel labelled "NORA / CEUR workshop paper" in every claim that uses it.
- ✅ Tier D (N2/N3) appears only in the "NONE USED" disclaimer — never in a claim body.
- ✅ All seven citation ids used (N1, N4, OSRM-PAPER, N5, S-VROOM, S-VALHALLA, S-OSRM) resolve
  in `thesis/citations/INDEX.md` (2 hits each — table entry + file-map / tally mention).
- ✅ 53 `[citation:` markers in dossier.md — every claim ends with a citation id → locator or
  a criteria-file pointer (criteria pointers used because Ch5 makes no new claims).

## Scope discipline (criterion-1: no scope widening)

- Only the 4 required dossier files written, all under `thesis/ch5-conclusion/`.
- No edits to `src/`, `flutter_app/`, `enrich_narratives.py`, the DB, `criteria.md`,
  `INDEX.md`, `citations/`, `references.bib`, or the archived prior-draft chapters.
- No new thesis prose written (per the dossier spec — output is evidence packet for the human
  writer, not final prose).

## Residual risks (for the orchestrator / supervisor)

1. **`thesis/evidence/05-db-completeness.json` still reports `total_active_pois: 255`** —
   this is a Ch6-owned refresh task per criteria §5; Ch5 flags it in prose but cannot fix it
   (read-only outside `thesis/ch5-conclusion/`). The dossier instructs the writer to use 310
   in prose and label the 255-snapshot counts as pre-refresh.
2. **The keystone ablation is the single biggest open research-grade gap.** Ch5 discloses it
   honestly as the §5.2.3 main limitation and the §5.3.1 top future-work item, but it cannot
   be filled from the existing evidence — it requires running the eval harness in ablation
   mode. This is a known, criteria-acknowledged blocker (criteria §5: "BLOCKING: the single
   most defensible chart").
3. **`narrative_sources.json` shows only a 2-POI pre-enrich probe** (model `glm-4.7`); METRIC
   4's ≥ 85% threshold is PENDING the full Windows enrichment run. The dossier explicitly
   flags the probe as not-the-metric.

## Commands run (validation)

- `ls -la thesis/ch5-conclusion/` → 4 files present, no extras.
- `grep -c "$id" thesis/citations/INDEX.md` for all 7 ids → all resolve (2 hits each).
- `grep -n "N2\|N3" citations-used.md` → only in the "NONE USED" disclaimer.
- `grep -n "255" *.md` → every occurrence contextualized as stale/snapshot, never canonical.
- `grep -c "310"` → 13 in dossier, 8 in evidence-packet (canonical count present).
- `grep -c "22%\|35%\|0\.69"` → only in anti-fabrication warning context (NOT as cited data);
  the one `0.22%` match is PyVRP's legitimate CVRP optimality gap.
- `grep -nE "^# §5\.[123]"` → all three required subsections present.
- `grep -c "\[citation:"` → 53 citation markers in dossier.
- `wc -c` → 69,306 B total across the 4 files.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Only the 4 required dossier files written, all under thesis/ch5-conclusion/ (dossier.md 29001 B, evidence-packet.md 21143 B, figures-spec.md 5952 B, citations-used.md 13210 B). No edits to src/, flutter_app/, enrich_narratives.py, the DB, criteria.md, INDEX.md, citations/, references.bib, or the archived prior-draft chapters. No thesis prose written (dossier = evidence packet per criteria §6)."
    },
    {
      "id": "criterion-2",
      "status": "satisfied",
      "evidence": "Every §5 claim ends with a [citation: <id> -> locator] resolving in INDEX.md (53 citation markers in dossier.md); all 7 ids (N1, N4, OSRM-PAPER, N5, S-VROOM, S-VALHALLA, S-OSRM) verified to resolve in INDEX.md (grep -c returns 2 hits each). POI count = 310 everywhere (13 hits in dossier); every 255 occurrence explicitly flagged as stale pre-refresh snapshot, never canonical. All 5 PENDING metric families + the keystone ablation labelled PENDING with blocker; no number invented (ItiNera 86->242.8 framed as borrowed-evidence baseline, not VOYO measurement). Fabricated/banned stats (Reflexion +22%, Liu +35%, Pai 0.69 structural beta) appear ONLY in anti-fabrication warning context, never as cited data; ids 05/08/09 not used in any claim body. Tier D (N2/N3) appears only in 'NONE USED' disclaimer. N5 AgentTravel labelled 'NORA/CEUR workshop paper' on every use. Ch5 makes NO new claims per criteria §4 (cross-reference audit trail in citations-used.md traces every §5 claim back to its Ch1-Ch4 origin)."
    }
  ],
  "changedFiles": [
    "thesis/ch5-conclusion/dossier.md (new, 29001 B)",
    "thesis/ch5-conclusion/evidence-packet.md (new, 21143 B)",
    "thesis/ch5-conclusion/figures-spec.md (new, 5952 B)",
    "thesis/ch5-conclusion/citations-used.md (new, 13210 B)",
    "thesis/ch5-conclusion/_run-summary.md (new, this file)"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "ls -la thesis/ch5-conclusion/",
      "result": "passed",
      "summary": "4 required dossier files present, no extras."
    },
    {
      "command": "grep -c '$id' thesis/citations/INDEX.md for N1/N4/OSRM-PAPER/N5/S-VROOM/S-VALHALLA/S-OSRM",
      "result": "passed",
      "summary": "All 7 citation ids resolve in INDEX.md (2 hits each)."
    },
    {
      "command": "grep -n 'N2|N3' thesis/ch5-conclusion/citations-used.md",
      "result": "passed",
      "summary": "Tier-D ids appear ONLY in 'NONE USED' disclaimer (lines 37, 121), never in claim bodies."
    },
    {
      "command": "grep -n '255' thesis/ch5-conclusion/*.md",
      "result": "passed",
      "summary": "Every 255 occurrence explicitly contextualized as stale pre-refresh snapshot, never used as canonical count."
    },
    {
      "command": "grep -c '310' dossier.md evidence-packet.md",
      "result": "passed",
      "summary": "Canonical POI count 310 present (13 hits in dossier, 8 in evidence-packet)."
    },
    {
      "command": "grep -nE '22%|35%|0\\.69' *.md",
      "result": "passed",
      "summary": "Fabricated/banned stats appear ONLY in anti-fabrication warning context (DO NOT cite); the single 0.22% hit is PyVRP's legitimate CVRP gap."
    },
    {
      "command": "grep -nE '^# §5\\.[123]' dossier.md",
      "result": "passed",
      "summary": "All three required subsections present: §5.1 restating contribution, §5.2 limitations, §5.3 future work."
    },
    {
      "command": "grep -c 'PENDING' dossier.md",
      "result": "passed",
      "summary": "21 PENDING markers — all 5 PENDING metric families + keystone ablation explicitly labelled PENDING with blocker."
    },
    {
      "command": "grep -n 'keystone.*PENDING|Ablation.*PENDING|PENDING the evaluation harness in ablation mode' dossier.md",
      "result": "passed",
      "summary": "Keystone ablation (§5.2.3) explicitly labelled PENDING the eval harness in ablation mode; tied to ItiNera 86->242.8 borrowed-evidence baseline."
    },
    {
      "command": "grep -c '\\[citation:' dossier.md",
      "result": "passed",
      "summary": "53 citation markers — every §5 claim ends with a citation id -> locator or criteria-file pointer."
    },
    {
      "command": "wc -c thesis/ch5-conclusion/*.md",
      "result": "passed",
      "summary": "Total 69306 B across the 4 dossier files."
    }
  ],
  "validationOutput": [
    "All 7 citation ids used resolve in thesis/citations/INDEX.md (Tier A: N1, N4, OSRM-PAPER; Tier B: N5; Tier C: S-VROOM, S-VALHALLA, S-OSRM).",
    "Tier D (N2 TRIP-PAL, N3 TravelAgent) NOT USED — appears only in 'NONE USED' disclaimer.",
    "POI count = 310 canonical everywhere; every 255 occurrence explicitly flagged as stale pre-refresh snapshot.",
    "Dual gov.eg prices = 58, gov.eg descriptions = 76, any-enrichment = 97 (criteria §4) — used verbatim in §5.3.3.",
    "All 5 PENDING metric families (METRICS 1, 2, 3, 4, 6) + keystone ablation report NO NUMBER; strategy + threshold + blocker only.",
    "Fabricated/banned stats (Reflexion +22% ALFWorld, Liu +35% feature discovery, Pai 0.69 structural beta) NOT cited as data; appear only in DO-NOT-CITE warnings. Ids 05/08/09 not used in any §5 claim body.",
    "S-VROOM 'no paper exists' confirmation (Issue #735 verbatim, jcoupey 2022-07-07) is the citation defending against inventing a VROOM paper.",
    "OSRM correctly split into OSRM-PAPER (Tier A algorithm) + S-OSRM (Tier C software) wherever both are referenced.",
    "N5 AgentTravel labelled 'NORA / CEUR workshop paper' on every use.",
    "Ch5 makes NO new claims per criteria §4 — citations-used.md contains a 16-row cross-reference audit trail tracing every §5 claim back to its Ch1-Ch4 origin."
  ],
  "residualRisks": [
    "thesis/evidence/05-db-completeness.json still reports total_active_pois: 255 — Ch6-owned refresh task (criteria §5); Ch5 cannot fix it (read-only outside thesis/ch5-conclusion/) but flags it in prose and uses 310 as canonical.",
    "Keystone ablation (full-hybrid vs LLM-only) cannot be filled from existing evidence — requires running the eval harness in ablation mode. Disclosed honestly as §5.2.3 main limitation + §5.3.1 top future-work item. Criteria-acknowledged blocker (§5 'BLOCKING: the single most defensible chart').",
    "narrative_sources.json shows only a 2-POI pre-enrich probe (model glm-4.7); METRIC 4 >= 85% threshold is PENDING the full Windows enrichment run. Probe explicitly flagged as not-the-metric."
  ],
  "noStagedFiles": true,
  "notes": "Dossier delivered per criteria §4 Ch5 row: (a) §5.1 restates the hybrid-deterministic contribution (LLM intent+personalization <-> deterministic engines for reachability/routing/isochrones/matrices/feasibility/time-window optimization), grounded in N1 Q3 + N4 + OSRM-PAPER + S-VROOM/S-OSRM/S-VALHALLA; (b) §5.2 limitations explicitly tied to the held eval harness — the 5 PENDING metric families (retrieval, feasibility, reliability, provenance, UX) + the new keystone ablation (full-hybrid vs LLM-only, PENDING), with secondary substrate/free-tier limitations restated from Ch3/Ch6; (c) §5.3 future work led by running the keystone ablation + full eval harness (thresholds pre-committed), then substrate extension and free-tier ceiling lifting. NO new claims; every §5 claim traces to Ch1-Ch4. Tier-A load-bearing citations: N1, N4, OSRM-PAPER. Tier B: N5 (labelled workshop). Tier C: S-VROOM, S-OSRM, S-VALHALLA. Tier D: NONE. The supervisor can audit each claim back to its origin chapter via the cross-reference table in citations-used.md."
}
```