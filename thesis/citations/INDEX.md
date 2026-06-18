# VOYO Thesis — Verified Citation Evidence Base (INDEX)

> Built by the VOYO Thesis Citation Librarian, 2026-06-16; **re-tiered 2026-06-16 by the
> orchestrator** to encode the citation-admissibility policy in
> `thesis/criteria/thesis-criteria.md` §2. Every entry was re-verified by **fetching real
> text** (curl/ar5iv/PDF/DSpace-API/Semantic-Scholar), not by trusting web_search syntheses.
>
> **TIER governs admissibility** (criteria.md §2): **A** = load-bearing primary-academic;
> **B** = supporting; **C** = software-infrastructure (never a paper); **D** = preprint-only,
> deprioritized. A core contribution claim must trace to ≥1 Tier-A source.
>
> **STATUS** = VERIFIED (real text fetched & quoted) | VERIFIED-META (metadata only, text
> fetch-pending) | PARTIALLY VERIFIED. "Locator-rich" = 3–8 verbatim quotes in `quotes.md`.

## TIER A — PRIMARY-ACADEMIC (load-bearing; may ground core contribution claims)

| Ref id | Short name | Venue (cite this way) | STATUS | Primary URL | Thesis sections |
|---|---|---|---|---|---|
| **N1** | ItiNera (Tang et al.) | EMNLP 2024 Industry + KDD UrbComp 2024 Best Paper | **VERIFIED** | https://arxiv.org/abs/2402.07204 | Ch1, Ch2.2(T2), Ch2.3, Ch3, Ch4 |
| **N4** | PyVRP (Wouda, Lan, Kool) | INFORMS Journal on Computing | **VERIFIED** | https://arxiv.org/abs/2403.13795 | Ch2.3, Ch3, Ch4 |
| **OSRM-PAPER** | Luxen & Vetter | ACM SIGSPATIAL GIS 2011 (DOI 10.1145/2093973.2094062) | **VERIFIED** ✅ (abstract + References fetched verbatim via Wayback snapshot of ACM page, 2026-06-17; 3 quotes in quotes.md) | https://doi.org/10.1145/2093973.2094062 | Ch2.3, Ch3 |
| 01–07 | Compound AI Systems; Wang survey; AutoGen; TravelPlanner; Reflexion; Gorilla; Toolformer | NeurIPS/ICML/BAIR/Springer | **VERIFIED** | (per entry) | Ch1–Ch3 (Tier A *within* the agentic-architecture theme) |

## TIER B — SUPPORTING (reinforce only; may not carry a core claim alone)

| Ref id | Short name | Venue | STATUS | Primary URL | Thesis sections |
|---|---|---|---|---|---|
| **N5** | AgentTravel (Zhao, Feng, Li) | NORA / CEUR workshop | **VERIFIED** ⚠️ label as workshop | https://openreview.net/pdf?id=34kIv0YVNe | Ch2.2(T2), Ch4 (eval design only) |
| 08 | Pai STT | Sustainability (MDPI) | **VERIFIED** ✅ full-text (accessibility β=0.285 confirmed; ⚠️ "0.69" is discriminant-validity, not structural β) | https://www.mdpi.com/2071-1050/12/16/6592 | Ch2.2(T4), Ch4 |
| 09 | Liu Adaptive UI/UX | CS&IT Research Journal | **VERIFIED** ✅ full-text (22% task completion + SOM confirmed; ⚠️ "+35% feature discovery" NOT found — drop) | https://doi.org/10.51594/csitrj.v5i8.1457 | Ch2.2(T4), Ch3, Ch4 |
| 10 | Christina Tokopedia | J. Business & Info Systems | **VERIFIED** ✅ full-text (N=204, PLS-SEM, UTAUT, satisfaction fully mediates) | https://thejbis.upy.ac.id/index.php/jbis/article/view/326 | Ch2.2(T4), Ch4 |
| 11 | Pang Chatbot Stickiness | JTAER (MDPI) | **VERIFIED** ✅ authors confirmed from PDF (Hua Pang, Zhuyun Hu, **Lei Wang**) | https://www.mdpi.com/0718-1876/20/3/228 | Ch2.2(T4), Ch4 |
| 12 | Onuiri ITMS | ASRJETS | **VERIFIED** ✅ full-text (50 locations, RUP, MySQL/HTML/PHP, hybrid rec — all confirmed) | https://asrjetsjournal.org/index.php/American_Scientific_Journal/article/view/1577 | Ch2.2(T4), Ch6 |
| 13 | AlSaeed LOCUS | Informatica (Slovenia) | **VERIFIED** ✅ full-text (SUS 87.75, 5.4s, CF, N=10 all confirmed) | https://informatica.si/index.php/informatica/article/view/4351 | Ch2.2(T4), Ch3, Ch4 |
| 14 | Tsaih AI Tech-Stack | Communications of the ACM | **VERIFIED** ✅ (full text fetched 2026-06-16; DOI 10.1145/3568026) | https://cacm.acm.org/research/the-ai-tech-stack-model/ | Ch3 |
| 15 | Swanepoel Architecture | M.Eng thesis, Stellenbosch | **VERIFIED** ✅ full-text (179pp; title/degree/supervisor/date all confirmed verbatim) | https://scholar.sun.ac.za/handle/10019.1/125975 | Ch2.2(T4), Ch3 |

