import sys,pathlib,re
from watchpoint.commun.utils import get
S=pathlib.Path("samples")
r=get("https://www.tajan.com/fr/sitemap_index.xml",pause=3.0)
t=r.text; (S/"tajan_sitemapindex.xml").write_text(t,encoding="utf-8")
print(r.status_code,r.url,len(t),r.headers.get("content-type"))
print(re.findall(r'<loc>([^<]+)</loc>',t))
