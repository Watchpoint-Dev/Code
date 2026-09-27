# Ce qu'on peut faire avec les données

**Généré le 2026-09-21** par `python moteur/vues.py` — ne pas éditer à la main.

Sur 136 377 lignes collectées, **113 135 sont gardées par le filtre**. Tout ce qui suit ne porte que sur celles-là : les lignes rejetées restent en base pour l'audit, elles ne servent pas l'analyse.

## 1. L'escalier de l'exploitabilité

Chaque marche retire ce qui manque. C'est le chiffre du bas qui compte, pas celui du haut.

| Marche | Lignes | Part | Ce que ça permet |
|---|---|---|---|
| gardées par le filtre | 113 135 | 100 % | on sait que c'est une montre |
| + une marque | 112 486 | 99 % | on sait de qui elle est |
| + un prix chiffré | 112 486 | 99 % | on a une valeur |
| + une date | 94 271 | 83 % | on peut la situer dans le temps |
| + une référence constructeur | 74 817 | 66 % | on peut la rapprocher d'une autre annonce du même modèle |
| + une transaction réelle | 47 892 | 42 % | **le socle d'une cote** : réalisé ou vendu, pas une opinion de vendeur |

**47 892 lignes forment le socle exploitable**, soit 42 % du gardé. C'est peu, et c'est normal : les marchands publient des prix sans référence constructeur, les forums sans référence du tout.

## 2. Nature du prix croisée avec la référence

La question qui commande tout le reste : de quoi parle ce prix, et sait-on à quel modèle il se rapporte ?

| Nature | référence constructeur | identifiant faible | aucun identifiant | Total |
|---|---|---|---|---|
| demandé | 36 556 | 2 416 | 3 221 | 42 193 |
| vendu | 31 526 | 5 189 | 938 | 37 653 |
| réalisé | 16 858 | 0 | 10 469 | 27 327 |
| prix neuf | 3 951 | 160 | 532 | 4 643 |
| estimation | 952 | 0 | 367 | 1 319 |

L'identifiant faible est un SKU de marchand — `P-O 82172/000P-H062` chez Berry's, `LMMOD3312RNNS` chez Craft & Tailored. C'est un numéro d'inventaire : il identifie un exemplaire dans un stock, jamais un modèle, et ne permet donc aucun rapprochement entre deux annonces.

## 3. Ce que chaque source apporte au socle

Le volume d'une source ne dit pas sa valeur. Seules comptent les lignes qui franchissent toutes les marches.

| Source | Gardées | Dans le socle | Rendement | Années couvertes |
|---|---|---|---|---|
| Hodinkee Shop | 18 745 | 17 784 | 95 % | 2016 → 2024 |
| Christie's | 10 758 | 6 962 | 65 % | 2017 → 2026 |
| The Keystone | 4 953 | 4 085 | 82 % | 2018 → 2026 |
| Analog:Shift | 7 314 | 3 734 | 51 % | 2015 → 2026 |
| Loupe This | 3 942 | 3 196 | 81 % | 2021 → 2026 |
| Craft & Tailored | 3 302 | 3 034 | 92 % | 2016 → 2026 |
| Artcurial | 5 546 | 2 913 | 53 % | 2008 → 2026 |
| Monaco Legend Auctions | 4 013 | 2 230 | 56 % | 2019 → 2026 |
| Bulang and Sons | 2 609 | 1 584 | 61 % | 2026 → 2026 |
| Fortuna | 1 783 | 1 008 | 57 % | 2016 → 2026 |
| Berry's Jewellers | 2 159 | 448 | 21 % | 2015 → 2026 |
| A Collected Man | 683 | 415 | 61 % | 2015 → 2026 |
| Lyon & Turnbull | 1 065 | 302 | 28 % | 2020 → 2026 |
| Montredo | 17 025 | 234 | 1 % | 2026 → 2026 |
| CW Sellors | 2 426 | 121 | 5 % | 2017 → 2025 |
| Hairspring | 150 | 87 | 58 % | 2023 → 2026 |
| EveryWatch | 1 | 0 | 0 % | — |
| Topper Fine Jewelers | 2 347 | 0 | 0 % | — |
| Watchtrader | 4 099 | 0 | 0 % | — |
| Wanna Buy A Watch | 5 838 | 0 | 0 % | — |
| Amsterdam Watch Company | 2 205 | 0 | 0 % | — |
| Global Watch Shop | 851 | 0 | 0 % | — |
| Chronofinder | 589 | 0 | 0 % | — |
| Amsterdam Vintage Watches | 341 | 0 | 0 % | — |
| Watches of Distinction | 496 | 0 | 0 % | — |
| Watches of Switzerland | 2 296 | 0 | 0 % | — |
| WatchRecon | 6 061 | 0 | 0 % | — |
| Sworders | 1 538 | 0 | 0 % | — |

