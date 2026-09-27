"""Les faits sur les sources qu'AUCUN code ne peut deviner.

Le reste de l'inventaire se derive tout seul : les adaptateurs branches se lisent
dans `sources/`, les volumes reels dans `data/price_points.jsonl`, les essais dans
`essais/`. Ce qui suit ne s'en deduit pas — c'est le resultat de la campagne
d'audit du 09/08/2026, chaque ligne appuyee par des echantillons dans `preuves/`.

C'est le SEUL fichier a editer a la main quand le paysage des sources change.
`rapports/inventaire.py` le fusionne avec le reste et ecrit `docs/rapports/SOURCES.md`.
"""
from __future__ import annotations

# --------------------------------------------------------------------------
# Prouvees par recuperation reelle, pas encore reliees au moteur.
# volume = ce qui est ATTEIGNABLE, pas ce qui est collecte.
# --------------------------------------------------------------------------
PROUVEES = [
    dict(nom="EveryWatch", categorie="agregateur", nature="realise", volume="218 000",
         historique="2,5 ans glissants", acces="endpoint JSON Next.js, auctionType=result",
         note="mur payant avant 2024 ; devise convertie, pas native"),
    dict(nom="Bezel — API interne", categorie="marketplace", nature="demande", volume="32 620",
         historique="releve", acces="/api/marketplace/listings?active=true",
         note="remplace la voie sitemap actuelle, 366x plus de volume"),
    dict(nom="Hodinkee Shop", categorie="marchand", nature="demande", volume="18 946",
         historique="date", acces="Shopify /products.json",
         note="94 % des SKU sont des codes internes — extraire la reference du titre"),
    dict(nom="Wanna Buy A Watch", categorie="marchand", nature="vendu", volume="6 477",
         historique="date", acces="WooCommerce Store API",
         note="l'archive conserve les prix ET la categorie SOLD — vrai prix vendu"),
    dict(nom="Loupe This", categorie="encheres en ligne", nature="realise", volume="4 145",
         historique="2021 -> 2026", acces="API JSON publique, sans authentification",
         note="robots le plus permissif du dossier ; specs a 100 %"),
    dict(nom="Watchtrader", categorie="marchand", nature="demande", volume="3 916",
         historique="date", acces="WooCommerce Store API",
         note="meilleure completude de specs du projet (~100 % sur tout)"),
    dict(nom="Monaco Legend", categorie="maison de ventes", nature="realise", volume="3 738",
         historique="2019 -> 2026", acces="JSON-LD + attributs data- des pages de vente",
         note="deux devises : EUR (Monaco) et CHF (Geneve)"),
    dict(nom="Menta Watches", categorie="marchand", nature="demande", volume="2 882",
         historique="date", acces="WooCommerce Store API",
         note="prix purges de l'archive ; Crawl-delay 10"),
    dict(nom="Amsterdam Vintage Watches", categorie="marchand", nature="demande", volume="2 482",
         historique="date", acces="WooCommerce Store API",
         note="33 % de « prix sur demande » ; archive sans prix"),
]

