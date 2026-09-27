"""Global Watch Shop — marchand britannique. Reference en champ dedie a 100 %.

2 760 fiches, et la meilleure couverture de reference du dossier : l'attribut
`Model` est renseigne sur 300 fiches sur 300 dans l'echantillon, toutes avec un
chiffre — 126710BLNR, 278274, 326935.

RESERVE : 38 % des prix sont a zero. C'est du « prix sur demande » masque, que
le moteur ecarte. Et « Out of stock » y signifie retire ou vendu, le prix
affiche restant le dernier prix demande.
Reconnaissance du 28/08/2026.
"""
from __future__ import annotations

from . import _woo

SOURCE = {
    "id": "globalwatchshop",
    "name": "Global Watch Shop",
    "type": "dealer",
    "price_nature": "asking",
    "access": "WooCommerce Store API",
    "robots": "OK — seul ?rest_route= est bloque, /wp-json/ ne l'est pas",
    "corpus_horloger": True,
    "reserve": "38 % des fiches sont a prix zero (prix sur demande)",
}


def collect(cap: int = 4000):
    return _woo.collecte(SOURCE, cap, base="https://www.globalwatchshop.co.uk",
                         chemin="/wp-json/wc/store/products")
