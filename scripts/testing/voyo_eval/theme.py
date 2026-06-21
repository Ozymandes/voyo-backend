"""
VOYO thesis chart theme.

Single source of truth for every figure the evaluation pipelines render, so
the whole results section speaks one visual language: on-brand palette (lifted
verbatim from design-system/DESIGN_TOKENS.md), serif titles, hairline grid,
no chartjunk, and dual PNG (300 DPI) + PDF (vector) output at thesis print size.

This module imports ONLY matplotlib + numpy — no app code — so it can be used
to render synthetic test figures without the live stack.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Sequence

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

# ── Brand palette (design-system/DESIGN_TOKENS.md) ────────────────────
VOYO_COLORS = {
    "page":   "#F7F5F1",  # scaffold background
    "paper":  "#FFFFFF",
    "vellum": "#F0EBE3",  # CLEO chat
    "smoke":  "#E8E2D8",  # dividers
    "expedition": "#D45028",  # primary CTA / Cairo
    "terra":      "#C4622A",  # Giza
    "sky":        "#1C72B4",  # brand blue / CLEO
    "discovery":  "#8860D4",  # Luxor
    "verified":   "#2A7A50",  # success / Aswan
    "caution":    "#D48A10",  # amber warnings
    "ink":   "#1A1714",  # primary text
    "stone": "#6A6058",  # secondary text
}

# Region → hex (for any chart keyed by region).
REGION_COLORS = {
    "Cairo":      "#D45028",
    "Giza":       "#C4622A",
    "Alexandria": "#1C72B4",
    "Luxor":      "#8860D4",
    "Aswan":      "#2A7A50",
    "Hurghada":   "#0EA5E9",
    "Marsa Alam": "#0891B2",
    "Sinai":      "#7C3AED",
}

# Category → hex.
CATEGORY_COLORS = {
    "historical":     "#B45309",
    "cultural":       "#7C3AED",
    "natural":        "#059669",
    "entertainment":  "#EC4899",
    "religious":      "#1E3A5F",
    "shopping":       "#D97706",
    "dining":         "#EA580C",
    "accommodation":  "#0EA5E9",
}

# Two-condition contrast for the keystone ablation. The "full system" uses the
# brand's verified green (the success colour); the degraded baseline uses
# expedition red. This makes the headline chart read correctly at a glance.
ABLATION_COLORS = {
    "full":     VOYO_COLORS["verified"],   # VOYO + VROOM
    "baseline": VOYO_COLORS["expedition"], # LLM-only (naive times)
}

# Accessible sequential ramp for heatmaps / single-series gradients.
SEQUENTIAL = ["#F0EBE3", "#E8C9A8", "#D48A10", "#C4622A", "#7A2E12"]

_THEME_APPLIED = False


def apply_theme() -> None:
    """Apply the VOYO thesis style to matplotlib's rcParams (idempotent)."""
    global _THEME_APPLIED
    if _THEME_APPLIED:
        return

    matplotlib.rcParams.update({
        # Sans-serif throughout; size tuned for a ~6-inch thesis column.
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
        "font.size": 10,

        # Warm paper backgrounds, never pure white.
        "figure.facecolor": VOYO_COLORS["page"],
        "axes.facecolor":   VOYO_COLORS["paper"],
        "savefig.facecolor": VOYO_COLORS["paper"],

        # Text colours from the token set.
        "text.color":       VOYO_COLORS["ink"],
        "axes.labelcolor":  VOYO_COLORS["ink"],
        "xtick.color":      VOYO_COLORS["stone"],
        "ytick.color":      VOYO_COLORS["stone"],
        "axes.edgecolor":   VOYO_COLORS["smoke"],

        # Hairline grid, y-axis only (Tufte discipline).
        "axes.grid":        True,
        "axes.axisbelow":   True,
        "grid.color":       VOYO_COLORS["smoke"],
        "grid.linewidth":   0.6,
        "grid.alpha":       0.9,

        # Spines: keep left + bottom only, thin.
        "axes.spines.top":   False,
        "axes.spines.right": False,
        "axes.linewidth":    0.8,

        # Legend: no frame.
        "legend.frameon":  False,
        "legend.fontsize": 9,

        # Subtle ink outline on bars/patches.
        "patch.linewidth": 0.5,
        "patch.edgecolor": VOYO_COLORS["ink"],
    })
    _THEME_APPLIED = True


def titled_figure(
    title: str,
    subtitle: Optional[str] = None,
    width: float = 7.5,
    height: float = 4.2,
) -> plt.Figure:
    """Return a figure with a weighted title + muted subtitle line.

    Layout uses constrained_layout so labels never clip — important for the
    multi-panel ablation figure.
    """
    apply_theme()
    fig, ax = plt.subplots(figsize=(width, height), constrained_layout=True)
    fig.suptitle(title, fontsize=13, fontweight="bold", color=VOYO_COLORS["ink"],
                 x=0.02, ha="left", y=0.98)
    if subtitle:
        fig.text(0.02, 0.935, subtitle, fontsize=9, color=VOYO_COLORS["stone"],
                 ha="left", style="italic")
    return fig


def save_figure(fig: plt.Figure, name: str, fig_dir: str | Path) -> dict:
    """Save a figure as PNG (300 DPI) + PDF (vector) and return the paths.

    Every chart in the results section goes through here so output format is
    uniform. PDFs are the print-quality artefact for the thesis; PNGs are the
    preview artefact for the presentation slides.
    """
    out = Path(fig_dir)
    out.mkdir(parents=True, exist_ok=True)
    stem = out / name
    png = stem.with_suffix(".png")
    pdf = stem.with_suffix(".pdf")
    fig.savefig(png, dpi=300, bbox_inches="tight")
    fig.savefig(pdf, bbox_inches="tight")
    return {"png": str(png), "pdf": str(pdf)}


def color_cycle(keys: Sequence[str], mapping: dict) -> list:
    """Resolve a sequence of keys (e.g. region names) to brand colours,
    falling back to the ink/stone pair for anything unmapped."""
    return [mapping.get(str(k), VOYO_COLORS["sky"]) for k in keys]
