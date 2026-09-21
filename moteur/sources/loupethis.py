"""Loupe This — encheres de montres en ligne. La seule source qui publie LES DEUX.

4 268 lots depuis juillet 2021, et une particularite qu'aucune autre source du
dossier n'offre : l'API expose a la fois le MARTEAU et le prix FRAIS INCLUS.

    current_bid_price_cents   l'enchere gagnante, marteau nu
    sold_price_cents          le meme, majore de buyers_premium_percent

La relation a ete verifiee sur 243 lots clos : `sold == round(bid x 1,10)`, sans
exception. On charge donc le MARTEAU — c'est la valeur la plus comparable avec
Artcurial et Lyon & Turnbull — et le drapeau de frais dit que les frais n'y sont
pas.

Acces : API JSON:API publique, sans authentification.

    https://api.loupethis.com/api/v1/auctions?page=N

PIEGE : toute URL contenant un crochet, meme encode `%5B`, est silencieusement
redirigee vers la racine de l'API qui repond le corps `"ok"`. Le parametre
`page[size]` de la norme JSON:API est donc inutilisable, et on reste bloque a
25 lots par page — d'ou 171 requetes pour tout l'historique.

RESERVES : les invendus ne sont pas publies (243 lots clos sur 243 ont un prix
de vente). La plateforme fonctionne majoritairement sans prix de reserve, donc
le biais est probablement faible, mais il n'est pas mesurable. Et l'estimation
n'est pas dans l'API : elle n'existe que dans le HTML de la page.

Reconnaissance du 28/08/2026.
"""
from __future__ import annotations

import datetime as dt
import json

from schema import price_point, reference_dans, reference_libre
from utils import get

SOURCE = {
    "id": "loupethis",
    "name": "Loupe This",
    "type": "auction",
    "price_nature": "realised",
    "access": "API JSON:API publique api.loupethis.com/api/v1/auctions",
    "robots": "OK — 'Disallow:' vide, rien n'est interdit",
    "corpus_horloger": True,
    "reserve": "invendus non publies ; estimation absente de l'API",
}

BASE = "https://api.loupethis.com/api/v1/auctions"


def _relation(lot: dict, nom: str, inclus: dict):
    """JSON:API separe les objets lies : on les recolle par leur identifiant."""
    lien = ((lot.get("relationships") or {}).get(nom) or {}).get("data")
    if not isinstance(lien, dict):
        return {}
    return inclus.get((lien.get("type"), lien.get("id")), {})


def fiche(lot: dict, inclus: dict | None = None) -> dict | None:
    inclus = inclus or {}
    attributs = lot.get("attributes") or lot
    marteau = attributs.get("current_bid_price_cents")
    fin = attributs.get("ends_at")
    if not marteau or not fin:
        return None
    # Une enchere qui n'est pas close n'est pas une transaction : son montant
    # est l'enchere du moment, pas un prix de vente. 22 lots etaient dans ce cas.
    if str(fin)[:10] > dt.date.today().isoformat():
        return None

    titre = attributs.get("title") or attributs.get("name")
    marque = (_relation(lot, "brand", inclus).get("attributes") or {}).get("name")
    reference = reference_dans(titre) or reference_libre(titre)

    return price_point(
        source_id=SOURCE["id"], source_type=SOURCE["type"],
        source_url=f"https://loupethis.com/auctions/{attributs.get('slug') or lot.get('id')}",
        external_id=str(lot.get("id")),
        price_nature="realised",
        price_nature_provenance="champ_dedie",
        listing_status="sold",
        # On charge le MARTEAU : `sold_price_cents` est le meme montant majore
        # de 10 %, relation verifiee sur 243 lots sans exception.
        price_includes_premium=False,
        price_amount=float(marteau) / 100,
        price_currency="USD",
        price_date=fin,
        brand=marque,
        reference=reference,
        reference_provenance="extrait_titre" if reference else None,
        title=titre,
        seller="Loupe This",
    )


def _inclus(charge: dict) -> dict:
    return {(x.get("type"), x.get("id")): x for x in (charge.get("included") or [])
            if isinstance(x, dict)}


def lots_du_brut(entrees: list) -> list[tuple]:
    trouves = []
    for entree in entrees:
        try:
            charge = json.loads(entree.get("payload", ""))
        except (json.JSONDecodeError, AttributeError):
            continue
        inclus = _inclus(charge)
        for lot in charge.get("data") or []:
            if isinstance(lot, dict):
                trouves.append((lot, inclus))
    return trouves


def collect(cap: int = 6000):
    raw: list[dict] = []
    journal: list[str] = []
    records: list[dict] = []
    page = 1
    total = None

    while len(records) < cap:
        try:
            resp = get(BASE, params={"page": page}, pause=1.0)
        except Exception as exc:
            journal.append(f"page {page}: {type(exc).__name__}")
            break
        raw.append({"url": resp.url, "status": resp.status_code, "payload": resp.text})
        if resp.status_code != 200:
            journal.append(f"page {page}: HTTP {resp.status_code}")
            break
        try:
            charge = json.loads(resp.text)
        except json.JSONDecodeError:
            break
        lots = charge.get("data") or []
        if not lots:
            break
        if total is None:
            total = ((charge.get("meta") or {}).get("pagination") or {}).get("total_count")
            journal.append(f"{total} encheres annoncees par l'API")

        inclus = _inclus(charge)
        for lot in lots:
            enregistrement = fiche(lot, inclus)
            if enregistrement is not None:
                records.append(enregistrement)
        page += 1

    journal.append(f"{page - 1} pages lues, 25 lots par page (les crochets JSON:API "
                   f"sont rediriges, `page[size]` est inutilisable)")
    if len(records) >= cap:
        journal.append(f"TRONQUE: plafond de {cap} atteint — il reste des donnees a prendre")
    return raw, records, journal
