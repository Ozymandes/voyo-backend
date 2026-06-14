# Chapter 6 — The POI Data Pipeline: A Clean Rebuild

> **In one sentence:** The single most important thing this project did was stop trying to
> *use* the inherited enrichment pipeline and instead *replace* it with a 350-line, self-contained
> rebuild that produced 255 verified, deduplicated, image-backed points of interest — because
> a neuro-symbolic planner reasoning over garbage produces confidently-wrong itineraries.

---

## 6.1 Why this chapter is the strongest contribution

A travel-planning system is only as good as the substrate it reasons over. The VOYO
planner (CLEO + VROOM, Chapters 4–5) can be perfectly implemented and still produce
nonsense if the POI database says the Great Pyramid has no image, that Luxor Temple
exists twice, or that a 4,000-year-old temple has exactly five Google reviews. Before
this work, *all three* were true simultaneously, plus two more latent defects we found
only by auditing the live database row-by-row.

The honest summary of the situation at project start: the inherited
`src/pipeline/optimized_enrichment_pipeline.py` was a 583-line system with Redis caching,
a dead-letter queue, and thread pooling. It *ran* to completion. It *looked* healthy in
its logs. And it had silently produced a database in which only **55 of 275 master
entries** had made it in, **4 of those were exact duplicates**, every single image URL was
both *malformed* and *dying*, and ~28 entries had been rejected at the enum layer without
anyone noticing.

The contribution of this chapter is not "we built an enrichment pipeline." It is: **we
diagnosed five independent silent-failure modes, decided correctly *not* to patch them in
place, and shipped a deliberately smaller pipeline that produces data we are willing to
defend to a committee.** The decision-making — what to cut, what to keep, what to disclose
as a gap — is the contribution. The code is its evidence.

---

## 6.2 The five bugs, audited live

Every claim below was verified against the live Supabase instance (anonymous **and**
service keys agreeing) and against the source code line-by-line. The audit is recorded in
`docs/devlog/PIPELINE_AUDIT.md`. Table 6.1 summarizes the defects and their resolution.

### Table 6.1 — Inherited pipeline defects and their resolution

| # | Defect (before) | Evidence | Fix (after) | Where in `rebuild_database.py` |
|---|---|---|---|---|
| 1 | `image_urls` stored as `{"images": [...]}` (dict wrapper) — app expects a flat array, so `Image.network` parsed nothing | Every one of the 41 imaged rows, live | Flat JSON array: `wiki.get("images") or []` | `build_row()` |
| 2 | `tags` stored as `{"tags": [...]}` (dict wrapper) — same class of bug | 40/55 rows | `_build_tags()` returns `list(dict.fromkeys(...))` — flat, deduped, order-preserving | `_build_tags()` |
| 3 | `total_reviews = len(reviews)` — but Google `/details` caps the `reviews` array at **5**, so almost every POI reported ≤5 reviews | Live rows: mostly `total_reviews ≤ 5`, a few large values from an older run | Read `user_ratings_total` from the Google `/details` payload, not the array length | `google_fetch()`, comment `# FIX bug #3` |
| 4 | Invalid enum categories `'Nature'` (25×) and `'Modern'` (3×) — DB enum only accepts lowercase values; insertion returns HTTP 400, logged as a generic failure | `POST {category:'nature'}` → `400 invalid input value for enum poi_category_enum` | Categories normalized to enum values at master-list cleaning time (`clean_master_list.py`); `build_row()` trusts `entry["category"]` is already valid | upstream of `build_row()` |
| 5 | No deduplication — inserter POSTed unconditionally and only swallowed HTTP 409, but there was no unique constraint on `name`, so 409 never fired | 4 exact duplicates: Khan el-Khalili (ids 55, 103), Al-Azhar Mosque, Luxor Temple, Bibliotheca Alexandrina | Upsert-by-normalized-name: existing match → `PATCH` in place; orphans → `is_active=False` | `DB.upsert()`, `DB._patch()`, `norm()` |

The failure mode these five share is **silentness**. None threw an exception. The pipeline
returned a clean exit code every time. That is the most important lesson of this chapter:
*a pipeline that logs "success" and a database that contains correct data are two different
things.* The audit that found all five was not triggered by a crash — it was triggered by
opening the app, tapping the Great Pyramid, and seeing a broken image.

---

## 6.3 The strategic decision: rewrite, don't patch

We had two paths once the audit landed:

