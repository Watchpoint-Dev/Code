"""A Collected Man — marchand londonien d'horlogerie independante.

1 508 montres, dont 725 avec un prix exploitable. La source la plus haut de
gamme du dossier : Patek 225, F. P. Journe 180, Audemars Piguet 116, Lange 105.

DEUX PARTICULARITES :

  `available` EST TROMPEUR. Seules 17 montres sur 1 508 sont `available: true`,
  parce que 1 144 fiches sont en « Enquire Only » : en vitrine, avec un prix
  affiche, mais non achetables en ligne. Le vrai signal de vente est le tag.

  LA PAGE MASQUE LE PRIX, PAS L'API. Les fiches vendues affichent « Sold » sans
  montant, mais products.json et le JSON-LD le portent encore. C'est une donnee
  que le marchand a choisi de ne pas afficher publiquement.

Un detail rare : 25 lots portent un tag `auction-ended:<variante>:<prix>:<epoch>`
qui encode un vrai prix REALISE horodate, issu des quatre ventes aux encheres
organisees par la maison en 2022. Le marteau y differe du prix de la variante
dans 22 cas sur 25 — la variante est l'estimation.

58 % des titres portent une reference ; les manquants sont surtout de
l'horlogerie independante qui n'en a reellement pas (Journe, Voutilainen,
Daniels), ce n'est donc pas un defaut d'extraction.
Reconnaissance du 28/08/2026.
"""
from __future__ import annotations

from . import _shopify

SOURCE = {
    "id": "acollectedman",
    "name": "A Collected Man",
    "type": "dealer",
    "price_nature": "asking",
    "access": "Shopify products.json",
    "robots": "OK — /products.json non interdit, Crawl-delay seulement pour Ahrefs",
    "reserve": "l'horlogerie independante n'a souvent pas de reference constructeur",
}


# Les reglages de NORMALISATION, en un seul endroit. Le rejeu hors ligne tenait
# sa propre copie dans collecte/rejoue.py : les deux ont diverge, et les tags de
# nature comme le SKU-reference ne franchissaient pas le rejeu. Une donnee
# dupliquee finit toujours par se contredire.
NORMALISATION = dict(devise="GBP", domaine="www.acollectedman.com", etat="preowned")


def collect(cap: int = 2500):
    return _shopify.collecte(SOURCE, cap, pays="GB", **NORMALISATION)
