# L'entonnoir, source par source

**Généré le 2026-09-21** par `python moteur/entonnoir.py` — ne pas éditer à la main.

Trois questions dans l'ordre : combien de brut, qu'en garde le filtre, et combien portent une référence constructeur.

## En un coup d'œil

- **136 377 lignes collectées** depuis 28 sources
- **113 135 passent le filtre 0** — c'est une montre, d'une marque connue (83 %)
- **89 843 passent le filtre 1** — elles portent une référence constructeur (66 %)
- **48 137 forment le socle** — référence + date + transaction réelle (35 %)

## 1. L'entonnoir

Chaque colonne est un sous-ensemble de la précédente.

| Source | Brut collecté | Sur disque | Filtre 0 : montre | Filtre 1 : référence | Socle |
|---|---|---|---|---|---|
| Hodinkee Shop | 18 945 | 17 Mo | 18 745 (99 %) | 17 784 (94 %) | **17 784** |
| Montredo | 18 139 | 10 Mo | 17 025 (94 %) | 16 100 (89 %) | **234** |
| Christie's | 12 507 | 16 Mo | 10 758 (86 %) | 7 600 (61 %) | **6 962** |
| Artcurial | 8 625 | 11 Mo | 5 546 (64 %) | 2 913 (34 %) | **2 913** |
| Analog:Shift | 8 273 | 26 Mo | 7 314 (88 %) | 4 120 (50 %) | **3 734** |
| WatchRecon | 6 923 | 90 Mo | 6 061 (88 %) | 4 528 (65 %) | **0** |
| Wanna Buy A Watch | 6 441 | 14 Mo | 5 838 (91 %) | 4 606 (72 %) | **0** |
| Lyon & Turnbull | 5 763 | 5 Mo | 1 065 (18 %) | 353 (6 %) | **302** |
| Berry's Jewellers | 5 653 | 7 Mo | 2 159 (38 %) | 2 145 (38 %) | **448** |
| The Keystone | 5 026 | 4 Mo | 4 953 (99 %) | 4 316 (86 %) | **4 085** |
| Loupe This | 4 257 | 2 Mo | 3 942 (93 %) | 3 196 (75 %) | **3 196** |
| Monaco Legend Auctions | 4 188 | 2 Mo | 4 013 (96 %) | 2 493 (60 %) | **2 230** |
| Watchtrader | 4 116 | 8 Mo | 4 099 (100 %) | 4 096 (100 %) | **0** |
| Bulang and Sons | 3 684 | 7 Mo | 2 609 (71 %) | 2 381 (65 %) | **1 584** |
| Craft & Tailored | 3 637 | 44 Mo | 3 302 (91 %) | 3 096 (85 %) | **3 034** |
| Topper Fine Jewelers | 3 631 | 3 Mo | 2 347 (65 %) | 2 182 (60 %) | **0** |
| CW Sellors | 2 942 | 3 Mo | 2 426 (82 %) | 351 (12 %) | **121** |
| Sworders | 2 750 | 2 Mo | 1 538 (56 %) | 247 (9 %) | **0** |
| Amsterdam Watch Company | 2 690 | 12 Mo | 2 205 (82 %) | 1 810 (67 %) | **0** |
| Watches of Switzerland | 2 475 | 1 Mo | 2 296 (93 %) | 1 769 (71 %) | **0** |
| Fortuna | 2 010 | 2 Mo | 1 783 (89 %) | 1 008 (50 %) | **1 008** |
| Global Watch Shop | 972 | 6 Mo | 851 (88 %) | 851 (88 %) | **0** |
| A Collected Man | 962 | 8 Mo | 683 (71 %) | 420 (44 %) | **415** |
| Chronofinder | 592 | 3 Mo | 589 (99 %) | 585 (99 %) | **0** |
| Watches of Distinction | 507 | 4 Mo | 496 (98 %) | 469 (93 %) | **0** |
| Amsterdam Vintage Watches | 346 | 9 Mo | 341 (99 %) | 328 (95 %) | **0** |
| Hairspring | 322 | 0 Mo | 150 (47 %) | 96 (30 %) | **87** |
| EveryWatch | 1 | 3 Mo | 1 (100 %) | 0 (0 %) | **0** |

## 2. Comment la référence est obtenue, source par source

La méthode diffère parce que les sources ne publient pas la même chose. Un SKU de marchand n'est jamais une référence constructeur.

