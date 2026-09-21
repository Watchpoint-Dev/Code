"""CW Sellors — detaillant britannique. Prix DEMANDES, tres gros catalogue.

RESERVE MAJEURE, a ne jamais oublier en analyse : la boutique melange prix TTC
et prix HT dans le MEME flux, sans aucun champ pour les distinguer. Un ecart de
20 % entre deux lignes de cette source peut n'etre que de la TVA. Les montants
sont donc exploitables pour la structure (nature, reference, marque) mais pas
pour une comparaison de niveau de prix tant que ce point n'est pas tranche.

On interroge la collection `watches` et non tout le magasin : le reste est de
la joaillerie et de l'orfevrerie.

Fiche de preuve : preuves/fiches/cwsellors.json
"""
from __future__ import annotations

from . import _shopify

SOURCE = {
    "id": "cwsellors",
    "name": "CW Sellors",
    "type": "dealer",
    "price_nature": "asking",
    "access": "Shopify /collections/watches/products.json (country=GB obligatoire)",
    "robots": "OK — verifie le 11/08/2026",
    "reserve": "TTC et HT melanges dans le meme flux, sans champ distinctif",
}


# Les reglages de NORMALISATION, en un seul endroit. Le rejeu hors ligne tenait
# sa propre copie dans moteur/rejoue.py : les deux ont diverge, et les tags de
# nature comme le SKU-reference ne franchissaient pas le rejeu. Une donnee
# dupliquee finit toujours par se contredire.
NORMALISATION = dict(devise="GBP", domaine="www.cwsellors.co.uk")


def collect(cap: int = 12000):
    return _shopify.collecte(SOURCE, cap, pays="GB", chemin=(
                                 "/collections/mens-watches/products.json",
                                 "/collections/ladies-watches/products.json",
                                 "/collections/luxury-watches/products.json",
                                 "/collections/watches/products.json"), **NORMALISATION)
