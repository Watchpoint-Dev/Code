"""Lyon & Turnbull — maison de ventes ecossaise. La seule qui publie ses INVENDUS.

C'est ce qui la rend precieuse malgre un volume modeste. Toutes nos autres
maisons ne servent que les lots vendus : la base heritait d'un biais de survie,
puisqu'on ne voyait jamais un prix que le marche a refuse. Ici `status` vaut
`sold` ou `unsold`, et les deux entrent — le vendu en prix realise, l'invendu en
estimation, avec son statut.

Acces : site Next.js. Chaque page de vente embarque un `__NEXT_DATA__` qui
contient le catalogue COMPLET de la vente, un objet par lot. Aucune pagination,
un seul GET par vente. Verifie a 411 lots sur une vente sans troncature.

Trois points a ne pas manquer :

  LE MARTEAU EST NU. `hammer_price` est le prix au marteau et `financeItem.premium`
  donne les frais a part (2 565 sur un marteau de 9 500, soit 27 %). C'est la
  meme convention qu'Artcurial, l'inverse de Christie's qui publie frais inclus.

  LA DATE DU SOUS-TITRE N'EST PAS LA DATE DE VENTE. Deux tiers des lots portent
  une mention 'made circa 2016' : c'est l'annee de FABRICATION. La date de vente
  est `session_date`, et elle seule.

  LA REFERENCE VIT DANS LE SOUS-TITRE, sous la forme 'Ref.116710BNLR'. Le titre,
  lui, porte la marque en tete : 'Rolex. A popular and desirable...'.

Fiche de preuve : preuves/fiches/lyonandturnbull.json
"""
from __future__ import annotations

import json
import re

from filtre import filtre
from schema import price_point, reference_dans
from utils import get

SOURCE = {
    "id": "lyonandturnbull",
    "name": "Lyon & Turnbull",
    "type": "auction",
    "price_nature": "realised",
    "access": "Next.js __NEXT_DATA__, catalogue complet par vente",
    "robots": "OK — verifie le 11/08/2026",
}

BASE = "https://www.lyonandturnbull.com"
INDEX = f"{BASE}/auctions/auction-results"

# Seules les ventes horlogeres. Mesure du 25/08/2026 : les 20 ventes de
# joaillerie du catalogue n'ont rendu que 36 montres pour 5 178 lots, soit
# 0,7 %. Vingt requetes pour cinq mille lignes de bijoux marquees a rejeter,
# ce n'est pas un compromis, c'est du bruit.
MOTS_VENTE = re.compile(r"watch", re.I)

