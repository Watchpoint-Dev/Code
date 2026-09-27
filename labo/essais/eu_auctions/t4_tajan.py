import sys,pathlib,re
sys.path.append("/Users/vale/Desktop/WP/labo/shared")
from utils import get
S=pathlib.Path("samples")
for name,u in [("tajan_catalog_watches.html","https://www.tajan.com/auction-catalog/watches_U3889ZEC0L?pageNum=1"),
               ("tajan_past.html","https://www.tajan.com/fr/past/")]:
    r=get(u,pause=3.0); t=r.text; (S/name).write_text(t,encoding="utf-8")
    print(name,r.status_code,r.url,len(t),r.headers.get("server"))
    for kw in ["Sold","Estimate","EUR","€","lot-","Adjug","Price Realized","Realized"]:
        print("   ",kw,t.count(kw))
    print("   sample links:",sorted(set(re.findall(r'href="([^"]*(?:auction-lot|auction-catalog)[^"]*)"',t)))[:5])
