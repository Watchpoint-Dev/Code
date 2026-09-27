# Panorama des sources

**Généré le 2026-09-02** par `python moteur/panorama.py` — ne pas éditer à la main, ce fichier est écrasé à chaque exécution.

## En un coup d'œil

- **134 240 prix** collectés, sur **28 sources** qui rendent des données (30 adaptateurs écrits)
- **110 670 gardés** par le filtre (82 %), 22 982 rejetés, 588 en quarantaine
- **252 Mo de brut** conservé sur le disque, rejouable sans une seule requête réseau
- période couverte : **2007 → 2026**

## 1. Les sources

| Source | Type | Prix | Nature dominante | Période | Brut | Collecte |
|---|---|---|---|---|---|---|
| **Hodinkee Shop** | marchand | 18 945 | vendu · demandé | 2016 → 2024 | 8.5 Mo | complète |
| **Montredo** | marchand | 18 306 | demandé · vendu | 2026 → 2026 | 6.2 Mo | complète |
| **Christie's** | maison de ventes | 12 507 | réalisé (marteau) · estimation | 2017 → 2026 | 14.3 Mo | complète |
| **Artcurial** | maison de ventes | 8 625 | réalisé (marteau) | 2007 → 2026 | 7.5 Mo | complète |
| **Analog:Shift** | marchand | 8 213 | vendu · demandé | 2015 → 2026 | 17.2 Mo | complète |
| **Wanna Buy A Watch** | marchand | 6 441 | demandé | — → — | 14.1 Mo | complète |
| **Lyon & Turnbull** | maison de ventes | 5 763 | réalisé (marteau) · estimation | 2019 → 2026 | 3.3 Mo | partielle |
| **Berry's Jewellers** | marchand | 5 638 | demandé · vendu | 2014 → 2026 | 4.8 Mo | complète |
| **The Keystone** | marchand | 5 020 | vendu · demandé | 2018 → 2026 | 1.9 Mo | complète |
| **WatchRecon** | forums | 4 950 | demandé | 2026 → 2026 | 73.1 Mo | complète |
| **Loupe This** | maison de ventes | 4 220 | réalisé (marteau) | 2021 → 2026 | 1.0 Mo | complète |
| **Monaco Legend Auctions** | maison de ventes | 4 188 | réalisé (marteau) · estimation | 2019 → 2026 | 1.1 Mo | complète |
| **Watchtrader** | marchand | 4 090 | demandé | — → — | 4.0 Mo | complète |
| **Topper Fine Jewelers** | retail | 3 687 | prix neuf | 2018 → 2026 | 1.7 Mo | complète |
| **Bulang and Sons** | marchand | 3 683 | vendu · demandé | 2026 → 2026 | 3.4 Mo | complète |
| **Craft & Tailored** | marchand | 3 646 | vendu · demandé | 2016 → 2026 | 38.8 Mo | complète |
| **CW Sellors** | marchand | 2 948 | demandé · vendu | 2017 → 2026 | 1.8 Mo | complète |
| **Amsterdam Watch Company** | marchand | 2 686 | demandé | — → — | 5.9 Mo | complète |
| **Sworders** | maison de ventes | 2 506 | réalisé (marteau) | — → — | 0.8 Mo | complète |
| **Watches of Switzerland** | retail | 2 475 | prix neuf | — → — | 1.0 Mo | partielle |
| **Fortuna** | maison de ventes | 2 010 | réalisé (marteau) | 2016 → 2026 | 1.2 Mo | complète |
| **Global Watch Shop** | marchand | 971 | demandé | — → — | 2.8 Mo | complète |
| **A Collected Man** | marchand | 962 | vendu · demandé | 2015 → 2026 | 3.8 Mo | complète |
| **Chronofinder** | marchand | 592 | demandé | — → — | 1.6 Mo | complète |
| **Watches of Distinction** | marchand | 507 | demandé | — → — | 3.6 Mo | complète |
| **Amsterdam Vintage Watches** | marchand | 342 | demandé | — → — | 5.1 Mo | complète |
| **Hairspring** | marchand | 318 | vendu · demandé | 2023 → 2026 | 0.2 Mo | complète |
| **EveryWatch** | agrégateur | 1 | réalisé (marteau) | 2026 → 2026 | 2.9 Mo | complète |

