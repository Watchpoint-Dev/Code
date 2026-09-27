"""PASSE 2 — extraction et mesure : reference, nature du prix, delta.

    cd ~/Desktop/WP
    python research/outils/extraction.py

Repond a trois questions, source par source, en telechargeant de VRAIES fiches :

  1. LA REFERENCE — combien de fiches en portent une, et de quelle qualite ?
     On distingue trois cas, qui ne valent pas la meme chose :
       · champ dedie      la source publie la reference, fiable
       · extraite du titre  on la devine, avec un taux d'erreur
       · SKU               souvent un code interne, PAS la reference constructeur
     On interroge plusieurs marques par source : un taux mesure sur une seule
     marque ne dit rien de la source.

  2. LA NATURE DU PRIX — la repartition reelle, pas la nature declaree.
     Une source peut melanger demande et vendu selon le statut de l'annonce.

  3. LE DELTA — ce qui a change depuis la derniere mesure. Combien de fiches
     nouvelles, combien ont disparu. C'est ce qui dit si une source est vivante.

Politesse : 3 s entre requetes, sequentiel par hote, 3 domaines en parallele,
arret immediat sur un 429.
"""
from __future__ import annotations

from watchpoint import config

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
from watchpoint.commun.utils import HEADERS  # noqa: E402

LABO = config.RACINE
SORTIE = config.RESEARCH / "outils" / "sortie"
PAUSE = 3.0
PARALLELE = 3
CIBLE_FICHES = 250

# Marques interrogees pour verifier qu'une mesure ne depend pas d'une seule.
MARQUES_TEST = ["rolex", "omega", "patek philippe", "cartier", "tudor", "seiko"]

# Un SKU qui ressemble a ca est un code interne, pas une reference constructeur.
SKU_INTERNE = re.compile(r"^[A-Z]{2,}[-_]|^\d{1,3}[-_]\d|^[a-z]{2,}\d{2,}$", re.I)
REF_TITRE = re.compile(r"\bref\.?\s*n?o?\.?\s*([A-Z0-9][A-Z0-9./-]{2,15})", re.I)
REF_NUE = re.compile(r"\b(\d{4,6}[A-Z]{0,3}(?:[-/]\d{2,4}[A-Z]?)?)\b")
# Mots qui designent un sitemap de fiches. On les cherche APRES avoir retire
# le mot « sitemap » lui-meme, sinon « item » matche tout.
MOTS_SITEMAP = r"produc|lot|watch|shop|sale|vente|auction|catalog|archive|montre|result|item"

MONNAIE = re.compile(r"(?:USD|EUR|GBP|CHF|HKD|\$|€|£)\s?(\d[\d\s.,']{2,})", re.I)

VENDU = ("sold", "vendu", "adjuge", "hammer", "realised", "realized", "verkauft")
DISPO = ("available", "instock", "in_stock", "for sale", "disponible", "published")


class Budget:
    """Plafonne les requetes d'une source et coupe net sur un 429."""

    def __init__(self, plafond):
        self.reste, self.bloque, self.utilisees = plafond, False, 0

    def get(self, url, **kw):
        if self.reste <= 0 or self.bloque:
            return None
        self.reste -= 1
        self.utilisees += 1
        try:
            r = requests.get(url, headers=HEADERS, timeout=30, **kw)
        except requests.RequestException:
            time.sleep(PAUSE)
            return None
        if r.status_code == 429:
            self.bloque = True
        time.sleep(PAUSE)
        return r


# ---------------------------------------------------------------- mesures

def _montant(texte):
    m = MONNAIE.search(str(texte or ""))
    if not m:
        return None
    n = re.sub(r"[\s']", "", m.group(1)).rstrip(".,")
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
        return float(n)
    except ValueError:
        return None


