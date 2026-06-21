# VOYO Evaluation Framework

The full automated evaluation battery for the thesis results section. Every
pipeline renders thesis-calibre charts (300 DPI PNG + vector PDF, on the VOYO
brand palette) and persists reproducible, timestamped artefacts.

## Quick start

```bash
# Prereqs (you run these, once): full stack up + a real user id
docker-compose up -d                                 # Valhalla :8002, OSRM :5000, VROOM :8081
./venv/Scripts/python.exe -m uvicorn src.api.main:app --port 8000
export VOYO_EVAL_USER_ID=<your Supabase user UUID>   # required for ablation + planner
export VOYO_TOKEN=<your JWT>                         # optional: enables authenticated load endpoint
```

Run any single pipeline directly:

| Pipeline | Command | Needs |
|---|---|---|
| **Keystone ablation** (headline chart) | `python scripts/testing/run_keystone_ablation.py --user-id $VOYO_EVAL_USER_ID` | Docker + Groq + DB |
| **Planner benchmark** (saves itineraries) | `python scripts/testing/run_planner_benchmark.py --user-id $VOYO_EVAL_USER_ID` | Docker + Groq + DB |
| **Load / stress test** | `python scripts/testing/run_load_test.py` | Backend only |
| **Deep CLEO** (LLM-judged) | `python scripts/testing/run_deep_cleo.py --sample 20` | Groq (quota-hungry) |
| **e2e (Playwright)** | `bash tests/e2e/run_e2e.sh` | Flutter web on :8099 |
| **Isochrone figure** (Valhalla, reproducible) | `python scripts/testing/render_isochrone.py --title "..." [--pois]` | Valhalla up (POI overlay optional) |

Or run them as **pi chains** (each does smoke → run → review): see
`.pi/chains/voyo-eval-*.chain.json`. The master `voyo-eval-all` runs the whole
battery (Groq-free pipelines in parallel, Groq-heavy ones sequenced to respect
quota) and writes `thesis/evidence/07-eval-results.md`.

## What each pipeline proves

- **Keystone ablation** — paired comparison: same LLM POI selection, VROOM-
  assigned times vs naive evenly-spaced slots, both scored against ground-truth
  opening hours. The in-domain replication of ItiNera's optimizer ablation.
  Outputs: feasibility delta (pp), margin-penalty delta, per-profile chart.
- **Planner benchmark** — live `/plan` over 12 trip profiles. Saves EVERY
  generated itinerary (closes the "itineraries were never persisted" gap).
  Records provenance breakdown, pace→stops, latency, solver status.
- **Load test** — p50/p95/p99 + throughput vs concurrency on read endpoints.
- **Deep CLEO** — the 145-query benchmark with the 7 heuristic metrics PLUS a
  Groq LLM-judge (groundedness / relevance / helpfulness). Groundedness directly
  measures the "nothing fabricated" thesis claim. Saves every prompt+response.
- **e2e** — the 4 critical demo flows (Explore / CLEO / Add-to-itinerary /
  Isochrone) with screenshots for the appendix.
- **Isochrone renderer** — fetches the REAL reachable-area polygons from
  Valhalla and renders an ItiNera-style clean figure (VOYO palette, labelled
  time bands, optional nearby-POI overlay). Reproducible and app-independent.
  For the "this is the real product" proof, the Playwright e2e suite also
  auto-screenshots the in-app isochrone panel.

## Outputs

Every run writes to a single timestamped dir under
`data/evaluation/runs/<name>_<ts>/`:

```
report.json          aggregate metrics + metadata (git commit stamped)
results.jsonl        one record per unit (profile / query / request)
itineraries/         one JSON per generated itinerary (planner/ablation)
prompts/             one JSON per CLEO prompt+response (deep CLEO)
figures/             PNG (300 dpi) + PDF (vector) per chart
```

## Honest scope notes (for the methodology section)

- The 7 heuristic CLEO metrics are keyword/regex-based; the **LLM judge is the
  semantic layer**. State both; do not present the heuristic set as deep NLP.
- **No embeddings**: Groq has no embeddings API. LLM-as-judge is the stronger
  choice for the groundedness claim anyway; embedding similarity is future work.
- The ablation's "naive baseline" is a paired control (same selection, no
  optimizer) — this is methodologically stronger than a between-subjects toggle.
- All Groq-heavy pipelines share one quota; the master chain sequences them.

## LLM backend: OPTO (free) vs Groq (default)

The eval pipelines route to the **OPTO gateway** (`gemma4-26b`) automatically
when `OPTO_LLM_API_KEY` is present, so eval / load runs never touch the Groq
free-tier quota. The production/demo path stays on Groq unless
`VOYO_LLM_BACKEND=opto` is set.

- OPTO is OpenAI-compatible at `https://optollm.optomatica.com/v1` — driven by
  the stock `openai` SDK, so CLEO's tool-using ReAct loop works unchanged
  (gemma4-26b supports function calling, verified).
- To force Groq for a run: `export VOYO_LLM_BACKEND=groq`.
- curl against OPTO needs `--http1.1` (an HTTP/2 server quirk); Python is
  unaffected (httpx defaults to HTTP/1.1).
- Switch is a single factory: `src.cleo/config.py::get_llm_client()`. The three
  call sites (CLEO agent, Safarny planner, LLM judge) instantiate through it.
