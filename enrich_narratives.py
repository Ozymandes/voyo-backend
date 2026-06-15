#!/usr/bin/env python3
"""
One-time batch script: generates a ~120-word LLM narrative for each POI
and writes it to the `narrative` column in Supabase.

Prerequisites:
    1. Run config/sql/002_add_narrative.sql in Supabase SQL editor.
    2. Set env vars: GROQ_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY

Usage:
    python enrich_narratives.py               # enrich all unenriched POIs
    python enrich_narratives.py --dry-run     # generate but don't write
    python enrich_narratives.py --limit 50    # process first 50 only
    python enrich_narratives.py --all         # re-enrich even existing ones

Token budget: 255 POIs × ~450 tokens ≈ 115k tokens total.
Groq free tier = 100k/day. Run in two sittings or after a quota reset.
"""

import os
import sys
import time
import argparse

from dotenv import load_dotenv
from groq import Groq
from supabase import create_client

load_dotenv()

GROQ_API_KEY  = os.getenv('GROQ_API_KEY')
SUPABASE_URL  = os.getenv('SUPABASE_URL')
SUPABASE_KEY  = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_ANON_KEY')

MODEL          = 'llama-3.3-70b-versatile'
CALL_DELAY     = 2.0   # seconds between Groq calls — stay well under rate limits
MAX_TOKENS_OUT = 200   # ~120-word narrative fits comfortably

PROMPT_TEMPLATE = """\
You are an expert travel writer specialising in Egypt. Write a vivid, \
culturally rich description of the following Egyptian site in 110-130 words. \
Write in second person ("you"). Capture the atmosphere, the history, and \
what makes it worth visiting. Use flowing prose — no bullet points, no headers.

Name: {name}
Category: {category}
City / Region: {city}
Historical significance: {significance}
Current description: {description}

Write the narrative now:"""


def make_prompt(poi: dict) -> str:
    return PROMPT_TEMPLATE.format(
        name        = poi.get('name', ''),
        category    = poi.get('category', 'attraction'),
        city        = poi.get('city') or 'Egypt',
        significance= poi.get('historical_significance') or 'Not specified',
        description = poi.get('description') or 'Not specified',
    )


def generate(client: Groq, poi: dict) -> str | None:
    try:
        resp = client.chat.completions.create(
            model    = MODEL,
            messages = [{'role': 'user', 'content': make_prompt(poi)}],
            max_tokens  = MAX_TOKENS_OUT,
            temperature = 0.75,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f'  ✗ Groq error: {e}')
        return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true',
                        help='Generate text but do not write to Supabase')
    parser.add_argument('--limit', type=int, default=0,
                        help='Cap number of POIs processed (0 = all)')
    parser.add_argument('--all', dest='all_pois', action='store_true',
                        help='Re-enrich POIs that already have a narrative')
    args = parser.parse_args()

    if not all([GROQ_API_KEY, SUPABASE_URL, SUPABASE_KEY]):
        sys.exit('Missing env vars: GROQ_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY')

    groq      = Groq(api_key=GROQ_API_KEY)
    supabase  = create_client(SUPABASE_URL, SUPABASE_KEY)

    q = supabase.from_('pois').select(
        'id, name, category, city, historical_significance, description'
    ).eq('is_active', True)

    if not args.all_pois:
        q = q.is_('narrative', 'null')

    result = q.order('popularity_score', desc=True).execute()
    pois   = result.data

    if args.limit:
        pois = pois[:args.limit]

    total = len(pois)
    print(f'POIs to enrich : {total}')
    print(f'Est. tokens    : {total * 450:,}  (~{total * 450 / 100_000:.1f} day quota)')
    print(f'Mode           : {"DRY RUN" if args.dry_run else "LIVE WRITE"}\n')

    ok = fail = 0
    for i, poi in enumerate(pois, 1):
        print(f'[{i}/{total}] {poi["name"]} ({poi.get("city", "?")})', end=' … ', flush=True)

        narrative = generate(groq, poi)
        if not narrative:
            fail += 1
            continue

        if args.dry_run:
            print(f'OK (dry)\n        {narrative[:90]}…')
            ok += 1
        else:
            try:
                supabase.from_('pois').update(
                    {'narrative': narrative}
                ).eq('id', poi['id']).execute()
                print('OK')
                ok += 1
            except Exception as e:
                print(f'DB ERROR: {e}')
                fail += 1

        if i < total:
            time.sleep(CALL_DELAY)

    print(f'\n{"─" * 50}')
    print(f'Done  ✓ {ok}   ✗ {fail}')
    if not args.dry_run and ok:
        print('Verify: SELECT COUNT(*) FROM pois WHERE narrative IS NOT NULL;')


if __name__ == '__main__':
    main()
