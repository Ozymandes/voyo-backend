#!/usr/bin/env python3
"""
VOYO Database Rebuild Pipeline — AUTHORITATIVE, CLEAN.

Fixes all bugs identified in docs/devlog/PIPELINE_AUDIT.md:
  1. image_urls stored as flat JSON array (was: {'images': [...]} dict wrapper)
  2. tags stored as flat JSON array (was: {'tags': [...]} dict wrapper)
  3. total_reviews from user_ratings_total (was: len(reviews) — capped at 5)
  4. all categories enum-valid (was: 'Nature'/'Modern' rejected by enum)
  5. dedup via upsert-by-name (was: unconditional insert → duplicates)

Image strategy (Decision B): Wikimedia Commons permanent URLs (primary).
Data strategy: Google Places for rating/hours/website/reviews/coords.

Dedup: matches existing POIs by normalized name, UPDATEs in place (preserves
       itinerary FK references), deactivates any orphaned duplicates.

Usage:
  python rebuild_database.py --limit 3       # smoke test on 3 POIs
  python rebuild_database.py --region Cairo   # one region
  python rebuild_database.py                  # all 250
"""
import argparse
import json
import logging
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from dotenv import load_dotenv

load_dotenv()
MASTER_JSON = Path(__file__).parent / "data" / "master_attractions.json"
assert MASTER_JSON.exists(), f"Run clean_master_list.py first — missing {MASTER_JSON}"
MASTER_ATTRACTIONS = json.loads(MASTER_JSON.read_text(encoding="utf-8"))

# ── Config ────────────────────────────────────────────────────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
GOOGLE_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
assert SUPABASE_URL and SUPABASE_KEY, "Supabase env vars required"
assert GOOGLE_KEY, "GOOGLE_PLACES_API_KEY required"

REGION_ID = {  # master region name -> pois.region_id
    "Cairo": 1, "Giza": 2, "Alexandria": 3, "Luxor": 4,
    "Aswan": 5, "Hurghada": 6, "Marsa Alam": 7, "Sinai": 8,
}

GOOGLE_TEXT = "https://maps.googleapis.com/maps/api/place/textsearch/json"
GOOGLE_DETAILS = "https://maps.googleapis.com/maps/api/place/details/json"
WIKI_SUMMARY = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
WIKI_API = "https://en.wikipedia.org/w/api.php"
UA = {"User-Agent": "VoyoApp/1.0 (educational thesis project)"}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler()],
)
log = logging.getLogger("rebuild")


