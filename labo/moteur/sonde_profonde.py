"""Sonde PROFONDE — va chercher la donnee, pas seulement la page d'accueil.

    cd ~/Desktop/WP/labo
    shared/.venv/bin/python moteur/sonde_profonde.py

La sonde simple dit "le site repond". Celle-ci repond a la vraie question :
QU'EST-CE QU'ON PEUT EN TIRER ? Pour chaque source jugee accessible, elle
cherche une page de liste (annonces, lots, catalogue), y detecte le mecanisme
de donnees, et en extrait de VRAIS prix pour mesurer ce qu'on obtiendrait.

Elle ne traite que les sources deja jugees accessibles par `sonde.py` : inutile
de re-solliciter un site qui nous bloque ou nous interdit.

POLITESSE — la lecon du 429 : on ralentit et on limite.
  · 3 secondes entre deux requetes sur un meme site
  · 6 requetes maximum par source
  · 3 domaines en parallele seulement
  · un 429 arrete la source, on ne reessaie pas dans la foulee
"""
from __future__ import annotations

import collections
import datetime as dt
import json
import pathlib
import re
import statistics
import sys
import time
import urllib.parse

import requests
from bs4 import BeautifulSoup

ICI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
sys.path.insert(0, str(ICI.parent / "shared"))
from utils import HEADERS  # noqa: E402

SONDE = ICI.parent / "data" / "sonde.json"
SORTIE = ICI.parent / "data" / "sonde_profonde.json"
PAUSE = 3.0
PARALLELE = 3
MAX_REQUETES = 6

# Chemins ou vivent habituellement les listes d'annonces ou de lots.
PISTES = ["/collections/all", "/shop", "/watches", "/catalogue", "/catalog",
          "/auctions", "/results", "/auction-results", "/for-sale", "/boutique"]

MONTANT = re.compile(
    r"(?:USD|EUR|GBP|CHF|HKD|JPY|\$|€|£)\s?([\d][\d\s.,']{2,})", re.I)
DATE_ISO = re.compile(r"\b(19|20)\d{2}-\d{2}-\d{2}\b")
ANNEE = re.compile(r"\b(19[3-9]\d|20[0-2]\d)\b")
REF = re.compile(r"\bref\.?\s*([A-Z0-9][A-Z0-9./-]{2,15})", re.I)

MARQUES = ("rolex", "omega", "patek", "tudor", "cartier", "seiko", "iwc",
           "breitling", "longines", "heuer", "zenith", "oris", "jaeger",
           "audemars", "panerai", "hamilton", "tissot", "vacheron", "chopard")


class Budget:
    """Compte les requetes d'une source et coupe net au plafond."""

    def __init__(self, plafond=MAX_REQUETES):
        self.reste = plafond
        self.bloque = False

    def get(self, url, **kw):
        if self.reste <= 0 or self.bloque:
            return None
        self.reste -= 1
        try:
            r = requests.get(url, headers=HEADERS, timeout=25, **kw)
        except requests.RequestException:
            time.sleep(PAUSE)
            return None
        if r.status_code == 429:
            self.bloque = True          # on n'insiste jamais sur un 429
        time.sleep(PAUSE)
        return r


def _nombres(texte: str) -> list[float]:
    out = []
    for brut in MONTANT.findall(texte):
        n = re.sub(r"[\s']", "", brut).rstrip(".,")
        if "," in n and "." in n:
            n = n.replace(",", "") if n.rfind(".") > n.rfind(",") else n.replace(".", "").replace(",", ".")
        elif "," in n:
            p = n.split(",")
            n = n.replace(",", "") if len(p[-1]) == 3 else n.replace(",", ".")
        elif "." in n:
            p = n.split(".")
            if len(p) > 2 or len(p[-1]) == 3:
                n = n.replace(".", "")
        try:
            v = float(n)
            if 50 <= v <= 20_000_000:      # une montre, pas un numero de telephone
                out.append(v)
        except ValueError:
            pass
    return out


