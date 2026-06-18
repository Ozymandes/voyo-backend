# N4 — PyVRP: a high-performance VRP solver package

- **STATUS: VERIFIED** (fetched full paper text via ar5iv HTML, 415 KB; arXiv abstract page)
- **Type:** PAPER (published in INFORMS Journal on Computing)

## Bibliographic record
- **Authors:** Niels A. Wouda, Leon Lan, Wouter Kool
- **Title:** PyVRP: a high-performance VRP solver package
- **arXiv:** 2403.13795 (v1 submitted 22 Nov 2023; v2 21 Mar 2024)
- **Venue / Year:** INFORMS Journal on Computing (the ar5iv references list cites "Wouda, Lan, Kool (2023)" with DOI 10.1287/ijoc.2023.0055.cd, companion data at github.com/INFORMSJoC/2023.0055)
- **Primary URL:** https://arxiv.org/abs/2403.13795 (full text: https://ar5iv.labs.arxiv.org/html/2403.13795); code https://github.com/PyVRP/PyVRP ; docs https://pyvrp.org

## Fetched-text summary (what I actually read)
Full text (intro, problem description, related projects, HGS technical implementation, package, experiments, conclusion). PyVRP implements **hybrid genetic search (HGS)** — a genetic algorithm + granular local search — for the **CVRP and VRPTW**. Earlier versions **ranked 1st in the 2021 DIMACS VRPTW challenge** and **1st on the static variant of the EURO meets NeurIPS 2022 VRP competition**. Local search accounts for 80–90% of runtime and is in C++; the rest is Python. Experiments: mean gap 0.22% (CVRP, X instances) and 0.40% (VRPTW, Homberger–Gehring 1000-customer) vs best-known. The paper's **Related Projects section explicitly characterizes VROOM** (useful for cross-citing S1).

## Why it matters to VOYO (librarian's gloss — NOT a quote)
PyVRP is the academic anchor that legitimises VOYO's *choice of problem family* — it establishes that the Capacitated VRP / VRP with Time Windows is a well-defined, benchmarked operations-research problem solved to near-optimality by hybrid genetic search, and that the same HGS lineage underlies the tools (and the algorithmic ideas) behind VROOM. Cite it to defend: (a) why VOYO frames itinerary optimization as a VRP/VRPTW, and (b) why a metaheuristic solver is an appropriate (near-optimal, fast) choice. Its candid comparison of VROOM vs SOTA solvers is also directly quotable.

## Thesis sections supported
Ch2.2 (lit-review — optimization foundations), Ch2.3 tables, Ch3.5.1 (Valhalla/VROOM routing — algorithmic lineage), Ch4 (eval — optimality-gap framing).