1. **Patch in place** — five surgical edits to `optimized_enrichment_pipeline.py`, keep
   its Redis/DLQ/threading scaffolding, re-run.
2. **Write a clean, self-contained rebuild** — `rebuild_database.py`, ~350 lines, no Redis,
   no DLQ, sequential with pacing.

We chose (2). The reasoning is worth stating plainly because it is the kind of call a
committee will probe:

- **The target table is 250 rows, not 250,000.** Redis caching, a dead-letter queue, and a
  thread pool exist to make *large* enrichment jobs survivable. For a thesis-scale corpus
  they are pure complexity — five more places a bug can hide, five more services that have
  to be running for the pipeline to be reproducible. The DLQ, in particular, is exactly
  where Bug #4 (enum rejection) went to die silently.
- **The inherited pipeline had already eroded trust.** We had found five defects by
  sampling. We had no reason to believe there were not a sixth and seventh in the 583
  lines we had not yet read. Patching five known bugs in code we did not fully understand
  is the textbook way to ship a sixth.
- **Reproducibility for the defense.** A reviewer who wants to re-run our data build
  should need one command and one Python file, not a Redis instance, a DLQ topic, and a
  thread-pool configuration. `python rebuild_database.py` is that command.

The cost was honesty about scope: `rebuild_database.py` is *not* production-grade. It is
single-threaded with 0.15 s pacing between POIs, it has no retry queue for permanent
failures, and it would not scale to a national-scale corpus without rework. That is an
acceptable trade for a system whose evaluation corpus is 255 rows. We name this limitation
explicitly in §6.7.

The inherited `optimized_enrichment_pipeline.py` was **left untouched** — a surgical
boundary. It still exists in the repository as the historical record; nothing depends on
it.

---

## 6.4 The image strategy: Wikimedia permanent URLs, not Google photo tokens

This deserves its own section because it is the decision a committee is most likely to
second-guess, and it is the one we are most confident in.

The inherited pipeline fetched images from Google Places via:

```
https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference=<token>&key=<API_KEY>
```

This URL has two independent defects, either of which is disqualifying on its own:

1. **The `photoreference` token expires.** Google's own documentation states these
   references "may change." In practice they decay within days. So even the rows that
   *had* images were pointing at URLs that were already 404ing or about to.
2. **The API key is embedded in every stored URL.** These URLs are shipped to the Flutter
   client and loaded by `Image.network`. That is a credential leak into a publicly
   distributed binary. This alone would be a finding in a security review.

We chose **Wikimedia Commons** image URLs as the sole image source. The trade, stated
without spin:

| Property | Google Places photo | Wikimedia Commons |
|---|---|---|
| URL permanence | ❌ token expires | ✅ permanent |
| API key in URL | ❌ yes (leak) | ✅ no key at all |
| Cost | billed per request | free |
| Image quality | generally higher | slightly lower for some POIs |
| Coverage of obscure sites | higher | lower (needs a Wikipedia article) |

We picked reliability and safety over polish. A demo that shows a slightly-less-glamorous
photo of Abu Simbel is fine; a demo that shows a broken-image icon for the Great Pyramid is
not. The coverage gap (Wikimedia needs a Wikipedia article) shows up in the 18% of POIs
without images — mostly remote diving reefs and desert locations — and is disclosed in §6.7.

The implementation is `wikimedia_fetch()`. It pulls the lead image and extract from the
Wikipedia REST summary endpoint, validates that the response is a real article (not a
disambiguation page — `if d.get("type") == "disambiguation"`), and falls back through a
list of candidate query strings (`search_queries` from the master entry, then the bare
name, then `"<name> <region>"`). Coordinates come from a separate MediaWiki API call,
which we found more reliable than the summary endpoint's coordinate field.