## 4. La profondeur du socle, année par année

Combien de transactions datées et rattachables à un modèle, par année. C'est la matière d'une courbe de cote.

| Année | Transactions |  |
|---|---|---|
| 2026 | 4 049 | █████████ |
| 2025 | 3 582 | ████████ |
| 2024 | 5 290 | ███████████ |
| 2023 | 8 862 | ███████████████████ |
| 2022 | 12 898 | ████████████████████████████ |
| 2021 | 4 018 | █████████ |
| 2020 | 2 029 | ████ |
| 2019 | 2 607 | ██████ |
| 2018 | 2 305 | █████ |
| 2017 | 1 182 | ███ |
| 2016 | 549 | █ |
| 2015 | 104 | █ |
| 2014 | 95 | █ |
| 2013 | 85 | █ |
| 2012 | 73 | █ |
| 2011 | 100 | █ |
| 2009 | 52 | █ |
| 2008 | 12 | █ |

## 5. Les modèles qu'on peut réellement suivre

Une référence n'a d'intérêt que si elle revient. Voici celles qui apparaissent le plus souvent dans le socle — ce sont elles qui permettront les premières courbes.

| Marque et référence | Transactions |
|---|---|
| Rolex 1601 | 476 |
| Rolex 5513 | 392 |
| Rolex 1675 | 380 |
| Rolex 1680 | 323 |
| Rolex 16570 | 310 |
| Rolex 1803 | 307 |
| Tudor 79030 | 224 |
| Rolex 18038 | 217 |
| Rolex 16610 | 209 |
| Rolex 1603 | 204 |
| Rolex 16710 | 198 |
| Rolex 18238 | 177 |
| Rolex 16520 | 176 |
| Rolex 214270 | 163 |
| Rolex 114270 | 161 |

**15 277 références distinctes** dans le socle, dont **3 022 apparaissent au moins trois fois** — le minimum pour esquisser une tendance plutôt qu'un point isolé.

## 6. Le neuf face à l'occasion

Comparer un tarif catalogue à un prix de marché demande la même référence des deux côtés. Voici où c'est possible aujourd'hui.

- **3 665 références** portent un prix neuf
- **14 397 références** portent une transaction
- **363 sont communes aux deux** — c'est là, et seulement là, qu'on peut mesurer une décote

Premiers rapprochements possibles, à devise identique :

| Référence | Prix neuf | Médiane marché | Transactions | Écart |
|---|---|---|---|---|
| Grand Seiko SBGE277 | 6 800 USD | 5 100 | 3 | -25 % |
| Omega 131.10.39.20.01.001 | 7 400 USD | 4 000 | 1 | -46 % |
| Omega 220.12.41.21.03.001 | 6 800 USD | 4 000 | 3 | -41 % |
| Parmigiani Fleurier PFC804-1020001-100182 | 26 500 USD | 11 600 | 3 | -56 % |
| Omega 220.10.41.21.03.002 | 7 100 USD | 4 000 | 7 | -44 % |
| Longines L37904969 | 2 650 GBP | 2 650 | 1 | +0 % |
| Omega 210.30.42.20.03.001 | 6 700 USD | 4 500 | 50 | -33 % |
| Grand Seiko SBGH347 | 7 300 USD | 3 900 | 1 | -47 % |
| Zenith 18.3200.3600/69.C901 | 24 500 USD | 11 000 | 1 | -55 % |
| Omega 234.32.41.21.01.001 | 7 600 USD | 5 850 | 1 | -23 % |

Réserve : le prix neuf est relevé chez un détaillant britannique en GBP, et les transactions viennent de maisons de ventes dont certaines publient frais acheteur inclus. Ces écarts sont des ordres de grandeur, pas des décotes établies.

## 7. Ce qui manque pour aller plus loin

| Ce qui manque | Constat mesuré | Ce qu'il faudrait |
|---|---|---|
| Référence constructeur chez les marchands | 7 765 lignes portent un SKU au lieu d'une référence | lire la fiche produit au lieu du catalogue |
| Date de transaction chez les marchands | la date publiée est celle de la mise en ligne, pas de la vente | relever les disparitions d'annonces jour après jour |
| Profondeur avant 2017 hors Artcurial | Christie's ne sert plus ses lots anciens, les marchands n'ont pas d'archive | brancher une maison de ventes à archive profonde |
| Le modèle, presque absent | 3 % des lignes portent un nom de modèle en champ propre | le déduire de la référence, une fois le référentiel constitué |
