# §2.2 / §2.3 Literature-Review Dossier — Run Summary

> **Section covered:** Chapter 2 Background & Literature Review — all four themes (T1, T2, T3,
> T4) + the §2.3 route-optimization crux + the research-gap statement, per the advisor's
> restructured §2.2.
>
> **Argument served:** *VOYO couples an LLM (CLEO — intent + personalization only) to
> deterministic optimization engines (Valhalla/VROOM/OSRM — reachability, routing, isochrones,
> matrices, VRPTW feasibility), because an LLM alone cannot reliably plan.* Every claim in the
> dossier reinforces this hybrid-deterministic thesis.

## Deliverables produced (4 files, all under `thesis/ch2-background/`)

| File | Purpose | Size |
|---|---|---|
| `dossier.md` | Cited argument outline: §2.2.A T1, §2.2.B T2 (crux), §2.2.C T3, §2.2.D T4, §2.3 route-opt crux, Research-Gap statement (GAP-1..GAP-5), writer's anti-fabrication checklist. 58 `[citation: id → locator]` tags. | 29 KB |
| `evidence-packet.md` | All verbatim quotes + numbers the writer copies, grouped by tier (A/B/C/D), with locators. All flagged-for-correction stats explicitly ABSENT. | 31 KB |
| `figures-spec.md` | Spec for Tables 2.1–2.4 (literature-synthesis, from quotes.md) + a new conceptual Figure 2.1 (research-gap map). Pending items labelled. | 10 KB |
| `citations-used.md` | Per-tier list of every citation used; resolves in INDEX.md; tier-discipline audit + anti-fabrication flag table. | 6 KB |

## Citations used (by tier)

- **Tier A (load-bearing): 10** — N1 ItiNera, N4 PyVRP, OSRM-PAPER, and the agentic-architecture
  set 01–07 (Compound AI Systems, Wang Survey, AutoGen, TravelPlanner, Reflexion, Gorilla,
  Toolformer). All required Tier-A citations for §2.2 (criteria §4 Ch2 row) are present.
  - **T2 (the crux theme)** is grounded by **N1 ItiNera** as PRIMARY (Tier A).
  - **§2.3 (route-opt crux)** is grounded by **N4 PyVRP + OSRM-PAPER** as PRIMARY (Tier A);
    software S-VROOM/S-VALHALLA/S-OSRM cited as infra.
- **Tier B (supporting): 9** — N5 AgentTravel (labelled "NORA / CEUR workshop"), 08 Pai, 09 Liu,
  10 Christina, 11 Pang, 12 Onuiri, 13 AlSaeed, 14 Tsaih, 15 Swanepoel. Used only as
  supporting evidence; no core claim rests on Tier-B alone.
- **Tier C (software): 3** — S-VROOM, S-VALHALLA, S-OSRM. Cited as software; **NO paper
  invented for VROOM** (Issue #735 maintainer confirmation quoted verbatim).
- **Tier D (preprint-only): 2** — N2 TRIP-PAL, N3 TravelAgent. Used ONLY as explicitly-labelled
  "arXiv preprint, not peer-reviewed" footnotes (T2-9, GAP-4). **Preferred ItiNera for every
  point they might otherwise carry.**

## Claims I could NOT ground (escalations)

**None.** Every required claim in the task brief was grounded against a verified quote bank
or criteria.md-mandated number. The two preprints (N2, N3) were included only as labelled
footnotes per criteria §2.

## Pending metrics labelled (not invented)

- **§4 eval metrics** (retrieval P@k/R/nDCG, feasibility, reliability, provenance coverage, UX
  e2e pass rate): **deferred entirely to Ch4** — Ch2 introduces NONE of these as results; only
  the *strategy* is defined (via AgentTravel's KnowEval/TripEval template, N5 Q5).
- **`thesis/evidence/05-db-completeness.json`** still reports the stale `total_active_pois:
  255`; flagged for regeneration (criteria §5) in figures-spec.md. **In Ch2 the dossier cites
  the criteria-mandated 310 for substrate size** and never cites 255 as a positive claim.
- **Dual-price count = 58, gov.eg descriptions = 76, any-enrichment = 97:** criteria-mandated
  (§4); cited in the research-gap statement without inventing provenance detail.

## Anti-fabrication compliance (criteria §7)

Verified by automated scan: every flagged stat appears ONLY inside "DO NOT cite / NEVER /
STALE" warnings, never as a positive claim:

| Stat | Status in dossier |
|---|---|
| Reflexion "+22% ALFWorld" | ABSENT as a claim; replaced with verified "130/134 ALFWorld" + "91% HumanEval" |
| Liu "+35% feature discovery" | ABSENT as a claim; replaced with verified "+22% task completion" |
| Pai "0.69" as structural β | ABSENT as a claim; replaced with verified "0.285 accessibility path coefficient" |
| Pang "β=0.326" | ABSENT as a claim; cited only as N=735 + qualitative finding |
| TravelAgent "5 modules" | Cited correctly as FOUR modules |
| POI count "255" | ABSENT as a positive claim; only appears in stale-flag warnings |
| VROOM paper | NONE invented; S-VROOM cited as software + cross-cited via N4 Q6 |
| Tsaih DOI | 10.1145/3568026 (NOT 10.1145/3579366) |
| Swanepoel degree | Master of Engineering (NOT Ph.D.) |

## Key research-gap framing delivered (GAP-1..GAP-5)

The synthesized closing claim, ready for the writer: *No prior system combines (i) an LLM
intent layer [01,03] with (ii) VRPTW-grade deterministic optimization [N4 Q4] over (iii) a
verified, region-balanced Egyptian POI substrate (310 POIs) with (iv) dual Egyptian/foreigner
pricing (58 POIs).* ItiNera [N1] is the closest precedent (satisfies (i) + a TSP-class (ii)
without time windows); VOYO's contribution is the gap ItiNera leaves: VRPTW-grade feasibility
+ Egyptian substrate + dual pricing.

## Notes for the parent orchestrator

1. The dossier is **read-only outside `thesis/ch2-background/`** — no edits to src/, citations/,
   evidence/, criteria.md, or the archived prior draft.
2. **Tables 2.1, 2.2, 2.3 are populated from verified `quotes.md`** (literature synthesis, not
   benchmark runs); a new Table 2.4 (route-opt crux) and Figure 2.1 (research-gap map) are
   introduced. None depend on the eval harness.
3. The dossier's Tier-A spine is symmetric with the thesis argument: T2 (the crux) and §2.3 (the
   technical anchor) both rest on N1 + N4 + OSRM-PAPER — exactly the criteria §2 admissibility
   rule.
4. **One residual for Ch6's regeneration queue:** `evidence/05-db-completeness.json` must be
   re-run on the 310-POI DB before Ch6 closes (criteria §5). The dossier flags this; Ch2
   doesn't block on it.
