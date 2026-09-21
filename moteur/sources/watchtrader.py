"""Watchtrader — marchand britannique. Le schema le plus propre du dossier.

C'est la seule source ou la reference constructeur est un CHAMP DEDIE, renseigne
sur 4 092 fiches sur 4 092 et vrai sur 99,8 %. Partout ailleurs il faut la
deviner dans un titre ou une description.

Acces : WooCommerce, API Store publique. `robots.txt` n'interdit pas `/wp-json/`.
Deux appels, et c'est le second qui compte :

    /wp-json/wc/store/products?per_page=100&page=N                 601 en vitrine
    /wp-json/wc/store/products?per_page=100&page=N&stock_status=outofstock
                                                                 3 491 vendues

Sans le second, on ne verrait que le stock courant et on manquerait 85 % de la
source. Les fiches vendues CONSERVENT leur prix, ce qui en fait du prix demande
au moment du retrait — l'equivalent de ce que donne Craft & Tailored.

Les attributs de taxonomie WooCommerce portent, tous a 100 % : Brand, Model,
Reference, Condition, Box, Papers, Case Material — et l'annee de fabrication
('Watch Year') a 97,2 %, de 1940 a 2026.

RESERVE : le site a ete refait en fevrier 2025 et ses dates ne remontent pas
au-dela. Dix-huit mois de profondeur, et c'est une date de mise en ligne, pas
de vente.
Reconnaissance du 28/08/2026.
"""
from __future__ import annotations

import json
import re

from schema import parse_money, price_point, reference_dans
from utils import get

SOURCE = {
    "id": "watchtrader",
    "name": "Watchtrader",
    "type": "dealer",
    "price_nature": "asking",
    "access": "WooCommerce Store API (/wp-json/wc/store/products)",
    "robots": "OK — /wp-json/ n'est pas interdit, verifie le 28/08/2026",
    "corpus_horloger": True,
    "reserve": "site refait en 02/2025 : 18 mois de profondeur, date de mise en ligne",
}

BASE = "https://www.watchtrader.co.uk/wp-json/wc/store/products"
PAR_PAGE = 100
_BALISES = re.compile(r"<[^>]+>")


def _attribut(produit: dict, nom: str):
    """La valeur d'un attribut de taxonomie WooCommerce, par son libelle."""
    for a in produit.get("attributes") or []:
        if str(a.get("name", "")).strip().lower() == nom.lower():
            termes = [t.get("name") for t in (a.get("terms") or []) if t.get("name")]
            if termes:
                return " ".join(termes).strip()
    return None


def _annee(valeur):
    trouve = re.search(r"\b(19\d{2}|20[0-2]\d)\b", str(valeur or ""))
    return int(trouve.group(1)) if trouve else None


def fiche(produit: dict) -> dict | None:
    """Un produit WooCommerce -> un enregistrement normalise."""
    prix = (produit.get("prices") or {})
    montant, _ = parse_money(prix.get("price"))
    # WooCommerce exprime ses montants en centimes quand `currency_minor_unit`
    # vaut 2 : 985000 est 9 850,00 £, pas 985 000 £.
    unite = prix.get("currency_minor_unit")
    if montant and unite:
        montant = montant / (10 ** int(unite))
    if not montant:
        return None

    titre = produit.get("name")
    disponible = not any("outofstock" in str(c) for c in (produit.get("class_list") or []))
    reference = _attribut(produit, "Reference")
    if reference and not re.search(r"\d", reference):
        reference = None
    if not reference:
        reference = reference_dans(titre) or reference_dans(
            _BALISES.sub(" ", produit.get("description") or "")[:1500])
        provenance = "extrait_titre" if reference else None
    else:
        provenance = "champ_dedie"

    return price_point(
        source_id=SOURCE["id"], source_type=SOURCE["type"],
        source_url=produit.get("permalink"),
        external_id=str(produit.get("id")),
        # Une fiche epuisee chez un marchand de pieces uniques est une montre
        # partie, et elle garde son prix affiche.
        price_nature="asking" if disponible else "sold",
        price_nature_provenance="deduite_statut",
        listing_status="active" if disponible else "sold",
        price_amount=montant,
        price_currency=prix.get("currency_code") or "GBP",
        # La source ne date pas ses ventes ; `date_created` est la mise en ligne.
        price_date=produit.get("date_created"),
        brand=_attribut(produit, "Brand"),
        model=_attribut(produit, "Model"),
        reference=reference, reference_provenance=provenance,
        year=_annee(_attribut(produit, "Watch Year")),
        case_material=_attribut(produit, "Case Material"),
        condition=_attribut(produit, "Condition"),
        title=titre,
        seller="Watchtrader",
    )


def lots_du_brut(entrees: list) -> list[tuple]:
    """Chaque produit d'une collecte deja stockee."""
    trouves = []
    for entree in entrees:
        try:
            produits = json.loads(entree.get("payload", ""))
        except (json.JSONDecodeError, AttributeError):
            continue
        if isinstance(produits, list):
            trouves.extend((p,) for p in produits if isinstance(p, dict))
    return trouves


def collect(cap: int = 8000):
    raw: list[dict] = []
    journal: list[str] = []
    records: list[dict] = []
    vus: set[str] = set()

    # Le stock courant PUIS les fiches epuisees : sans le second passage, on ne
    # voit que 601 montres sur 4 092.
    for statut, libelle in ((None, "en vitrine"), ("outofstock", "vendues")):
        page = 1
        avant = len(records)
        while len(records) < cap:
            params = {"per_page": PAR_PAGE, "page": page}
            if statut:
                params["stock_status"] = statut
            try:
                resp = get(BASE, params=params, pause=1.0)
            except Exception as exc:
                journal.append(f"{libelle} p{page}: {type(exc).__name__}")
                break
            raw.append({"url": resp.url, "status": resp.status_code, "payload": resp.text})
            if resp.status_code != 200:
                journal.append(f"{libelle} p{page}: HTTP {resp.status_code}")
                break
            try:
                produits = json.loads(resp.text)
            except json.JSONDecodeError:
                break
            if not produits:
                break

            for produit in produits:
                enregistrement = fiche(produit)
                if enregistrement is None or enregistrement["external_id"] in vus:
                    continue
                vus.add(enregistrement["external_id"])
                records.append(enregistrement)

            if len(produits) < PAR_PAGE:
                break
            page += 1
        journal.append(f"{libelle} : {len(records) - avant} fiches")

    if len(records) >= cap:
        journal.append(f"TRONQUE: plafond de {cap} atteint — il reste des donnees a prendre")
    return raw, records, journal