def qualifie_reference(fiche: dict) -> str:
    """D'ou vient la reference, et vaut-elle quelque chose ?"""
    if fiche.get("ref_champ"):
        return "champ dedie"
    sku = str(fiche.get("sku") or "")
    if sku and not SKU_INTERNE.match(sku) and re.search(r"\d{3,}", sku):
        return "sku exploitable"
    # Un SKU interne ne doit PAS masquer une reference lisible dans le titre :
    # chez certains marchands le SKU est un code maison, mais le titre porte
    # bien « Ref. 6239 ». On regarde le titre avant de renoncer.
    if fiche.get("ref_titre"):
        return "extraite du titre"
    if sku:
        return "sku interne"
    return "absente"


def qualifie_nature(fiche: dict) -> str:
    """La nature reelle, deduite des champs de statut."""
    blob = " ".join(str(fiche.get(k) or "") for k in ("statut", "dispo", "categorie", "titre")).lower()
    if any(v in blob for v in VENDU):
        return "vendu ou realise"
    if fiche.get("est_enchere"):
        return "realise"
    if any(d in blob for d in DISPO) or fiche.get("prix") is not None:
        return "demande"
    return "indetermine"


# ------------------------------------------------------------- extracteurs

def _fiche_depuis_jsonld(html: str) -> list[dict]:
    out = []
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
                t = t[0] if isinstance(t, list) and t else t
                if t in ("Product", "IndividualProduct"):
                    offre = o.get("offers") or {}
                    offre = offre[0] if isinstance(offre, list) and offre else offre
                    marque = o.get("brand")
                    if isinstance(marque, dict):
                        marque = marque.get("name")
                    out.append({
                        "titre": o.get("name"), "marque": marque,
                        "ref_champ": o.get("mpn") or o.get("productID") or o.get("model"),
                        "sku": o.get("sku"),
                        "prix": _montant(offre.get("price")) if isinstance(offre, dict) else None,
                        "devise": (offre or {}).get("priceCurrency") if isinstance(offre, dict) else None,
                        "dispo": str((offre or {}).get("availability", "")) if isinstance(offre, dict) else "",
                        "statut": "", "categorie": o.get("category"), "est_enchere": False,
                    })
                pile += [v for v in o.values() if isinstance(v, (dict, list))]
            elif isinstance(o, list):
                pile += o
    return out


def _fiches_shopify(base, b, journal):
    fiches, page = [], 1
    devise = None
    r = b.get(urllib.parse.urljoin(base, "/meta.json"))
    if r is not None and r.status_code == 200:
        try:
            devise = r.json().get("currency")
        except ValueError:
            pass
    while len(fiches) < CIBLE_FICHES and not b.bloque:
        url = urllib.parse.urljoin(base, f"/products.json?limit=250&page={page}")
        if devise:
            url += f"&currency={devise}"
        r = b.get(url)
        if r is None or r.status_code != 200:
            journal.append(f"products.json page {page}: {getattr(r,'status_code','timeout')}")
            break
        try:
            prods = r.json().get("products", [])
        except ValueError:
            break
        if not prods:
            break
        for p in prods:
            v = (p.get("variants") or [{}])[0]
            titre = p.get("title") or ""
            m = REF_TITRE.search(titre)
            fiches.append({
                "id": str(p.get("id")), "titre": titre, "marque": p.get("vendor"),
                "ref_champ": None, "sku": v.get("sku"),
                "ref_titre": m.group(1) if m else None,
                "prix": _montant(v.get("price")) or (float(v["price"]) if v.get("price") else None),
                "devise": devise, "dispo": "available" if v.get("available") else "",
                "statut": "", "categorie": p.get("product_type"), "est_enchere": False,
                "date": (p.get("published_at") or p.get("created_at") or "")[:10] or None,
            })
        if len(prods) < 250:
            break
        page += 1
    return fiches


