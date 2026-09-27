import sys,pathlib,re,collections
sys.path.append("/Users/vale/Desktop/WP/labo/shared")
from utils import get
S=pathlib.Path("samples")
r=get("https://www.tajan.com/auction-catalog/watches_1HGIP4UDXZ?pageNum=1",pause=3.0); t=r.text
(S/"tajan_catalog_watches_old.html").write_text(t,encoding="utf-8")
print(r.status_code,r.url,len(t))
print("date:",re.findall(r'class="date dateTime[^"]*">\s*([^<]+)',t)[:2])
print("lots:",re.findall(r'<h2 class="inline-block[^"]*">\s*([\d,]+)',t)[:2])
res=[float(x) for x in re.findall(r'&quot;priceResult&quot;:([\-\d.]+)',t)]
print("priceResult n",len(res),"sold",sum(1 for x in res if x>0),"sample",res[:10])
print("titles:",re.findall(r'&quot;title&quot;:&quot;([^&]{0,35})',t)[7:15])
print("cur:",collections.Counter(re.findall(r'&quot;currency&quot;:&quot;(\w+)&quot;',t)))
print("lotNumber:",re.findall(r'&quot;lotNumber&quot;:&quot;?([^,&]{1,6})',t)[:8])
