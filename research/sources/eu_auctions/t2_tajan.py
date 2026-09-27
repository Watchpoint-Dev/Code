import sys,pathlib,re
from watchpoint.commun.utils import get
S=pathlib.Path("samples")
for name,u in [("tajan_product_sitemap.xml","https://www.tajan.com/product-sitemap.xml"),
               ("tajan_hksn_sitemap.xml","https://www.tajan.com/hksn-preview-sale-sitemap.xml")]:
    r=get(u,pause=3.0); t=r.text; (S/name).write_text(t,encoding="utf-8")
    L=re.findall(r'<loc>([^<]+)</loc>',t)
    print(name,r.status_code,len(t),"locs",len(L))
    print("  ",L[:5]); print("  ...",L[-3:])
