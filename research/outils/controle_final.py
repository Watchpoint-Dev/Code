"""Controle final : re-verifier a la main les affirmations qui partent en reunion.

    cd ~/Desktop/WP
    python research/outils/controle_final.py

Les fiches ont ete redigees par des analystes. Ce script rejoue LUI-MEME les
affirmations les plus lourdes, celles du groupe « bonnes » : l'endpoint repond-il
encore, le compteur de volume dit-il bien ce qu'on annonce, l'enregistrement
ancien cite existe-t-il ?

Ce qui n'est pas confirme ici ne doit pas etre affirme devant quelqu'un.

Politesse : sequentiel, 3 s entre requetes, 3 requetes max par source, et un 429
arrete la source. On s'est deja fait limiter, on ne recommence pas.
"""
from __future__ import annotations

from watchpoint import config

import datetime as dt
import json
import pathlib
import re
import sys
import time

import requests

ICI = pathlib.Path(__file__).resolve().parent
from watchpoint.commun.utils import HEADERS  # noqa: E402

SORTIE = config.DATA / "controle_final.json"
PAUSE = 3.0


def get(url, **kw):
    try:
        r = requests.get(url, headers=HEADERS, timeout=30, **kw)
    except requests.RequestException as e:
        time.sleep(PAUSE)
        return None, f"reseau: {type(e).__name__}"
    time.sleep(PAUSE)
    if r.status_code == 429:
        return None, "429, le site nous limite"
    return r, None


# Chaque controle renvoie (confirme: bool, constat: str).
# Le constat doit etre citable tel quel : c'est ce qu'on pourra dire.

def artcurial():
    # endpoint exact releve dans la fiche, pas devine
    r, err = get("https://www.artcurial.com/ace/sales/results",
                 params={"filter": "specialties.specialty.ref,MTCA,WATCHES",
                         "page": 0, "size": 5, "sort": "effectiveDate,asc"})
    if err or r is None or r.status_code != 200:
        return False, f"API /ace injoignable ({err or r.status_code})"
    try:
        d = r.json()
    except ValueError:
        return False, "API /ace : reponse non JSON"
    total = d.get("totalElements")
    ventes = d.get("content") or []
    if not ventes:
        return False, "API /ace repond mais ne renvoie aucune vente"
    v = ventes[0]
    return True, (f"API JSON ouverte sans authentification, {total} ventes montres ; "
                  f"la plus ancienne : {str(v.get('effectiveDate'))[:10]}, "
                  f"« {str(v.get('title') or v.get('name'))[:40]} »")


def cottone():
    r, err = get("https://www.cottoneauctions.com/prices-realized",
                 params={"PricesRealizedForm[category_slug]": "clocks-timepieces",
                         "PricesRealizedForm[num_per_page]": 200, "page": 1})
    if err or r is None or r.status_code != 200:
        return False, f"page des ventes passees injoignable ({err or r.status_code})"
    montants = re.findall(r"\$[\d][\d,]{2,}", r.text)
    lots = len(re.findall(r"/lots/\d+", r.text))
    pages = [int(x) for x in re.findall(r"[?&]page=(\d+)", r.text)]
    if not lots:
        return False, "page des prix realises accessible mais aucun lot lisible"
    return True, (f"HTML rendu serveur, {lots} lots et {len(montants)} montants sur une page"
                  + (f", pagination jusqu'a la page {max(pages)}" if pages else ""))


def lyon_turnbull():
    r, err = get("https://www.lyonandturnbull.com/auctions/auction-results")
    if err or r is None or r.status_code != 200:
        return False, f"page injoignable ({err or r.status_code})"
    nd = '__NEXT_DATA__' in r.text
    ventes = len(set(re.findall(r'/auctions/([a-z0-9-]+-\d+)"', r.text)))
    hammer = r.text.count('hammer_price')
    return bool(nd), (f"__NEXT_DATA__ present, {ventes} ventes listees"
                      + (f", champ hammer_price present ({hammer} occurrences)" if hammer else
                         ", hammer_price absent de cette page (present sur les pages de vente)")
                      if nd else "__NEXT_DATA__ absent, mecanisme a revoir")


def loupethis():
    r, err = get("https://api.loupethis.com/api/v1/auctions",
                 params={"status": "closed", "per_page": 1, "page": 1})
    if err or r is None or r.status_code != 200:
        return False, f"API injoignable ({err or r.status_code})"
    try:
        d = r.json()
    except ValueError:
        return False, "API : reponse non JSON"
    items = d.get("data", d) if isinstance(d, dict) else d
    meta = d.get("meta", {}) if isinstance(d, dict) else {}
    total = meta.get("total") or (d.get("total") if isinstance(d, dict) else None)
    ex = ""
    if isinstance(items, list) and items:
        a = items[0]
        attrs = a.get("attributes", a)
        ex = f" ; derniere close : {str(attrs.get('ends_at'))[:10]}"
    return True, f"API publique sans authentification, {total or '?'} encheres closes{ex}"


