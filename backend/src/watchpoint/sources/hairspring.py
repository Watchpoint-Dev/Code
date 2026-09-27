"""Hairspring — marchand vintage americain. Petit volume, cas d'ecole.

315 fiches seulement, mais la source demontre quelque chose : `vendor` vaut
'Hairspring' sur 100 % des fiches et les titres ne citent pas la marque
('3940J, First Series'). On a d'abord conclu que la marque etait introuvable et
que R3 rejetterait tout — 0,6 % de conservation. C'etait faux : la description
la contient, et le dictionnaire du filtre la retrouve sur la moitie des fiches.
Mesure du 28/08/2026 apres correction : reference 70 %, marque 51 %,
conservation 46 %. La lecon vaut pour toute source : ne pas conclure a
l'absence d'un champ avant d'avoir ouvert le corps de l'annonce.

Fiche de preuve : preuves/fiches/hairspring.json
"""
from __future__ import annotations

from . import _shopify

SOURCE = {
    "id": "hairspring",
    "name": "Hairspring",
    "type": "dealer",
    "price_nature": "asking",
    "access": "Shopify products.json (country=US obligatoire)",
    "robots": "OK — verifie le 11/08/2026",
    # Le corpus est garanti horloger (marchand exclusivement horloger) : R4 n'a pas
    # a exiger le mot "montre" dans le titre pour valider une marque ambigue.
    "corpus_horloger": True,
    "reserve": "le champ vendor vaut 'Hairspring' sur 100 % des fiches ; la marque "
               "est retrouvee dans la description, mais pour la moitie seulement",
}


# Les reglages de NORMALISATION, en un seul endroit. Le rejeu hors ligne tenait
# sa propre copie dans collecte/rejoue.py : les deux ont diverge, et les tags de
# nature comme le SKU-reference ne franchissaient pas le rejeu. Une donnee
# dupliquee finit toujours par se contredire.
NORMALISATION = dict(devise="USD", domaine="hairspring.com", etat="preowned")


def collect(cap: int = 400):
    return _shopify.collecte(SOURCE, cap, pays="US", **NORMALISATION)
