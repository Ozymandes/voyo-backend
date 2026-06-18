# Data-Gathering Pipeline & Verified POI Substrate — Deep-Dive Evidence

> **Scope:** VOYO's data layer end-to-end — the curated 310-POI substrate, the
> three scraping paths (PADI, experienceegypt.eg, **egymonuments.gov.eg** with
> its hidden Umbraco WebAPI), the enrichment pipeline (Wikipedia + LLM
> narrative grounding), the dual Egyptian/foreigner ticket-pricing migration,
> and the idempotent price upsert. Every claim below traces to a file opened
> with `read`/`bash`; symbols are tagged `path/to/file.py::symbol`.
>
> **Layer:** this is VOYO's **Ground-Truth Data** layer — the curated reality
> the Presentation, Gateway, and Agentic-Orchestration layers are anchored to.

---

## 1. Overview

VOYO is built around a deliberately small, deliberately verified catalog of
**310 Egyptian points of interest (POIs)** distributed across eight regions
(Cairo 40, Giza 39, Luxor 39, Aswan 42, Hurghada 27, Marsa Alam 40, Sinai 42,
Alexandria 41 — see `data/master_attractions.json`). The catalog is *not* an
open crawl of OpenStreetMap or Google Places; it is a hand-curated list
(`data/master_attractions_clean.py::MASTER_ATTRACTIONS`, 2 073 lines) whose
entries carry an `importance` tier (`Must-See` ×89, `Major` ×204, `World
Wonder` ×17), a category, and a `UNESCO_site` flag (92 set). The downstream
agentic and routing layers consume only these 310 POIs — there is no
free-text POI lookup against the open web at request time. That is the
central anti-hallucination bet of the architecture, mirroring the
LLM-plus-spatial-optimizer design of Tang et al. (2024), where a curated POI
pool is the precondition for a planner that "lacks the optimization
capabilities" on its own but is reliable because its action space is bounded.

Around that curated list VOYO builds three additional data assets:

1. **Official descriptions** from three scraped sources (PADI for natural /
   dive POIs, experienceegypt.eg for regional context, egymonuments.gov.eg for
   authoritative cultural / historical / museum records). These feed the
   narrative generator (`enrich_narratives.py`) as the *highest-priority*
   grounding source, ahead of Wikipedia.
2. **Dual Egyptian/foreigner ticket prices** — a domain-specific data
   feature captured exclusively from the Ministry's portal
   (egymonuments.gov.eg), stored in a JSONB column
   (`config/sql/004_ticket_prices.sql`), and loaded into the DB by a
   NULL-guarded idempotent SQL script (`data/ticket_prices_upsert.sql`, 58
   `UPDATE` statements).
3. **LLM-generated narratives + tips** for every POI, grounded in (a) the
   scraped official source when present, (b) Wikipedia otherwise, (c) Tavily
   as a last-resort search fallback. An audit trail
   (`thesis/evidence/narrative_sources.json`) records which source backed
   each generated paragraph.

The pipeline that ties scraping → enrichment → DB together has two parallel
implementations: a sequential baseline (`src/pipeline/enrichment_pipeline.py`)
and a Redis-cached, multi-threaded variant
(`src/pipeline/optimized_enrichment_pipeline.py`). Both ultimately write into
the same Supabase `pois` table defined by `src/database/schema.py::POI`.

---

## 2. How it works

### 2.1 The curated substrate — `data/master_attractions.json` + `_clean.py`

Every downstream stage references the same 310-entry list. Two representations
exist side-by-side and both are 310 entries:

- `data/master_attractions.json` — pure JSON, region → list of `{name,
  name_arabic, category, importance, search_queries, description,
  ticket_price, expected_rating, UNESCO_site}`. Categories: `historical` 130,
  `natural` 63, `entertainment` 40, `cultural` 39, `religious` 30,
  `shopping` 7, `dining` 1.
- `data/master_attractions_clean.py::MASTER_ATTRACTIONS` — the same data as a
  Python dict literal; consumed by both enrichment pipelines via
  `src/pipeline/master_attractions_loader.py::MasterAttractionsLoader`.

`MasterAttractionsLoader` exposes region / category / importance / UNESCO
slices (`get_attractions_by_importance`, `get_unesco_sites`,
`get_attractions_by_category`, `get_must_see_attractions`). The load path is
strict: it tries `master_attractions_clean` first, falls back to
`master_attractions_sample` only on ImportError, and warns if empty
(`_validate`). The "Cleaned version — no malls, focus on real
cultural/historical attractions" comment at the top of `_clean.py` documents
the deliberate editorial pass: this is not a fire-hose of OSM nodes but a
vetted travel corpus.

### 2.2 Three scraping paths, three discovery strategies

