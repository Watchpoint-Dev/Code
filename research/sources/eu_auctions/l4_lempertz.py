import sys,pathlib,re,collections
from watchpoint.commun.utils import get
S=pathlib.Path("samples")
for i in (17,):
    r=get(f"https://www.lempertz.com/sitemap/sitemap-en-lots-{i}.xml",pause=3.0)
    t=r.text; (S/f"lempertz_lots{i}.xml").write_text(t,encoding="utf-8")
    locs=re.findall(r'<loc>([^<]+)</loc>',t)
    cats=[int(m.group(1)) for l in locs if (m:=re.search(r'/lot/(\d+)-',l))]
    w=[l for l in locs if re.search(r'-(wristwatch|watch|chronograph|rolex|omega|patek)',l)]
    print(i,r.status_code,"locs",len(locs),"catmin",min(cats),"catmax",max(cats),"distinct",len(set(cats)),"watchish",len(w))
    print("  ex watch:",w[:4])