def _mecanisme(html: str) -> tuple[str, int]:
    """Quel format de donnees structurees, et combien d'objets dedans."""
    soupe = BeautifulSoup(html, "lxml")

    blocs = soupe.find_all("script", type="application/ld+json")
    produits = 0
    for b in blocs:
        try:
            d = json.loads(b.string or "{}", strict=False)
        except (json.JSONDecodeError, TypeError):
            continue
        pile = [d]
        while pile:
            o = pile.pop()
            if isinstance(o, dict):
                if o.get("@type") in ("Product", "Offer", "ListItem"):
                    produits += 1
                pile += [v for v in o.values() if isinstance(v, (dict, list))]
            elif isinstance(o, list):
                pile += o
    if produits:
        return f"JSON-LD ({produits} objets)", produits

    if 'id="__NEXT_DATA__"' in html:
        return "__NEXT_DATA__", html.count('"price')
    if re.search(r"window\.__(data|INITIAL|PRELOADED)", html):
        return "JSON embarque", html.count('"price')
    if "application/json" in html and html.count('"price') > 5:
        return "JSON inline", html.count('"price')
    return "HTML seul", 0


def _pagination(html: str) -> str:
    for motif, nom in [(r'rel="next"', "rel=next"), (r"[?&]page=\d+", "?page="),
                       (r"[?&]p=\d+", "?p="), (r"[?&]offset=\d+", "?offset="),
                       (r"[?&]start=\d+", "?start=")]:
        if re.search(motif, html):
            return nom
    return ""


def profonde(mesure: dict) -> dict:
    nom, base = mesure["source"], mesure["url"]
    b = Budget()
    res = {"source": nom, "url": base, "categorie": mesure.get("categorie", ""),
           "verdict_sonde": mesure["verdict"], "score_sonde": mesure["score"]}

    # 1) volume : le sitemap donne un ordre de grandeur sans charger le site
    sm = b.get(urllib.parse.urljoin(base, "/sitemap.xml"))
    if sm is not None and sm.status_code == 200 and "<loc>" in sm.text:
        res["urls_sitemap"] = sm.text.count("<loc>")
        sous = re.findall(r"<loc>([^<]+\.xml)</loc>", sm.text)
        res["sitemap_index"] = len(sous)

    # 2) trouver une page qui porte des prix
    page, chemin = None, None
    for piste in PISTES:
        if b.reste <= 1:
            break
        r = b.get(urllib.parse.urljoin(base, piste))
        if r is not None and r.status_code == 200 and len(_nombres(r.text)) >= 3:
            page, chemin = r.text, piste
            break
    if page is None:
        r = b.get(base)
        if r is not None and r.status_code == 200:
            page, chemin = r.text, "/"

    if b.bloque:
        res["verdict"] = "limite par le site (429)"
        return res
    if page is None:
        res["verdict"] = "aucune page de liste trouvee"
        return res

    res["page_testee"] = chemin
    meca, objets = _mecanisme(page)
    res["mecanisme"] = meca
    res["objets_structures"] = objets
    res["pagination"] = _pagination(page)

    prix = _nombres(page)
    res["prix_sur_la_page"] = len(prix)
    if prix:
        res["prix_min"] = round(min(prix))
        res["prix_median"] = round(statistics.median(prix))
        res["prix_max"] = round(max(prix))
    res["devises"] = " ".join(sorted({d for d in ("USD", "EUR", "GBP", "CHF", "HKD")
                                      if d in page or {"USD": "$", "EUR": "€", "GBP": "£"}.get(d, "@") in page}))

    dates = DATE_ISO.findall(page)
    annees = sorted({int(a) for a in ANNEE.findall(page)})
    res["dates_iso"] = len(dates)
    res["annee_min"] = annees[0] if annees else None
    res["annee_max"] = annees[-1] if annees else None
    res["profondeur_apparente"] = (annees[-1] - annees[0]) if len(annees) > 1 else 0

    bas = page.lower()
    res["marques_reperees"] = sum(1 for m in MARQUES if m in bas)
    res["references_reperees"] = len(set(REF.findall(page)))

    # verdict : ce qu'on peut en tirer, pas seulement s'il repond
    if res["prix_sur_la_page"] >= 10 and objets >= 5:
        res["verdict"] = "RICHE — donnees structurees + prix en nombre"
    elif res["prix_sur_la_page"] >= 10:
        res["verdict"] = "prix en clair, a parser en HTML"
    elif objets >= 5:
        res["verdict"] = "structure mais peu de prix sur cette page"
    elif res["prix_sur_la_page"] >= 3:
        res["verdict"] = "quelques prix seulement"
    else:
        res["verdict"] = "pas de prix trouve (rendu JS ?)"
    return res


