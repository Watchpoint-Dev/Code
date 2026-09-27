"""Watches.com — detaillant agree multimarque americain. Prix DEMANDES.

Catalogue de NEUF, tres majoritairement micro-marques et marques accessibles :
RZE, Oceaneva, Xeric, Hemel, Duxot, Nubeo, G-Shock, Shinola. Mesure du
21/09/2026 sur 250 fiches : 238 portent un `product_type` 'Watch'/'Watches',
11 sont des bracelets. Le rayon est donc quasi pur — aucune collection dediee
n'est necessaire, le filtre ecarte les 4 % restants.

`available=false` EST UNE RUPTURE DE STOCK, PAS UNE VENTE. La boutique vend des
references de catalogue neuves, livrees en dropship par la marque (tags
'drop ship' / 'dropship' sur 134 des 250 fiches) : la meme reference revient.
83 fiches sur 250 sont indisponibles a un instant donne. Les compter comme des
ventes, comme chez un marchand de pieces uniques, fabriquerait 33 % de fausses
transactions — l'erreur deja payee chez Topper. D'ou `indisponible='inactive'`.

`published_at` NE DATE RIEN : c'est l'horodatage de la DERNIERE republication.
Mesure du 21/09/2026 : sur 250 fiches, 223 ont `published_at` posterieur a
`created_at` — de 26 jours en median et jusqu'a 1 148 jours (creee le
11/03/2025, republiee le 11/09/2026). La page 1 de products.json ne contient
que des republications des trois derniers mois. On date donc du RELEVE, comme
chez Montredo, et l'historique se construira en rejouant la collecte.

LE SKU N'EST PAS LA REFERENCE : 'RZE-UTD-STG-NY-P' pour une RZE UTD-8000-STG.
C'est un code maison qui cite la marque, pas le constructeur —
`sku_est_reference` reste donc a False. Consequence honnete : seules 56 fiches
sur 250 (22 %) rendent une vraie reference, lue dans le titre ; 179 retombent
sur le SKU avec la provenance `sku`, et 15 n'en portent aucune. Les
micro-marques ne publient pas de reference au sens horloger classique.

DEVISE : boutique mono-marche en USD. Mesure du 21/09/2026 : `country=US` ne
change AUCUN des trois prix temoins (279,00 / 1 769,00 / 42 800,00 identiques
avec et sans localisation), et 279,00 USD est bien le montant affiche sur la
fiche publique /products/utd-8000-stg. Le parametre est conserve comme
garde-fou : la page d'accueil nous localise `Shopify.country = "CH"`, et c'est
exactement la configuration qui a coute -17,8 % chez Craft & Tailored.

Reconnaissance du 21/09/2026 — essais/watches-com/notes.md
"""
from __future__ import annotations

from . import _shopify

SOURCE = {
    "id": "watchesdotcom",
    "name": "Watches.com",
    "type": "retail",
    "price_nature": "asking",
    "access": "Shopify products.json (currency=USD&country=US)",
    "robots": "OK — products.json non interdit, lu le 21/09/2026",
    "reserve": "prix du NEUF non remise (compare_at_price vide sur 250/250) ; "
               "reference constructeur sur 22 % des fiches seulement",
}


# Les reglages de NORMALISATION, en un seul endroit. Le rejeu hors ligne tenait
# sa propre copie dans moteur/rejoue.py : les deux ont diverge, et les tags de
# nature comme le SKU-reference ne franchissaient pas le rejeu. Une donnee
# dupliquee finit toujours par se contredire.
NORMALISATION = dict(devise="USD", domaine="www.watches.com",
                    indisponible="inactive", date="releve", etat="new")


def collect(cap: int = 8000):
    return _shopify.collecte(SOURCE, cap, pays="US", **NORMALISATION)
