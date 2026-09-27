import sys, re, json, pathlib
from watchpoint.commun.utils import get
from bs4 import BeautifulSoup

URLS = {
  "results": "https://www.christies.com/en/results",
  "lot": "https://www.christies.com/lot/lot-6591601",
}
for name, url in URLS.items():
    print(f"\n===== {name}: {url} =====")
    try:
        r = get(url, pause=1)
    except Exception as e:
        print("  ERREUR requete:", e); continue
    print(f"  HTTP {r.status_code} | {len(r.text):,} chars | server={r.headers.get('server')}")
    if r.status_code != 200:
        print("  -> non-200 (blocage probable). extrait:", r.text[:160].replace('\n',' ')); continue
    soup = BeautifulSoup(r.text, "lxml")
    print("  title:", (soup.title.string if soup.title else None))
    for m in ["__NEXT_DATA__","__NUXT__","__APOLLO","application/ld+json","/api/","graphql","algolia","dataLayer","react","angular"]:
        if m.lower() in r.text.lower(): print("   marker:", m)
    ld = soup.find_all("script", type="application/ld+json")
    print("  json-ld blocks:", len(ld))
    for i,t in enumerate(ld[:4]):
        try:
            d = json.loads(t.string or "{}")
            typ = d.get("@type") if isinstance(d,dict) else type(d).__name__
            print(f"    ld[{i}] @type={typ} keys={list(d)[:10] if isinstance(d,dict) else ''}")
        except Exception as e: print("    ld err", e)
    for sel in ["[class*=lot]","article","[class*=result]","[class*=card]"]:
        print(f"  sel {sel}: {len(soup.select(sel))}")
