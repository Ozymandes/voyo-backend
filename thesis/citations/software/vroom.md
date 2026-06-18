# S1 — VROOM (Vehicle Routing Open-source Optimization Machine) — SOFTWARE

- **STATUS: VERIFIED** (GitHub README + Issue #735 comments via GitHub API + source file via raw.githubusercontent.com)
- **Type:** SOFTWARE. **There is NO academic paper for VROOM** — confirmed verbatim by the maintainer in Issue #735 (quoted below). Cite VROOM as primary SOFTWARE with GitHub permalinks, never fabricate a paper.

## Bibliographic / project record
- **Project:** VROOM — Vehicle Routing Open-source Optimization Machine
- **Maintainer:** Julien Coupey (GitHub `jcoupey`), maintained by **Verso** (https://verso-optim.com)
- **Language:** C++20
- **Repo:** https://github.com/VROOM-Project/vroom
- **License header (from source):** "Copyright (c) 2015-2025, Julien Coupey. All rights reserved (see LICENSE)."
- **Primary URL:** https://github.com/VROOM-Project/vroom (README: master branch raw)

## ⚠️ NO-PAPER-EXISTS confirmation (the whole point — quote verbatim)
GitHub Issue #735, titled **"Paper describing the heuristics used in VROOM?"** (state: closed), asks "Is there a paper that describes which heuristics are used inside VROOM?" Maintainer `jcoupey` replied (2022-07-07):

> "No, there is no paper associated with the project. If you're interested in the heuristics, your best bet is to check out the implementation [...] We have two main heuristics used to compute initial solutions prior to applying the local search process: `basic` that is loosely adapted from the well-known Solomon I1 heuristic [...]; `dynamic_vehicle_choice` that is somehow a generalization of the latter [...] We also have a dedicated solving pipeline for the TSP which is based on an implementation of the Christofides heuristic + an ad-hoc local search process."

And closing the issue (2022-09-16):

> "Closing here as there is nothing actionable. Writing a research paper is outside the scope of this repo. ;-)"
- **Locator:** https://github.com/VROOM-Project/vroom/issues/735 (issue body + comment by `jcoupey` 2022-07-07; closing comment 2022-09-16). Fetched via GitHub API 2026-06-16.

## README description (verbatim, master branch)
> "Complex Route Optimization in Milliseconds / Good solutions, fast. [...] Vroom is an open-source route optimization engine written in C++20 that solves complex vehicle routing problems (VRP) in milliseconds."
- **Locator:** https://github.com/VROOM-Project/vroom/blob/master/README.md, lines 1–11 (raw: https://raw.githubusercontent.com/VROOM-Project/vroom/master/README.md).

## Source-file permalink (verbatim header)
From `src/algorithms/heuristics/heuristics.cpp`:
> "This file is part of VROOM. / Copyright (c) 2015-2025, Julien Coupey. / All rights reserved (see LICENSE)."
followed by `namespace vroom::heuristics {`
- **Locator:** https://github.com/VROOM-Project/vroom/blob/master/src/algorithms/heuristics/heuristics.cpp (lines 1–13); raw: https://raw.githubusercontent.com/VROOM-Project/vroom/master/src/algorithms/heuristics/heuristics.cpp

## Why it matters to VOYO (librarian's gloss — NOT a quote)
VROOM is VOYO's chosen route-optimization backend (the "optimize" stage of curate→optimize). It is the correct tool because it is purpose-built for *fast, real-life* VRPs (milliseconds) and integrates with routing engines (OSRM/Valhalla) — exactly VOYO's stack. The honest framing (supported by PyVRP's Q6) is: VROOM is fast and practical but **not** a state-of-the-art research solver; that trade-off is acceptable for VOYO because itinerary planning needs real-time, "good-enough" routes, not provably optimal ones.

## Thesis sections supported
Ch2.3.1 (self-hosted routing), Ch3.4.3 (curate→optimize), Ch3.5.1 (Valhalla/VROOM routing), Ch6 (data pipeline — matrix/optimization calls).
