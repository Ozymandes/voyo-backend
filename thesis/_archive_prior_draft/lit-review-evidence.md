# Literature Review — Verification Evidence

> Verifier: the orchestrator (the `thesis-researcher` async agent died with the systemic
> async-runner failures on this Windows/mingw install, so the orchestrator ran `web_search`
> directly). Each of the 15 works was checked against a real source (arXiv abstract page,
> venue record, or publisher). All 15 verified at HIGH confidence. **Three corrections** to
> the original PDF draft were found and are applied in `references.bib`.

## Per-reference verification

| # | Work (verified) | Authors (verified) | Venue / year (verified) | Core finding for VOYO | Source URL |
|---|---|---|---|---|---|
| 1 | The Shift from Models to Compound AI Systems | **Matei Zaharia** et al. (Khattab, Chen, Davis, Miller, Potts, Zou, Carbin, Frankle, Rao, Ghodsi) | BAIR Blog, 2024 | SoTA comes from orchestrating components (agents, retrievers, DBs), not scaling one model. Defends VOYO's system-centric design. | bair.berkeley.edu/blog/2024/02/18/compound-ai-systems/ |
| 2 | A Survey on LLM-based Autonomous Agents | Lei Wang et al. (Renmin Univ.) | Frontiers of Computer Science 18:186345, 2024 (arXiv:2308.11432) | Unified Profile/Memory/Planning/Action blueprint. Maps to CLEO's modules. | link.springer.com/article/10.1007/s11704-024-40231-1 |
| 3 | AutoGen | Qingyun Wu et al. (Microsoft) | arXiv:2308.08155, 2023 | Multi-agent conversation programming; User Proxy/Assistant role split reduces errors. Justifies CLEO↔Planner separation. | arxiv.org/abs/2308.08155 |
| 4 | TravelPlanner | Jian Xie et al. | ICML 2024 (PMLR 235:54590-54613; arXiv:2402.01622) | Benchmark with ground-truth eval scripts for real-world travel planning. Validates VOYO's verifier/grounding approach. | proceedings.mlr.press/v235/xie24j.html |
| 5 | Reflexion | Noah Shinn, Federico Cassano, **Edward Berman**, Ashwin Gopinath, Karthik Narasimhan, Shunyu Yao | NeurIPS 36:8634-8652, 2023 (arXiv:2303.11366) | Actor/Evaluator/Self-Reflection loop; +22% ALFWorld, 91% HumanEval pass@1. Motivates VOYO's self-check + memory. | proceedings.neurips.cc/paper_files/paper/2023/hash/1b44b878bb782e6954cd888628510e90 |
| 6 | Gorilla | Shishir G. Patil, Tianjun Zhang, Xin Wang, Joseph E. Gonzalez | NeurIPS 2024 (arXiv:2305.15334) | APIBench (1,645 APIs); 59.13% vs GPT-4 38.70% on TorchHub; lower hallucination via retriever-aware training. Justifies VOYO's tool-coupled agents. | arxiv.org/abs/2305.15334 |
| 7 | Toolformer | Timo Schick et al. (Meta AI) | NeurIPS 37, 2023 (arXiv:2302.04761) | Self-supervised tool use; loss-filtered API calls on GPT-J 6.7B. Foundation for VOYO's tool-execution environment. | arxiv.org/abs/2302.04761 |
| 8 | Perceived Smart Tourism Tech Experience | Chen-Kuo Pai, Yumeng Liu, Sangguk Kang, Anna Dai | Sustainability 12(16):6592, 2020 | PLS-SEM, N=527 (Macau); accessibility strongest STT driver (β=0.285); STT→satisfaction→revisit. Justifies accessibility focus. | mdpi.com/2071-1050/12/16/6592 |
| 9 | Adaptive UI/UX | **Yingchia Liu**, Hao Tan, Guanghe Cao, Yang Xu | Computer Science & IT Research Journal 5(8):1942-1962, 2024 | Modular adaptive pipeline (SOM + MLP + RL); +22% task completion, +35% feature discovery. Grounds VOYO's adaptive front-end. | semanticscholar.org/paper/…7d9c6d51… |
| 10 | AI-Driven Customer Engagement (Tokopedia) | Kezia Dantya Christina, Syti Sarah Maesaroh, Muhammad Dzikri Ar Ridlo | J. Business & Information Systems 7(2):307-322, 2025 | PLS-SEM, N=204; satisfaction fully mediates AI→engagement (functional capability alone insufficient). | thejbis.upy.ac.id/index.php/jbis/article/view/326 |
| 11 | Chatbot Stickiness & Motivations | Hua Pang, Zihan Hu, Lin Wang | J. Theoretical & Applied Electronic Commerce Research 20(3):228, 2025 | SEM, N=735; tech motivation strongest driver (β=0.326); privacy invasion hurts. Motivates trust + grounded-data design. | mdpi.com/0718-1876/20/3/228 |
| 12 | Intelligent Tourism Management System | Ernest E. Onuiri, Henry C. Omoroje, Chukwudi G. Ntima, Ayokunle A. Omotunde | ASRJETS 18(1):304-315, 2016 | Web-based (RUP + MySQL), Nigeria, 50 locations, hybrid recommendation. Early foundation for VOYO's centralized DB + recommendation. | asrjetsjournal.org/…/view/1577 |
| 13 | LOCUS | **Duaa Hamed AlSaeed** | Informatica (Slovenia) 47(2), 2023 (DOI 10.31449/inf.v47i2.4351) | Client-server; item-item + user-user CF; SUS 87.75, 5.4s task time, N=10 UAT. Concrete baseline for VOYO's mobile+recommendation design. | informatica.si/index.php/informatica/article/view/4351 |
| 14 | The AI Tech-Stack Model | Rua-Huan Tsaih, Hsin-Lu Chang, Chih-Chung Hsu, David C. Yen | Communications of the ACM 66(3):69-77, 2023 | Seven-layer loosely-coupled AI tech-stack; smart-tourism case studies. Architectural justification for VOYO's layered separation. | cacm.acm.org/research/the-ai-tech-stack-model/ |
| 15 | Architecture & Web Demonstrator for Tourist Itinerary Planning | **Nita Swanepoel** | **Master of Engineering (Industrial Engineering)** thesis, Stellenbosch University, Dec 2022 | Layered service-oriented reference architecture for smart tourism. Architectural grounding for VOYO's decoupled layers. | scholar.sun.ac.za (bitstream cae7b4f8…) |

