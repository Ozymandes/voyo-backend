# Chapter 2 — Background and Related Work (enhancement layer)

> Maps to PDF Chapter 2. The PDF draft already contains a complete 2.1 (General Research Context)
> and 2.2.1–2.2.16 (literature review) plus the List-of-Tables entries for Tables 2.1–2.3. **This
> file is the enhancement/verification layer, not a replacement for the PDF body.** It (a) records
> the corrections the verification pass found, (b) flags the one unverifiable statistic, (c)
> populates the three comparison tables that the PDF left stubbed, and (d) adds a synthesis
> paragraph. The verified reference list lives in `thesis/references.bib`; per-reference evidence
> in `thesis/lit-review-evidence.md`.

## 2.0 Verification corrections to apply to the PDF body

When transferring the PDF's §2.1–2.2.16 into the LaTeX repo, apply these corrections (all
verified, see `thesis/lit-review-evidence.md`):

1. **Reference [1] — author.** The PDF *body* correctly says "Zaharia et al. [1]". The PDF
   *reference list* wrongly says "R. Gupta et al." The paper is **Matei Zaharia et al.**,
   *"The Shift from Models to Compound AI Systems,"* Berkeley BAIR Blog, Feb 2024. Correct the
   reference-list entry.
2. **Reference [15] — degree.** The PDF says *"Ph.D. dissertation."* It is a **Master of
   Engineering (Industrial Engineering)** thesis (Stellenbosch, Dec 2022). Correct.
3. **Reference [2] — venue.** The PDF says *"vol 18, no 6."* The Springer record is *vol 18,
   article 186345* (2024). Correct.
4. **References [9], [13] — author names.** Expand "Y. Liu" → **Yingchia Liu** (with Tan, Cao,
   Xu); "D. H. AlSaeed" → **Duaa Hamed AlSaeed**.
5. **Reference [5] — Reflexion authors.** Include **Edward Berman** (Shinn, Cassano, Berman,
   Gopinath, Narasimhan, Yao).
6. **§2.2.7 Toolformer statistics — flag.** The directional claim (large zero-shot gains on
   SQuAD-style factual completion, ASDiv math reasoning, and DATESET temporal reasoning) is
   verified. The **exact percentages** (17.8→33.8 / 7.5→40.4 / 3.9→27.3) were **not re-quoted in
   the sources returned** and are marked **[UNVERIFIED per-benchmark]** in
   `lit-review-evidence.md`. Either re-check them against the full Toolformer paper text before
   keeping the exact figures, or soften to "substantial zero-shot gains across factual,
   mathematical, and temporal reasoning benchmarks."

All other statistics in the PDF body (Reflexion +22% ALFWorld / 91% HumanEval; Gorilla 59.13%
vs 38.70% / hallucination 6.98% vs 36.55%; Pai β=0.285 accessibility / β=0.69 STT→satisfaction
/ N=527; Liu +22% task completion / +35% feature discovery; Christina N=204 full mediation;
Pang N=735 / β=0.326 tech motivation; LOCUS SUS 87.75 / 5.4 s / N=10) are **verified** against
their sources.

## 2.1 General Research Context — unchanged

The PDF §2.1 (the move from static recommender systems → monolithic LLMs → RAG → agentic and
compound AI) is accurate and well-written; it stands as-is. The framing — that hallucination and
hard-constraint failure in monolithic LLMs motivate the compound-system shift [1] — is exactly
the problem VOYO addresses.

## 2.2 Literature Review — synthesis note to append

The PDF §2.2.1–2.2.16 is retained verbatim. The following one-paragraph synthesis should be
appended to §2.2.16 (after the tables), tying the corpus to VOYO's actual design:

> Read together, the corpus maps cleanly onto VOYO's architecture. The compound-systems and
> agentic-coding works [1, 2, 3, 4, 5, 6, 7] justify the architectural skeleton — a system-centric
> design [1] with the standardized Profile/Memory/Planning/Action modules [2], role separation
> between a conversational agent and a logic agent [3, 4], and tool-coupled reasoning grounded in
> verified functions [6, 7] with a self-correction loop [5]. The smart-tourism and engagement
> works [8, 9, 10, 11] justify the experience priorities — accessibility and verified information
> for long-term retention [8], adaptive front-end design [9], and the empirical finding that AI
> influences engagement *indirectly* through satisfaction rather than raw functionality [10, 11].
> Finally, the intelligent-systems and architecture works [12, 13, 14, 15] provide the
> applications-and-layering baseline that VOYO extends — replacing static recommendation and
> rule-based retrieval [12, 13] with agentic reasoning over a verified database, and aligning with
> the loosely-coupled, layered architecture model [14, 15] that keeps reasoning, data, and
> presentation independently evolvable.

## 2.3 Comparison Tables (populated; the PDF left these stubbed)

The three tables below populate the PDF's List-of-Tables entries 2.1–2.3, drawing on the verified
findings in `lit-review-evidence.md`. Markdown lives in `thesis/tables/2.1-2.3-skeleton.md`
(populated form below); emit LaTeX equivalents for the repo.

### Table 2.1 — AI Architecture and Agentic Coding Research [refs 1–7]

