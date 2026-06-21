# Claude Prompt — Chapter 4 (Results & Evaluation) Prose Generation

> **Paste everything below this line into your Claude project as the opening message.**
> Then upload the files listed in the "File directory table" section at the bottom.

---

## ROLE AND TASK

You are writing **Chapter 4 (Results & Evaluation)** of a competitive undergraduate AI
Bachelor's thesis on **VOYO**, a deterministic AI travel planner for Egypt. The chapter must
read as polished academic prose at upper-first-class / strong-A calibre — the kind of writing
that survives a viva.

You are NOT designing the evaluation. The evaluation has already been run (2026-06-20). Your
job is to turn the supplied evidence dossier into thesis prose: argument → measured numbers →
figures → honest disclosure → discussion. Every number you cite is already in the supplied
`07-eval-results.json`; **never invent a number for a metric that is PENDING.** If a metric is
labelled PENDING in the dossier, write it as PENDING in the prose with the stated reason — do
not fabricate.

## THE SPINE (every subsection must reinforce this)

> *VOYO's evaluation measures the hybrid-deterministic contribution along six metric families.
> On 2026-06-20 the eval harness ran, flipping four of the six from PENDING to MEASURED. The
> measured headlines: **+35.6 pp travel-time feasibility gap (full-hybrid vs LLM-only, n=12
> paired)**, **91.3% opening-hours feasibility (clears the ≥90% threshold)**, **0.919
> LLM-judge groundedness over 125 conversational queries**, **0% error rate under 40×
> concurrency load**. Retrieval P@k and UX e2e remain PENDING but are not load-bearing for
> the contribution. The keystone ablation is the decisive result: an LLM authoring its own
> travel-time estimates schedules physically-impossible transitions 52.3% of the time; a
> VRPTW solver reduces that to 16.8%.*

## REQUIRED SECTION STRUCTURE

Write the chapter in this order, with these section numbers. Do not invent additional
sections. Do not include a separate "reachability visualisation" section (isochrone views) —
that has been deliberately removed; Valhalla's role is evidenced quantitatively by the
ablation, and in-app UI screenshots will be added in a later pass.

- **4.1 Evaluation method overview** — the six-metric framework, why these six, the
  protocol reference back to §3.5. Lead with the metric-family table.
- **4.2 Measured-now results (deterministic substrate)** — §4.2.1 latency (p95 1.662 ms,
  threshold <500 ms, PASSES), §4.2.2 regression-test pass rate, §4.2.3 A/B correctness
  (engine discriminates between profiles), §4.2.4 data-substrate integrity (310 POIs).
- **4.3 Pending metrics (strategy defined)** — §4.3.1 retrieval P@k/nDCG (PENDING: needs
  POI-level human labels), §4.3.4 provenance coverage (PENDING: Windows enrich run),
  §4.3.6 UX e2e (PENDING: Playwright suite authored, blocked on Flutter web semantics +
  authenticated session — full suite will accompany digital submission). For §4.3.2
  feasibility and §4.3.3 reliability, state the strategy here but point forward to §4.6
  for the measured numbers.
- **4.4 Measured-vs-pending summary table** — the 4-of-6 MEASURED table. This is the
  single most important table for the "excellence" criterion; get it exactly right.
- **4.6 Measured evaluation results (the 2026-06-20 harness run)** — the empirical core.
  Four subsections, in this order:
  - **4.6.1 Keystone ablation** (Figure 4.12) — the headline. Lead §4.6 with the
    feasibility table: 83.2% vs 47.7% travel-time (+35.6 pp), 91.3% vs 84.7% opening-hours
    (+6.5 pp), margin penalty 172 vs 434 (−262). State the paired-design advantage (same
    LLM selection, only the optimizer varies → delta is attributable to the engine, not
    LLM-selection variance). Disclose the 12/12 LLM-selected, 11/12 VROOM-optimized
    provenance; mention the single VROOM-down case as Valhalla's documented 400 km intra-day
    matrix limit (graceful degradation, not a defect). Disclose P07 (Sinai trek, 0.167
    feasibility on BOTH arms) as a data-substrate gap (null `average_visit_duration`, 200 km+
    POI spread, sparse city-tagging) — this *strengthens* the paired-design argument.
  - **4.6.2 Live planner benchmark** (Figure 4.13) — determinism provenance: 12/12 LLM
    selection, 12/12 VROOM optimization, 92% geo-guard firing, median latency 20.3 s, max
    34.3 s. Frame as the audit trail proving the architectural contract from §3.3 holds in
    production.
  - **4.6.3 Deep CLEO groundedness** (Figures 4.14–4.16) — 0.919 groundedness over 125
    queries, out_of_scope groundedness 1.000 (never fabricates when it should refuse),
    2.4% degraded rate (3/125). Category breakdown: factual / personalized / itinerary.
    Tie back to the §3.3 contract (CLEO only answers from retrieved POI context).
  - **4.6.4 Load test** (Figure 4.17) — 0% errors across c=1→40, peak 751 RPS, p95 ≤138 ms
    at c=40. The deterministic substrate's scalability proof.
  - **4.6.5 What is still PENDING** — one paragraph naming exactly what is and is not
    measured, and why the pending items (retrieval P@k, provenance coverage, UX e2e) do
    not undermine the contribution. This is the honesty argument that protects the chapter
    in a viva.
