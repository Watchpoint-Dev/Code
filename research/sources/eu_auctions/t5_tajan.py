import sys,pathlib,re
from watchpoint.commun.utils import get
S=pathlib.Path("samples")
r=get("https://www.tajan.com/fr/auction/montres-142/",pause=3.0); t=r.text
(S/"tajan_auction_montres142.html").write_text(t,encoding="utf-8")
print(r.status_code,r.url,len(t))
print("TITLE:",re.search(r'<title>(.*?)</title>',t,re.S).group(1)[:120])
cat=sorted(set(re.findall(r'https://www\.tajan\.com/auction-catalog/[^"?]+',t)))
print("CATALOG:",cat)
print("dates:",sorted(set(re.findall(r'\b\d{1,2}\s+\w+\s+20\d\d\b',t)))[:6], re.findall(r'20\d\d-\d\d-\d\d',t)[:6])
