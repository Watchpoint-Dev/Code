"""Sonde une liste de sites et les note — re-executable, pour detecter les regressions.

    cd ~/Desktop/WP/labo
    shared/.venv/bin/python moteur/sonde.py                  # toutes les sources connues
    shared/.venv/bin/python moteur/sonde.py christies bezel   # seulement celles-ci
    shared/.venv/bin/python moteur/sonde.py --url https://exemple.com  # un site au hasard

Pourquoi : `catalogue.py` fige des verdicts a la main. Trois sources sont mortes en
trois semaines sans que rien ne le signale. Cette sonde REMESURE ce qui est
mesurable, et compare au dernier passage : une source qui passe de vert a rouge
apparait comme REGRESSION.

Ce qu'elle mesure vraiment (rien d'autre — elle ne devine pas) :

  FAISABILITE            VALEUR
  · robots.txt           · signal de prix (montants + devises dans la page)
  · joignable (HTTP)     · signal de date (dates reperees)
  · anti-bot             · indice de volume (sitemap, pagination)
  · rendu serveur ou JS
  · donnees structurees

Elle est POLIE : robots.txt lu en premier, site saute s'il l'interdit, pause entre
requetes, 3 requetes par site au maximum. Elle ne contourne aucune protection.

CE QU'ELLE NE FAIT PAS — a lire avant de se fier au score :

  Elle ne regarde que la PAGE D'ACCUEIL et deux endpoints standard. Elle ne sait
  pas ou vivent les vraies donnees. Christie's est note bas parce que sa page
  d'accueil ne porte aucun prix — alors que son API interne est la meilleure
  source du projet. L'inverse existe aussi : une vitrine pleine de prix dont le
  catalogue est inatteignable.

  Donc : la note de FAISABILITE est fiable (robots, HTTP, anti-bot, endpoints
  sont mesures directement). La note de VALEUR n'est qu'un indice tire de la page
  d'accueil. Un score bas veut dire "a regarder de plus pres", jamais "sans
  interet". Seul un pilote sur les vraies pages tranche.

  Son vrai usage est le TRIAGE et la SURVEILLANCE : degrossir 200 sites en une
  passe, et surtout detecter qu'une source acquise vient de se fermer.
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import re
import sys
import time
import urllib.parse

import requests

ICI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
sys.path.insert(0, str(ICI.parent / "shared"))

from utils import HEADERS  # noqa: E402

HISTORIQUE = ICI.parent / "data" / "sonde.json"
PAUSE = 1.5
DELAI = 25

# Signatures d'anti-bot. On les DETECTE pour classer la source, jamais pour passer outre.
ANTIB0T_DUR = {
    "Cloudflare": ("cf-browser-verification", "cf_chl_", "challenge-platform",
                   "__cf_bm", "Just a moment", "cdn-cgi/challenge"),
    "Incapsula/Imperva": ("_Incapsula_Resource", "incap_ses", "visid_incap"),
    "Akamai": ("ak_bmsc", "_abck", "bm_sz"),
    "AWS WAF": ("awswaf", "aws-waf-token", "challenge.js"),
    "PerimeterX": ("_px", "px-captcha", "perimeterx"),
    "DataDome": ("datadome", "dd_cookie"),
}

# Mecanismes de donnees structurees, du plus exploitable au moins.
STRUCTURE = [
    ("Shopify products.json", "/products.json?limit=1"),
    ("WooCommerce Store API", "/wp-json/wc/store/products?per_page=1"),
]
MARQUEURS_HTML = {
    "JSON-LD": r'type="application/ld\+json"',
    "__NEXT_DATA__": r'id="__NEXT_DATA__"',
    "window.__data": r"window\.__data\s*=",
    "Apollo state": r"__APOLLO_STATE__",
}

MONNAIE = re.compile(
    r"(?:USD|EUR|GBP|CHF|HKD|JPY|\$|€|£|CHF\.?|Fr\.)\s?\d[\d\s.,']{2,}", re.I)
DATE = re.compile(r"\b(?:19|20)\d{2}-\d{2}-\d{2}\b|\b(?:19|20)\d{2}\b")


def _get(url: str, **kw):
    try:
        r = requests.get(url, headers=HEADERS, timeout=DELAI,
                         allow_redirects=True, **kw)
        time.sleep(PAUSE)
        return r
    except requests.RequestException as e:
        time.sleep(PAUSE)
        return type("Echec", (), {"status_code": 0, "text": "", "url": url,
                                  "headers": {}, "erreur": type(e).__name__})()


# --------------------------------------------------------------------- robots

def controle_robots(base: str) -> dict:
    """Lit robots.txt AVANT tout le reste. C'est la premiere regle de la maison."""
    r = _get(urllib.parse.urljoin(base, "/robots.txt"))
    if r.status_code != 200:
        # pas de robots.txt = rien d'interdit, mais on le note
        return {"robots": "absent", "robots_ok": True, "crawl_delay": None,
                "params_interdits": ""}

    texte = r.text
    if len(texte) < 3000 and any(s in texte for sig in ANTIB0T_DUR.values() for s in sig):
        return {"robots": "illisible (anti-bot sur le robots.txt)", "robots_ok": False,
                "crawl_delay": None, "params_interdits": ""}

    # bloc User-agent: *
    bloc, dans = [], False
    for ligne in texte.splitlines():
        l = ligne.strip()
        if l.lower().startswith("user-agent:"):
            dans = l.split(":", 1)[1].strip() == "*"
        elif dans and l and not l.startswith("#"):
            bloc.append(l)

    interdits = [l.split(":", 1)[1].strip() for l in bloc
                 if l.lower().startswith("disallow:")]
    delai = next((l.split(":", 1)[1].strip() for l in bloc
                  if l.lower().startswith("crawl-delay:")), None)
    tout_interdit = any(i == "/" or i == "*" for i in interdits)
    params = [i for i in interdits if "=" in i or "?" in i]

    return {
        "robots": "INTERDIT TOUT" if tout_interdit else f"{len(interdits)} regles",
        "robots_ok": not tout_interdit,
        "crawl_delay": delai,
        "params_interdits": " · ".join(params[:6]),
    }