_NEXT = re.compile(r'id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.S)
_REFERENCE = re.compile(r"\bref(?:erence)?\.?\s*:?\s*([A-Z0-9][A-Z0-9./-]{2,15})", re.I)
_DEVISES = {"£": "GBP", "$": "USD", "€": "EUR"}


def _next_data(texte: str) -> dict:
    trouve = _NEXT.search(texte)
    if not trouve:
        return {}
    try:
        return json.loads(trouve.group(1))
    except json.JSONDecodeError:
        return {}


def _langue(champ):
    """Les textes sont des dictionnaires par langue : {'en': '...'}."""
    if isinstance(champ, dict):
        return champ.get("en") or next(iter(champ.values()), None)
    return champ


def _sous_titre(lot) -> str:
    bloc = _langue(lot.get("dynamic_fields")) or {}
    if isinstance(bloc, dict):
        return str(bloc.get("sub_title") or "")
    return ""


def _ventes(raw, journal) -> list[dict]:
    try:
        resp = get(INDEX, pause=1.0)
    except Exception as exc:
        journal.append(f"index des ventes: {type(exc).__name__}")
        return []
    raw.append({"url": resp.url, "status": resp.status_code, "payload": resp.text})
    if resp.status_code != 200:
        journal.append(f"index des ventes: HTTP {resp.status_code}")
        return []

    toutes = (_next_data(resp.text).get("props", {})
              .get("pageProps", {}).get("auctionsListData") or [])
    retenues = [v for v in toutes
                if MOTS_VENTE.search(f"{v.get('title')} {v.get('department')}")]
    journal.append(f"{len(retenues)} ventes retenues sur {len(toutes)} passees")
    return retenues


def fiche(lot: dict, lien: str, categories: dict) -> dict | None:
    """Un lot Lyon & Turnbull -> un enregistrement normalise.

    `categories` traduit les category_uuid du lot en libelles ('Rings',
    'Wristwatches'...). La page de vente les publie dans props.pageProps.
    C'est la categorie que R0 lit : elle explique pourquoi une vente de montres
    contient aussi des bagues et des pendules.
    """
    titre = _langue(lot.get("title")) or ""
    sous_titre = _sous_titre(lot)
    texte = f"{titre} {sous_titre}".strip()
    if not texte:
        return None

    statut = (lot.get("status") or "").lower()
    marteau = lot.get("hammer_price")
    vendu = statut == "sold" and marteau and float(marteau) > 0

    reference = reference_dans(sous_titre) or reference_dans(titre)
    symbole = ((lot.get("auction") or {}).get("currency") or {}).get("symbol")

    return price_point(
        source_id=SOURCE["id"], source_type=SOURCE["type"],
        source_url=f"{BASE}{lien}?lot={lot.get('lot_no')}",
        external_id=str(lot.get("uuid")),
        # Un lot invendu n'est pas une transaction : il dit que le marche a
        # refuse ce prix. On le garde sous sa vraie nature.
        price_nature="realised" if vendu else "estimate",
        price_nature_provenance="champ_dedie",
        listing_status="sold" if vendu else "unsold",
        # hammer_price est le marteau NU ; financeItem.premium donne les frais
        # a part et n'est pas charge ici.
        price_includes_premium=False,
        price_amount=float(marteau) if vendu else lot.get("low"),
        price_currency=_DEVISES.get(symbole, "GBP"),
        # session_date, jamais l'annee du sous-titre : celle-ci est l'annee de
        # fabrication de la montre.
        price_date=lot.get("session_date") or (lot.get("auction") or {}).get("start_date"),
        estimate_low=lot.get("low"), estimate_high=lot.get("high"),
        brand=filtre().verdict(texte, "AUCTION").get("brand"),
        reference=reference,
        reference_provenance="extrait_titre" if reference else None,
        source_category=categories.get(lot.get("category_uuid")),
        title=texte[:300],
        seller="Lyon & Turnbull",
    )


def lots_du_brut(entrees: list) -> list[tuple]:
    """(lot, lien, categories) pour chaque lot d'une collecte deja stockee."""
    trouves = []
    for entree in entrees:
        donnee = _next_data(entree.get("payload", "") or "")
        pp = donnee.get("props", {}).get("pageProps", {})
        lots = pp.get("lots") or []
        # Le brut contient des collectes anterieures, ventes de joaillerie
        # comprises. On rejoue ce que la collecte ferait aujourd'hui : les
        # ventes horlogeres seulement.
        if not lots or not MOTS_VENTE.search(entree.get("url", "")):
            continue
        categories = {c.get("uuid"): c.get("name")
                      for c in (pp.get("categories") or []) if isinstance(c, dict)}
        lien = "/" + entree.get("url", "").split("/", 3)[-1] if "/" in entree.get("url", "") else ""
        for lot in lots:
            trouves.append((lot, lien, categories))
    return trouves


def collect(cap: int = 12000):
    raw: list[dict] = []
    journal: list[str] = []
    records: list[dict] = []
    tri = filtre()
    invendus = 0

    for vente in _ventes(raw, journal):
        if len(records) >= cap:
            break
        lien = vente.get("arrowLink") or ""
        if not lien.startswith("/"):
            continue
        try:
            resp = get(f"{BASE}{lien}", pause=1.2)
        except Exception as exc:
            journal.append(f"vente {vente.get('saleNumber')}: {type(exc).__name__}")
            continue
        raw.append({"url": resp.url, "status": resp.status_code, "payload": resp.text})
        if resp.status_code != 200:
            journal.append(f"vente {vente.get('saleNumber')}: HTTP {resp.status_code}")
            continue

        donnee = _next_data(resp.text).get("props", {}).get("pageProps", {})
        lots = donnee.get("lots") or []
        categories = {c.get("uuid"): c.get("name")
                      for c in (donnee.get("categories") or []) if isinstance(c, dict)}
        for lot in lots:
            if len(records) >= cap:
                break
            enregistrement = fiche(lot, lien, categories)
            if enregistrement is None:
                continue
            if enregistrement["listing_status"] == "unsold":
                invendus += 1
            records.append(enregistrement)

    if invendus:
        journal.append(f"{invendus} lots invendus conserves en nature 'estimate' "
                       f"— aucune autre source ne les publie")
    if len(records) >= cap:
        journal.append(f"TRONQUE: plafond de {cap} atteint — il reste des donnees a prendre")
    return raw, records, journal