- **4.5 Discussion** — what the results mean. Three moves: (a) the measured metrics are
  precisely the deterministic-core metrics the hybrid argument predicts should be strong;
  (b) the gaps are honestly disclosed and orthogonal to the contribution; (c) positioning
  against ItiNera (the closest peer) — VOYO's paired ablation is methodologically stronger
  than ItiNera's config-toggle ablation, and VOYO's feasibility/reliability numbers are the
  operational proof ItiNera only asserts.

## CITATION DISCIPLINE (critical)

Use these BibTeX keys via `\cite{...}`. **Do not invent citation keys.** Only four sources
are load-bearing for this chapter:

- `itinera_tang_2024` — the closest peer; used for the comparison in §4.5 and the
  methodological contrast (paired vs config-toggle ablation). PDF supplied.
- `pyvrp_wouda_2024` — the VRPTW solver substrate (VROOM wraps PyVRP). Cite when naming the
  optimizer in §4.6.1. PDF supplied.
- `luxen_vetter_2011` — the OSRM contraction-hierarchies paper; cite for the travel-time
  matrix substrate that the feasibility check invokes. PDF supplied
  (`OSRM-PAPER_luxen2011.pdf`).
- `agenttravel_zhao_2024` — the KnowEval/TripEval two-axis evaluation framework VOYO's
  metric design follows. No PDF; the dossier already contains the relevant quotes
  (`thesis/citations/new-route-opt/agenttravel/quotes.md`) — cite as `agenttravel_zhao_2024`
  and do not quote beyond what is in the supplied quotes file.

Map any legacy citation tags you encounter in the dossier as follows: **N1 →
`itinera_tang_2024`**, **N4 → `pyvrp_wouda_2024`**, **N5 → `agenttravel_zhao_2024`**,
**OSRM-PAPER → `luxen_vetter_2011`**. The references list (`references.bib`) is supplied.

## FIGURE HANDLING (critical)

Nine vector PDF figures are supplied at `thesis/figures/eval/`. Embed each at the location
indicated in the structure above using `\includegraphics[width=0.9\textwidth]{...}` with
**relative path `figures/eval/<filename>`** (the main `main.tex` lives at `thesis/main.tex`,
so `figures/eval/...` is correct — do not use `thesis/figures/eval/...`). Give each a
numbered `\caption{...}` and `\label{fig:...}`. The nine files:

| Thesis Fig # | File | Section |
|---|---|---|
| 4.12 | `figures/eval/ablation_ablation_headline.pdf` | §4.6.1 (lead figure) |
| (supporting) | `figures/eval/ablation_ablation_per_profile.pdf` | §4.6.1 |
| 4.13 | `figures/eval/planner_planner_latency.pdf` | §4.6.2 |
| (supporting) | `figures/eval/planner_planner_pace_stops.pdf` | §4.6.2 |
| 4.14 | `figures/eval/deep_deep_cleo_overall.pdf` | §4.6.3 |
| 4.15 | `figures/eval/deep_deep_cleo_groundedness.pdf` | §4.6.3 |
| 4.16 | `figures/eval/deep_deep_cleo_category_heatmap.pdf` | §4.6.3 |
| 4.17 | `figures/eval/load_load_latency.pdf` | §4.6.4 |
| (supporting) | `figures/eval/load_load_throughput.pdf` | §4.6.4 |

**Do NOT include any isochrone figure.** The reachability-visualisation section has been
removed; in-app UI screenshots will be added in a later pass and live outside
`figures/eval/`.

## NUMBERS DISCIPLINE

- The canonical number source is `thesis/evidence/07-eval-results.json`. If a number is in
  the dossier but not in the JSON, prefer the JSON. If a number is in neither, do not
  invent it.
- Report latencies as "p95" not "average" unless the dossier specifies otherwise.
- Report feasibility as percentages with one decimal (83.2%, not 83%).
- Margin penalty is "lower is better" — make sure the prose never implies higher is better.
- n=12 for ablation and planner; n=125 for deep CLEO; 5 concurrency levels for load.

## HONESTY REQUIREMENTS (these protect you in the viva)

The following MUST appear in the prose, not be buried:

1. **Same-model-judge bias.** The deep CLEO groundedness scores are produced by an LLM-judge
   (`gpt-4o-mini`) judging outputs produced by the same model. State this explicitly in
   §4.6.3. State the mitigation: a model-independent heuristic layer (heuristic_overall
   0.692) corroborates the judge, and the architectural contract (CLEO answers only from
   retrieved context) makes fabrication structurally unlikely. Do NOT claim the judge is
   bias-free.
