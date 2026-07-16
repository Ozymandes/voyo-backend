#!/usr/bin/env python3
"""
One-time batch script: generates a ~120-word LLM narrative for each POI
and writes it to the `narrative` column in Supabase.

Prerequisites:
    1. Run config/sql/002_add_narrative.sql in Supabase SQL editor.
    2. Set env vars: GROQ_API_KEY, SUPABASE_URL, SUPABASE_SECRET_KEY

Usage:
    python enrich_narratives.py               # enrich all unenriched POIs
    python enrich_narratives.py --dry-run     # generate but don't write
    python enrich_narratives.py --limit 50    # process first 50 only
    python enrich_narratives.py --all         # re-enrich even existing ones

Grounding: each POI is grounded in its Wikipedia article (search-based
fetch) before generation, so narratives cite real facts — not LLM memory.
An anti-hallucination prompt constrains output to the sourced material.
Source audit trail → thesis/evidence/narrative_sources.json.

Token budget (grounded): ~315 POIs × ~1200 tokens ≈ 380k total.
Groq free tier = 100k/day → ~4 sittings across ~4 days (script is idempotent:
re-running skips already-enriched POIs).
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path

import requests
from dotenv import load_dotenv
from groq import Groq
from supabase import create_client

load_dotenv()

GROQ_API_KEY  = os.getenv('GROQ_API_KEY')
SUPABASE_URL  = os.getenv('SUPABASE_URL')
SUPABASE_KEY  = os.getenv('SUPABASE_SECRET_KEY')
# The Tavily key is stored as SEARCH_API_KEY in .env (SEARCH_PROVIDER=tavily),
# consistent with src/cleo/tools/web_search_tool.py. Fall back to the explicit
# TAVILY_API_KEY name in case the operator sets it that way instead.
TAVILY_API_KEY = os.getenv('SEARCH_API_KEY') or os.getenv('TAVILY_API_KEY')

# LLM provider: z.ai (GLM) when Z_AI_API_KEY is set, else Groq (original path).
# z.ai's GLM Coding Plan credits live on the *coding* endpoint, not the general
# one (general returns code 1113 "no resource package"), so Z_AI_BASE_URL defaults
# to the coding endpoint. MODEL is env-overridable via LLM_MODEL; glm-4.7 is the
# default because the 5.x line are reasoning-first models whose thinking tokens
# eat the 200-token output budget — 4.7 returns prose directly.
Z_AI_API_KEY  = os.getenv('Z_AI_API_KEY')
Z_AI_BASE_URL = os.getenv('Z_AI_BASE_URL') or 'https://api.z.ai/api/coding/paas/v4'
USE_ZAI       = bool(Z_AI_API_KEY)
MODEL         = (os.getenv('Z_AI_MODEL') or 'glm-4.7') if USE_ZAI else (os.getenv('LLM_MODEL') or 'llama-3.3-70b-versatile')
CALL_DELAY     = 2.0   # seconds between LLM calls — stay well under rate limits
# Gold-standard depth: ~300-340 word expert profile + 3-4 short tips.
# ~560 words total ~ 750 tokens headroom for the structured NARRATIVE:/TIPS: format.
MAX_TOKENS_OUT = 750

# ── Grounding: Wikipedia (free, high-quality source for Egyptian sites) ────
WIKI_API = 'https://en.wikipedia.org/w/api.php'
TAVILY_API = 'https://api.tavily.com/search'
UA = {'User-Agent': 'VoyoApp/1.0 (thesis narrative enrichment)'}

# ── Official scraped sources (HIGHEST priority grounding) ─────────────────
# Produced by the voyo-scrape chain: egymonuments.gov.eg, padi.com,
# experienceegypt.eg → real official descriptions, not LLM memory.
# Falls back gracefully to Wikipedia when the file is absent (pre-scrape) so
# the pipeline still works standalone.
OFFICIAL_SOURCES_XLSX = Path(__file__).parent / 'data' / 'enrichment_sources.xlsx'
OFFICIAL_SOURCES_CSV = Path(__file__).parent / 'data' / 'enrichment_sources.csv'
OFFICIAL_SOURCES = {}  # populated in main() after argparse


def _norm_name(s: str) -> str:
    """Normalize a POI name for cross-source matching."""
    import re
    return re.sub(r'[^a-z0-9]', '', s.lower())


def load_official_sources():
    """Load the voyo-scrape master file into {norm_name: {description, url}}.
    Prefers the .csv (pandas reads it natively, no extra deps); falls back to
    .xlsx (needs openpyxl). Returns {} if neither loads — Wikipedia/Tavily
    then handle every POI. Bugfix: previously picked .xlsx first and, when
    openpyxl was absent, bailed to {} instead of trying .csv, silently dropping
    all 178 official sources."""
    try:
        import pandas as pd
    except ImportError:
        return {}
    candidates = []
    if OFFICIAL_SOURCES_CSV.exists():
        candidates.append(OFFICIAL_SOURCES_CSV)
    if OFFICIAL_SOURCES_XLSX.exists():
        candidates.append(OFFICIAL_SOURCES_XLSX)
    df = None
    loaded_from = None
    for src in candidates:
        try:
            df = pd.read_csv(src) if src.suffix == '.csv' else pd.read_excel(src)
            loaded_from = src.name
            break
        except Exception as e:
            print(f'  (official sources: {src.name} skipped: {e})', flush=True)
    if df is None:
        return {}
    col_desc = next((c for c in df.columns if 'desc' in c.lower()), None)
    col_url = next((c for c in df.columns if c.lower() in ('source_url', 'url', 'best_source_url')), None)
    col_name = next((c for c in df.columns if c.lower() in ('poi_name', 'name')), None)
    if not (col_desc and col_name):
        return {}
    rows = {}
    for _, r in df.iterrows():
        raw_name = r.get(col_name)
        if not isinstance(raw_name, str) or not raw_name.strip():
            continue  # blank/NaN name row
        desc = r.get(col_desc)
        if not isinstance(desc, str) or len(desc) < 40:
            continue  # no real description → let Wikipedia/Tavily handle this POI
        rows[_norm_name(raw_name)] = {
            'description': desc[:2500],
            'url': r.get(col_url) if col_url and isinstance(r.get(col_url), str) else None,
        }
    print(f'  (official sources loaded: {len(rows)} POIs with descriptions, from {loaded_from})', flush=True)
    return rows


def _tokens(s: str) -> set:
    """Significant lowercase tokens (len >= 4) for relevance matching."""
    return {w.lower().strip('.,()') for w in s.split() if len(w.strip('.,()')) >= 4}


def grounding_fetch(name: str, region: str = ''):
    """Search Wikipedia → fetch the canonical article's lead extract.
    Returns (extract_text, source_url) or ('', None) when no usable article.
    Region is included in the query for geographic disambiguation, and a
    title-relevance guard rejects unrelated matches (e.g. 'Sataya Reef' →
    'Pterois miles') — a wrong source is worse than no source."""
    clean = name.split('(')[0].strip()
    query = f'{clean} {region}'.strip() if region else clean
    for attempt in range(3):
        try:
            r = requests.get(WIKI_API, params={
                'action': 'query', 'format': 'json', 'generator': 'search',
                'gsrsearch': query, 'gsrlimit': '1',
                'prop': 'extracts', 'exintro': '1', 'explaintext': '1', 'exchars': '2500',
            }, headers=UA, timeout=12)
            pages = r.json().get('query', {}).get('pages', {})
            if not pages:
                return ('', None)
            pg = next(iter(pages.values()))
            if pg.get('missing') is not None:
                return ('', None)
            title = pg['title']
            # Relevance guard: require >= 1 significant shared token with the POI name.
            name_tokens = _tokens(clean)
            if name_tokens and not (name_tokens & _tokens(title)):
                return ('', None)
            ext = (pg.get('extract') or '').strip()
            if len(ext) < 60:
                return ('', None)
            url = f'https://en.wikipedia.org/wiki/{title.replace(" ", "_")}'
            return (ext[:2500], url)
        except Exception:
            time.sleep(1.5 * (attempt + 1))
    return ('', None)


def tavily_fetch(name: str, region: str = ''):
    """Search Tavily → fetch top result's content as grounding source.
    Returns (extract_text, source_url) or ('', None) when no usable result.
    Used ONLY when Wikipedia fails (obscure reefs, nature reserves, hidden gems).
    Preserves the 1000-search/month quota by avoiding redundant calls."""
    if not TAVILY_API_KEY:
        return ('', None)
    clean = name.split('(')[0].strip()
    query = f'{clean} {region} Egypt tourist attraction travel guide'.strip()
    for attempt in range(2):
        try:
            r = requests.post(TAVILY_API, json={
                'api_key': TAVILY_API_KEY,
                'query': query,
                'search_depth': 'basic',
                'max_results': 1,
                'include_answer': False,
                'include_raw_content': True,
            }, timeout=15)
            r.raise_for_status()
            data = r.json()
            if not data.get('results'):
                return ('', None)
            result = data['results'][0]
            content = result.get('content', '').strip()
            if len(content) < 60:
                return ('', None)
            url = result.get('url', '')
            # Relevance guard: require at least one significant shared token
            name_tokens = _tokens(clean)
            title_tokens = _tokens(result.get('title', ''))
            if name_tokens and not (name_tokens & title_tokens):
                return ('', None)
            return (content[:2500], url)
        except Exception:
            time.sleep(2 * (attempt + 1))
    return ('', None)


# Gold-standard expert-guide prompt. Mirrors the approved Valley of the
# Kings sample: perspective opener -> context -> key facts/history -> what you
# see -> expert guidance -> nearby pairing -> source attribution. Also emits a
# short TIPS block that feeds the Flutter "Good to know" card. Output is parsed
# into (narrative, tips) via parse_narrative_tips().
PROMPT_TEMPLATE = """\
You are a senior Egyptologist and veteran Egypt-based travel guide with 20+ \
years leading discerning travelers. Write an authoritative profile of ONE site \
for a curious traveler who tapped it in an app and wants to genuinely \
understand it.

