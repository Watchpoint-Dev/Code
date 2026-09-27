import sys,pathlib,re
sys.path.append("/Users/vale/Desktop/WP/labo/shared")
from utils import get
S=pathlib.Path("samples")
for name,u in [("cortrie_auktionen.html","https://www.cortrie.de/auktionen/"),
               ("cortrie_armbanduhren.html","https://www.cortrie.de/uhren/armbanduhren/")]:
    r=get(u,pause=2.5)
    print(name,r.status_code,r.url,len(r.text),r.headers.get("server"))
    (S/name).write_text(r.text,encoding="utf-8")
    hs=sorted(set(re.findall(r'href="([^"]+)"',r.text)))
    print("  links sample:",[h for h in hs if any(k in h.lower() for k in["auktion","ergebn","archiv","detail","result","zuschlag","seite","page"])][:40])
