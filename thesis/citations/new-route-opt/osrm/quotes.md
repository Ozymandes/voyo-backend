# OSRM-PAPER — VERBATIM QUOTE BANK

> **STATUS: FULL-TEXT VERIFIED (Tier A).** Abstract + References fetched verbatim 2026-06-17
> from the Wayback Machine snapshot of the closed-access ACM dl.acm.org page. **Body text
> (all 4 pages) additionally extracted 2026-06-17 from the provided full PDF**
> (`thesis/citations/pdfs/OSRM-PAPER_luxen2011.pdf`) — so body-level algorithmic claims (CH
> query time, vanishing-bottlenecks, Dijkstra-scaling) are now quotable. Cross-checked
> against OpenAlex + Google Scholar.

## Q1 — Full abstract — VERBATIM
> "Routing services on the web and on hand-held devices have become ubiquitous in the past couple of years. Websites like Bing or Google Maps allow users to find routes between arbitrary locations comfortably in no time. Likewise onboard navigation units belong to the off-the-shelf equipment of virtually any new car. The amount of volunteered spatial data of the OpenStreetMap project has increased rapidly in the past five years. In many areas, the data quality already matches that of commercial map data, if not outright surpass it. We demonstrate both a server and a hand-held device based implementation working with OpenStreetMap data. Both applications provide real-time and exact shortest path computation on continental sized networks with millions of street segments. We also demonstrate sophisticated real-time features like draggable routes and round-trip planning."
- **Locator:** Luxen & Vetter (2011), *Abstract*. Wayback snapshot of the canonical ACM
  dl.acm.org page (`web.archive.org/web/20250604182910/https://dl.acm.org/doi/10.1145/2093973.2094062`).
  First 50 words cross-verified identical against OpenAlex `abstract_inverted_index`; first
  ~70 words identical against Google Scholar `gs_rs` snippet.

## Q2 — Contraction-hierarchy / speedup lineage — VERBATIM (from the published References list)
> "[4] R. Geisberger, P. Sanders, D. Schultes, and D. Delling. Contraction Hierarchies: Faster and Simpler Hierarchical Routing in Road Networks. In C. C. McGeoch, editor, Proceedings of the 7th Workshop on Experimental Algorithms (WEA'08), volume 5038 of Lecture Notes in Computer Science, pages 319--333. Springer, June 2008."
- **Locator:** Luxen & Vetter (2011), **References, entry [4]** (same Wayback URL). The paper
  also cites reference [1] (Bauer, Delling, Sanders et al., "Combining Hierarchical and
  Goal-Directed Speed-Up Techniques for Dijkstra's Algorithm", ACM JEA 15(2.3), 2010) — i.e.
  the paper sits squarely in the CH / speed-up-techniques-for-Dijkstra lineage.

### Q2-supporting (software locator, not the paper) — OSRM README enumerates today's pipelines
> "There are two pre-processing pipelines available: - Contraction Hierarchies (CH) - Multi-Level Dijkstra (MLD) [...] We recommend using MLD by default except for special use cases such as very large distance matrices where CH is still a better fit for the time being."
- **Locator:** `Project-OSRM/osrm-backend` README, "Quick Start" section. Permalink
  `github.com/Project-OSRM/osrm-backend/blob/1c66f8e33b265113c9afd50fff8b0b1d8aadc8c6/README.md`.
  Use for the running system; pair with the paper's [4] for the academic citation.

## Q3 — OSM-data pipeline claim — VERBATIM (from the abstract)
> "The amount of volunteered spatial data of the OpenStreetMap project has increased rapidly in the past five years. In many areas, the data quality already matches that of commercial map data, if not outright surpass it. We demonstrate both a server and a hand-held device based implementation working with OpenStreetMap data. Both applications provide real-time and exact shortest path computation on continental sized networks with millions of street segments."
- **Locator:** Luxen & Vetter (2011), **Abstract** (sub-section). Same Wayback URL as Q1.

## Q4 — BibTeX block the project itself publishes (verbatim, README)
> "@inproceedings{luxen-vetter-2011, author = {Luxen, Dennis and Vetter, Christian}, title = {Real-time routing with OpenStreetMap data}, booktitle = {Proceedings of the 19th ACM SIGSPATIAL International Conference on Advances in Geographic Information Systems}, series = {GIS '11}, year = {2011}, isbn = {978-1-4503-1031-4}, location = {Chicago, Illinois}, pages = {513--516}, numpages = {4}, url = {http://doi.acm.org/10.1145/2093973.2094062}, doi = {10.1145/2093973.2094062}, publisher = {ACM}, address = {New York, NY, USA} }"
- **Locator:** `Project-OSRM/osrm-backend` README, "References in publications" (master
  commit `1c66f8e`). Authoritative citation form — pages **513–516**, 4pp, series **GIS '11**.

## Q5 — Contraction Hierarchies query/preprocessing time (FULL BODY, from the PDF) — VERBATIM
> "Contraction Hierarchies (CH) [4] have a very convenient trade-off between preprocessing and query time. Road networks of continental size can be preprocessed within a matter of minutes and queries run in the order of about a hundred microseconds."
- **Locator:** Luxen & Vetter (2011), §Contraction Hierarchies (body). Full-text PDF
  `thesis/citations/pdfs/OSRM-PAPER_luxen2011.pdf`, 4pp.

## Q6 — Vanishing Bottlenecks: routing is no longer the bottleneck (FULL BODY) — VERBATIM
> "We have seen that the actual routing algorithm runs in the order of a few (server) to a hundred milliseconds (hand-held) on data covering the European continent. Thus, routing is not a bottleneck anymore, and other components become obstacles."
- **Locator:** Luxen & Vetter (2011), §Vanishing Bottlenecks (body). Full-text PDF.

## Q7 — Motivation: Dijkstra does not scale (FULL BODY) — VERBATIM
> "Finding shortest paths in a road network is a problem that was solved in the early ages of computation. Unfortunately Dijkstra's seminal algorithm does not scale to large graphs [...]"
> "[the algorithm engineering community] developed algorithms and data structures that provide substantial speedups over Dijkstra's algorithm and guaranteed optimal routes."
- **Locator:** Luxen & Vetter (2011), §Introduction (body). Full-text PDF.

---
### Accuracy / honesty flags for the thesis author
- ✅ **FULL-TEXT VERIFIED 2026-06-17.** The provided PDF supplies the complete 4-page body.
  Body-level claims now quotable: CH preprocessing in minutes / queries ~100 µs (Q5);
  routing no longer a bottleneck, few–100 ms server/hand-held on continental data (Q6);
  Dijkstra's scaling limit + CH speedup motivation (Q7).
- The paper is **4 pages** (pp. 513–516) — a short conference paper; abstract + body together
  carry all load-bearing claims.
- Cite the *abstract/body* for "real-time shortest-path on continental-sized OSM networks";
  cite *reference [4]* (Geisberger et al. 2008) for the CH algorithm itself.
- Authors confirmed from body: **Dennis Luxen (Karlsruhe Institute of Technology) and
  Christian Vetter (Nokia)**.
