import sys,pathlib,re
sys.path.append("/Users/vale/Desktop/WP/labo/shared")
from utils import get
S=pathlib.Path("samples")
for name,u in [("lem_saleresults.html","https://www.lempertz.com/en/auctions/sale-results.html"),
               ("lem_catalogues.xml","https://www.lempertz.com/sitemap/sitemap-en-catalogues-0.xml")]:
    r=get(u,pause=3.0); t=r.text
    (S/name).write_text(t,encoding="utf-8")
    print(name,r.status_code,r.url,len(t))
    print("   lot links:",len(set(re.findall(r'/catalogues/lot/[^"\']+',t))),"| locs:",len(re.findall(r'<loc>',t)))
    if "xml" in name:
        L=re.findall(r'<loc>([^<]+)</loc>',t); print("   first",L[:3]); print("   last",L[-3:])
    else:
        print("   forms:",re.findall(r'<form[^>]*action="([^"]*)"',t)[:5])
        print("   selects:",re.findall(r'<select[^>]*name="([^"]+)"',t)[:10])
        print("   inputs:",re.findall(r'<input[^>]*name="([^"]+)"',t)[:15])
