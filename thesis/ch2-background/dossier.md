# §2.2 / §2.3 — Background & Literature Review — CITED ARGUMENT OUTLINE

> **Section thesis sentence (the spine every claim serves):** *VOYO couples an LLM (CLEO —
> for intent parsing and personalization only) to deterministic optimization engines
> (Valhalla, VROOM, OSRM — for reachability, routing, isochrones, distance matrices, and
> VRPTW-grade feasibility / time-window optimization), because an LLM alone cannot reliably
> plan: it lacks optimization capability and hallucinates geography, prices, and constraints.*
> [citation: criteria §1 → thesis-criteria.md §1] [citation: N1 → Q3 (LLMs "lack the
> optimization capabilities required for planning tasks")].
>
> This dossier is an **evidence packet for the human thesis writer, NOT final prose.** Each
> numbered claim is followed by its citation id → locator (resolvable in
> `thesis/citations/INDEX.md`) and a one-line "phrase it as" note. Verbatim text the writer
> should copy lives in `evidence-packet.md`; figures/tables in `figures-spec.md`.

## Tier map for this dossier (admissibility per criteria §2)

- **Tier A — load-bearing (may ground core contribution claims):** N1 ItiNera; N4 PyVRP;
  OSRM-PAPER; the agentic-architecture set 01–07 (Tier A *within* T1).
- **Tier B — supporting (reinforce only; cannot carry a core claim alone):** N5 AgentTravel
  (label "workshop paper"); 08–15.
- **Tier C — software-infrastructure (cite as software; NEVER as a paper):** S-VROOM,
  S-VALHALLA, S-OSRM.
- **Tier D — preprint-only (footnote only, explicitly labelled "arXiv preprint, not
  peer-reviewed"; never core evidence):** N2 TRIP-PAL, N3 TravelAgent.

---

# §2.2.A — T1: LLM Agents & Tool-Use

> **Theme positioning sentence (must close T1):** *VOYO is a compound system; CLEO is its
> conversational/agent layer, deliberately coupled to verified deterministic tools rather
> than trusted with feasibility.*

**T1-1 — The "compound systems, not monolithic models" thesis.** State-of-the-art AI results
increasingly come from "compound systems with multiple interacting components, not just
monolithic models," and this paradigm is expected to remain leading "even as models improve."
[citation: 01 → Q2,Q3,Q5]. **Phrase as:** the section's opening framing line; pair 01 (BAIR
blog) with the peer-reviewed AutoGen [03] for empirical support, since 01 is a blog post.
[citation: criteria §2 → Tier A-within-theme, supporting].

**T1-2 — Definition of a Compound AI System.** A compound AI system is "a system that tackles
AI tasks using multiple interacting components, including multiple calls to models, retrievers,
or external tools." [citation: 01 → Q1]. **Phrase as:** the canonical definition; use verbatim.

**T1-3 — The canonical agent blueprint (Profile / Memory / Planning / Action).** The Wang et
al. survey standardizes the four-module architecture (profiling, memory, planning, action),
in which the first three modules collectively influence the action module.
[citation: 02 → Q1,Q2,Q3,Q4]. **Phrase as:** CLEO's modules map onto this blueprint (intent
≈ planning+profiling; preference memory ≈ memory; deterministic-engine calls ≈ action).

**T1-4 — Role separation via multi-agent conversation (AutoGen).** AutoGen agents are
"conversable, customizable, and can be based on LLMs, tools, humans, or even a combination
of them," and multi-agent conversation is the programming substrate.
[citation: 03 → Q1,Q2,Q3,Q4]. **Phrase as:** justifies VOYO's separation of CLEO
(conversational LLM) from the deterministic engines (the "tool/proxy" side); reduces error
propagation by not letting the LLM author feasibility logic.

**T1-5 — Self-correction via verbal reinforcement (Reflexion).** Reflexion introduces an
Actor/Evaluator/Self-Reflection loop where an agent writes verbal reflections into episodic
memory and retries. ⚠️ **Cite the verified figures ONLY:** "91% pass@1 accuracy on the
HumanEval coding benchmark" and on ALFWorld "completing 130 out of 134 tasks" using "the
simple heuristic to detect hallucinations and inefficient planning." **DO NOT cite any
"+22% ALFWorld" figure — that stat is fabricated and absent from the paper.**
[citation: 05 → Q1,Q2,Q3,Q4; criteria §7 (no-fabrication)]. **Phrase as:** motivates CLEO's
self-check pass + persistent memory; explicitly say "130/134 tasks" not "+22%".

**T1-6 — Tool-coupled reasoning reduces hallucination (Gorilla).** A fine-tuned Gorilla model
surpasses GPT-4 on writing API calls, with retrieval "demonstrates a strong capability" and
reduces hallucination. Verified zero-shot TorchHub results: Gorilla 59.13% accuracy / 6.98%
hallucination vs GPT-4 38.70% / 36.55%. [citation: 06 → Q1,Q4,Q5]. **Phrase as:** motivates
VOYO's tight coupling of CLEO to verified tool functions over the curated 310-POI substrate.

**T1-7 — Self-supervised tool-use foundation (Toolformer).** Toolformer learns to insert API
calls in a self-supervised way by filtering calls that reduce a perplexity loss; on a 6.7B
GPT-J base it outperforms much larger GPT-3. Verified per-benchmark gains (Tables 3/4/7):
SQuAD 17.8→33.8; ASDiv 7.5→40.4; Dateset 3.9→27.3. [citation: 07 → Q1,Q2,Q3,Q4,Q5,Q6].
**Phrase as:** the foundation citation for VOYO's tool-execution environment.

**T1 positioning (close the theme).** CLEO = the conversational/agent layer of a compound
system [01,03], architected per the canonical four-module blueprint [02], grounded by
retrieval [06] and self-correction [05] over a verified substrate; it is coupled to — never
substituted for — deterministic tools [07]. This is exactly the "system, not model" framing
the thesis defends. [citation: 01 → Q2; criteria §1 → thesis sentence].

---

# §2.2.B — T2: Recommendation & Itinerary Planning (THE CRUX)

> **Theme positioning sentence (must close T2):** *VOYO's curate→optimize stage is ItiNera's
> core insight — that an LLM must be paired with a spatial-optimization solver because it
> lacks optimization capability — instantiated for Egyptian tourism with VRPTW-grade
> feasibility.*

**T2-1 — The closest precedent (Tier A, load-bearing).** ItiNera defines the Open-domain
Urban Itinerary Planning (OUIP) task and proposes a system that "integrates spatial
optimization with large language models." [citation: N1 → Q1]. **Phrase as:** the section's
single most important citation; call ItiNera the closest prior art.

**T2-2 — ItiNera's motivation = the thesis's motivation.** ItiNera explicitly states that
"(1) Pure LLMs cannot refer to specific POI lists, resulting in outdated or hallucinated POIs.
(2) LLMs lack the optimization capabilities required for planning tasks, leading to suboptimal
itineraries. Consequently, LLM-generated itineraries can be circuitous, lack detail, and
include impractical information." [citation: N1 → Q3]. **Phrase as:** quote verbatim — this
is the academic source for the thesis's "LLM-alone cannot plan" motivation.

**T2-3 — ItiNera's architecture (5 LLM-assisted modules + a spatial optimizer).** ItiNera
comprises five LLM-assisted modules (UPC, RD, PPR, **CSO**, IG), of which Cluster-aware
Spatial Optimization (CSO) "solv[es] a hierarchical traveling salesman problem." ItiNera's
dataset: "1233 top-rated urban itineraries and 7578 POIs." [citation: N1 → Q2,Q4,Q7].
**Phrase as:** the structural precedent VOYO's curate→optimize stage descends from.

**T2-4 — Ablation evidence that the solver is load-bearing (Tier A).** Removing CSO worsens
route quality: Average Margin rises from **86.0 (full)** to **242.8 (w/o CSO)** on the
Shanghai dataset. [citation: N1 → Q5, Table 2 p.6]. **Phrase as:** the *quantitative*
argument for why a separate optimization module is necessary — without it, route detour
roughly triples.

**T2-5 — ItiNera was deployed and evaluated by humans (Tier A).** ItiNera ran as a deployed
system, evaluated by "464 regular users of our system (User) and 33 experienced travel
assistants from our partnered travel agency (Expert)." [citation: N1 → Q6]. **Phrase as:**
the precedent is not a toy benchmark — it shipped.

**T2-6 — LLM planning without tools/constraints fails (peer-reviewed ICML 2024 benchmark).**
TravelPlanner finds that "current language agents are not yet capable of handling such complex
planning tasks — even GPT-4 only achieves a success rate of 0.6%," because agents "struggle
to stay on task, use the right tools to collect information [...], or keep track of multiple
constraints." [citation: 04 → Q1,Q2,Q3]. **Phrase as:** independent ICML-grade evidence that
monolithic LLMs cannot plan under constraints.

**T2-7 — AgentTravel: the most architecturally congruent comparand (Tier B, label as
workshop).** AgentTravel is "a unified framework that combines knowledge-grounded modeling,
agentic reasoning, and multi-perspective evaluation" — three components: TravelLLM (domain
adaptation), TravelAgent (online planner with retrieval + structured itinerary memory), and
TravelBench (KnowEval + TripEval). [citation: N5 → Q1,Q3,Q4,Q5]. **Phrase as:** label as
"NORA / CEUR workshop paper" (per criteria §2); use for eval-design comparand only.

