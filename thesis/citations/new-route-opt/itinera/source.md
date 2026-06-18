# N1 — ITINERA: Integrating Spatial Optimization with Large Language Models for Open-domain Urban Itinerary Planning

- **STATUS: VERIFIED** (fetched full paper text: arXiv PDF 18.6 MB via wget + arXiv abstract page + GitHub README)
- **Type:** PAPER (peer-reviewed, EMNLP 2024 Industry Track; Best Paper at KDD UrbComp 2024)

## Bibliographic record
- **Authors:** Yihong Tang, Zhaokai Wang, Ao Qu, Yihao Yan, Zhaofeng Wu, Dingyi Zhuang, Jushi Kai, Kebing Hou, Xiaotong Guo, Han Zheng, Tiange Luo, Jinhua Zhao, Zhan Zhao, Wei Ma
  (affiliations: Tutu AI; University of Hong Kong; Shanghai Jiao Tong University; MIT; University of Michigan; Hong Kong Polytechnic University)
- **Title:** ITINERA: Integrating Spatial Optimization with Large Language Models for Open-domain Urban Itinerary Planning
- **Venue / Year:** EMNLP 2024 Industry Track Proceedings; also **Best Paper Award, KDD Urban Computing Workshop (UrbComp) 2024**
- **arXiv:** 2402.07204 (v5, 9 Jan 2025)
- **Primary URLs:**
  - arXiv abstract: https://arxiv.org/abs/2402.07204
  - ACL anthology PDF: https://aclanthology.org/2024.emnlp-industry.104.pdf
  - Code/README: https://github.com/YihongT/ITINERA
- **Note on fetch:** ar5iv returns a broken "Untitled Document" page for this id; the quotable full text was obtained from the arXiv PDF (`arxiv.org/pdf/2402.07204`, 20 pages, 18.6 MB) via wget. The abstract below is confirmed identical on the arXiv abstract page, the ACL anthology PDF page 1, and the repo README.

## Fetched-text summary (what I actually read)
20-page EMNLP Industry paper. Defines the **Open-domain Urban Itinerary Planning (OUIP)** task and proposes ITINERA, a system with **five LLM-assisted modules**: User-owned POI Database Construction (UPC), Request Decomposition (RD), Preference-aware POI Retrieval (PPR), **Cluster-aware Spatial Optimization (CSO)**, and Itinerary Generation (IG). The CSO module solves a **hierarchical traveling salesman problem (TSP)** to order POIs (§3.5). An ablation (Table 2, Shanghai dataset) shows removing CSO increases the Average Margin (route detour) metric from 86.0 to 242.8. §4.5 reports a deployed system evaluated by 464 users + 33 travel experts.

## Why it matters to VOYO (librarian's gloss — NOT a quote)
ITINERA is the closest prior art to VOYO's contribution: it explicitly argues that pure LLMs "lack the optimization capabilities required for planning tasks" and therefore bolts a spatial-optimization (hierarchical TSP) stage onto an LLM pipeline — exactly the LLM-coupled-to-solver pattern VOYO's CLEO→optimize stage instantiates. It directly grounds the thesis's "route-optimization-for-agentic-planning" framing and supplies a quantitative, ablation-backed argument for *why* a separate optimization module is necessary.

## Thesis sections supported
Ch2.2 (lit-review — the new "LLM + spatial optimization" theme / research gap), Ch2.3 tables, Ch3.4.3 (itinerary curate→optimize), Ch3.5.1 (routing/optimization choice).
