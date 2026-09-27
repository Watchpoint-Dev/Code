import sys,pathlib,re
from watchpoint.commun.utils import get
S=pathlib.Path("samples")
r=get("https://www.lempertz.com/en/search.html",params={"id":"113","tx_kesearch_pi1[sword]":"wristwatch"},pause=3.0)
t=r.text; (S/"lem_search2.html").write_text(t,encoding="utf-8")
print(r.status_code,r.url,len(t))
print("count:",re.findall(r'(\d[\d.,]*)\s*results',t,re.I)[:3])
L=sorted(set(re.findall(r'href="(/en/catalogues/lot/[^"]+)"',t)))
print("lot links:",len(L)); print(L[:6])
print("pagination:",sorted(set(re.findall(r'href="([^"]*page[^"]*)"',t)))[:8])