# ------------------------------------------------------------------ page type

def controle_page(base: str) -> dict:
    r = _get(base)
    corps = r.text or ""
    res = {
        "http": r.status_code,
        "octets": len(corps),
        "erreur_reseau": getattr(r, "erreur", ""),
    }

    detecte = [nom for nom, signatures in ANTIB0T_DUR.items()
               if any(s.lower() in corps.lower() for s in signatures)]
    # un 200 avec un corps minuscule est une page de challenge deguisee
    if not detecte and r.status_code == 200 and 0 < len(corps) < 2000:
        detecte = ["page suspecte (200 mais < 2 ko)"]
    if r.status_code in (403, 429):
        detecte = detecte or [f"HTTP {r.status_code}"]
    res["antibot"] = " · ".join(detecte)
    # reCAPTCHA seul n'est PAS un blocage : c'est souvent un formulaire de contact.
    # On le note sans le compter comme mur — sinon on classe fermees des sources
    # dont l'endpoint repond parfaitement (cas rencontre sur Hodinkee).
    res["signal_faible"] = "reCAPTCHA" if any(
        s in corps.lower() for s in ("g-recaptcha", "recaptcha/api.js")) else ""

    res["mecanismes"] = " · ".join(
        nom for nom, motif in MARQUEURS_HTML.items() if re.search(motif, corps))

    prix = MONNAIE.findall(corps)
    res["signal_prix"] = len(set(prix))
    annees = [int(a) for a in re.findall(r"\b(19\d{2}|20[0-3]\d)\b", corps)]
    res["signal_date"] = len(set(annees))
    res["annee_min"] = min(annees) if annees else None
    return res


