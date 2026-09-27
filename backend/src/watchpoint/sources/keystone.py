"""The Keystone — marchand haut de gamme. Le schema le mieux structure du lot.

5 081 fiches, dont 4 763 vendues (93,7 %). Huit ans de mise en ligne continue,
600 fiches par an, et surtout un bloc structure dans la description :

    <b>Reference</b>: 6239 <br> <b>Year</b>: 1968 <br> <b>Brand</b>: Rolex ...

La reference y est presente sur 91,5 % des fiches et vraie sur 84,9 %. Le meme
bloc livre l'annee de fabrication (81,3 %), la matiere, le cadran, le mouvement,
la completude du set. C'est la source la plus riche en specifications apres les
maisons de ventes.

PIEGE DEVISE CONFIRME ICI : `currency=EUR&country=FR` rend 283 184,95 la ou
`currency=USD&country=US` rend 325 000,00, soit -12,9 %. Le couple devise/pays
est obligatoire.

Le `sku` (214628) est un numero d'inventaire marchand, pas une reference.
Reconnaissance du 28/08/2026.
"""
from __future__ import annotations

from . import _shopify

SOURCE = {
    "id": "keystone",
    "name": "The Keystone",
    "type": "dealer",
    "price_nature": "asking",
    "access": "Shopify products.json (currency=USD&country=US obligatoire)",
    "robots": "OK — products.json non interdit, aucun Crawl-delay",
    "corpus_horloger": True,
}


# Les reglages de NORMALISATION, en un seul endroit. Le rejeu hors ligne tenait
# sa propre copie dans collecte/rejoue.py : les deux ont diverge, et les tags de
# nature comme le SKU-reference ne franchissaient pas le rejeu. Une donnee
# dupliquee finit toujours par se contredire.
NORMALISATION = dict(devise="USD", domaine="thekeystone.com", etat="preowned")


def collect(cap: int = 8000):
    return _shopify.collecte(SOURCE, cap, pays="US", **NORMALISATION)