SITE: {name} ({category}, {city})
VERIFIED FACTS (use ONLY these — never invent dates, names, dimensions, prices, or species):
  Significance: {significance}
  Description: {description}
{sources}

OUTPUT FORMAT (follow EXACTLY):

NARRATIVE:
Write 300-340 words, second person ("you"), flowing prose (no headers/bullets). Structure:
1. Open with a PERSPECTIVE or framing — what kind of place this is and why it matters conceptually. Do NOT open with "Rising", "Stand", "Step", or "You" — vary openings.
2. Give CONTEXT: where it sits, what it is, its place in Egyptian history or geography.
3. Provide KEY INFORMATION a visitor should know: history, era, who built/used it, specific grounded facts (dates, names, dimensions, species, exhibits — whatever applies and is in the facts).
4. Describe WHAT YOU SEE: the defining visual/features a visitor encounters. For natural sites: notable inhabitants, special features. For museums: key exhibits, layout.
5. Weave EXPERT PRACTICAL GUIDANCE: timing, pacing, what to prioritize, a real insider tip.
6. Mention NEARBY pairings or clustering strategy when relevant.
7. Close with SOURCE ATTRIBUTION in one sentence (e.g. "UNESCO lists…", "PADI describes…", "The official site notes…", "Wikipedia notes…"), citing the grounding source.