def _fiches_woo(base, b, journal):
    fiches, page = [], 1
    while len(fiches) < CIBLE_FICHES and not b.bloque:
        r = b.get(urllib.parse.urljoin(base, f"/wp-json/wc/store/products?per_page=100&page={page}"))
        if r is None or r.status_code != 200:
            journal.append(f"store api page {page}: {getattr(r,'status_code','timeout')}")
            break
        try:
            prods = r.json()
        except ValueError:
            break
        if not isinstance(prods, list) or not prods:
            break
        for p in prods:
            pr = p.get("prices") or {}
            unite = int(pr.get("currency_minor_unit", 2) or 0)
            brut = pr.get("price")
            montant = float(brut) / (10 ** unite) if brut not in (None, "") else None
            titre = p.get("name") or ""
            m = REF_TITRE.search(titre)
            marque = None
            for att in (p.get("attributes") or []):
                if re.search(r"brand|marque", str(att.get("name", "")), re.I):
                    termes = att.get("terms") or []
                    marque = termes[0].get("name") if termes else None
            cats = " ".join(str(c.get("name", "")) for c in (p.get("categories") or []))
            fiches.append({
                "id": str(p.get("id")), "titre": titre, "marque": marque,
                "ref_champ": None, "sku": p.get("sku"), "ref_titre": m.group(1) if m else None,
                "prix": montant, "devise": pr.get("currency_code"),
                "dispo": "instock" if p.get("is_in_stock") else "",
                "statut": "", "categorie": cats, "est_enchere": False, "date": None,
                "unite_mineure": unite,
            })
        if len(prods) < 100:
            break
        page += 1
    return fiches


def _fiches_jsonld(base, b, journal, urls):
    fiches = []
    for u in urls:
        if b.bloque or len(fiches) >= CIBLE_FICHES:
            break
        r = b.get(u)
        if r is None or r.status_code != 200:
            continue
        for f in _fiche_depuis_jsonld(r.text):
            titre = f.get("titre") or ""
            m = REF_TITRE.search(titre)
            f["ref_titre"] = m.group(1) if m else None
            f["id"] = u
            f["date"] = None
            fiches.append(f)
    if not fiches:
        journal.append("aucune fiche JSON-LD exploitable")
    return fiches


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


def _urls_fiches(base, b, plafond):
    """Collecte des URL de fiche depuis les sitemaps."""
    dom = urllib.parse.urlparse(base).netloc
    # « acollectedman.com » et « www.acollectedman.com » designent le meme site :
    # le sitemap ecrit souvent l'un quand l'URL de base porte l'autre.
    dom_nu = dom.removeprefix("www.")
    dom_re = r"(?:www\.)?" + re.escape(dom_nu)
    r = b.get(urllib.parse.urljoin(base, "/sitemap.xml"))
    if r is None or r.status_code != 200 or "<loc>" not in r.text:
        for u in _sitemaps_declares(base, b):
            r = b.get(u)
            if r is not None and r.status_code == 200 and "<loc>" in r.text:
                break
        else:
            return []
    sous = [u for u in _locs(r.text) if ".xml" in u.lower()]
    textes = [r.text]
    sous = [s.replace("&amp;", "&") for s in sous]
    def _pertinent(u):
        return re.search(MOTS_SITEMAP, u.replace("sitemap", ""), re.I)
    for s in [x for x in sous if _pertinent(x)][:2]:
        if b.bloque:
            break
        rr = b.get(s)
        if rr is not None and rr.status_code == 200:
            textes.append(rr.text)
    urls = []
    for t in textes:
        for m in [u for u in _locs(t) if re.match(rf"https?://{dom_re}", u)]:
            if re.search(r"/(products?|lots?|item|watch(es)?|montres?)/[^/]{4,}", m) and m not in urls:
                urls.append(m)
    # echantillon reparti sur tout le catalogue, pas les N premieres
    if len(urls) > plafond:
        pas = len(urls) // plafond
        urls = urls[::pas][:plafond]
    return urls


# ---------------------------------------------------------------- mesure