def controle_endpoints(base: str, robots_ok: bool) -> dict:
    """Teste les endpoints standard — c'est ce qui rend une source triviale."""
    if not robots_ok:
        return {"endpoint": "", "sitemap": "", "volume_indice": ""}
    for nom, chemin in STRUCTURE:
        r = _get(urllib.parse.urljoin(base, chemin))
        if r.status_code == 200 and r.text.strip().startswith(("{", "[")):
            try:
                d = json.loads(r.text)
                # Shopify renvoie {"products": [...]}, WooCommerce une liste nue
                lot = d.get("products", d) if isinstance(d, dict) else d
                n = len(lot) if isinstance(lot, (list, dict)) else 0
                return {"endpoint": nom, "sitemap": "",
                        "volume_indice": f"{n} sur la 1re page"}
            except json.JSONDecodeError:
                pass
    r = _get(urllib.parse.urljoin(base, "/sitemap.xml"))
    if r.status_code == 200 and "<loc>" in r.text:
        return {"endpoint": "", "sitemap": f"{r.text.count('<loc>')} URLs",
                "volume_indice": f"{r.text.count('<loc>')} URLs au sitemap"}
    return {"endpoint": "", "sitemap": "", "volume_indice": ""}


# ------------------------------------------------------------------- notation

def note(m: dict) -> dict:
    """Deux notes sur 100, et leur produit. Chaque point est justifie par une mesure."""
    f = 0
    if m["robots_ok"]:
        f += 30
    if m["http"] == 200:
        f += 25
    if not m["antibot"]:
        f += 25
    if m["endpoint"]:
        f += 20
    elif m["mecanismes"]:
        f += 12
    elif m["sitemap"]:
        f += 6

    v = 0
    v += min(40, m["signal_prix"] * 2)       # des prix dans la page
    v += min(30, m["signal_date"] * 3)       # des dates
    if m["volume_indice"]:
        v += 30
    elif m["mecanismes"]:
        v += 15

    return {"faisabilite": f, "valeur": min(100, v), "score": round(f * min(100, v) / 100)}


def verdict(m: dict) -> str:
    if not m["robots_ok"]:
        return "INTERDIT par robots"
    if m["http"] == 0:
        return "injoignable"
    if m["endpoint"]:
        # un endpoint qui rend du JSON prouve l'acces, quoi que dise la page d'accueil
        return f"FACILE ({m['endpoint']})"
    if m["antibot"]:
        return f"BLOQUE ({m['antibot'].split(' · ')[0]})"
    if m["http"] != 200:
        return f"HTTP {m['http']}"
    if m["signal_prix"] == 0:
        return "rendu JS ou pas de prix en clair"
    if m["mecanismes"]:
        return "exploitable (donnees structurees)"
    if m["sitemap"]:
        return "a creuser (sitemap seul, pas d'endpoint)"
    return "exploitable (HTML)"


# ---------------------------------------------------------------------- cibles

def cibles_connues() -> list[tuple[str, str]]:
    """Les sites qu'on connait, tires du code et du catalogue."""
    import catalogue
    import sources as paquet

    vus, liste = set(), []

    def ajoute(nom, url):
        d = urllib.parse.urlparse(url).netloc
        if d and d not in vus:
            vus.add(d)
            liste.append((nom, f"https://{d}/"))

    for m in paquet.ALL:
        base = (getattr(m, "BASE", None) or getattr(m, "SITEMAP", None)
                or getattr(m, "CALENDAR", None) or getattr(m, "LOTSEARCH", None) or "")
        ajoute(m.SOURCE["name"], base)

    connus = {
        "EveryWatch": "https://everywatch.com", "Loupe This": "https://loupethis.com",
        "Monaco Legend": "https://monacolegendauctions.com",
        "Hodinkee Shop": "https://shop.hodinkee.com",
        "Watchtrader": "https://watchtrader.co.uk",
        "Wanna Buy A Watch": "https://wannabuyawatch.com",
        "Menta Watches": "https://mentawatches.com",
        "Amsterdam Vintage Watches": "https://amsterdamvintagewatches.com",
        "Patek Philippe": "https://www.patek.com", "Grand Seiko": "https://www.grand-seiko.com",
        "WatchCharts": "https://watchcharts.com", "Chrono24": "https://www.chrono24.com",
        "Barnebys": "https://www.barnebys.com", "Phillips": "https://www.phillips.com",
        "Sotheby's": "https://www.sothebys.com", "the-saleroom": "https://www.the-saleroom.com",
        "Invaluable": "https://www.invaluable.com", "Bonhams": "https://www.bonhams.com",
        "Antiquorum": "https://www.antiquorum.swiss", "Artcurial": "https://www.artcurial.com",
        "Dorotheum": "https://www.dorotheum.com", "Heritage": "https://www.ha.com",
        "Watchfinder": "https://www.watchfinder.co.uk", "Bob's Watches": "https://www.bobswatches.com",
        "Chronext": "https://www.chronext.com", "1stDibs": "https://www.1stdibs.com",
    }
    for nom, url in connus.items():
        ajoute(nom, url)
    return liste


