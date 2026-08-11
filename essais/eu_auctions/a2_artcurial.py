import sys,json,pathlib
sys.path.append("/Users/vale/Desktop/WP/labo/shared")
from utils import get
S=pathlib.Path("samples")
B="https://www.artcurial.com/ace"
import json as J
sales=J.loads((S/"ac_sales_watches.json").read_text())["content"]
# pick a 2016 and the newest
import re
pick=[s for s in sales if (s.get("effectiveDate") or "").startswith("2016")][:1]+[sales[0]]
for s in pick:
    ref=s["ref"]
    r=get(f"{B}/sales/{ref}/items?page=0&size=300",pause=2.5)
    print(ref,s.get("effectiveDate"),s.get("totalLots"),r.status_code,len(r.text))
    (S/f"ac_items_{ref}.json").write_text(r.text,encoding="utf-8")