2. **Eval model ≠ demo model.** All three LLM-using eval pipelines ran on `gpt-4o-mini` via
   the OPTO gateway; the demo path runs on Groq `llama-3.3-70b-versatile`. State this in
   §4.6 opening. Frame as model-agnosticism (single-model discipline for reproducibility),
   not as a weakness to hide — but acknowledge an examiner may ask whether llama-70b would
   lift the intent-layer numbers.
3. **Reliability is a proxy.** Margin penalty (172 vs 434) is a tightness proxy, not a
   strict per-constraint violation rate. Say so in §4.6.1 / §4.6.5.
4. **8% overlapping-stops days.** 2 of 24 planner days (P10, P12) have overlapping
   consecutive stop times. Disclose in §4.6.2 as a real VROOM imperfection, not hidden.
5. **20% cost coverage.** Only 17 of 85 itinerary stops have a real `cost_egp` (the
   `ticket_price` field is null for the rest). Disclose in §4.6.2 as a data-substrate gap.
6. **No human evaluation.** State in §4.6.5 that no human-subject evaluation was conducted;
   the LLM-judge + heuristic layer is the triangulation available.
7. **No head-to-head with ItiNera on shared data.** The ItiNera comparison in §4.5 is
   methodological (paired vs config-toggle design) + borrowed comparand, not a shared-data
   bake-off. State this.

## LENGTH AND REGISTER

- Target **3,500–4,500 words** of prose (excluding tables, figures, captions).
- Register: confident but never overclaiming. "The measured results support the claim
  that…" not "The results prove…". Use "the data show" not "we can see".
- First person plural ("we") is fine; "the system" / "VOYO" is fine. Avoid "obviously",
  "clearly", "of course".
- Every claim ends with a citation or a forward-reference to a table/figure.

## OUTPUT

Return a single complete LaTeX chapter: `\chapter{Results \& Evaluation}` followed by the
sections in the order above. Use `\section`, `\subsection`, `\subsection`. Tables as
`tabular` in `table` floats with `\label{tab:...}`. Figures as `figure` floats with
`\includegraphics` + `\caption` + `\label`. BibTeX citations as `\cite{key}`. Do NOT
include the bibliography itself (it is in `references.bib`). Do NOT include a chapter
summary/recap at the end — the discussion §4.5 is the close.

---

## FILE DIRECTORY TABLE (upload these to the Claude project)

| # | File (relative to repo root) | Why Claude needs it |
|---|---|---|
| 1 | `thesis/ch4-results/dossier.md` | The argument outline — section-by-section claims, citations, phrasing guidance |
| 2 | `thesis/ch4-results/evidence-packet.md` | All verbatim numbers (§A–G), the no-fabrication source |
| 3 | `thesis/ch4-results/figures-spec.md` | Figure specs + which are MEASURED vs PENDING |
| 4 | `thesis/ch4-results/citations-used.md` | Per-claim citation map |
| 5 | `thesis/ch4-results/supervisor-review.md` | The auditor's gap report — tells Claude what NOT to overclaim |
| 6 | `thesis/ch4-results/_run-summary.md` | Headline numbers table + honest-disclosure list |
| 7 | `thesis/evidence/07-eval-results.json` | **Canonical number source** — every metric resolves here |
| 8 | `thesis/ch3-methodology/dossier.md` | For §3.5 protocol cross-refs (paired design, travel-time feasibility metric, model disclosure §3.2.5) |
| 9 | `thesis/ch3-methodology/evidence-packet.md` | For the §3.5.2a/§3.5.2b protocol detail the ch4 prose must point back to |
| 10 | `thesis/citations/new-route-opt/agenttravel/quotes.md` | The only AgentTravel (N5) quotes Claude may use — no PDF exists |
| 11 | `thesis/references.bib` | BibTeX keys — so `\cite{}` keys match the bibliography |
| 12–20 | `thesis/figures/eval/*.pdf` (9 files) | The 9 vector PDF figures — see figure table above |

**Citation PDFs already in your ch2 project (verify these 3 specifically uploaded):**
- `thesis/citations/pdfs/itinera_tang2024.pdf` (ItiNera — N1)
- `thesis/citations/pdfs/pyvrp_wouda2024.pdf` (PyVRP — N4) ← **ch4 needs this; verify it's in your ch2 upload**
- `thesis/citations/pdfs/OSRM-PAPER_luxen2011.pdf` (OSRM — luxen_vetter_2011) ← **ch4 needs this; verify it's in your ch2 upload**

(AgentTravel / N5 has no PDF — only `quotes.md`, which is file #10 above. TravelPlanner and
Reflexion are NOT cited in ch4 — they live in ch2/ch3 only — so you do not need to re-upload
them for the ch4 pass.)