**Les collectes marquées partielles ne sont pas des totaux.** Ce qui les a arrêtées, mot pour mot :

| Source | Ce que le collecteur a inscrit |
|---|---|
| Lyon & Turnbull | `50 ventes retenues sur 307 passees` |
| Watches of Switzerland | `2500 fiches retenues sur 33106 — selection etalee, la collecte complete demanderait ~9 h` |

Les adaptateurs écrits mais qui ne rendent rien aujourd'hui :

| Source | Type | Pourquoi |
|---|---|---|
| **LiveAuctioneers** | agrégateur | BLOQUE (anti-bot Incapsula depuis ~08/2026) |
| **Bezel** | marketplace | EN ATTENTE — les CGU interdisent le scraping, arbitrage humain requis |

## 2. Ce que le filtre en fait

Le filtre est apposé à l'ingestion : chaque ligne porte son verdict, la règle qui l'a produit et la version du filtre utilisée. Rien n'est supprimé — corriger le filtre et rejouer l'historique ne coûte aucune requête.

| Source | Gardé | Rejeté | Quarantaine | % gardé |
|---|---|---|---|---|
| Hodinkee Shop | 18 742 | 203 | 0 | 99 % |
| Montredo | 17 103 | 1 203 | 0 | 93 % |
| Christie's | 10 732 | 1 775 | 0 | 86 % |
| Artcurial | 5 520 | 3 105 | 0 | 64 % |
| Analog:Shift | 7 180 | 1 033 | 0 | 87 % |
| Wanna Buy A Watch | 5 825 | 615 | 1 | 90 % |
| Lyon & Turnbull | 1 048 | 4 715 | 0 | 18 % |
| Berry's Jewellers | 2 142 | 3 496 | 0 | 38 % |
| The Keystone | 4 945 | 75 | 0 | 99 % |
| WatchRecon | 4 352 | 206 | 392 | 88 % |
| Loupe This | 3 902 | 318 | 0 | 92 % |
| Monaco Legend Auctions | 4 008 | 180 | 0 | 96 % |
| Watchtrader | 4 070 | 11 | 9 | 100 % |
| Topper Fine Jewelers | 2 404 | 1 283 | 0 | 65 % |
| Bulang and Sons | 2 604 | 1 079 | 0 | 71 % |
| Craft & Tailored | 3 294 | 351 | 1 | 90 % |
| CW Sellors | 2 432 | 516 | 0 | 82 % |
| Amsterdam Watch Company | 2 099 | 507 | 80 | 78 % |
| Sworders | 1 504 | 1 002 | 0 | 60 % |
| Watches of Switzerland | 2 029 | 440 | 6 | 82 % |
| Fortuna | 1 779 | 231 | 0 | 89 % |
| Global Watch Shop | 804 | 85 | 82 | 83 % |
| A Collected Man | 650 | 312 | 0 | 68 % |
| Chronofinder | 589 | 3 | 0 | 99 % |
| Watches of Distinction | 496 | 8 | 3 | 98 % |
| Amsterdam Vintage Watches | 269 | 73 | 0 | 79 % |
| Hairspring | 147 | 157 | 14 | 46 % |
| EveryWatch | 1 | 0 | 0 | 100 % |

### Pourquoi une ligne ne passe pas

| Verdict et règle | Lignes |
|---|---|
| `REJETER R0` | 11 453 |
| `REJETER R3` | 7 997 |
| `REJETER R1` | 3 236 |
| `QUARANTAINE R7a` | 588 |
| `REJETER R5` | 128 |
| `REJETER R4` | 128 |
| `REJETER R3b` | 40 |

R3 = aucune marque connue dans le titre · R4 = marque au nom ambigu sans le mot montre · R1 = objet qui n'est pas une montre · R7a = le texte ne tranche pas, mise en quarantaine.

## 3. Les natures de prix

C'est la question qui décide de ce qu'on peut afficher. Un prix demandé est une opinion de vendeur ; un prix réalisé est une transaction.

| Nature | Prix | Part |
|---|---|---|
| demandé | 47 990 | 36 % |
| vendu | 40 268 | 30 % |
| réalisé (marteau) | 38 296 | 29 % |
| prix neuf | 6 162 | 5 % |
| estimation | 1 524 | 1 % |