## TIER C — SOFTWARE-INFRASTRUCTURE (cite as software; NEVER an academic paper)

| Ref id | Tool | STATUS | Primary URL | Thesis sections |
|---|---|---|---|---|
| **S-VROOM** | VROOM | **VERIFIED** (incl. verbatim "no paper exists" — Issue #735) | https://github.com/VROOM-Project/vroom | Ch2.3, Ch3, Ch6 |
| **S-VALHALLA** | Valhalla | **VERIFIED** | https://valhalla.github.io/valhalla/api/isochrone/api-reference/ | Ch2.3, Ch3, Ch6 |
| **S-OSRM** | OSRM (the tool) | **VERIFIED** | https://project-osrm.org/docs/v5.24.0/api/ | Ch2.3, Ch3, Ch6 |

## TIER D — DEPRIORITIZED / PREPRINT-ONLY (omit unless clearly labelled; never core evidence)

| Ref id | Short name | Venue | STATUS | Rule |
|---|---|---|---|---|
| **N2** | TRIP-PAL (de la Rosa et al.) | **arXiv:2406.10196 preprint** | **VERIFIED** (text fetched) | Do NOT rely on as core evidence. Cite only as labelled-preprint footnote if used at all. Prefer ItiNera (Tier A) for the same point. |
| **N3** | TravelAgent (Chen et al.) | **arXiv:2409.08069 preprint** | **VERIFIED** ⚠️ 4 modules not 5 | Same as N2. Omit from core architecture argument. |

## Tally
- **Tier A (primary-academic):** N1, N4, OSRM-PAPER, 01–07 → 10 entries (OSRM-PAPER now VERIFIED — abstract fetched via Wayback 2026-06-17).
- **Tier B (supporting):** N5, 08–15 → 9 entries (**all FULL-TEXT VERIFIED 2026-06-17** from provided PDFs: 08/09/10/11/12/13/15; abstract residuals noted per-entry: 08 "0.69" is discriminant-validity not structural; 09 "+35% feature discovery" not found — drop it).
- **Tier C (software):** S-VROOM, S-VALHALLA, S-OSRM → 3 entries (VERIFIED; no fabricated papers).
- **Tier D (preprint, deprioritized):** N2, N3 → 2 entries (VERIFIED text, but usage-restricted).
- **TOTAL:** 24 citation targets across 23 sources (OSRM has BOTH a Tier-A paper and a Tier-C software entry).
- **Corrections surfaced (apply to references.bib on regeneration):** see `work/librarian_phase0.md` §4 — incl. Tsaih DOI 10.1145/3568026, Swanepoel handle 10019.1/125975, Pang 2nd-author, Reflexion "+22% ALFWorld" is FABRICATED (verbatim = "130 out of 134 tasks").

## File map
```
thesis/citations/
  INDEX.md                      (this file)
  new-route-opt/{itinera,trip-pal,travelagent,pyvrp,agenttravel,osrm}/{source.md,quotes.md}
  software/{vroom,valhalla,osrm}.md
  ref 01..15:  <slug>/{source.md,quotes.md}
```
