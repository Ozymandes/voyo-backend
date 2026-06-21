"""
Evaluation IO — timestamped run directories + artefact persistence.

Every evaluation run writes to a single timestamped directory so a results
section can cite an exact, reproducible artefact. This also closes the
documented gap that generated itineraries were never persisted: the planner
benchmark saves every `/plan` output as JSON alongside the aggregate report.

Layout produced (under <root>/):
    <run_name>_<timestamp>/
        report.json            — aggregate metrics + metadata
        results.jsonl          — one record per unit (profile / query / request)
        itineraries/           — one JSON per generated itinerary (planner run)
        prompts/               — one JSON per CLEO prompt+response (deep run)
        figures/               — rendered PNG + PDF charts

This module touches only the filesystem — no app/network imports.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, Optional


def _project_root() -> Path:
    # scripts/testing/voyo_eval/io.py → repo root is 4 parents up.
    return Path(__file__).resolve().parents[3]


def default_eval_root() -> Path:
    """Canonical root for all evaluation runs: data/evaluation/runs/."""
    return _project_root() / "data" / "evaluation" / "runs"


class EvalRun:
    """A single timestamped evaluation run directory."""

    def __init__(self, name: str, root: Optional[Path] = None):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.name = name
        self.run_id = f"{name}_{ts}"
        self.dir = (root or default_eval_root()) / self.run_id
        self.fig_dir = self.dir / "figures"
        self.itin_dir = self.dir / "itineraries"
        self.prompt_dir = self.dir / "prompts"
        for d in (self.dir, self.fig_dir, self.itin_dir, self.prompt_dir):
            d.mkdir(parents=True, exist_ok=True)

    # ── writers ───────────────────────────────────────────────────────
    def save_report(self, report: Dict[str, Any]) -> Path:
        path = self.dir / "report.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        return path

    def save_results_jsonl(self, results: Iterable[Dict[str, Any]]) -> Path:
        path = self.dir / "results.jsonl"
        with open(path, "w", encoding="utf-8") as f:
            for rec in results:
                f.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
        return path

    def save_itinerary(self, itinerary: Dict[str, Any], key: str) -> Path:
        """Persist a single generated itinerary. ``key`` disambiguates runs
        (e.g. '<profile_id>__full' / '<profile_id>__baseline')."""
        safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in str(key))
        path = self.itin_dir / f"{safe}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(itinerary, f, indent=2, ensure_ascii=False, default=str)
        return path

    def save_prompt(self, record: Dict[str, Any], key: str) -> Path:
        safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in str(key))
        path = self.prompt_dir / f"{safe}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2, ensure_ascii=False, default=str)
        return path

    # ── metadata ──────────────────────────────────────────────────────
    def base_metadata(self) -> Dict[str, Any]:
        """Common metadata stamped onto every report for reproducibility."""
        return {
            "run_id": self.run_id,
            "name": self.name,
            "timestamp": datetime.now().isoformat(),
            "git_commit": _git_commit(),
            "host": os.environ.get("COMPUTERNAME") or os.environ.get("HOSTNAME"),
        }


def _git_commit() -> Optional[str]:
    try:
        import subprocess
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=_project_root(), capture_output=True, text=True, timeout=5,
        )
        return out.stdout.strip() if out.returncode == 0 else None
    except Exception:
        return None


def run_dir(name: str, root: Optional[Path] = None) -> EvalRun:
    """Convenience constructor used by the package __init__."""
    return EvalRun(name, root)
