# Chapter 1 — Introduction

> Maps to PDF Chapter 1. Drafted by the orchestrator (thesis-author async agents died with the
> systemic async-runner failures on this Windows/mingw install; the orchestrator holds all
> verified evidence + references in context and writes directly). Every quantitative claim below
> traces to `thesis/evidence/**`; every literature claim to `thesis/references.bib`.

## 1.1 Context and Motivation

Egypt is one of the world's most-visited destinations — yet foreign travellers consistently
report a fragmented, low-trust information environment. The practical questions a visitor most
needs answered (Is this site genuinely worth the detour? What does the ticket actually cost?
When is it open? Is this a tourist trap?) are precisely the ones that generic search results
and monolithic chatbots answer least reliably. The result is a "critical information gap" that
leaves visitors vulnerable to inflated prices, logistical dead-ends, and missed experiences —
and the smart-tourism literature shows this gap is retention-critical, not merely convenient:
Pai et al. [8] find that accessibility of verified information is the strongest driver of
smart-tourism satisfaction (β=0.285, N=527), which in turn drives revisit intention, and Pang
et al. [11] find that perceived information invasion significantly erodes chatbot stickiness
(N=735).

Generative AI looks, at first glance, like the natural solution: a single conversational agent
that plans a trip, answers cultural questions, and reasons about budgets and timings. In
practice, the opposite has happened. When a Large Language Model (LLM) is asked to plan travel
unsupervised, its stochasticity becomes a liability: it invents transit connections that do not
exist, states opening hours it cannot verify, and produces itineraries that are textually
fluent but logistically infeasible. This is the well-documented *hallucination* failure of
monolithic LLMs in fact-sensitive domains [1], and it is acute in tourism precisely because
the hard data — prices, hours, coordinates, distances — is local, volatile, and not reliably
present in a model's training corpus.

## 1.2 Problem Statement

This thesis addresses a single, concrete question: **how do you build a travel-planning AI that
a visitor can trust?** Trust here is not a vague property; it decomposes into three testable
requirements:

1. **Grounding.** Every factual claim the system makes (a ticket price, a site's location, an
   opening hour) must trace to a verified data record, not to the model's parametric memory.
2. **Constraint awareness.** When the system plans an itinerary, the plan must respect hard
   constraints — budgets, operating windows, travel times — rather than merely *sounding*
   coherent.
3. **Honest scope.** The system must disclose, not hide, what it cannot yet do.

A monolithic LLM satisfies none of these reliably. A naive retrieval-augmented wrapper satisfies
the first only weakly and the second not at all.

## 1.3 Approach — a Compound Agentic Architecture

VOYO adopts the architectural shift argued by Zaharia et al. [1]: state-of-the-art behaviour in
complex domains is achieved by *engineering compound systems* — orchestrating interacting
components (agents, retrievers, deterministic tools, and verified data) — rather than by scaling
a single model. Concretely, VOYO adopts Wang et al.'s [2] Profile/Memory/Planning/Action agent
blueprint and the conversational-vs-executor role separation AutoGen [3] argues reduces
multi-step error. VOYO is built as a four-layer compound agentic system (Figure 3.1):

- **Presentation** — a Flutter mobile client (chat, interactive map, itinerary timeline).
- **Gateway** — a FastAPI async backend with Supabase Auth, exposing the agent, recommendation,
  routing, and itinerary endpoints.
- **Agentic Orchestration** — CLEO, a ReAct conversational agent (Groq-hosted Llama 3) with a
  suite of deterministic tools, *forced* to ground itinerary answers in the database; a
  deterministic seven-dimension recommendation engine; and an itinerary curate→optimize pipeline.
- **Ground-Truth Data** — a Supabase PostgreSQL store of 255 curated, deduplicated Egyptian
  points of interest (POIs), enriched via Wikimedia and Google Places.

The guiding principle is a *curation–optimization split*: the LLM reasons conversationally and
selects candidate POIs, but all factual data and all hard-constraint reasoning are delegated to
verified tools and deterministic solvers. The agent is never permitted to guess volatile data.

## 1.4 Contributions

This thesis makes the following contributions, each grounded in the implemented system and its
evidence:

1. **A compound agentic architecture for grounded travel planning.** A four-layer system in
   which a conversational ReAct agent and a deterministic recommendation/optimization layer
   share a single verified-data substrate. (Ch 3; Figure 3.1.)

2. **A native tool-call recovery parser plus a force-tool grounding fix.** CLEO recovers from
   the host model's intermittent native-format tool-call leaks, and is *forced* to call the
   database tool on itinerary and POI queries — eliminating the memory-only answers that caused
   hallucinated places, prices, and durations. The fix is a reusable pattern for grounding any
   tool-using LLM in a verified database. (§3.4; `thesis/evidence/06-cleo-grounding.md`.)

3. **A clean, verified 255-POI database and rebuild pipeline.** The strongest single
   contribution: a self-contained pipeline (`rebuild_database.py`) that diagnosed and fixed five
   independent silent-failure modes in the inherited enrichment code, switched imagery to
   permanent key-free Wikimedia URLs, and produced 255 deduplicated POIs across eight regions —
   including permanent imagery on all six most-famous sites that previously had none.
   (Ch 6; `thesis/evidence/05-db-completeness.json`.)

4. **A deterministic recommendation engine with measured sub-millisecond performance.** A
   seven-dimension weighted scorer with greedy diversification, benchmarked at a median
   **0.75 ms** for full recommendation over the POI set against a 200 ms target — roughly
   267× headroom — as part of a 99-test, 100%-pass core suite. (Ch 4; Tables 4.1, 4.4;
   `thesis/evidence/02-latency.json`, `01-test-results.json`.)

5. **An honest evaluation.** A benchmark suite (13 latency benchmarks + 4 A/B correctness
   scenarios, 99 tests passing) together with explicit disclosure of the project's real
   limitations: Groq free-tier ceilings, the VROOM optimization step pending, Redis
   non-operational, and a regional imbalance in POI coverage. (Ch 4, Ch 5.)

## 1.5 Thesis Roadmap

- **Chapter 2 — Background** situates VOYO in the literature on compound AI systems, agentic
  architectures, tool use, and smart-tourism technology, via 15 verified works.
- **Chapter 3 — Methodology** details the four-layer architecture and the actual implementation
  (real file paths and function names), correcting the aspirational claims of earlier drafts.
- **Chapter 4 — Results and Discussion** presents the benchmark results, the A/B correctness
  evidence, the database-completeness audit, and an honest discussion of limitations.
- **Chapter 5 — Conclusion** recaps the contributions, restates the limitations, and proposes
  concrete future work.
- **Chapter 6 — The POI Data Pipeline** is the standalone account of the strongest contribution:
  the rebuild, the five bugs it fixed, the decisions behind it, and the honest gaps that remain.

The recurrent thread is the title of the thesis: *orchestrating trust*. Each chapter is, in its
own way, an answer to the question of how a compound system earns — and keeps — a visitor's trust.
