import sys,pathlib,re,json
from watchpoint.commun.utils import get
S=pathlib.Path("samples")
t=(S/"lempertz_lots17.xml").read_text()
locs=re.findall(r'<loc>([^<]+)</loc>',t)
old=[l for l in locs if "/lot/822-" in l]
print("cat822 lots:",len(old)); print(old[:3])
u=old[0]
r=get(u,pause=3.0); h=r.text
(S/"lem_lot_822.html").write_text(h,encoding="utf-8")
print(r.status_code,len(h))
m=re.search(r'<div class="lot-prices">(.*?)</div>\s*</div>',h,re.S)
print("PRICES:",re.sub(r'\s+',' ',m.group(1))[:400] if m else "none")
print("DESC META:",re.search(r'name="description" content="([^"]*)"',h).group(1)[:200])
print("countdown:",re.findall(r'data-start="\s*([^"]*)"',h)[:3])
print("auction date-ish:",re.findall(r'\b(\d{1,2}\s+\w+\s+20\d\d|\d{2}\.\d{2}\.\d{4}|20\d\d-\d\d-\d\d)\b',h)[:12])
for mm in re.finditer(r'application/ld\+json[^>]*>(.*?)</script>',h,re.S):
    print("LD:",re.sub(r'\s+',' ',mm.group(1))[:600])
