"""PASSE 1 — reconnaissance : ou vivent les donnees exploitables ?

    cd ~/Desktop/WP/labo
    shared/.venv/bin/python moteur/reconnaissance.py

La sonde profonde n'a regarde qu'une PAGE DE LISTE. Or beaucoup de sites ne
publient leur JSON-LD que sur les FICHES PRODUIT : une source classee « HTML
seul » peut tres bien exposer un JSON-LD parfait sur chacune de ses fiches.

Cette passe le verifie a moindre frais : pour chaque source, on prend UNE seule
fiche et on regarde ce qu'elle porte. Deux ou trois requetes par source, contre
une centaine pour une extraction complete. Elle dit lesquelles meritent la
passe 2.

Politesse : 3 s entre requetes, 3 requetes max par source, 3 domaines en
parallele, arret immediat sur un 429.
"""
from __future__ import annotations

import collections
import datetime as dt
import json
import pathlib
import re
import sys
import time
import urllib.parse

import requests
from bs4 import BeautifulSoup

ICI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ICI.parent / "shared"))
from utils import HEADERS  # noqa: E402

LABO = ICI.parent
SORTIE = LABO / "output2"
PAUSE = 3.0
PARALLELE = 3
MAX_REQUETES = 5

# Motifs d'URL de fiche produit ou de lot, du plus courant au moins.
MOTIFS_FICHE = [
    r"/products?/[^/\"'<>?]{4,}",
    r"/lots?/[^/\"'<>?]{4,}",
    r"/lot-details/[^/\"'<>?]{4,}",
    r"/item/[^/\"'<>?]{4,}",
    r"/ventes?/[^/\"'<>?]{6,}",
    r"/auctions?/[^/\"'<>?]{6,}",
    r"/watch(?:es)?/[^/\"'<>?]{6,}",
    r"/montre[s]?/[^/\"'<>?]{6,}",
    r"/shop/[^/\"'<>?]{6,}",
    r"/catalog(?:ue)?/[^/\"'<>?]{6,}",
]
# Mots qui designent un sitemap de fiches. On les cherche APRES avoir retire
# le mot « sitemap » lui-meme, sinon « item » matche tout.
MOTS_SITEMAP = r"produc|lot|watch|shop|sale|vente|auction|catalog|archive|montre|result|item"

MONNAIE = re.compile(r"(?:USD|EUR|GBP|CHF|HKD|\$|€|£)\s?\d[\d\s.,']{2,}", re.I)


class Budget:
    def __init__(self, plafond=MAX_REQUETES):
        self.reste, self.bloque = plafond, False

    def get(self, url):
        if self.reste <= 0 or self.bloque:
            return None
        self.reste -= 1
        try:
            r = requests.get(url, headers=HEADERS, timeout=25)
        except requests.RequestException:
            time.sleep(PAUSE)
            return None
        if r.status_code == 429:
            self.bloque = True
        time.sleep(PAUSE)
        return r


def _jsonld(html: str) -> tuple[int, list[str], bool]:
    """Compte les objets Product/Offer et dit si un prix y figure."""
    produits, types, avec_prix = 0, set(), False
    for bloc in BeautifulSoup(html, "lxml").find_all("script", type="application/ld+json"):
        try:
            d = json.loads(bloc.string or "{}", strict=False)
        except (json.JSONDecodeError, TypeError):
            continue
        pile = [d]
        while pile:
            o = pile.pop()
            if isinstance(o, dict):
                t = o.get("@type")
                if isinstance(t, list):
                    t = t[0] if t else None
                if t:
                    types.add(str(t))
                if t in ("Product", "Offer", "IndividualProduct"):
                    produits += 1
                    if o.get("price") or (o.get("offers") or {}):
                        avec_prix = True
                pile += [v for v in o.values() if isinstance(v, (dict, list))]
            elif isinstance(o, list):
                pile += o
    return produits, sorted(types)[:6], avec_prix


# Les sitemaps s'ecrivent de trois facons : <loc>url</loc>, avec du CDATA,
# ou avec des espaces. Une seule fonction les lit toutes, sinon on rate des
# sites entiers sans s'en apercevoir.
LOC = re.compile(r"<loc>\s*(?:<!\[CDATA\[)?\s*(https?://[^\]<\s]+?)\s*(?:\]\]>)?\s*</loc>", re.I)


