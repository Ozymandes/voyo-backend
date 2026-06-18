#!/usr/bin/env python3
"""
Scrape experienceegypt.eg for regional / city descriptive prose.

WHAT THIS SOURCE ACTUALLY YIELDS (honest scope):
  experienceegypt.eg is a SERVER-RENDERED marketing portal (Cloudflare Rocket
  Loader only; plain requests work — NO Playwright needed). The descriptive
  copy lives on the CITY pages (/en/city/{id}/{slug}). The REGION pages
  (/en/region/{id}/{slug}) are navigation landing pages that carry NO
  descriptive prose. There is NO per-POI structured data here (no tickets,
  opening hours, or official per-site descriptions) — only region/city-level
  marketing prose.

  Therefore every row below is REGION/CITY-LEVEL CONTEXT, not a specific POI's
  official record. A row is marked matched=true ONLY when a single paragraph
  clearly and specifically describes one named POI we already hold (the POI
  name leads the paragraph and no other indexed POI is named). Everything else
  is recorded as honest region-level context with matched=false.

OUTPUT:
  data/enrichment_sources_expeg.csv
    columns: poi_name, poi_id, region, source_url, official_description,
             matched(bool), method(bs4)

  poi_id is intentionally left blank: the live POI ids live in the cloud
  Supabase DB, which this task is explicitly forbidden to touch; names are
  matched against data/master_attractions.json instead.

Re-runnable: `python3 scripts/scrape/scrape_experienceegypt.py`
Polite: 2s delay between requests, descriptive User-Agent, bs4 only.
"""
from __future__ import annotations
import csv
import json
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
BASE = "https://www.experienceegypt.eg"
DELAY = 2.0  # seconds between requests (polite)
TIMEOUT = 30
HDR = {
    "User-Agent": ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"),
    "Accept-Language": "en-US,en;q=0.9",
}

# (label, path, [voyo regions this page covers])
PAGES = [
    ("Cairo & Giza",     "/en/city/1/cairo-giza",          ["Cairo", "Giza"]),
    ("Luxor",            "/en/city/22/luxor",              ["Luxor"]),
    ("Aswan",            "/en/city/9/aswan-abu-simbel",    ["Aswan"]),
    ("Sharm El Sheikh",  "/en/city/16/sharm-al-sheikh",    ["Sinai"]),
    ("Hurghada",         "/en/city/23/hurghada",           ["Hurghada"]),
    ("The Nile",         "/en/region/12/the-nile",         ["Cairo", "Luxor", "Aswan"]),
    ("The Red Sea",      "/en/region/13/the-red-sea",      ["Hurghada", "Marsa Alam", "Sinai"]),
    ("The Mediterranean","/en/region/14/the-mediterranean",["Alexandria"]),
    ("Deserts & Oases",  "/en/region/15/deserts-oases",    ["Marsa Alam"]),
]

# Boilerplate snippets to exclude from "main descriptive prose".
BOILER = [
    "subscribe", "newsletter", "cookie", "find your dream", "get ready for the",
    "upcoming event", "eye on egypt", "good to know", "about egypt", "where to go",
    "what to do", "what's on", "useful information", "all rights reserved",
    "sign up", "read more", "recommended places", "plan your trip",
    "official promotional website", "tourism authority", "ministry of tourism",
]


# --------------------------------------------------------------------------- #
# POI index (from master_attractions.json)
# --------------------------------------------------------------------------- #
def build_poi_index():
    """Return list of dicts: {name, region, keys:set[str]} for conservative matching."""
    data = json.loads((ROOT / "data" / "master_attractions.json").read_text())
    index = []
    for region, items in data.items():
        for it in items:
            name = it["name"]
            base = re.sub(r"\s*\(.*?\)\s*", " ", name).strip()       # strip parenthetical
            base = re.sub(r"\s{2,}", " ", base)
            inner = re.findall(r"\(([^)]*)\)", name)                  # parenthetical content
            keys = set()
            for n in {name, base}:
                if n:
                    keys.add(n)
                    keys.add(n.replace("el-", "al-").replace("El-", "Al-"))
                    keys.add(n.replace("al-", "el-").replace("Al-", "El-"))
            # add parenthetical as alias only if multi-word & long (avoid noisy single words)
            for ip in inner:
                ip = ip.strip()
                if len(ip) >= 8 and len(ip.split()) >= 2:
                    keys.add(ip)
            # drop trivially short keys (<5 chars) that would over-match
            keys = {k for k in keys if len(k) >= 5}
            index.append({"name": name, "region": region, "keys": keys})
    return index


def first_sentence(text: str) -> str:
    return text.split(".")[0].lower()


