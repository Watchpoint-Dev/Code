"""Montredo — detaillant neuf europeen. Prix DEMANDES, gros volume.

DEUX RESERVES, toutes deux structurelles :

  Le catalogue est RECREE integralement chaque nuit. Les identifiants Shopify
  changent et `published_at` vaut la date du dernier rebuild. On prend donc le
  `handle` comme cle stable, et on date le prix du jour du releve : c'est la
  seule chose vraie qu'on puisse en dire. L'historique se construira en
  rejouant la collecte, pas en lisant la source.

  Sans `country=DE`, la boutique bascule sur le marche suisse et le prix temoin
  perd 9,16 %.

  `available=false` NE DIT PAS LA VENTE ICI. Montredo est un detaillant agree
  de montres NEUVES : une fiche indisponible porte le tag `inquiry-only` et
  veut dire « nous consulter », pas « vendue ». Mesure du 28/08/2026 : 18 des
  20 lignes `sold` tirees au hasard portaient ce tag, contre 0 des 10 lignes
  `asking`. On comptait ainsi 3 319 fausses ventes.

Fiche de preuve : preuves/fiches/montredo.json
"""
from __future__ import annotations

from . import _shopify

SOURCE = {
    "id": "montredo",
    "name": "Montredo",
    "type": "dealer",
    "price_nature": "asking",
    "access": "Shopify products.json (country=DE obligatoire)",
    "robots": "OK — verifie le 11/08/2026",
    # Le corpus est garanti horloger (detaillant exclusivement horloger) : R4 n'a pas
    # a exiger le mot "montre" dans le titre pour valider une marque ambigue.
    "corpus_horloger": True,
    "reserve": "catalogue reconstruit chaque nuit : identifiants et dates de la source inutilisables",
}


# Les reglages de NORMALISATION, en un seul endroit. Le rejeu hors ligne tenait
# sa propre copie dans collecte/rejoue.py : les deux ont diverge, et les tags de
# nature comme le SKU-reference ne franchissaient pas le rejeu. Une donnee
# dupliquee finit toujours par se contredire.
NORMALISATION = dict(devise="EUR", domaine="www.montredo.com", cle="handle",
                    date="releve",
                    tags_nature={"inquiry-only": ("asking", "inactive")})


def collect(cap: int = 25000):
    return _shopify.collecte(SOURCE, cap, pays="DE", **NORMALISATION)
