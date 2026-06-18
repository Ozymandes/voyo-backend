# §2.2 / §2.3 — Evidence Packet (verbatim quotes + numbers for the writer)

> Every entry is **copied verbatim** from the cited source.md / quotes.md file in
> `thesis/citations/`. Each entry records its locator. The writer copies directly from this
> file. **Nothing here is paraphrased or invented.** All flagged-for-correction stats
> (Reflexion +22%, Liu +35%, Pai 0.69-as-β, Pang β=0.326) are explicitly ABSENT and labelled
> as such below.

## Tier-A citations

### N1 — ItiNera (Tang et al., EMNLP 2024 Industry + KDD UrbComp 2024 Best Paper)
- arXiv:2402.07204, v5 (9 Jan 2025), 20pp.
- **Q1 — system definition (Abstract, p.1):** "we introduce the novel task of Open-domain
  Urban Itinerary Planning (OUIP), which generates personalized urban itineraries from user
  requests in natural language. We then present ITINERA, an OUIP system that integrates
  spatial optimization with large language models to provide customized urban itineraries
  based on user needs. This involves decomposing user requests, selecting candidate points of
  interest (POIs), ordering the POIs based on cluster-aware spatial optimization, and
  generating the itinerary."
- **Q2 — five-module architecture (§1, p.1–2):** "ITINERA comprises five LLM-assisted
  modules: User-owned POI Database Construction (UPC), Request Decomposition (RD),
  Preference-aware POI Retrieval (PPR), Cluster-aware Spatial Optimization (CSO), and
  Itinerary Generation (IG), to deliver personalized [...]"
- **Q3 — motivation (§1, p.1):** "their limitations in itinerary planning are evident [...]
  (1) Pure LLMs cannot refer to specific POI lists, resulting in outdated or hallucinated
  POIs. (2) LLMs lack the optimization capabilities required for planning tasks, leading to
  suboptimal itineraries. Consequently, LLM-generated itineraries can be circuitous, lack
  detail, and include impractical information." *(load-bearing quote for the thesis
  motivation — T2-2, T3-1, T3-2, §2.3-1, GAP-4)*
- **Q4 — CSO as hierarchical TSP (§3.5, p.4):** "we compute spatial clusters of the retrieved
  POIs and select candidates based on proximity and matching scores, addressing cluster-aware
  spatial optimization by solving a hierarchical traveling salesman problem [...], a common
  and fundamental spatial reasoning task [...]."
- **Q5 — ablation, removing CSO destroys route quality (Table 2, p.6):** "Removing the CSO
  module worsens the Average Margin and Overlaps but improves Recall Rate, POI Quality, and
  Match, showing the full model balances alignment with spatial ability."
  - Verbatim table rows: **"ITINERA (full) ✓ ✓ ✓ ✓ ✓ 31.4 86.0 0.42 69.8 64.6 72.0"** vs
    **"ITINERA w/o CSO ✓ ✓ ✓ × ✓ 32.8 242.8 1.04 72.1 60.2 74.2"** — i.e., Average Margin
    **86.0 (full) → 242.8 (w/o CSO)**.
- **Q6 — deployed system (§4.5, p.7):** "Our deployed system is currently accessible to a
  select group of users recommended by our partnered travel agency. To verify the
  effectiveness of our system in real-world scenarios, we conduct human evaluations. [...] We
  invite 464 regular users of our system (User) and 33 experienced travel assistants from our
  partnered travel agency (Expert) to compare [...]"
- **Q7 — dataset scale (§4.1, p.5):** "In total, the dataset covers 1233 top-rated urban
  itineraries and 7578 POIs."
- Venue provenance (GitHub README, verbatim): "Published in the EMNLP 2024 Industry Track
  Proceedings / Received Best Paper Award at KDD Urban Computing Workshop (UrbComp) 2024."

