# N5 — AgentTravel: Knowledge-Augmented LLM Agent Framework for Urban Travel Planning

- **STATUS: VERIFIED** (fetched full PDF via OpenReview, 571 KB; extracted text with pypdf, 8 pages)
- **Type:** PAPER (OpenReview submission, [Regular Track])
- **Note:** the OpenReview id is `34kIv0YVNe`.

## Bibliographic record
- **Authors:** Jie Zhao, Jie Feng, Yong Li (corresponding) — Department of Electronic Engineering, Tsinghua University; BNRist
- **Title:** AgentTravel: Knowledge-Augmented LLM Agent Framework for Urban Travel Planning
- **Venue:** OpenReview (Regular Track submission). Code/datasets: https://github.com/csjiezhao/AgentTravel
- **Primary URL:** https://openreview.net/pdf?id=34kIv0YVNe (forum: https://openreview.net/forum?id=34kIv0YVNe)
- **Note on venue:** Fetched as the OpenReview PDF. No external peer-review venue stamp appears on the PDF itself (it is a [Regular Track] submission) — flag this if the thesis needs a peer-reviewed venue; the GitHub repo is live and matches.

## Fetched-text summary (what I actually read)
Full 8-page text (abstract, intro, method, evaluation, conclusion). AgentTravel is a **three-component** framework: (1) **TravelLLM** — a domain-adapted base model fine-tuned with urban/spatial knowledge; (2) **TravelAgent** — an online agentic planner with real-time Web-API retrieval + structured itinerary memory + adaptive planning; (3) **TravelBench** — a benchmark with two modules, **KnowEval** (factual/spatial knowledge) and **TripEval** (plan feasibility, personalization, constraint satisfaction). Evaluated across **five Chinese cities**; releases a multi-source urban knowledge dataset (road networks, POIs, attractions, accommodations, restaurants). The intro explicitly motivates the work by citing that LLMs "often fail to accurately account for geographic distances, travel times, or accessibility constraints."

## Why it matters to VOYO (librarian's gloss — NOT a quote)
AgentTravel is the most architecturally congruent comparand to VOYO: it shares VOYO's three pillars — a knowledge-grounded model, an agentic planner with memory/retrieval, and a multi-perspective benchmark. Its benchmark split (KnowEval / TripEval) is a useful template for VOYO's evaluation chapter, and its explicit framing of "LLMs fail on spatial reasoning → ground them with real data + retrieval" is the same thesis VOYO argues. Note the naming collision: this paper's "TravelAgent" *component* is distinct from paper N3 (Chen et al.); disambiguate in prose.

## Thesis sections supported
Ch2.2 (lit-review — knowledge-grounded agentic travel theme), Ch2.3 tables, Ch3.4.1 (CLEO), Ch3.4.2 (recommendation / domain-adapted model), Ch3.4.5 (retrieval + memory), Ch4 (eval design — KnowEval/TripEval template).
