"""Chronofinder — marchand britannique. Petit mais integralement prixe.

593 fiches, et c'est tout le catalogue. Sa particularite : 100 % des fiches
portent un prix, aucune n'est en « prix sur demande » — ce qui n'arrive nulle
part ailleurs dans le dossier.

`currency_minor_unit` vaut 0 : les prix sont en livres entieres. Confondre avec
les boutiques a 2 donnerait un facteur 100.

La reference vit dans l'attribut `Mpn` (47 %) et dans le titre (98,7 %).
Reconnaissance du 28/08/2026.
"""
from __future__ import annotations

from . import _woo

SOURCE = {
    "id": "chronofinder",
    "name": "Chronofinder",
    "type": "dealer",
    "price_nature": "asking",
    "access": "WooCommerce Store API",
    "robots": "OK — /wp-json/ autorise",
    "corpus_horloger": True,
}


def collect(cap: int = 2000):
    return _woo.collecte(SOURCE, cap, base="https://chronofinder.com",
                         chemin="/wp-json/wc/store/products")