### N4 — PyVRP (Wouda, Lan, Kool; INFORMS Journal on Computing)
- arXiv:2403.13795 (DOI 10.1287/ijoc.2023.0055).
- **Q1 — Abstract:** "We introduce PyVRP, a Python package that implements hybrid genetic
  search in a state-of-the-art vehicle routing problem (VRP) solver. The package is designed
  for the VRP with time windows (VRPTW) [...] PyVRP is a polished implementation of the
  algorithm that ranked 1st in the 2021 DIMACS VRPTW challenge and, after improvements, ranked
  1st on the static variant of the EURO meets NeurIPS 2022 vehicle routing competition."
- **Q2 — HGS = genetic + local search (§4.1):** "HGS is a hybrid algorithm that combines a
  genetic algorithm with a local search algorithm. It maintains a population with feasible
  and infeasible solutions. [...] in every iteration, two parents are selected from the
  population, and combined using a crossover operator to create a new offspring solution.
  [...] In each iteration, the new offspring solution is improved using local search, which
  considers time windows and capacities as soft constraints by penalising violations."
- **Q3 — runtime profile (§4.3):** "This improvement procedure is typically the most
  expensive part of the HGS algorithm. Software profiling suggests that in PyVRP it accounts
  for 80-90% of the runtime, which is why the local search is implemented in C++."
- **Q4 — VRPTW definition (§2.2):** "For the VRPTW, each customer additionally has a service
  time [...], an earliest arrival time [...] and latest arrival time [...] in between which
  service should start. A vehicle can wait at customer i when arriving too early, but cannot
  arrive after [the latest time]."
- **Q5 — benchmark gaps (§6):** "PyVRP obtains a mean gap of 0.22% and a gap of the mean of
  0.27% on the solved instances." (CVRP, X); "PyVRP achieves a mean gap of 0.40% and gap of
  mean of 0.46% on the VRPTW benchmark instances [...]. Furthermore, during extended runs,
  PyVRP managed to improve 27 of the 300 best known solutions of the complete Homberger and
  Gehring instances." (VRPTW).
- **Q6 — academic VROOM characterization (§3 Related projects):** "VROOM (Coupey et al.
  2023), the Vehicle Routing Open-source Optimisation Machine, is an open-source solver that
  aims to provide good solutions to real-life VRPs. In particular, it integrates well with
  open-source routing software to solve real-life VRPs within limited computation time. It
  implements many constructive heuristics and a local search algorithm in C++ and can handle
  different types of VRPs. However, it is unable to compete with state-of-the-art algorithms
  and lacks documentation to customise its underlying solver."
- **Q7 — aims (§1):** "We especially hope that PyVRP will help machine learning (ML)
  researchers interested in vehicle routing to easily build on the state-of-the-art, and move
  beyond LKH-3 [...] as the most commonly used baseline."
- **Q8 — provenance:** "Wouda NA, Lan L, Kool W (2023) PyVRP: a high-performance VRP solver
  package. URL http://dx.doi.org/10.1287/ijoc.2023.0055.cd"

### OSRM-PAPER — Luxen & Vetter (ACM SIGSPATIAL GIS 2011; DOI 10.1145/2093973.2094062)
- 4-page conference paper, pp. 513–516. STATUS: **FULL-TEXT VERIFIED 2026-06-17** (abstract
  via Wayback snapshot of ACM page + 4-page body PDF).
- **Q1 — full abstract:** "Routing services on the web and on hand-held devices have become
  ubiquitous in the past couple of years. Websites like Bing or Google Maps allow users to
  find routes between arbitrary locations comfortably in no time. Likewise onboard navigation
  units belong to the off-the-shelf equipment of virtually any new car. The amount of
  volunteered spatial data of the OpenStreetMap project has increased rapidly in the past
  five years. In many areas, the data quality already matches that of commercial map data,
  if not outright surpass it. We demonstrate both a server and a hand-held device based
  implementation working with OpenStreetMap data. Both applications provide real-time and
  exact shortest path computation on continental sized networks with millions of street
  segments. We also demonstrate sophisticated real-time features like draggable routes and
  round-trip planning."
