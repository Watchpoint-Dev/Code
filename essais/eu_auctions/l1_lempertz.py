import sys,pathlib,re
sys.path.append("/Users/vale/Desktop/WP/labo/shared")
from utils import get
S=pathlib.Path("samples")
r=get("https://www.lempertz.com/sitemap/sitemap-en-lots-0.xml",pause=3.0)
t=r.text; (S/"lempertz_lots0.xml").write_text(t,encoding="utf-8")
locs=re.findall(r'<loc>([^<]+)</loc>',t)
print("lots0:",r.status_code,len(t),"locs:",len(locs))
print(locs[:5]); print(locs[-3:])