Banned phrases: "rich history", "must-see", "hidden gem", "steeped in", "testament to", "footsteps of", "tapestry", "nestled". Be concrete over pretty.

TIPS:
Write 3-4 short, specific, actionable expert tips (one line each, each starting with "-"). Each tip must be a concrete instruction that improves the visit (timing, route, what to prioritize, what to bring, what to skip). No filler.

==="""


def make_prompt(poi: dict, sources: str) -> str:
    return PROMPT_TEMPLATE.format(
        name        = poi.get('name', ''),
        category    = poi.get('category', 'attraction'),
        city        = poi.get('city') or 'Egypt',
        significance= poi.get('historical_significance') or 'Not specified',
        description = poi.get('description') or 'Not specified',
        sources     = sources,
    )


def parse_narrative_tips(raw: str) -> tuple[str | None, list[str]]:
    """Split the model's structured response into (narrative, tips).
    Tolerant: handles missing TIPS section, extra whitespace, and tips given as
    a prose paragraph instead of a list. Never raises — on any parse issue,
    keeps the narrative (the high-value output) and returns best-effort tips."""
    if not raw:
        return (None, [])
    text = raw.strip()
    # Normalize the section markers we asked for.
    upper = text.upper()
    t_idx = upper.find('TIPS:')
    n_idx = upper.find('NARRATIVE:')
    narrative = text
    tips_block = ''
    if t_idx != -1:
        tips_block = text[t_idx + len('TIPS:'):]
        narrative = text[:t_idx]
    if n_idx != -1:
        narrative = narrative[n_idx + len('NARRATIVE:'):]
    narrative = narrative.strip()
    # Tips: lines beginning with - or *, or numbered; fall back to splitting sentences.
    tips = []
    for line in tips_block.splitlines():
        ln = line.strip().lstrip('-*').strip()
        # strip leading "N. " numbering
        if ln and ln[0].isdigit():
            ln = ln.split('.', 1)[-1].strip()
        if len(ln) >= 12:  # real tip, not stray token
            tips.append(ln)
    if not tips and tips_block.strip():
        # model wrote tips as prose — keep as a single tip if substantial
        joined = ' '.join(tips_block.split())
        if len(joined) >= 20:
            tips = [joined]
    return (narrative or None, tips[:6])  # cap at 6 for the card


def generate(client, poi: dict, sources: str) -> tuple[str | None, list[str]] | None:
    """Returns (narrative, tips) or None on total failure. Provider-agnostic:
    both Groq and OpenAI/z.ai expose chat.completions.create identically."""
    try:
        resp = client.chat.completions.create(
            model    = MODEL,
            messages = [{'role': 'user', 'content': make_prompt(poi, sources)}],
            max_tokens  = MAX_TOKENS_OUT,
            temperature = 0.75,
        )
        raw = resp.choices[0].message.content.strip()
        return parse_narrative_tips(raw)
    except Exception as e:
        # Avoid the Windows cp1252 crash on the bullet glyph by ASCII-only log.
        print(f'  [LLM error] {type(e).__name__}: {str(e)[:160]}')
        return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true',
                        help='Generate text but do not write to Supabase')
    parser.add_argument('--limit', type=int, default=0,
                        help='Cap number of POIs processed (0 = all)')
    parser.add_argument('--all', dest='all_pois', action='store_true',
                        help='Re-enrich POIs that already have a narrative')
    parser.add_argument('--tavily-only', action='store_true',
                        help='Process only POIs with no grounding (targeted re-run for Tavily fallback)')
    parser.add_argument('--to-file', metavar='PATH',
                        help='Generate narrative+tips to a JSONL review file and SKIP all DB writes '
                             '(human review gate before commit). Use with --all.')
    args = parser.parse_args()

    if not SUPABASE_URL or not SUPABASE_KEY:
        sys.exit('Missing env vars: SUPABASE_URL, SUPABASE_SECRET_KEY')
    if USE_ZAI:
        if not Z_AI_API_KEY:
            sys.exit('USE_ZAI path selected but Z_AI_API_KEY missing in .env')
    elif not GROQ_API_KEY:
        sys.exit('Missing env vars: GROQ_API_KEY (or set Z_AI_API_KEY for the z.ai path)')

    # Provider-agnostic LLM client. Groq and OpenAI both expose
    # chat.completions.create with the same signature, so generate() is unchanged.
    if USE_ZAI:
        from openai import OpenAI
        llm = OpenAI(api_key=Z_AI_API_KEY, base_url=Z_AI_BASE_URL)
        print(f'LLM provider: z.ai ({Z_AI_BASE_URL}) model={MODEL}')
    else:
        llm = Groq(api_key=GROQ_API_KEY)
        print(f'LLM provider: Groq model={MODEL}')
    supabase  = create_client(SUPABASE_URL, SUPABASE_KEY)

    q = supabase.from_('pois').select(
        'id, name, category, city, historical_significance, description'
    ).eq('is_active', True)

    if not args.all_pois and not args.tavily_only:
        q = q.is_('narrative', 'null')

    if args.tavily_only:
        # Targeted re-run: process ONLY the POIs a previous run logged as
        # ungrounded (grounding_kind == 'none') in the audit trail. This avoids
        # re-spending Groq tokens or Tavily quota on already-grounded POIs and
        # is the whole point of the flag. Reads thesis/evidence/narrative_sources.json
        # (rewritten every run). Those POIs already carry a DB-only narrative, so we
        # deliberately skip the default `narrative IS NULL` filter above.
        audit_path = Path('thesis/evidence/narrative_sources.json')
        ungrounded_ids = []
        if audit_path.exists():
            try:
                prev = json.loads(audit_path.read_text())
                ungrounded_ids = [p['id'] for p in prev.get('pois', [])
                                  if p.get('grounding_kind') == 'none']
            except Exception as e:
                print(f'⚠️  Tavily-only: could not read audit trail ({e})')
        if ungrounded_ids:
            q = q.in_('id', ungrounded_ids)
            print(f'⚠️  Tavily-only mode: targeting {len(ungrounded_ids)} '
                  f'previously-ungrounded POIs')
        else:
            print('⚠️  Tavily-only mode: no ungrounded POIs found in audit trail '
                  '(thesis/evidence/narrative_sources.json). Nothing to target.')
            return

    result = q.order('popularity_score', desc=True).execute()
    pois   = result.data

    if args.limit:
        pois = pois[:args.limit]

    total = len(pois)
    print(f'POIs to enrich : {total}')
    print(f'Est. tokens    : {total * 1200:,}  (~{total * 1200 / 100_000:.1f} Groq day quota)')
    mode = 'REVIEW-TO-FILE' if args.to_file else ('DRY RUN' if args.dry_run else 'LIVE WRITE')
    print(f'Mode           : {mode}')
    if args.to_file:
        print(f'Review file    : {args.to_file}  (no DB writes until reviewed)')
    # Load official scraped sources (highest-priority grounding). No-op pre-scrape.
    OFFICIAL_SOURCES.update(load_official_sources())
    print()

    # Per-POI worker: pure function (grounding -> generate -> optional write).
    # Returns an audit record plus per-POI counters; never mutates shared state,
    # so it is safe to run concurrently under a ThreadPoolExecutor. The Groq/
    # z.ai clients and the Supabase client are all safe for concurrent use.
    def process_poi(poi):
        # Grounding priority: (1) official scraped source, (2) Wikipedia,
        # (3) Tavily fallback, (4) none.
        official = OFFICIAL_SOURCES.get(_norm_name(poi['name']))
        if official:
            src_url = official.get('url')
            sources_str = f'OFFICIAL source ({src_url or "scraped"}):\n{official["description"]}'
            audit_src = [{'url': src_url, 'kind': 'official'}]
            grounded_kind = 'official'
        else:
            wiki_text, wiki_url = grounding_fetch(poi['name'], poi.get('city'))
            if wiki_text:
                sources_str = f'Wikipedia source:\n{wiki_text}'
                audit_src = [{'url': wiki_url, 'kind': 'wikipedia'}]
                grounded_kind = 'wikipedia'
            else:
                tavily_text, tavily_url = tavily_fetch(poi['name'], poi.get('city'))
                if tavily_text:
                    sources_str = f'Tavily search source ({tavily_url}):\n{tavily_text}'
                    audit_src = [{'url': tavily_url, 'kind': 'tavily'}]
                    grounded_kind = 'tavily'
                else:
                    sources_str = ('(No Wikipedia article found — use ONLY the DB fields '
                                   'above; keep it conservative, do not embellish.)')
                    audit_src = []
                    grounded_kind = 'none'

        out = generate(llm, poi, sources_str)
        if out is None:
            return {'idx': poi['_idx'], 'name': poi['name'], 'id': poi['id'],
                    'ok': False, 'grounded': False, 'grounding_kind': grounded_kind,
                    'sources': audit_src, 'narrative': None, 'tips': []}
        narrative, tips = out
        if not narrative:
            return {'idx': poi['_idx'], 'name': poi['name'], 'id': poi['id'],
                    'ok': False, 'grounded': False, 'grounding_kind': grounded_kind,
                    'sources': audit_src, 'narrative': None, 'tips': []}

        # Write path: review-file (no DB) < dry-run (no write) < live DB write.
        if args.to_file:
            # review record carries the generated content for human sign-off
            return {'idx': poi['_idx'], 'name': poi['name'], 'id': poi['id'],
                    'ok': True, 'grounded': grounded_kind != 'none',
                    'grounding_kind': grounded_kind, 'sources': audit_src,
                    'narrative': narrative, 'tips': tips, 'review': True,
                    'category': poi.get('category'), 'city': poi.get('city')}
        if args.dry_run:
            return {'idx': poi['_idx'], 'name': poi['name'], 'id': poi['id'],
                    'ok': True, 'grounded': grounded_kind != 'none',
                    'grounding_kind': grounded_kind, 'sources': audit_src,
                    'narrative': narrative, 'tips': tips, 'dry': True}
        # LIVE WRITE
        try:
            supabase.from_('pois').update(
                {'narrative': narrative, 'travel_tips': tips if tips else None}
            ).eq('id', poi['id']).execute()
        except Exception as e:
            return {'idx': poi['_idx'], 'name': poi['name'], 'id': poi['id'],
                    'ok': False, 'grounded': grounded_kind != 'none',
                    'grounding_kind': grounded_kind, 'sources': audit_src,
                    'narrative': None, 'tips': [], 'db_error': str(e)[:120]}
        return {'idx': poi['_idx'], 'name': poi['name'], 'id': poi['id'],
                'ok': True, 'grounded': grounded_kind != 'none',
                'grounding_kind': grounded_kind, 'sources': audit_src,
                'narrative': narrative, 'tips': tips}

    # Tag each POI with its original index so audit order is deterministic after
    # concurrent execution returns results out-of-order.
    for _i, _poi in enumerate(pois, 1):
        _poi['_idx'] = _i

    ok = fail = grounded_ct = 0
    audit = []  # thesis defensibility: trace each narrative to its sources

    # Concurrency: fan out when there are enough POIs to benefit. Review-to-file
    # and live-write both parallelize; dry-run (small/tested) stays sequential.
    parallel = (total >= 8 and not args.dry_run)
    if parallel:
        workers = int(os.getenv('ENRICH_WORKERS', '4'))
        from concurrent.futures import ThreadPoolExecutor, as_completed
        print(f'(parallel: {workers} workers)\n')
        done = 0
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futs = {ex.submit(process_poi, poi): poi for poi in pois}
            for fut in as_completed(futs):
                r = fut.result()
                done += 1
                if r['ok']:
                    ok += 1
                    if r['grounded']:
                        grounded_ct += 1
                    kind = r['grounding_kind']
                    wcount = len((r.get('narrative') or '').split())
                    print(f"[{done}/{total}] OK ({kind}, {wcount}w, {len(r.get('tips', []))} tips) — {r['name']}")
                else:
                    fail += 1
                    err = r.get('db_error', 'generate failed')
                    print(f"[{done}/{total}] FAIL — {r['name']} — {err}")
                audit.append(r)
    else:
        for poi in pois:
            print(f'[{poi["_idx"]}/{total}] {poi["name"]} ({poi.get("city", "?")})',
                  end=' … ', flush=True)
            r = process_poi(poi)
            if r['ok']:
                ok += 1
                if r['grounded']:
                    grounded_ct += 1
                wcount = len((r.get('narrative') or '').split())
                if args.dry_run:
                    print(f"OK (dry, {r['grounding_kind']}, {wcount}w)\n        {(r['narrative'] or '')[:90]}…")
                    for t in r.get('tips', []):
                        print(f'        - {t}')
                else:
                    print(f"OK ({r['grounding_kind']}, {wcount}w)")
            else:
                fail += 1
                print(r.get('db_error', 'generate failed'))
            audit.append(r)
            if poi['_idx'] < total:
                time.sleep(CALL_DELAY)

    # Preserve original POI order in the audit trail (concurrency returns OoO).
    audit.sort(key=lambda r: r['idx'])
    # In review-file mode, keep the generated narrative+tips in the review file
    # (not the audit trail). The audit trail tracks grounding only.
    if args.to_file:
        from pathlib import Path
        out_path = Path(args.to_file)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open('w', encoding='utf-8') as f:
            for r in audit:
                if r.get('ok'):
                    f.write(json.dumps({
                        'id': r['id'], 'name': r['name'],
                        'category': r.get('category'), 'city': r.get('city'),
                        'narrative': r['narrative'], 'tips': r.get('tips', []),
                        'grounding_kind': r['grounding_kind'],
                        'sources': r['sources'],
                    }, ensure_ascii=False) + '\n')
        print(f'Review file written: {out_path} ({sum(1 for r in audit if r.get("ok"))} entries)')
    for r in audit:
        r.pop('idx', None)
        r.pop('narrative', None)
        r.pop('tips', None)

    # Write source audit trail (thesis defensibility)
    from pathlib import Path
    Path('thesis/evidence').mkdir(parents=True, exist_ok=True)
    Path('thesis/evidence/narrative_sources.json').write_text(json.dumps({
        'generated_count': ok, 'grounded_count': grounded_ct,
        'grounding_rate': f'{100 * grounded_ct // max(ok, 1)}%',
        'model': MODEL, 'pois': audit,
    }, indent=2))

    print(f'\n{"─" * 50}')
    print(f'Done  ✓ {ok}   ✗ {fail}')
    print(f'Grounding: {grounded_ct}/{ok} narratives sourced (Wikipedia/Tavily/Official)')
    print('Audit trail: thesis/evidence/narrative_sources.json')
    if not args.dry_run and ok:
        print('Verify: SELECT COUNT(*) FROM pois WHERE narrative IS NOT NULL;')


if __name__ == '__main__':
    main()