- **Q2 — References [4] (CH lineage):** "[4] R. Geisberger, P. Sanders, D. Schultes, and D.
  Delling. Contraction Hierarchies: Faster and Simpler Hierarchical Routing in Road Networks.
  In C. C. McGeoch, editor, Proceedings of the 7th Workshop on Experimental Algorithms
  (WEA'08), volume 5038 of Lecture Notes in Computer Science, pages 319--333. Springer, June
  2008."
- **Q5 — CH query time (body):** "Contraction Hierarchies (CH) [4] have a very convenient
  trade-off between preprocessing and query time. Road networks of continental size can be
  preprocessed within a matter of minutes and queries run in the order of about a hundred
  microseconds."
- **Q6 — vanishing bottlenecks (body):** "We have seen that the actual routing algorithm runs
  in the order of a few (server) to a hundred milliseconds (hand-held) on data covering the
  European continent. Thus, routing is not a bottleneck anymore, and other components become
  obstacles."
- **Q7 — Dijkstra does not scale (body):** "Finding shortest paths in a road network is a
  problem that was solved in the early ages of computation. Unfortunately Dijkstra's seminal
  algorithm does not scale to large graphs [...]" / "[the algorithm engineering community]
  developed algorithms and data structures that provide substantial speedups over Dijkstra's
  algorithm and guaranteed optimal routes."
- **Q4 — BibTeX:** "@inproceedings{luxen-vetter-2011, author = {Luxen, Dennis and Vetter,
  Christian}, title = {Real-time routing with OpenStreetMap data}, booktitle = {Proceedings
  of the 19th ACM SIGSPATIAL International Conference on Advances in Geographic Information
  Systems}, series = {GIS '11}, year = {2011}, isbn = {978-1-4503-1031-4}, location =
  {Chicago, Illinois}, pages = {513--516}, numpages = {4}, url =
  {http://doi.acm.org/10.1145/2093973.2094062}, doi = {10.1145/2093973.2094062}, publisher =
  {ACM}, address = {New York, NY, USA} }"

### 01 — Compound AI Systems (Zaharia et al., BAIR Blog, 18 Feb 2024)
- **Q1 — definition:** "We define a Compound AI System as a system that tackles AI tasks using
  multiple interacting components, including multiple calls to models, retrievers, or
  external tools."
- **Q2 — core thesis:** "We argue that compound AI systems will likely be the best way to
  maximize AI results in the future, and might be one of the most impactful trends in AI in
  2024."
- **Q3 — SoTA comes from systems:** "state-of-the-art AI results are increasingly obtained by
  compound systems with multiple components, not just monolithic models."
- **Q5 — persistence:** "we believe compound AI systems will remain a leading paradigm even as
  models improve."

### 02 — Wang Agent Survey (Frontiers of Computer Science 18:186345, 2024; arXiv:2308.11432)
- **Q1 — four-module architecture:** "the overall structure of our framework is illustrated
  Figure 2, which is composed of a profiling module, a memory module, a planning module, and
  an action module."
- **Q2 — module interaction:** "the profiling module impacts the memory and planning modules,
  and collectively, these three modules influence the action module."
- **Q3 — profiling:** "The profiling module aims to indicate the profiles of the agent roles,
  which are usually written into the prompt to influence the LLM behaviors."

### 03 — AutoGen (Wu et al., arXiv:2308.08155; ICASSP 2024)
- **Q1 — agent properties:** "AutoGen agents are customizable, conversable, and can operate in
  various modes that employ combinations of LLMs, human inputs, and tools."
- **Q2 — conversation as substrate:** "Both natural language and computer code can be used to
  program flexible conversation patterns for different applications."
- **Q4 — composition:** "AutoGen agents are conversable, customizable, and can be based on
  LLMs, tools, humans, or even a combination of them."

### 04 — TravelPlanner (Xie et al., ICML 2024 / PMLR 235:54590–54613; arXiv:2402.01622)
- **Q1 — GPT-4 0.6%:** "Comprehensive evaluations show that the current language agents are
  not yet capable of handling such complex planning tasks—even GPT-4 only achieves a success
  rate of 0.6%."
- **Q2 — why hard:** "Language agents struggle to stay on task, use the right tools to collect
  information [...], or keep track of multiple constraints. However, we note that the mere
  possibility for language agents to tackle such a complex problem is in itself non-trivial
  progress. TravelPlanner provides a challenging yet meaningful testbed for future language
  agents."

### 05 — Reflexion (Shinn et al., NeurIPS 2023; arXiv:2303.11366) ⚠️ ANTI-FABRICATION
- **Q1 — verified HumanEval result:** "Reflexion achieves a 91% pass@1 accuracy on the
  HumanEval coding benchmark, surpassing the previous state-of-the-art GPT-4 that achieves
  80%."
- **Q2 — verified ALFWorld result (the precise figure):** "ReAct + Reflexion significantly
  outperforms ReAct by completing 130 out of 134 tasks using the simple heuristic to detect
  hallucinations and inefficient planning. Further, ReAct + Reflexion learns to solve
  additional tasks by learning in 12 consecutive trials."
- **Q3 — self-reflection mechanism:** "[an agent] works through trial, error, and
  self-reflection. Generating useful reflective feedback is challenging since it requires a
  good understanding of where the model made mistakes (i.e. the credit assignment problem
  [...]) as well as the ability to generate a summar[y] [...]"
- ⚠️ **DO NOT WRITE "+22% ALFWorld"** — the librarian proved this figure is absent from the
  paper; the abstract's broad sentence mentions "20% in HotPotQA" (not 22, not ALFWorld). Use
  only the verified "130/134 tasks" (Q2) and "91% HumanEval" (Q1).

### 06 — Gorilla (Patil et al., NeurIPS 2024; arXiv:2305.15334)
- **Q1 — headline:** "We release Gorilla, a finetuned LLaMA-based model that surpasses the
  performance of GPT-4 on writing API calls. When combined with a document retriever, Gorilla
  demonstrates a strong cap[ability] [...]"
- **Q3 — scale:** "model cards for each of these 1,645 API calls into a json object [...]"
- **Q4 — verified head-to-head:** "GPT-4 (0-shot) 38.70 36.55 24.7 [...] Gorilla (0-shot)
  59.13 6.98 33.87 [...]" — i.e., accuracy 38.70 → 59.13; hallucination 36.55 → 6.98
  (zero-shot TorchHub).
- **Q5 — retrieval reduces hallucination:** "The successful integration of the retrieval
  system with Gorilla demonstrates the potential for LLMs to use tools more accurately, keep
  up w[ith] [...]" *(Q5 is partial due to ar5iv line-wrap; safe to cite as quoted)*.

### 07 — Toolformer (Schick et al., NeurIPS 2023; arXiv:2302.04761)
- **Q1 — self-supervised tool use:** "This is done in a self-supervised way, requiring nothing
  more than a handful of demonstrations for each API. We incorporate a range of tools,
  including a calculator, a Q&A system, a search engine, a translation system, and a
  calendar."
- **Q2 — loss-filtered calls:** "We then execute these API calls and filter out all calls
  which do not reduce the loss [...] over the next tokens. All remaining API calls are
  interleaved with the original text [...]"
- **Q4 — verified LAMA results (Table 3):** GPT-J SQuAD 17.8 / Google-RE 0 / T-REx 4.9;
  Toolformer SQuAD 33.8 / Google-RE 11.5 / T-REx 53.5.
- **Q5 — verified math results (Table 4):** GPT-J ASDiv 7.5 / SVAMP 5.2 / MAWPS 9.9;
  Toolformer ASDiv 40.4 / SVAMP 29.4 / MAWPS 44.0.
- **Q6 — verified temporal results (Table 7):** GPT-J TempLAMA 13.7 / Dateset 3.9;
  Toolformer TempLAMA 16.3 / Dateset 27.3.

## Tier-B citations

### N5 — AgentTravel (Zhao, Feng, Li; OpenReview 34kIv0YVNe / NORA / CEUR workshop)
- ⚠️ **Label as "workshop paper" per criteria §2.** OpenReview is the only venue of record;
  no printed conference stamp.
- **Q1 — three components:** "This paper proposes AgentTravel, a unified framework that
  combines knowledge-grounded modeling, agentic reasoning, and multi-perspective evaluation.
  It includes: 1) TravelLLM, a domain-adapted model enriched with urban and spatial
  knowledge; 2) TravelAgent, an agentic planner with structured itinerary memory and
  real-time data retrieval; and 3) TravelBench, a benchmark assessing both knowledge
  grounding and plan quality."
