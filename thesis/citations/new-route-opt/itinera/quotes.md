# N1 ITINERA — VERBATIM QUOTE BANK

> Every quote below is copied verbatim from fetched text. Locator = arXiv:2402.07204 + exact location.
> `v5` = arXiv:2402.07204v5 (9 Jan 2025). Page numbers refer to that PDF.

## Q1 — Definition of the OUIP task and the system (Abstract, p.1; also on arXiv abstract page)
> "we introduce the novel task of Open-domain Urban Itinerary Planning (OUIP), which generates personalized urban itineraries from user requests in natural language. We then present ITINERA, an OUIP system that integrates spatial optimization with large language models to provide customized urban itineraries based on user needs. This involves decomposing user requests, selecting candidate points of interest (POIs), ordering the POIs based on cluster-aware spatial optimization, and generating the itinerary."
- **Locator:** arXiv:2402.07204, Abstract, p.1. (mirrored verbatim at https://arxiv.org/abs/2402.07204 and https://github.com/YihongT/ITINERA README §Abstract)

## Q2 — The five-module architecture (§1 Introduction, p.1–2)
> "ITINERA comprises five LLM-assisted modules: User-owned POI Database Construction (UPC), Request Decomposition (RD), Preference-aware POI Retrieval (PPR), Cluster-aware Spatial Optimization (CSO), and Itinerary Generation (IG), to deliver personalized [...]"
- **Locator:** arXiv:2402.07204, §1 Introduction, p.1–2.

## Q3 — Motivation: pure LLMs lack optimization capability (§1, p.1)
> "their limitations in itinerary planning are evident [...] (1) Pure LLMs cannot refer to specific POI lists, resulting in outdated or hallucinated POIs. (2) LLMs lack the optimization capabilities required for planning tasks, leading to suboptimal itineraries. Consequently, LLM-generated itineraries can be circuitous, lack detail, and include impractical information."
- **Locator:** arXiv:2402.07204, §1 Introduction, p.1.

## Q4 — CSO solved as a hierarchical TSP (§3.5, p.4)
> "we compute spatial clusters of the retrieved POIs and select candidates based on proximity and matching scores, addressing cluster-aware spatial optimization by solving a hierarchical traveling salesman problem [...], a common and fundamental spatial reasoning task [...]."
- **Locator:** arXiv:2402.07204, §3.5 Cluster-aware Spatial Optimization / §3.5.1, p.4.

## Q5 — Ablation: removing CSO destroys route quality (Table 2, p.6; discussion p.7)
> "Removing the CSO module worsens the Average Margin and Overlaps but improves Recall Rate, POI Quality, and Match, showing the full model balances alignment with spatial ability."
- Table row (verbatim): "ITINERA w/o CSO ✓ ✓ ✓ × ✓ 32.8 242.8 1.04 72.1 60.2 74.2" vs "ITINERA (full) ✓ ✓ ✓ ✓ ✓ 31.4 86.0 0.42 69.8 64.6 72.0"
- **Locator:** arXiv:2402.07204, Table 2 (Ablation study on Shanghai dataset) p.6; discussion text p.7. Metric AM=Average Margin: 86.0 (full) → 242.8 (w/o CSO).

## Q6 — Deployed real-world system (§4.5, p.7)
> "Our deployed system is currently accessible to a select group of users recommended by our partnered travel agency. To verify the effectiveness of our system in real-world scenarios, we conduct human evaluations. [...] We invite 464 regular users of our system (User) and 33 experienced travel assistants from our partnered travel agency (Expert) to compare [...]"
- **Locator:** arXiv:2402.07204, §4.5 Deployed System Performance, p.7.

## Q7 — Dataset scale (§4.1, p.5)
> "In total, the dataset covers 1233 top-rated urban itineraries and 7578 POIs."
- **Locator:** arXiv:2402.07204, §4.1 Experimental Setup, p.5.

## Venue provenance (for citing as EMNLP/KDD, from the GitHub README — verbatim)
> "Code for 'ITINERA: Integrating Spatial Optimization with Large Language Models for Open-domain Urban Itinerary Planning' / Published in the EMNLP 2024 Industry Track Proceedings / Received Best Paper Award at KDD Urban Computing Workshop (UrbComp) 2024"
- **Locator:** https://github.com/YihongT/ITINERA README, lines 3–7 (fetched 2026-06-16).

---
### Accuracy flags for the thesis author
- arXiv id is **2402.07204** (the task brief's instruction to "find the arXiv id from the repo README" succeeded — the README links it directly).
- EMNLP Industry Track paper = **20 pages**; the EMNLP version and the arXiv v5 are substantively the same (the "5 LLM-assisted modules" framing is in both).