**T2-8 — AgentTravel's spatial-reasoning failure framing matches VOYO's thesis.** AgentTravel
motivates its design by noting that "current LLMs exhibit limited spatial reasoning
capabilities — they often fail to accurately account for geographic distances, travel times,
or accessibility constraints when generating feasible itineraries." [citation: N5 → Q2].
**Phrase as:** corroborates N1's Q3 motivation from an independent group.

**T2-9 — Tier-D footnotes (LABELLED preprints; non-core, optional).** Two arXiv preprints
reach the same conclusion and may be cited as labelled footnotes only: (a) TRIP-PAL — a
hybrid LLM + PDDL planner that reports GPT-4 returning only "14 valid plans out of the 100
tasks" [citation: N2 → Q6]; (b) TravelAgent (Chen et al.) — a four-module system (NOT five:
"Tool-usage, Recommendation, Planning, and Memory Module") scoring 9.56/8.87/8.44 vs a GPT-4
agent's 8.16/6.25/4.31 on Rationality/Comprehensiveness/Personalization
[citation: N3 → Q1,Q6]. **Phrase as:** *explicitly* "arXiv preprint, not peer-reviewed";
prefer ItiNera (Tier A) for the same point per criteria §2.

**T2 positioning (close the crux).** VOYO's curate→optimize stage = ItiNera's CSO insight
[N1], reaffirmed by TravelPlanner's near-zero LLM-alone success [04] and corroborated by
AgentTravel's spatial-reasoning-failure framing [N5]; VOYO's contribution is to instantiate
this for a verified Egyptian substrate with **VRPTW-grade** (not hierarchical-TSP) feasibility
and dual Egyptian/foreigner pricing — see the Research-Gap statement below.

