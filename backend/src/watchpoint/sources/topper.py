"""Topper Fine Jewelers — detaillant agree americain. Tarif du NEUF.

2 549 montres sur 3 693 fiches, le reste etant de la joaillerie que le filtre
ecarte. Interet : c'est une deuxieme source de PRIX NEUF, apres Watches of
Switzerland — la nature dont la base manque le plus.

PIEGE DECISIF, releve a la reconnaissance : chez ce marchand `available=false`
signifie RUPTURE DE STOCK, pas vente. La meme reference est reapprovisionnee.
Le traiter comme une vente, comme on le fait chez les marchands de pieces
uniques, fabriquerait de fausses transactions. D'ou `indisponible='inactive'`.

Le SKU EST la reference constructeur sur le neuf — 94,9 % : `SPB249` (Seiko),
`324.20.38.50.02.002` (Omega). C'est l'inverse des marchands d'occasion, ou le
SKU est un numero d'inventaire. Sur les 116 fiches pre-owned, en revanche, le
SKU redevient un code marchand.
Reconnaissance du 28/08/2026.
"""
from __future__ import annotations

from . import _shopify

SOURCE = {
    "id": "topper",
    "name": "Topper Fine Jewelers",
    "type": "retail",
    "price_nature": "msrp",
    "access": "Shopify products.json (currency=USD&country=US)",
    "robots": "OK — products.json non interdit",
    "reserve": "catalogue mixte : ~1 000 fiches de joaillerie, ecartees par le filtre",
}


# Les reglages de NORMALISATION, en un seul endroit. Le rejeu hors ligne tenait
# sa propre copie dans collecte/rejoue.py : les deux ont diverge, et les tags de
# nature comme le SKU-reference ne franchissaient pas le rejeu. Une donnee
# dupliquee finit toujours par se contredire.
NORMALISATION = dict(devise="USD", domaine="topperjewelers.com",
                    indisponible="inactive", nature_neuf="msrp", etat="new")


def collect(cap: int = 6000):
    return _shopify.collecte(SOURCE, cap, pays="US", **NORMALISATION)