The pipeline does not invent a scraping strategy per source — each source
shaped its own.

#### (a) PADI dive sites — reverse-engineered Angular JSON API
`scripts/scrape/scrape_padi.py`

PADI's `/dive-sites/egypt` page is an Angular SSR *shell*: the visible HTML
has no dive-site data, which loads client-side from a JSON endpoint at
`https://travel.padi.com/api/v2/travel`. The scraper reverse-engineers three
endpoints (`scrape_padi.py:38-56`):

```python
# Map (pins) endpoint:
GET https://travel.padi.com/api/v2/travel/dsl/dive-sites/map/
    ?top_right=<lat>,<lng>&bottom_left=<lat>,<lng>
# Per-pin detail endpoint:
GET https://travel.padi.com/api/v2/travel/dsl/dive-sites/<id>/map/
# Human-written description, SSR-embedded on padi.com/dive-site/egypt/<slug>/
```

It then runs **five phases** (`main()`): (1) bounding-box pin discovery
across three Red Sea sub-regions (`Sinai`, `Hurghada`, `Marsa Alam` —
coordinates tuned so the Dahab trio and the Abu Nuhas wreck cluster are not
clipped); (2) per-pin detail fetch; (3) fuzzy **token-set matching** between
PADI titles and the 310-POI substrate; (4) SSR HTML scrape of the matched
slug; (5) capture of unmatched PADI pins (other Red Sea dive sites) for
review. The SSR description parser explicitly prefers the *full*
`collapsable-content` copy over the ~500-char truncated one
(`scrape_padi.py::parse_detail_page`).

#### (b) experienceegypt.eg — plain `requests` + BeautifulSoup
`scripts/scrape/scrape_experienceegypt.py`

The simplest path. The site is a *server-rendered* marketing portal behind
Cloudflare Rocket Loader only — no SPA, no JSON API, no auth. The scraper's
honesty contract is in its docstring: experienceegypt.eg has *no per-POI
structured data* — no tickets, no opening hours, no per-site official text —
only region/city-level marketing prose. So the scraper emits one
**region-level context row** per page (honest `matched=false`) and
*additionally* extracts a `matched=true` row only when a paragraph describes
exactly one named POI whose name leads the first sentence and whose
paragraph is short (≤200 chars — long paragraphs are multi-site city
overviews that would wrongly attach to the one indexed POI they happen to
name). The match guard (`scrape_experienceegypt.py::pois_in_text`,
`first_sentence`) is the key correctness mechanism.

#### (c) egymonuments.gov.eg — the hidden Umbraco WebAPI
The crown-jewel source. This is the Egyptian Ministry of Tourism &
Antiquities' official portal and the **only source that publishes per-POI
official descriptions and dual ticket fees**. There is no scraper in
`scripts/scrape/` for it — the engineering story is documented across four
`work/egymonuments_*.md` reports and the build script
`work/build_egymonuments_merge.py`. The chain has three stages (see §4 for
the challenge narrative):

1. **Catalog.** A single `POST /Umbraco/Api/MapsWebAPI/GetAllMapPins` with
   empty body `{}` returns 183 entries unpaginated. The spike proved this is
   reachable by plain `requests` with no browser, no cookies, no CSRF token
   (`work/egymonuments_spike.md`):

   ```python
   # work/egymonuments_catalog.md — the recipe
   r = requests.post(URL, json={},
       headers={"User-Agent":"Mozilla/5.0","Content-Type":"application/json"},
       timeout=30)
   items = r.json()["Data"]["ListItems"]   # 183
   ```

   The trimmed catalog (`data/egymonuments_catalog.json`) keeps 6 fields per
   entry (`Id, Title, Description, Latitude, Longitude, ContentUrlName`); the
   full payload is cached at
   `scripts/scrape/cache/egymonuments/GetAllMapPins.json` for provenance and
   re-processing without re-hitting the server. The 183 entries split 125
   monuments / 34 archaeological-sites / 24 museums by `ContentUrlName`
   segment.

2. **Child-item descriptions.** For each parent site/museum the scraper
   replays a second Umbraco endpoint whose URL contains a **literal,
   production typo** (`work/egymonuments_desc.md`):

   | `ContentUrlName` contains | Endpoint | pageSize |
   |---|---|---|
   | `archaeological-sites` | `POST …/InnersWebAPI/GetMonumnetByArcSiteId` | 100 |
   | `museums`              | `POST …/InnersWebAPI/GetAntiquitiesByMuseumId` | 50 |
   | `monuments`            | *(none — leaf nodes)* | — |

   Only 58 of 183 entries are parents; the 125 `/en/monuments/` entries are
   leaves and were empirically probed to have zero children. Output:
   `data/egymonuments_descriptions.json` (183 entries; 37 parents have ≥1
   child; 238 child rows total).

