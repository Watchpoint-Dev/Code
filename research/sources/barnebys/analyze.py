import sys, re, json, pathlib
from watchpoint.commun.utils import get, samples_dir, save_text
from bs4 import BeautifulSoup

URL = "https://www.barnebys.com/realized-prices/watches-and-clocks?h=Christie%27s"
print(f"GET {URL}")
r = get(URL, pause=0)
print(f"  HTTP {r.status_code} | {len(r.text):,} chars | ctype={r.headers.get('content-type')}")
print(f"  server={r.headers.get('server')} | via/cf={r.headers.get('cf-ray','-')}")

s = samples_dir(__file__); save_text(s/"realized_christies.html", r.text)
soup = BeautifulSoup(r.text, "lxml")
print("  title:", (soup.title.string if soup.title else None))

txt = r.text
# framework / data delivery markers
for m in ["__NEXT_DATA__","__NUXT__","__INITIAL_STATE__","window.__APOLLO","algolia","Algolia",
          "graphql","/api/","application/ld+json","react","svelte","data-reactroot"]:
    if m.lower() in txt.lower():
        print("  MARKER:", m)

# json-ld
ld = soup.find_all("script", type="application/ld+json")
print("  json-ld blocks:", len(ld))
for i,t in enumerate(ld[:3]):
    try:
        d = json.loads(t.string or "{}")
        print(f"    ld[{i}] type={d.get('@type')} keys={list(d)[:8]}")
    except Exception as e:
        print("    ld parse err", e)

# find API-ish URLs referenced in the HTML/JS
apis = sorted(set(re.findall(r'https?://[a-zA-Z0-9._/-]*(?:api|algolia|graphql|search)[a-zA-Z0-9._/?=&-]*', txt)))[:15]
print("  API-like urls found:", len(apis))
for a in apis: print("    ", a[:120])

# count listing-ish nodes
for sel in ["[class*=lot]","[class*=item]","[class*=card]","article","[data-testid]"]:
    print(f"  sel {sel}: {len(soup.select(sel))}")