- **Q2 — spatial-reasoning failure framing:** "current LLMs exhibit limited spatial reasoning
  capabilities—they often fail to accurately account for geographic distances, travel times,
  or accessibility constraints when generating feasible itineraries [...]. Second,
  integrating heterogeneous and real-time information from open APIs, transportation
  platforms, and local knowledge bases remains non-trivial [...]"
- **Q5 — TravelBench:** "TravelBench, a scalable benchmark suite with two complementary
  modules: KnowEval, which evaluates factual and spatial knowledge integration using curated
  urban datasets, and TripEval, which measures plan feasibility, personalization, and
  constraint satisfaction across realistic travel scenarios."

### 08 — Pai STT (Sustainability 12(16):6592, 2020; DOI 10.3390/su12166592) ⚠️ ANTI-FABRICATION
- **Q1 — STT dimensions:** "The main purpose of this study was to explore whether tourists
  are satisfied with their smart tourism technology experience (i.e., informativeness,
  accessibility, interactivity, personalization, and security)."
- **Q2 — sample:** "Surveys of a total of 527 participants who traveled to Macau from Mainland
  China were used for the analysis."
- **Q3 — accessibility strongest:** "The results showed that accessibility is the most
  important factor affecting the smart tourism technology experience and personalization the
  least."