def main() -> None:
    if not SONDE.exists():
        sys.exit("lance d'abord : python moteur/sonde.py --registre")
    mesures = json.load(SONDE.open(encoding="utf-8"))["mesures"]
    # Toute source qu'on a le droit de solliciter et qui repond, quel que soit
    # son score : un score bas vient souvent d'une page d'accueil vitrine, pas
    # d'une absence de donnees. On ne juge pas ce qu'on n'a pas ouvert.
    deja = set()
    ancien = ICI.parent / "data" / "sonde_profonde.json"
    if ancien.exists() and "--tout" not in sys.argv:
        deja = {s["source"] for s in json.load(ancien.open(encoding="utf-8"))["sources"]}
    cibles = [m for m in mesures
              if m.get("robots_ok") and m.get("http") == 200
              and "BLOQUE" not in m["verdict"] and m["source"] not in deja]

    print(f"Sonde profonde sur {len(cibles)} sources accessibles "
          f"(sur {len(mesures)} testees).")
    print(f"{MAX_REQUETES} requetes max par source, {PAUSE}s de pause, "
          f"{PARALLELE} domaines en parallele.\n")

    from concurrent.futures import ThreadPoolExecutor, as_completed
    resultats, faits = [], 0
    with ThreadPoolExecutor(max_workers=PARALLELE) as pool:
        futurs = {pool.submit(profonde, m): m["source"] for m in cibles}
        for f in as_completed(futurs):
            faits += 1
            try:
                resultats.append(f.result())
            except Exception as e:
                resultats.append({"source": futurs[f], "verdict": f"erreur {type(e).__name__}"})
            if faits % 15 == 0:
                print(f"    ... {faits}/{len(cibles)}")

    ordre = {"RICHE — donnees structurees + prix en nombre": 0,
             "prix en clair, a parser en HTML": 1,
             "structure mais peu de prix sur cette page": 2,
             "quelques prix seulement": 3}
    resultats.sort(key=lambda r: (ordre.get(r.get("verdict"), 9),
                                  -r.get("prix_sur_la_page", 0)))

    print(f"\n{'SOURCE':<28}{'PRIX':>6}{'OBJETS':>8}  {'MECANISME':<24}{'ANNEES':>12}")
    print("-" * 84)
    for r in resultats[:40]:
        plage = (f"{r.get('annee_min')}-{r.get('annee_max')}"
                 if r.get("annee_min") else "")
        print(f"{r['source'][:27]:<28}{r.get('prix_sur_la_page', 0):>6}"
              f"{r.get('objets_structures', 0):>8}  {r.get('mecanismes', r.get('mecanisme', ''))[:23]:<24}{plage:>12}")

    # On COMPLETE le fichier au lieu de l'ecraser : les sources deja sondees
    # gardent leur mesure, on ne re-sollicite pas un site pour rien.
    anciens = []
    if SORTIE.exists() and "--tout" not in sys.argv:
        anciens = json.load(SORTIE.open(encoding="utf-8"))["sources"]
        nouveaux = {r["source"] for r in resultats}
        anciens = [a for a in anciens if a["source"] not in nouveaux]
    SORTIE.write_text(json.dumps(
        {"date": dt.datetime.now().isoformat(timespec="seconds"),
         "sources": anciens + resultats},
        ensure_ascii=False, indent=1), encoding="utf-8")

    c = collections.Counter(r.get("verdict", "?").split(" —")[0] for r in resultats)
    print()
    for k, n in c.most_common():
        print(f"  {n:>3}  {k}")
    print(f"\nresultats : data/{SORTIE.name}")


if __name__ == "__main__":
    main()
