# VOYO Scrape Data-Integrity Review

Reviewer: independent (adversarial) pass over `scripts/scrape/` + the `data/enrichment_sources*` deliverables.
Date: 2026-06-16. Method: read-only inspection (`git`, `pandas`, `grep`, `curl`). No files were edited.

---

## Verdict: **PASS**

The scrape work is honest and conservative. Every `matched=true` description traces verbatim to a real upstream page (3/3 spot-checks pass on live URLs); every blank is correctly `matched=false`; both scrapers are read-only with 2s throttling; no secrets are committed; pricing is correctly absent from the scrape outputs.

---

## Findings by severity

### Blocker
None.

### Fix-now
None.

### Optional (parent decision — not scrape-blocking)

**O1. `data/manual_prices.csv` is untracked AND not git-ignored → would be committed by a blanket `git add`.**
- Evidence: `git check-ignore data/manual_prices.csv` returns non-zero (NOT ignored). `git ls-files` shows it is not yet tracked.
- Content: 227 rows, 182 with a `current_ticket_price` (EGP), 127 with a `website_url` source. Prices carry source URLs (e.g. `bibalex.org`, `alexandria.gov.eg`) — they are curated, not invented by these scrapers — **neither scrape script produces prices** (verified: `scrape_experienceegypt.py` emits `description` only; `scrape_padi.py` emits `description` + `extra_attrs` only).
- Risk: low. The prices look real and sourced, but the task scope said "pricing is correctly ABSENT". This file is a parallel curated artifact unrelated to the two scrapers under review. Parent should decide: either `.gitignore` it (keeps pricing out of the repo entirely), or accept it as a tracked hand-curated source. It is NOT a scrape deliverable.

**O2. `config/sql/004_ticket_prices.sql` exists (untracked).**
- Inspected: it is pure DDL — `ALTER TABLE pois ADD COLUMN ticket_prices JSONB` + a `CHECK` constraint validating the `{"egyptian","foreigner","currency":"EGP"}` shape. **No `INSERT`/`UPDATE`/`DELETE`**, so it does not lie about any price. Not misleading. Flagging only because the task called out "no misleading SQL file" — this one passes that bar.

### Nit

**N1. One honest empty-description row propagates into the merged CSV.**
- `Tiger Reef` (`poi_id=padi:1052`, `data/enrichment_sources_padi.csv:51`, mirrored at `data/enrichment_sources.csv:114`) has a `source_url` but a blank `official_description`. This is correct, not fabricated: the live PADI page genuinely has no prose, the scraper recorded the empty description honestly, and the row is `matched=false` / `kind=extra_capture`. No action needed.

---

## Evidence (by acceptance criterion)

### 1. Zero fabricated descriptions — CONFIRMED
- `data/enrichment_sources.csv` (the merged deliverable, 130 rows): all **21 `matched=true`** descriptions appear **verbatim** in either `enrichment_sources_padi.csv` or `enrichment_sources_expeg.csv` (set-membership check). `0` untraced.
- All `matched=true` rows have both a non-blank description AND a non-blank `source_url` (in all three CSVs).
- Every row with a non-blank description has a `source_url` (0 violations across all 3 CSVs).
- Live spot-checks (3/3 verbatim matches against upstream pages):
  1. **Panorama Reef** → `https://www.padi.com/dive-site/egypt/panorama-north-2/` (HTTP 200): the CSV's opening sentence `"Panorama reef is one of the biggest and well-known reefs in Safaga…"` is present word-for-word inside `dive-site-overview__content-description`.
  2. **Sha'ab Abu Nuhas (Giannis D)** → `https://www.padi.com/dive-site/egypt/abu-nuhas-ghiannis-d/` (HTTP 200): CSV phrase `"loaded with sawn timber at Rijeka"` found on live page.
  3. **Cairo & Giza region + Khan el-Khalili** → `https://www.experienceegypt.eg/en/city/1/cairo-giza` (HTTP 200): both `"one of the world"` and `"Khan al-Khalili, Cairo"` found verbatim on the live page.

