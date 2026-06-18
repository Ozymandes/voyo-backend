# §2.2 / §2.3 — Citations Used

> Every citation id below resolves in `thesis/citations/INDEX.md`. Tier per criteria §2.
> Each row records the dossier claim(s) it grounds and the locator (quote id).

## Tier A — PRIMARY-ACADEMIC (load-bearing; ground core contribution claims)

| id | Short name | Locator(s) used | Dossier claims grounded |
|---|---|---|---|
| **N1** | ItiNera (Tang et al.) | Q1,Q2,Q3,Q4,Q5,Q6,Q7 | T2-1..T2-5; T3-1,T3-2; §2.3-1,§2.3-7; GAP-1,GAP-2,GAP-4,GAP-5 |
| **N4** | PyVRP (Wouda, Lan, Kool) | Q1,Q2,Q3,Q4,Q5,Q6 | §2.3-2,§2.3-3,§2.3-4; GAP-2; Table 2.4 (solver framing + VROOM characterization) |
| **OSRM-PAPER** | Luxen & Vetter | Q1,Q2,Q4,Q5,Q6,Q7 | §2.3-5; Table 2.4 (CH algorithm + "routing not a bottleneck") |
| **01** | Compound AI Systems (Zaharia et al.) | Q1,Q2,Q3,Q5 | T1-1,T1-2; T1 positioning; T2/T3 framing |
| **02** | Wang Agent Survey | Q1,Q2,Q3,Q4 | T1-3 |
| **03** | AutoGen (Wu et al.) | Q1,Q2,Q3,Q4 | T1-4; T2 positioning (role separation) |
| **04** | TravelPlanner (Xie et al.) | Q1,Q2,Q3 | T2-6; T3-3; GAP-4; Table 2.1 |
| **05** | Reflexion (Shinn et al.) | Q1,Q2,Q3,Q4 | T1-5; T3-4 (anti-fabrication: +22% ALFWorld NEVER) |
| **06** | Gorilla (Patil et al.) | Q1,Q3,Q4,Q5 | T1-6; T3-5; Table 2.1 |
| **07** | Toolformer (Schick et al.) | Q1,Q2,Q3,Q4,Q5,Q6 | T1-7; Table 2.1 |

**Tier-A count: 10** (N1, N4, OSRM-PAPER, 01–07). All required Tier-A citations for §2.2/§2.3
are present per criteria §4 (Ch2 row).

## Tier B — SUPPORTING (reinforce only; never carry a core claim alone)

| id | Short name | Locator(s) used | Dossier claims grounded |
|---|---|---|---|
| **N5** | AgentTravel (Zhao, Feng, Li) | Q1,Q2,Q5 | T2-7,T2-8; §2.3-8; Table 2.4 (eval comparand) — ⚠️ label "workshop paper" |
| **08** | Pai STT | Q1,Q2,Q3,Q4,Q5,Q6 | T4-1; Table 2.2 (anti-fabrication: 0.69-as-β NEVER; cite 0.285) |
| **09** | Liu Adaptive UI/UX | Q1,Q2,Q3,Q5,Q6 | T4-2; Table 2.2 (anti-fabrication: +35% feature-discovery NEVER; cite +22%) |
| **10** | Christina Tokopedia | Q1,Q2,Q3,Q4 | T4-3; Table 2.2 |
| **11** | Pang Chatbot Stickiness | Q1,Q2,Q3,Q4,Q5 | T4-4; Table 2.2 (anti-fabrication: β=0.326 NEVER; cite N=735 + qualitative) |
| **12** | Onuiri ITMS | Q1,Q2,Q3,Q4,Q5,Q6 | T4-5; Table 2.3 |
| **13** | AlSaeed LOCUS | Q1,Q3,Q4,Q5 | T4-6; Table 2.3 |
| **14** | Tsaih AI Tech-Stack | Q1,Q2,Q3,Q4,Q5 | T4-7; Table 2.3 (DOI 10.1145/3568026) |
| **15** | Swanepoel | Q1,Q2,Q3,Q4 | T4-8; Table 2.3 (M.Eng, not Ph.D.) |

**Tier-B count: 9** (N5, 08–15). Used only as supporting evidence; no core contribution claim
rests on a Tier-B source alone.

