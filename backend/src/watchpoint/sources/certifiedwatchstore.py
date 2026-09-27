"""Certified Watch Store — revendeur americain de montres neuves. Prix DEMANDES.

Le meilleur taux de reference du lot : 245 fiches sur 250 (98 %) rendent une
reference constructeur propre, lue dans le titre — 'CA0649-06X', 'AW0152-58H',
'NH8354-58A'. La boutique termine systematiquement son titre par la reference,
et la marque est renseignee sur 250/250 (Casio, Timex, Luminox, Orient, Tissot,
Citizen, Bulova, Victorinox). Mesure du 21/09/2026.

LE SKU RESTE UN CODE MAISON, meme s'il contient la reference : 'CI2-CA0649-06X'
est la reference Citizen prefixee du code fournisseur maison. Le prefixe n'est
pas un etat ('P-O', 'NOS') et `_sans_prefixe` ne le retire pas : activer
`sku_est_reference` ecrirait 250 references inexistantes chez Citizen. On laisse
donc le moteur lire le TITRE, qui donne la reference nue.

`product_type` EST LA TAXONOMIE EBAY, pas une categorie maison :
'Jewelry & Watches:Watches, Parts & Accessories:Watches:Wristwatches'. Elle
contient le mot 'Watches', donc `est_une_montre` la reconnait. 243 des 250
fiches sont horlogeres ; le reste est residuel et heteroclite (lunettes, stylo
Montblanc, couteaux, un jean) — 3 % que le filtre ecarte. Aucune collection
dediee : la restreindre couterait plus de volume qu'elle n'eviterait de bruit,
comme mesure chez CW Sellors (191 montres dans la collection 'watches' sur
~3 000 au catalogue).

`available=false` EST UNE RUPTURE DE STOCK, PAS UNE VENTE. Ce sont des
references de catalogue neuves et reapprovisionnables, pas des pieces uniques :
95 fiches sur 250 sont indisponibles a un instant donne, toutes portant une
reference de production courante. Les compter comme des ventes fabriquerait
38 % de fausses transactions. D'ou `indisponible='inactive'`.

`published_at` est ici une VRAIE date de mise en ligne : elle vaut exactement
`created_at` sur 250/250 fiches (contrairement a Watches.com, ou la
republication l'ecrase). Elle date la mise en ligne, JAMAIS une transaction —
le prix collecte est celui du jour du releve.

DEVISE : boutique mono-marche en USD. Mesure du 21/09/2026 : `country=US` ne
change aucun des trois prix temoins (235,00 / 309,00 / 345,00 identiques avec
et sans localisation) et 235,00 USD est bien le montant de la fiche publique.
Le parametre reste un garde-fou : la page d'accueil nous localise
`Shopify.country = "CH"`.

Reconnaissance du 21/09/2026 — essais/certified-watch-store/notes.md
"""
from __future__ import annotations

from . import _shopify

SOURCE = {
    "id": "certifiedwatchstore",
    "name": "Certified Watch Store",
    "type": "dealer",
    "price_nature": "asking",
    "access": "Shopify products.json (currency=USD&country=US)",
    "robots": "OK — products.json non interdit, lu le 21/09/2026",
    "reserve": "catalogue de neuf a rotation rapide : 38 % des fiches en rupture, "
               "aucune n'est une vente",
}


# Les reglages de NORMALISATION, en un seul endroit. Le rejeu hors ligne tenait
# sa propre copie dans collecte/rejoue.py : les deux ont diverge, et les tags de
# nature comme le SKU-reference ne franchissaient pas le rejeu. Une donnee
# dupliquee finit toujours par se contredire.
NORMALISATION = dict(devise="USD", domaine="www.certifiedwatchstore.com",
                    indisponible="inactive", etat="new")


def collect(cap: int = 4000):
    return _shopify.collecte(SOURCE, cap, pays="US", **NORMALISATION)
