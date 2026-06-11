# VOYO Documentation Hub

> Living documentation for the VOYO AI Travel Planner thesis project.
> Every phase, every change, every failure, and every success is tracked here.

## Structure

```
docs/
├── devlog/                    # Chronological development log (daily entries)
│   ├── phase-1a-auth.md       # Backend Auth & Profiles
│   ├── phase-1b-cleo.md       # CLEO Agent Rework
│   ├── phase-2a-routing.md    # Routing Infrastructure
│   ├── phase-2b-itinerary.md  # Itinerary Engine
│   ├── phase-3-frontend.md    # Flutter App Rebuild
│   ├── phase-4-testing.md     # Testing & Benchmarking
│   └── phase-5-docs.md        # Documentation & Thesis
│
├── architecture/              # System design documents
│   ├── system-overview.md     # High-level architecture
│   ├── neuro-symbolic-design.md  # LLM + VROOM split
│   ├── cleo-agent-design.md   # CLEO internals
│   ├── routing-stack.md       # Valhalla + VROOM
│   ├── data-model.md          # Supabase schema & POI model
│   └── frontend-architecture.md  # Flutter app structure
│
├── thesis-drafts/             # Thesis chapter drafts
│   ├── 01-introduction.md
│   ├── 02-background.md
│   ├── 03-related-work.md
│   ├── 04-methodology.md
│   ├── 05-implementation.md
│   ├── 06-evaluation.md
│   ├── 07-discussion.md
│   └── 08-conclusion.md
│
├── api-reference/             # Auto-generated + handwritten API docs
│   ├── endpoints.md           # All REST endpoints
│   ├── auth-flow.md           # JWT auth flow
│   └── data-contracts.md      # Request/response schemas
│
├── benchmark-results/         # Performance data & graphs
│   ├── cleo-quality.json      # Response quality scores
│   ├── cleo-accuracy.json     # Factual accuracy results
│   ├── routing-performance.json # Optimization timing
│   ├── figures/               # Thesis-ready graphs (300 DPI PNG)
│   └── raw/                   # Unprocessed benchmark output
│
├── critical-assessments/      # Honest evaluations
│   ├── cleo-assessment.md     # CLEO strengths & weaknesses
│   ├── routing-assessment.md  # Routing stack evaluation
│   ├── ux-assessment.md       # Frontend UX review
│   └── system-assessment.md   # Overall system assessment
│
├── phase-reports/             # Phase completion summaries
│   ├── phase-1a-report.md     # What was built, what failed, what succeeded
│   ├── phase-1b-report.md
│   ├── phase-2a-report.md
│   ├── phase-2b-report.md
│   ├── phase-3-report.md
│   ├── phase-4-report.md
│   └── phase-5-report.md
│
└── SETUP.md                   # Developer onboarding guide
```

## Writing Tone

All documentation is written in the voice of a CS senior who knows their craft — 
clear, engaging, articulate, and honest. Not a professor lecturing, not a startup 
pitching, but someone who built something and can explain exactly why every decision 
was made. When something doesn't work, we say so. When something is genuinely clever, 
we explain the insight without overselling it.

## Agent Instructions

The Documentation Agent (Phase 5) is responsible for:
1. **Devlog entries** — Written during EVERY phase, not just Phase 5
2. **Phase reports** — Completed at the end of each phase with full change log
3. **Architecture docs** — Updated as implementation reveals design decisions
4. **Thesis drafts** — Written incrementally, not dumped at the end
5. **Benchmark results** — Captured from Phase 4 testing, formatted for thesis inclusion

Other agents should log their changes to `docs/devlog/phase-X.md` as they work.
The Documentation Agent will later formalize these logs into reports and thesis sections.
