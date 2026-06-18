# R6 Gorilla — VERBATIM QUOTE BANK
> Source: arXiv:2305.15334 via https://ar5iv.labs.arxiv.org/html/2305.15334 (fetched 2026-06-16).

## Q1 — Headline result
> "We release Gorilla, a finetuned LLaMA-based model that surpasses the performance of GPT-4 on writing API calls. When combined with a document retriever, Gorilla demonstrates a strong cap[ability] [...]"
- **Locator:** arXiv:2305.15334, Abstract.

## Q2 — APIBench dataset
> "we introduce APIBench, a comprehensive dataset consisting of HuggingFace, TorchHub, and TensorHub APIs."
- **Locator:** arXiv:2305.15334, Abstract / §APIBench.

## Q3 — 1,645 APIs scale
> "model cards for each of these 1,645 API calls into a json object with the following fields: {domain, framework, functionality, api_name, api_call, api_arguments, environment_requirements, example_code, performance, and description.}"
- **Locator:** arXiv:2305.15334, §Dataset construction.

## Q4 — Head-to-head accuracy (results table, TorchHub zero-shot)
Verbatim table row: "GPT-4 (0-shot) 38.70 36.55 24.7 [...] Gorilla (0-shot) 59.13 6.98 33.87 [...]"
- **Locator:** arXiv:2305.15334, Results table (accuracy / hallucination columns). Gorilla 59.13% vs GPT-4 38.70% accuracy; Gorilla hallucination 6.98% vs GPT-4 36.55%.

## Q5 — Retrieval reduces hallucination
> "The successful integration of the retrieval system with Gorilla demonstrates the potential for LLMs to use tools more accurately, keep up w[ith] [...]"
- **Locator:** arXiv:2305.15334, §APIBench / retrieval discussion.

---
### Accuracy flag
The prior lit-review stat "59.13% vs GPT-4 38.70% on TorchHub; 6.98% vs 36.55% hallucination" is **VERIFIED verbatim** from the results table (the numbers appear exactly as "59.13 6.98" and "38.70 36.55"). Safe to cite. Note these are the **zero-shot** rows.
