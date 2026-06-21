"""
LLM-as-judge evaluator for CLEO — the semantic metric layer.

The existing 7 metric calculators (tests/academic/metric_calculators.py) are
deterministic but surface-level: keyword overlap, regex, counter-based entity
checks. They cannot tell whether an answer is actually FAITHFUL to the
database (the core VOYO "nothing fabricated" claim) or merely keyword-similar.

This module adds three Groq-judged dimensions, designed to complement (never
replace) the heuristic set:

  • groundedness  — does the answer stick to facts supportable by VOYO's DB
                    + tool sources, or does it fabricate? (the thesis claim)
  • relevance     — does it actually answer the question asked?
  • helpfulness   — is it genuinely useful travel advice?

Each is a 0.0–1.0 score with a one-line rationale, returned in the same shape
as the existing ``EvaluationResult`` so the two layers compose in one report.

The judge reuses the existing Groq client (no new provider). Results are cached
by (query+answer) hash so re-runs don't re-spend quota on identical content.
Determinism is controlled via temperature=0 + a strict JSON contract.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# The rubric the judge applies. Temperature 0 + this fixed rubric makes scores
# reproducible across runs (test-retest reliability), which matters for the
# thesis methodology section.
JUDGE_RUBRIC = """You are a strict, calibrated evaluator for VOYO's travel
assistant CLEO. Score the assistant's ANSWER to the USER's question on three
dimensions. Be rigorous — a 1.0 is rare and reserved for excellent answers.

groundedness (0.0–1.0): Does the answer avoid fabrication? It must not invent
  POIs, prices, hours, or facts that are unlikely to be true. If the answer
  includes a {SOURCES} block of evidence the assistant used, treat anything
  consistent with it as grounded. Penalise invented specifics heavily.
relevance (0.0–1.0): Does it actually address what the user asked, or does it
  dodge / change the subject?
helpfulness (0.0–1.0): Is it genuinely useful, actionable travel advice for an
  Egypt visitor? Generic filler scores low; specific, practical guidance high.

Return ONLY one JSON object, no markdown:
{"groundedness": <0-1>, "relevance": <0-1>, "helpfulness": <0-1>,
 "rationale": "<one short sentence>"}
"""


class EvaluationResult:
    """Mirrors tests.academic.metric_calculators.EvaluationResult so the deep
    metrics compose with the heuristic set in one report."""

    def __init__(self, name: str, score: float, passed: bool,
                 details: Optional[Dict] = None):
        self.name = name
        self.score = float(score)
        self.passed = bool(passed)
        self.details = details or {}


class LLMJudge:
    """Groq-backed judge producing groundedness/relevance/helpfulness scores."""

    PASS_BAR = 0.7  # a dimension "passes" at >= 0.7 (matches the heuristic suite)

    def __init__(self, model: Optional[str] = None):
        from src.cleo.config import get_llm_client
        self.llm = get_llm_client()
        self.model = model  # None → client default (llama-3.3-70b-versatile)
        self._cache: Dict[str, Dict[str, float]] = {}

    @staticmethod
    def _key(query: str, answer: str) -> str:
        return hashlib.md5((query + "\n||\n" + answer).encode("utf-8")).hexdigest()

    async def judge(self, query: str, answer: str,
                    sources: Optional[List[str]] = None) -> Dict[str, "EvaluationResult"]:
        """Return {dim: EvaluationResult} for the three dimensions.

        ``sources`` is the list of CLEO source pills / tool outputs (when
        available) — feeding the judge the evidence CLEO used lets it score
        groundedness against what was actually retrieved, not a guess.
        """
        key = self._key(query, answer)
        if key in self._cache:
            c = self._cache[key]
            return {d: EvaluationResult(f"judge_{d}", c[d], c[d] >= self.PASS_BAR,
                                        {"rationale": c.get("rationale", "")})
                    for d in ("groundedness", "relevance", "helpfulness")}

        src_block = ""
        if sources:
            src_block = ("\nEvidence CLEO used (treat as ground truth for "
                         "groundedness):\n" + "\n".join(f"- {s}" for s in sources[:8]))
        system = JUDGE_RUBRIC.replace("{SOURCES}", src_block or "no explicit sources")
        messages = [{"role": "system", "content": system},
                    {"role": "user",
                     "content": f"USER QUESTION:\n{query}\n\nCLEO ANSWER:\n{answer}"}]

        try:
            resp = await self.llm.generate_async(messages, temperature=0.0)
            content = (resp.content or "").strip()
            # Strip stray code fences.
            if content.startswith("```"):
                content = content.split("\n", 1)[-1]
                if content.endswith("```"):
                    content = content.rsplit("```", 1)[0]
            obj = json.loads(content)
            scores = {
                "groundedness": _clip(obj.get("groundedness", 0.0)),
                "relevance":    _clip(obj.get("relevance", 0.0)),
                "helpfulness":  _clip(obj.get("helpfulness", 0.0)),
            }
            rationale = str(obj.get("rationale", ""))[:200]
        except Exception as e:
            logger.warning(f"LLM judge failed (degrading to neutral 0.5): {e}")
            scores = {"groundedness": 0.5, "relevance": 0.5, "helpfulness": 0.5}
            rationale = f"judge-error: {e}"[:200]

        self._cache[key] = {**scores, "rationale": rationale}
        return {d: EvaluationResult(f"judge_{d}", scores[d], scores[d] >= self.PASS_BAR,
                                    {"rationale": rationale})
                for d in ("groundedness", "relevance", "helpfulness")}


def _clip(v: Any) -> float:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, f))