def pois_in_text(text: str, index):
    """Return list of matched POI names whose name appears (word-boundary)."""
    low = text.lower()
    found = []
    for poi in index:
        for k in poi["keys"]:
            kl = k.lower()
            pat = r"(?<![a-z0-9])" + re.escape(kl) + r"(?![a-z0-9])"
            if re.search(pat, low):
                found.append(poi["name"])
                break
    # de-duplicate preserving order
    seen = set()
    uniq = []
    for n in found:
        if n not in seen:
            seen.add(n)
            uniq.append(n)
    return uniq


# --------------------------------------------------------------------------- #
# Extraction
# --------------------------------------------------------------------------- #
def extract_prose(soup):
    """Return list of substantial descriptive paragraph strings."""
    paras = []
    for p in soup.find_all("p"):
        t = " ".join(p.get_text(" ", strip=True).split())
        if len(t) < 100:          # substantial prose only
            continue
        if "." not in t:          # must read as a sentence
            continue
        low = t.lower()
        if any(b in low for b in BOILER):
            continue
        paras.append(t)
    # de-duplicate while keeping order
    seen, out = set(), []
    for t in paras:
        k = t.lower()
        if k not in seen:
            seen.add(k)
            out.append(t)
    return out


def fetch(path):
    url = BASE + path
    r = requests.get(url, headers=HDR, timeout=TIMEOUT)
    return r


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main():
    out_csv = ROOT / "data" / "enrichment_sources_expeg.csv"
    index = build_poi_index()

    rows = []          # CSV rows
    summary = []       # (label, status, n_prose, region_rows, poi_rows)

    for label, path, regions in PAGES:
        try:
            r = fetch(path)
            status = r.status_code
        except Exception as e:  # network blip
            print(f"[!] {label}: fetch error {e}", file=sys.stderr)
            summary.append((label, "ERR", 0, 0, 0))
            continue

        soup = BeautifulSoup(r.text, "html.parser") if status == 200 else None
        prose = extract_prose(soup) if soup else []
        url = BASE + path
        region_rows = 0
        poi_rows = 0

        if prose:
            # 1) region-level context row (the honest primary deliverable)
            joined = "\n\n".join(prose)
            rows.append({
                "poi_name": "", "poi_id": "", "region": label,
                "source_url": url, "official_description": joined,
                "matched": "false", "method": "bs4",
            })
            region_rows = 1

            # 2) conservative single-POI matches per paragraph
            matched_by_poi = {}
            for para in prose:
                hits = pois_in_text(para, index)
                if len(hits) != 1:
                    continue  # 0 or >1 => not a focused single-site description
                poi_name = hits[0]
                keyset = next(p["keys"] for p in index if p["name"] == poi_name)
                # require the POI name to appear in the FIRST sentence ...
                if not any(k.lower() in first_sentence(para) for k in keyset):
                    continue
                # ... AND keep only short, focused site "tips". Long paragraphs
                # here are multi-site regional/city overviews (verified 500-600
                # chars) that would falsely attach to the one indexed POI they
                # happen to name; genuine single-site cards are ~110-160 chars.
                if len(para) > 200:
                    continue
                matched_by_poi.setdefault(poi_name, []).append(para)

            for poi_name, paras in matched_by_poi.items():
                poi_region = next(p["region"] for p in index if p["name"] == poi_name)
                rows.append({
                    "poi_name": poi_name, "poi_id": "", "region": poi_region,
                    "source_url": url, "official_description": "\n\n".join(paras),
                    "matched": "true", "method": "bs4",
                })
                poi_rows += 1

        summary.append((label, status, len(prose), region_rows, poi_rows))
        print(f"[+] {label:20} status={status} prose_paras={len(prose)} "
              f"region_rows={region_rows} poi_rows={poi_rows}")
        time.sleep(DELAY)

    # write CSV
    fields = ["poi_name", "poi_id", "region", "source_url",
              "official_description", "matched", "method"]
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow(row)

    # coverage summary
    print("\n" + "=" * 64)
    print("COVERAGE SUMMARY — experienceegypt.eg")
    print("=" * 64)
    print(f"{'page':22}{'status':>8}{'prose':>7}{'region':>8}{'poi':>6}")
    tot_prose = tot_region = tot_poi = 0
    for label, status, n, rr, pr in summary:
        print(f"{label:22}{str(status):>8}{n:>7}{rr:>8}{pr:>6}")
        tot_prose += n
        tot_region += rr
        tot_poi += pr
    print("-" * 51)
    print(f"{'TOTAL':22}{'':>8}{tot_prose:>7}{tot_region:>8}{tot_poi:>6}")
    print(f"\nCSV rows written: {len(rows)}  ->  {out_csv}")
    print(f"  region-level context rows (matched=false): {sum(1 for r in rows if r['matched']=='false')}")
    print(f"  single-POI description rows (matched=true): {sum(1 for r in rows if r['matched']=='true')}")
    print("\nNOTE: region pages carry NO prose (navigation landing pages only).")
    print("NOTE: all rows are region/city-level marketing context, NOT per-POI")
    print("      structured data (no tickets / hours / official per-site text).")


if __name__ == "__main__":
    main()