---

# §2.2.C — T3: Grounding / RAG / Hallucination

> **Theme positioning sentence (must close T3):** *VOYO grounds every POI, price, and route
> in deterministic sources; the LLM is never trusted to invent geography, prices, or
> constraints.*

**T3-1 — Pure LLMs hallucinate POIs (Tier A).** ItiNera Q3 (verbatim): "Pure LLMs cannot
refer to specific POI lists, resulting in outdated or hallucinated POIs." [citation: N1 →
Q3]. **Phrase as:** the load-bearing citation for why VOYO forces CLEO to ground every POI
in the curated database.

**T3-2 — Pure LLMs cannot plan/optimize (Tier A).** ItiNera Q3 (verbatim): "LLMs lack the
optimization capabilities required for planning tasks, leading to suboptimal itineraries."
[citation: N1 → Q3]. **Phrase as:** second load-bearing citation; ties T3 to T2/§2.3.

**T3-3 — TravelPlanner: constraint-tracking failure.** "Language agents struggle to stay on
task, use the right tools to collect information [...], or keep track of multiple
constraints." GPT-4 achieves only **0.6%** success on real-world travel planning with
commonsense + hard constraints. [citation: 04 → Q1,Q2,Q3]. **Phrase as:** peer-reviewed
evidence that un-grounded LLM planning fails on constraints.

**T3-4 — Reflexion: hallucination detection as a self-correction signal.** Reflexion detects
"hallucinations and inefficient planning" via verbal self-reflection; on ALFWorld it reached
"130 out of 134 tasks." (⚠️ Never cite a "+22% ALFWorld" stat — it is fabricated; criteria §7.)
[citation: 05 → Q2,Q3; criteria §7]. **Phrase as:** motivates CLEO's self-check pass + the
force-tool grounding fix.

