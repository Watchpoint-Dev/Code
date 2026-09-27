"""Verification REELLE des sources a endpoint standard : on extrait, on mesure.

    cd ~/Desktop/WP/labo
    shared/.venv/bin/python moteur/verifie_sources.py

La sonde ne regarde que la page d'accueil : elle dit si un site repond, pas ce
qu'il contient. Ce script va plus loin — il telecharge de VRAIS produits sur
chaque boutique Shopify / WooCommerce reperee par la sonde, et mesure ce qu'on
obtiendrait vraiment : combien de fiches, quels champs remplis, quelles dates,
quelle devise.

C'est la difference entre "le site repond" et "la source vaut quelque chose".

Politesse : 1,2 s entre requetes sur un meme site, 3 requetes maximum par site,
domaines traites en parallele mais jamais deux requetes simultanees sur un hote.
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

ICI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
sys.path.insert(0, str(ICI.parent / "shared"))
from utils import HEADERS  # noqa: E402

SONDE = ICI.parent / "data" / "sonde.json"
SORTIE = ICI.parent / "data" / "verification_sources.json"
PAUSE = 2.5
PARALLELE = 3

# Champs du modele qu'on cherche a remplir, et ou les trouver selon la plateforme.
CHAMPS = ["brand", "reference", "year", "price_amount", "price_currency",
          "price_date", "condition", "images"]

REF = re.compile(r"\bref\.?\s*([A-Z0-9][A-Z0-9./-]{2,15})", re.I)
ANNEE = re.compile(r"\b(19[3-9]\d|20[0-2]\d)\b")


def _get(url, **kw):
    """Un 429 n'est pas un echec de la source : c'est nous qui allons trop vite."""
    for tentative in range(2):
        try:
            r = requests.get(url, headers=HEADERS, timeout=25, **kw)
        except requests.RequestException:
            time.sleep(PAUSE)
            return None
        if r.status_code == 429:
            attente = int(r.headers.get("Retry-After", 12))
            if tentative == 0:
                time.sleep(min(attente, 30))
                continue
            time.sleep(PAUSE)
            return r
        time.sleep(PAUSE)
        return r
    return None


# --------------------------------------------------------------- extraction

def _shopify(base: str) -> tuple[list[dict], dict]:
    """products.json — on impose la devise, sinon Shopify localise et convertit."""
    meta = _get(urllib.parse.urljoin(base, "/meta.json"))
    devise = None
    if meta is not None and meta.status_code == 200:
        try:
            devise = json.loads(meta.text).get("currency")
        except json.JSONDecodeError:
            pass

    url = urllib.parse.urljoin(base, "/products.json?limit=250")
    if devise:
        url += f"&currency={devise}"
    r = _get(url)
    if r is None or r.status_code != 200:
        return [], {"erreur": f"HTTP {getattr(r, 'status_code', 'timeout')}"}
    try:
        produits = json.loads(r.text).get("products", [])
    except json.JSONDecodeError:
        return [], {"erreur": "JSON illisible"}

    fiches = []
    for p in produits:
        v = (p.get("variants") or [{}])[0]
        titre = p.get("title") or ""
        ref = REF.search(titre)
        an = ANNEE.match(titre.strip())
        fiches.append({
            "brand": p.get("vendor"),
            "reference": ref.group(1) if ref else None,
            "year": int(an.group(1)) if an else None,
            "price_amount": float(v["price"]) if v.get("price") else None,
            "price_currency": devise,
            "price_date": (p.get("published_at") or p.get("created_at") or "")[:10] or None,
            "condition": "preowned" if v.get("available") else None,
            "images": len(p.get("images") or []) > 0,
            "titre": titre,
        })
    return fiches, {"devise_boutique": devise, "page_pleine": len(produits) >= 250}


def _woo(base: str) -> tuple[list[dict], dict]:
    """Store API — attention aux unites mineures : 21000000 au lieu de 210000."""
    r = _get(urllib.parse.urljoin(base, "/wp-json/wc/store/products?per_page=100"))
    if r is None or r.status_code != 200:
        return [], {"erreur": f"HTTP {getattr(r, 'status_code', 'timeout')}"}
    try:
        produits = json.loads(r.text)
    except json.JSONDecodeError:
        return [], {"erreur": "JSON illisible"}
    if not isinstance(produits, list):
        return [], {"erreur": "format inattendu"}

    fiches, mineures = [], None
    for p in produits:
        prix = p.get("prices") or {}
        brut = prix.get("price")
        dec = prix.get("currency_minor_unit", 2)
        montant = None
        if brut not in (None, ""):
            try:
                montant = float(brut) / (10 ** int(dec))
                mineures = int(dec)
            except (ValueError, TypeError):
                montant = None
        titre = p.get("name") or ""
        ref = REF.search(titre)
        an = ANNEE.match(titre.strip())
        marque = None
        for att in (p.get("attributes") or []):
            if "brand" in str(att.get("name", "")).lower() or "marque" in str(att.get("name", "")).lower():
                termes = att.get("terms") or []
                marque = termes[0].get("name") if termes else None
        fiches.append({
            "brand": marque,
            "reference": ref.group(1) if ref else None,
            "year": int(an.group(1)) if an else None,
            "price_amount": montant,
            "price_currency": prix.get("currency_code"),
            "price_date": None,           # le Store API n'expose pas de date
            "condition": None,
            "images": len(p.get("images") or []) > 0,
            "titre": titre,
        })
    return fiches, {"unite_mineure": mineures, "page_pleine": len(produits) >= 100,
                    "date_absente": True}


# ------------------------------------------------------------------ mesure

def verifie(nom: str, url: str, plateforme: str) -> dict:
    fiches, info = (_shopify(url) if "Shopify" in plateforme else _woo(url))
    res = {"source": nom, "url": url, "plateforme": plateforme,
           "fiches_extraites": len(fiches), **info}

    if not fiches:
        res["verdict"] = ("limite par le site (429) — a reessayer plus tard"
                          if "429" in str(info.get("erreur", ""))
                          else "aucune donnee extraite")
        return res

    n = len(fiches)
    res["completude"] = {
        c: round(100 * sum(1 for f in fiches if f.get(c) not in (None, "", False)) / n)
        for c in CHAMPS
    }
    montants = [f["price_amount"] for f in fiches if f.get("price_amount")]
    if montants:
        res["prix"] = {
            "min": round(min(montants)), "median": round(statistics.median(montants)),
            "max": round(max(montants)),
            "aberrants": sum(1 for m in montants if m > 5_000_000 or m < 10),
        }
    dates = sorted(f["price_date"] for f in fiches if f.get("price_date"))
    if dates:
        res["dates"] = {"plus_ancienne": dates[0], "plus_recente": dates[-1]}
    marques = collections.Counter(f["brand"] for f in fiches if f.get("brand"))
    res["marques_distinctes"] = len(marques)
    res["top_marques"] = [m for m, _ in marques.most_common(4)]
    res["exemple"] = next((f["titre"][:70] for f in fiches if f.get("price_amount")), "")

    # Une boutique de montres, ou un bazar ? Une liste de marques ne suffit pas :
    # elle rejetait A Collected Man (F.P. Journe, Lange) et Watches.com (G-Shock)
    # parce qu'ils ne vendent pas les 19 marques de luxe qu'on avait listees.
    # On teste donc le VOCABULAIRE horloger, present quelle que soit la gamme.
    MOTS = ("watch", "montre", "automatic", "quartz", "chronograph", "chronographe",
            "dial", "cadran", "bezel", "lunette", "gmt", "diver", "wristwatch",
            "caliber", "calibre", "movement", "mouvement", "perpetual", "tourbillon",
            "seiko", "rolex", "omega", "ref.", "mm ")
    pertinentes = sum(
        1 for f in fiches
        if any(m in f" {f.get('brand') or ''} {f.get('titre') or ''} ".lower() for m in MOTS))
    res["part_horlogere"] = round(100 * pertinentes / n) if n else 0

    cle = res["completude"]
    if res["part_horlogere"] < 20:
        res["verdict"] = "hors perimetre (peu de montres)"
    elif cle["price_amount"] >= 90 and cle["reference"] >= 40:
        res["verdict"] = "SOLIDE"
    elif cle["price_amount"] >= 90:
        res["verdict"] = "exploitable (reference faible)"
    else:
        res["verdict"] = "prix incomplets"
    return res


def main() -> None:
    if not SONDE.exists():
        sys.exit("lance d'abord : python moteur/sonde.py --registre")
    mesures = json.load(SONDE.open(encoding="utf-8"))["mesures"]
    cibles = [(m["source"], m["url"], m["endpoint"]) for m in mesures
              if m.get("endpoint") and ("Shopify" in m["endpoint"] or "Woo" in m["endpoint"])]

    print(f"Verification reelle de {len(cibles)} boutiques a endpoint standard.")
    print("On telecharge de vrais produits et on mesure ce qu'on obtiendrait.\n")

    from concurrent.futures import ThreadPoolExecutor, as_completed
    resultats = []
    with ThreadPoolExecutor(max_workers=PARALLELE) as pool:
        futurs = {pool.submit(verifie, n, u, p): n for n, u, p in cibles}
        for f in as_completed(futurs):
            try:
                resultats.append(f.result())
            except Exception as e:
                resultats.append({"source": futurs[f], "verdict": f"erreur {type(e).__name__}"})

    ordre = {"SOLIDE": 0, "exploitable (reference faible)": 1, "prix incomplets": 2,
             "hors perimetre (peu de montres)": 3, "aucune donnee extraite": 4}
    resultats.sort(key=lambda r: (ordre.get(r.get("verdict"), 9),
                                  -r.get("fiches_extraites", 0)))

    print(f"{'SOURCE':<28}{'FICHES':>7}  {'VERDICT':<32}{'PRIX':>6}{'REF':>6}{'DATE':>6}")
    print("-" * 92)
    for r in resultats:
        c = r.get("completude", {})
        print(f"{r['source'][:27]:<28}{r.get('fiches_extraites', 0):>7}  "
              f"{r.get('verdict', '?'):<32}"
              f"{c.get('price_amount', 0):>5}%{c.get('reference', 0):>5}%"
              f"{c.get('price_date', 0):>5}%")

    SORTIE.write_text(json.dumps(
        {"date": dt.datetime.now().isoformat(timespec="seconds"), "sources": resultats},
        ensure_ascii=False, indent=1), encoding="utf-8")

    solides = [r for r in resultats if r.get("verdict") == "SOLIDE"]
    total = sum(r.get("fiches_extraites", 0) for r in resultats)
    print(f"\n{len(solides)} boutiques SOLIDES · {total} fiches reellement extraites")
    print(f"resultats : data/{SORTIE.name}")


if __name__ == "__main__":
    main()