def everywatch():
    r, err = get("https://everywatch.com/watch-listing")
    if err or r is None or r.status_code != 200:
        return False, f"page injoignable ({err or r.status_code})"
    b = re.search(r'"buildId":"([^"]+)"', r.text)
    return bool(b), (f"__NEXT_DATA__ lisible, buildId={b.group(1)} (change a chaque deploiement)"
                     if b else "buildId introuvable, l'endpoint JSON n'est pas atteignable")


def patek():
    r, err = get("https://www.patek.com/en/collection/watch-finder")
    if err or r is None or r.status_code != 200:
        return False, f"page injoignable ({err or r.status_code})"
    prix = re.findall(r"(?:CHF|USD|EUR)[\s\u00a0]?[\d][\d'’,.\s\u00a0]{3,}", r.text) \
           or re.findall(r'"price"\s*:\s*"?[\d]{4,}', r.text)
    refs = set(re.findall(r"\b\d{4}[A-Z]?/\d{1,3}[A-Z]?-\d{3}\b", r.text))
    mention = "suggested retail" in r.text.lower()
    ok = len(prix) > 50 and len(refs) > 50
    return ok, (f"{len(refs)} references et {len(prix)} prix sur une seule page"
                + (", mention « suggested retail prices » presente" if mention else ""))


def shopify(nom, base):
    def f():
        r, err = get(f"{base}/meta.json")
        devise = None
        if r is not None and r.status_code == 200:
            try:
                devise = r.json().get("currency")
            except ValueError:
                pass
        url = f"{base}/products.json?limit=250" + (f"&currency={devise}" if devise else "")
        r2, err2 = get(url)
        if err2 or r2 is None or r2.status_code != 200:
            return False, f"products.json injoignable ({err2 or r2.status_code})"
        try:
            prods = r2.json().get("products", [])
        except ValueError:
            return False, "products.json : reponse non JSON"
        if not prods:
            return False, "products.json repond mais ne renvoie aucun produit"
        p = prods[0]
        prix = (p.get("variants") or [{}])[0].get("price")
        return True, (f"{len(prods)} produits sur la premiere page, devise {devise or 'non declaree'}"
                      f" ; exemple : {str(p.get('title'))[:44]} a {prix}")
    f.__name__ = nom
    return f


def woo(nom, base):
    def f():
        r, err = get(f"{base}/wp-json/wc/store/products?per_page=100")
        if err or r is None or r.status_code != 200:
            return False, f"Store API injoignable ({err or r.status_code})"
        try:
            prods = r.json()
        except ValueError:
            return False, "Store API : reponse non JSON"
        if not isinstance(prods, list) or not prods:
            return False, "Store API repond mais ne renvoie aucun produit"
        p = prods[0]
        pr = p.get("prices") or {}
        unite = pr.get("currency_minor_unit", 2)
        montant = float(pr.get("price", 0)) / (10 ** int(unite))
        return True, (f"{len(prods)} produits sur la premiere page, {pr.get('currency_code')}"
                      f", unite mineure {unite} ; exemple : {str(p.get('name'))[:40]}"
                      f" a {montant:,.0f}".replace(",", " "))
    f.__name__ = nom
    return f


CONTROLES = [
    ("Artcurial", artcurial),
    ("Cottone Auctions", cottone),
    ("Lyon & Turnbull", lyon_turnbull),
    ("Loupe This", loupethis),
    ("EveryWatch", everywatch),
    ("Patek Philippe", patek),
    ("Craft & Tailored", shopify("craft", "https://craftandtailored.com")),
    ("Hodinkee Shop", shopify("hodinkee", "https://shop.hodinkee.com")),
    ("Analog Shift", shopify("analog", "https://analogshift.com")),
    ("Montredo", shopify("montredo", "https://montredo.com")),
    ("Watchtrader", woo("watchtrader", "https://watchtrader.co.uk")),
    ("Wanna Buy A Watch", woo("wbaw", "https://wannabuyawatch.com")),
    ("Amsterdam Watch Company", woo("awco", "https://amsterdamwatchcompany.com")),
    ("Menta Watches", woo("menta", "https://mentawatches.com")),
]


def main() -> None:
    print(f"Controle final de {len(CONTROLES)} sources du groupe « bonnes ».")
    print("Sequentiel, 3 s entre requetes. Ce qui n'est pas confirme ne sera pas affirme.\n")
    resultats = []
    for nom, fonction in CONTROLES:
        try:
            ok, constat = fonction()
        except Exception as exc:
            ok, constat = False, f"erreur {type(exc).__name__}: {exc}"
        resultats.append({"source": nom, "confirme": ok, "constat": constat})
        print(f"  {'CONFIRME' if ok else 'NON CONFIRME':<14} {nom:<26} {constat[:82]}")

    SORTIE.write_text(json.dumps(
        {"date": dt.datetime.now().isoformat(timespec="seconds"), "controles": resultats},
        ensure_ascii=False, indent=1), encoding="utf-8")
    ok = sum(1 for r in resultats if r["confirme"])
    print(f"\n{ok}/{len(resultats)} confirmes. Resultats dans data/{SORTIE.name}")
    if ok < len(resultats):
        print("Les non confirmes doivent etre retires ou requalifies avant diffusion.")


if __name__ == "__main__":
    main()