# ── Helpers ───────────────────────────────────────────────────────────────
def norm(name: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", name.lower()).strip()


def with_retry(fn, tries=4, base_delay=1.0):
    last = None
    for i in range(tries):
        try:
            return fn()
        except Exception as e:
            last = e
            time.sleep(base_delay * (2 ** i))
    raise last


# ── Source 1: Wikimedia (images + coordinates) ────────────────────────────
def wikimedia_fetch(name: str, region: str, search_queries: list):
    """Return {images: [urls], coords: (lat,lng), significance, arabic} or {}."""
    out = {}
    candidates = list(search_queries or []) + [name, f"{name} {region}"]
    for cand in candidates:
        title = cand.strip()
        try:
            r = requests.get(WIKI_SUMMARY.format(title=title), headers=UA, timeout=12)
            if r.status_code != 200:
                continue
            d = r.json()
            # validate it's a real article, not a disambiguation
            if d.get("type") == "disambiguation" or not d.get("extract"):
                continue
            img = (d.get("originalimage") or {}).get("source") or \
                  (d.get("thumbnail") or {}).get("source")
            if img:
                out["images"] = [img]  # one solid permanent image
            if d.get("extract"):
                out["significance"] = d["extract"]
            break
        except Exception:
            continue

    # coordinates via MediaWiki API (more reliable than summary)
    for cand in candidates[:2]:
        try:
            r = requests.get(WIKI_API, params={
                "action": "query", "format": "json", "prop": "coordinates",
                "titles": cand.strip(), "colimit": "1",
            }, headers=UA, timeout=12)
            pages = r.json().get("query", {}).get("pages", {})
            for pg in pages.values():
                coords = pg.get("coordinates")
                if coords:
                    out["coords"] = (coords[0]["lat"], coords[0]["lon"])
                    break
            if "coords" in out:
                break
        except Exception:
            continue

    return out


# ── Source 2: Google Places (structured data) ─────────────────────────────
def google_fetch(name: str, region: str, search_queries: list):
    """Return dict of structured fields, or {} on failure."""
    queries = list(search_queries or []) + [f"{name} {region} Egypt"]
    place_id = None
    for q in queries:
        try:
            r = with_retry(lambda q=q: requests.get(GOOGLE_TEXT, params={
                "query": q, "key": GOOGLE_KEY,
                "fields": "place_id,name,rating,user_ratings_total,geometry",
            }, timeout=12))
            j = r.json()
            if j.get("status") == "OK" and j.get("results"):
                place_id = j["results"][0]["place_id"]
                break
        except Exception:
            continue
    if not place_id:
        return {}

    try:
        r = with_retry(lambda: requests.get(GOOGLE_DETAILS, params={
            "place_id": place_id, "key": GOOGLE_KEY,
            "fields": "name,formatted_address,geometry,rating,user_ratings_total,"
                      "opening_hours,website,formatted_phone_number,price_level",
        }, timeout=12))
        j = r.json()
        if j.get("status") != "OK":
            return {}
        d = j.get("result", {})
    except Exception as e:
        log.warning(f"google details failed for {name}: {e}")
        return {}

    loc = d.get("geometry", {}).get("location", {})
    out = {
        "google_place_id": place_id,
        "address": d.get("formatted_address"),
        "coords": (loc.get("lat"), loc.get("lng")) if loc.get("lat") else None,
        "rating": d.get("rating"),
        "total_reviews": d.get("user_ratings_total", 0),  # FIX bug #3
        "website_url": d.get("website"),
        "phone_number": d.get("formatted_phone_number"),
        "price_level": d.get("price_level"),
    }
    weekday = (d.get("opening_hours") or {}).get("weekday_text")
    if weekday:
        out["opening_hours"] = {"weekday_text": weekday}
    return out


# ── Merge sources -> POI row ──────────────────────────────────────────────
def build_row(entry: dict, region: str) -> dict:
    """Combine master entry + wikimedia + google into a Supabase-ready row."""
    name = entry["name"]
    wiki = with_retry(lambda: wikimedia_fetch(name, region, entry.get("search_queries")), tries=3)
    time.sleep(0.1)  # gentle on Wikimedia
    goog = google_fetch(name, region, entry.get("search_queries"))

    # Coordinates: prefer Google, fall back to Wikimedia
    coords = goog.get("coords") or wiki.get("coords")

    row = {
        "name": name,
        "name_arabic": entry.get("name_arabic") or None,
        "category": entry["category"],  # already lowercase enum value
        "region_id": REGION_ID[region],
        "description": entry.get("description") or "",
        "historical_significance": wiki.get("significance") or entry.get("description"),
        "address": goog.get("address") or "",
        "latitude": coords[0] if coords else None,
        "longitude": coords[1] if coords else None,
        "average_rating": goog.get("rating") or entry.get("expected_rating") or None,
        "total_reviews": goog.get("total_reviews") or 0,
        "ticket_price": entry.get("ticket_price"),
        "currency": "EGP" if entry.get("ticket_price") else None,
        "website_url": goog.get("website_url") or None,
        "phone_number": goog.get("phone_number") or None,
        "opening_hours": goog.get("opening_hours") or None,
        "image_urls": wiki.get("images") or [],   # FIX bug #1: flat array
        "tags": _build_tags(entry, wiki),          # FIX bug #2: flat array
        "is_active": True,
        "is_verified": True,
        "updated_at": datetime.utcnow().isoformat(),
    }
    # popularity: derive from reviews
    tr = row["total_reviews"]
    row["popularity_score"] = round(min(100, (tr / 500) * 10) + 
                                    (10 if entry.get("importance") == "Must-See" else 0) +
                                    (15 if entry.get("importance") == "World Wonder" else 0), 1)
    return row


def _build_tags(entry: dict, wiki: dict) -> list:
    tags = [entry["category"]]
    if entry.get("UNESCO_site"):
        tags.append("unesco")
    imp = entry.get("importance")
    if imp in ("Must-See", "World Wonder"):
        tags.append("must-see")
    if imp == "World Wonder":
        tags.append("world-wonder")
    return list(dict.fromkeys(tags))  # dedup preserve order


# ── Supabase upsert-by-name ───────────────────────────────────────────────
class DB:
    def __init__(self):
        self.hdr = {
            "apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json", "Prefer": "return=representation",
        }
        self.name_map = {}  # normalized name -> [ids]
        self.columns = set()
        self._detect_columns()
        self._load_existing()

    def _detect_columns(self):
        """Probe the live schema so we only write columns that actually exist.
        Makes the pipeline robust to schema drift (e.g. missing phone_number/city)."""
        try:
            r = requests.get(f"{SUPABASE_URL}/rest/v1/pois?select=*&limit=1",
                             headers=self.hdr, timeout=15)
            rows = r.json()
            if rows:
                self.columns = set(rows[0].keys())
                log.info(f"Live pois columns ({len(self.columns)}): {sorted(self.columns)}")
        except Exception as e:
            log.warning(f"column probe failed ({e}); writing all fields")

    def _load_existing(self):
        r = requests.get(f"{SUPABASE_URL}/rest/v1/pois?select=id,name,is_active",
                         headers=self.hdr, params={"limit": "1000"})
        for p in r.json():
            k = norm(p["name"])
            self.name_map.setdefault(k, []).append(p["id"])
        log.info(f"Loaded {sum(len(v) for v in self.name_map.values())} existing POIs "
                 f"({len(self.name_map)} unique names)")

    def upsert(self, row: dict):
        # Filter to columns that actually exist (robust to schema drift)
        safe = {k: v for k, v in row.items() if k in self.columns} if self.columns else dict(row)
        key = norm(safe["name"])
        ids = self.name_map.get(key, [])
        if ids:
            keep_id = min(ids)
            for dup_id in ids:
                if dup_id != keep_id:
                    self._patch(dup_id, {"is_active": False})
            self._patch(keep_id, safe)
            return ("updated", keep_id)
        else:
            new_id = self._insert(safe)
            if new_id:
                self.name_map.setdefault(key, []).append(new_id)
            return ("inserted", new_id)

    def _patch(self, poi_id, fields):
        safe = {k: v for k, v in fields.items() if k in self.columns} if self.columns else dict(fields)
        r = requests.patch(f"{SUPABASE_URL}/rest/v1/pois?id=eq.{poi_id}",
                           headers=self.hdr, json=safe, timeout=15)
        # 204 = no body, 200 = return=representation. Both are success.
        if r.status_code not in (200, 204):
            log.error(f"PATCH {poi_id} failed: {r.status_code} {r.text[:150]}")

    def _insert(self, row):
        safe = {k: v for k, v in row.items() if k in self.columns} if self.columns else dict(row)
        r = requests.post(f"{SUPABASE_URL}/rest/v1/pois", headers=self.hdr, json=safe, timeout=15)
        if r.status_code == 201:
            return r.json()[0]["id"]
        log.error(f"INSERT '{safe.get('name')}' failed: {r.status_code} {r.text[:150]}")
        return None


# ── Orchestration ─────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--region", help="single region")
    ap.add_argument("--limit", type=int, help="max POIs (smoke test)")
    args = ap.parse_args()

    work = []
    for region, attrs in MASTER_ATTRACTIONS.items():
        if args.region and region != args.region:
            continue
        for a in attrs:
            work.append((region, a))
    if args.limit:
        work = work[: args.limit]

    log.info(f"=" * 60)
    log.info(f"REBUILD: {len(work)} POIs" +
             (f" region={args.region}" if args.region else "") +
             (f" limit={args.limit}" if args.limit else ""))
    log.info(f"=" * 60)

    db = DB()
    results = {"updated": 0, "inserted": 0, "failed": 0}
    failures = []

    def process(item):
        region, entry = item
        try:
            row = build_row(entry, region)
            if row["latitude"] is None:
                raise ValueError("no coordinates from any source")
            return db.upsert(row)
        except Exception as e:
            return ("failed", str(e), entry["name"])

    # Sequential with gentle pacing (Google rate safety). Parallelism risks 429.
    for i, item in enumerate(work, 1):
        res = process(item)
        tag = res[0]
        results[tag] = results.get(tag, 0) + 1
        if tag == "failed":
            failures.append(res[2])
        if i % 10 == 0 or i == len(work):
            log.info(f"  [{i}/{len(work)}] updated={results['updated']} "
                     f"inserted={results['inserted']} failed={results['failed']}")
        time.sleep(0.15)  # gentle pacing

    log.info(f"=" * 60)
    log.info(f"DONE. {results}")
    if failures:
        log.warning(f"{len(failures)} failures:")
        for f in failures[:20]:
            log.warning(f"  - {f}")
    # write report
    Path("rebuild_report.json").write_text(json.dumps({
        "total": len(work), "results": results,
        "failures": failures, "timestamp": datetime.utcnow().isoformat(),
    }, indent=2))
    log.info("Report: rebuild_report.json")


if __name__ == "__main__":
    main()