- **Q4 — chain:** "Smart tourism technology experience is shown to be significantly associated
  with travel experience satisfaction, and travel experience satisfaction has a positive
  effect on both tourists' happiness and revisit intention."
- **Q5 — verified accessibility path coefficient (FULL-TEXT VERIFIED 2026-06-17):** "Among
  these five paths, accessibility was the most significant variable (path coefficient is
  0.285, T value is 35.093), followed by informativeness (path coefficient is 0.254, T value
  is 31.044), security (path coefficient is 0.239, T value is 30.062) [...]"
- ⚠️ **DO NOT cite "0.69" as a structural β** — it is the ACC↔INT discriminant-validity
  correlation in Table 3, not a STT→satisfaction structural coefficient. **Cite only the
  verified 0.285 accessibility path coefficient (Q5).**

### 09 — Liu Adaptive UI/UX (CSITRJ 5(8):1942–1962, 2024; DOI 10.51594/csitrj.v5i8.1457) ⚠️ ANTI-FABRICATION
- **Q1 — framework + adaptation engine:** "A context-aware adaptation engine was designed to
  adjust interface elements based on real-time user data dynamically. The proposed framework
  was implemented in a mobile learning application and subjected to rigorous usability
  testing and user engagement analysis."
- **Q2 — results:** "Results demonstrated significant improvements in task completion rates,
  user satisfaction, and overall engagement metrics compared to non-adaptive interfaces."
- **Q5 — SOM clustering (FULL-TEXT VERIFIED 2026-06-17):** "The User Profile Module utilizes
  a Self-Organizing Map (SOM) algorithm to cluster users into distinct groups based on their
  profile attributes. This unsupervised learning approach allows [...]"
