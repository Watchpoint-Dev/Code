import sys,pathlib,re
from watchpoint.commun.utils import get
S=pathlib.Path("samples")
for name,u in [("cortrie_search_rolex.html","https://www.cortrie.de/uhren/search?q=Rolex"),
               ("cortrie_search_rolex_p2.html","https://www.cortrie.de/uhren/search?q=Rolex&start=100")]:
    r=get(u,pause=3.0)
    txt=r.text
    print(name,r.status_code,r.url,len(txt))
    (S/name).write_text(txt,encoding="utf-8")
    print("  Zuschlag:",txt.count("Zuschlag"),"| los-nummer:",txt.count("los-nummer"),"| Treffer:",re.findall(r'[\d.]+\s*(?:Treffer|Ergebnis\w*)',txt)[:3])
    print("  pag:",sorted(set(re.findall(r'href="([^"]*(?:start|page|seite)=[^"]*)"',txt)))[:12])
