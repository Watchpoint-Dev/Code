"""Analog:Shift — marchand vintage americain. Prix DEMANDES et VENDUS.

8 661 fiches en 35 requetes, marque et prix a 100 %, aucun antibot.
Fiche de preuve : preuves/fiches/analogshift.json
"""
from __future__ import annotations

from . import _shopify

SOURCE = {
    "id": "analogshift",
    "name": "Analog:Shift",
    "type": "dealer",
    "price_nature": "asking",
    "access": "Shopify products.json (country=US obligatoire)",
    "robots": "OK — /products.json couvert par aucun Disallow, verifie le 11/08/2026",
    # Le corpus est garanti horloger (marchand exclusivement horloger) : R4 n'a pas
    # a exiger le mot "montre" dans le titre pour valider une marque ambigue.
    "corpus_horloger": True,
}


# Les reglages de NORMALISATION, en un seul endroit. Le rejeu hors ligne tenait
# sa propre copie dans collecte/rejoue.py : les deux ont diverge, et les tags de
# nature comme le SKU-reference ne franchissaient pas le rejeu. Une donnee
# dupliquee finit toujours par se contredire.
NORMALISATION = dict(devise="USD", domaine="www.analogshift.com", etat="preowned")


def collect(cap: int = 25000):
    return _shopify.collecte(SOURCE, cap, pays="US", **NORMALISATION)
