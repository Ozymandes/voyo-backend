"""
VOYO Evaluation Framework — shared foundation for all automated evaluation,
benchmarking, ablation, load, and e2e pipelines.

Modules:
    theme    — matplotlib VOYO thesis theme (brand palette, 300 DPI PNG + PDF).
    profiles — the fixed, reproducible battery of trip profiles.
    io       — timestamped run directories; persists results + itineraries.
    metrics  — feasibility / margin / travel metrics over a schedule.

These modules are deliberately live-stack-agnostic: they import nothing from
the app that touches the network, so they can be imported and unit-tested
without Docker/Groq/Supabase running.
"""

from .theme import VOYO_COLORS, REGION_COLORS, CATEGORY_COLORS, apply_theme, save_figure
from .io import EvalRun, run_dir

__all__ = [
    "VOYO_COLORS",
    "REGION_COLORS",
    "CATEGORY_COLORS",
    "apply_theme",
    "save_figure",
    "EvalRun",
    "run_dir",
]
