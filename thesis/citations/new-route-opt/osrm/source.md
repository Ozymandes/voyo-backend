# OSRM-PAPER — Luxen & Vetter (2011) — CITATION SOURCE

> **TIER A — PRIMARY-ACADEMIC** (per `thesis/criteria/thesis-criteria.md` §2). The academic
> routing reference for VOYO's distance-matrix infrastructure. Cite THIS for the *algorithmic
> basis*; pair with `thesis/citations/software/osrm.md` for the *running tool*.

## Verified metadata (Semantic Scholar + DBLP + OpenAlex + Crossref + README, 2026-06-17)
- **Title:** Real-time routing with OpenStreetMap data
- **Authors:** Dennis Luxen (Karlsruhe Institute of Technology, Institute of Theoretical
  Computer Science); Christian Vetter (Nokia GmbH, Berlin) — affiliations per Crossref API.
- **Venue:** Proceedings of the 19th ACM SIGSPATIAL International Conference on Advances in
  Geographic Information Systems, **GIS '11**, Chicago, IL, Nov 1–4 2011.
- **Pages:** 513–516 (numpages = 4) — a short conference paper.
- **DOI:** **10.1145/2093973.2094062** — verified (Crossref + DBLP + S2 + README).
- **DBLP key:** `conf/gis/LuxenV11` — verified.
- **ISBN:** 978-1-4503-1031-4 (per README canonical BibTeX block).
- **Semantic Scholar paperId:** `04314c6f9e2f472aeb4b81594b193ba1fa55458d`.
- **OpenAlex work id:** `doi:10.1145/2093973.2094062` (Work W2096892483 lineage).
- **Open access:** CLOSED at the publisher (`openAccessPdf.status = CLOSED` on S2;
  OpenAlex `best_oa_location: null`; `is_oa: false`). **However**, the publisher's
  *abstract* + *References list* are rendered on the public ACM landing page, which the
  Internet Archive Wayback Machine has snapshotted; the live ACM page is Cloudflare-blocked
  to curl/non-browser clients, but the Wayback copy is reachable and quotable.

## STATUS: ✅ VERIFIED (Tier A) — abstract + References fetched verbatim 2026-06-17
The closed-access ACM abstract + the paper's published References list were fetched
verbatim from the Internet Archive Wayback Machine snapshot of the canonical
`dl.acm.org/doi/10.1145/2093973.2094062` page (snapshot timestamp 2025-06-04 18:29:10 UTC).
The fetched text was cross-checked against two independent sources (OpenAlex
`abstract_inverted_index`, Google Scholar's `gs_rs` snippet) — all three agree word-for-word
on the abstract's opening paragraph. **3 verbatim quotes** (full abstract; CH/speedup
lineage via References [1] + [4]; OSM-data pipeline claim from the abstract itself) are
populated in `quotes.md`. The 4-page *body* text remains paywalled (no institutional login
available in this environment) — see `quotes.md` honesty flag for what is and isn't
quotable.

## Fetch recipe (what was tried; what worked)
1. ❌ `dl.acm.org/doi/10.1145/2093973.2094062` direct — **Cloudflare 403** "Just a moment…".
2. ✅ Wayback Machine `web.archive.org/web/20250604182910/https://dl.acm.org/doi/10.1145/2093973.2094062`
   — **HTTP 200**, returns the snapshot of the publisher's landing page (abstract + References).
3. ✅ OpenAlex API `api.openalex.org/works/doi:10.1145/2093973.2094062` — abstract
   `inverted_index` (first 50 words verbatim; same as Wayback). Crossref API: abstract=null.
4. ✅ DBLP `dblp.org/rec/conf/gis/LuxenV11.{bib,html}` — BibTeX metadata only (no abstract).
5. ✅ OSRM GitHub README `raw.githubusercontent.com/Project-OSRM/osrm-backend/master/README.md`
   — verbatim canonical BibTeX block (lines 210–228) + algorithm-pipeline enumeration (line 56).
6. ❌ ResearchGate — 403 to non-browser UA.
7. ✅ Google Scholar `gs_rs` snippet — corroborates first ~70 words of the Wayback abstract.
8. ❌ Author homepage / KIT CS publication list — no specific abstract mirror located
   (Luxen's personal page not indexable from this environment).
9. ❌ CORE.ac.uk API — 404.

## Intended thesis use (criteria.md §2.3, §3 Ch3)
- **§2.3 route-opt crux / Ch3 Methodology:** the academic citation for "real-time routing
  on OSM data via Contraction Hierarchies on continental-sized networks" — grounds VOYO's
  OSRM distance-matrix layer's algorithmic lineage. Pair with the software citation
  (`thesis/citations/software/osrm.md`) for the running system.
- Always cite as: *Luxen, D., & Vetter, C. (2011). Real-time routing with OpenStreetMap
  data. In Proceedings of the 19th ACM SIGSPATIAL International Conference on Advances in
  Geographic Information Systems (GIS '11), pp. 513–516. DOI: 10.1145/2093973.2094062.*
