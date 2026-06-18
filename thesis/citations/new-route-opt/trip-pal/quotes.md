# N2 TRIP-PAL — VERBATIM QUOTE BANK

> All quotes copied verbatim from ar5iv HTML. Locator = arXiv:2406.10196 + section.
> Rendered text fetched from https://ar5iv.labs.arxiv.org/html/2406.10196 (2026-06-16).

## Q1 — Core claim / hybrid design (Abstract)
> "We propose TRIP-PAL, a hybrid method that combines the strengths of LLMs and automated planners, where (i) LLMs get and translate travel information and user information into data structures that can be fed into planners; and (ii) automated planners generate travel plans that guarantee constraint satisfaction and optimize for users' utility."
- **Locator:** arXiv:2406.10196, Abstract.

## Q2 — Why LLMs alone fail at planning (Abstract)
> "current state-of-the-art models often generate plans that lack coherence, fail to satisfy constraints fully, and do not guarantee the generation of high-quality solutions."
- **Locator:** arXiv:2406.10196, Abstract.

## Q3 — LLMs as bad reasoners for sequential decision making (Introduction)
> "However, LLMs have been shown to be bad reasoners especially in tasks that involve sequential decision making [...]; travel planning is one such type of domain."
- **Locator:** arXiv:2406.10196, Introduction.

## Q4 — Soundness/optimality guarantee from the formal planner (Method: Automated Planning Task)
> "By explicitly representing the planning problem and using an optimal planner, we ensure that the generated plans are sound (valid), comply with constraints, and are optimal."
- **Locator:** arXiv:2406.10196, Method — Automated Planning Task.

## Q5 — The planner used (Evaluation: Experimental Setting)
> "TRIP-PAL uses Fast Downward (Helmert 2006) as the AI planner [...]. We use the seq-opt-lmcut configuration of Fast Downward, which runs A* with the admissible lmcut heuristic to compute plans that are guaranteed to be valid and optimal."
- **Locator:** arXiv:2406.10196, Evaluation — Experimental Setting, Approaches.

## Q6 — Headline result: GPT-4 validity is very low (Results)
> "GPT-4 returned 14 valid plans out of the 100 tasks, clearly indicating that it struggles to generate travel plans that satisfy hard constraints."
- **Locator:** arXiv:2406.10196, Results — Standard Day Travel Planning.

## Q7 — Utility advantage even among GPT-4's few valid plans (Results)
> "Focusing back on the 14 tasks for which GPT-4 generated a valid travel plan, TRIP-PAL's plans have on average of 1.19 ± 0.12 times more utility."
- **Locator:** arXiv:2406.10196, Results — Standard Day Travel Planning.

## Q8 — Robustness of TRIP-PAL when validity check is removed (Results)
> "In this setting, TRIP-PAL is still generating plans with higher utility than GPT-4 in 79 of the 100 problems. This highlights that, even when we do not constrain GPT-4 to follow some guidelines, it is still generating worse travel itineraries than TRIP-PAL, whose plans are guaranteed to be sound and optimal."
- **Locator:** arXiv:2406.10196, Results — Standard Day Travel Planning.

## Q9 — Oversubscription planning framing (Method)
> "Oversubscription planning focuses on the class of tasks where not all goals can be achieved because the availability of bounded resources. This is the case for travel planning, since a tourist may be willing to visit more POIs that one can handle in a day itinerary."
- **Locator:** arXiv:2406.10196, Method — Automated Planning Task.

## Q10 — Conclusion / generalizable hybrid claim (Conclusions and Future Work)
> "we presented a hybrid approach for travel planning that combines the strengths of LLMs and automated planners to generate travel plans that guarantee feasibility and maximize the satisfaction of user goals."
- **Locator:** arXiv:2406.10196, Conclusions and Future Work.

---
### Accuracy flags for the thesis author
- TRIP-PAL's solver is a classical **PDDL/AI planner (Fast Downward)**, *not* a VRP/VRPTW solver. Cite it as the "LLM + formal planner" exemplar, distinct from VOYO's "LLM + VRP solver (VROOM)" choice. Do not conflate the two solver families.
- arXiv:2406.10196 carries a **JP Morgan disclaimer** (informational, not investment research) — irrelevant to citation but worth knowing.
