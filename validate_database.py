"""Comprehensive validation of the rebuilt database."""
import os, re
from dotenv import load_dotenv
load_dotenv()
import requests

url = os.environ['SUPABASE_URL']; key = os.environ['SUPABASE_SERVICE_KEY']
hdr = {'apikey': key, 'Authorization': f'Bearer {key}'}

def get(path):
    for i in range(4):
        try:
            r = requests.get(f"{url}/rest/v1/{path}", headers=hdr, timeout=30)
            if r.status_code == 200: return r.json()
        except Exception: pass
    return None

pois = get("pois?select=*&is_active=eq.true&order=id&limit=2000")
print("=" * 60)
print("VALIDATION REPORT — active POIs")
print("=" * 60)
print(f"Total active: {len(pois)}")

# 1. Duplicates
def norm(s): return re.sub(r'[^a-z0-9 ]', '', s.lower()).strip()
nm = {}; dups = []
for p in pois:
    k = norm(p['name'])
    if k in nm: dups.append((p['name'], p['id'], nm[k]))
    else: nm[k] = p['id']
print(f"\n[1] DUPLICATES: {len(dups)}")
for d in dups: print(f"    id={d[1]} '{d[0]}' ~= id={d[2]}")

# 2. Field completeness
fields = ['image_urls','historical_significance','opening_hours','ticket_price','website_url',
          'average_rating','total_reviews','tags','latitude','longitude','description']
print(f"\n[2] FIELD COMPLETENESS ({len(pois)} active POIs):")
allgood = True
for f in fields:
    present = sum(1 for p in pois if p.get(f) not in (None, '', [], {}))
    pct = 100*present//len(pois)
    flag = ' OK' if pct >= 70 else ' <<LOW'
    print(f"    {f:24} {present:4}/{len(pois)} ({pct}%){flag}")
    if pct < 70: allgood = False

# 3. image_urls format — must be flat list, permanent URLs
img_list = sum(1 for p in pois if isinstance(p.get('image_urls'), list))
img_wiki = sum(1 for p in pois if isinstance(p.get('image_urls'), list) and p['image_urls'] and 'upload.wikimedia.org' in str(p['image_urls'][0]))
img_dict = sum(1 for p in pois if isinstance(p.get('image_urls'), dict))  # old broken format
print(f"\n[3] IMAGE FORMAT:")
print(f"    flat list (correct):     {img_list}/{len(pois)}")
print(f"    wikimedia permanent URL: {img_wiki}/{len(pois)}")
print(f"    dict wrapper (OLD BUG):  {img_dict}/{len(pois)}  {'OK' if img_dict==0 else '<<< STILL BROKEN'}")

# 4. tags format — must be flat list
tag_list = sum(1 for p in pois if isinstance(p.get('tags'), list))
tag_dict = sum(1 for p in pois if isinstance(p.get('tags'), dict))
print(f"\n[4] TAGS FORMAT:")
print(f"    flat list (correct):     {tag_list}/{len(pois)}")
print(f"    dict wrapper (OLD BUG):  {tag_dict}/{len(pois)}  {'OK' if tag_dict==0 else '<<< STILL BROKEN'}")

# 5. total_reviews sanity — should be real (not capped at 5)
trs = [p['total_reviews'] for p in pois if p.get('total_reviews')]
capped5 = sum(1 for t in trs if t == 5)
print(f"\n[5] REVIEW COUNTS:")
print(f"    POIs with reviews: {len(trs)} | min={min(trs)} max={max(trs)}")
print(f"    count==5 (old bug): {capped5}  {'OK' if capped5==0 else '<<< some still capped'}")

# 6. category enum validity
valid_cats = {'historical','cultural','religious','natural','entertainment','shopping','dining','accommodation','transportation','services'}
bad_cats = [(p['name'], p.get('category')) for p in pois if p.get('category') not in valid_cats]
print(f"\n[6] CATEGORY ENUM: {len(bad_cats)} invalid  {'OK' if not bad_cats else bad_cats[:5]}")

# 7. the 6 popular POIs that had NO images before — do they have them now?
print(f"\n[7] THE FAMOUS 6 (had no images before rebuild):")
for target in ['Great Pyramid','Karnak','Great Sphinx','Valley of the Kings','Egyptian Museum','Abu Simbel']:
    match = [p for p in pois if target.lower() in p['name'].lower()]
    if match:
        p = match[0]
        has_img = isinstance(p.get('image_urls'), list) and bool(p['image_urls'])
        print(f"    {'OK ' if has_img else 'NO '} {p['name']:32} reviews={p['total_reviews']:6} img={'Y' if has_img else 'N'}")

# 8. by region
print(f"\n[8] BY REGION:")
rid = {1:'Cairo',2:'Giza',3:'Alexandria',4:'Luxor',5:'Aswan',6:'Hurghada',7:'Marsa Alam',8:'Sinai'}
from collections import Counter
rc = Counter(p.get('region_id') for p in pois)
for i in sorted(rc): print(f"    {rid.get(i,'?'):14} {rc[i]}")

print("\n" + "=" * 60)
print("SUMMARY: " + ("PASS - database is clean and complete" if (not dups and img_dict==0 and tag_dict==0 and not bad_cats and allgood) else "ATTENTION NEEDED - see above"))
