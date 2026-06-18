# Ch1 — Introduction — CITATIONS USED

> Every citation id below resolves in `thesis/citations/INDEX.md`. Tier per criteria §2.
> Each row records the dossier claim(s) it grounds and the locator (quote id). **Hard rule
> (criteria §4 Ch1 row): required citations = 01 + N1; both present below.**

## Tier A — PRIMARY-ACADEMIC (load-bearing; grounds core contribution claims)

| id | Short name | Venue (cite this way) | Locator(s) used | Dossier claims grounded |
|---|---|---|---|---|
| **N1** | ItiNera (Tang et al.) | **EMNLP 2024 Industry Track + KDD UrbComp 2024 Best Paper** (arXiv:2402.07204) | Q1, Q3, Q4, Q5, Q7 | P3 (problem statement, verbatim Q3); P4 (ablation 86→242.8); H2,H3 (trust boundary + rationale); C0,C1,C3 (architecture + feasibility motivation); M1,M2,M3,M4 (the entire "LLM-alone cannot plan" motivation block) |
| **01** | Compound AI Systems (Zaharia et al.) | BAIR Blog, 18 Feb 2024 | Q1, Q3, Q5 | P1 (systems-not-models frame); P2 (compound-system definition); C1 (hybrid-architecture contribution) |

**Tier-A count: 2.** Both required citations for Ch1 (criteria §4: 01 + N1) are present, and
every **core** Ch1 claim (problem statement, thesis sentence's motivation half, the
hybrid-architecture contribution, the deterministic-feasibility contribution, the motivation
block) traces to ≥1 Tier-A source — N1 carries the load, 01 reinforces the systems framing.

## Tier C — SOFTWARE-INFRASTRUCTURE (named by role only; NEVER cited as a paper in Ch1)

| id | Tool | Role named (criteria §1) | Ch1 use |
|---|---|---|---|
| **S-VALHALLA** | Valhalla | isochrones (reachability) + routing | named in thesis sentence (H1,H2) + feasibility layer (C3); not cited as a paper |
| **S-VROOM** | VROOM | VRPTW feasibility + time-window optimization | named in thesis sentence (H1,H2) + feasibility layer (C3); not cited as a paper |
| **S-OSRM** | OSRM | distance / travel-time matrices | named in thesis sentence (H1,H2) + feasibility layer (C3); not cited as a paper |

**Tier-C count: 3** (named by role per criteria §1). The *academic* citations for these engines
(N4 PyVRP, OSRM-PAPER) are deliberately **deferred to Ch2/Ch3** per criteria §4 (Ch1 citation
set = 01 + N1); Ch1 does not widen scope to pull them in.

## Tier D — PREPRINT-ONLY (NOT USED)

| id | Short name | Rule | Ch1 disposition |
|---|---|---|---|
| **N2** | TRIP-PAL (de la Rosa et al.) | arXiv:2406.10196 preprint only; footnote-only if used | **OMITTED** — criteria §4 prefers N1 (Tier A) for the "LLM-alone cannot plan" point |
| **N3** | TravelAgent (Chen et al.) | arXiv:2409.08069 preprint only; footnote-only if used | **OMITTED** — same rule as N2 |

**Tier-D count: 0 used.** No preprint carries any Ch1 claim. (If the writer later wants a
secondary "LLM-planning unreliability" footnote, N2 may be added *only* as an explicitly
labelled "arXiv preprint, not peer-reviewed" footnote — but N1 already covers the point at
Tier A, so this is unnecessary.)

## Non-citation authorities (criteria + provenance files, not in INDEX.md)

These are **mandates and provenance**, not literature citations; they are cited inline as
criteria/provenance pointers, not as academic sources:

| Authority | Used for | Locator |
|---|---|---|
| `thesis/criteria/thesis-criteria.md` §1 | the verbatim thesis sentence (H1) + engine-role trust boundary (H2, C3) | criteria §1 |
| `thesis/criteria/thesis-criteria.md` §4 | the canonical numbers (POI=310, dual-price=58, gov.eg-desc=76, any-enrich=97) + stale-number sweep | criteria §4 |
| `data/ticket_prices_upsert.sql` | provenance for the **58** dual-price POIs (verified by line count, 2026-06-17) | SQL header + 58 `UPDATE pois` rows |

## Anti-fabrication audit (criteria §7)

- ✅ **Reflexion "+22% ALFWorld"** — FABRICATED; **never cited** in Ch1 (not in the citation
  list; Reflexion is not a Ch1 source at all).
- ✅ **POI count = 310** everywhere canonical; the stale **255** appears only as a flagged
  STALE value in `evidence-packet.md` §D, never as a positive claim.
- ✅ **No invented paper** for VROOM/Valhalla (named by role per criteria §1; "no paper exists"
  for VROOM per S-VROOM Issue #735).
- ✅ **N1's 86.0 → 242.8** is attributed to ItiNera, never to VOYO; VOYO's own ablation number
  is PENDING (Ch4), never stated in Ch1.