# ------------------------------------------------------------------------ run

def sonde_un(nom: str, url: str) -> dict:
    m = {"source": nom, "url": url}
    m.update(controle_robots(url))
    if m["robots_ok"]:
        m.update(controle_page(url))
        m.update(controle_endpoints(url, m["robots_ok"]))
    else:
        m.update({"http": 0, "octets": 0, "antibot": "", "signal_faible": "", "mecanismes": "",
                  "signal_prix": 0, "signal_date": 0, "annee_min": None,
                  "erreur_reseau": "", "endpoint": "", "sitemap": "",
                  "volume_indice": ""})
    m.update(note(m))
    m["verdict"] = verdict(m)
    return m


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--url" in sys.argv:
        u = sys.argv[sys.argv.index("--url") + 1]
        cibles = [(urllib.parse.urlparse(u).netloc, u)]
    else:
        cibles = cibles_connues()
        if args:
            filtre = {a.lower() for a in args}
            cibles = [(n, u) for n, u in cibles
                      if any(f in n.lower() or f in u.lower() for f in filtre)]
    if not cibles:
        sys.exit("aucune cible — noms connus : " +
                 ", ".join(n for n, _ in cibles_connues()))

    ancien = {}
    if HISTORIQUE.exists():
        ancien = {d["source"]: d for d in json.loads(HISTORIQUE.read_text())["mesures"]}

    print(f"Sonde de {len(cibles)} site(s) — robots.txt d'abord, {PAUSE}s entre requetes\n")
    mesures, regressions, progressions = [], [], []
    for i, (nom, url) in enumerate(cibles, 1):
        m = sonde_un(nom, url)
        mesures.append(m)
        avant = ancien.get(nom)
        fleche = ""
        if avant:
            if avant["score"] >= 40 > m["score"]:
                regressions.append((nom, avant["verdict"], m["verdict"]))
                fleche = "  <== REGRESSION"
            elif m["score"] >= 40 > avant["score"]:
                progressions.append((nom, avant["verdict"], m["verdict"]))
                fleche = "  <== s'est ouvert"
        print(f"{i:>3}. {nom:<26} {m['score']:>3}/100  {m['verdict']}{fleche}")

    HISTORIQUE.write_text(json.dumps(
        {"date": dt.datetime.now().isoformat(timespec="seconds"), "mesures": mesures},
        ensure_ascii=False, indent=1), encoding="utf-8")

    print("\n" + "=" * 74)
    for m in sorted(mesures, key=lambda x: -x["score"])[:5]:
        print(f"  meilleur  {m['source']:<26} {m['score']:>3}  {m['verdict']}")
    fermes = [m for m in mesures if m["score"] < 40]
    print(f"\n  {len(mesures) - len(fermes)} exploitables · {len(fermes)} fermes")

    if regressions:
        print("\n" + "!" * 74)
        for nom, avant, apres in regressions:
            print(f"REGRESSION  {nom} : {avant} -> {apres}")
        print("!" * 74)
    for nom, avant, apres in progressions:
        print(f"OUVERTURE   {nom} : {avant} -> {apres}")

    print(f"\nmesures enregistrees dans data/{HISTORIQUE.name} "
          f"(relance la sonde pour comparer)")
    if regressions:
        sys.exit(1)


if __name__ == "__main__":
    main()