# --------------------------------------------------------------------------
# Fermees techniquement. La seule voie est un accord ou un acces officiel.
# priorite 1 = le type de prix qu'on n'a pas du tout.
# --------------------------------------------------------------------------
A_NEGOCIER = [
    dict(priorite=1, nom="WatchCharts", categorie="indice",
         demande="licence de donnees ou API d'indices", blocage="Cloudflare, blocage total"),
    dict(priorite=1, nom="Chrono24 — ChronoPulse", categorie="indice",
         demande="API ou partenariat data", blocage="Cloudflare, blocage total"),

    dict(priorite=2, nom="eBay", categorie="marketplace",
         demande="API Marketplace Insights (prix vendus)",
         blocage="acces restreint sur approbation ; nos cles production sont bloquees "
                 "par une mise en conformite a realiser"),
    dict(priorite=2, nom="EveryWatch — historique", categorie="agregateur",
         demande="l'anteriorite avant 2024",
         blocage="mur payant ; 2,5 ans glissants sont gratuits"),
    dict(priorite=2, nom="Reddit", categorie="communaute",
         demande="cle d'API officielle", blocage="robots interdit tout le domaine"),

    dict(priorite=3, nom="Barnebys", categorie="agregateur",
         demande="flux licencie d'encheres",
         blocage="robots interdit tout le site, permission ecrite exigee"),
    dict(priorite=3, nom="Phillips", categorie="maison de ventes",
         demande="resultats de ventes",
         blocage="403 par URL ; la page listant les ventes montres est interdite"),
    dict(priorite=3, nom="Sotheby's", categorie="maison de ventes",
         demande="resultats de ventes",
         blocage="la seule route portant les donnees est interdite par robots"),
    dict(priorite=3, nom="the-saleroom", categorie="agregateur",
         demande="resultats multi-maisons", blocage="pare-feu applicatif AWS"),
    dict(priorite=3, nom="Invaluable", categorie="agregateur",
         demande="prix realises",
         blocage="joignable, mais le seul chemin vers les resultats est interdit"),
    dict(priorite=3, nom="LiveAuctioneers", categorie="agregateur",
         demande="prix realises dates",
         blocage="anti-bot Incapsula installe vers le 08/2026 — marchait le 01/08"),

    dict(priorite=4, nom="Patek Philippe", categorie="marque",
         demande="acces au tarif catalogue",
         blocage="CONTROLE DU 11/08 : les 266 fiches produit sont accessibles mais ne "
                 "portent AUCUN prix en HTTP simple. Le tarif est derriere un bouton "
                 "« Display the product price ». Une campagne anterieure affirmait "
                 "l'inverse — c'etait faux, elle avait pris des URL d'images pour des prix."),
    dict(priorite=4, nom="Grand Seiko", categorie="marque",
         demande="acces au tarif catalogue",
         blocage="CONTROLE DU 11/08 : aucun prix sur la page collection ni sur la fiche "
                 "produit, quel que soit le marche teste."),
    dict(priorite=4, nom="Rolex, Omega, Cartier, TAG Heuer, IWC, Tudor", categorie="marque",
         demande="tarif catalogue", blocage="protection Akamai"),
    dict(priorite=4, nom="Audemars Piguet", categorie="marque",
         demande="tarif catalogue", blocage="endpoint de prix verrouille cote serveur"),

    dict(priorite=5, nom="WatchUSeek", categorie="communaute",
         demande="acces aux archives", blocage="epreuve de calcul anti-robot"),
    dict(priorite=5, nom="WatchProSite", categorie="communaute",
         demande="acces aux archives", blocage="Cloudflare Turnstile"),
    dict(priorite=5, nom="Rolex Forums", categorie="communaute",
         demande="acces aux archives", blocage="challenge JS Cloudflare"),
    dict(priorite=5, nom="TimeZone", categorie="communaute",
         demande="acces aux archives", blocage="robots interdit tout"),
]

# --------------------------------------------------------------------------
# A retirer des listes : ces sources n'existent plus ou sont hors d'atteinte
# pour une raison qui ne se negocie pas.
# --------------------------------------------------------------------------
ECARTEES = [
    dict(nom="WatchAnalytics", raison="le site a ferme — sert une page d'arret d'activite"),
    dict(nom="Antiquorum", raison="le site a disparu — redirige vers une vitrine sans archives"),
    dict(nom="WatchBox / 1916 Company", raison="eteint — plus aucun catalogue en ligne"),
    dict(nom="Chronext", raison="SPA, catalogue non enumerable ; quelques centaines de fiches au mieux"),
    dict(nom="1stDibs", raison="annonces en JavaScript ; 29 % de completude, remplace par Bezel"),
    dict(nom="Lot-Art", raison="robots.txt interdit explicitement notre outil — a evaluer autrement"),
]

# Note de contexte reprise dans le document genere.
# Corrige le 11/08/2026 apres controle manuel : le prix neuf n'est PAS
# recuperable. Ni Patek ni Grand Seiko ne servent de prix en HTTP simple.
# La conclusion de juillet etait donc juste, et celle d'aout etait fausse.
NATURES_COUVERTES = 3   # realise, demande, vendu. Manquent : prix neuf et indice

AVERTISSEMENT = (
    "Trois sources sont mortes en trois semaines (LiveAuctioneers, Antiquorum, "
    "WatchBox), dont deux faisaient partie des cinq sources validees en juillet. "
    "Ce marche se ferme progressivement : les verdicts ci-dessous ont une date de "
    "peremption, et les accords commerciaux prennent de la valeur avec le temps."
)
