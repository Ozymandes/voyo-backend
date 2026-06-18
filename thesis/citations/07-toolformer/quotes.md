# R7 Toolformer — VERBATIM QUOTE BANK
> Source: arXiv:2302.04761 via https://ar5iv.labs.arxiv.org/html/2302.04761 (fetched 2026-06-16).

## Q1 — Self-supervised tool learning
> "This is done in a self-supervised way, requiring nothing more than a handful of demonstrations for each API. We incorporate a range of tools, including a calculator, a Q&A system, a search engine, a translation system, and a calendar."
- **Locator:** arXiv:2302.04761, Abstract.

## Q2 — Loss-filtered API calls (the mechanism)
> "We then execute these API calls and filter out all calls which do not reduce the loss [...] over the next tokens. All remaining API calls are interleaved with the original text [...]"
- **Locator:** arXiv:2302.04761, §2 Approach.

## Q3 — GPT-J 6.7B base, beats larger models
> "[Toolformer,] which is based on a pretrained GPT-J model [...] with 6.7B parameters, achieves much stronger zero-shot results, clearly outperforming a much larger GPT-3 model [...]"
- **Locator:** arXiv:2302.04761, §2 Approach / §Experiments.

## Q4 — SQuAD / LAMA result (Table 3 — verbatim, resolves prior UNVERIFIED flag)
Table 3 row, LAMA subsets:
```
                 SQuAD  Google-RE  T-REx
GPT-J            17.8      0        4.9
Toolformer       33.8     11.5      53.5
```
- **Locator:** arXiv:2302.04761, Table 3 (Results on subsets of LAMA).

## Q5 — ASDiv math result (Table 4 — verbatim)
Table 4 row:
```
                 ASDiv   SVAMP   MAWPS
GPT-J             7.5     5.2     9.9
Toolformer       40.4    29.4    44.0
```
- **Locator:** arXiv:2302.04761, Table 4 (Math results).

## Q6 — DATESET temporal result (Table 7 — verbatim)
Table 7 row:
```
                 TempLAMA  Dateset
GPT-J              13.7      3.9
Toolformer         16.3     27.3
```
- **Locator:** arXiv:2302.04761, Table 7 (Temporal results).

---
### ✅ RESOLVES the prior UNVERIFIED flag
The prior `lit-review-evidence.md` marked the Toolformer per-benchmark numbers **"SQuAD 17.8→33.8, ASDiv 7.5→40.4, DATESET 3.9→27.3"** as **[UNVERIFIED per-benchmark]**. They are now **VERIFIED VERBATIM** from the paper's Tables 3, 4, and 7 (Q4–Q6 above). The exact figures are safe to cite, with table-number locators.

(Note on Table 4 alignment: the lit-review mapped "ASDiv 7.5→40.4"; both 7.5 (GPT-J) and 40.4 (Toolformer) appear in Table 4 and are the same-column pair, confirming the mapping. The absolute improvement is large in all three tasks.)