- **Q6 — verified task-completion gain (FULL-TEXT VERIFIED 2026-06-17):** "The personalized
  interface generation resulted in a 22% higher task completion rate than the next best
  adaptive solution."
- ⚠️ **DO NOT cite "+35% feature discovery"** — not in the paper. The "35%" occurrences are a
  demographic age-group percentage (Table 2); "feature discovery" appears only as a
  table-header label. **Cite only the verified 22% task-completion gain (Q6).**

### 10 — Christina Tokopedia (JBIS 7(2):307–322, 2025) — FULL-TEXT VERIFIED 2026-06-17
- **Q1 — method + N:** "Employing a quantitative explanatory design, data from 204 Tokopedia
  users in Jabodetabek were analyzed using Partial Least Squares–Structural Equation Modeling
  (PLS-SEM) with SmartPLS 4.0."
- **Q2 — headline mediation:** "The results reveal that chatbot interaction and
  recommendation systems do not directly strengthen engagement, but both significantly
  improve satisfaction, which in turn enhances engagement. Satisfaction also mediates the
  effects of the chatbot and recommendation system[s] [...]"
- **Q3 — AI features:** "This research examines the impact of Tokopedia's AI-driven features,
  including the TANYA chatbot and automated product recommendations, on customer engagement,
  with satisfaction serving as an intermediary construct."

### 11 — Pang Chatbot Stickiness (JTAER 20(3):228, 2025; DOI 10.3390/jtaer20030228) ⚠️ RESIDUAL
- **Q1 — four motivational categories:** "[...] four key motivational categories: utilitarian
  (information acquisition), hedonic (enjoyment and time passing), technology (media appeal),
  and social (social presence and interaction) significantly influence user attitude toward
  chatbot services."
- **Q2 — sample:** "Utilizing survey data from 735 Chinese university students who have
  engaged with AI-powered chatbots [...]"
- **Q3 — privacy negative:** "Conversely, privacy invasion exerts a negative impact on user
  attitude, suggesting that while chatbots provide certain benefits, privacy issues can
  significantly undermine user satisfaction."
- **Q4 — attitude pivotal:** "[...] user attitude serves as a pivotal determinant in fostering
  both user stickiness and sustainable usage of chatbot services."
- ⚠️ The specific "β=0.326 tech motivation strongest" figure is **NOT in the abstract** (lives
  in paywalled tables not yet fetched). **Do not cite β=0.326.** Cite N=735 + the qualitative
  four-motivation finding + the privacy-negative finding.

### 12 — Onuiri ITMS (ASRJETS 18(1):304–315, 2016) — FULL-TEXT VERIFIED 2026-06-17
- **Q1 — aim:** "the aim of this research entails the design and implementation of an
  intelligent platform that will assist tourists in gaining access to information on tourist
  locations in Nigeria."
- **Q2 — stack:** "the system was implemented using Rational Unified Process as the adopted
  software development process, whereas MySQL, HTML and PHP were the implementation tools used
  in the development of the system."
- **Q4 — 50 locations:** "The table holds the 50 tourist locations used in the system as well
  as the information pertaining to each of the sites."
- **Q5 — hybrid rec:** "It was also able to act intelligently by using hybrid recommendation
  technique to recommend tourist locations based on their preference."

### 13 — AlSaeed LOCUS (Informatica 47(2), 2023; DOI 10.31449/inf.v47i2.4351) — FULL-TEXT VERIFIED
- **Q3 — recommenders:** "integrates two types of recommender systems, the item-item
  collaborative filtering algorithm and the user-user collaborative filtering algorithm."
- **Q4 — SUS:** "User satisfaction was measured through a System Usability Scale (SUS)
  survey, the achieved score was 87.75 which is higher than the threshold to pass the SUS
  test which is 68, thus LOCUS has fulfilled the user satisfaction measure."
- **Q5 — task time + UAT:** "the average completion time was 5.4s which is accepted." /
  "The user acceptance testing was conducted on 10 users from a variety of backgrounds and
  ages." **(N=10 ✓)**.

