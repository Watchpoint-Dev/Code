import sys,pathlib,re
from watchpoint.commun.utils import get
S=pathlib.Path("samples")
for name,u in [("lem_lot_1274_296.html","https://www.lempertz.com/en/catalogues/lot/1274-1/296-a-steel-automatic-rolex-datejust-wristwatch.html"),
               ("lem_search_wristwatch.html","https://www.lempertz.com/en/search.html?q=wristwatch")]:
    r=get(u,pause=3.0); t=r.text
    (S/name).write_text(t,encoding="utf-8")
    print(name,r.status_code,r.url,len(t))
    for kw in ["Result","Ergebnis","EUR","Estimate","Schätzpreis","hammer","sold"]:
        print("   ",kw,t.count(kw))
