"""Berry's Jewellers — detaillant agree britannique. Prix DEMANDES.

Catalogue MIXTE : montres, joaillerie et accessoires dans le meme flux. C'est
precisement le cas ou le filtre gagne sa place — sans lui, les bagues et les
colliers entrent avec les montres.

PIEGE DE DEVISE : sans `country=GB`, nos en-tetes nous placent sur le marche
suisse et Shopify retire la TVA britannique (822 GBP affiche -> 685 renvoyes).
Regler l'Accept-Language ne suffit pas, seul le parametre `country` corrige.
Fiche de preuve : preuves/fiches/berrys.json

LE SKU EST ICI UNE VRAIE REFERENCE. Berry's est un detaillant AGREE : il
inscrit dans ce champ la reference du constructeur — 'L38204930' chez Longines,
'IW503607' chez IWC, 'M2836C1A0-0103' chez Tudor — precede de 'P-O ' pour
l'occasion. La compter comme un code maison, comme chez CW Sellors ou Topper,
ramenait la source a 183 references au lieu d'environ 2 000.
"""
from __future__ import annotations

from . import _shopify

SOURCE = {
    "id": "berrys",
    "name": "Berry's Jewellers",
    "type": "dealer",
    "price_nature": "asking",
    "access": "Shopify products.json (country=GB obligatoire)",
    "robots": "OK — verifie le 11/08/2026",
}


# Les reglages de NORMALISATION, en un seul endroit. Le rejeu hors ligne tenait
# sa propre copie dans collecte/rejoue.py : les deux ont diverge, et les tags de
# nature comme le SKU-reference ne franchissaient pas le rejeu. Une donnee
# dupliquee finit toujours par se contredire.
NORMALISATION = dict(devise="GBP", domaine="www.berrysjewellers.co.uk",
                    sku_est_reference=True)


def collect(cap: int = 25000):
    return _shopify.collecte(SOURCE, cap, pays="GB", **NORMALISATION)