### Déclarée ou mesurée ?

Une nature déclarée une fois pour toutes dans l'adaptateur ne distingue ni un lot invendu d'un lot vendu, ni une montre en vitrine d'une montre partie. Une nature déduite du statut de l'annonce, si.

| Source | Natures | Provenance |
|---|---|---|
| Hodinkee Shop | vendu 18 937 · demandé 8 | deduite_statut 18 945 |
| Montredo | demandé 18 043 · vendu 263 | deduite_statut 14 904 · declaree_tag 3 402 |
| Christie's | réalisé (marteau) 11 623 · estimation 884 | deduite_statut 12 507 |
| Artcurial | réalisé (marteau) 8 625 | champ_dedie 8 625 |
| Analog:Shift | vendu 7 271 · demandé 942 | deduite_statut 8 213 |
| Wanna Buy A Watch | demandé 6 441 | deduite_statut 6 441 |
| Lyon & Turnbull | réalisé (marteau) 5 573 · estimation 190 | champ_dedie 5 763 |
| Berry's Jewellers | demandé 4 774 · vendu 864 | deduite_statut 5 638 |
| The Keystone | vendu 4 704 · demandé 316 | deduite_statut 5 020 |
| WatchRecon | demandé 4 950 | constante_source 4 950 |
| Loupe This | réalisé (marteau) 4 220 | champ_dedie 4 220 |
| Monaco Legend Auctions | réalisé (marteau) 3 738 · estimation 450 | champ_dedie 4 188 |
| Watchtrader | demandé 4 090 | deduite_statut 4 090 |
| Topper Fine Jewelers | prix neuf 3 687 | deduite_statut 3 687 |
| Bulang and Sons | vendu 2 143 · demandé 1 540 | declaree_tag 2 642 · deduite_statut 1 041 |
| Craft & Tailored | vendu 3 544 · demandé 102 | deduite_statut 3 646 |
| CW Sellors | demandé 1 502 · vendu 1 446 | deduite_statut 2 948 |
| Amsterdam Watch Company | demandé 2 686 | deduite_statut 2 686 |
| Sworders | réalisé (marteau) 2 506 | deduite_statut 2 506 |
| Watches of Switzerland | prix neuf 2 475 | deduite_statut 2 475 |
| Fortuna | réalisé (marteau) 2 010 | champ_dedie 2 010 |
| Global Watch Shop | demandé 971 | deduite_statut 971 |
| A Collected Man | vendu 815 · demandé 147 | deduite_statut 962 |
| Chronofinder | demandé 592 | deduite_statut 592 |
| Watches of Distinction | demandé 507 | deduite_statut 507 |
| Amsterdam Vintage Watches | demandé 342 | deduite_statut 342 |
| Hairspring | vendu 281 · demandé 37 | deduite_statut 318 |
| EveryWatch | réalisé (marteau) 1 | champ_dedie 1 |

## 4. La référence

Elle n'est pas un critère de filtrage — un prix sans référence reste une observation de marché valide. Elle est le crochet d'identité entre une annonce et une montre : sans elle, on a un prix mais pas de quoi, et on ne peut pas construire l'objet Watch.