## Tier C — SOFTWARE-INFRASTRUCTURE (cite as software; NEVER as a paper)

| id | Tool | Locator(s) used | Dossier claims grounded |
|---|---|---|---|
| **S-VROOM** | VROOM | README; Issue #735 (maintainer "no paper") | §2.3-4; GAP-2; Table 2.4 — paired with N4 Q6 for academic characterization |
| **S-VALHALLA** | Valhalla | Isochrone API overview | §2.3-6; Table 2.4 |
| **S-OSRM** | OSRM (the tool) | `/table` service definition; README pipelines | §2.3-5; Table 2.4 — paired with OSRM-PAPER for the algorithm |

**Tier-C count: 3.** All cited as software; **no paper invented for VROOM** (Issue #735
maintainer confirmation); OSRM-the-tool is distinct from OSRM-the-paper.

## Tier D — PREPRINT-ONLY (footnotes only, explicitly labelled; never core evidence)

| id | Short name | Locator(s) used | Where used |
|---|---|---|---|
| **N2** | TRIP-PAL (de la Rosa et al.) | Q1,Q6 | T2-9 (footnote); GAP-4 (footnote) — explicitly labelled "arXiv preprint, not peer-reviewed" |
| **N3** | TravelAgent (Chen et al.) | Q1,Q6 | T2-9 (footnote) — explicitly labelled "arXiv preprint, not peer-reviewed"; **four modules, not five** |

**Tier-D count: 2.** Used ONLY as labelled-preprint footnotes per criteria §2. **Preferred
ItiNera (Tier A) for every point N2/N3 might otherwise carry.** No Tier-D source carries a
core contribution claim.

## Tier-discipline audit

- ✅ Every core contribution claim (T2-1..T2-5, T3-1..T3-2, §2.3-1..§2.3-7, GAP-1..GAP-5) traces
  to ≥1 Tier-A source (N1, N4, OSRM-PAPER, or 01–07).
- ✅ Tier-D (N2, N3) appears only as explicitly-labelled preprint footnotes (T2-9, GAP-4).
- ✅ Tier-C (S-VROOM, S-VALHALLA, S-OSRM) cited as software; no paper invented for VROOM
  (Issue #735 maintainer confirmation).
- ✅ OSRM is correctly split: OSRM-PAPER (Tier A, algorithm) ≠ S-OSRM (Tier C, running tool).
- ✅ N5 AgentTravel labelled "NORA / CEUR workshop paper" wherever used.

## Anti-fabrication flags applied (criteria §7 + quotes.md residuals)

| Stat | Status | Action |
|---|---|---|
| Reflexion "+22% ALFWorld" | FABRICATED (not in paper) | NEVER cited; replaced with verified "130/134 ALFWorld" + "91% HumanEval" |
| Liu "+35% feature discovery" | NOT in paper | NEVER cited; replaced with verified "+22% task completion" |
| Pai "0.69" as structural β | Discriminant-validity correlation, NOT structural | NEVER cited as β; replaced with verified "0.285 accessibility path coefficient" |
| Pang "β=0.326" | NOT in abstract (paywalled tables) | NEVER cited; replaced with verified N=735 + qualitative finding |
| TravelAgent "5 modules" | Paper says FOUR | Cited correctly as four modules |
| POI count "255" | STALE (criteria §4 mandates 310) | NEVER cited as 255; dossier uses 310 and flags evidence/05 for regeneration |
| VROOM paper | DOES NOT EXIST (Issue #735) | Cited as software (S-VROOM) + cross-cited via N4 Q6 |
| Tsaih DOI | Correct DOI is 10.1145/3568026 | NOT 10.1145/3579366 |
| Swanepoel degree | Master of Engineering | NOT Ph.D. |

## Citations NOT used (intentionally omitted)

None of the dossier's required citations were dropped. The full §2.2/§2.3 set mandated by
criteria §4 (T1:01–07; T2:N1; T3:N1,04; T4:08–15; §2.3:N4,OSRM-PAPER,S-VROOM,S-VALHALLA,S-OSRM,N5)
is present. N2 and N3 are included as Tier-D footnotes (criteria §2 allows this only when
explicitly labelled).
