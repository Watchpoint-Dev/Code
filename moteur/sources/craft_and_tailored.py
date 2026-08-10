"""Craft & Tailored — marchand. Prix DEMANDES, avec date de mise en ligne.

Acces : endpoint public Shopify `products.json`. C'est le pattern repetable —
le meme adaptateur rebranche n'importe quelle boutique Shopify en changant le
domaine (cf. RAPPORT_FINAL_sourcing §3).
"""
from __future__ import annotations

import json
import re

from schema import parse_money, price_point
from utils import get

SOURCE = {
    "id": "craft_and_tailored",
    "name": "Craft & Tailored",
    "type": "dealer",
    "price_nature": "asking",
    "access": "Shopify products.json",
    "robots": "OK — 'Allow: /' ; les restrictions Shopify visent le checkout, pas le catalogue",
}

BASE = "https://craftandtailored.com/products.json"
PAR_PAGE = 250
# Devise canonique de la boutique, verifiee sur /meta.json ("currency":"USD",
# Los Angeles). C'est elle qu'on impose a chaque requete — cf. commentaire dans collect().
DEVISE = "USD"


def _reference_from_title(title):
    """'1969 Rolex Daytona (Ref. 6239) Black \"Paul Newman\" Dial' -> '6239'"""
    if not title:
        return None
    match = re.search(r"\bref\.?\s*([A-Z0-9][A-Z0-9./-]{2,15})", str(title), re.I)
    return match.group(1).rstrip(".,)") if match else None


def _year_from_title(title):
    """L'annee de production ouvre souvent le titre chez ce marchand."""
    match = re.match(r"\s*(19\d{2}|20[0-2]\d)\b", str(title or ""))
    return int(match.group(1)) if match else None


def collect(cap: int = 1000):
    raw: list[dict] = []
    journal: list[str] = []
    records: list[dict] = []

    page = 1
    while len(records) < cap:
        # `currency` est OBLIGATOIRE : nos en-tetes portent un Accept-Language, qui
        # declenche la localisation de devise Shopify. Sans ce parametre la boutique
        # renvoie des prix CONVERTIS (-17,8 % constate) qu'on etiquetterait USD a tort.
        # A reprendre tel quel pour toute autre boutique Shopify.
        resp = get(BASE, params={"limit": PAR_PAGE, "page": page, "currency": DEVISE},
                   pause=1.2)
        raw.append({"url": resp.url, "status": resp.status_code, "payload": resp.text})
        if resp.status_code != 200:
            journal.append(f"page {page}: HTTP {resp.status_code}")
            break
        try:
            produits = json.loads(resp.text).get("products", [])
        except json.JSONDecodeError:
            journal.append(f"page {page}: JSON illisible")
            break
        if not produits:
            break

        for produit in produits:
            variante = (produit.get("variants") or [{}])[0]
            montant, _ = parse_money(variante.get("price"))
            titre = produit.get("title")
            # Shopify ne renvoie pas la devise ici : la boutique facture en USD.
            records.append(price_point(
                source_id=SOURCE["id"], source_type=SOURCE["type"],
                source_url=f"https://craftandtailored.com/products/{produit.get('handle')}",
                external_id=str(produit.get("id")),
                price_nature="asking",
                price_amount=montant, price_currency=DEVISE,
                price_date=produit.get("published_at") or produit.get("created_at"),
                brand=produit.get("vendor"), title=titre,
                reference=_reference_from_title(titre), year=_year_from_title(titre),
                condition="preowned" if variante.get("available") else None,
                seller="Craft & Tailored",
            ))

        journal.append(f"page {page}: {len(produits)} produits")
        if len(produits) < PAR_PAGE:
            break
        page += 1

    # Un plafond atteint = collecte partielle. Le dire, sinon le chiffre passe
    # pour un total alors qu'il est un plancher.
    if len(records) >= cap:
        journal.append(f"TRONQUE: plafond de {cap} atteint — il reste des donnees a prendre")
    return raw, records[:cap], journal