**T3-5 — Retrieval reduces hallucination for tool use.** Gorilla: integrating "the retrieval
system with Gorilla demonstrates the potential for LLMs to use tools more accurately," and
hallucination drops from 36.55% (GPT-4) to 6.98% (Gorilla) at zero-shot TorchHub.
[citation: 06 → Q4,Q5]. **Phrase as:** grounds VOYO's retriever-grounded tool selection
(coupled to the curated 310-POI substrate).

**T3 positioning.** The LLM must be coupled to deterministic tools + a verified substrate
because it hallucinates POIs [N1 Q3], cannot optimize [N1 Q3], loses constraints under
multi-step planning [04], and only retrieval + self-correction reduce hallucination [05,06].
VOYO's force-tool grounding (per-iteration `force_tool` policy + slimmed tool results +
name→ID resolution) is the concrete operationalization of this entire body of evidence.
[citation: N1 → Q3; 04 → Q2; 05 → Q2; 06 → Q5; criteria §1 → thesis sentence].

---

# §2.2.D — T4: Tourism Domain Systems

> **Theme positioning sentence (must close T4):** *VOYO extends this lineage with a
> deterministic core and a verified 310-POI Egyptian substrate (with dual Egyptian/foreigner
> pricing) — moving the tourism-IT literature from content/recommendation systems to
> constraint-aware, optimization-grounded itinerary generation.*

**T4-1 — What tourists value in smart-tourism tech (UTAUT + PLS-SEM, Tier B).** Pai et al.
survey N=527 Macau tourists; STT treated as a second-order construct (informativeness,
accessibility, interactivity, personalization, security). ⚠️ **Verified finding (cite ONLY
this):** "accessibility was the most significant variable (path coefficient is 0.285, T value
is 35.093)." ⚠️ **DO NOT cite "0.69" as a structural β** — that figure is the ACC↔INT
*discriminant-validity* correlation in Table 3, NOT a structural STT→satisfaction coefficient.
[citation: 08 → Q1,Q2,Q3,Q4,Q5,Q6; criteria §7 / Tier-B residual flag]. **Phrase as:** cite
the accessibility path coefficient (0.285) as the quantitative anchor; pair with Q4's
STT→satisfaction→(happiness, revisit) chain.

**T4-2 — Adaptive UI/UX and engagement (Tier B).** Liu et al. design a context-aware
adaptation engine (with a Self-Organizing Map clustering the user-profile module). ⚠️
**Verified finding (cite ONLY this):** "personalized interface generation resulted in a 22%
higher task completion rate than the next best adaptive solution." ⚠️ **DO NOT cite "+35%
feature discovery"** — that stat is not in the paper (35% in the paper is a demographic
age-group percentage, and "feature discovery" is only a table-header label). [citation: 09 →
Q1,Q2,Q3,Q5,Q6; criteria §7 / Tier-B residual flag]. **Phrase as:** grounds VOYO's adaptive
front-end; cite the SOM engine + the 22% task-completion gain.

**T4-3 — AI features influence engagement *through* satisfaction, not directly (Tier B).**
Christina et al., N=204 Tokopedia users, PLS-SEM with SmartPLS 4.0 under UTAUT: "chatbot
interaction and recommendation systems do not directly strengthen engagement, but both
significantly improve satisfaction, which in turn enhances engagement. Satisfaction also
mediates [...]." [citation: 10 → Q1,Q2,Q3,Q4]. **Phrase as:** defends VOYO's CLEO (trust/
satisfaction) ↔ deterministic-engine (utility) separation — functional capability alone is
insufficient; trust mediates engagement.

**T4-4 — Chatbot stickiness and trust/privacy (Tier B).** Pang et al., N=735 Chinese
university students, SEM integrating U&G + TAM + ECM: four motivational categories
(utilitarian, hedonic, technology, social) influence user attitude; "privacy invasion exerts
a negative impact on user attitude." [citation: 11 → Q1,Q2,Q3,Q4,Q5]. ⚠️ The specific
β=0.326 "tech motivation strongest driver" figure is NOT in the abstract (lives in
paywalled tables); **do not cite β=0.326**; cite N=735 + the qualitative four-motivation
finding + the privacy-negative finding as the verified result. [citation: 11 → Q1–Q5; Tier-B
residual flag in quotes.md]. **Phrase as:** motivates VOYO's grounded-data + privacy-aware
design.

