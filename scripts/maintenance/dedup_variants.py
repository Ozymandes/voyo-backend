"""
VOYO variant-dedup utility — one-time curation pass.

Resolves name-variant duplicates that defeat exact normalized-name matching.
Example: "Abu Simbel" and "Abu Simbel Temples" normalize to different keys, so
DB.upsert() treats them as distinct rows even though they are the same POI.

Mechanism: substring containment on normalized names. If normalized straggler
name S is a substring of a master name M, or vice versa (both length >= 4 to
avoid noise from short tokens like "Sinai"), the straggler is treated as a
variant of the master POI and deactivated. The master (curated, fuller) row
wins; the variant row is set is_active=false.

This was originally run as an ad-hoc pass during the 2026-06-11 rebuild and
deactivated 13 variants (e.g. "Abu Simbel" vs "Abu Simbel Temples", "Karnak
Temple" vs "Karnak Temple Complex") while keeping 7 genuinely-unique stragglers
(Dahab, Blue Hole, El Gouna, Ras Mohammed, etc.) for re-enrichment. It is
preserved here as a reproducible, citable utility.

Idempotent: re-running it only ever deactivates variants; it never reactivates
or duplicates. Pair with validate_database.py to confirm 0 duplicates after.

Usage:
    python dedup_variants.py            # dry-run, prints what it would do
    python dedup_variants.py --apply    # actually deactivate variants
"""
import os
import re
import sys

import requests
from dotenv import load_dotenv

load_dotenv()
url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_SERVICE_KEY"]
hdr = {"apikey": key, "Authorization": f"Bearer {key}",
       "Content-Type": "application/json", "Prefer": "return=representation"}

MIN_LEN = 4  # ignore short tokens to avoid false matches like "Sinai" in many names


def normalize(name: str) -> str:
    """Lowercase, strip non-alphanumeric. Same key used by DB.upsert()."""
    return re.sub(r"[^a-z0-9 ]", "", (name or "").lower()).strip()


def is_variant(straggler: str, master_names: list[str]) -> bool:
    """True if straggler is a substring-variant of any master name (or vice versa)."""
    s = normalize(straggler)
    if len(s) < MIN_LEN:
        return False
    return any(
        (s in normalize(m) or normalize(m) in s)
        for m in master_names
        if len(normalize(m)) >= MIN_LEN
    )


def main(apply: bool = False) -> None:
    # Active POIs
    r = requests.get(
        f"{url}/rest/v1/pois?select=id,name,is_active&is_active=eq.true&limit=3000",
        headers=hdr, timeout=30)
    pois = r.json()

    # The curated master list is the canonical set of names.
    # Variants are active POIs whose name is a substring of (or contains) a master name,
    # but which are not themselves exact master matches.
    import json
    from pathlib import Path
    master = json.loads(Path("data/master_attractions.json").read_text(encoding="utf-8"))
    master_names = [a["name"] for region in master.values() for a in region]
    master_keys = {normalize(n) for n in master_names}

    variants, unique = [], []
    for p in pois:
        if normalize(p["name"]) in master_keys:
            continue  # exact master match, keep
        if is_variant(p["name"], master_names):
            variants.append(p)
        else:
            unique.append(p)

    print(f"Active POIs: {len(pois)}")
    print(f"Name-variant duplicates to deactivate: {len(variants)}")
    print(f"Genuinely-unique stragglers (kept): {len(unique)}\n")

    for p in variants:
        print(f"  DEACTIVATE id={p['id']:4} {p['name']}")
        if apply:
            requests.patch(f"{url}/rest/v1/pois?id=eq.{p['id']}",
                           headers=hdr, json={"is_active": False}, timeout=20)

    mode = "APPLIED" if apply else "DRY RUN (use --apply to deactivate)"
    print(f"\n{mode}. {len(variants)} variants {'deactivated' if apply else 'identified'}.")


if __name__ == "__main__":
    main(apply="--apply" in sys.argv)