### 14 — Tsaih AI Tech-Stack (CACM 66(3):69–77, 2023; DOI 10.1145/3568026)
- **Q1 — seven layers:** "The proposed modularized, loosely coupled, seven-layered AI
  tech-stack model can leverage AIaaS offerings [...] The seven layers—from bottom to
  top—are AI infrastructure, AI platform, AI framework, AI algorithm, AI data pipeline, AI
  services, and AI solution layers."
- **Q2 — modularization argument:** "when using the decomposition concept, each vendor's
  AIaaS offering corresponds to one layer's functionality; thus, a change of vendor will not
  impact a change of vendors in other layers through the modularization architecture."
- **Q3 — four layering principles:** "1. Categorize similar functions into the same layer [...]
  2. Create a boundary at a point where the service description can be concise and the number
  of interactions across boundaries is minimized. 3. Decompose layers for handling AI jobs
  that are manifestly unique in task description or skill requirements. 4. Develop a boundary
  at a point where industry solutions are available and have proven useful."
- **Q4 — smart-tourism empirical case:** "Tourism has been the industry most affected by the
  COVID-19 pandemic and has urgently sought digital transformation opportunities to boost
  business in the post-pandemic market by activating an AI-driven smart tourism strategy. We
  explained the proposed AI tech-stack model in an executive MBA class, and four companies
  expressed their interest in applying the model to their desired smart tourism
  recommendation system (STRS)."
- **Q5 — conceptual framework:** "The proposed AI tech-stack model can be deemed as a
  conceptual framework and does not map to specific systems."
- ⚠️ **Use the correct DOI 10.1145/3568026** — the prior 10.1145/3579366 resolves to an
  unrelated IoT paper.

### 15 — Swanepoel (M.Eng Industrial Engineering thesis, Stellenbosch, Dec 2022; handle 10019.1/125975)
- **Q1 — trip-planning importance:** "An area of the industry that has gained more attraction
  recently is trip planning, as it is arguably one of the most important aspects of a
  tourist's journey regardless of their background or income level."
- **Q3 — planning overload:** "With the wide variety of travel websites, online booking
  platforms and tourist recommendations available on the internet and social media, the task
  of creating an itinerary can be daunting [...]"
- **Q4 — title-page metadata (verbatim):** "Development of an architecture and web-based
  demonstrator for tourist itinerary planning — by Nita Swanepoel — Thesis presented in
  partial fulfilment of the requirements for the degree of Master of Engineering (Industrial
  Engineering) in the Faculty of Engineering at Stellenbosch University — Supervisor: Prof JF
  Bekker — December 2022" *(Note: M.Eng — NOT Ph.D.)*

## Tier-C software citations

### S-VROOM — VROOM (cite as software; NO paper exists)
- **Maintainer confirmation (Issue #735, 2022-07-07):** "No, there is no paper associated
  with the project. If you're interested in the heuristics, your best bet is to check out the
  implementation [...] We have two main heuristics used to compute initial solutions prior to
  applying the local search process: `basic` that is loosely adapted from the well-known
  Solomon I1 heuristic [...]; `dynamic_vehicle_choice` that is somehow a generalization of the
  latter [...] We also have a dedicated solving pipeline for the TSP which is based on an
  implementation of the Christofides heuristic + an ad-hoc local search process." Closing
  (2022-09-16): "Closing here as there is nothing actionable. Writing a research paper is
  outside the scope of this repo. ;-)"
- **README:** "Complex Route Optimization in Milliseconds / Good solutions, fast. [...] Vroom
  is an open-source route optimization engine written in C++20 that solves complex vehicle
  routing problems (VRP) in milliseconds."
- **Academic characterization (cross-cite N4 Q6, NOT a VROOM paper):** "good solutions to
  real-life VRPs [...] However, it is unable to compete with state-of-the-art algorithms."

