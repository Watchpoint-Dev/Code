import sys, re, json, pathlib
from bs4 import BeautifulSoup
html = (pathlib.Path(__file__).parent/"samples"/"realized_christies.html").read_text(encoding="utf-8")
soup = BeautifulSoup(html, "lxml")

# 1) all /api/ paths mentioned
paths = sorted(set(re.findall(r'["\'](/api/[^"\']+)["\']', html)))[:25]
print("== /api/ paths ==", len(paths))
for p in paths: print("  ", p[:140])

# 2) big JSON script blobs
print("\n== script blobs with JSON ==")
for sc in soup.find_all("script"):
    t = sc.string or ""
    if len(t) > 500 and (t.strip().startswith("{") or "realized" in t.lower() or "hits" in t.lower()):
        print(f"  script len={len(t)} start={t.strip()[:80]!r}")

# 3) inspect first 2 articles for fields
print("\n== sample article structure ==")
for art in soup.find_all("article")[:2]:
    print("  --- article ---")
    print("   text:", re.sub(r'\s+',' ', art.get_text(' ', strip=True))[:220])
    a = art.find("a", href=True)
    if a: print("   link:", a['href'][:120])
    img = art.find("img")
    if img: print("   img:", (img.get('src') or img.get('data-src') or '')[:90])
