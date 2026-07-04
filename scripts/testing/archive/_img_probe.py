import sys; sys.path.insert(0,'.')
from dotenv import load_dotenv
load_dotenv('.env')
from src.database.supabase_client import SupabaseClient
import requests, time
sb=SupabaseClient()
for name_pat in ['%Egyptian Museum%','%Khan el-Khalili%']:
    r=sb.client.table('pois').select('name,image_urls').ilike('name',name_pat).limit(1).execute()
    if not r.data: 
        print(f'NO DATA for {name_pat}'); continue
    p=r.data[0]
    urls=p.get('image_urls') or []
    print(f'\n=== {p["name"]}: {len(urls)} image URLs ===')
    for u in urls[:3]:
        try:
            t0=time.time()
            resp=requests.head(u, timeout=8, headers={'User-Agent':'VOYO-App/1.0 (Egypt travel guide; thesis project)'})
            print(f'  HTTP {resp.status_code} ({time.time()-t0:.2f}s): {u[:100]}')
        except Exception as e:
            print(f'  FAIL {type(e).__name__}: {u[:100]}')