def _mesure_fiches(nom, base, voie, fiches, b, journal) -> dict:
    res = {"source": nom, "url": base, "voie": voie,
           "requetes": b.utilisees, "limite_429": b.bloque,
           "fiches": len(fiches), "journal": journal}
    if not fiches:
        res["verdict"] = "429" if b.bloque else "aucune fiche extraite"
        return res

    n = len(fiches)
    # --- 1. la reference
    q = collections.Counter(qualifie_reference(f) for f in fiches)
    res["ref_champ_dedie_pct"] = round(100 * q["champ dedie"] / n)
    res["ref_sku_exploitable_pct"] = round(100 * q["sku exploitable"] / n)
    res["ref_titre_pct"] = round(100 * q["extraite du titre"] / n)
    res["ref_sku_interne_pct"] = round(100 * q["sku interne"] / n)
    res["ref_absente_pct"] = round(100 * q["absente"] / n)
    res["ref_utilisable_pct"] = round(100 * (q["champ dedie"] + q["sku exploitable"] + q["extraite du titre"]) / n)

    # --- 2. la nature du prix
    nat = collections.Counter(qualifie_nature(f) for f in fiches)
    for k, lib in [("demande", "nature_demande_pct"), ("vendu ou realise", "nature_vendu_pct"),
                   ("realise", "nature_realise_pct"), ("indetermine", "nature_indetermine_pct")]:
        res[lib] = round(100 * nat[k] / n)
    res["nature_dominante"] = nat.most_common(1)[0][0]

    # --- 3. la donnee elle-meme
    prix = [f["prix"] for f in fiches if f.get("prix")]
    res["prix_pct"] = round(100 * len(prix) / n)
    if prix:
        res["prix_min"], res["prix_median"], res["prix_max"] = (
            round(min(prix)), round(statistics.median(prix)), round(max(prix)))
        res["prix_aberrants"] = sum(1 for p in prix if p < 20 or p > 10_000_000)
    res["devises"] = " ".join(sorted({str(f.get("devise")) for f in fiches if f.get("devise")}))
    res["date_pct"] = round(100 * sum(1 for f in fiches if f.get("date")) / n)
    res["marque_pct"] = round(100 * sum(1 for f in fiches if f.get("marque")) / n)
    marques = collections.Counter(f["marque"] for f in fiches if f.get("marque"))
    res["marques_distinctes"] = len(marques)
    res["top_marques"] = " · ".join(str(m) for m, _ in marques.most_common(4))
    if any("unite_mineure" in f for f in fiches):
        res["unite_mineure_woo"] = fiches[0].get("unite_mineure")

    # --- 4. le cout de collecte
    res["fiches_par_requete"] = round(n / max(b.utilisees, 1), 1)
    res["exemple"] = str(fiches[0].get("titre"))[:70]
    res["ids"] = [str(f.get("id")) for f in fiches if f.get("id")]
    res["verdict"] = ("SOLIDE" if res["prix_pct"] >= 90 and res["ref_utilisable_pct"] >= 50
                      else "exploitable" if res["prix_pct"] >= 90
                      else "prix incomplets")
    return res

def _fiches_html(base, b, journal):
    """Dernier recours : lire les prix sur une page de liste, sans structure."""
    for piste in ("/collections/all", "/shop", "/watches", "/catalogue",
                  "/auctions", "/results", "/prices-realized", "/"):
        if b.bloque or b.reste <= 0:
            break
        r = b.get(urllib.parse.urljoin(base, piste))
        if r is None or r.status_code != 200:
            continue
        soupe = BeautifulSoup(r.text, "lxml")
        # on prend les blocs qui portent a la fois un texte et un montant
        fiches = []
        for bloc in soupe.find_all(["article", "li", "div"], limit=4000):
            txt = bloc.get_text(" ", strip=True)[:220]
            if not txt or len(txt) < 12:
                continue
            montant = _montant(txt)
            if montant is None or not (20 <= montant <= 10_000_000):
                continue
            if any(txt[:40] in f["titre"] for f in fiches):
                continue
            m = REF_TITRE.search(txt)
            fiches.append({"id": None, "titre": txt[:120], "marque": None,
                           "ref_champ": None, "sku": None,
                           "ref_titre": m.group(1) if m else None,
                           "prix": montant, "devise": None, "dispo": "",
                           "statut": "", "categorie": "", "est_enchere": False,
                           "date": None})
            if len(fiches) >= CIBLE_FICHES:
                break
        if len(fiches) >= 5:
            journal.append(f"prix lus en HTML sur {piste}")
            return fiches
    return []


