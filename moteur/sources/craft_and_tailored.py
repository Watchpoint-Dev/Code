"""Craft & Tailored — marchand de vintage. Prix VENDUS, avec date de mise en ligne.

Acces : endpoint public Shopify `products.json`. C'etait la premiere boutique
Shopify du dossier, et son collecteur a longtemps porte sa propre copie du
moteur — copie qui a cesse de suivre. Elle ignorait le plancher de prix, la
reference lue en entier dans le titre et le garde-fou sur `vendor`. Elle est
donc rendue au moteur commun : une boutique Shopify n'a pas de raison d'avoir
son propre normaliseur.

TROIS PARTICULARITES MESUREES :

  Le parametre `country=US` est indispensable. Sans lui la boutique sert des
  prix convertis : 33 650 USD affiches contre 27 644 renvoyes, soit -17,85 %
  sur la moitie de la base. C'est le plus gros ecart de devise du dossier.

  `available=false` VEUT DIRE VENDUE ici — 97 % du catalogue est dans ce cas.
  Reserve assumee : le montant est le dernier prix AFFICHE, pas le montant
  encaisse.

  Le champ `vendor` vaut litteralement 'Other' sur les pieces qui ne sont pas
  d'une grande maison — un Eterna des annees 1940, un Movado Super Sub Sea.
  Le champ est fidele, mais il ne nomme aucune marque : le moteur commun le
  reconnait comme muet et relit le titre.
"""
from __future__ import annotations

from . import _shopify

SOURCE = {
    "id": "craft_and_tailored",
    "name": "Craft & Tailored",
    "type": "dealer",
    "price_nature": "asking",
    "access": "Shopify products.json (country=US obligatoire)",
    "robots": "OK — 'Allow: /' ; les restrictions Shopify visent le checkout, pas le catalogue",
    # Le corpus est garanti horloger (marchand exclusivement horloger) : R4 n'a pas
    # a exiger le mot "montre" dans le titre pour valider une marque ambigue.
    "corpus_horloger": True,
}

# Les reglages de NORMALISATION, en un seul endroit — lus aussi par le rejeu.
# Devise canonique verifiee sur /meta.json ("currency":"USD", Los Angeles).
NORMALISATION = dict(devise="USD", domaine="craftandtailored.com", etat="preowned")


def collect(cap: int = 4000):
    return _shopify.collecte(SOURCE, cap, pays="US", **NORMALISATION)