**T4-5 — Early centralized tourism-IT (Tier B).** Onuiri et al.'s ITMS, for Nigeria, uses
Rational Unified Process + MySQL/HTML/PHP, surfaces "50 tourist locations," and "act[s]
intelligently by using hybrid recommendation technique to recommend tourist locations based
on their preference." [citation: 12 → Q1,Q2,Q3,Q4,Q5,Q6]. **Phrase as:** the early
centralized-tourism-DB lineage VOYO descends from — but note it does no route optimization.

**T4-6 — Mobile recommendation baseline (Tier B).** AlSaeed's LOCUS: client–server mobile
tourism app, item-item + user-user collaborative filtering, **SUS = 87.75** (threshold 68),
**5.4 s average task time**, user-acceptance testing **N=10**. [citation: 13 → Q1,Q3,Q4,Q5].
**Phrase as:** the concrete mobile+recommender baseline for VOYO's recommendation design.

**T4-7 — Layered architecture justification (Tier B).** Tsaih et al.'s "modularized, loosely
coupled, seven-layered AI tech-stack model" (AI infrastructure → AI solution) and its four
layering principles (categorize similar functions per layer; minimize cross-boundary
interactions; unique-task layers; industry-proven boundaries). Smart-tourism is the paper's
empirical case: "Tourism [...] has urgently sought digital transformation opportunities
[...] by activating an AI-driven smart tourism strategy." [citation: 14 → Q1,Q2,Q3,Q4,Q5].
**Phrase as:** the architectural justification for VOYO's layered separation; cite Q2+Q3 for
the boundary-design principles; honestly cite Q5 as "consistent with / informed by" (the
model is conceptual, not prescriptive).

**T4-8 — Layered service-oriented reference architecture (Tier B).** Swanepoel's M.Eng
(Industrial Engineering) thesis: trip planning is "one of the most important aspects of a
tourist's journey"; with the abundance of travel websites, "the task of creating an itinerary
can be daunting." Develops a layered service-oriented reference architecture + web-based
demonstrator. [citation: 15 → Q1,Q2,Q3,Q4]. **Phrase as:** the architecture-lineage citation;
note it is a Master's thesis (per the bibliographic correction in 15's quotes.md).

**T4 positioning.** This lineage establishes *what* tourists value (accessibility [08],
adaptation [09], trust-mediated engagement [10,11]) and *how* tourism-IT has been
architected (centralized DB [12], CF recommenders [13], layered stacks [14,15]). VOYO extends
it with a deterministic optimization core over a verified **310-POI** Egyptian substrate
(criteria §4 — POI count = 310; the prior draft's 255 is stale), with dual Egyptian/foreigner
pricing (58 POIs enriched, per criteria §4) — moving tourism-IT from recommendation to
constraint-aware itinerary generation.

---

# §2.3 — The Route-Optimization Crux (the contribution's technical anchor)

> **§2.3 thesis sentence:** *VOYO frames itinerary optimization as a VRP with time windows
> and delegates it to a deterministic solver (VROOM), routing/matrix infrastructure to OSRM/
> Valhalla-class engines, because (a) this OR family is well-defined and near-optimally
> solvable, (b) the LLM provably lacks the optimization capability for it, and (c) no prior
> system couples an LLM intent layer with VRPTW-grade optimization over a verified Egyptian
> substrate.*

**§2.3-1 — The motivation: LLMs cannot plan (Tier A).** Per ItiNera Q3: "LLMs lack the
optimization capabilities required for planning tasks, leading to suboptimal itineraries."
The CSO ablation quantifies this — removing the optimizer triples the route detour (Average
Margin 86.0 → 242.8). [citation: N1 → Q3,Q5]. **Phrase as:** the §2.3 opener; the same Tier-A
quote grounds the contribution's motivation.

**§2.3-2 — VRPTW is a well-defined, benchmarked OR problem family (Tier A).** PyVRP defines
the VRPTW: each customer has a service time, earliest arrival, and latest arrival; "A vehicle
can wait at customer i when arriving too early, but cannot arrive after [the latest time]."
This is exactly the constraint structure of a tourist day (POIs with opening windows, fixed
durations). [citation: N4 → Q4]. **Phrase as:** the formal definition justifies *why* VOYO
frames itinerary optimization as a VRPTW.

**§2.3-3 — VRPTW is solved near-optimally by hybrid genetic search (Tier A).** PyVRP's HGS
"combines a genetic algorithm with a local search algorithm," with time windows and capacities
as soft constraints. Local search is 80–90% of runtime and in C++. Benchmarks: mean gap
**0.22%** (CVRP, X instances), **0.40%** (VRPTW, Homberger–Gehring 1000-customer); the
implementation "ranked 1st in the 2021 DIMACS VRPTW challenge" and 1st on the EURO-meets-
NeurIPS 2022 static variant. [citation: N4 → Q1,Q2,Q3,Q5]. **Phrase as:** grounds that a
metaheuristic solver is the appropriate (near-optimal, fast) choice for VOYO's optimize stage.

**§2.3-4 — VROOM characterized academically (Tier A) AND as software (Tier C — never as a
paper).** PyVRP's Related Projects section (the single best academically-sourced sentence
about VROOM): "VROOM (Coupey et al. 2023), the Vehicle Routing Open-source Optimisation
Machine, is an open-source solver that aims to provide good solutions to real-life VRPs [...]
However, it is unable to compete with state-of-the-art algorithms and lacks documentation to
customise its underlying solver." [citation: N4 → Q6]. **No paper exists for VROOM** — the
maintainer (jcoupey) confirmed in GitHub Issue #735: "No, there is no paper associated with
the project." [citation: S-VROOM → Issue #735, 2022-07-07]. VROOM's README describes it as an
"open-source route optimization engine written in C++20 that solves complex vehicle routing
problems (VRP) in milliseconds." [citation: S-VROOM → README lines 1–11]. **Phrase as:**
honest framing — VROOM is *fast and practical* but *not* SOTA; that trade-off is acceptable
for VOYO because itinerary planning needs real-time "good-enough" routes, not provably
optimal ones. ⚠️ **Never invent a VROOM paper.**