| Source | Un identifiant | Dont référence constructeur | Avec marque | D'où il vient |
|---|---|---|---|---|
| Hodinkee Shop | 100 % | **11 %** | 99 % | jeton_titre 15 805 · extrait_titre 1 837 · sku 1 049 · extrait_description 211 |
| Montredo | 100 % | **84 %** | 100 % | extrait_description 15 278 · jeton_titre 2 138 · sku 863 · extrait_titre 27 |
| Christie's | 63 % | **63 %** | 94 % | extrait_titre 7 761 · extrait_description 58 |
| Artcurial | 39 % | **39 %** | 66 % | extrait_titre 2 804 · extrait_description 517 |
| Analog:Shift | 87 % | **47 %** | 99 % | extrait_description 3 841 · sku 2 977 · jeton_titre 312 · extrait_titre 35 |
| Wanna Buy A Watch | 74 % | **71 %** | 96 % | champ_dedie 4 289 · extrait_titre 303 · jeton_titre 170 · extrait_description 11 |
| Lyon & Turnbull | 6 % | **6 %** | 20 % | extrait_titre 365 |
| Berry's Jewellers | 99 % | **98 %** | 100 % | champ_dedie 5 544 · jeton_titre 23 · sku 20 |
| The Keystone | 100 % | **85 %** | 100 % | extrait_titre 3 872 · sku 680 · extrait_description 407 · jeton_titre 61 |
| WatchRecon | 73 % | **15 %** | 99 % | jeton_titre 2 846 · extrait_titre 746 |
| Loupe This | 77 % | **77 %** | 98 % | extrait_titre 3 262 |
| Monaco Legend Auctions | 61 % | **59 %** | 100 % | extrait_titre 2 459 · jeton_titre 96 |
| Watchtrader | 100 % | **100 %** | 100 % | champ_dedie 4 085 · extrait_description 2 |
| Topper Fine Jewelers | 98 % | **0 %** | 100 % | jeton_titre 2 458 · sku 1 149 · extrait_titre 3 |
| Bulang and Sons | 100 % | **36 %** | 97 % | jeton_titre 1 271 · extrait_titre 1 203 · sku 1 081 · extrait_description 121 |
| Craft & Tailored | 100 % | **84 %** | 95 % | extrait_titre 3 041 · sku 383 · jeton_titre 184 · extrait_description 30 |
| CW Sellors | 100 % | **5 %** | 100 % | sku 2 536 · jeton_titre 256 · extrait_description 153 · extrait_titre 3 |
| Amsterdam Watch Company | 74 % | **71 %** | 86 % | champ_dedie 1 220 · extrait_titre 688 · jeton_titre 65 · extrait_description 2 |
| Sworders | 13 % | **0 %** | 64 % | jeton_titre 312 · extrait_titre 3 |
| Watches of Switzerland | 76 % | **76 %** | 100 % | extrait_titre 1 887 |
| Fortuna | 52 % | **51 %** | 92 % | extrait_titre 617 · extrait_description 404 · jeton_titre 20 |
| Global Watch Shop | 99 % | **97 %** | 97 % | champ_dedie 943 · jeton_titre 15 |
| A Collected Man | 100 % | **9 %** | 85 % | sku 535 · jeton_titre 342 · extrait_titre 44 · extrait_description 41 |
| Chronofinder | 99 % | **79 %** | 100 % | champ_dedie 400 · jeton_titre 120 · extrait_description 67 |
| Watches of Distinction | 94 % | **93 %** | 100 % | extrait_titre 470 · jeton_titre 6 |
| Amsterdam Vintage Watches | 96 % | **92 %** | 98 % | champ_dedie 312 · jeton_titre 15 · extrait_description 1 |
| Hairspring | 66 % | **4 %** | 51 % | jeton_titre 195 · extrait_description 14 |
| EveryWatch | 0 % | **0 %** | 100 % | aucune |

**107 364 prix sur 134 240 portent un identifiant (80 %), mais seulement 69 381 portent une vraie référence constructeur (52 %).** La différence n'est pas cosmétique. Un SKU est un numéro d'inventaire de marchand — `P-O 82172/000P-H062` chez Berry's — et une référence lue dans le corps de l'annonce peut être un calibre ou un numéro de boîtier. Une source affichant 100 % d'identifiants peut n'avoir aucune référence exploitable : c'est le cas de CW Sellors et de Montredo.

## 5. La profondeur historique

Attention à ce que la date signifie : chez une maison de ventes c'est le jour du marteau, chez un marchand c'est la mise en ligne de l'annonce. La seconde ne date pas une transaction.

