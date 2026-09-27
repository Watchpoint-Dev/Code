"""Wanna Buy A Watch — marchand americain. 6 360 prix, douze ans de mise en ligne.

La meilleure des boutiques WooCommerce sondees. Champ dedie `Model/Case Ref#`
renseigne sur 4 965 fiches, vraie reference sur 67 %. Marque en champ dedie a
93,6 %, plus `Circa`, `Case Serial #`, `Movement Caliber`, `Box / Papers`.

TROUVAILLE : la page publique affiche 'SOLD' sans montant, mais l'API Store
conserve le dernier prix demande sur 5 985 montres parties. C'est ce qui rend
cette archive exploitable — avec la reserve que le marchand a choisi de ne pas
afficher ces montants publiquement.

Profondeur 2014 -> 2026, date de mise en ligne. `Circa` est l'annee de
fabrication, jamais la date de vente.
Reconnaissance du 28/08/2026.
"""
from __future__ import annotations

from . import _woo

SOURCE = {
    "id": "wannabuyawatch",
    "name": "Wanna Buy A Watch",
    "type": "dealer",
    "price_nature": "asking",
    "access": "WooCommerce Store API",
    "robots": "OK — seuls /wp-admin/ et un export d'impression sont interdits",
    "corpus_horloger": True,
}


def collect(cap: int = 9000):
    return _woo.collecte(SOURCE, cap, base="https://wannabuyawatch.com")