**§2.3-5 — Routing/matrix infrastructure: the OSRM algorithm (Tier A) + tool (Tier C).**
Luxen & Vetter demonstrate "real-time and exact shortest path computation on continental sized
networks with millions of street segments." Contraction Hierarchies give "a very convenient
trade-off between preprocessing and query time. Road networks of continental size can be
preprocessed within a matter of minutes and queries run in the order of about a hundred
microseconds." Result: "routing is not a bottleneck anymore, and other components become
obstacles" — because Dijkstra's seminal algorithm "does not scale to large graphs."
[citation: OSRM-PAPER → Q1,Q5,Q6,Q7]. The running tool exposes two pipelines (CH and MLD);
its `/table` service "computes the duration of the fastest route between all pairs of
supplied coordinates," returning "the durations or distances [...] in seconds and [...] meters"
— i.e., *fastest-route* distance, not straight-line. [citation: S-OSRM → /table-service
section; Q2-supporting README]. **Phrase as:** pair OSRM-PAPER (the algorithm) with S-OSRM
(the running tool); emphasize the honesty point that matrices are *fastest-route* distance.

**§2.3-6 — Valhalla: isochrones + matrix (Tier C — software only).** Valhalla's isochrone
service "computes areas that are reachable within specified time intervals from a location,
and returns the reachable regions as contours of polygons or lines." [citation: S-VALHALLA →
Isochrone API overview]. **Phrase as:** cite as software only; pair with S-OSRM for the
matrix service that feeds VROOM.

**§2.3-7 — The closest precedent: ItiNera couples an LLM to a spatial optimizer (Tier A).**
ItiNera "integrates spatial optimization with large language models," with CSO solving a
"hierarchical traveling salesman problem." [citation: N1 → Q1,Q4]. **Phrase as:** VOYO's
contribution is the same LLM-coupled-to-solver pattern, instantiated for Egyptian tourism
with a VRPTW-grade (not TSP) optimizer — see the Research-Gap statement.