| Année | Prix | Principales sources |
|---|---|---|
| 2026 | 33 751 | Montredo 18 306 · WatchRecon 4 947 · Bulang and Sons 3 683 |
| 2025 | 8 697 | Christie's 1 254 · Berry's Jewellers 1 201 · Analog:Shift 989 |
| 2024 | 10 213 | Hodinkee Shop 1 632 · Christie's 1 276 · Analog:Shift 1 001 |
| 2023 | 13 812 | Hodinkee Shop 5 678 · Christie's 1 327 · Analog:Shift 1 213 |
| 2022 | 17 883 | Hodinkee Shop 9 653 · Christie's 1 592 · Analog:Shift 1 540 |
| 2021 | 8 943 | Christie's 2 374 · Lyon & Turnbull 1 523 · Hodinkee Shop 1 334 |
| 2020 | 4 874 | Christie's 1 219 · Lyon & Turnbull 1 181 · The Keystone 538 |
| 2019 | 4 990 | Christie's 1 241 · Artcurial 735 · The Keystone 725 |
| 2018 | 3 679 | Christie's 1 125 · The Keystone 825 · Artcurial 636 |
| 2017 | 2 730 | Analog:Shift 835 · Christie's 640 · Artcurial 326 |
| 2016 | 1 168 | Artcurial 591 · Hodinkee Shop 322 · Craft & Tailored 104 |
| 2015 | 354 | Artcurial 182 · Analog:Shift 144 · Berry's Jewellers 27 |
| 2014 | 438 | Artcurial 382 · Berry's Jewellers 56 |
| 2013 | 410 | Artcurial 410 |
| 2012 | 457 | Artcurial 457 |
| 2011 | 842 | Artcurial 842 |
| 2009 | 165 | Artcurial 165 |
| 2008 | 135 | Artcurial 135 |
| 2007 | 86 | Artcurial 86 |

## 6. Les devises

Aucune conversion n'est appliquée : les montants sont ceux de la source. **Ne jamais comparer deux lignes de devises différentes.**

| Devise | Prix |
|---|---|
| USD | 64 010 |
| EUR | 37 897 |
| GBP | 26 476 |
| CHF | 3 079 |
| HKD | 2 778 |

## 7. Les réserves connues

Ce que chaque source ne peut pas dire, ou dit mal. À lire avant toute analyse qui s'appuie sur elle.

| Source | Réserve |
|---|---|
| EveryWatch | fenetre glissante de 24 mois ; invendus non publies ; montants pre-convertis en USD par la source |
| Montredo | catalogue reconstruit chaque nuit : identifiants et dates de la source inutilisables |
| CW Sellors | TTC et HT melanges dans le meme flux, sans champ distinctif |
| Hairspring | le champ vendor vaut 'Hairspring' sur 100 % des fiches ; la marque est retrouvee dans la description, mais pour la moitie seulement |
| Hodinkee Shop | archive figee : plus aucune fiche publiee apres octobre 2024 |
| Topper Fine Jewelers | catalogue mixte : ~1 000 fiches de joaillerie, ecartees par le filtre |
| Bulang and Sons | migration de boutique en 08/2025 : les dates de la source ne datent rien |
| A Collected Man | l'horlogerie independante n'a souvent pas de reference constructeur |
| Artcurial | l'API ne sert que les lots vendus : biais de survie assume |
| Monaco Legend Auctions | prix frais acheteur INCLUS, comme Christie's — pas un marteau nu |
| Watches of Switzerland | une fiche du sitemap peut etre epuisee ; le prix reste affiche |
| Fortuna | invendus non publies ; 5 ventes sur 145 ont un bareme de frais degressif |
| Loupe This | invendus non publies ; estimation absente de l'API |
| Sworders | aucune date de vente : la source ne la publie que sur la fiche du lot |
| Watchtrader | site refait en 02/2025 : 18 mois de profondeur, date de mise en ligne |
| Amsterdam Watch Company | la taxonomie de marque melange 'Omega Speedmaster' et 'Other brands' |
| Global Watch Shop | 38 % des fiches sont a prix zero (prix sur demande) |
| Amsterdam Vintage Watches | le prix est retire a la vente : la source ne publie que son stock vivant |
| Watches of Distinction | aucune date : la source ne publie ni mise en ligne ni date de vente |

S'y ajoutent trois réserves transverses, et la première est la plus coûteuse. **Deux maisons de ventes ne publient pas la même chose** : Christie's affiche le prix frais acheteur inclus, Artcurial et Lyon & Turnbull le marteau nu. L'écart est d'environ un quart. Le champ `price_includes_premium` porte l'information ligne par ligne — toute comparaison entre maisons qui l'ignore surévalue Christie's. **Les invendus sont invisibles** chez les maisons de ventes qui ne servent que leurs lots vendus : toute moyenne héritera d'un biais de survie. **La date d'un marchand est celle de la mise en ligne**, pas celle de la vente : une montre publiée en 2016 et vendue en 2019 porte 2016.

