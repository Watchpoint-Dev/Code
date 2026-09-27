"""Amsterdam Watch Company — marchand neerlandais. Le prix negatif comme signal.

2 531 prix exploitables sur 2 545 montres. Champ dedie `Reference` a 48 %,
`Brand` a 89,9 %, union avec le titre a 78,9 %.

PIEGE UNIQUE AU DOSSIER : 231 montres portent un prix NEGATIF — `price: "-14750"`.
C'est une convention maison pour marquer une vente ; la valeur absolue est le
dernier prix demande. Les jeter perdrait 231 observations, les prendre au pied
de la lettre casserait toute statistique.

Le domaine amsterdamwatchcompany.com redirige vers awco.nl.
`currency_minor_unit` vaut 0 : les prix sont en euros entiers, pas en centimes.
Reconnaissance du 28/08/2026.
"""
from __future__ import annotations

from . import _woo

SOURCE = {
    "id": "awco",
    "name": "Amsterdam Watch Company",
    "type": "dealer",
    "price_nature": "asking",
    "access": "WooCommerce Store API (awco.nl)",
    "robots": "OK — wp-json non interdit",
    "corpus_horloger": True,
    "reserve": "la taxonomie de marque melange 'Omega Speedmaster' et 'Other brands'",
}


def collect(cap: int = 4000):
    return _woo.collecte(SOURCE, cap, base="https://awco.nl")
