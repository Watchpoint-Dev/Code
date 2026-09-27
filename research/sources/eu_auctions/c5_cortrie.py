import sys,pathlib,re
from watchpoint.commun.utils import get
S=pathlib.Path("samples")
for auk,los in [("93","4100"),("93","4200")]:
    u=f"https://www.cortrie.de/uhren/armbanduhren/detail/{auk}/{los}/"
    r=get(u,pause=3.0); t=r.text
    (S/f"cortrie_detail_{auk}_{los}.html").write_text(t,encoding="utf-8")
    lots=re.findall(r'id="lot_(\d+)-(\d+)"',t)
    zu=re.findall(r'Zuschlag:\s*([\d.,]+)\s*&euro;<br>\s*<small>([^<]+)</small>',t)
    tit=re.findall(r'<span class="los-titel" itemprop="name">([^<]{0,90})',t)
    print(auk,los,r.status_code,len(t),"| lots",len(lots),"| prix",len(zu),zu[:4])
    print("   titres:",tit[:3])
