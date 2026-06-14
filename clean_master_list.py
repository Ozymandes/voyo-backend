"""
VOYO Master List Cleaner
Produces a de-duplicated, enum-safe, importance-filtered master list as JSON.

Decision A: keep Must-See + World Wonder + Major, drop Minor.
  - Fix categories: 'Nature' -> 'Natural', 'Modern' -> 'Cultural'
  - Remove intra-list duplicate names (keep first occurrence)
  - Output: data/master_attractions.json (data-as-data, no Python-literal issues)
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "data"))
import master_attractions_clean as ml  # original .py source of truth

ENUM_VALUES = {'historical', 'cultural', 'religious', 'natural',
               'entertainment', 'shopping', 'dining',
               'accommodation', 'transportation', 'services'}

CAT_MAP = {
    'Historical': 'historical', 'Cultural': 'cultural', 'Religious': 'religious',
    'Natural': 'natural', 'Entertainment': 'entertainment', 'Shopping': 'shopping',
    'Dining': 'dining', 'Accommodation': 'accommodation',
    'Transportation': 'transportation', 'Services': 'services',
    'Nature': 'natural',        # FIX: was invalid
    'Modern': 'cultural',       # FIX: was invalid -> cultural is closest
}

KEEP_IMPORTANCE = {'Must-See', 'World Wonder', 'Major'}


def normalize(name: str) -> str:
    return re.sub(r'[^a-z0-9 ]', '', name.lower()).strip()


def main():
    raw = ml.MASTER_ATTRACTIONS
    cleaned = {}
    dropped = {'minor': [], 'dup': [], 'unmapped_cat': []}
    seen = set()
    before_total = sum(len(v) for v in raw.values())
    cat_usage = Counter()

    for region, attrs in raw.items():
        kept = []
        for a in attrs:
            name = a['name']
            imp = a.get('importance', 'Major')

            if imp not in KEEP_IMPORTANCE:
                dropped['minor'].append((region, name, imp))
                continue
            key = normalize(name)
            if key in seen:
                dropped['dup'].append((region, name))
                continue
            seen.add(key)

            raw_cat = a.get('category', 'Historical')
            mapped = CAT_MAP.get(raw_cat)
            if mapped is None:
                dropped['unmapped_cat'].append((region, name, raw_cat))
                continue
            cat_usage[mapped] += 1

            entry = dict(a)
            entry['category'] = mapped  # store lowercase enum value directly
            kept.append(entry)
        if kept:
            cleaned[region] = kept

    after_total = sum(len(v) for v in cleaned.values())

    print("=" * 70)
    print("MASTER LIST CLEANUP REPORT")
    print("=" * 70)
    print(f"Before: {before_total} | After: {after_total} | Dropped: {before_total - after_total}")
    print(f"  Minor: {len(dropped['minor'])} | Dup: {len(dropped['dup'])} | Unmapped: {len(dropped['unmapped_cat'])}")
    print("\nBy region (after):")
    for r, c in sorted(cleaned.items(), key=lambda x: -len(x[1])):
        print(f"  {r:14} {c}")
    print("\nCategories:", "ALL VALID ✓" if all(c in ENUM_VALUES for c in cat_usage) else "INVALID!")
    for c, n in cat_usage.most_common():
        flag = "" if c in ENUM_VALUES else " <INVALID>"
        print(f"  {c:16} {n}{flag}")

    out_path = Path(__file__).parent / "data" / "master_attractions.json"
    out_path.write_text(json.dumps(cleaned, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\n✓ Wrote: {out_path} ({after_total} entries)")


if __name__ == "__main__":
    main()