| Ref | Primary focus | Grounding / tool-use | Technical goal | Role in VOYO |
|---|---|---|---|---|
| [1] Compound AI Systems | Orchestrating interacting components, not scaling one model | Retrievers + DBs to solve model hallucination | Shift from model-centric to system-centric design | Defends the compound-system skeleton; justifies the heavy backend |
| [2] Agent Survey | Standardizing Profile / Memory / Planning / Action | Links the "brain" to the tool suite | Unifies fragmented agent terminology into a modular blueprint | Maps to CLEO's modules + the deterministic recommendation engine |
| [3] AutoGen | Task-solving via structured multi-agent conversation | Separates reasoning (Assistant) from execution (User Proxy) | Separation of concerns improves reliability | Justifies separating CLEO (conversation) from the Planner/optimizer |
| [4] TravelPlanner | Multi-constraint logistical travel planning | Ground-truth content for accurate, feasible plans | Ensure itineraries are logical and feasible | Validates specialized agents + tool-verified logistics |
| [5] Reflexion | Self-correction via verbal reinforcement learning | Decides if a query needs a tool vs. a direct response | Structured feedback + memory improve agent behaviour | Motivates CLEO's response-validation pass + persistent memory |
| [6] Gorilla | Accurate external API invocation | Retriever-aware tool selection | Reduce hallucinated API usage | Motivates tight coupling of CLEO to verified tool functions |
| [7] Toolformer | Self-supervised tool use | Loss-filtered API calls | Teach the model *when* to call tools | Foundation for CLEO's tool-execution environment |

### Table 2.2 — Smart Tourism Technology and User Engagement Research [refs 8–11]

| Ref | Primary focus & theory | Methodology & sample | Key findings | Role in VOYO |
|---|---|---|---|---|
| [8] Smart Tourism Tech (UTAUT) | How STT attributes drive satisfaction | PLS-SEM, N=527 (Macau) | Accessibility strongest driver (β=0.285); STT→satisfaction→revisit | Justifies mobile-first accessibility + verified data for retention |
| [9] Adaptive UI/UX | Real-time interface personalization | Modular pipeline (SOM+MLP+RL), 10k+ users | +22% task completion; +35% feature discovery | Grounds VOYO's adaptive front-end + decoupled presentation |
| [10] Tokopedia (UTAUT) | Chatbot/recommender → engagement | PLS-SEM, N=204 | Satisfaction fully mediates AI→engagement | Supports CLEO (trust) ↔ Planner (utility) separation |
| [11] Chatbot Stickiness | Motivations → sustainable usage | SEM (U&G+TAM+ECM+ISSM), N=735 | Tech motivation strongest (β=0.326); privacy invasion hurts | Validates grounded-data design to preserve user trust |

### Table 2.3 — Intelligent Systems and Software Architecture Research [refs 12–15]

| Ref | Primary focus | Methodology & architecture | Key contributions | Role in VOYO |
|---|---|---|---|---|
| [12] Intelligent Tourism Mgmt | Information overload, fragmented data access | Web-based (RUP + MySQL), Nigeria, 50 locations | Hybrid recommendation; reduced search effort | Early foundation for VOYO's centralized DB + recommendation |
| [13] LOCUS | Personalized recommendations on mobile | Client–server; item-item + user-user CF; cosine similarity | SUS 87.75; 5.4 s task time; N=10 UAT | Baseline for VOYO's mobile + recommendation design |
| [14] AI Tech-Stack Model | Managing AI-system complexity / vendor lock-in | Seven-layer loosely-coupled stack (Infrastructure→Solution) | Localizes tech debt; flexible API integration | Architectural justification for VOYO's layered separation |
| [15] Swanepoel (Master's) | Scalability + data heterogeneity in smart tourism | Layered service-oriented reference architecture | Decoupled data/intelligence/application services | Reinforces VOYO's decoupled layers at national-tourism scale |

### 2.3.1 The implemented extension: self-hosted routing

A point worth making explicit because it is a genuine contribution rather than a literature
summary: the [12]–[15] lineage stops short of *implemented, constraint-aware routing*. Onuiri et
al. [12] centralize data behind a web UI but perform no route optimization; LOCUS [13] is a
recommendation-only client–server system; Tsaih et al.'s [14] seven-layer model and
Swanepoel's [15] reference architecture describe layered separation conceptually but ship no
routing engine. VOYO extends this lineage by pairing its curated database with a self-hosted
Valhalla + VROOM stack (§3.5.1) — the concrete layer that turns verified POIs into feasible,
hard-constraint-aware itineraries. This is also where VOYO most directly answers TravelPlanner's
[4] call for ground-truth, feasibility-checked itinerary evaluation, and where it differs most
concretely from the accessibility/engagement findings of [8]–[11]: those works establish *what*
makes smart-tourism tech satisfying, while VOYO implements a *specific, constraint-aware*
routing substrate that operationalizes it.

## 2.4 Note on the reference count

The corpus remains the PDF's 15 works; no new citations were added, in keeping with the
"prefer extending the existing 15 over scattering new ones" rule. All 15 are verified at HIGH
confidence in `thesis/references.bib`.
