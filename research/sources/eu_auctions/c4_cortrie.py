import sys,pathlib,re,collections
from watchpoint.commun.utils import get
S=pathlib.Path("samples")
for name,u in [("cortrie_ab_search_rolex.html","https://www.cortrie.de/uhren/armbanduhren/search?q=Rolex"),
               ("cortrie_ab_start24.html","https://www.cortrie.de/uhren/armbanduhren/?start=24")]:
    r=get(u,pause=3.0); t=r.text
    (S/name).write_text(t,encoding="utf-8")
    lots=re.findall(r'id="lot_(\d+)-(\d+)"',t)
    print(name,r.status_code,len(t),"| lots:",len(lots),"| auctions:",dict(collections.Counter(a for a,b in lots)))
    print("   H2:",re.findall(r'<h2>\s*([^<]{0,60})',t)[:3])
    print("   pag:",sorted(set(re.findall(r'href="([^"]*start=\d+)"',t)))[:12])
