# N2 — TRIP-PAL: Travel Planning with Guarantees by Combining Large Language Models and Automated Planners

- **STATUS: VERIFIED** (fetched full paper text via ar5iv HTML, 479 KB)
- **Type:** PAPER

## Bibliographic record
- **Authors:** Tomás de la Rosa, Sriram Gopalakrishnan, Alberto Pozanco, Zhen Zeng, Daniel Borrajo (JP Morgan AI Research; de la Rosa on leave from Universidad Carlos III de Madrid)
- **Title:** TRIP-PAL: Travel Planning with Guarantees by Combining Large Language Models and Automated Planners
- **arXiv:** 2406.10196 (submitted 14 Jun 2024)
- **Primary URL:** https://ar5iv.labs.arxiv.org/html/2406.10196 (mirror: https://arxiv.org/abs/2406.10196)
- **Disclaimer in paper:** "This paper was prepared for informational purposes by the Artificial Intelligence Research group of JPMorgan Chase & Co." (Conclusions section)

## Fetched-text summary (what I actually read)
Full text (abstract, intro, related work, method, evaluation, results, conclusion). TRIP-PAL is a **hybrid**: an LLM (GPT-4) extracts/translates travel info and user goals, then a **sound + optimal automated planner (Fast Downward, seq-opt-lmcut / A\* with admissible lmcut)** solves the resulting PDDL planning task, guaranteeing constraint satisfaction and utility maximisation. The paper studies **oversubscription planning** (not all POIs can be visited; the planner selects the optimal subset). Benchmark: 20 cities, 100 tasks. GPT-4 alone produced only **14/100 valid plans**; TRIP-PAL's plans have on average **1.19× more utility**; even ignoring validity, TRIP-PAL beats GPT-4 in 79/100 problems.

## Why it matters to VOYO (librarian's gloss — NOT a quote)
TRIP-PAL supplies the rigorous, citation-defensible argument that **an LLM alone cannot guarantee feasible/optimal itineraries** — it shows GPT-4 returns invalid (unexecutable) plans the vast majority of the time — and that pairing the LLM with a formal solver yields *guaranteed* constraint satisfaction. This is the academic justification for VOYO handing the "optimize" step to a dedicated solver (VROOM) rather than trusting the LLM with ordering. The oversubscription framing also maps onto VOYO's "select + order a feasible subset of POIs" stage.

## Thesis sections supported
Ch2.2 (lit-review — LLM+solver hybrid theme / research gap), Ch2.3 tables, Ch3.4.3 (curate→optimize), Ch3.5.1 (routing/optimization choice), Ch4 (eval rationale — feasibility/validity as a first-class metric).
