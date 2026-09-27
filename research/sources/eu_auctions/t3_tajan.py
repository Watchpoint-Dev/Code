import sys,pathlib,re
from watchpoint.commun.utils import get
S=pathlib.Path("samples")
for name,u in [("tajan_auction_3221.html","https://www.tajan.com/fr/auction/3221-montres/"),
               ("tajan_auction_montres1439.html","https://www.tajan.com/fr/auction/montres-1439/")]:
    r=get(u,pause=3.0); t=r.text; (S/name).write_text(t,encoding="utf-8")
    print(name,r.status_code,r.url,len(t))
    for kw in ["Adjug","adjudic","Estimation","Lot ","€","Résultat","result","Vendu"]:
        print("   ",kw,t.count(kw))
    print("   lot links:",sorted(set(re.findall(r'href="([^"]*/lot/[^"]*)"',t)))[:4])