**§2.3-8 — Eval-design comparand (Tier B, label as workshop).** AgentTravel's TravelBench
benchmark (KnowEval for factual/spatial knowledge; TripEval for "plan feasibility,
personalization, and constraint satisfaction") is the methodological template for VOYO's
evaluation chapter. [citation: N5 → Q5]. **Phrase as:** cite as "NORA / CEUR workshop
paper"; use only as eval-design comparand, never as architecture precedent.

---

# Research-Gap Statement (the VOYO-vs-ItiNera delta)

> **Required by criteria §3 ("Research gap statement (verbatim-derivable): no prior system
> combines an LLM intent layer with VRPTW-grade deterministic optimization over a verified,
> region-balanced Egyptian POI substrate with dual (Egyptian/foreigner) pricing").**

**GAP-1 — Substrate gap.** ItiNera's substrate is "1233 top-rated urban itineraries and 7578
POIs" for urban China. [citation: N1 → Q7]. VOYO's substrate is a verified **310-POI**
Egyptian corpus across 8 regions (criteria §4; ⚠️ evidence/05-db-completeness.json still
reports the stale 255 count and must be regenerated — see figures-spec.md). The substrate
*country and region balance* differ; VOYO cannot reuse ItiNera's data.

**GAP-2 — Optimizer-class gap.** ItiNera's CSO solves a **hierarchical TSP** to *order* POIs
[citation: N1 → Q4]; it does not solve a VRPTW and does not model POI opening windows or
service times as hard time-window constraints. VOYO frames the same problem as a **VRPTW**
and delegates to VROOM [citation: N4 → Q4 (VRPTW definition); S-VROOM → README], giving
*time-window feasibility* (open-hours compliance) as a first-class guarantee — a capability
ItiNera does not claim.

**GAP-3 — Pricing-model gap.** No prior surveyed system (N1, N5, 12, 13, 15) models dual
Egyptian/foreigner admission pricing — VOYO enriches **58 POIs** with dual gov.eg prices
(criteria §4). **Phrase as:** state this *as a gap*, not by inventing a competitor that lacks
it; the comparison is to the surveyed corpus, and dual-pricing is absent across the corpus.

**GAP-4 — Reliability gap (peer-reviewed evidence that the LLM-alone baseline fails).** Two
Tier-A / Tier-B sources independently show the LLM-alone baseline is infeasible: ItiNera
Q3 ("LLMs lack the optimization capabilities required for planning tasks") [citation: N1 →
Q3]; TravelPlanner's "0.6%" GPT-4 success rate [citation: 04 → Q1]. ⚠️ Tier-D TRIP-PAL's
"14/100 valid GPT-4 plans" [citation: N2 → Q6] may be cited as a labelled-preprint footnote
only — never as core gap evidence.

**GAP-5 — The synthesized gap (the contribution's lit-review headline).** *No prior system
combines (i) an LLM intent layer [01,03] with (ii) VRPTW-grade deterministic optimization
[N4 → Q4] over (iii) a verified, region-balanced Egyptian POI substrate (criteria §4: 310
POIs) with (iv) dual Egyptian/foreigner pricing (criteria §4: 58 POIs).* ItiNera [N1] is the
closest precedent (it satisfies (i) + a TSP-class (ii) without time windows); VOYO's
contribution is the gap ItiNera leaves: VRPTW-grade feasibility + Egyptian substrate + dual
pricing. **Phrase as:** the closing paragraph of §2.2/§2.3; everything above builds to this
sentence.

---

## Writer's anti-fabrication checklist (from criteria §7 + quotes.md flags)

1. **POI count = 310** everywhere (criteria §4); the prior draft's 255 is stale and must not
   reappear. Flag the stale `evidence/05-db-completeness.json` (still 255) for regeneration
   in figures-spec.md.
2. **Never cite "+22% ALFWorld"** — fabricated; the verified Reflexion figures are "130 out
   of 134 tasks" + "91% pass@1 HumanEval" [citation: 05 → Q1,Q2; criteria §7].
3. **Never cite "+35% feature discovery"** for Liu — not in the paper; cite only the verified
   "+22% task completion" [citation: 09 → Q6; criteria §7].
4. **Never cite Pai "0.69" as a structural β** — it is a discriminant-validity correlation;
   cite only the verified accessibility path coefficient 0.285 [citation: 08 → Q5].
5. **Never cite Pang "β=0.326"** — not in the abstract; cite only N=735 + the qualitative
   four-motivation finding [citation: 11 → Q1–Q5].
6. **TravelAgent (Chen et al.) is FOUR modules, not five** [citation: N3 → Q1]; cite as Tier-D
   preprint only.
7. **No paper exists for VROOM** — cite S-VROOM as software; pair with N4 Q6 for the academic
   characterization [citation: S-VROOM → Issue #735].
8. **OSRM is BOTH a Tier-A paper (OSRM-PAPER) AND Tier-C software (S-OSRM)** — never conflate
   them. The Q5/Q6/Q7 body quotes are now quotable (FULL-TEXT VERIFIED 2026-06-17).
