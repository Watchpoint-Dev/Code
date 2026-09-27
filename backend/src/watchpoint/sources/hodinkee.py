"""Hodinkee Shop — l'archive du pre-owned. 18 807 montres, toutes vendues.

C'est un GISEMENT, pas un flux : la boutique pre-owned s'est arretee en octobre
2024. Rien n'est publie apres cette date. On l'aspire une fois, elle ne bougera
plus — ce qui en fait une des rares sources dont la collecte est definitive.

18 946 fiches au total, dont 18 807 de type 'Watches : ...'. La reference vit
dans le TITRE et y est vraie sur 96,5 % des fiches. Le `sku` ressemble a une
reference mais n'en est pas une : c'est un code marchand `10-21-ROL-Q8CGDG`.

`available=false` sur 18 806 fiches sur 18 807 : une seule montre reste en
vitrine. Chez un marchand de pieces uniques, cela vaut prix VENDU — avec la
reserve habituelle qu'une fiche peut aussi avoir ete retiree.

Les 1 565 articles de la marque maison (bracelets, accessoires) sont ecartes par
le filtre, leur `product_type` ne portant pas 'Watches'.
Reconnaissance du 28/08/2026.
"""
from __future__ import annotations

from . import _shopify

SOURCE = {
    "id": "hodinkee",
    "name": "Hodinkee Shop",
    "type": "dealer",
    "price_nature": "sold",
    "access": "Shopify products.json (currency=USD&country=US)",
    "robots": "OK — products.json non interdit",
    "corpus_horloger": True,
    "reserve": "archive figee : plus aucune fiche publiee apres octobre 2024",
}


# Les reglages de NORMALISATION, en un seul endroit. Le rejeu hors ligne tenait
# sa propre copie dans collecte/rejoue.py : les deux ont diverge, et les tags de
# nature comme le SKU-reference ne franchissaient pas le rejeu. Une donnee
# dupliquee finit toujours par se contredire.
NORMALISATION = dict(devise="USD", domaine="shop.hodinkee.com", etat="preowned")


def collect(cap: int = 20000):
    return _shopify.collecte(SOURCE, cap, pays="US", **NORMALISATION)