### S-VALHALLA — Valhalla (cite as software)
- **Isochrone definition:** "Valhalla's isochrone service computes areas that are reachable
  within specified time intervals from a location, and returns the reachable regions as
  contours of polygons or lines that you can display on a map."
- **Use case:** "For example, you can use the isochrone service to find out where you can
  travel within a 15-minute walk from your office building."

### S-OSRM — OSRM (cite as software; pair with OSRM-PAPER for the algorithm)
- **/table service definition:** "Table service Computes the duration of the fastest route
  between all pairs of supplied coordinates. Returns the durations or distances or both
  between the coordinate pairs. Note that the distances are not the shortest distance between
  two coordinates, but rather the distances of the fastest routes. Duration is in seconds and
  distances is in meters." *(honesty point: matrices are fastest-route, not straight-line)*.
- **README pipelines:** "There are two pre-processing pipelines available: - Contraction
  Hierarchies (CH) - Multi-Level Dijkstra (MLD) [...] We recommend using MLD by default
  except for special use cases such as very large distance matrices where CH is still a
  better fit for the time being."

## Tier-D citations (LABELLED preprints — footnotes only, never core)

### N2 — TRIP-PAL (de la Rosa et al., arXiv:2406.10196) — preprint
- **Q1 — hybrid design:** "We propose TRIP-PAL, a hybrid method that combines the strengths
  of LLMs and automated planners, where (i) LLMs get and translate travel information and
  user information into data structures that can be fed into planners; and (ii) automated
  planners generate travel plans that guarantee constraint satisfaction and optimize for
  users' utility."
- **Q6 — GPT-4 validity very low:** "GPT-4 returned 14 valid plans out of the 100 tasks,
  clearly indicating that it struggles to generate travel plans that satisfy hard
  constraints."
- ⚠️ TRIP-PAL's solver is a classical **PDDL planner (Fast Downward)**, NOT a VRP/VRPTW
  solver — distinct from VOYO's VROOM. Do not conflate the solver families.

### N3 — TravelAgent (Chen et al., arXiv:2409.08069) — preprint, **FOUR modules not five**
- **Q1 — four modules:** "we introduce TravelAgent, a travel planning system powered by large
  language models (LLMs) designed to provide reasonable, comprehensive, and personalized
  travel itineraries grounded in dynamic scenarios. TravelAgent comprises four modules:
  Tool-usage, Recommendation, Planning, and Memory Module."
- **Q6 — human eval (Table 1):** TravelAgent vs GPT-4+ agent — Rationality 9.56 / 8.16;
  Comprehensiveness 8.87 / 6.25; Personalization 8.44 / 4.31 (20 travel cases).

## Numerical ground-truth (criteria §4 + §5 — cite as criteria)

> The POI/pricing/enrichment counts below are mandated by `thesis/criteria/thesis-criteria.md`
> §4 (the "stale-number sweep"). The supervisor enforces them.

- **POI count = 310** (criteria §4 — *never* 255, which is the stale archived number).
- **Dual gov.eg prices = 58 POIs.**
- **Authoritative gov.eg descriptions = 76 POIs.**
- **POIs with any enrichment = 97.**
- ⚠️ **`thesis/evidence/05-db-completeness.json` still reports `total_active_pois: 255`** and
  must be regenerated before Ch6 closes (criteria §5); until then, cite the criteria-mandated
  310 for the substrate size. Flag in figures-spec.md.
- **ItiNera's dataset** (for the VOYO-vs-ItiNera delta): "1233 top-rated urban itineraries
  and 7578 POIs" [citation: N1 → Q7] — *urban China*, not Egypt.

## Metrics marked PENDING (do not invent)

Per criteria §5: retrieval (P@k/R/nDCG), feasibility (time-budget adherence, geo coherence),
reliability (constraint-violation rate), provenance coverage, UX (e2e Playwright pass rate)
are all PENDING the eval harness. **This §2.2 dossier does not introduce any of these as
results** — they are deferred to Ch4; Ch2 only defines the *strategy*.
