"""Christie's — maison de ventes. Prix REALISES avec date : le socle historique.

Acces : API JSON interne du site (discoverywebsite). Deux appels enchaines —
le calendrier des ventes passees, puis les lots de chaque vente montres.
"""
from __future__ import annotations

import json
import re

from schema import parse_money, price_point
from utils import get

SOURCE = {
    "id": "christies",
    "name": "Christie's",
    "type": "auction",
    "price_nature": "realised",
    "access": "API JSON interne (discoverywebsite)",
    "robots": "OK — les Disallow visent */search, */AjaxPages… ; 'lotsearch' n'est pas '/search'",
}

COMPONENT = "e7d92272-7bcc-4dba-ae5b-28e4f3729ae8"
CALENDAR = "https://www.christies.com/api/discoverywebsite/auctioncalendar/auctionresults"
LOTSEARCH = "https://www.christies.com/api/discoverywebsite/auctionpages/lotsearch"

YEARS = (2026, 2025, 2024)
MONTHS = (3, 6, 9, 12)
PAGES_PAR_VENTE = 2
TAILLE_PAGE = 84


def _deep_find(obj, key):
    """La liste utile est emboitee a une profondeur variable selon l'endpoint."""
    if isinstance(obj, dict):
        if isinstance(obj.get(key), list) and obj[key]:
            return obj[key]
        for value in obj.values():
            found = _deep_find(value, key)
            if found:
                return found
    elif isinstance(obj, list):
        for value in obj:
            found = _deep_find(value, key)
            if found:
                return found
    return None


def _split_estimate(text):
    """'USD 100,000 - 200,000' -> (100000.0, 200000.0)"""
    if not text:
        return None, None
    parts = re.split(r"\s*[-–]\s*", str(text))
    low, _ = parse_money(parts[0])
    high, _ = parse_money(parts[1]) if len(parts) > 1 else (None, None)
    return low, high


def _brand_from_title(title):
    """Heuristique : Christie's titre ses lots 'ROLEX, A STAINLESS STEEL...'.

    Le fabricant est le segment en capitales avant la premiere virgule. On ne
    devine rien au-dela : mieux vaut un champ vide qu'une marque inventee.
    """
    if not title:
        return None
    head = str(title).split(",")[0].strip()
    return head.title() if 0 < len(head) <= 30 and head.isupper() else None


def _reference_from_title(title):
    """'... REF. 116509, NO. 1/1' -> '116509'"""
    if not title:
        return None
    match = re.search(r"\bREF(?:\.|ERENCE)?\s*([A-Z0-9][A-Z0-9./-]{2,15})", str(title), re.I)
    return match.group(1).rstrip(".,") if match else None


def _ventes_montres(raw, journal):
    ventes = []
    for year in YEARS:
        for month in MONTHS:
            params = {"language": "en", "month": month, "year": year, "component": COMPONENT}
            resp = get(CALENDAR, params=params, pause=1.0)
            raw.append({"url": resp.url, "status": resp.status_code, "payload": resp.text[:400_000]})
            if resp.status_code != 200:
                journal.append(f"calendrier {month}/{year}: HTTP {resp.status_code}")
                continue
            try:
                events = _deep_find(json.loads(resp.text), "events") or []
            except json.JSONDecodeError:
                journal.append(f"calendrier {month}/{year}: JSON illisible")
                continue
            for event in events:
                if not re.search(r"watch", str(event.get("title_txt", "")), re.I):
                    continue
                landing = event.get("landing_url", "")
                sale_id = re.search(r"SaleID=(\d+)", landing)
                sale_no = re.search(r"SaleNumber=(\d+)", landing)
                if sale_id and sale_no:
                    ventes.append({"titre": event.get("title_txt"), "sale_id": sale_id.group(1),
                                   "sale_number": sale_no.group(1), "annee": year})
    return ventes


def collect(cap: int = 800):
    raw: list[dict] = []
    journal: list[str] = []
    records: list[dict] = []

    ventes = _ventes_montres(raw, journal)
    journal.append(f"{len(ventes)} ventes montres reperees sur {YEARS}")

    for vente in ventes:
        if len(records) >= cap:
            break
        for page in range(1, PAGES_PAR_VENTE + 1):
            params = {"language": "en", "saleid": vente["sale_id"], "salenumber": vente["sale_number"],
                      "page": page, "pagesize": TAILLE_PAGE, "saletype": "Sale", "component": COMPONENT}
            resp = get(LOTSEARCH, params=params, pause=1.2)
            raw.append({"url": resp.url, "status": resp.status_code, "payload": resp.text[:400_000]})
            if resp.status_code != 200:
                journal.append(f"lots {vente['sale_number']} p{page}: HTTP {resp.status_code}")
                break
            try:
                lots = _deep_find(json.loads(resp.text), "lots") or []
            except json.JSONDecodeError:
                break
            if not lots:
                break

            for lot in lots:
                titre = lot.get("title_primary_txt")
                montant, devise = parse_money(lot.get("price_realised_txt"))
                bas, haut = _split_estimate(lot.get("estimate_txt"))
                records.append(price_point(
                    source_id=SOURCE["id"], source_type=SOURCE["type"],
                    source_url=lot.get("url") or vente["titre"],
                    external_id=f"{vente['sale_number']}-{lot.get('lot_id_txt')}",
                    price_nature="realised",
                    price_amount=montant, price_currency=devise,
                    price_date=lot.get("start_date"),
                    estimate_low=bas, estimate_high=haut,
                    brand=_brand_from_title(titre), reference=_reference_from_title(titre),
                    title=titre, seller="Christie's",
                ))
            if len(lots) < TAILLE_PAGE or len(records) >= cap:
                break

    return raw, records[:cap], journal
