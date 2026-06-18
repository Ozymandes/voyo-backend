# R14 Tsaih AI Tech-Stack — QUOTE BANK

> ✅ **STATUS: VERIFIED.** Content fetched directly from cacm.acm.org on 2026-06-16 (orchestrator retrieval via a bot-tolerant fetch path; the librarian's curl was Cloudflare-blocked, so the orchestrator completed this entry). Every quote below is verbatim from the fetched article.

## Q1 — The seven-layer model (Key Insights + body)
> "The proposed modularized, loosely coupled, seven-layered AI tech-stack model can leverage AIaaS offerings to help organizations resolve management and technology challenges. The seven layers—from bottom to top—are AI infrastructure, AI platform, AI framework, AI algorithm, AI data pipeline, AI services, and AI solution layers."
- **Locator:** https://cacm.acm.org/research/the-ai-tech-stack-model/ — "Key Insights" box (verbatim) and restated in §"The AI Tech-Stack Model". DOI 10.1145/3568026.

## Q2 — Why loosely coupled / modularization matters (the central architectural argument)
> "when using the decomposition concept, each vendor's AIaaS offering corresponds to one layer's functionality; thus, a change of vendor will not impact a change of vendors in other layers through the modularization architecture. Furthermore, IT managers can replace existing AI functions with better alternatives without interfering with the working functions of other layers."
- **Locator:** §"The AI Tech-Stack Model", paragraph following Table 2 assessment. DOI 10.1145/3568026.

## Q3 — The four layering principles (defends the boundary choices)
> "To define each specific layer in the AI tech-stack model, the following principles were adopted:
> 1. Categorize similar functions into the same layer to enable function changes within a layer without affecting other layers.
> 2. Create a boundary at a point where the service description can be concise and the number of interactions across boundaries is minimized.
> 3. Decompose layers for handling AI jobs that are manifestly unique in task description or skill requirements.
> 4. Develop a boundary at a point where industry solutions are available and have proven useful."
- **Locator:** §"The AI Tech-Stack Model", enumerated principles. DOI 10.1145/3568026.

## Q4 — Smart-tourism empirical grounding (the case study that ties it to VOYO's domain)
> "Tourism has been the industry most affected by the COVID-19 pandemic and has urgently sought digital transformation opportunities to boost business in the post-pandemic market by activating an AI-driven smart tourism strategy. We explained the proposed AI tech-stack model in an executive MBA class, and four companies expressed their interest in applying the model to their desired smart tourism recommendation system (STRS)."
- **Locator:** §"Applying the AI Tech-Stack Model in Enterprises". Case companies: Lion Travel (L), Colatour Travel (C), Tripaa Travel (T), Foru-Tek Travel (F). DOI 10.1145/3568026.

## Q5 — The model as a conceptual (not prescriptive) framework
> "The proposed AI tech-stack model can be deemed as a conceptual framework and does not map to specific systems. However, clearly characterizing the services provided by each layer, the model facilitates vendor interoperability [...]"
- **Locator:** §"The AI Tech-Stack Model", final paragraph of the model definition. DOI 10.1145/3568026.

## Verified bibliographic facts (safe to cite as metadata)
- Title: "The AI Tech-Stack Model" — verified.
- Authors: Rua-Huan Tsaih, Hsin-Lu Chang, Chih-Chung Hsu, David C. Yen — verified (CACM author byline).
- Venue: Communications of the ACM, vol. 66, no. 3, pp. 69–77, 2023 — verified.
- DOI: **10.1145/3568026** — verified (⚠️ NOT 10.1145/3579366, which is an unrelated IoT paper).

## Why it matters for VOYO (librarian's gloss — NOT a quote)
VOYO's layered architecture (Presentation → Gateway → Agentic Orchestration → Data) is an instance of exactly this kind of loosely-coupled, modularized AI system: each layer can be swapped (e.g. self-hosted Valhalla instead of a paid routing API) without disrupting the others. Q2 + Q3 give the architectural-justification language; Q4 anchors the model in the smart-tourism domain, so citing Tsaih positions VOYO within a peer-reviewed smart-tourism architecture lineage (not as an ad-hoc stack). Use Q5 honestly — it's a *conceptual* framework, so claim "informed by / consistent with" rather than "implements."