One operational detail worth recording: our first Wikimedia backoff attempt, at 0.1 s per
request, was *silently* returning empty responses — Wikimedia was throttling us and we
were ignoring the empty bodies. The fix was a descriptive `User-Agent`
(`"VoyoApp/1.0 (educational thesis project)"`, per Wikimedia's policy), 1 s pacing during
backfill, and `with_retry()` exponential backoff. Silent empty-response handling is the
same class of failure mode as the five bugs above; we now treat any "successful" HTTP 200
with an empty payload as a failure to investigate, not a success to log.

---

## 6.5 The rebuild, component by component

`rebuild_database.py` is organized into four layers. Every name below is a real symbol in
the file.

**Normalization and retry — `norm()`, `with_retry()`.** `norm()` lowercases a name and
strips non-alphanumeric characters (`re.sub(r"[^a-z0-9 ]", "", name.lower())`). This is
the dedup key. `with_retry()` is exponential backoff with `tries=4, base_delay=1.0` — used
for every network call.

**Source 1, Wikimedia — `wikimedia_fetch(name, region, search_queries)`.** Returns
`{images, coords, significance}` (or `{}`). One image per POI; we deliberately store a
single solid permanent URL rather than a list of varying quality.

**Source 2, Google Places — `google_fetch(name, region, search_queries)`.** Two-call
pattern: `GOOGLE_TEXT` text-search to resolve a `place_id`, then `GOOGLE_DETAILS` for the
structured fields (address, rating, `user_ratings_total`, hours, website, phone, price
level). The `# FIX bug #3` comment marks where `user_ratings_total` is read instead of
`len(reviews)`.

**Merge — `build_row(entry, region)`.** Combines the master entry, Wikimedia output, and
Google output into a Supabase-ready row. Coordinate resolution prefers Google, falls back
to Wikimedia. `popularity_score` is a *transparent heuristic*, not a learned model:

```python
popularity_score = round(
    min(100, (total_reviews / 500) * 10)
    + (10 if importance == "Must-See" else 0)
    + (15 if importance == "World Wonder" else 0), 1)
```

We disclose this because "popularity score" sounds more authoritative than it is: it is a
review-count term capped at 10 plus an importance-tier bonus. It is defensible (review
volume correlates with foot traffic; the importance tier encodes curator judgment) but it
is a formula, and the thesis says so.

**Persistence — the `DB` class.** This is where Bugs #1, #2, and #5 are structurally
prevented from recurring:

- `_detect_columns()` probes the *live* schema (`SELECT * ... LIMIT 1`) and stores the
  column set. Every write is then filtered to existing columns via
  `{k: v for k, v in row.items() if k in self.columns}`. This makes the pipeline robust to
  the schema drift the audit found (the live table was missing `phone_number`, `city`,
  etc., relative to `database_schema.sql`). Rather than fail, the pipeline simply omits
  columns that do not exist yet.
- `_load_existing()` builds `name_map: normalized_name -> [ids]` once at startup.
- `upsert(row)` is the dedup heart: if `norm(name)` matches an existing key, it keeps the
  lowest `id` (`keep_id = min(ids)`), `PATCH`es that row in place, and deactivates any
  orphans via `is_active=False`. **Patching in place — rather than delete-and-reinsert —
  preserves any foreign-key references to that POI id** (itineraries, saved trips). This
  matters: a naive dedup that deletes duplicates would orphan user data.

Running `python rebuild_database.py` processes all 250 master entries sequentially with
0.15 s pacing; `--region Cairo` and `--limit 5` flags support smoke-testing a single
region or a handful of POIs.

---

## 6.6 Deduplication: exact-match at insert, fuzzy match at cleaning

Deduplication happened in two passes, and we are careful to distinguish them because they
are different mechanisms:

1. **Exact normalized-name dedup at insert time** — `DB.upsert()` with the `norm()` key.
   This is what makes the pipeline *idempotent*: re-running it never creates duplicates.
   It is fully implemented and verified in `rebuild_database.py`.
2. **Fuzzy name-variant dedup at cleaning time** — handles cases like *"Abu Simbel"* vs
   *"Abu Simbel Temples"*, which normalize to different keys and so defeat exact match.
   Implemented in `dedup_variants.py` (`is_variant()`): substring containment on
   normalized names, with a minimum-length floor of 4 to avoid noise from short tokens
   like *"Sinai"*. When the normalized straggler is a substring of a master name (or
   vice versa), the straggler is treated as a variant of the curated master POI and
   deactivated (`is_active = false`); the fuller master row wins. Per the rebuild log
   (`docs/devlog/DATABASE_REBUILD_COMPLETE.md`, CHANGELOG entry 2026-06-11), this pass
   deactivated **13 variants** and kept **7 genuinely-unique stragglers** which were
   then re-enriched. We re-ran the utility in dry-run mode while writing this chapter
   and it identified **0 remaining variants** — confirming the dedup is idempotent.

> The split is deliberate and verifiable: exact-match idempotency belongs in the
> pipeline (`rebuild_database.py:DB.upsert`, runs on every re-run); fuzzy variant-
> resolution belongs in one-time curation (`dedup_variants.py`, runs once when the
> variants are first merged). The dry-run confirmation above is the evidence the
> curation step is complete.

This split is deliberate: exact-match idempotency belongs in the pipeline (it must hold on
every re-run); fuzzy variant-resolution belongs in one-time curation (once the variants are
merged, they stay merged).

---

## 6.7 Results — and the honest gaps

After the rebuild, validated live:

| Metric | Before | After |
|---|---|---|
| Active POIs | 55 | **255** |
| Exact duplicates | 4 | **0** |
| Dict-wrapped `image_urls` | 41 (all imaged rows) | **0** |
| Dict-wrapped `tags` | 40 | **0** |
| Review counts capped at 5 | most rows | **0** |
| Invalid-enum rejections | ~28 blocked | **0** |
| Permanent Wikimedia images | 0 | **208 / 255 (82%)** |
| Famous-6 sites with images | 0 / 6 | **6 / 6** |
| `historical_significance` filled | 54 / 55 | **254 / 255 (99%)** |
| Coordinates present | 55 / 55 | **255 / 255 (100%)** |

The famous six — Great Pyramid, Karnak, Sphinx, Valley of the Kings, Egyptian Museum, Abu
Simbel — are the sites a demo opens first. Before: zero of six had a usable image. After:
all six. That single before/after line is, in practical terms, the difference between a
demo that lands and one that does not.

**Figure 6.1** (`thesis/figures/fig_field_completeness.png`) plots field completeness across
the 255 active POIs, live-queried. The chart is deliberately two-colored: green for fields
at or above 70%, orange below. The orange fields are *not* bugs, and the figure's subtitle
says so. Three gaps dominate the orange:

- **`ticket_price` ~58% populated.** 107 of 255 POIs are genuinely free — beaches, reefs,
  streets, markets, open-air sites. A null price is *semantically correct* for these; the
  master list confirms exactly 107 free entries. Faking a price to hit 100% would be the
  dishonest choice.
- **`opening_hours` ~67%.** Outdoor and natural sites (reefs, mountains, deserts) have no
  operating hours because they don't operate on a schedule. Null is correct.
- **`website_url` ~40%.** Natural sites rarely have websites. Null is correct.

We disclose these rather than paper over them. A committee that reads "82% image coverage"
and then finds out the missing 18% are remote diving reefs — not the Pyramids — gets a
more accurate picture of the system than one that reads a rounded-up "90%+". Honesty about
where the gaps are is, we argue, a stronger methodology statement than a higher number.

**Figure 6.2** (`thesis/figures/fig_regional_distribution.png`) shows the regional spread.
Here the gap *is* a curation artifact, not a semantic correctness issue, and we say so:
**Cairo (11) and Giza (9) are the two thinnest regions despite being the two most-visited.**
The master list under-represents the capital. This is the single most legitimate criticism
a reviewer can level at the corpus, and we lead with it rather than bury it. The fix is
curation effort (more Cairo/Giza entries in the master list), not engineering — which is
exactly why it sits in the limitations section instead of the bug list.

---

## 6.8 What this chapter claims, and what it does not

**Claims (defensible, cited):**

- 255 active, validated POIs across 8 regions, 0 duplicates — `validate_database.py`, live count.
- All five enumerated code defects are resolved in `rebuild_database.py` at the cited functions.
- Image URLs are permanent, key-free Wikimedia Commons URLs — `wikimedia_fetch()`.
- The pipeline is idempotent — `DB.upsert()` with `norm()`.
- All six most-famous sites have images — verified live.

**Non-claims (explicit limitations):**

- The corpus is **regionally unbalanced** (Cairo/Giza thin). Curation gap, disclosed.
- Image coverage is **82%, not 100%**. The 18% gap is concentrated in obscure remote sites.
- `rebuild_database.py` is **not production-scale**: single-threaded, 0.15 s pacing, no
  retry queue for permanent failures. Acceptable at 255 rows; would need rework at scale.
- The fuzzy name-variant dedup mechanism is implemented in `dedup_variants.py`
  (`is_variant()`, substring containment, length floor 4) and was verified idempotent
  by a dry-run re-check during writing (0 remaining variants).
- `popularity_score` is a **transparent heuristic**, not a learned ranking model. Stated, not hidden.

The strongest version of this chapter is the one that hands the committee the limitations
*before* they find them. That is the version above.