def essaie_tout(source: dict) -> dict:
    """Essaie chaque voie jusqu'a ce qu'une rende des fiches. L'extraction EST le test."""
    nom, base = source["source"], source["url"]
    journal, essais = [], []
    for voie, budget in (("shopify", 8), ("woo", 8), ("jsonld", 110), ("html", 10)):
        b = Budget(budget)
        try:
            if voie == "shopify":
                fiches = _fiches_shopify(base, b, journal)
            elif voie == "woo":
                fiches = _fiches_woo(base, b, journal)
            elif voie == "jsonld":
                urls = _urls_fiches(base, b, 100)
                fiches = _fiches_jsonld(base, b, journal, urls) if urls else []
            else:
                fiches = _fiches_html(base, b, journal)
        except Exception as e:
            fiches = []
            journal.append(f"{voie}: {type(e).__name__}")
        essais.append(f"{voie}={len(fiches)}")
        if b.bloque:
            journal.append(f"{voie}: 429, on arrete cette source")
            return {"source": nom, "url": base, "voie": voie, "fiches": 0,
                    "verdict": "429, le site nous limite", "journal": journal,
                    "essais": " ".join(essais)}
        if len(fiches) >= 5:
            r = _mesure_fiches(nom, base, voie, fiches, b, journal)
            r["essais"] = " ".join(essais)
            return r
    return {"source": nom, "url": base, "voie": "", "fiches": 0,
            "verdict": "aucune voie n'a rendu de fiches", "journal": journal,
            "essais": " ".join(essais)}


def main() -> None:
    LABO_DATA = LABO / "data"
    sonde = {m["source"]: m for m in json.load((LABO_DATA / "sonde.json").open(encoding="utf-8"))["mesures"]}
    cibles = [{"source": s, "url": m["url"]} for s, m in sonde.items()
              if m.get("robots_ok") and m.get("http") == 200 and "BLOQUE" not in m.get("verdict", "")]

    print(f"Extraction sur {len(cibles)} sources accessibles.")
    print("Cascade : Shopify, WooCommerce, sitemap+JSON-LD, puis HTML.")
    print(f"{CIBLE_FICHES} fiches visees par source, {PAUSE}s entre requetes, "
          f"{PARALLELE} domaines en parallele.\n")

    from concurrent.futures import ThreadPoolExecutor, as_completed
    resultats, faits = [], 0
    with ThreadPoolExecutor(max_workers=PARALLELE) as pool:
        futurs = {pool.submit(essaie_tout, c): c["source"] for c in cibles}
        for f in as_completed(futurs):
            faits += 1
            try:
                resultats.append(f.result())
            except Exception as e:
                resultats.append({"source": futurs[f], "fiches": 0,
                                  "verdict": f"erreur {type(e).__name__}"})
            if faits % 10 == 0:
                total = sum(r.get("fiches", 0) for r in resultats)
                print(f"    ... {faits}/{len(cibles)} · {total} fiches extraites")

    resultats.sort(key=lambda r: -r.get("fiches", 0))
    SORTIE.mkdir(parents=True, exist_ok=True)
    (SORTIE / "extraction.json").write_text(json.dumps(
        {"date": dt.datetime.now().isoformat(timespec="seconds"), "sources": resultats},
        ensure_ascii=False, indent=1), encoding="utf-8")

    avec = [r for r in resultats if r.get("fiches", 0) >= 5]
    print(f"\n{'SOURCE':<30}{'FICHES':>7}{'REF':>6}{'PRIX':>6}  NATURE DOMINANTE")
    print("-" * 86)
    for r in avec[:45]:
        print(f"{r['source'][:29]:<30}{r['fiches']:>7}{r.get('ref_utilisable_pct',0):>5}%"
              f"{r.get('prix_pct',0):>5}%  {str(r.get('nature_dominante',''))[:28]}")
    total = sum(r.get("fiches", 0) for r in resultats)
    print(f"\n{len(avec)} sources ont rendu des fiches · {total} fiches au total")
    print(f"resultats : research/outils/sortie/extraction.json")


if __name__ == "__main__":
    main()
