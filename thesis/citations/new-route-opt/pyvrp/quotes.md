# N4 PyVRP — VERBATIM QUOTE BANK

> All quotes copied verbatim from ar5iv HTML. Locator = arXiv:2403.13795 + section.
> Rendered text fetched from https://ar5iv.labs.arxiv.org/html/2403.13795 (2026-06-16).

## Q1 — What PyVRP is (Abstract)
> "We introduce PyVRP, a Python package that implements hybrid genetic search in a state-of-the-art vehicle routing problem (VRP) solver. The package is designed for the VRP with time windows (VRPTW), but can be easily extended to support other VRP variants. PyVRP combines the flexibility of Python with the performance of C++ [...] PyVRP is a polished implementation of the algorithm that ranked 1st in the 2021 DIMACS VRPTW challenge and, after improvements, ranked 1st on the static variant of the EURO meets NeurIPS 2022 vehicle routing competition."
- **Locator:** arXiv:2403.13795, Abstract.

## Q2 — HGS = genetic algorithm + local search (§4.1 Overview of HGS)
> "HGS is a hybrid algorithm that combines a genetic algorithm with a local search algorithm. It maintains a population with feasible and infeasible solutions. [...] in every iteration, two parents are selected from the population, and combined using a crossover operator to create a new offspring solution. [...] In each iteration, the new offspring solution is improved using local search, which considers time windows and capacities as soft constraints by penalising violations."
- **Locator:** arXiv:2403.13795, §4.1 Overview of HGS.

## Q3 — Local search dominates runtime and lives in C++ (§4.3)
> "This improvement procedure is typically the most expensive part of the HGS algorithm. Software profiling suggests that in PyVRP it accounts for 80-90% of the runtime, which is why the local search is implemented in C++. The implementation explores a granular neighbourhood [...]."
- **Locator:** arXiv:2403.13795, §4.3 Local search.

## Q4 — VRPTW problem definition (§2.2)
> "For the VRPTW, each customer additionally has a service time [...], an earliest arrival time [...] and latest arrival time [...] in between which service should start. A vehicle can wait at customer i when arriving too early, but cannot arrive after [the latest time]."
- **Locator:** arXiv:2403.13795, §2.2 VRPTW.

## Q5 — Benchmark results near-optimal (§6 Experiments; Tables 1–2)
> "PyVRP obtains a mean gap of 0.22% and a gap of the mean of 0.27% on the solved instances." [CVRP, X instances]
> "PyVRP achieves a mean gap of 0.40% and gap of mean of 0.46% on the VRPTW benchmark instances [...]. Furthermore, during extended runs, PyVRP managed to improve 27 of the 300 best known solutions of the complete Homberger and Gehring instances." [VRPTW]
- **Locator:** arXiv:2403.13795, §6.1 CVRP (Table 1) and §6.2 VRPTW (Table 2).

## Q6 — Academic characterisation of VROOM (Related Projects §3) — cross-cites S1
> "VROOM (Coupey et al. 2023), the Vehicle Routing Open-source Optimisation Machine, is an open-source solver that aims to provide good solutions to real-life VRPs. In particular, it integrates well with open-source routing software to solve real-life VRPs within limited computation time. It implements many constructive heuristics and a local search algorithm in C++ and can handle different types of VRPs. However, it is unable to compete with state-of-the-art algorithms and lacks documentation to customise its underlying solver."
- **Locator:** arXiv:2403.13795, §3 Related projects, VROOM bullet.

## Q7 — Aims / audience (§1 Introduction)
> "We especially hope that PyVRP will help machine learning (ML) researchers interested in vehicle routing to easily build on the state-of-the-art, and move beyond LKH-3 [...] as the most commonly used baseline."
- **Locator:** arXiv:2403.13795, §1 Introduction.

## Q8 — BibTeX-grade provenance (References section)
> "Wouda NA, Lan L, Kool W (2023) PyVRP: a high-performance VRP solver package. URL http://dx.doi.org/10.1287/ijoc.2023.0055.cd, available for download at https://github.com/INFORMSJoC/2023.0055"
- **Locator:** arXiv:2403.13795, References — Wouda et al. (2023).

---
### Accuracy flags for the thesis author
- The arXiv abstract title reads "PyVRP: a high-performance VRP solver package"; the published INFORMS JoC companion DOI is **10.1287/ijoc.2023.0055**. Either citation form is valid; for a thesis, prefer the INFORMS JoC venue + DOI.
- Q6 is the single best academically-sourced sentence about VROOM — use it to frame *why* VROOM is "good enough / fast" but *not* SOTA, which is honest and defensible.
