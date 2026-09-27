# Rapport par source

**Généré le 2026-09-02** par `python moteur/rapport_source.py` — ne pas éditer à la main.

Une fiche par source. Le tableau `TOUTES_LES_SOURCES.md` répond à « combien » ; ce rapport-ci répond à « peut-on s'en servir, et pour quoi faire ».

**28 sources collectent**, 18 ont été sondées puis écartées. En tout :

- **134 240 lignes** ramenées
- **110 670** sont une montre d'une marque connue (82 %)
- **88 312** portent une référence constructeur (66 %)
- **48 021** forment le socle : référence + date + transaction réelle (36 %)

---

## Sommaire

| # | Source | Type | Brut | Socle | Ce qu'elle apporte |
|---|---|---|---|---|---|
| 1 | [Hodinkee Shop](#1-hodinkee) | marchand | 18 945 | 17 784 | le socle — transactions datées et référencées |
| 2 | [Montredo](#2-montredo) | marchand | 18 306 | 234 | des références et des prix, sans date |
| 3 | [Christie's](#3-christies) | maison de ventes | 12 507 | 6 959 | le socle — transactions datées et référencées |
| 4 | [Artcurial](#4-artcurial) | maison de ventes | 8 625 | 2 912 | le socle — transactions datées et référencées |
| 5 | [Analog:Shift](#5-analogshift) | marchand | 8 213 | 3 712 | le socle — transactions datées et référencées |
| 6 | [Wanna Buy A Watch](#6-wannabuyawatch) | marchand | 6 441 | 0 | des références et des prix, sans date |
| 7 | [Lyon & Turnbull](#7-lyonandturnbull) | maison de ventes | 5 763 | 301 | un appoint |
| 8 | [Berry's Jewellers](#8-berrys) | marchand | 5 638 | 397 | des références et des prix, sans date |
| 9 | [The Keystone](#9-keystone) | marchand | 5 020 | 4 081 | le socle — transactions datées et référencées |
| 10 | [WatchRecon](#10-watchrecon) | forums | 4 950 | 0 | des références et des prix, sans date |
| 11 | [Loupe This](#11-loupethis) | maison de ventes | 4 220 | 3 169 | le socle — transactions datées et référencées |
| 12 | [Monaco Legend Auctions](#12-monacolegend) | maison de ventes | 4 188 | 2 229 | le socle — transactions datées et référencées |
| 13 | [Watchtrader](#13-watchtrader) | marchand | 4 090 | 0 | des références et des prix, sans date |
| 14 | [Topper Fine Jewelers](#14-topper) | détaillant | 3 687 | 0 | des références et des prix, sans date |
| 15 | [Bulang and Sons](#15-bulangandsons) | marchand | 3 683 | 1 583 | le socle — transactions datées et référencées |
| 16 | [Craft & Tailored](#16-craft_and_tailored) | marchand | 3 646 | 3 039 | le socle — transactions datées et référencées |
| 17 | [CW Sellors](#17-cwsellors) | marchand | 2 948 | 121 | un appoint |
| 18 | [Amsterdam Watch Company](#18-awco) | marchand | 2 686 | 0 | des références et des prix, sans date |
| 19 | [Sworders](#19-sworders) | maison de ventes | 2 506 | 0 | un appoint |
| 20 | [Watches of Switzerland](#20-watchesofswitzerland) | détaillant | 2 475 | 0 | des références et des prix, sans date |
| 21 | [Fortuna](#21-fortuna) | maison de ventes | 2 010 | 1 007 | le socle — transactions datées et référencées |
| 22 | [Global Watch Shop](#22-globalwatchshop) | marchand | 971 | 0 | des références et des prix, sans date |
| 23 | [A Collected Man](#23-acollectedman) | marchand | 962 | 407 | un appoint |
| 24 | [Chronofinder](#24-chronofinder) | marchand | 592 | 0 | des références et des prix, sans date |
| 25 | [Watches of Distinction](#25-watchesofdistinction) | marchand | 507 | 0 | un appoint |
| 26 | [Amsterdam Vintage Watches](#26-amsterdamvintage) | marchand | 342 | 0 | un appoint |
| 27 | [Hairspring](#27-hairspring) | marchand | 318 | 86 | un appoint |
| 28 | [EveryWatch](#28-everywatch) | agrégateur | 1 | 0 | un appoint |

---

<a name="1-hodinkee"></a>

## 1. Hodinkee Shop

`hodinkee` · marchand · Shopify products.json (currency=USD&country=US)

**Ce qu'elle donne**

| Étape | Lignes | Part du brut |
|---|---|---|
| Brut collecté | 18 945 | 100 % |
| Filtre 0 — c'est une montre | 18 742 | 99 % |
| Filtre 1 — référence constructeur | 17 784 | 94 % |
| Socle — + date + transaction | 17 784 | 94 % |

**Natures de prix** — vendu 18 739 · demandé 3  
**Devises** — USD 18 742  
**Période** — 2016 → 2024 (9 années)  
**Montant médian** — 5 175  

**Ce qu'elle remplit**

| montant | devise | date | marque | référence | modèle | année | boîtier | diamètre | mouvement | cadran | estimation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 100 % | 100 % | 100 % | 100 % | 100 % | 0 % | 5 % | 0 % | 0 % | 0 % | 0 % | 0 % |

**D'où vient la donnée**

- Référence : `jeton_titre` 15 781 · `extrait_titre` 1 803 · `sku` 926 · `extrait_description` 200
- Nature du prix : `deduite_statut` 18 742
- Statut d'annonce : sold 18 739 · active 3

**Ce qu'il faut savoir**

Archive figée : plus rien publié après octobre 2024. On l'aspire une fois, elle ne bougera plus — c'est un gisement, pas un flux.

> **Réserve déclarée** — archive figee : plus aucune fiche publiee apres octobre 2024

*robots.txt : OK — products.json non interdit*

**Ce qui a été vérifié**

`8/8 montants · 8/8 references · 8/8 natures · 8/8 marques` — Rien a corriger. Notre marque est meilleure que celle de la boutique : `vendor` dit « HODINKEE Shop », nous disons « Audemars Piguet ».

<details><summary>Pourquoi des lignes sont écartées</summary>

| Verdict et règle | Lignes |
|---|---|
| `REJETER · R3` | 135 |
| `REJETER · R1` | 35 |
| `REJETER · R0` | 25 |
| `REJETER · R3b` | 6 |
| `REJETER · R5` | 2 |

</details>

---

<a name="2-montredo"></a>

## 2. Montredo

`montredo` · marchand · Shopify products.json (country=DE obligatoire)

**Ce qu'elle donne**

| Étape | Lignes | Part du brut |
|---|---|---|
| Brut collecté | 18 306 | 100 % |
| Filtre 0 — c'est une montre | 17 103 | 93 % |
| Filtre 1 — référence constructeur | 16 358 | 89 % |
| Socle — + date + transaction | 234 | 1 % |

**Natures de prix** — demandé 16 855 · vendu 248  
**Devises** — EUR 17 103  
**Période** — 2026 → 2026 (1 années)  
**Montant médian** — 2 670  

**Ce qu'elle remplit**

| montant | devise | date | marque | référence | modèle | année | boîtier | diamètre | mouvement | cadran | estimation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 100 % | 100 % | 100 % | 100 % | 100 % | 0 % | 0 % | 0 % | 0 % | 0 % | 0 % | 0 % |

**D'où vient la donnée**

- Référence : `extrait_description` 14 319 · `jeton_titre` 2 013 · `sku` 745 · `extrait_titre` 26
- Nature du prix : `deduite_statut` 13 901 · `declaree_tag` 3 202
- Statut d'annonce : active 13 653 · inactive 3 202 · sold 248

**Ce qu'il faut savoir**

Le tag `inquiry-only` dit « nous consulter », pas « vendue » : 3 071 fausses ventes ont été retirées le 28/08. Catalogue reconstruit chaque nuit, d'où une date de relevé et zéro profondeur.

> **Réserve déclarée** — catalogue reconstruit chaque nuit : identifiants et dates de la source inutilisables

*robots.txt : OK — verifie le 11/08/2026*

**Ce qui a été vérifié**

`8/8 montants · 7/8 references · 2/8 natures · 8/8 marques` — CORRIGE. 18 des 20 lignes « vendues » tirees au hasard portaient le tag `inquiry-only` : 3 071 fausses ventes retirees.

<details><summary>Pourquoi des lignes sont écartées</summary>

| Verdict et règle | Lignes |
|---|---|
| `REJETER · R3` | 823 |
| `REJETER · R1` | 307 |
| `REJETER · R0` | 72 |
| `REJETER · R3b` | 1 |

</details>

---

<a name="3-christies"></a>

## 3. Christie's

`christies` · maison de ventes · API JSON interne (discoverywebsite)

**Ce qu'elle donne**

| Étape | Lignes | Part du brut |
|---|---|---|
| Brut collecté | 12 507 | 100 % |
| Filtre 0 — c'est une montre | 10 732 | 86 % |
| Filtre 1 — référence constructeur | 7 597 | 61 % |
| Socle — + date + transaction | 6 959 | 56 % |

**Natures de prix** — réalisé 9 918 · estimation 814  
**Devises** — USD 6 042 · HKD 2 386 · CHF 2 196 · EUR 108  
**Période** — 2017 → 2026 (10 années)  
**Montant médian** — 15 000  
**Régime de frais** — frais acheteur INCLUS  

**Ce qu'elle remplit**

| montant | devise | date | marque | référence | modèle | année | boîtier | diamètre | mouvement | cadran | estimation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 100 % | 100 % | 100 % | 96 % | 71 % | 0 % | 63 % | 86 % | 80 % | 85 % | 85 % | 100 % |

**D'où vient la donnée**

- Référence : `extrait_titre` 7 560 · `extrait_description` 37
- Nature du prix : `deduite_statut` 10 732
- Statut d'annonce : sold 9 918 · unsold 814

**Ce qu'il faut savoir**

Publie ses prix FRAIS ACHETEUR INCLUS — mesuré : 39 % de montants ronds contre 97 % chez Artcurial. Sa fiche technique donne matière, mouvement, cadran et diamètre à plus de 80 %.

*robots.txt : OK — les Disallow visent */search, */AjaxPages… ; 'lotsearch' n'est pas '/search'*

**Ce qui a été vérifié**

`7/8 montants · 8/8 references · 8/8 dates` — Le drapeau « frais inclus » est juste : 89 a 95 % des montants se decomposent en (marteau sur echelon) x (taux publie). Reserve : pour les ventes en ligne la date est l'OUVERTURE, pas l'adjudication.

<details><summary>Pourquoi des lignes sont écartées</summary>

| Verdict et règle | Lignes |
|---|---|
| `REJETER · R3` | 1 031 |
| `REJETER · R1` | 718 |
| `REJETER · R3b` | 18 |
| `REJETER · R5` | 8 |

</details>

---

<a name="4-artcurial"></a>

## 4. Artcurial

`artcurial` · maison de ventes · API JSON interne /ace (Nuxt runtimeConfig)

**Ce qu'elle donne**

| Étape | Lignes | Part du brut |
|---|---|---|
| Brut collecté | 8 625 | 100 % |
| Filtre 0 — c'est une montre | 5 520 | 64 % |
| Filtre 1 — référence constructeur | 2 912 | 34 % |
| Socle — + date + transaction | 2 912 | 34 % |

**Natures de prix** — réalisé 5 520  
**Devises** — EUR 5 520  
**Période** — 2007 → 2026 (19 années)  
**Montant médian** — 3 500  
**Régime de frais** — MARTEAU NU  

**Ce qu'elle remplit**

| montant | devise | date | marque | référence | modèle | année | boîtier | diamètre | mouvement | cadran | estimation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 100 % | 100 % | 100 % | 100 % | 53 % | 11 % | 86 % | 91 % | 0 % | 57 % | 58 % | 100 % |

**D'où vient la donnée**

- Référence : `extrait_titre` 2 414 · `extrait_description` 498
- Nature du prix : `champ_dedie` 5 520
- Statut d'annonce : sold 5 520

**Ce qu'il faut savoir**

Marteau nu, dix-neuf ans de profondeur. L'API ne sert que les lots vendus : biais de survie assumé.

> **Réserve déclarée** — l'API ne sert que les lots vendus : biais de survie assume

*robots.txt : OK — aucun Disallow sur /ace, robots.txt relu le 11/08/2026*

**Ce qui a été vérifié**

`7/7 montants · 8/8 references · 7/7 dates` — CORRIGE sur la provenance : 495 references venaient de la description et se disaient tirees du titre. Notre montant est le marteau et ne correspond JAMAIS au « Vendu » affiche, qui est frais inclus.

<details><summary>Pourquoi des lignes sont écartées</summary>

| Verdict et règle | Lignes |
|---|---|
| `REJETER · R3` | 2 502 |
| `REJETER · R1` | 504 |
| `REJETER · R0` | 94 |
| `REJETER · R3b` | 5 |

</details>

---

<a name="5-analogshift"></a>

## 5. Analog:Shift

`analogshift` · marchand · Shopify products.json (country=US obligatoire)

**Ce qu'elle donne**

| Étape | Lignes | Part du brut |
|---|---|---|
| Brut collecté | 8 213 | 100 % |
| Filtre 0 — c'est une montre | 7 180 | 87 % |
| Filtre 1 — référence constructeur | 4 075 | 50 % |
| Socle — + date + transaction | 3 712 | 45 % |

**Natures de prix** — vendu 6 500 · demandé 680  
**Devises** — USD 7 180  
**Période** — 2015 → 2026 (12 années)  
**Montant médian** — 7 700  

**Ce qu'elle remplit**

| montant | devise | date | marque | référence | modèle | année | boîtier | diamètre | mouvement | cadran | estimation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 100 % | 100 % | 100 % | 100 % | 88 % | 0 % | 0 % | 0 % | 0 % | 0 % | 0 % | 0 % |

**D'où vient la donnée**

- Référence : `extrait_description` 3 784 · `sku` 2 265 · `jeton_titre` 256 · `extrait_titre` 35
- Nature du prix : `deduite_statut` 7 180
- Statut d'annonce : sold 6 500 · active 680

**Ce qu'il faut savoir**

La référence vit dans le corps de l'annonce, pas dans le titre ; son SKU est un code marchand qu'il ne faut pas confondre.

*robots.txt : OK — /products.json couvert par aucun Disallow, verifie le 11/08/2026*

**Ce qui a été vérifié**

`8/8 montants · 3/8 references · 8/8 natures · 8/8 marques` — Le SKU maison ne sera jamais une reference : 2 946 lignes en portent un, et sont comptees a part. La reference reelle est dans le corps de l'annonce.

<details><summary>Pourquoi des lignes sont écartées</summary>

| Verdict et règle | Lignes |
|---|---|
| `REJETER · R0` | 563 |
| `REJETER · R3` | 317 |
| `REJETER · R1` | 151 |
| `REJETER · R3b` | 1 |
| `REJETER · R5` | 1 |

</details>

---

<a name="6-wannabuyawatch"></a>

## 6. Wanna Buy A Watch

`wannabuyawatch` · marchand · WooCommerce Store API

**Ce qu'elle donne**

| Étape | Lignes | Part du brut |
|---|---|---|
| Brut collecté | 6 441 | 100 % |
| Filtre 0 — c'est une montre | 5 825 | 90 % |
| Filtre 1 — référence constructeur | 4 599 | 71 % |
| Socle — + date + transaction | 0 | 0 % |

**Natures de prix** — demandé 5 825  
**Devises** — USD 5 825  
**Période** — aucune date : ces lignes ne peuvent pas entrer dans le socle  
**Montant médian** — 4 650  

**Ce qu'elle remplit**

| montant | devise | date | marque | référence | modèle | année | boîtier | diamètre | mouvement | cadran | estimation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 100 % | 100 % | 0 % | 100 % | 79 % | 0 % | 63 % | 0 % | 0 % | 0 % | 0 % | 0 % |

**D'où vient la donnée**

- Référence : `champ_dedie` 4 183 · `extrait_titre` 298 · `jeton_titre` 107 · `extrait_description` 11
- Nature du prix : `deduite_statut` 5 825
- Statut d'annonce : sold 5 509 · active 316

**Ce qu'il faut savoir**

L'API conserve le dernier prix demandé de 5 985 montres que la page publique affiche pourtant en « SOLD » sans montant.

*robots.txt : OK — seuls /wp-admin/ et un export d'impression sont interdits*

**Ce qui a été vérifié**

`6/6 montants · 3/6 references · 0/6 natures` — CORRIGE par le meme defaut de stock. 1 218 lignes restent sans aucune reference.

<details><summary>Pourquoi des lignes sont écartées</summary>

| Verdict et règle | Lignes |
|---|---|
| `REJETER · R3` | 403 |
| `REJETER · R1` | 134 |
| `REJETER · R0` | 70 |
| `REJETER · R5` | 5 |
| `REJETER · R3b` | 3 |

</details>

---

<a name="7-lyonandturnbull"></a>

## 7. Lyon & Turnbull

`lyonandturnbull` · maison de ventes · Next.js __NEXT_DATA__, catalogue complet par vente

**Ce qu'elle donne**

| Étape | Lignes | Part du brut |
|---|---|---|
| Brut collecté | 5 763 | 100 % |
| Filtre 0 — c'est une montre | 1 048 | 18 % |
| Filtre 1 — référence constructeur | 352 | 6 % |
| Socle — + date + transaction | 301 | 5 % |

**Natures de prix** — réalisé 968 · estimation 80  
**Devises** — GBP 1 048  
**Période** — 2019 → 2026 (8 années)  
**Montant médian** — 1 800  
**Régime de frais** — MARTEAU NU  

**Ce qu'elle remplit**

| montant | devise | date | marque | référence | modèle | année | boîtier | diamètre | mouvement | cadran | estimation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 100 % | 100 % | 100 % | 100 % | 34 % | 0 % | 0 % | 0 % | 0 % | 0 % | 0 % | 100 % |

**D'où vient la donnée**

- Référence : `extrait_titre` 352
- Nature du prix : `champ_dedie` 1 048
- Statut d'annonce : sold 968 · unsold 80

**Ce qu'il faut savoir**

La seule source qui publie ses INVENDUS. Ses ventes « horlogères » sont à 80 % de la joaillerie, d'où un taux de conservation faible mais justifié.

*robots.txt : OK — verifie le 11/08/2026*

**Ce qui a été vérifié**

`7/8 montants · 8/8 references · 7/7 dates` — La plus propre du lot : marteau nu confirme par champ dedie, bareme de frais et dates de session explicites.

<details><summary>Pourquoi des lignes sont écartées</summary>

| Verdict et règle | Lignes |
|---|---|
| `REJETER · R0` | 4 333 |
| `REJETER · R3` | 341 |
| `REJETER · R1` | 38 |
| `REJETER · R3b` | 2 |
| `REJETER · R5` | 1 |

</details>

---

<a name="8-berrys"></a>

## 8. Berry's Jewellers

`berrys` · marchand · Shopify products.json (country=GB obligatoire)

**Ce qu'elle donne**

| Étape | Lignes | Part du brut |
|---|---|---|
| Brut collecté | 5 638 | 100 % |
| Filtre 0 — c'est une montre | 2 142 | 38 % |
| Filtre 1 — référence constructeur | 2 127 | 38 % |
| Socle — + date + transaction | 397 | 7 % |

**Natures de prix** — demandé 1 743 · vendu 399  
**Devises** — GBP 2 142  
**Période** — 2014 → 2026 (13 années)  
**Montant médian** — 5 995  

**Ce qu'elle remplit**

| montant | devise | date | marque | référence | modèle | année | boîtier | diamètre | mouvement | cadran | estimation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 100 % | 100 % | 100 % | 100 % | 99 % | 0 % | 1 % | 0 % | 0 % | 0 % | 0 % | 0 % |

**D'où vient la donnée**

- Référence : `champ_dedie` 2 125 · `sku` 3 · `jeton_titre` 2
- Nature du prix : `deduite_statut` 2 142
- Statut d'annonce : active 1 743 · sold 399

**Ce qu'il faut savoir**

Détaillant AGRÉÉ : son champ SKU porte la vraie référence constructeur (L38204930, IW503607), pas un code maison. La compter comme un SKU ramenait la source à 183 références au lieu de 2 125.

*robots.txt : OK — verifie le 11/08/2026*

**Ce qui a été vérifié**

`6/6 montants · 6/6 references · 6/6 natures` — CORRIGE. Son champ SKU porte la vraie reference constructeur : la source passe de 183 a 2 125 references exploitables. Sans `country=GB` le prix perd 16,7 % de TVA.

<details><summary>Pourquoi des lignes sont écartées</summary>

| Verdict et règle | Lignes |
|---|---|
| `REJETER · R0` | 3 215 |
| `REJETER · R3` | 147 |
| `REJETER · R1` | 115 |
| `REJETER · R4` | 19 |

</details>

---

<a name="9-keystone"></a>

## 9. The Keystone

`keystone` · marchand · Shopify products.json (currency=USD&country=US obligatoire)

**Ce qu'elle donne**

| Étape | Lignes | Part du brut |
|---|---|---|
| Brut collecté | 5 020 | 100 % |
| Filtre 0 — c'est une montre | 4 945 | 99 % |
| Filtre 1 — référence constructeur | 4 310 | 86 % |
| Socle — + date + transaction | 4 081 | 81 % |

**Natures de prix** — vendu 4 637 · demandé 308  
**Devises** — USD 4 945  
**Période** — 2018 → 2026 (9 années)  
**Montant médian** — 23 500  

**Ce qu'elle remplit**

| montant | devise | date | marque | référence | modèle | année | boîtier | diamètre | mouvement | cadran | estimation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 100 % | 100 % | 100 % | 100 % | 100 % | 0 % | 0 % | 0 % | 0 % | 0 % | 0 % | 0 % |

**D'où vient la donnée**

- Référence : `extrait_titre` 3 855 · `sku` 635 · `extrait_description` 395 · `jeton_titre` 60
- Nature du prix : `deduite_statut` 4 945
- Statut d'annonce : sold 4 637 · active 308

**Ce qu'il faut savoir**

Le schéma le mieux structuré des marchands : un bloc « Reference / Year / Brand » dans la description, et huit ans de mise en ligne.

*robots.txt : OK — products.json non interdit, aucun Crawl-delay*

**Ce qui a été vérifié**

`8/8 montants · 8/8 references · 8/8 natures · 8/8 marques` — 27 fiches a 1,00 USD, prix sentinelle reellement publie par le site — desormais ecartees par le plancher du moteur.

<details><summary>Pourquoi des lignes sont écartées</summary>

| Verdict et règle | Lignes |
|---|---|
| `REJETER · R1` | 44 |
| `REJETER · R3` | 19 |
| `REJETER · R0` | 12 |

</details>

---

<a name="10-watchrecon"></a>

## 10. WatchRecon

`watchrecon` · forums · HTML structure (.galleryItemContainer)

**Ce qu'elle donne**

| Étape | Lignes | Part du brut |
|---|---|---|
| Brut collecté | 4 950 | 100 % |
| Filtre 0 — c'est une montre | 4 352 | 88 % |
| Filtre 1 — référence constructeur | 3 232 | 65 % |
| Socle — + date + transaction | 0 | 0 % |

**Natures de prix** — demandé 4 352  
**Devises** — USD 4 320 · EUR 26 · GBP 6  
**Période** — 2026 → 2026 (1 années)  
**Montant médian** — 3 500  

**Ce qu'elle remplit**

| montant | devise | date | marque | référence | modèle | année | boîtier | diamètre | mouvement | cadran | estimation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 100 % | 100 % | 100 % | 100 % | 74 % | 0 % | 0 % | 0 % | 0 % | 0 % | 0 % | 0 % |

**D'où vient la donnée**

- Référence : `jeton_titre` 2 560 · `extrait_titre` 672
- Nature du prix : `constante_source` 4 352
- Statut d'annonce : unknown 4 352

**Ce qu'il faut savoir**

Agrégateur de forums, la source la plus fraîche du dossier. Un tiers de ses titres portent une référence qu'on ne lisait pas. La nature du prix y reste déclarée, jamais mesurée.

*robots.txt : OK sous conditions — 'last_days=' et 'page_size=' interdits, non utilises*

**Ce qui a été vérifié**

`8/8 montants · 0/8 references avant correction` — CORRIGE. Un tiers des titres portaient une reference qu'on ne lisait pas : 3 232 lignes en ont une aujourd'hui. Le dedoublonnage comptait aussi 1 709 annonces deux fois.

<details><summary>Pourquoi des lignes sont écartées</summary>

| Verdict et règle | Lignes |
|---|---|
| `QUARANTAINE · R7a` | 392 |
| `REJETER · R3` | 102 |
| `REJETER · R1` | 69 |
| `REJETER · R5` | 35 |

</details>

---

<a name="11-loupethis"></a>

## 11. Loupe This

`loupethis` · maison de ventes · API JSON:API publique api.loupethis.com/api/v1/auctions

**Ce qu'elle donne**

| Étape | Lignes | Part du brut |
|---|---|---|
| Brut collecté | 4 220 | 100 % |
| Filtre 0 — c'est une montre | 3 902 | 92 % |
| Filtre 1 — référence constructeur | 3 169 | 75 % |
| Socle — + date + transaction | 3 169 | 75 % |

**Natures de prix** — réalisé 3 902  
**Devises** — USD 3 902  
**Période** — 2021 → 2026 (6 années)  
**Montant médian** — 9 000  
**Régime de frais** — MARTEAU NU  

**Ce qu'elle remplit**

| montant | devise | date | marque | référence | modèle | année | boîtier | diamètre | mouvement | cadran | estimation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 100 % | 100 % | 100 % | 98 % | 81 % | 0 % | 0 % | 0 % | 0 % | 0 % | 0 % | 0 % |

**D'où vient la donnée**

- Référence : `extrait_titre` 3 169
- Nature du prix : `champ_dedie` 3 902
- Statut d'annonce : sold 3 902

**Ce qu'il faut savoir**

La seule source qui publie À LA FOIS le marteau et le prix frais inclus. On charge le marteau ; la relation ×1,10 est vérifiée sur 243 lots sans exception.

> **Réserve déclarée** — invendus non publies ; estimation absente de l'API

*robots.txt : OK — 'Disallow:' vide, rien n'est interdit*

**Ce qui a été vérifié**

`8/8 montants · 8/8 references · 8/8 dates` — Marteau nu verifie sur 4 220 lots sur 4 220. Attention au regime economique et non au drapeau : les frais n'y sont que de 10 %, contre 25 a 30 % ailleurs.

<details><summary>Pourquoi des lignes sont écartées</summary>

| Verdict et règle | Lignes |
|---|---|
| `REJETER · R3` | 236 |
| `REJETER · R1` | 81 |
| `REJETER · R5` | 1 |

</details>

---

<a name="12-monacolegend"></a>

## 12. Monaco Legend Auctions

`monacolegend` · maison de ventes · JSON-LD EventSeries + attributs data- des pages de vente

**Ce qu'elle donne**

| Étape | Lignes | Part du brut |
|---|---|---|
| Brut collecté | 4 188 | 100 % |
| Filtre 0 — c'est une montre | 4 008 | 96 % |
| Filtre 1 — référence constructeur | 2 492 | 60 % |
| Socle — + date + transaction | 2 229 | 53 % |

**Natures de prix** — réalisé 3 587 · estimation 421  
**Devises** — EUR 3 689 · CHF 319  
**Période** — 2019 → 2026 (8 années)  
**Montant médian** — 20 000  
**Régime de frais** — frais acheteur INCLUS  

**Ce qu'elle remplit**

| montant | devise | date | marque | référence | modèle | année | boîtier | diamètre | mouvement | cadran | estimation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 100 % | 100 % | 100 % | 100 % | 62 % | 0 % | 97 % | 0 % | 0 % | 0 % | 0 % | 100 % |

**D'où vient la donnée**

- Référence : `extrait_titre` 2 402 · `jeton_titre` 90
- Nature du prix : `champ_dedie` 4 008
- Statut d'annonce : sold 3 587 · unsold 421

**Ce qu'il faut savoir**

Sept ans d'enchères exclusivement horlogères en 20 requêtes — le meilleur rapport volume/coût du dossier. Publie ses INVENDUS (421 lots) et deux devises. Prix FRAIS ACHETEUR INCLUS, comme Christie's : ne pas le comparer à un marteau nu.

> **Réserve déclarée** — prix frais acheteur INCLUS, comme Christie's — pas un marteau nu

*robots.txt : OK — /auction autorise ; /livewire interdit et non utilise*

**Ce qui a été vérifié**

`structure revérifiée avant collecte` — Le JSON-LD était passé d'un `EventSeries` nu à un `@graph` depuis la reconnaissance : le code lit les deux. Rejeu hors ligne identique à la collecte, 4 188 sur 4 188.

<details><summary>Pourquoi des lignes sont écartées</summary>

| Verdict et règle | Lignes |
|---|---|
| `REJETER · R1` | 104 |
| `REJETER · R3` | 63 |
| `REJETER · R5` | 9 |
| `REJETER · R3b` | 4 |

</details>

---

<a name="13-watchtrader"></a>

## 13. Watchtrader

`watchtrader` · marchand · WooCommerce Store API (/wp-json/wc/store/products)

**Ce qu'elle donne**

| Étape | Lignes | Part du brut |
|---|---|---|
| Brut collecté | 4 090 | 100 % |
| Filtre 0 — c'est une montre | 4 070 | 100 % |
| Filtre 1 — référence constructeur | 4 067 | 99 % |
| Socle — + date + transaction | 0 | 0 % |

**Natures de prix** — demandé 4 070  
**Devises** — GBP 4 070  
**Période** — aucune date : ces lignes ne peuvent pas entrer dans le socle  
**Montant médian** — 9 950  

**Ce qu'elle remplit**

| montant | devise | date | marque | référence | modèle | année | boîtier | diamètre | mouvement | cadran | estimation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 100 % | 100 % | 0 % | 100 % | 100 % | 0 % | 97 % | 100 % | 0 % | 0 % | 0 % | 0 % |

**D'où vient la donnée**

- Référence : `champ_dedie` 4 065 · `extrait_description` 2
- Nature du prix : `deduite_statut` 4 070
- Statut d'annonce : sold 3 477 · active 593

**Ce qu'il faut savoir**

La référence est un CHAMP DÉDIÉ rempli à 99,8 %. Mais 3 477 de ses 4 070 fiches ont quitté le catalogue : ce sont des archives, pas des offres vives, et la source ne date rien.

> **Réserve déclarée** — site refait en 02/2025 : 18 mois de profondeur, date de mise en ligne

*robots.txt : OK — /wp-json/ n'est pas interdit, verifie le 28/08/2026*

**Ce qui a été vérifié**

`6/6 montants · 6/6 references · 0/6 natures` — CORRIGE. 3 477 de ses 4 070 fiches ont quitte le catalogue et sortaient « en vente » : le moteur lisait un champ de stock que l'API n'envoie pas.

<details><summary>Pourquoi des lignes sont écartées</summary>

| Verdict et règle | Lignes |
|---|---|
| `QUARANTAINE · R7a` | 9 |
| `REJETER · R0` | 6 |
| `REJETER · R3` | 3 |
| `REJETER · R1` | 2 |

</details>

---

<a name="14-topper"></a>

## 14. Topper Fine Jewelers

`topper` · détaillant · Shopify products.json (currency=USD&country=US)

**Ce qu'elle donne**

| Étape | Lignes | Part du brut |
|---|---|---|
| Brut collecté | 3 687 | 100 % |
| Filtre 0 — c'est une montre | 2 404 | 65 % |
| Filtre 1 — référence constructeur | 2 238 | 61 % |
| Socle — + date + transaction | 0 | 0 % |

**Natures de prix** — prix neuf 2 404  
**Devises** — USD 2 404  
**Période** — 2018 → 2026 (9 années)  
**Montant médian** — 4 400  

**Ce qu'elle remplit**

| montant | devise | date | marque | référence | modèle | année | boîtier | diamètre | mouvement | cadran | estimation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 100 % | 100 % | 100 % | 100 % | 100 % | 0 % | 0 % | 0 % | 0 % | 0 % | 0 % | 0 % |

**D'où vient la donnée**

- Référence : `jeton_titre` 2 235 · `sku` 161 · `extrait_titre` 3
- Nature du prix : `deduite_statut` 2 404
- Statut d'annonce : active 1 387 · inactive 1 017

**Ce qu'il faut savoir**

Détaillant de NEUF : `available=false` y signifie rupture de stock, pas vente. Le traiter comme une vente fabriquerait de fausses transactions.

> **Réserve déclarée** — catalogue mixte : ~1 000 fiches de joaillerie, ecartees par le filtre

*robots.txt : OK — products.json non interdit*

**Ce qui a été vérifié**

`6/6 montants · 5/6 references · 6/6 natures` — La regle « rupture n'est pas vente » tient : 100 % en prix neuf. Une Breitling Premier publiee a 500 USD par la boutique elle-meme.

<details><summary>Pourquoi des lignes sont écartées</summary>

| Verdict et règle | Lignes |
|---|---|
| `REJETER · R0` | 991 |
| `REJETER · R3` | 248 |
| `REJETER · R1` | 44 |

</details>

---

<a name="15-bulangandsons"></a>

## 15. Bulang and Sons

`bulangandsons` · marchand · Shopify products.json

**Ce qu'elle donne**

| Étape | Lignes | Part du brut |
|---|---|---|
| Brut collecté | 3 683 | 100 % |
| Filtre 0 — c'est une montre | 2 604 | 71 % |
| Filtre 1 — référence constructeur | 2 379 | 65 % |
| Socle — + date + transaction | 1 583 | 43 % |

**Natures de prix** — vendu 1 746 · demandé 858  
**Devises** — EUR 2 604  
**Période** — 2026 → 2026 (1 années)  
**Montant médian** — 9 500  

**Ce qu'elle remplit**

| montant | devise | date | marque | référence | modèle | année | boîtier | diamètre | mouvement | cadran | estimation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 100 % | 100 % | 100 % | 100 % | 100 % | 0 % | 0 % | 0 % | 0 % | 0 % | 0 % | 0 % |

**D'où vient la donnée**

- Référence : `extrait_titre` 1 180 · `jeton_titre` 1 090 · `sku` 225 · `extrait_description` 109
- Nature du prix : `declaree_tag` 2 556 · `deduite_statut` 48
- Statut d'annonce : sold 1 746 · active 858

**Ce qu'il faut savoir**

`available` ne dit pas la vente ici, ce sont les tags. Et sa description énumère les BRACELETS livrés : 443 fiches portaient la référence du bracelet au lieu de celle de la montre.

> **Réserve déclarée** — migration de boutique en 08/2025 : les dates de la source ne datent rien

*robots.txt : OK — /products.json non interdit*

**Ce qui a été vérifié**

`8/8 montants · 5/8 references · 8/8 natures · 8/8 marques` — CORRIGE. 443 fiches portaient la reference du BRACELET livre avec la montre, et 305 un prix de 1 EUR. Le titre est desormais epuise avant la description.

<details><summary>Pourquoi des lignes sont écartées</summary>

| Verdict et règle | Lignes |
|---|---|
| `REJETER · R0` | 944 |
| `REJETER · R3` | 80 |
| `REJETER · R5` | 34 |
| `REJETER · R1` | 21 |

</details>

---

<a name="16-craft_and_tailored"></a>

## 16. Craft & Tailored

`craft_and_tailored` · marchand · Shopify products.json (country=US obligatoire)

**Ce qu'elle donne**

| Étape | Lignes | Part du brut |
|---|---|---|
| Brut collecté | 3 646 | 100 % |
| Filtre 0 — c'est une montre | 3 294 | 90 % |
| Filtre 1 — référence constructeur | 3 097 | 85 % |
| Socle — + date + transaction | 3 039 | 83 % |

**Natures de prix** — vendu 3 232 · demandé 62  
**Devises** — USD 3 294  
**Période** — 2016 → 2026 (11 années)  
**Montant médian** — 5 650  

**Ce qu'elle remplit**

| montant | devise | date | marque | référence | modèle | année | boîtier | diamètre | mouvement | cadran | estimation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 100 % | 100 % | 100 % | 100 % | 100 % | 0 % | 64 % | 0 % | 0 % | 0 % | 0 % | 0 % |

**D'où vient la donnée**

- Référence : `extrait_titre` 2 933 · `sku` 196 · `jeton_titre` 153 · `extrait_description` 11
- Nature du prix : `deduite_statut` 3 294
- Statut d'annonce : sold 3 232 · active 62

**Ce qu'il faut savoir**

97 % de son catalogue est vendu. Le plus gros piège de devise du dossier : sans `country=US`, -17,85 % sur la moitié de la base.

*robots.txt : OK — 'Allow: /' ; les restrictions Shopify visent le checkout, pas le catalogue*

**Ce qui a été vérifié**

`8/8 montants · 7/8 references · 8/8 natures · 6/8 marques` — CORRIGE. `vendor` valait litteralement « Other » sur les petites maisons ; le moteur relit le titre. Son collecteur maison a ete rendu au moteur commun.

<details><summary>Pourquoi des lignes sont écartées</summary>

| Verdict et règle | Lignes |
|---|---|
| `REJETER · R0` | 131 |
| `REJETER · R3` | 113 |
| `REJETER · R1` | 88 |
| `REJETER · R5` | 19 |
| `QUARANTAINE · R7a` | 1 |

</details>

---

<a name="17-cwsellors"></a>

## 17. CW Sellors

`cwsellors` · marchand · Shopify /collections/watches/products.json (country=GB obligatoire)

**Ce qu'elle donne**

| Étape | Lignes | Part du brut |
|---|---|---|
| Brut collecté | 2 948 | 100 % |
| Filtre 0 — c'est une montre | 2 432 | 82 % |
| Filtre 1 — référence constructeur | 355 | 12 % |
| Socle — + date + transaction | 121 | 4 % |

**Natures de prix** — demandé 1 232 · vendu 1 200  
**Devises** — GBP 2 432  
**Période** — 2017 → 2026 (10 années)  
**Montant médian** — 1 579  

**Ce qu'elle remplit**

| montant | devise | date | marque | référence | modèle | année | boîtier | diamètre | mouvement | cadran | estimation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 100 % | 100 % | 100 % | 100 % | 100 % | 0 % | 0 % | 0 % | 0 % | 0 % | 0 % | 0 % |

**D'où vient la donnée**

- Référence : `sku` 2 077 · `jeton_titre` 224 · `extrait_description` 128 · `extrait_titre` 3
- Nature du prix : `deduite_statut` 2 432
- Statut d'annonce : active 1 232 · sold 1 200

**Ce qu'il faut savoir**

Mélange prix TTC et HT dans le même flux sans champ distinctif : un écart de 20 % peut n'être que de la TVA.

> **Réserve déclarée** — TTC et HT melanges dans le meme flux, sans champ distinctif

*robots.txt : OK — verifie le 11/08/2026*

**Ce qui a été vérifié**

`6/6 montants · 1/6 references · 6/6 natures` — Son SKU est un vrai code maison (« DOX-333 ») : 12 % de references seulement, et c'est exact. Ses 1 200 « vendues » sont des prix catalogue de detaillant agree.

<details><summary>Pourquoi des lignes sont écartées</summary>

| Verdict et règle | Lignes |
|---|---|
| `REJETER · R3` | 405 |
| `REJETER · R1` | 103 |
| `REJETER · R0` | 8 |

</details>

---

<a name="18-awco"></a>

## 18. Amsterdam Watch Company

`awco` · marchand · WooCommerce Store API (awco.nl)

**Ce qu'elle donne**

| Étape | Lignes | Part du brut |
|---|---|---|
| Brut collecté | 2 686 | 100 % |
| Filtre 0 — c'est une montre | 2 099 | 78 % |
| Filtre 1 — référence constructeur | 1 736 | 65 % |
| Socle — + date + transaction | 0 | 0 % |

**Natures de prix** — demandé 2 099  
**Devises** — EUR 2 099  
**Période** — aucune date : ces lignes ne peuvent pas entrer dans le socle  
**Montant médian** — 6 250  

**Ce qu'elle remplit**

| montant | devise | date | marque | référence | modèle | année | boîtier | diamètre | mouvement | cadran | estimation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 100 % | 100 % | 0 % | 100 % | 83 % | 0 % | 91 % | 63 % | 0 % | 0 % | 0 % | 0 % |

**D'où vient la donnée**

- Référence : `champ_dedie` 1 148 · `extrait_titre` 553 · `jeton_titre` 33 · `extrait_description` 2
- Nature du prix : `deduite_statut` 2 099
- Statut d'annonce : sold 1 805 · active 294

**Ce qu'il faut savoir**

Un prix NÉGATIF y marque une vente, la valeur absolue étant le dernier prix demandé. Convention unique au dossier.

> **Réserve déclarée** — la taxonomie de marque melange 'Omega Speedmaster' et 'Other brands'

*robots.txt : OK — wp-json non interdit*

**Ce qui a été vérifié**

`6/6 montants · 4/6 references · 2/6 natures` — CORRIGE par le meme defaut de stock. Le champ SKU est vide chez ce marchand : la reference vient du titre.

<details><summary>Pourquoi des lignes sont écartées</summary>

| Verdict et règle | Lignes |
|---|---|
| `REJETER · R0` | 276 |
| `REJETER · R3` | 213 |
| `QUARANTAINE · R7a` | 80 |
| `REJETER · R1` | 18 |

</details>

---

<a name="19-sworders"></a>

## 19. Sworders

`sworders` · maison de ventes · recherche par marque, 96 lots par page

**Ce qu'elle donne**

| Étape | Lignes | Part du brut |
|---|---|---|
| Brut collecté | 2 506 | 100 % |
| Filtre 0 — c'est une montre | 1 504 | 60 % |
| Filtre 1 — référence constructeur | 247 | 10 % |
| Socle — + date + transaction | 0 | 0 % |

**Natures de prix** — réalisé 1 504  
**Devises** — GBP 1 504  
**Période** — aucune date : ces lignes ne peuvent pas entrer dans le socle  
**Montant médian** — 350  
**Régime de frais** — MARTEAU NU  

**Ce qu'elle remplit**

| montant | devise | date | marque | référence | modèle | année | boîtier | diamètre | mouvement | cadran | estimation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 100 % | 100 % | 0 % | 100 % | 16 % | 0 % | 0 % | 0 % | 0 % | 0 % | 0 % | 0 % |

**D'où vient la donnée**

- Référence : `jeton_titre` 245 · `extrait_titre` 2
- Nature du prix : `deduite_statut` 1 504
- Statut d'annonce : sold 1 504

**Ce qu'il faut savoir**

Atteinte par sa recherche, marque par marque : son index ne publie que 57 ventes récentes et ses ventes sont à 80 % joaillières. Marteau nu vérifié. Aucune date : la source ne la publie que sur la fiche du lot, à 10 s de délai imposé par requête.

> **Réserve déclarée** — aucune date de vente : la source ne la publie que sur la fiche du lot

*robots.txt : OK — Crawl-delay: 10 respecte*

**Ce qui a été vérifié**

`régime de frais vérifié arithmétiquement` — Ses conditions disent « hammer price plus a buyer's premium » de 27 %, mais cela dit ce qu'on paie, pas ce qu'affiche la page. Le contrôle tranche : 77 % des montants tombent sur un échelon d'enchère tels quels, 8 % après division par 1,27. C'est un marteau.

<details><summary>Pourquoi des lignes sont écartées</summary>

| Verdict et règle | Lignes |
|---|---|
| `REJETER · R1` | 550 |
| `REJETER · R3` | 343 |
| `REJETER · R4` | 109 |

</details>

---

<a name="20-watchesofswitzerland"></a>

## 20. Watches of Switzerland

`watchesofswitzerland` · détaillant · sitemap produit + API OCC v2 (SAP Commerce), une requete par fiche

**Ce qu'elle donne**

| Étape | Lignes | Part du brut |
|---|---|---|
| Brut collecté | 2 475 | 100 % |
| Filtre 0 — c'est une montre | 2 029 | 82 % |
| Filtre 1 — référence constructeur | 1 559 | 63 % |
| Socle — + date + transaction | 0 | 0 % |

**Natures de prix** — prix neuf 2 029  
**Devises** — GBP 2 029  
**Période** — aucune date : ces lignes ne peuvent pas entrer dans le socle  
**Montant médian** — 3 600  

**Ce qu'elle remplit**

| montant | devise | date | marque | référence | modèle | année | boîtier | diamètre | mouvement | cadran | estimation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 100 % | 100 % | 0 % | 100 % | 77 % | 100 % | 0 % | 0 % | 0 % | 0 % | 0 % | 0 % |

**D'où vient la donnée**

- Référence : `extrait_titre` 1 559
- Nature du prix : `deduite_statut` 2 029
- Statut d'annonce : inactive 1 371 · active 658

**Ce qu'il faut savoir**

Détaillant agréé : source du prix NEUF au tarif officiel. Collecte bornée à 2 500 fiches sur 33 106 — une requête par fiche, neuf heures pour le tout.

> **Réserve déclarée** — une fiche du sitemap peut etre epuisee ; le prix reste affiche

*robots.txt : OK — /search et '*q=' interdits et non utilises ; les fiches /p/ sont libres*

**Ce qui a été vérifié**

`6/6 montants · 3/6 references · 6/6 natures` — API irreprochable. 470 lignes sans reference alors qu'elle est dans l'URL : defaut de rappel, pas de justesse.

<details><summary>Pourquoi des lignes sont écartées</summary>

| Verdict et règle | Lignes |
|---|---|
| `REJETER · R0` | 332 |
| `REJETER · R1` | 56 |
| `REJETER · R3` | 52 |
| `QUARANTAINE · R7a` | 6 |

</details>

---

<a name="21-fortuna"></a>

## 21. Fortuna

`fortuna` · maison de ventes · API REST WordPress /wp-json/wp/v2/lots

**Ce qu'elle donne**

| Étape | Lignes | Part du brut |
|---|---|---|
| Brut collecté | 2 010 | 100 % |
| Filtre 0 — c'est une montre | 1 779 | 89 % |
| Filtre 1 — référence constructeur | 1 007 | 50 % |
| Socle — + date + transaction | 1 007 | 50 % |

**Natures de prix** — réalisé 1 779  
**Devises** — USD 1 779  
**Période** — 2016 → 2026 (11 années)  
**Montant médian** — 3 500  
**Régime de frais** — MIXTE — 1 748 frais inclus, 31 marteau nu  

**Ce qu'elle remplit**

| montant | devise | date | marque | référence | modèle | année | boîtier | diamètre | mouvement | cadran | estimation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 100 % | 100 % | 100 % | 99 % | 57 % | 0 % | 0 % | 0 % | 0 % | 0 % | 0 % | 100 % |

**D'où vient la donnée**

- Référence : `extrait_titre` 602 · `extrait_description` 386 · `jeton_titre` 19
- Nature du prix : `champ_dedie` 1 779
- Statut d'annonce : sold 1 779

**Ce qu'il faut savoir**

Son champ `hammer_price` n'est un marteau que sur les 31 lots où les frais sont publiés ; sur les 1 713 autres il les inclut déjà. Nous avions généralisé depuis 1,7 % du corpus — la seule population qui se comporte autrement.

> **Réserve déclarée** — invendus non publies ; 5 ventes sur 145 ont un bareme de frais degressif

*robots.txt : OK — /wp-json/ n'est pas interdit, verifie le 28/08/2026*

**Ce qui a été vérifié**

`8/8 montants · 8/8 references · 8/8 dates` — CORRIGE, et c'est la correction la plus lourde : `hammer_price` n'est un marteau que sur 31 lots ; sur les 1 713 autres il inclut deja 25 % de frais. Les dates et la taxonomie des marques sont desormais dans le brut : la source est rejouable de bout en bout.

<details><summary>Pourquoi des lignes sont écartées</summary>

| Verdict et règle | Lignes |
|---|---|
| `REJETER · R3` | 188 |
| `REJETER · R1` | 42 |
| `REJETER · R5` | 1 |

</details>

---

<a name="22-globalwatchshop"></a>

## 22. Global Watch Shop

`globalwatchshop` · marchand · WooCommerce Store API

**Ce qu'elle donne**

| Étape | Lignes | Part du brut |
|---|---|---|
| Brut collecté | 971 | 100 % |
| Filtre 0 — c'est une montre | 804 | 83 % |
| Filtre 1 — référence constructeur | 804 | 83 % |
| Socle — + date + transaction | 0 | 0 % |

**Natures de prix** — demandé 804  
**Devises** — GBP 804  
**Période** — aucune date : ces lignes ne peuvent pas entrer dans le socle  
**Montant médian** — 9 950  

**Ce qu'elle remplit**

| montant | devise | date | marque | référence | modèle | année | boîtier | diamètre | mouvement | cadran | estimation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 100 % | 100 % | 0 % | 100 % | 100 % | 0 % | 0 % | 100 % | 0 % | 0 % | 0 % | 0 % |

**D'où vient la donnée**

- Référence : `champ_dedie` 802 · `jeton_titre` 2
- Nature du prix : `deduite_statut` 804
- Statut d'annonce : sold 614 · active 190

**Ce qu'il faut savoir**

Référence en champ dédié à 100 %, mais 38 % des fiches sont à prix zéro : du prix sur demande masqué.

> **Réserve déclarée** — 38 % des fiches sont a prix zero (prix sur demande)

*robots.txt : OK — seul ?rest_route= est bloque, /wp-json/ ne l'est pas*

**Ce qui a été vérifié**

`6/6 montants · 6/6 references · 3/6 natures` — CORRIGE par le meme defaut de stock. Sa fiche Breitling se contredit elle-meme entre son champ MODEL et son titre ; on recopie le champ.

<details><summary>Pourquoi des lignes sont écartées</summary>

| Verdict et règle | Lignes |
|---|---|
| `QUARANTAINE · R7a` | 82 |
| `REJETER · R0` | 70 |
| `REJETER · R5` | 12 |
| `REJETER · R3` | 3 |

</details>

---

<a name="23-acollectedman"></a>

## 23. A Collected Man

`acollectedman` · marchand · Shopify products.json

**Ce qu'elle donne**

| Étape | Lignes | Part du brut |
|---|---|---|
| Brut collecté | 962 | 100 % |
| Filtre 0 — c'est une montre | 650 | 68 % |
| Filtre 1 — référence constructeur | 412 | 43 % |
| Socle — + date + transaction | 407 | 42 % |

**Natures de prix** — vendu 636 · demandé 14  
**Devises** — GBP 650  
**Période** — 2015 → 2026 (11 années)  
**Montant médian** — 45 000  

**Ce qu'elle remplit**

| montant | devise | date | marque | référence | modèle | année | boîtier | diamètre | mouvement | cadran | estimation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 100 % | 100 % | 100 % | 100 % | 100 % | 0 % | 1 % | 0 % | 0 % | 0 % | 0 % | 0 % |

**D'où vient la donnée**

- Référence : `jeton_titre` 329 · `sku` 238 · `extrait_titre` 44 · `extrait_description` 39
- Nature du prix : `deduite_statut` 650
- Statut d'annonce : sold 636 · active 14

**Ce qu'il faut savoir**

Horlogerie indépendante haut de gamme. Ses manquants en référence n'en sont pas : Journe et Voutilainen n'ont réellement pas de référence constructeur.

> **Réserve déclarée** — l'horlogerie independante n'a souvent pas de reference constructeur

*robots.txt : OK — /products.json non interdit, Crawl-delay seulement pour Ahrefs*

**Ce qui a été vérifié**

`6/6 montants · 2/6 references · 6/6 natures` — Son SKU est un code maison honnete. La vraie reference est parfois dans l'URL et nous echappe.

<details><summary>Pourquoi des lignes sont écartées</summary>

| Verdict et règle | Lignes |
|---|---|
| `REJETER · R0` | 237 |
| `REJETER · R3` | 70 |
| `REJETER · R1` | 5 |

</details>

---

<a name="24-chronofinder"></a>

## 24. Chronofinder

`chronofinder` · marchand · WooCommerce Store API

**Ce qu'elle donne**

| Étape | Lignes | Part du brut |
|---|---|---|
| Brut collecté | 592 | 100 % |
| Filtre 0 — c'est une montre | 589 | 99 % |
| Filtre 1 — référence constructeur | 585 | 99 % |
| Socle — + date + transaction | 0 | 0 % |

**Natures de prix** — demandé 589  
**Devises** — GBP 589  
**Période** — aucune date : ces lignes ne peuvent pas entrer dans le socle  
**Montant médian** — 11 250  

**Ce qu'elle remplit**

| montant | devise | date | marque | référence | modèle | année | boîtier | diamètre | mouvement | cadran | estimation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 100 % | 100 % | 0 % | 100 % | 99 % | 0 % | 0 % | 96 % | 0 % | 0 % | 0 % | 0 % |

**D'où vient la donnée**

- Référence : `champ_dedie` 400 · `jeton_titre` 118 · `extrait_description` 67
- Nature du prix : `deduite_statut` 589
- Statut d'annonce : sold 462 · active 127

**Ce qu'il faut savoir**

Petite mais intégralement prixée — aucune fiche en « prix sur demande », ce qui n'arrive nulle part ailleurs.

*robots.txt : OK — /wp-json/ autorise*

**Ce qui a été vérifié**

`6/6 montants · 5/6 references · 2/6 natures` — CORRIGE par le meme defaut de stock. Une reference divergente trouvee sur un champ dedie (18238 contre 18038 en ligne).

<details><summary>Pourquoi des lignes sont écartées</summary>

| Verdict et règle | Lignes |
|---|---|
| `REJETER · R1` | 2 |
| `REJETER · R0` | 1 |

</details>

---

<a name="25-watchesofdistinction"></a>

## 25. Watches of Distinction

`watchesofdistinction` · marchand · WooCommerce Store API

**Ce qu'elle donne**

| Étape | Lignes | Part du brut |
|---|---|---|
| Brut collecté | 507 | 100 % |
| Filtre 0 — c'est une montre | 496 | 98 % |
| Filtre 1 — référence constructeur | 469 | 93 % |
| Socle — + date + transaction | 0 | 0 % |

**Natures de prix** — demandé 496  
**Devises** — GBP 496  
**Période** — aucune date : ces lignes ne peuvent pas entrer dans le socle  
**Montant médian** — 5 495  

**Ce qu'elle remplit**

| montant | devise | date | marque | référence | modèle | année | boîtier | diamètre | mouvement | cadran | estimation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 100 % | 100 % | 0 % | 100 % | 95 % | 0 % | 90 % | 99 % | 0 % | 0 % | 0 % | 0 % |

**D'où vient la donnée**

- Référence : `extrait_titre` 464 · `jeton_titre` 5
- Nature du prix : `deduite_statut` 496
- Statut d'annonce : active 409 · sold 87

**Ce qu'il faut savoir**

Fiche très structurée : marque à 100 %, référence à 93 %, année exacte à 90 %, matière du boîtier à 98 %. Mais deux tiers de son catalogue sont à prix zéro — 4 962 fiches écartées faute de montant.

> **Réserve déclarée** — aucune date : la source ne publie ni mise en ligne ni date de vente

*robots.txt : OK — /wp-json/ non interdit, verifie le 02/09/2026*

**Ce qui a été vérifié**

`année recoupée titre contre attribut` — Son attribut d'année donne une DÉCENNIE — « 2010's » — quand le titre porte le millésime : 401 lignes sur 496 divergeaient, dont une montre de 2020 datée de 2010. Le titre prime désormais, zéro divergence.

<details><summary>Pourquoi des lignes sont écartées</summary>

| Verdict et règle | Lignes |
|---|---|
| `REJETER · R3` | 8 |
| `QUARANTAINE · R7a` | 3 |

</details>

---

<a name="26-amsterdamvintage"></a>

## 26. Amsterdam Vintage Watches

`amsterdamvintage` · marchand · WooCommerce Store API

**Ce qu'elle donne**

| Étape | Lignes | Part du brut |
|---|---|---|
| Brut collecté | 342 | 100 % |
| Filtre 0 — c'est une montre | 269 | 79 % |
| Filtre 1 — référence constructeur | 257 | 75 % |
| Socle — + date + transaction | 0 | 0 % |

**Natures de prix** — demandé 269  
**Devises** — EUR 269  
**Période** — aucune date : ces lignes ne peuvent pas entrer dans le socle  
**Montant médian** — 22 800  

**Ce qu'elle remplit**

| montant | devise | date | marque | référence | modèle | année | boîtier | diamètre | mouvement | cadran | estimation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 100 % | 100 % | 0 % | 98 % | 96 % | 0 % | 94 % | 87 % | 0 % | 0 % | 0 % | 0 % |

**D'où vient la donnée**

- Référence : `champ_dedie` 246 · `jeton_titre` 10 · `extrait_description` 1
- Nature du prix : `deduite_statut` 269
- Statut d'annonce : sold 228 · active 41

**Ce qu'il faut savoir**

La fiche la mieux remplie du dossier : référence, année, matière et numéro de série en champs DÉDIÉS — 91 % de références publiées, 96 % d'années. Mais le prix est SUPPRIMÉ à la vente : seul le stock vivant a un montant.

> **Réserve déclarée** — le prix est retire a la vente : la source ne publie que son stock vivant

*robots.txt : OK — /wp-json/ autorise*

**Ce qui a été vérifié**

`branchée le 29/08 sur le moteur WooCommerce` — Ni attribut ni champ natif de marque : ses 342 fiches sortaient sans marque et R3 les rejetait toutes. Le repli sur le titre a été ajouté au moteur — il fait aussi gagner des marques à Wanna Buy A Watch et AWCO.

<details><summary>Pourquoi des lignes sont écartées</summary>

| Verdict et règle | Lignes |
|---|---|
| `REJETER · R0` | 73 |

</details>

---

<a name="27-hairspring"></a>

## 27. Hairspring

`hairspring` · marchand · Shopify products.json (country=US obligatoire)

**Ce qu'elle donne**

| Étape | Lignes | Part du brut |
|---|---|---|
| Brut collecté | 318 | 100 % |
| Filtre 0 — c'est une montre | 147 | 46 % |
| Filtre 1 — référence constructeur | 93 | 29 % |
| Socle — + date + transaction | 86 | 27 % |

**Natures de prix** — vendu 136 · demandé 11  
**Devises** — USD 147  
**Période** — 2023 → 2026 (4 années)  
**Montant médian** — 70 000  

**Ce qu'elle remplit**

| montant | devise | date | marque | référence | modèle | année | boîtier | diamètre | mouvement | cadran | estimation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 100 % | 100 % | 100 % | 100 % | 63 % | 0 % | 2 % | 0 % | 0 % | 0 % | 0 % | 0 % |

**D'où vient la donnée**

- Référence : `jeton_titre` 87 · `extrait_description` 6
- Nature du prix : `deduite_statut` 147
- Statut d'annonce : sold 136 · active 11

**Ce qu'il faut savoir**

Le champ marque vaut « Hairspring » sur 100 % des fiches ; la vraie marque se retrouve dans la description, pour la moitié seulement.

> **Réserve déclarée** — le champ vendor vaut 'Hairspring' sur 100 % des fiches ; la marque est retrouvee dans la description, mais pour la moitie seulement

*robots.txt : OK — verifie le 11/08/2026*

**Ce qui a été vérifié**

`6/6 montants · 3/6 references · 6/6 natures` — Sans `country=US` le prix chute de 17,8 %. Minuscule, mais la plus propre en nature : 0 sur 35 revenue en stock.

<details><summary>Pourquoi des lignes sont écartées</summary>

| Verdict et règle | Lignes |
|---|---|
| `REJETER · R3` | 152 |
| `QUARANTAINE · R7a` | 14 |
| `REJETER · R1` | 5 |

</details>

---

<a name="28-everywatch"></a>

## 28. EveryWatch

`everywatch` · agrégateur · endpoint Next.js /_next/data/{buildId}/watch-listing.json

**Ce qu'elle donne**

| Étape | Lignes | Part du brut |
|---|---|---|
| Brut collecté | 1 | 100 % |
| Filtre 0 — c'est une montre | 1 | 100 % |
| Filtre 1 — référence constructeur | 0 | 0 % |
| Socle — + date + transaction | 0 | 0 % |

**Natures de prix** — réalisé 1  
**Devises** — USD 1  
**Période** — 2026 → 2026 (1 années)  
**Montant médian** — 1 908  
**Régime de frais** — frais acheteur INCLUS  

**Ce qu'elle remplit**

| montant | devise | date | marque | référence | modèle | année | boîtier | diamètre | mouvement | cadran | estimation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 100 % | 100 % | 100 % | 100 % | 0 % | 100 % | 0 % | 0 % | 0 % | 0 % | 0 % | 0 % |

**D'où vient la donnée**

- Référence : aucune référence
- Nature du prix : `champ_dedie` 1
- Statut d'annonce : sold 1

**Ce qu'il faut savoir**

573 015 annonces annoncées, ~210 000 exploitables — mais la source BLOQUE après une dizaine de requêtes : 32 réponses sur 42 refusées le 28/08. Elle tolère quelques appels, pas une collecte.

> **Réserve déclarée** — fenetre glissante de 24 mois ; invendus non publies ; montants pre-convertis en USD par la source

*robots.txt : OK — 'User-agent: * / Allow: /', seul Amazonbot est banni*

**Ce qui a été vérifié**

`collecte impossible` — 32 reponses sur 42 refusees le 28/08.

---

## Les sources sondées puis écartées

Chacune a coûté des requêtes réelles. Le volume est ce qui serait *atteignable*, jamais ce qui a été collecté.

| Source | Type | Volume atteignable | Prix | Référence | Profondeur | Verdict |
|---|---|---|---|---|---|---|
| **Abell Auction** | maison de ventes | ~250 lots horlogers | realise, marteau nu | quasi nulle | 12/2024 | a creuser |
| **LiveAuctioneers** | agregateur | non mesurable | realise | non mesuree | — | a creuser |
| **New Orleans Auction** | maison de ventes | ~178 000 lots | realise, frais inclus (+25 %) | 65 % texte libre | 26/07/1992 | a creuser |
| **Watchfinder** | marchand | ~5 500 fiches | demande | URL et titre | aucune | a creuser |
| **EveryWatch (fenetre)** | agregateur | 573 015 annonces | realise, frais inclus | 63 % champ dedie | 24 mois glissants | branchee, avec reserve |
| **Bezel** | marketplace | 32 670 annonces | demande | champ dedie | releve | decision requise |
| **DavidSW** | marchand | 499 fiches servies par l'API | demande | ~87,5 % (titre) | 2022 | decision requise |
| **Grailzee** | marketplace d'encheres | 54 603 encheres | realise, marteau nu | 99,86 % champ structure | 19/08/2022 | decision requise |
| **Watches of Knightsbridge** | maison de ventes | ~12 000 lots | realise, MARTEAU NU | 31 a 40 % (titre tronque) | 12/07/2014 | decision requise |
| **Certified Watch Store** | marchand | 1 127 montres | neuf remise | 98 % (SKU prefixe) | aucune | ecartee |
| **Cortrie Auktionen** | maison de ventes | 24 lots vedettes | realise, FRAIS INCLUS ('inkl. Aufgeld') | ~100 % (titre) | non atteignable | ecartee |
| **Cottone Auctions** | maison de ventes | 3 323 lots | realise, frais inclus | 2 % | 2009 | ecartee |
| **John Moran Auctioneers** | maison de ventes | 1 catalogue passe accessible | realise, frais inclus (+27 %) | non mesurable | non atteignable | ecartee |
| **Kunsthaus Lempertz** | maison de ventes | 271 lots horlogers | realise, frais inclus | non mesuree | 2002 | ecartee |
| **Menta Watches** | marchand | 2 902 fiches | demande | 60 % (titre) | import 2023 | ecartee |
| **Morphy Auctions** | maison de ventes | ~12 ventes horlogeres | realise, frais a taux variable | 0 % | 2016 | ecartee |
| **The Watch Club** | marchand | 59 montres | demande (AUD) | ~0 % | aucune | ecartee |
| **Watches of Distinction (collecte gelee)** | marchand | 507 lignes deja collectees | demande | 93 % (titre) | aucune | gelee |

### Pourquoi

**Abell Auction** — Le JSON-LD laisse fuiter le prix realise malgre le 'Login for Price' affiche. Mais l'archive s'arrete a la migration de fin 2024 : vingt mois, et 1,2 % de lots horlogers.

**LiveAuctioneers** — LE BLOCAGE ETAIT LE NOTRE. En nous annoncant honnetement ClaudeBot le 02/09/2026, la source repond 318 Ko la ou notre faux UA Chrome recevait 962 octets de challenge — l'anti-bot visait le navigateur simule. Mais l'archive reste hors d'atteinte : ?status=archive rend 13 lots prixes sur 14, sans pagination, et le seul chemin qui pagine est `/search/?`, explicitement interdit par son robots.txt. Accessible n'est pas collectable.

**New Orleans Auction** — La plus profonde de toutes — trente-quatre ans. Resondee le 02/09/2026 : l'archive est bien la, en marque blanche d'Invaluable, et les prix REALISES sont servis dans le HTML — 16 lots prixes sur les 20 d'une page. Mais la pagination ne repond pas : ?page=2 rend toujours la page 0. Au-dela de 20 lots par catalogue il faut appeler Algolia avec la cle embarquee du site. Meme cas que Grailzee : decision requise.

**Watchfinder** — L'API de stock est explicitement en Disallow, donc une requete par fiche. Aucune date nulle part : c'est un instantane de stock.

**EveryWatch (fenetre)** — Resondee le 02/09/2026 : le BLOCAGE EST LEVE — 2 refus sur 42 contre 32 le 28/08. Mais la source est desormais videe : sur 50 lots servis en `auctionLotType: RESULT`, ZERO porte un prix ou une date. Une requete entiere n'a rendu qu'un seul lot exploitable, date de la veille. L'acces est ouvert, la donnee ne l'est plus.

**Bezel** — robots.txt autorise l'API mais les CGU interdisent verbatim le scraping. Adaptateur ecrit, bride par un drapeau, en attente d'arbitrage humain.

**DavidSW** — Resondee le 02/09/2026 : l'API WooCommerce repond et sert 499 fiches prixees, marque et modele en categories. MAIS son robots.txt porte `Disallow: /wp-json/` pour `User-agent: *`, et c'est sous cette regle que nous tombons puisque nous envoyons un UA Chrome. Verifie le 02/09/2026 apres etre passes a ClaudeBot : le groupe `claudebot` interdit LUI AUSSI `/wp-json/` — c'est la plomberie qui est fermee, pas le catalogue. Ses fiches produit nous sont ouvertes, mais elles sont 18 000 et le site bride dur : 6 refus 429 sur 8 pages a 2,5 s d'intervalle. Des jours de collecte pour un marchand de 499 pieces en stock.

**Grailzee** — Techniquement la meilleure source mesuree : reference normalisee a 99,9 %, invendus publies, ~110 requetes. Mais les prix ne sont accessibles que par un endpoint interne a cle embarquee.

**Watches of Knightsbridge** — Le meilleur rapport profondeur/cout du dossier — 57 requetes pour douze ans en marteau nu, invendus a 34 %. Mais son robots.txt porte 'User-agent: ClaudeBot / Disallow: /' : exclusion explicite.

**Certified Watch Store** — 1 076 fiches creees le meme jour par un import d'avril 2026 : aucun signal temporel. Entree de gamme, marche secondaire absent.

**Cortrie Auktionen** — Resondee le 29/08 puis le 02/09/2026, sans changement. La fiche est la plus riche qu'on ait vue — 'Referenz 6241, Seriennummer 17673..., Zuschlag: 272.360,00 € inkl. Aufgeld'. Mais l'archive n'est pas ouverte : le parametre de pagination est IGNORE (les memes 24 lots vedettes reviennent identiques a start=0, 24, 48, 72 et 4800) et les ventes passees repondent 404. Seule la vente en cours est visible.

**Cottone Auctions** — Maison d'horloges anciennes : sur ses 3 323 lots aspires, le filtre n'en garde que 40. Regulateurs, orreries, horloges de parquet — pas le marche de la montre-bracelet.

**John Moran Auctioneers** — Resondee le 29/08/2026 : le site est une marque blanche d'Invaluable, avec `realizedPriceIndicator:false` et un catalogue servi par Algolia, 20 lots par page au-dela desquels il faut une cle. Sa boutique WordPress ne vend que des sacs et des livres d'art. La profondeur de 1993 n'est pas atteignable par le site lui-meme.

**Kunsthaus Lempertz** — 86 805 URL enumerees par ses sitemaps pour 271 lots horlogers seulement, et aucun prix marteau disponible. Mauvais rapport.

**Menta Watches** — L'archive est fermee a l'API : 1 produit rendu sur 300 demandes. 8,8 % des fiches conservent un prix, et 73 % datent du meme import de lancement.

**Morphy Auctions** — Zero reference sur 132 titres examines, et des frais acheteur variables selon le canal d'enchere : le marteau n'est pas reconstructible. La page de resultats est en Disallow.

**The Watch Club** — Le champ marque vaut 'The Watch Club' sur toutes les fiches, et le catalogue contient plus de livres que de montres.

**Watches of Distinction (collecte gelee)** — Collectee le 02/09/2026 sous l'ancien en-tete, quand son robots.txt l'autorisait et qu'elle repondait. Depuis notre passage a ClaudeBot elle rend 403 sur toute requete : son robots.txt ne nous interdit rien, mais son pare-feu refuse les UA de robot. Un 403 est un refus, on ne le contourne pas. Les 496 montres deja en base restent, avec leur brut ; la source ne sera plus rappelee.

