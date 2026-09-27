"""Watches of Distinction — marchand britannique. Prix DEMANDES, fiche structuree.

2 996 fiches servies par l'API Store de WooCommerce, avec la marque, l'annee, la
matiere du boitier et le diametre en ATTRIBUTS DEDIES. La reference vit dans le
titre, sous une forme constante : 'Rolex EXPLORER II REF 216570 (2020) FULL SET'.

Deux points mesures le 02/09/2026 :

  `currency_minor_unit` vaut 2 : les montants arrivent en pence. 749500 se lit
  7 495 GBP. Le confondre avec les boutiques a 0 donnerait un facteur cent.

  La reconnaissance d'aout annoncait 67 % de fiches a prix zero. Ce n'est plus
  le cas sur le catalogue servi aujourd'hui : le moteur ecarte de toute facon
  les lignes sans prix, et le journal dit combien.

Le robots.txt n'interdit que le panier et l'administration : l'API est ouverte.
"""
from __future__ import annotations

from . import _woo

SOURCE = {
    "id": "watchesofdistinction",
    "name": "Watches of Distinction",
    "type": "dealer",
    "price_nature": "asking",
    "access": "WooCommerce Store API",
    "robots": "OK — /wp-json/ non interdit, verifie le 02/09/2026",
    # Marchand exclusivement horloger : R4 n'a pas a exiger le mot "montre"
    # dans le titre pour valider une marque ambigue.
    "corpus_horloger": True,
    "reserve": "aucune date : la source ne publie ni mise en ligne ni date de vente",
}


def collect(cap: int = 4000):
    return _woo.collecte(SOURCE, cap, base="https://watchesofdistinction.com",
                         chemin="/wp-json/wc/store/v1/products")
