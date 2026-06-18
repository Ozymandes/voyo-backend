# R5 Reflexion — VERBATIM QUOTE BANK
> Source: arXiv:2303.11366 via https://ar5iv.labs.arxiv.org/html/2303.11366 (fetched 2026-06-16).

## Q1 — 91% HumanEval result (headliner)
> "Reflexion achieves a 91% pass@1 accuracy on the HumanEval coding benchmark, surpassing the previous state-of-the-art GPT-4 that achieves 80%."
- **Locator:** arXiv:2303.11366, Abstract.

## Q2 — ALFWorld result (the precise figure)
> "ReAct + Reflexion significantly outperforms ReAct by completing 130 out of 134 tasks using the simple heuristic to detect hallucinations and inefficient planning. Further, ReAct + Reflexion learns to solve additional tasks by learning in 12 consecutive trials."
- **Locator:** arXiv:2303.11366, §4.1 Results (Figure 3 caption + text).

## Q3 — Self-reflection mechanism
> "[an agent] works through trial, error, and self-reflection. Generating useful reflective feedback is challenging since it requires a good understanding of where the model made mistakes (i.e. the credit assignment problem [...]) as well as the ability to generate a summar[y] [...]"
- **Locator:** arXiv:2303.11366, §1 Introduction.

## Q4 — Actor/Evaluator/Self-Reflection components
> "Initialize Actor, Evaluator, Self-Reflection: [...] Initialize policy [...]"
- **Locator:** arXiv:2303.11366, §3 Method (Reflexion algorithm).

---
### ⚠️ Accuracy flag — CORRECTS the prior lit-review
The prior `lit-review-evidence.md` stated **"Reflexion +22% ALFWorld."** That exact figure does **NOT** appear in the paper. The verbatim ALFWorld result is **"completing 130 out of 134 tasks"** (≈97%). **Do not write "+22% ALFWorld"** — replace with the verbatim "130 out of 134 tasks" figure (Q2). The abstract's broad improvement statement mentions "ALFWorld, 20% in HotPotQA, and 11% on HumanEval" in one sentence, which is where the "22" may have been garbled from; treat the per-benchmark "+22%" as **UNVERIFIED / drop it**. The **91% HumanEval** figure (Q1) *is* verbatim and safe to cite.