### 2. Every blank is honestly `matched=false` — CONFIRMED
- `matched=true` rows with blank description: **0** in all three CSVs.
- `enrichment_sources_expeg.csv`: 4 `matched=true` rows are all conservative single-POI tips (`Khan el-Khalili`, `Valley of the Queens`, `Nubian Village`, `Sha'ab Samadai`) extracted only when the POI name leads the paragraph, the paragraph is ≤200 chars, and it's a focused single-site mention — the matching logic in `scrape_experienceegypt.py:187-218` (`pois_in_text` requires exactly 1 POI hit + first-sentence lead + length cap) is deliberately strict against false single-POI claims.

### 3. Scrapers are read-only — CONFIRMED
- Imports (`scripts/scrape/scrape_*.py`): stdlib only + `requests`/`bs4`. **No `supabase`, `psycopg`, `sqlite3`, no `create_client`, no auth-bypass pattern.**
- `grep -rniE "supabase|\.insert\(|\.update\(|\.delete\(|psycopg|sqlite3|INSERT INTO|UPDATE .*SET|DELETE FROM|create_client|auth\.|api[_-]?key|token|secret|password|bypass" scripts/scrape/` (excluding `cache/`): the only hits are (a) a docstring comment in `scrape_experienceegypt.py:26` stating the DB is explicitly off-limits, and (b) the word "token" inside benign regex/matching comments in `scrape_padi.py`. **Zero DB-write code.**
- All file writes confined to: the two declared output CSVs (`enrichment_sources_expeg.csv`, `enrichment_sources_padi.csv`) and the local HTTP cache (`scripts/scrape/cache/`, 259 files, untracked, idempotent on re-run). `master_attractions.json` is opened **read-only**.
- `validate_database.py` is **not modified** (`git diff` empty); only `validate_structure.py` shows changes (CRLF churn, out of scrape scope).

### 4. Gentle rate-limiting (2s delays) — CONFIRMED in BOTH scripts
- `scripts/scrape/scrape_experienceegypt.py:46` → `DELAY = 2.0`; enforced at line 231 (`time.sleep(DELAY)` per page).
- `scripts/scrape/scrape_padi.py:64` → `DELAY = 2.0`; enforced via `_throttle()` (lines 78-83) on every `_get()`, plus `DELAY*2` backoff on HTTP 429/5xx (line 102).

### 5. `data/enrichment_sources.xlsx` + `.csv` are well-formed — CONFIRMED
- `enrichment_sources.xlsx`: single sheet `enrichment_sources`, shape `(130, 10)`, columns identical to the CSV.
- `enrichment_sources.csv`: `(130, 10)`. `enrichment_sources_expeg.csv`: `(9, 7)`. `enrichment_sources_padi.csv`: `(122, 7)`.
- All four files open cleanly under `pandas.read_csv` / `pd.ExcelFile` with no parse errors. All `best_source_url`s in the merged file are present in one of the two source CSVs (`0` orphan URLs).

### 6. Pricing correctly ABSENT from scrape deliverables — CONFIRMED
- Neither scrape script emits any price column. Spot-checked output schemas: `{poi_name, poi_id, region, source_url, official_description, matched, method}` and `{poi_name, poi_id, source_url, official_description, extra_attrs, matched, method}` — no price/fee/ticket field anywhere.
- `004_ticket_prices.sql` is DDL-only (see O2). No invented prices in the scrape path. (See O1 re: the unrelated `manual_prices.csv`.)

### 7. No secrets committed — CONFIRMED
- `git ls-files | grep '\.env'` returns only `.env.example` and `flutter_app/.env.example` (templates).
- `git check-ignore` confirms `.env`, `flutter_app/.env`, and `flutter_app/build/**/.env` are all **ignored**. The Supabase anon/service-role JWTs that appear in `.env` are **not** tracked.
- `grep` for high-entropy secrets (`sk-…`, `ghp_…`, `AKIA…`, bare service-role JWTs) finds matches **only** inside `.env`/build artifacts — all git-ignored.