def _locs(texte: str) -> list[str]:
    return [u.replace("&amp;", "&") for u in LOC.findall(texte)]


def _sitemaps_declares(base, b):
    """Le sitemap n'est pas toujours a /sitemap.xml : la norme veut qu'il soit
    declare dans le robots.txt, et beaucoup de sites ne font que ca."""
    r = b.get(urllib.parse.urljoin(base, "/robots.txt"))
    if r is None or r.status_code != 200:
        return []
    return [u.strip() for u in re.findall(r"(?im)^\s*sitemap:\s*(\S+)", r.text)][:3]


def _urls_fiches(base: str, b: Budget, plafond: int = 3) -> list[str]:
    """Trouve des URL de fiche produit ou de lot, en partant des sitemaps.

    Quatre pieges rencontres, tous silencieux, tous corriges ici :
      · /sitemap.xml renvoie souvent 404 : la norme veut qu'il soit declare
        dans le robots.txt, et beaucoup de sites ne font que ca
      · les URL sont parfois enveloppees dans du CDATA
      · le mot « sitemap » contient « item », donc un filtre naif matche tout
      · « exemple.com » et « www.exemple.com » designent le meme site
    """
    dom_nu = urllib.parse.urlparse(base).netloc.removeprefix("www.")
    dom_re = r"(?:www\.)?" + re.escape(dom_nu)

    r = b.get(urllib.parse.urljoin(base, "/sitemap.xml"))
    if r is None or r.status_code != 200 or "<loc>" not in r.text:
        for u in _sitemaps_declares(base, b):
            r = b.get(u)
            if r is not None and r.status_code == 200 and "<loc>" in r.text:
                break

    textes = []
    if r is not None and r.status_code == 200 and "<loc>" in r.text:
        sous = [u for u in _locs(r.text) if ".xml" in u.lower()]
        # on retire « sitemap » du nom avant de chercher les mots-cles
        pertinents = [s for s in sous
                      if re.search(MOTS_SITEMAP, s.replace("sitemap", ""), re.I)]
        for s in (pertinents or sous)[:2]:
            if b.bloque or b.reste <= 1:
                break
            r2 = b.get(s)
            if r2 is not None and r2.status_code == 200:
                textes.append(r2.text)
        textes.append(r.text)

    if not textes:
        r3 = b.get(base)
        if r3 is not None and r3.status_code == 200:
            textes.append(r3.text)

    trouvees = []
    for texte in textes:
        # d'abord les URL completes du sitemap, puis les liens relatifs du HTML
        for u in _locs(texte):
            if re.match(rf"https?://{dom_re}", u) and any(
                    re.search(m, u) for m in MOTIFS_FICHE):
                if u not in trouvees:
                    trouvees.append(u)
        if not trouvees:
            for motif in MOTIFS_FICHE:
                for m in re.findall(rf"https?://{dom_re}{motif}", texte)[:4]:
                    if m not in trouvees:
                        trouvees.append(m)
                for m in re.findall(rf'"({motif})"', texte)[:4]:
                    u = urllib.parse.urljoin(base, m)
                    if u not in trouvees:
                        trouvees.append(u)
        if trouvees:
            break

    # echantillon reparti, pas les premieres du catalogue
    if len(trouvees) > plafond:
        pas = max(1, len(trouvees) // plafond)
        trouvees = trouvees[::pas]
    return trouvees[:plafond]


def reconnait(source: dict) -> dict:
    nom, base = source["source"], source["url"]
    b = Budget()
    res = {"source": nom, "url": base, "verdict_sonde": source.get("verdict", "")}

    fiches = _urls_fiches(base, b)
    if b.bloque:
        res["verdict"] = "429, le site nous limite"
        return res
    if not fiches:
        res["verdict"] = "aucune URL de fiche reperee"
        return res
    res["exemple_fiche"] = fiches[0]

    r = b.get(fiches[0])
    if r is None or r.status_code != 200:
        res["verdict"] = f"fiche injoignable ({getattr(r, 'status_code', 'timeout')})"
        return res

    html = r.text
    produits, types, avec_prix = _jsonld(html)
    res["jsonld_objets"] = produits
    res["jsonld_types"] = " · ".join(types)
    res["jsonld_avec_prix"] = avec_prix
    res["next_data"] = 'id="__NEXT_DATA__"' in html
    res["prix_html"] = len(set(MONNAIE.findall(html)))
    res["octets"] = len(html)

    # ce que la passe 2 pourrait en tirer
    if produits and avec_prix:
        res["verdict"] = "JSON-LD Product avec prix — extractible"
        res["voie"] = "jsonld"
    elif res["next_data"] and res["prix_html"]:
        res["verdict"] = "__NEXT_DATA__ avec prix — extractible"
        res["voie"] = "nextdata"
    elif produits:
        res["verdict"] = "JSON-LD sans prix — a confirmer"
        res["voie"] = "jsonld"
    elif res["prix_html"] >= 2:
        res["verdict"] = "prix en HTML seulement — extraction sur mesure"
        res["voie"] = "html"
    else:
        res["verdict"] = "aucun prix sur la fiche"
        res["voie"] = ""
    return res


def main() -> None:
    sonde = {m["source"]: m for m in json.load((LABO / "data" / "sonde.json").open(encoding="utf-8"))["mesures"]}
    profonde = json.load((LABO / "data" / "sonde_profonde.json").open(encoding="utf-8"))["sources"]

    # On ne reconnait QUE ce qui n'a pas deja un endpoint standard : ces
    # sources-la sont deja extractibles sans effort.
    cibles = []
    for p in profonde:
        s = sonde.get(p["source"], {})
        if s.get("endpoint"):
            continue
        if not s.get("robots_ok") or s.get("http") != 200:
            continue
        if "BLOQUE" in s.get("verdict", ""):
            continue
        cibles.append({"source": p["source"], "url": s["url"], "verdict": p.get("verdict", "")})

    print(f"Passe 1 — reconnaissance sur {len(cibles)} sources sans endpoint standard.")
    print(f"{MAX_REQUETES} requetes max par source, {PAUSE}s de pause.\n")

    from concurrent.futures import ThreadPoolExecutor, as_completed
    resultats, faits = [], 0
    with ThreadPoolExecutor(max_workers=PARALLELE) as pool:
        futurs = {pool.submit(reconnait, c): c["source"] for c in cibles}
        for f in as_completed(futurs):
            faits += 1
            try:
                resultats.append(f.result())
            except Exception as e:
                resultats.append({"source": futurs[f], "verdict": f"erreur {type(e).__name__}"})
            if faits % 15 == 0:
                print(f"    ... {faits}/{len(cibles)}")

    ordre = {"JSON-LD Product avec prix — extractible": 0,
             "__NEXT_DATA__ avec prix — extractible": 1,
             "JSON-LD sans prix — a confirmer": 2,
             "prix en HTML seulement — extraction sur mesure": 3}
    resultats.sort(key=lambda r: (ordre.get(r.get("verdict"), 9), -r.get("prix_html", 0)))

    print(f"\n{'SOURCE':<32}{'OBJETS':>7}{'PRIX':>6}  VERDICT")
    print("-" * 92)
    for r in resultats:
        print(f"{r['source'][:31]:<32}{r.get('jsonld_objets', 0):>7}{r.get('prix_html', 0):>6}  "
              f"{r.get('verdict', '?')[:44]}")

    SORTIE.mkdir(parents=True, exist_ok=True)
    (SORTIE / "reconnaissance.json").write_text(json.dumps(
        {"date": dt.datetime.now().isoformat(timespec="seconds"), "sources": resultats},
        ensure_ascii=False, indent=1), encoding="utf-8")

    c = collections.Counter(r.get("verdict", "?").split(" —")[0] for r in resultats)
    print()
    for k, n in c.most_common():
        print(f"  {n:>3}  {k}")
    retenues = sum(1 for r in resultats if r.get("voie") in ("jsonld", "nextdata"))
    print(f"\n{retenues} sources retenues pour la passe 2 (extraction generique).")
    print(f"resultats : output2/reconnaissance.json")


if __name__ == "__main__":
    main()
