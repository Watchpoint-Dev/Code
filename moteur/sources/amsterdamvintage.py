"""Amsterdam Vintage Watches — marchand neerlandais. La fiche la mieux remplie.

2 493 fiches, et c'est le catalogue le plus richement decrit du dossier : la
reference, l'annee, la matiere du boitier, le numero de serie, les dimensions
et le fermoir vivent chacun dans un ATTRIBUT DEDIE, pas dans une phrase qu'il
faudrait deviner. La plupart de nos marchands n'en publient aucun.

DEUX RESERVES, mesurees :

  LE PRIX EST SUPPRIME A LA VENTE, pas masque. Une montre partie garde sa fiche,
  ses photos et sa reference, mais son montant tombe a zero — le vendeur ne
  publie pas ce qu'il en a tire. Le moteur ecarte ces lignes : une fiche sans
  prix n'est pas un prix a zero. On ne garde donc que le stock vivant, et cette
  source ne dira jamais une vente.

  `currency_minor_unit` vaut 0 : les montants sont en euros entiers. Le
  confondre avec les boutiques a 2 donnerait un facteur cent.

Reconnaissance du 28/08/2026, branchee le 29/08/2026.
"""
from __future__ import annotations

from . import _woo

SOURCE = {
    "id": "amsterdamvintage",
    "name": "Amsterdam Vintage Watches",
    "type": "dealer",
    "price_nature": "asking",
    "access": "WooCommerce Store API",
    "robots": "OK — /wp-json/ autorise",
    # Marchand exclusivement horloger : R4 n'a pas a exiger le mot "montre"
    # dans le titre pour valider une marque ambigue.
    "corpus_horloger": True,
    "reserve": "le prix est retire a la vente : la source ne publie que son stock vivant",
}


def collect(cap: int = 3000):
    return _woo.collecte(SOURCE, cap, base="https://amsterdamvintagewatches.com",
                         chemin="/wp-json/wc/store/v1/products")
