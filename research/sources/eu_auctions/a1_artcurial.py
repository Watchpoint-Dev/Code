import sys,json,pathlib
from watchpoint.commun.utils import get
S=pathlib.Path("samples")
B="https://www.artcurial.com/ace"
def go(name,url,**kw):
    r=get(url,pause=2.5,**kw)
    print(name,r.status_code,r.headers.get("content-type"),len(r.text))
    (S/name).write_text(r.text,encoding="utf-8")
    try: return r.json()
    except Exception: print("   NOT JSON:",r.text[:200]); return None
d=go("ac_sales_watches.json", B+"/sales/results?filter=specialties.specialty.ref,MTCA,WATCHES&page=0&size=500&sort=effectiveDate,desc")
if d: print("  totalElements",d.get("totalElements"),"n",len(d.get("content",[])))
d2=go("ac_items_1424.json", B+"/sales/1424/items?page=0&size=200")
if d2: print("  1424 totalElements",d2.get("totalElements"),"n",len(d2.get("content",[])))
