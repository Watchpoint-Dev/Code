"""LiveAuctioneers — agregateur d'encheres. Prix REALISES datés (fenetre glissante).

Acces : le state Redux embarque dans la page (`window.__data`), via le guide
des prix. Pas de parametre interdit par robots (`pagenum=` est proscrit, `page=`
ne l'est pas).
"""
from __future__ import annotations

import json
import re

from watchpoint.schema import price_point
from watchpoint.commun.utils import get

SOURCE = {
    "id": "liveauctioneers",
    "name": "LiveAuctioneers",
    "type": "aggregator",
    "price_nature": "realised",
    "access": "window.__data (price guide)",
    "robots": "OK — robots interdit 'pagenum=', on utilise 'page=' ; /price-guide/ non liste",
    # 02/09/2026 — LE BLOCAGE ETAIT LE NOTRE. Le site repondait 847 octets de
    # challenge Incapsula a notre faux UA Chrome ; il rend 318 Ko a un ClaudeBot
    # honnete. L'anti-bot visait le navigateur simule, pas nous.
    #
    # La source reste pourtant hors d'atteinte, pour une autre raison : son
    # archive de resultats ne se parcourt que par `/search/?`, que son propre
    # robots.txt interdit. Le chemin autorise — /c/watches/1246/?status=archive —
    # rend 13 lots prixes sur 14, sans page suivante. Accessible n'est pas
    # collectable.
    #
    # Ancienne note (09/08/2026) : la source marchait le 01/08 (48 lots). Elle
    # bascule donc sur la liste "a negocier" — on ne contourne pas un anti-bot.
    "statut": "ACCESSIBLE mais non paginable — voir la note du 02/09/2026",
}

MARQUEUR_ANTIBOT = "_Incapsula_Resource"

BASE = "https://www.liveauctioneers.com/price-guide/watches/"
PAGES = range(1, 7)


def _extraire_blob(html):
    """Isole l'objet JSON de window.__data par comptage d'accolades."""
    match = re.search(r"window\.__data\s*=\s*(\{.*)", html, re.S)
    if not match:
        return None
    blob = re.sub(r"\bundefined\b", "null", match.group(1))
    profondeur, fin = 0, None
    for index, char in enumerate(blob):
        if char == "{":
            profondeur += 1
        elif char == "}":
            profondeur -= 1
            if profondeur == 0:
                fin = index + 1
                break
    if fin is None:
        return None
    try:
        return json.loads(blob[:fin])
    except json.JSONDecodeError:
        return None


def _trouver_items(obj):
    """Le dictionnaire des lots est stocke sous une cle 'byId'."""
    if isinstance(obj, dict):
        if isinstance(obj.get("byId"), dict) and obj["byId"]:
            return obj["byId"]
        for value in obj.values():
            found = _trouver_items(value)
            if found:
                return found
    elif isinstance(obj, list):
        for value in obj:
            found = _trouver_items(value)
            if found:
                return found
    return None


def collect(cap: int = 400):
    raw: list[dict] = []
    journal: list[str] = []
    records: list[dict] = []
    vus: set[str] = set()

    for page in PAGES:
        if len(records) >= cap:
            break
        resp = get(BASE, params={"page": page}, pause=1.5)
        raw.append({"url": resp.url, "status": resp.status_code, "payload": resp.text})
        if resp.status_code != 200:
            journal.append(f"page {page}: HTTP {resp.status_code}")
            break
        if MARQUEUR_ANTIBOT in resp.text or len(resp.text) < 5_000:
            journal.append(f"page {page}: BLOQUE par l'anti-bot Incapsula "
                           f"({len(resp.text)} octets) — passer par la negociation")
            break

        data = _extraire_blob(resp.text)
        if data is None:
            journal.append(f"page {page}: window.__data introuvable")
            break
        items = _trouver_items(data) or {}

        nouveaux = 0
        for cle, item in items.items():
            if not isinstance(item, dict) or not item.get("salePrice"):
                continue
            identifiant = str(item.get("itemId") or cle)
            if identifiant in vus:
                continue
            vus.add(identifiant)
            nouveaux += 1
            records.append(price_point(
                source_id=SOURCE["id"], source_type=SOURCE["type"],
                source_url=item.get("itemUrl") or BASE,
                external_id=identifiant,
                price_nature="realised",
                # L'endpoint ne rend que des lots vendus (`salePrice` present).
                price_nature_provenance="deduite_statut",
                listing_status="sold",
                price_amount=float(item["salePrice"]),
                price_currency=item.get("currency"),
                price_date=item.get("saleStartTs"),
                title=item.get("title"),
                seller=item.get("sellerName"),
            ))
        journal.append(f"page {page}: {nouveaux} lots vendus")
        if nouveaux == 0:
            break

    # Un plafond atteint = collecte partielle. Le dire, sinon le chiffre passe
    # pour un total alors qu'il est un plancher.
    if len(records) >= cap:
        journal.append(f"TRONQUE: plafond de {cap} atteint — il reste des donnees a prendre")
    return raw, records[:cap], journal
