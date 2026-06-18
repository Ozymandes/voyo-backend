#!/usr/bin/env python3
"""
scrape_padi.py — Collect REAL PADI dive-site descriptions for VOYO Red Sea POIs.

TIER USED: (a) direct JSON API (no browser required).

Reverse-engineering notes (see work/padi.md for full write-up):
  - padi.com/dive-sites/egypt is an Angular SSR *shell*; dive-site data loads
    client-side from `https://travel.padi.com/api/v2/travel/...`.
  - Map (pins) endpoint:
        GET https://travel.padi.com/api/v2/travel/dsl/dive-sites/map/
            ?top_right=<lat>,<lng>&bottom_left=<lat>,<lng>
    -> [{id, latitude, longitude}, ...]
  - Per-pin detail endpoint:
        GET https://travel.padi.com/api/v2/travel/dsl/dive-sites/<id>/map/
    -> {id, latitude, longitude, title, types, travelUrl, background}
  - The full human-written description + common sightings are SSR-embedded in
        https://www.padi.com/dive-site/egypt/<slug>/
    inside `<div class="dive-site-overview__content-description">...</div>` and
    the `Common Sightings` metric. No JavaScript execution is required.

All network calls are serial with a 2s delay (gentle). Raw responses are cached
under scripts/scrape/cache/ so re-runs are fast and idempotent.

Deliverable: data/enrichment_sources_padi.csv
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
MASTER = os.path.join(ROOT, "data", "master_attractions.json")
OUT_CSV = os.path.join(ROOT, "data", "enrichment_sources_padi.csv")
CACHE_DIR = os.path.join(HERE, "cache")

API_BASE = "https://travel.padi.com/api/v2/travel"
PAGE_BASE = "https://www.padi.com"
DELAY = 2.0  # seconds between network calls (gentle)
UA = "Mozilla/5.0 (VOYO-research; dive-site enrichment; contact: dev@voyo)"

# Red Sea sub-region bounding boxes (top_right=NE, bottom_left=SW). Tuned so
# they capture the Dahab trio (Blue Hole/Canyon/Blue Lagoon ~28.55N) and the
# Gubal/Abu Nuhas wreck cluster (~27.65N) that a tighter box would clip.
REGIONS = {
    "Sinai":     ("28.70,35.00", "27.60,33.65"),  # Ras Mohammed / Dahab / Tiran / Sharm
    "Hurghada":  ("27.75,34.30", "26.40,33.30"),  # Hurghada / Safaga / Gubal / Abu Nuhas
    "Marsa Alam": ("26.50,37.50", "22.50,34.50"),  # Marsa Alam / Deep South / St. John's
}

# POI regions whose natural-category entries we care about
POI_REGIONS = ("Marsa Alam", "Hurghada", "Sinai")

# dive-site-like name keywords (incl. Arabic transliterations)
DIVE_KEYWORDS = re.compile(
    r"reef|wreck|bay|island|sha'?ab|sharm|\bras\b|marsa|habili|shoal|"
    r"lagoon|hole|straits|canyon|seamount|wall|pillar|tobia|thistlegorm|"
    r"dunraven|carnatic|giannis|uboot|salem|dump|numidia",
    re.IGNORECASE,
)

os.makedirs(CACHE_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# HTTP helpers (stdlib only, serial + delayed)
# ---------------------------------------------------------------------------
_last_call = 0.0


def _throttle():
    global _last_call
    wait = DELAY - (time.time() - _last_call)
    if wait > 0:
        time.sleep(wait)
    _last_call = time.time()


def _get(url, as_json=True, headers=None, retries=2):
    _throttle()
    hdr = {"User-Agent": UA, "Accept": "application/json",
           "X-Requested-With": "XMLHttpRequest",
           "Referer": "https://www.padi.com/dive-sites/egypt/"}
    if headers:
        hdr.update(headers)
    last_err = None
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, headers=hdr)
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                raw = r.read().decode("utf-8", "replace")
                status = r.status
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                sys.stderr.write(f"  HTTP {e.code} retry {attempt+1} {url}\n")
                time.sleep(DELAY * 2); last_err = e; continue
            sys.stderr.write(f"  HTTP {e.code} for {url}\n")
            return None, e.code
        except Exception as e:  # noqa: BLE001
            last_err = e
            if attempt < retries:
                sys.stderr.write(f"  ERR {e!r} retry {attempt+1} {url}\n")
                time.sleep(DELAY); continue
            sys.stderr.write(f"  ERR {e!r} for {url}\n")
            return None, None
        if as_json:
            try:
                return json.loads(raw), status
            except json.JSONDecodeError:
                return None, status
        return raw, status
    return None, None


def _cache_path(kind, key):
    return os.path.join(CACHE_DIR, f"{kind}_{key}.json")


def cached_get(url, kind, key, as_json=True):
    """HTTP GET with disk cache. Returns (data, status)."""
    p = _cache_path(kind, key)
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            try:
                return json.load(f), 200
            except json.JSONDecodeError:
                f.seek(0)
                return f.read(), 200
    data, status = _get(url, as_json=as_json)
    if data is not None:
        with open(p, "w", encoding="utf-8") as f:
            if isinstance(data, (dict, list)):
                json.dump(data, f, ensure_ascii=False)
            else:
                f.write(data)
    return data, status


# ---------------------------------------------------------------------------
# PADI fetch phases
# ---------------------------------------------------------------------------
def fetch_pin_ids():
    """Phase 1: bbox queries -> unique dive-site ids per region."""
    out = {}
    for region, (ne, sw) in REGIONS.items():
        url = f"{API_BASE}/dsl/dive-sites/map/?" + urllib.parse.urlencode(
            {"top_right": ne, "bottom_left": sw}
        )
        pins, status = cached_get(url, "map", region)
        ids = [p["id"] for p in (pins or []) if "id" in p]
        out[region] = ids
        print(f"  [{region}] {len(ids)} pins (HTTP {status})")
    return out


def fetch_pin_detail(ds_id):
    """Phase 2: per-pin detail -> title/types/slug."""
    url = f"{API_BASE}/dsl/dive-sites/{ds_id}/map/"
    data, status = cached_get(url, "pin", str(ds_id))
    if not data:
        return None
    return {
        "id": ds_id,
        "title": data.get("title", "").strip(),
        "types": data.get("types", ""),
        "travel_url": data.get("travelUrl", ""),
        "latitude": data.get("latitude"),
        "longitude": data.get("longitude"),
        "image": (data.get("background") or {}).get("origin", ""),
    }


def parse_detail_page(html):
    """SSR detail page -> description + common sightings.

    The page embeds TWO copies of the description: a ~500-char truncated
    'show-on-collapsed' version and the FULL 'collapsable-content' version.
    We prefer the full one.
    """
    res = {"description": "", "common_sightings": ""}
    desc = ""
    # full (collapsable-content) copy first, then the truncated fallback
    for pat in (
        r'collapsable-content[^>]*dive-site-overview__content-description[^>]*>(.*?)</div>',
        r'dive-site-overview__content-description[^>]*>(.*?)</div>',
    ):
        m = re.search(pat, html, re.S)
        if m and m.group(1).strip():
            desc = re.sub(r"<[^#>]+>", " ", m.group(1))
            desc = re.sub(r"\s+", " ", desc).strip()
            if desc:
                break
    res["description"] = desc
    # Common Sightings metric
    sib = re.search(
        r'dive-site-overview__content-metric__title">Common Sightings</span>'
        r'(.*?)</div>\s*</div>', html, re.S
    )
    if sib:
        sightings = re.sub(r"<[^>]+>", " ", sib.group(1))
        res["common_sightings"] = re.sub(r"\s+", " ", sightings).strip()
    return res


def fetch_detail_page(slug, ds_id):
    """Phase 3: SSR detail page for a dive site slug."""
    if not slug:
        return {"description": "", "common_sightings": ""}
    url = PAGE_BASE + slug
    html, status = cached_get(url, "page", str(ds_id), as_json=False)
    if not html:
        return {"description": "", "common_sightings": ""}
    return parse_detail_page(html)


# ---------------------------------------------------------------------------
# Target POI selection + matching
# ---------------------------------------------------------------------------
def load_targets():
    with open(MASTER, encoding="utf-8") as f:
        data = json.load(f)
    targets = {}
    for region in POI_REGIONS:
        for idx, e in enumerate(data.get(region, [])):
            if e.get("category") != "natural":
                continue
            name = e.get("name", "")
            if not DIVE_KEYWORDS.search(name):
                continue
            targets[f"{region}::{idx}::{name}"] = {
                "region": region, "idx": idx, "name": name,
                "poi_id": name,  # master_attractions has no id; use name
            }
    return targets


# Generic / non-distinguishing words to strip before matching. Color words are
# deliberately KEPT so "Blue Hole" != "Green Hole" and != "Blue Lagoon"; size /
# ordinal qualifiers (big, small, north...) ARE stripped so "Big Brother Island"
# == "Brother Islands".
_STOP = {
    "reef", "reefs", "wreck", "wrecks", "shipwreck", "the", "of", "and",
    "bay", "bays", "island", "islands", "islands",
    "shaab", "sharm", "marsa", "habili", "shoal", "shoals",
    "national", "park", "protectorate", "beach", "dive", "site", "sites",
    "divesite", "egypt", "egyptian", "sea",
    # size / ordinal qualifiers (non-distinctive)
    "big", "small", "little", "new", "old", "great", "grand",
    "north", "south", "east", "west", "el", "al",
}


def normalize(name):
    """Normalize a name into distinctive tokens for matching."""
    s = name.lower()
    s = s.replace("'", "")          # sha'ab -> shaab (so it gets stripped)
    s = re.sub(r"[^\w\s]", " ", s)  # punctuation -> space
    s = re.sub(r"\d+", " ", s)      # drop digits
    toks = [t for t in s.split() if t and t not in _STOP]
    return " ".join(toks)


# Dive-site TYPE words (not proper names). A subset match must hinge on at least
# one NON-structural token, otherwise "Colored Canyon" would wrongly match the
# Dahab dive site "Canyon".
_STRUCT = {
    "reef", "reefs", "wall", "walls", "pinnacle", "pinnacles", "bay", "bays",
    "beach", "shoal", "shoals", "seamount", "channel", "cave", "caves",
    "cavern", "canyon", "hole", "lagoon", "temple", "tower", "garden",
    "gardens", "house", "island", "islands", "paradise", "sandy", "bottom",
    "ocean", "water", "drift", "pool", "spring", "springs", "quarry",
}

# Curated canonical aliases the fuzzy matcher is deliberately too conservative
# to link (e.g. a POI name whose only shared token is a structural word like
# "canyon"). Value = a PADI travelUrl slug known to exist. Add sparingly.
ALIASES = {
    "The Canyon (Dahab)": "/dive-site/egypt/the-canyon-8/",
}


def _tok_match(t1, t2):
    """Token equality, tolerating transliteration variants (shitan ~ shaitan)."""
    if t1 == t2:
        return True
    if len(t1) >= 4 and len(t2) >= 4:
        import difflib
        return difflib.SequenceMatcher(None, t1, t2).ratio() >= 0.85
    return False


def match(poi_name, padi_title):
    """True if poi_name and padi_title refer to the same dive site.

    Rules (after stripping generic words):
      * exact normalized equality
      * one is a substring of the other
      * they share >=1 distinctive token (len>=4, fuzzy-tolerant) AND one
        token-set is a subset of the other (same head name)
    """
    a, b = normalize(poi_name), normalize(padi_title)
    if not a or not b:
        return False
    if a == b:
        return True
    ta = [t for t in a.split() if len(t) >= 4]
    tb = [t for t in b.split() if len(t) >= 4]
    if not ta or not tb:
        return False
    # which distinctive tokens are shared (fuzzy-tolerant)?
    shared = [x for x in ta if any(_tok_match(x, y) for y in tb)]
    if not shared:
        return False
    # one distinctive-set must be contained in the other (same head name)
    subset = all(any(_tok_match(x, y) for y in tb) for x in ta) or \
        all(any(_tok_match(x, y) for x in ta) for y in tb)
    if not subset:
        return False
    # the shared tokens must include a proper name, not only generic type-words
    # (prevents "Colored Canyon" / "White Canyon" matching the dive site "Canyon")
    return any(tok not in _STRUCT for tok in shared)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("== Loading target POIs (natural, Red Sea, dive-site-like) ==")
    targets = load_targets()
    print(f"  {len(targets)} target POIs:")
    for k in sorted(targets):
        print("    -", k)

    print("\n== Phase 1: fetch dive-site pin IDs by region ==")
    region_ids = fetch_pin_ids()
    all_ids = sorted({i for ids in region_ids.values() for i in ids})
    print(f"  total unique dive-site IDs: {len(all_ids)}")

    print("\n== Phase 2: fetch per-pin detail (title/types/slug) ==")
    pins = []
    for ds_id in all_ids:
        d = fetch_pin_detail(ds_id)
        if d:
            pins.append(d)
            print(f"  [{ds_id}] {d['title']!r}  types={d['types']!r}")
    print(f"  {len(pins)} pins with detail")

    print("\n== Phase 3: match to target POIs ==")
    import difflib
    # candidate quality: penalize generic house-reef / pool / try-dive entries
    NOISE = re.compile(r"house reef|try dive|\bpool\b|house reed|dive center",
                        re.IGNORECASE)

    def sim(poi, title):
        a, b = normalize(poi), normalize(title)
        return difflib.SequenceMatcher(None, a, b).ratio()

    matched_rows = []          # list of (tkey, t, [candidate pins sorted])
    matched_pin_ids = set()
    for tkey, t in targets.items():
        cand = []
        # 1) curated alias (exact POI name -> known PADI travelUrl)
        if t["name"] in ALIASES:
            for p in pins:
                if p["travel_url"] == ALIASES[t["name"]]:
                    cand = [p]
                    break
        # 2) fuzzy match against all pins
        if not cand:
            cand = [p for p in pins if match(t["name"], p["title"])]
            cand.sort(key=lambda p: (bool(NOISE.search(p["title"])),
                                     -sim(t["name"], p["title"])))
        if cand:
            for p in cand:
                matched_pin_ids.add(p["id"])
            matched_rows.append((tkey, t, cand))
            print(f"  MATCH  {t['name']!r}  ->  {cand[0]['title']!r} ({cand[0]['travel_url']})"
                  + (f"   [alt: {len(cand)-1} more]" if len(cand) > 1 else ""))
        else:
            print(f"  no-match {t['name']!r}")

    print("\n== Phase 4: fetch SSR descriptions for matched POIs ==")
    rows = []
    for tkey, t, cand in matched_rows:
        # try candidates in order; use the first that has a real description
        chosen, det = cand[0], {"description": "", "common_sightings": ""}
        for p in cand:
            d = fetch_detail_page(p["travel_url"], p["id"])
            if d["description"]:
                chosen, det = p, d
                break
        else:
            det = fetch_detail_page(chosen["travel_url"], chosen["id"])
        if chosen is not cand[0]:
            print(f"    fallback {t['name']!r} -> {chosen['title']!r}")
        extra = {}
        if chosen.get("types"):
            extra["dive_types"] = chosen["types"]
        if det.get("common_sightings"):
            extra["common_sightings"] = det["common_sightings"]
        if chosen.get("latitude") is not None:
            extra["lat"] = chosen["latitude"]; extra["lng"] = chosen["longitude"]
        source_url = PAGE_BASE + chosen["travel_url"] if chosen["travel_url"] else ""
        rows.append({
            "poi_name": t["name"],
            "poi_id": t["poi_id"],
            "source_url": source_url,
            "official_description": det["description"],
            "extra_attrs": json.dumps(extra, ensure_ascii=False),
            "matched": "true",
            "method": "api",
        })

    print("\n== Phase 4b: target POIs with no PADI match (coverage rows) ==")
    matched_names = {r["poi_name"] for r in rows if r["matched"] == "true"}
    for tkey, t in targets.items():
        if t["name"] in matched_names:
            continue
        rows.append({
            "poi_name": t["name"],
            "poi_id": t["poi_id"],
            "source_url": "",
            "official_description": "",
            "extra_attrs": json.dumps({"reason": "no_padi_match"},
                                        ensure_ascii=False),
            "matched": "false",
            "method": "",
        })
    print(f"  {sum(1 for r in rows if r['matched'] == 'false' and not r['poi_id'].startswith('padi:'))}"
          " target POIs without a PADI match")

    print("\n== Phase 5: unmatched captures (other Red Sea dive sites) ==")
    unmatched = 0
    for p in pins:
        if p["id"] in matched_pin_ids:
            continue
        det = fetch_detail_page(p["travel_url"], p["id"])
        extra = {}
        if p.get("types"):
            extra["dive_types"] = p["types"]
        if det.get("common_sightings"):
            extra["common_sightings"] = det["common_sightings"]
        source_url = PAGE_BASE + p["travel_url"] if p["travel_url"] else ""
        rows.append({
            "poi_name": p["title"] or f"(PADI id {p['id']})",
            "poi_id": f"padi:{p['id']}",
            "source_url": source_url,
            "official_description": det["description"],
            "extra_attrs": json.dumps(extra, ensure_ascii=False),
            "matched": "false",
            "method": "api",
        })
        unmatched += 1
    print(f"  {unmatched} unmatched captures")

    # Write CSV
    fields = ["poi_name", "poi_id", "source_url", "official_description",
              "extra_attrs", "matched", "method"]
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"\n== Wrote {len(rows)} rows -> {OUT_CSV} ==")

    # Coverage summary
    n_matched = sum(1 for r in rows if r["matched"] == "true")
    n_with_desc = sum(1 for r in rows if r["matched"] == "true"
                      and r["official_description"])
    n_nomatch = sum(1 for r in rows if r["matched"] == "false"
                    and not r["poi_id"].startswith("padi:"))
    print("\n===== COVERAGE SUMMARY =====")
    print(f"  Target POIs (natural, dive-site-like): {len(targets)}")
    print(f"  Matched to a PADI dive site         : {n_matched}")
    print(f"  Matched WITH an official description: {n_with_desc}")
    print(f"  Target POIs with NO PADI match      : {n_nomatch}")
    print(f"  Unmatched PADI captures (for review): {unmatched}")
    print(f"  Total CSV rows                      : {len(rows)}")
    print(f"  Tier used: (a) direct JSON API (no browser; Playwright/web_search not needed)")
    if targets:
        miss = [t["name"] for k, t in targets.items()
                if not any(r["poi_id"] == t["poi_id"] and r["matched"] == "true"
                           for r in rows)]
        print(f"  Target POIs with NO PADI match ({len(miss)}):")
        for m in miss:
            print("    -", m)


if __name__ == "__main__":
    main()