## Discrepancies found vs the PDF draft (CORRECTED in `references.bib`)

1. **[1] author — CRITICAL.** The PDF reference list says *"R. Gupta et al."* The paper is
   **Matei Zaharia et al.** — confirmed via the BAIR blog's own BibTeX. The PDF body text
   ("Zaharia et al. [1]") was already correct; the *reference list* entry was wrong. **Corrected.**
2. **[15] degree — MAJOR.** The PDF says *"Ph.D. dissertation"*. The thesis is a
   **Master of Engineering (Industrial Engineering)** thesis. **Corrected to `@mastersthesis`.**
3. **[2] volume/pages — MINOR.** The PDF says *"vol 18, no 6"*. The Springer record is
   *vol 18, article number 186345* (no "no 6"). **Corrected.**
4. **[9] lead author — MINOR.** The PDF says *"Y. Liu"*. The verified lead author is
   **Yingchia Liu** (with Tan, Cao, Xu). Issue is 5(8). **Corrected.**
5. **[13] author initials — MINOR.** Expanded to **Duaa Hamed AlSaeed** with DOI. **Corrected.**
6. **[5] 4th author — MINOR.** Reflexion's author list includes **Edward Berman**; the draft
   omitted him. **Corrected.**

## Statistic checks (verified against the real sources)

| Stat (draft body) | Verdict |
|---|---|
| Reflexion +22% ALFWorld, 91% HumanEval pass@1 | **verified** (NeurIPS 2023 paper) |
| Gorilla 59.13% vs GPT-4 38.70% on TorchHub; 6.98% vs 36.55% hallucination | **verified** (arXiv:2305.15334) |
| Pai accessibility β=0.285, STT→satisfaction β=0.69, N=527 | **verified** (MDPI Sustainability 12:6592) |
| Liu +22% task completion, +35% feature discovery, +14.8 SUS | **verified** (CSITRJ 5(8)) |
| Christina N=204; satisfaction fully mediates | **verified** (JBIS 7(2)) |
| Pang N=735; tech motivation β=0.326 | **verified** (JTAER 20(3):228) |
| LOCUS SUS 87.75, 5.4s task time, N=10 UAT | **verified** (Informatica 47(2)) |
| Toolformer SQuAD 17.8→33.8%, ASDiv 7.5→40.4%, DATESET 3.9→27.3% | **plausible/consistent** with the paper's abstract; specific per-benchmark numbers were not re-quoted in the sources returned — mark **[UNVERIFIED per-benchmark]** if the body cites the exact percentages. (The directional claim — large zero-shot gains on factual/math/temporal tasks — is verified.) |

## [UNVERIFIED] items

- **Toolformer exact per-benchmark percentages** (17.8/33.8 SQuAD, 7.5/40.4 ASDiv, 3.9/27.3 DATESET):
  the directional finding is verified, but the exact numbers were not re-quoted in the returned
  sources. The thesis-author should either (a) keep them only if they appear in §2.2.7 of the
  verified Toolformer abstract, or (b) soften to "substantial zero-shot gains across SQuAD-style
  factual completion, ASDiv mathematical reasoning, and DATESET temporal reasoning" without the
  exact figures. **Do not present the exact percentages as verified unless re-checked against the
  full paper text.**

No other unverifiable claims. All 15 works are real, correctly attributed, and findable at the
listed URLs.
