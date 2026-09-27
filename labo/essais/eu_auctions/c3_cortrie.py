import sys,pathlib,re
sys.path.append("/Users/vale/Desktop/WP/labo/shared")
from utils import get
S=pathlib.Path("samples")
for name,u in [("cortrie_detail_177_4194.html","https://www.cortrie.de/uhren/armbanduhren/detail/177/4194/"),
               ("cortrie_sitemap.xml","https://www.cortrie.de/sitemap.xml")]:
    r=get(u,pause=3.0)
    print(name,r.status_code,r.url,len(r.text),r.headers.get("content-type"))
    (S/name).write_text(r.text,encoding="utf-8")
    print("   Zuschlag:",r.text.count("Zuschlag"),"| head:",r.text[:150].replace("\n"," "))
