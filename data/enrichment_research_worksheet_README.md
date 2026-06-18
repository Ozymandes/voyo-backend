# Enrichment Research Worksheet

**File:** `data/enrichment_research_worksheet.csv`
**Purpose:** Fill in missing `ticket_prices` and/or `best_visit_times` for active
Egyptian tourist POIs, via web research. Return the filled CSV for DB import.

---

## What to fill

Only fill the **blank** columns. Two independent concerns; a row may need one or both.

### 1. Ticket prices — fill `egyptian_price` + `foreigner_price`
Only on rows where **`needs_price = Y`** (skip the `skip` rows — those are
likely free or already priced).

- **Units:** integer **EGP** (Egyptian pounds). No decimals, no currency symbol.
- **Egyptian = adult citizen rate. Foreigner = adult foreign-visitor rate.**
- Currency is a constant `EGP` (do not fill it — it's implied).
- This becomes the DB JSONB: `{"currency":"EGP","egyptian":N,"foreigner":N}`.
- A hard **CHECK constraint** forbids any other keys/currencies, so fill **only**
  the two numbers.
- **If the POI has free entry:** leave both price columns blank and write
  `free entry` in `notes`. Do not invent numbers.

### 2. Best visit times — fill `best_visit_season` + `best_visit_time_of_day`
Fill on every row where `current_best_visit_times` is blank (i.e. all worksheet
rows, since that's why they're listed).

- This becomes the DB JSONB: `{"season":"...","time_of_day":"..."}`.
- Be **specific and useful** — the existing 35 values are all bland
  `"Year-round"/"Any time"` and that low-value pattern is what we're improving.
  Prefer concrete guidance, e.g.:
  - `best_visit_season`: `"October–April"` · `"Avoid July–Aug heat"` · `"Year-round"`
  - `best_visit_time_of_day`: `"Early morning (opening)"` · `"Late afternoon / sunset"` · `"Sunset"` · `"Morning, before crowds"`
- `notes` is free-text for caveats, source links, or uncertainty.

---

## Research guidance

- **Start with the `website_url` column** (official site) and `current_legacy_price`
  (an existing single-tier price — a strong hint the POI charges admission).
- **Authoritative sources, in order:** official POI/museum site →
  egymonuments.gov.eg (already exhausted for major monuments, but double-check) →
  Lonely Planet / Tripadvisor / GetYourGuide for current dual-tier fees.
- **Egypt dual-pricing is standard** at state monuments/museums (citizen vs
  foreigner). Modern attractions (malls, some restaurants) may have a single
  price — if so, put the same number in both columns and note "single tier".
- **Do NOT fabricate.** If you cannot find a reliable figure, leave the cell blank
  and note `unverified` in `notes`. Blanks are safe; wrong numbers are not.
- **Price volatility:** Egyptian monument fees change; note the source/date in
  `notes` where possible.

---

## Column reference

| Column | Meaning | Fill? |
|---|---|---|
| `id` | POI primary key (keep for import) | no |
| `name`, `city`, `category` | identity / context | no |
| `website_url` | official site (research starting point) | no |
| `current_legacy_price` | existing single-tier `ticket_price` (hint) | no |
| `current_ticket_prices` | existing structured price, if any | no |
| `needs_price` | `Y` = research price; `skip` = likely free/already priced | no |
| `egyptian_price` | adult citizen rate, EGP int | **yes** (if needs_price=Y) |
| `foreigner_price` | adult foreigner rate, EGP int | **yes** (if needs_price=Y) |
| `current_best_visit_times` | existing value, if any | no |
| `best_visit_season` | e.g. "October–April" | **yes** |
| `best_visit_time_of_day` | e.g. "Early morning" | **yes** |
| `notes` | caveats / sources / "free entry" / "unverified" | optional |

---

## Scope summary (at generation time)

- Active POIs in DB: **316**
- Worksheet rows (missing ≥1 field): **302**
  - needing price research (`needs_price=Y`): **218**
  - needing visit-time research: **281**
- Excluded from price research as likely free: `natural` category POIs with no
  existing price (beaches, reefs, dive sites). If any of these actually charge,
  note it and the import step can pick it up.

## Import (after fill)

A separate import script (to be run once the CSV is returned) will:
- read `egyptian_price`/`foreigner_price` → upsert `ticket_prices` JSONB (NULL-guarded),
- read `best_visit_season`/`best_visit_time_of_day` → upsert `best_visit_times` JSONB,
- skip rows where the fill columns are blank (never write partial/null structures).