3. **Dual ticket fees from HTML.** Prices are **deliberately not in any JSON
   endpoint** (the spike verified: `GetEgyptianTreasureItemDetails` returns
   only location + open status, no price). They live only in
   server-rendered HTML inside `<div class="ticketPriceSec"> … <div
   class="ticketPriceDetails"> … <span style="white-space: pre-line">`. The
   parser (`work/egymonuments_price.md`):

   - **Section split** — matches `FOREIGNER(S)` and `EGYPTIAN(S)` at line
     start (word-only anchor, so `EGYPTIANS/ARABS:` parses too). The first
     foreigner and first egyptian section are used; secondary sub-blocks
     (e.g. Cairo Citadel's "Cart" ticket) never pollute the headline price.
   - **Value extraction** — within a section the *first* `Adult`/`Student`
     value wins (= the area-entry ticket). Both orders are accepted: `EGP
     700`, `EGP700`, `700 EGP`, `150EGP`.
   - **Currency integrity guard** — if a block says `$5` (Cairo Airport
     Museums), `foreigner_adult` is set to `null` rather than mislabeling
     USD as EGP.

   Output: `data/egymonuments_prices.json` (183 entries; **99 matched**, 84
   honestly `matched=false`). Sample (Cairo Citadel):

   ```json
   {"title": "Cairo  Citadel", "source_url": ".../cairo-citadel",
    "egyptian_adult": 60, "egyptian_student": 30,
    "foreigner_adult": 550, "foreigner_student": 275,
    "currency": "EGP", "matched": true,
    "price_block_raw": "Area entry ticket\nFOREIGNERS:\nAdult: EGP 550 / ..."}
   ```

   Headline price spread (EGP): foreigner adult median 220, mean 283, max
   2000 (Tomb of Seti I); egyptian adult median 20, mean 35, max 500.

### 2.3 The merge — `work/build_egymonuments_merge.py`

The merge is a **curated, manually reviewed 1:1 POI → gov.eg map** (76 pairs),
not a blind fuzzy join. The script carries the entire map inline as
`MATCH_MAP: Dict[poi_name, gov_id_str]`, with comments on each ambiguous pair
documenting *which* of two same-named Ministry records was chosen:

```python
MATCH_MAP = {
    "Giza Plateau": "1519",
    "Tomb of Seti I (KV17)": "4279",
    "Al-Nasir Muhammad Mosque": "1455",   # the Citadel mosque
                                           # (not the Mu'izz/Qalawun one)
    "Sultan Barquq Complex": "4232",      # al-Zahir Barquq, Mu'izz
                                           # (not the cemetery Farag one)
    ...
}
```

The script self-validates that every POI name exists in
`master_attractions.json` and every gov Id resolves to a standalone
description with a `source_url` — it raises `SystemExit(1)` on any mismatch.
It then writes three artifacts:

- **`data/enrichment_sources.csv` / `.xlsx`** — appended 76 `kind =
  official_gov` rows (130 → 206 rows; 97 total with `matched=true`
  distributed across kinds `authoritative` 18, `thin_tip` 3, `official_gov`
  76). Idempotent: rebuilds the `official_gov` section from `MATCH_MAP` on
  every run, dropping any previously-written rows of that kind.
- **`data/ticket_prices_upsert.sql`** — 58 idempotent `UPDATE` statements
  (76 matches − 18 with no dual gov price = 58). See §2.5.
- **`work/_egym_matchmap.json` + `work/_egym_stats.json`** — machine-readable
  provenance.

### 2.4 The enrichment pipeline — `src/pipeline/*.py`

Two pipeline variants. Both share a three-stage shape per POI from
`MASTER_ATTRACTIONS`:

**Baseline (`src/pipeline/enrichment_pipeline.py::VoyOEnrichmentPipeline.run`):**
(1) Google Places enrich (`GooglePlacesEnricher.enrich_attraction` —
text-search then details, merging coordinates, photos, opening hours,
ratings); (2) Wikipedia enrich
(`src/enrichers/wikipedia_enricher.py::WikipediaEnricher.enrich_poi` — adds
`historical_significance`, `historical_significance_arabic`,
`average_visit_duration`, `best_visit_times`, `tags`); (3) Egyptian price
derived from the foreigner price (`_calculate_egyptian_pricing`: 20% rule,
default 200 EGP / 40 EGP); (4) Supabase insert
(`SupabaseInserter.insert_poi`, with HTTP 409 → "already exists" treated as
warning not error). 200 ms rate-limit sleep per POI to respect the Google
Places free tier.

```python
# src/pipeline/enrichment_pipeline.py::VoyOEnrichmentPipeline.run
enriched = self.enricher.enrich_attraction(attraction)    # Google Places
if enriched:
    enriched = self.wikipedia_enricher.enrich_poi(enriched)  # Wikipedia
    enriched = self.enricher._calculate_egyptian_pricing(enriched)
    self.inserter.insert_poi(enriched)
```

**Optimized (`src/pipeline/optimized_enrichment_pipeline.py::OptimizedVoyOPipeline`):**
same three enrichers, plus three production-grade additions — Redis caching
of Google Places responses (`OptimizedGooglePlacesEnricher.cache`), a
`ThreadPoolExecutor` fan-out (`process_single_attraction` is documented as
thread-safe; stats updated under `self.stats_lock`), and a **Dead Letter
Queue** (`utils.dead_letter_queue.DeadLetterQueue`) that captures failed POIs
at each stage (`'google_places'`, `'database'`, `'unknown'`) into
`data/failed_pois_report.txt`. Config is externalized to
`config.pipeline_config.ConfigPresets.{fast,production,safe}`, varying
`max_workers` and `cache_ttl`. A separate orchestrator
(`src/pipeline/orchestrator.py::VOYOOrchestrator`) runs an alternative
`OSMScraper` → `GooglePlacesScraper` → `DataProcessor` → `batch_create_pois`
chain keyed on `target_pois_per_region`; it marks
`is_verified = poi.average_rating is not None` — a weaker notion of "verified"
than the curated substrate (§2.6).

#### LLM narrative grounding — `enrich_narratives.py` (repo root)

The script that produces the per-POI `narrative` column shown in the Flutter
app. It is the only LLM stage and **deliberately grounds every generation in
a fetched source before the LLM sees the prompt**. The grounding-priority
ladder (`enrich_narratives.py::process_poi`) is the architectural centerpiece
of the anti-hallucination strategy:

```python
# Grounding priority: (1) official scraped source, (2) Wikipedia,
# (3) Tavily fallback, (4) none.
official = OFFICIAL_SOURCES.get(_norm_name(poi['name']))
if official:                          # egymonuments / padi / experienceegypt
    sources_str = f'OFFICIAL source ({src_url}):\n{official["description"]}'
    grounded_kind = 'official'
else:
    wiki_text, wiki_url = grounding_fetch(poi['name'], poi.get('city'))
    ...
    else: grounded_kind = 'none'      # conservative — DB fields only
```

`OFFICIAL_SOURCES` is loaded from `data/enrichment_sources.{csv,xlsx}` —
the same file the egymonuments merge wrote into. The prompt
(`PROMPT_TEMPLATE`) explicitly forbids fabrication: "VERIFIED FACTS (use ONLY
these — never invent dates, names, dimensions, prices, or species)" and
"Banned phrases: rich history, must-see, hidden gem…". A **relevance guard**
in both `grounding_fetch` and `tavily_fetch` requires ≥1 shared significant
token between POI name and source title ("a wrong source is worse than no
source"). Output is split by `parse_narrative_tips()` into a `NARRATIVE:`
paragraph and a `TIPS:` list; the live write updates Supabase
`pois.narrative` + `pois.travel_tips`, and an audit record (grounding kind +
source URL) is appended to `thesis/evidence/narrative_sources.json`.

### 2.5 Dual ticket-pricing migration — `config/sql/004_ticket_prices.sql` + `data/ticket_prices_upsert.sql`

The Ministry publishes a **dual fee structure** structurally invisible to
Western scraping tools: every ticketed site has both a foreigner price and an
Egyptian/Arab price, often an order of magnitude apart (Giza Plateau:
foreigner 700 EGP, Egyptian 60 EGP; Karnak: 600 vs 40). VOYO models this
explicitly.

**Schema migration** (`config/sql/004_ticket_prices.sql`) adds a nullable
JSONB column with a CHECK constraint:

```sql
ALTER TABLE pois ADD COLUMN IF NOT EXISTS ticket_prices JSONB;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints
                   WHERE table_name = 'pois'
                     AND constraint_name = 'ticket_prices_structure') THEN
        ALTER TABLE pois ADD CONSTRAINT ticket_prices_structure
            CHECK (
                ticket_prices IS NULL OR (
                    ticket_prices ? 'egyptian' AND
                    ticket_prices ? 'foreigner' AND
                    ticket_prices ? 'currency' AND
                    jsonb_typeof(ticket_prices->'egyptian') = 'number' AND
                    jsonb_typeof(ticket_prices->'foreigner') = 'number' AND
                    ticket_prices->>'currency' = 'EGP'
                ));
    END IF;
END $$;
```

The DO block is required because PostgreSQL supports `ADD COLUMN IF NOT
EXISTS` but **not** `ADD CONSTRAINT IF NOT EXISTS` — the guarded block keeps
the migration re-runnable. The CHECK enforces exactly three keys, which is
why **student prices cannot go into the JSONB**: they are recorded only as
SQL `--` comments on the corresponding UPDATE line. The pre-existing scalar
`ticket_price` (`src/database/schema.py::POI.ticket_price`) is left intact as
a display fallback.

**Idempotent upsert** (`data/ticket_prices_upsert.sql`, 58 statements):

```sql
BEGIN;
-- Gate: (real POI match) AND (prices.json matched=true) AND
--       (egyptian_adult & foreigner_adult both non-null ints).
-- Guard: WHERE ticket_prices IS NULL  -> NEVER overwrites; re-runnable.
UPDATE pois SET ticket_prices = '{"egyptian":60,"foreigner":700,"currency":"EGP"}'
  WHERE name = 'Giza Plateau' AND ticket_prices IS NULL;
  -- student: egyptian=30, foreigner=350
UPDATE pois SET ticket_prices = '{"egyptian":500,"foreigner":2000,"currency":"EGP"}'
  WHERE name = 'Tomb of Seti I (KV17)' AND ticket_prices IS NULL;
  -- student: egyptian=250, foreigner=2000
...
COMMIT;
```

Two safety properties: (1) **never overwrites** — every statement is gated by
`ticket_prices IS NULL`, so a re-run is a no-op on already-populated rows;
(2) **name-keyed** — matched on `pois.name` (the DB exposes no slug), with
apostrophes `''`-escaped (`'Al-Rifa''i Mosque'`, `'Al-Mu''izz Street'`). 76
matched POIs − 58 with real dual fees = **18 with no gov-published price**
(Sphinx, Bent/Red Pyramids, free mosques and churches like Ibn Tulun,
Muhammad Ali, Hanging Church, Saint Catherine's). The migration was
independently reviewed in `review/egymonuments_review.md` with a live re-fetch
of the gov.eg source: 183/183 description match, 5/5 spot-checked prices
verbatim against the live `ticketPriceDetails` block.

### 2.6 What "verified" means

Three definitions coexist, by layer:

- **Curated substrate** (`master_attractions.json`) — the POI *exists as a
  real Egyptian attraction* because a human editor put it in the list with
  importance/category/UNESCO metadata. 310 / 310.
- **Per-POI `is_verified` flag** (`src/database/schema.py::POI.is_verified`,
  default `False`). Set to `True` by `SupabaseInserter.insert_poi` once the
  POI has been enriched through the pipeline; the orchestrator's weaker
  definition (`is_verified = poi.average_rating is not None`) is the
  *fallback* path.
- **Provenance verification** — every official description in
  `data/enrichment_sources.csv` carries `best_source_url` (a real
  `https://egymonuments.gov.eg/en/...` or `https://www.padi.com/dive-site/...`
  URL), and the raw cache under `scripts/scrape/cache/egymonuments/` (242
  files) preserves the original API response for auditability.

---

## 3. Why this design (decisions & tradeoffs)

### 3.1 Curated 310-POI list vs. open OSM crawl

**Choice:** hand-curated catalog. **Alternative:** the orchestrator's
`OSMScraper` chain (`src/pipeline/orchestrator.py`) already exists and can
pull hundreds of POIs per region. **Reason:** a small, vetted action space is
what makes the downstream LLM planner reliable. Tang et al. (2024) argue that
pure LLMs lack optimization capability; VOYO's symmetric argument is that
they also lack *reliable factual recall* for long-tail POIs, so the catalog
is the boundary at which human curation hands off to automation. The cost is
coverage: 310 POIs across all of Egypt is small, and the editorial comment
"no malls, focus on real cultural/historical attractions" in
`master_attractions_clean.py` makes the tradeoff explicit.

### 3.2 Three scraping sources instead of one

Each source fills a structural gap the others cannot:

| Source | Strength | Coverage on the 310-POI substrate |
|---|---|---|
| **egymonuments.gov.eg** | Official Ministry prose + dual fees | 76 POIs (24.5%), Cairo/Giza/Luxor/Aswan |
| **PADI** | Human-written dive-site descriptions | 18 authoritative + 85 extra captures, Red Sea only |
| **experienceegypt.eg** | Regional context | 5 region-context rows + 3 thin single-POI tips |

**Choice:** prefer gov.eg for `historical`/`cultural`/`religious` POIs and
PADI for `natural` POIs. **Alternative considered:** Wikipedia-only grounding.
**Reason:** Wikipedia is editable, sometimes inaccurate, and Western-perspective
biased on Egyptian sites; the Ministry is the *primary source* of ticket fees
(no other source publishes them). This priority order is encoded in
`enrich_narratives.py::process_poi` (official first, Wikipedia second).

### 3.3 JSONB `ticket_prices` vs. scalar columns

**Choice:** a single JSONB column
`{"egyptian":N,"foreigner":N,"currency":"EGP"}` with a CHECK constraint, plus
a nullable legacy scalar `ticket_price`. **Alternative considered:** two
columns `ticket_price_egyptian`, `ticket_price_foreigner`. **Reason (evident
from `004_ticket_prices.sql`):** JSONB lets the structure be validated
declaratively and lets future fields (a `student` tier, a `cars` tier — Cairo
Citadel publishes one) be added without a new migration. The CHECK enforces
exactly three keys for now, which is the tradeoff: the student tier is
currently lost from the JSONB (recorded only in SQL comments) — a deliberate
**constraint over convenience** choice so the data model can't drift.

### 3.4 Idempotent NULL-guarded upserts instead of `INSERT … ON CONFLICT`

**Choice:** `UPDATE … WHERE name = ? AND ticket_prices IS NULL`. **Reason:**
the build script keys on `name` because the live POI id is in the cloud
Supabase DB, which the scrape task was forbidden to touch (read-only data
gathering). `ticket_prices IS NULL` makes the script **re-runnable without
state**: a second run is a pure no-op, never overwriting a value that an
operator may have hand-edited in the dashboard. This pattern is paired with
the `DO $$ … IF NOT EXISTS … END $$` block in `004_ticket_prices.sql` for the
same re-runnability reason, and with the `idx_pois_narrative_null` partial
index in `config/sql/002_add_narrative.sql` so `enrich_narratives.py` can
efficiently find un-enriched rows.

### 3.5 Grounding-first LLM narrative generation

**Choice:** the LLM is the *last* stage, never the first. **Alternative:**
prompt the LLM with just the POI name and let it generate from parametric
memory. **Reason:** explicit anti-hallucination. The `PROMPT_TEMPLATE` line
"use ONLY these — never invent dates, names, dimensions, prices, or species"
is unenforceable on its own; it only works because the `VERIFIED FACTS`
section is populated from a fetched source. The audit trail
(`narrative_sources.json` per-POI `grounding_kind` ∈ {`official`,
`wikipedia`, `tavily`, `none`}) makes the policy machine-checkable for thesis
defensibility. This is exactly the design philosophy Tang et al. (2024)
recommend for hybrid systems: the LLM contributes fluency and structure; the
grounding layer contributes facts.

---

## 4. Challenges & solutions

### 4.1 The hidden Umbraco WebAPI discovery — *the* challenge story

The task framing assumed the Ministry portal was hard-blocked (browser-only,
HTTP 000 connection reset). The actual story, documented in
`work/egymonuments_spike.md`, is more interesting. A Playwright browser
capture of `https://egymonuments.gov.eg/en/monuments` revealed the Angular
SPA's data layer talks to a hidden Umbraco ASP.NET WebAPI at
`/Umbraco/Api/...`. The capture showed zero cookies and no XSRF/CSRF header
on any successful POST — the "anti-bot defense" was *not real*. Plain
`requests` POSTs with default UA, curl UA, and browser UA all returned HTTP
200 with the full 122 962-byte catalog. **The discovery was that the data
exists; the implementation was the boring realization that no defense needed
bypassing.** The spike documents this honestly:

> "The 'HTTP 000 / connection reset' premise in the task background is NOT
> REPRODUCIBLE and is wrong."

The endpoints surfaced from the Angular bundle
(`/Bundles/MainPortalAppBundles/main.js`, 1.44 MB) included
`MapsWebAPI/GetAllMapPins`, `InnersWebAPI/GetMonumnetByArcSiteId` (with a
**literal production typo "Monumnet"** — not VOYO's bug, the Ministry's),
`InnersWebAPI/GetAntiquitiesByMuseumId`, and
`MapsWebAPI/GetEgyptianTreasureItemDetails`. The typo had to be reproduced
verbatim or the endpoint returns 404.

### 4.2 Prices are not in any JSON endpoint

Even after the API was discovered, **prices are only in server-rendered
HTML**, inside the `ticketPriceSec` / `ticketPriceDetails` block. The
`GetEgyptianTreasureItemDetails` endpoint was the only price-shaped candidate
in the bundle but returns only `{Location, IsOpened, NextOpenTime, …}`. So
the price scraper had to GET each of the 183 `ContentUrlName` URLs and parse
the HTML with a custom regex/BS4 parser. This is the structural reason the
egymonuments chain is split into three stages (catalog JSON → children JSON →
HTML prices) instead of one. The HTML parser handles five quirks
(`work/egymonuments_price.md`): section-word-only anchoring for
`EGYPTIANS/ARABS:` variants, both orderings `EGP 700` and `700 EGP`, plural
`Adults:`, bare single-tier fallback (Workers' Town), and a currency guard
that refuses USD-labeled prices.

### 4.3 Name matching / transliteration — single-token collisions

POI-name matching across English, Arabic-transliterated, and Ministry-style
names is genuinely hard. Two complementary strategies are used:

1. **PADI matcher** (`scripts/scrape/scrape_padi.py::match`, `normalize`,
   `_tok_match`): stopword stripping (color words kept so "Blue Hole" ≠
   "Green Hole"; size words stripped so "Big Brother Island" = "Brother
   Islands"), then fuzzy `difflib.SequenceMatcher ≥ 0.85` per token for
   transliteration tolerance (`sha'ab` ≈ `shaab`, `shitan` ≈ `shaitan`). A
   curated `ALIASES` dict covers cases the fuzzy matcher is too conservative
   for (`"The Canyon (Dahab)": "/dive-site/egypt/the-canyon-8/"`).
2. **egymonuments merge** (`work/egymonuments_compile.md` §STEP 1):
   transliteration folding (`hassan↔hasan`, `khafre↔khefren↔chefren`,
   `sety↔seti`, `el↔al`, `ghouri↔ghuri`, `zuweila↔zuwayla`,
   `sakkara↔saqqara`, `zoser↔djoser`, `qaytbay↔qaitbay`,
   `mycerinus↔menkaure`, `ramesses↔ramses`), then a **distinctive
   strong-token** rule (len ≥ 4 after stopword removal) to avoid false
   positives.

The most concrete failure modes — and the manual review they triggered — are
documented in `work/egymonuments_compile.md`:

- **Museum artifacts that share a name token with a site** ("Khafre Statue",
  "Bracelets of King Ramesses II", "Bust of Neilos") are objects *inside* a
  museum, not POIs. Rejected.
- **Weak single-token collisions**: "ramses", "muhammad", "cairo", "aswan",
  "sharm", "marsa", "hasan"-alone, "nile", "town", "suez" all produced
  plausible-looking but wrong matches (e.g. "Marsa Matrouh Museum" → "Marsa
  Mubarak"; "Beni Hasan" → "Mosque of Sultan Hassan"). All rejected.
- **Ambiguous disambiguations resolved explicitly**: Al-Nasir Muhammad Mosque
  → the **Citadel** mosque (id 1455) not the Mu'izz/Qalawun one (30761);
  Sultan Barquq Complex → **al-Zahir on Mu'izz** (4232) not the cemetery
  Farag complex (30847); Wekalet El Ghouri → the **wikala** (30762),
  Al-Ghuri Complex → the **funerary complex** (30844). These are encoded as
  inline comments in `MATCH_MAP`.

The decision to curate the map by hand (rather than trust a fuzzy matcher)
is a deliberate **precision-over-recall** tradeoff: 76 verified matches
beats 100 noisy ones for a downstream LLM that would otherwise ingest wrong
descriptions.

### 4.4 84 unmatched prices — real source gaps, not failures

Of 183 catalog entries, **84 have `matched=false`** in
`data/egymonuments_prices.json`. The compile report
(`work/egymonuments_compile.md`) is explicit that these are *the Ministry's
gaps*, not parser failures: 72 entries have no price block at all (area/city
overviews like Ayn Shams City, Alexandria, Al-Fustat, and unticketed
sub-monuments); 8 are explicitly "free of charge" (Mosque of al-Hakim, Bab
al-Nasr, Bab al-Futuh, Al-Saliba Street); 2 are "Included in the citadel
ticket" (Muhammad Ali Mosque, Mosque of al-Nasir Muhammad); 1 is "Private
visits only" (the Great Sphinx); 1 is hours-only text (Saint Catherine's).
The reviewer's live re-fetch (`review/egymonuments_review.md`) confirmed 0
fabricated prices and 0 currency/nationality/tier swaps.

### 4.5 Geographic coverage gaps — also source, not failure

The compile report breaks coverage down by region: Cairo 28/40 (70%),
Alexandria 5/41 (12.2%), Sinai 1/42 (2.4%), Hurghada 0/27 (0%), Marsa Alam
0/40 (0%). The Red Sea and coastal Sinai gaps are by design — those POIs are
diving/resort/natural and are correctly served by PADI, not the Ministry.
The Alexandria / Luxor west-bank gaps (Catacombs of Kom El Shoqafa, Colossi
of Memnon, Valley of the Queens, Abydos, Esna) reflect the Ministry's own
selectivity (pharaonic + Islamic-Cairo favoritism, under-representation of
Greco-Roman Alexandria).

### 4.6 Politeness, retries, idempotency

Each scraper enforces a gentle-scraping contract because Ministry and PADI
servers are not API partners. `scrape_padi.py::_throttle` enforces a 2 s
inter-call delay with retry on `429/500/502/503/504`; the egymonuments chain
enforces 1.5 s with 2 retries on `5xx/Timeout/ConnectionError`
(`work/egymonuments_desc.md` §4). All three scrapers write a **disk cache**
(`scripts/scrape/cache/{padi-files, egymonuments/*}`; 260 PADI cache files,
242 egymon cache files) so re-runs issue zero network calls — both for
politeness and for reproducibility. The egymonuments desc chain reported
"idempotency: second run finished in 2.8 s, network: 0, cache: 58".

### 4.7 No challenge evident in the code for these areas

- No evidence of IP rotation, proxy pools, TLS-fingerprint spoofing, or
  Cloudflare-bypass tooling — the spike explicitly disproved the need.
- No CAPTCHA-solving code anywhere in the scraping layer.
- No dedup-of-prices logic across sources — by design each POI gets prices
  from at most one source (the Ministry).

---

## 5. Connections to the literature

**Tang et al. (2024) — ItiNera.** The single most direct precedent. VOYO's
310-POI curated substrate mirrors ItiNera's argument that a hybrid
LLM-plus-optimizer planner needs a *bounded, vetted POI pool* to be reliable,
because pure LLMs "lack the optimization capabilities required for planning
tasks." VOYO extends the same logic to factual grounding: the curated list is
also the boundary at which the LLM's parametric recall is replaced by fetched
official sources (`enrich_narratives.py::process_poi`'s
official→wikipedia→tavily→none ladder). The Tier-A status of ItiNera in
`thesis/citations/INDEX.md` makes it load-bearing for this design rationale.

**Onuiri et al. (2016) — ITMS.** A useful contrast. ITMS covers 50 Egyptian
locations with a MySQL/PHP/HTML stack and a hybrid recommender, but its data
model has no provenance, no per-POI narrative, no dual pricing, and no
verification flag. VOYO's pipeline is the engineering answer to the gaps
Onuiri et al. (2016) leave open: where ITMS treats "a database of tourist
information" as an off-the-shelf input, VOYO builds the data-acquisition
chain (`work/build_egymonuments_merge.py`, the three scrapers, the
narrative-grounding script) as a first-class subsystem.

**Swanepoel (2022) — itinerary architecture.** Argues from a Stellenbosch
M.Eng thesis that an itinerary-planning backend needs a clean separation
between the data, optimization, and presentation layers. VOYO's pipeline
matches that separation: the data layer
(`data/master_attractions.json`, `data/egymonuments_*.json`,
`data/enrichment_sources.csv`) is consumed read-only by the routing layer
(VROOM) and the agentic layer (CLEO); the schema migration
(`004_ticket_prices.sql`) and the upsert (`ticket_prices_upsert.sql`) are the
formal interface between them.

**Zaharia et al. (2024) — Compound AI Systems.** VOYO's data pipeline is the
*retrieval* arm of a compound system: scraping → enrichment → grounding is
what makes the LLM a *component* rather than the whole system — exactly the
failure mode compound systems are designed to avoid. **Wang et al. (2024) —
LLM-agent survey.** Its Profile/Memory/Planning/Action blueprint maps onto
VOYO: the curated substrate is the agent's Profile/Memory, the enrichment
pipeline is the long-term Memory write path, and the per-POI `narrative`
column is the surface the agent's Planning/Action layers read at request
time.

---

## Citations used

- **Tang et al. (2024)** — internal `N1` — INDEX.md Tier A — ItiNera. Used
  for §1, §3.1, §3.5, §5 (curated POI pool as anti-hallucination boundary;
  "lack the optimization capabilities" quote).
- **Onuiri et al. (2016)** — internal `12` — INDEX.md Tier B — ITMS. Used
  for §5 (contrast on data-model maturity).
- **Swanepoel (2022)** — internal `15` — INDEX.md Tier B — itinerary
  architecture. Used for §5 (layer separation argument).
- **Zaharia et al. (2024)** — internal `01` — INDEX.md Tier A — Compound AI
  Systems. Used for §5 (compound-systems framing).
- **Wang et al. (2024)** — internal `02` — INDEX.md Tier A — LLM-agent
  survey. Used for §5 (Profile/Memory/Planning/Action mapping).
- **VROOM / OSRM / Valhalla** — internal `S-VROOM / S-OSRM / S-VALHALLA` —
  INDEX.md Tier C software — mentioned in §5 as the downstream consumer
  layer; not used as a paper.
