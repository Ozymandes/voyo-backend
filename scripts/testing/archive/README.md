# Archived Evaluation Probe Scripts

These one-off debugging/probe scripts were created during the June 2026 evaluation
and thesis-evidence sessions. They are **not imported by any production code, test,
or pi-agent chain** (verified 2026-06-30), so they were moved here from
`scripts/testing/` to declutter the active workspace while preserving them for
reproducibility forensics.

## Why archived, not deleted

Each script produced a specific piece of evidence or figure that may have landed in
`thesis/evidence/` or the thesis PDF. If a number ever needs to be re-traced to its
generating script, it will be here.

## What lives here

| Script | Purpose |
|---|---|
| `_build_labeling_sheets.py` | Built the human-labeling spreadsheets for the retrieval P@k benchmark |
| `_drive_win_poi.py` | Selenium probe for Windows POI-detail screenshots |
| `_img_probe.py` | Image-dimension probe for figure aspect ratios |
| `_post_fix_aggregate.py` | Aggregated the post-fix retrieval rerun (chain A helper) |
| `_post_fix_collect.py` | Collected raw CLEO outputs for the post-fix rerun |
| `_post_fix_figs.py` | Rendered the post-fix retrieval figures (4.5, 4.6, 4.7) |
| `_post_fix_replicate_chat.py` | 3-run replication of chat-side variance (Table in §4.5.4) |
| `_repro_console.py` | Console harness for the 3-run replication |
| `_repro_ime_sheet.py` | Reproduced the Egyptian-Museum factual-lookup sheet |
| `_repro_planner.py` | Reproduced the planner benchmark run |
| `_repro_poi_sheet.py` | Reproduced the POI-detail sheet |
| `_repro_tiles.py` | Reproduced the map-tile / isochrone render |

## Note on `_post_fix_metrics.py`

This module is **NOT archived** — it stays in `scripts/testing/` because the five
thesis-evidence scripts `chain_a`–`chain_e` import `precision_at_k` and related
metrics from it. Moving it would break the post-fix retrieval rerun pathway.

## Regenerating results

If you need to re-run any of these, the active eval pipelines in
`scripts/testing/run_*.py` and `scripts/testing/chain_*.py` are the canonical
entry points (and are referenced by the pi-agent chains in `.pi/chains/voyo-eval-*.chain.json`).
These archived scripts are the intermediate helpers that fed those pipelines during
the original June-20 to June-26 sessions.