| Source | Méthode | Rendement |
|---|---|---|
| Hodinkee Shop | non documentée | 95 % du gardé |
| Montredo | extraite du corps de l'annonce | 95 % du gardé |
| Christie's | extraite du titre du lot, puis de la fiche technique | 71 % du gardé |
| Artcurial | extraite du titre puis de la description HTML | 53 % du gardé |
| Analog:Shift | extraite du corps de l'annonce | 56 % du gardé |
| WatchRecon | extraite du titre de l'annonce | 75 % du gardé |
| Wanna Buy A Watch | non documentée | 79 % du gardé |
| Lyon & Turnbull | extraite du sous-titre du lot | 33 % du gardé |
| Berry's Jewellers | champ SKU, qui porte ici la vraie référence constructeur | 99 % du gardé |
| The Keystone | non documentée | 87 % du gardé |
| Loupe This | non documentée | 81 % du gardé |
| Monaco Legend Auctions | extraite du titre du lot, qui cite la référence en clair | 62 % du gardé |
| Watchtrader | non documentée | 100 % du gardé |
| Bulang and Sons | non documentée | 91 % du gardé |
| Craft & Tailored | extraite du titre, puis du corps de l'annonce | 94 % du gardé |
| Topper Fine Jewelers | non documentée | 93 % du gardé |
| CW Sellors | SKU du marchand, référence parfois dans le corps | 14 % du gardé |
| Sworders | extraite du titre du lot, rarement présente | 16 % du gardé |
| Amsterdam Watch Company | non documentée | 82 % du gardé |
| Watches of Switzerland | lue dans l'URL de la fiche produit | 77 % du gardé |
| Fortuna | non documentée | 57 % du gardé |
| Global Watch Shop | non documentée | 100 % du gardé |
| A Collected Man | non documentée | 61 % du gardé |
| Chronofinder | non documentée | 99 % du gardé |
| Watches of Distinction | extraite du titre, sous la forme « REF 216570 » | 95 % du gardé |
| Amsterdam Vintage Watches | attribut `Reference` publié par le marchand | 96 % du gardé |
| Hairspring | extraite du corps de l'annonce | 64 % du gardé |
| EveryWatch | non documentée | 0 % du gardé |

## 3. Les natures de prix par source

Une ligne dont on ignore la nature ne se compare à rien.

| Source | Natures observées | Années du socle |
|---|---|---|
| Hodinkee Shop | vendu 18 742 · demandé 3 | 2016 → 2024 |
| Montredo | demandé 16 777 · vendu 248 | 2026 → 2026 |
| Christie's | réalisé 9 944 · estimation 814 | 2017 → 2026 |
| Artcurial | réalisé 5 546 | 2008 → 2026 |
| Analog:Shift | vendu 6 581 · demandé 733 | 2015 → 2026 |
| WatchRecon | demandé 6 061 | — |
| Wanna Buy A Watch | demandé 5 838 | — |
| Lyon & Turnbull | réalisé 981 · estimation 84 | 2020 → 2026 |
| Berry's Jewellers | demandé 1 709 · vendu 450 | 2015 → 2026 |
| The Keystone | vendu 4 643 · demandé 310 | 2018 → 2026 |
| Loupe This | réalisé 3 942 | 2021 → 2026 |
| Monaco Legend Auctions | réalisé 3 592 · estimation 421 | 2019 → 2026 |
| Watchtrader | demandé 4 099 | — |
| Bulang and Sons | vendu 1 749 · demandé 860 | 2026 → 2026 |
| Craft & Tailored | vendu 3 237 · demandé 65 | 2016 → 2026 |
| Topper Fine Jewelers | prix neuf 2 347 | — |
| CW Sellors | demandé 1 230 · vendu 1 196 | 2017 → 2025 |
| Sworders | réalisé 1 538 | — |
| Amsterdam Watch Company | demandé 2 205 | — |
| Watches of Switzerland | prix neuf 2 296 | — |
| Fortuna | réalisé 1 783 | 2016 → 2026 |
| Global Watch Shop | demandé 851 | — |
| A Collected Man | vendu 669 · demandé 14 | 2015 → 2026 |
| Chronofinder | demandé 589 | — |
| Watches of Distinction | demandé 496 | — |
| Amsterdam Vintage Watches | demandé 341 | — |
| Hairspring | vendu 138 · demandé 12 | 2023 → 2026 |
| EveryWatch | réalisé 1 | — |

## 4. Ce que la source a dit de ses propres limites

Mot pour mot, ce que le collecteur a inscrit dans son journal. Une collecte plafonnée n'est pas un total.

| Source | Journal de collecte |
|---|---|
| Christie's | `TRONQUE: plafond de 800 atteint — il reste des donnees a prendre` |
| Artcurial | `TRONQUE: plafond de 9000 atteint — il reste des donnees a prendre` |
| Montredo | `TRONQUE: plafond de 12000 atteint — il reste des donnees a prendre` |
| Lyon & Turnbull | `30 ventes retenues sur 307 passees` |
| Watches of Switzerland | `2500 fiches retenues sur 33194 — selection etalee, la collecte complete demanderait ~9 h` |

## 5. Pourquoi les lignes sont écartées

| Verdict et règle | Lignes |
|---|---|
| `REJETER R0` | 10 250 |
| `REJETER R3` | 8 152 |
| `REJETER R1` | 3 676 |
| `QUARANTAINE R7a` | 760 |
| `REJETER R4` | 216 |
| `REJETER R5` | 150 |
| `REJETER R3b` | 38 |
