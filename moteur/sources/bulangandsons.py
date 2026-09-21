"""Bulang & Sons — marchand allemand de vintage. 2 642 prix exploitables.

3 167 montres sur 4 169 fiches : le reste est du bracelet, du sac, du livre —
d'ou l'importance de la categorie publiee, que R0 lit.

DEUX PIEGES MESURES, tous deux contre-intuitifs :

  `available` NE DIT PAS LA VENTE ICI. 775 montres sont `available: false` tout
  en portant le tag `watches-for-sale` et un prix : elles sont en vente. C'est
  le TAG qui tranche — `sold-watches-archive` contre `watches-for-sale`.

  LE PRIX 1,00 EST UNE SENTINELLE. 318 montres portent 1,00 EUR pour dire
  « prix sur demande », et 160 portent 0. Le moteur les ecarte.

Piege de reference : la description contient AUSSI les references des bracelets
livres avec la montre ('Rolex Oyster bracelet ref 93150'). Extraire la premiere
occurrence du corps donnerait la reference du bracelet, pas celle de la montre.

Le `created_at` ne date rien : la boutique a migre en aout 2025 et toutes les
fiches en portent la date. Aucune profondeur, d'ou `date='releve'`.
Reconnaissance du 28/08/2026.
"""
from __future__ import annotations

from . import _shopify

SOURCE = {
    "id": "bulangandsons",
    "name": "Bulang and Sons",
    "type": "dealer",
    "price_nature": "asking",
    "access": "Shopify products.json",
    "robots": "OK — /products.json non interdit",
    "reserve": "migration de boutique en 08/2025 : les dates de la source ne datent rien",
}


# Les reglages de NORMALISATION, en un seul endroit. Le rejeu hors ligne tenait
# sa propre copie dans moteur/rejoue.py : les deux ont diverge, et les tags de
# nature comme le SKU-reference ne franchissaient pas le rejeu. Une donnee
# dupliquee finit toujours par se contredire.
NORMALISATION = dict(devise="EUR", domaine="bulangandsons.com", date="releve",
                    tags_nature={"sold-watches-archive": ("sold", "sold"),
                                 "watches-for-sale": ("asking", "active")}, etat="preowned")


def collect(cap: int = 5000):
    return _shopify.collecte(SOURCE, cap, pays="DE", **NORMALISATION)
