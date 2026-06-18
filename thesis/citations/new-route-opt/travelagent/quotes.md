# N3 TravelAgent — VERBATIM QUOTE BANK

> All quotes copied verbatim from ar5iv HTML. Locator = arXiv:2409.08069 + section.
> Rendered text fetched from https://ar5iv.labs.arxiv.org/html/2409.08069 (2026-06-16).

## Q1 — Four-module architecture + three criteria (Abstract)
> "we introduce TravelAgent, a travel planning system powered by large language models (LLMs) designed to provide reasonable, comprehensive, and personalized travel itineraries grounded in dynamic scenarios. TravelAgent comprises four modules: Tool-usage, Recommendation, Planning, and Memory Module."
- **Locator:** arXiv:2409.08069, Abstract.

## Q2 — The three evaluation criteria (Abstract)
> "services that support users in automatically creating practical and customized travel itineraries must address three key objectives: Rationality, Comprehensiveness, and Personalization."
- **Locator:** arXiv:2409.08069, Abstract.

## Q3 — Route Planner is spatiotemporal-aware (§3.4 Planning Module)
> "Planning Module comprises Budget Planner and Route Planner. We innovatively integrate budgetary elements into the planning process to enhance the itinerary's Rationality and Comprehensiveness, empowering planning with LLMs and a spatiotemporal-aware route algorithm."
- **Locator:** arXiv:2409.08069, §3.4 Planning Module.

## Q4 — Route Planner scoring mechanism (§3.4)
> "The scoring mechanism involves three components: [...] Return Time Score [...], which checks if the total travel time and duration at the [attraction] fit within the remaining day time; Optimal Visit Time Score [...], which evaluates how well the visit aligns with the preferred visiting window; [and] Reserve Time Score [...], which optimizes the use of the remaining time, prioritizing efficient day planning."
- **Locator:** arXiv:2409.08069, §3.4 Planning Module — Route Planner / Attraction Scores Calculation.

## Q5 — Memory Module: short-term + long-term (§3.5)
> "Memory Module is designed to promote Personalization and dynamic data processing and consists of two primary components: (1) Short-term Memory stores new user interactions and captures the immediate contextual travel data, constraints, and plans [...]. (2) Long-term Memory retains user data over extended periods, accumulating a comprehensive persona based on historical interactions."
- **Locator:** arXiv:2409.08069, §3.5 Memory Module.

## Q6 — Headline human-eval result (Table 1, §4.1)
Table 1 verbatim:
```
                    TravelAgent   GPT-4+ agent
Rationality             9.56          8.16
Comprehensiveness       8.87          6.25
Personalization         8.44          4.31
```
Caption: "Average human evaluation scores of Rationality, Comprehensiveness, and Personalization for TravelAgent and GPT-4+ agent across 20 travel cases."
- **Locator:** arXiv:2409.08069, Table 1, §4.1 Overall Evaluation Criteria.

## Q7 — Tool inventory (Appendix A, Table 2)
> "City Tool ... get_city_info — API-based — Retrieve real-time city information; Flight Tool ... get_flight_info — API-based — Retrieve real-time flight information; [...] Direction Tool ... get_direction_info — API-based — Retrieve route traffic information; [...] Distance Tool ... get_distance_info — Algorithm-based — Calculate distance"
- **Locator:** arXiv:2409.08069, Appendix A, Table 2 (List of Tools in Personalized TravelAgent).

---
### Accuracy flags for the thesis author
- ⚠️ The task brief called this a "5-module" system. The paper is explicit: **"four modules: Tool-usage, Recommendation, Planning, and Memory Module."** (Planning sub-contains Budget Planner + Route Planner, which is why it can be miscounted as five.) Cite as **four modules**.
- The TravelAgent here (Aili Chen et al., arXiv:2409.08069) is **different** from the "TravelAgent" component inside N5 AgentTravel (Jie Zhao et al.). Do not conflate the two when writing the lit review.
