import sys, re, pathlib
sys.path.append(str(next(p for p in pathlib.Path(__file__).resolve().parents if (p/"shared"/"utils.py").exists())/"shared"))
from utils import get
from bs4 import BeautifulSoup

BASE = "https://www.barnebys.com/realized-prices/watches-and-clocks?h=Christie%27s"
# total count in the page?
html = (pathlib.Path(__file__).parent/"samples"/"realized_christies.html").read_text(encoding="utf-8")
for pat in [r'([\d,]+)\s+results', r'([\d,]+)\s+lots', r'"total"\s*:\s*(\d+)', r'of\s+([\d,]+)']:
    m = re.findall(pat, html, re.I)
    if m: print("count-like:", pat, "->", m[:5])

# test pagination param ?page=2
for page in [2, 3]:
    u = f"{BASE}&page={page}"
    r = get(u, pause=1)
    n = len(BeautifulSoup(r.text,"lxml").find_all("article"))
    first = BeautifulSoup(r.text,"lxml").find("article")
    ft = re.sub(r'\s+',' ',first.get_text(' ',strip=True))[:60] if first else "-"
    print(f"page={page}: HTTP {r.status_code}, articles={n}, 1st={ft!r}")
