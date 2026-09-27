# Où vivent la référence et la nature du prix

**Généré le 2026-09-02** par `python moteur/audit_champs.py` — ne pas éditer à la main, ce fichier est écrasé à chaque exécution.

Deux champs décident de la valeur d'une source. Aucun des deux ne porte le même nom deux fois de suite, et aucun n'est garanti. Ce rapport mesure ce qui est réellement disponible, source par source, dans le brut lui-même.

## En un coup d'œil

| Source | La référence | La nature du prix |
|---|---|---|
| acollectedman | champ publié `variants[].sku` (100 %) | statut publié `variants[].available` (100 %) |
| amsterdamvintage | champ publié `sku` (100 %) | statut publié `sold_individually` (100 %) |
| analogshift | champ publié `variants[].sku` (96 %) | statut publié `variants[].available` (100 %) |
| artcurial | devinée dans le titre — 39 % (extrait_description · extrait_titre) | statut publié `status` (100 %) |
| awco | devinée dans le titre — 74 % (champ_dedie · extrait_description · extrait_titre · jeton_titre) | statut publié `sold_individually` (100 %) |
| berrys | champ publié `variants[].sku` (98 %) | statut publié `variants[].available` (100 %) |
| bezel | non mesurable, pas de brut lisible | non mesurable |
| bulangandsons | champ publié `variants[].sku` (100 %) | statut publié `variants[].available` (100 %) |
| christies | devinée dans le titre — 63 % (extrait_description · extrait_titre) | statut publié `lot_withdrawn` (100 %) |
| chronofinder | champ publié `sku` (100 %) | statut publié `sold_individually` (100 %) |
| craft_and_tailored | champ publié `variants[].sku` (100 %) | statut publié `variants[].available` (100 %) |
| cwsellors | champ publié `variants[].sku` (100 %) | statut publié `variants[].available` (100 %) |
| everywatch | absente — 0 % | déclarée par l'adaptateur, jamais vérifiée |
| fortuna | devinée dans le titre — 52 % (extrait_description · extrait_titre · jeton_titre) | statut publié `acf.sold` (100 %) |
| globalwatchshop | champ publié `sku` (100 %) | statut publié `sold_individually` (100 %) |
| hairspring | devinée dans le titre — 66 % (extrait_description · jeton_titre) | statut publié `variants[].available` (100 %) |
| hodinkee | champ publié `variants[].sku` (100 %) | statut publié `variants[].available` (100 %) |
| keystone | champ publié `variants[].sku` (100 %) | statut publié `variants[].available` (100 %) |
| liveauctioneers | non mesurable, pas de brut lisible | non mesurable |
| loupethis | devinée dans le titre — 77 % (extrait_titre) | statut publié `attributes.sold_price_cents` (87 %) |
| lyonandturnbull | absente — 6 % | déclarée par l'adaptateur, jamais vérifiée |
| monacolegend | devinée dans le titre — 61 % (extrait_titre · jeton_titre) | statut publié `@graph[].offers.availability` (95 %) |
| montredo | champ publié `variants[].sku` (100 %) | statut publié `variants[].available` (100 %) |
| sworders | devinée dans le titre — 13 % (extrait_titre · jeton_titre) | déduite du statut de l'annonce |
| topper | champ publié `variants[].sku` (82 %) | statut publié `variants[].available` (100 %) |
| wannabuyawatch | champ publié `sku` (100 %) | statut publié `sold_individually` (100 %) |
| watchesofdistinction | champ publié `sku` (100 %) | statut publié `sold_individually` (100 %) |
| watchesofswitzerland | devinée dans le titre — 76 % (extrait_titre) | déduite du statut de l'annonce |
| watchrecon | devinée dans le titre — 73 % (extrait_titre · jeton_titre) | déclarée par l'adaptateur, jamais vérifiée |
| watchtrader | champ publié `sku` (100 %) | statut publié `sold_individually` (100 %) |

Lecture : un champ publié par la source est fiable ; une valeur devinée dans le titre porte un taux d'erreur ; une nature déclarée par l'adaptateur ne sait pas distinguer un lot vendu d'un lot invendu.

## 1. Ce que la base contient aujourd'hui

| Source | Prix | Natures | Référence | Période |
|---|---|---|---|---|
| acollectedman | 962 | asking 147 · sold 815 | 100 % | 2015-09-23 → 2026-08-27 |
| amsterdamvintage | 342 | asking 342 | 96 % | sans date |
| analogshift | 8213 | asking 942 · sold 7271 | 87 % | 2015-03-23 → 2026-08-24 |
| artcurial | 8625 | realised 8625 | 39 % | 2007-12-11 → 2026-07-13 |
| awco | 2686 | asking 2686 | 74 % | sans date |
| berrys | 5638 | asking 4774 · sold 864 | 99 % | 2014-06-12 → 2026-08-25 |
| bulangandsons | 3683 | asking 1540 · sold 2143 | 100 % | 2026-08-29 → 2026-08-29 |
| christies | 12507 | estimate 884 · realised 11623 | 63 % | 2017-05-04 → 2026-06-05 |
| chronofinder | 592 | asking 592 | 99 % | sans date |
| craft_and_tailored | 3646 | asking 102 · sold 3544 | 100 % | 2016-01-31 → 2026-08-24 |
| cwsellors | 2948 | asking 1502 · sold 1446 | 100 % | 2017-10-31 → 2026-08-25 |
| everywatch | 1 | realised 1 | 0 % | 2026-08-27 → 2026-08-27 |
| fortuna | 2010 | realised 2010 | 52 % | 2016-10-18 → 2026-07-19 |
| globalwatchshop | 971 | asking 971 | 99 % | sans date |
| hairspring | 318 | asking 37 · sold 281 | 66 % | 2023-02-21 → 2026-08-24 |
| hodinkee | 18945 | asking 8 · sold 18937 | 100 % | 2016-03-08 → 2024-10-17 |
| keystone | 5020 | asking 316 · sold 4704 | 100 % | 2018-08-27 → 2026-08-27 |
| loupethis | 4220 | realised 4220 | 77 % | 2021-07-08 → 2026-08-28 |
| lyonandturnbull | 5763 | estimate 190 · realised 5573 | 6 % | 2019-12-04 → 2026-05-20 |
| monacolegend | 4188 | estimate 450 · realised 3738 | 61 % | 2019-07-17 → 2026-07-25 |
| montredo | 18306 | asking 18043 · sold 263 | 100 % | 2026-08-29 → 2026-08-29 |
| sworders | 2506 | realised 2506 | 13 % | sans date |
| topper | 3687 | msrp 3687 | 98 % | 2018-02-11 → 2026-08-28 |
| wannabuyawatch | 6441 | asking 6441 | 74 % | sans date |
| watchesofdistinction | 507 | asking 507 | 94 % | sans date |
| watchesofswitzerland | 2475 | msrp 2475 | 76 % | sans date |
| watchrecon | 4950 | asking 4950 | 73 % | 2026-07-26 → 2026-08-27 |
| watchtrader | 4090 | asking 4090 | 100 % | sans date |

### La nature du prix : déclarée ou mesurée ?

Une nature déclarée une fois pour toutes dans l'adaptateur ne distingue ni un lot invendu d'un lot vendu, ni une montre en vitrine d'une montre partie.

| Source | Provenance de la nature | Statut de l'annonce | Sans montant |
|---|---|---|---|
| acollectedman | deduite_statut 962 | active 147 · sold 815 | 0 |
| amsterdamvintage | deduite_statut 342 | active 73 · sold 269 | 0 |
| analogshift | deduite_statut 8213 | active 942 · sold 7271 | 0 |
| artcurial | champ_dedie 8625 | sold 8625 | 0 |
| awco | deduite_statut 2686 | active 433 · sold 2253 | 0 |
| berrys | deduite_statut 5638 | active 4774 · sold 864 | 0 |
| bulangandsons | declaree_tag 2642 · deduite_statut 1041 | active 1540 · sold 2143 | 0 |
| christies | deduite_statut 12507 | sold 11623 · unsold 884 | 0 |
| chronofinder | deduite_statut 592 | active 129 · sold 463 | 0 |
| craft_and_tailored | deduite_statut 3646 | active 102 · sold 3544 | 0 |
| cwsellors | deduite_statut 2948 | active 1502 · sold 1446 | 0 |
| everywatch | champ_dedie 1 | sold 1 | 0 |
| fortuna | champ_dedie 2010 | sold 2010 | 0 |
| globalwatchshop | deduite_statut 971 | active 249 · sold 722 | 0 |
| hairspring | deduite_statut 318 | active 37 · sold 281 | 0 |
| hodinkee | deduite_statut 18945 | active 8 · sold 18937 | 0 |
| keystone | deduite_statut 5020 | active 316 · sold 4704 | 0 |
| loupethis | champ_dedie 4220 | sold 4220 | 0 |
| lyonandturnbull | champ_dedie 5763 | sold 5573 · unsold 190 | 0 |
| monacolegend | champ_dedie 4188 | sold 3738 · unsold 450 | 0 |
| montredo | declaree_tag 3402 · deduite_statut 14904 | active 14641 · inactive 3402 · sold 263 | 0 |
| sworders | deduite_statut 2506 | sold 2506 | 0 |
| topper | deduite_statut 3687 | active 2558 · inactive 1129 | 0 |
| wannabuyawatch | deduite_statut 6441 | active 449 · sold 5992 | 0 |
| watchesofdistinction | deduite_statut 507 | active 417 · sold 90 | 0 |
| watchesofswitzerland | deduite_statut 2475 | active 824 · inactive 1651 | 0 |
| watchrecon | constante_source 4950 | unknown 4950 | 0 |
| watchtrader | deduite_statut 4090 | active 601 · sold 3489 | 0 |

### La référence : publiée, devinée, ou absente ?

| Source | Référence remplie | Provenance |
|---|---|---|
| acollectedman | 100 % | extrait_description 41 · extrait_titre 44 · jeton_titre 342 · sku 535 |
| amsterdamvintage | 96 % | champ_dedie 312 · extrait_description 1 · jeton_titre 15 |
| analogshift | 87 % | extrait_description 3841 · extrait_titre 35 · jeton_titre 312 · sku 2977 |
| artcurial | 39 % | extrait_description 517 · extrait_titre 2804 |
| awco | 74 % | champ_dedie 1220 · extrait_description 2 · extrait_titre 688 · jeton_titre 65 |
| berrys | 99 % | champ_dedie 5544 · jeton_titre 23 · sku 20 |
| bulangandsons | 100 % | extrait_description 121 · extrait_titre 1203 · jeton_titre 1271 · sku 1081 |
| christies | 63 % | extrait_description 58 · extrait_titre 7761 |
| chronofinder | 99 % | champ_dedie 400 · extrait_description 67 · jeton_titre 120 |
| craft_and_tailored | 100 % | extrait_description 30 · extrait_titre 3041 · jeton_titre 184 · sku 383 |
| cwsellors | 100 % | extrait_description 153 · extrait_titre 3 · jeton_titre 256 · sku 2536 |
| everywatch | 0 % | aucune |
| fortuna | 52 % | extrait_description 404 · extrait_titre 617 · jeton_titre 20 |
| globalwatchshop | 99 % | champ_dedie 943 · jeton_titre 15 |
| hairspring | 66 % | extrait_description 14 · jeton_titre 195 |
| hodinkee | 100 % | extrait_description 211 · extrait_titre 1837 · jeton_titre 15805 · sku 1049 |
| keystone | 100 % | extrait_description 407 · extrait_titre 3872 · jeton_titre 61 · sku 680 |
| loupethis | 77 % | extrait_titre 3262 |
| lyonandturnbull | 6 % | extrait_titre 365 |
| monacolegend | 61 % | extrait_titre 2459 · jeton_titre 96 |
| montredo | 100 % | extrait_description 15278 · extrait_titre 27 · jeton_titre 2138 · sku 863 |
| sworders | 13 % | extrait_titre 3 · jeton_titre 312 |
| topper | 98 % | extrait_titre 3 · jeton_titre 2458 · sku 1149 |
| wannabuyawatch | 74 % | champ_dedie 4289 · extrait_description 11 · extrait_titre 303 · jeton_titre 170 |
| watchesofdistinction | 94 % | extrait_titre 470 · jeton_titre 6 |
| watchesofswitzerland | 76 % | extrait_titre 1887 |
| watchrecon | 73 % | extrait_titre 746 · jeton_titre 2846 |
| watchtrader | 100 % | champ_dedie 4085 · extrait_description 2 |

### Ce que le filtre ferait de cette base

| Source | Garder | Rejeter | Quarantaine | % gardé |
|---|---|---|---|---|
| acollectedman | 622 | 331 | 9 | 65 % |
| amsterdamvintage | 293 | 39 | 10 | 86 % |
| analogshift | 6408 | 1669 | 136 | 78 % |
| artcurial | 4788 | 3837 | 0 | 56 % |
| awco | 2116 | 475 | 95 | 79 % |
| berrys | 2141 | 3496 | 1 | 38 % |
| bulangandsons | 2267 | 938 | 478 | 62 % |
| christies | 10164 | 2343 | 0 | 81 % |
| chronofinder | 494 | 20 | 78 | 83 % |
| craft_and_tailored | 2790 | 353 | 503 | 77 % |
| cwsellors | 2427 | 516 | 5 | 82 % |
| everywatch | 1 | 0 | 0 | 100 % |
| fortuna | 1455 | 555 | 0 | 72 % |
| globalwatchshop | 791 | 54 | 126 | 81 % |
| hairspring | 140 | 166 | 12 | 44 % |
| hodinkee | 17662 | 1026 | 257 | 93 % |
| keystone | 4856 | 136 | 28 | 97 % |
| loupethis | 3358 | 862 | 0 | 80 % |
| lyonandturnbull | 1048 | 4715 | 0 | 18 % |
| monacolegend | 3971 | 217 | 0 | 95 % |
| montredo | 15142 | 2911 | 253 | 83 % |
| sworders | 1504 | 1002 | 0 | 60 % |
| topper | 2309 | 1338 | 40 | 63 % |
| wannabuyawatch | 4736 | 1195 | 510 | 74 % |
| watchesofdistinction | 485 | 12 | 10 | 96 % |
| watchesofswitzerland | 2212 | 237 | 26 | 89 % |
| watchrecon | 4113 | 463 | 374 | 83 % |
| watchtrader | 3930 | 151 | 9 | 96 % |

## 2. Ce que le brut expose, champ par champ

Enumération de tous les chemins de clés réellement présents dans la dernière réponse de chaque source, avec leur taux de remplissage mesuré.

### acollectedman

- brut lu : `2026-08-28T15-52-02.json.gz` (8 requêtes)
- 1795 objets analysés

**Famille `id, title`** — 1795 objets, 36 chemins de clés

*Candidats RÉFÉRENCE*

| Champ | Rempli | Exemples |
|---|---|---|
| `variants[].sku` | 100 % | CSCPT_F4197 · CBCPT_P4206 |

*Candidats NATURE ou STATUT*

| Champ | Rempli | Exemples |
|---|---|---|
| `variants[].available` | 100 % | True · True |

### amsterdamvintage

- brut lu : `2026-08-29T20-00-56.json.gz` (50 requêtes)
- 4893 objets analysés

**Famille `id, name, price_html`** — 4893 objets, 58 chemins de clés

*Candidats RÉFÉRENCE*

| Champ | Rempli | Exemples |
|---|---|---|
| `sku` | 100 % | 8329 · 8415 |

*Candidats NATURE ou STATUT*

| Champ | Rempli | Exemples |
|---|---|---|
| `is_in_stock` | 100 % | True · True |
| `sold_individually` | 100 % | True · False |

### analogshift

- brut lu : `2026-08-25T13-29-05.json.gz` (36 requêtes)
- 8770 objets analysés

**Famille `id, title`** — 8770 objets, 36 chemins de clés

*Candidats RÉFÉRENCE*

| Champ | Rempli | Exemples |
|---|---|---|
| `variants[].sku` | 96 % | 40931072 · 40993118 |

*Candidats NATURE ou STATUT*

| Champ | Rempli | Exemples |
|---|---|---|
| `variants[].available` | 100 % | True · True |

### artcurial

- brut lu : `2026-08-25T10-55-07.json.gz` (90 requêtes)
- 9411 objets analysés

**Famille `adjudicationPrice, finalPrice, publishLot`** — 5855 objets, 53 chemins de clés

*Candidats RÉFÉRENCE* — aucun champ candidat.

*Candidats NATURE ou STATUT*

| Champ | Rempli | Exemples |
|---|---|---|
| `status` | 100 % | SOLD · SOLD |
| `reserve` | 100 % | 4000.0 · 1000.0 |
| `reserveType` | 100 % | FIRM · NET |
| `pictures[].document.status` | 100 % | ACCEPTED · ACCEPTED |

**Famille `adjudicationPrice, artistName, finalPrice`** — 1092 objets, 35 chemins de clés

*Candidats RÉFÉRENCE* — aucun champ candidat.

*Candidats NATURE ou STATUT*

| Champ | Rempli | Exemples |
|---|---|---|
| `status` | 100 % | SOLD · SOLD |
| `reserve` | 100 % | 2000.0 · 2500.0 |
| `reserveType` | 100 % | FIRM · FIRM |
| `pictures[].document.status` | 100 % | ACCEPTED · ACCEPTED |

**Famille `adjudicationPrice, finalPrice, publishLot`** — 1039 objets, 41 chemins de clés

*Candidats RÉFÉRENCE*

| Champ | Rempli | Exemples |
|---|---|---|
| `descriptions.ENGLISH.reference` | 0 % | — |

*Candidats NATURE ou STATUT*

| Champ | Rempli | Exemples |
|---|---|---|
| `status` | 100 % | SOLD · SOLD |
| `reserve` | 100 % | 1000.0 · 1000.0 |
| `reserveType` | 100 % | FIRM · FIRM |
| `pictures[].document.status` | 100 % | ACCEPTED · ACCEPTED |
| `descriptions.ENGLISH.state` | 0 % | — |

### awco

- brut lu : `2026-08-28T15-52-02.json.gz` (201 requêtes)
- 20215 objets analysés

**Famille `id, name, price_html`** — 19897 objets, 79 chemins de clés

*Candidats RÉFÉRENCE*

| Champ | Rempli | Exemples |
|---|---|---|
| `sku` | 0 % | 7900 |

*Candidats NATURE ou STATUT*

| Champ | Rempli | Exemples |
|---|---|---|
| `is_in_stock` | 100 % | True · True |
| `sold_individually` | 100 % | False · False |

**Famille `id, name`** — 316 objets, 3 chemins de clés

*Candidats RÉFÉRENCE* — aucun champ candidat.

*Candidats NATURE ou STATUT* — aucun champ candidat.

### berrys

- brut lu : `2026-08-25T13-29-05.json.gz` (23 requêtes)
- 5639 objets analysés

**Famille `id, title`** — 5639 objets, 36 chemins de clés

*Candidats RÉFÉRENCE*

| Champ | Rempli | Exemples |
|---|---|---|
| `variants[].sku` | 98 % | 58704BX_PB_G_BBB_00M · 56002BX_BB_R_XBX_00M |

*Candidats NATURE ou STATUT*

| Champ | Rempli | Exemples |
|---|---|---|
| `variants[].available` | 100 % | True · True |

### bezel

- brut lu : `2026-08-11T08-38-05.json` (1 requêtes)
- 0 objets analysés
- aucun bloc repete identifiable dans le DOM
- ni JSON-LD ni __NEXT_DATA__ — lecture du DOM

Aucune famille d'objets exploitable dans ce brut.

### bulangandsons

- brut lu : `2026-08-28T15-52-02.json.gz` (17 requêtes)
- 4169 objets analysés

**Famille `id, title`** — 4169 objets, 36 chemins de clés

*Candidats RÉFÉRENCE*

| Champ | Rempli | Exemples |
|---|---|---|
| `variants[].sku` | 100 % | W-3776 · W-3905 |

*Candidats NATURE ou STATUT*

| Champ | Rempli | Exemples |
|---|---|---|
| `variants[].available` | 100 % | True · True |

### christies

- brut lu : `2026-08-25T12-04-02.json.gz` (130 requêtes)
- 6079 objets analysés

**Famille `analytics_id, current_bid, lot_estimate_txt`** — 3006 objets, 33 chemins de clés

*Candidats RÉFÉRENCE* — aucun champ candidat.

*Candidats NATURE ou STATUT*

| Champ | Rempli | Exemples |
|---|---|---|
| `estimate_visible` | 100 % | True · True |
| `estimate_on_request` | 100 % | False · False |
| `estimate_low` | 100 % | 3000.0 · 3000.0 |
| `estimate_high` | 100 % | 6000.0 · 5000.0 |
| `estimate_txt` | 100 % | USD 3,000 - 6,000 · USD 3,000 - 5,000 |
| `lot_withdrawn` | 100 % | False · False |
| `price_realised` | 100 % | 4375.0 · 3750.0 |
| `price_realised_txt` | 100 % | USD 4,375 · USD 3,750 |

**Famille `analytics_id, event_id, subtitle_txt`** — 1855 objets, 29 chemins de clés

*Candidats RÉFÉRENCE* — aucun champ candidat.

*Candidats NATURE ou STATUT*

| Champ | Rempli | Exemples |
|---|---|---|
| `is_active` | 100 % | True · True |
| `status_txt` | 0 % | — |

**Famille `analytics_id, id`** — 1218 objets, 6 chemins de clés

*Candidats RÉFÉRENCE* — aucun champ candidat.

*Candidats NATURE ou STATUT* — aucun champ candidat.

### chronofinder

- brut lu : `2026-08-28T15-52-02.json.gz` (11 requêtes)
- 1057 objets analysés

**Famille `id, name, price_html`** — 1057 objets, 79 chemins de clés

*Candidats RÉFÉRENCE*

| Champ | Rempli | Exemples |
|---|---|---|
| `sku` | 100 % | CFW3786-1-1 · CFW3816 |

*Candidats NATURE ou STATUT*

| Champ | Rempli | Exemples |
|---|---|---|
| `is_in_stock` | 100 % | True · True |
| `sold_individually` | 100 % | True · True |

### craft_and_tailored

- brut lu : `2026-08-25T10-06-47.json` (15 requêtes)
- 3649 objets analysés

**Famille `id, title`** — 3649 objets, 36 chemins de clés

*Candidats RÉFÉRENCE*

| Champ | Rempli | Exemples |
|---|---|---|
| `variants[].sku` | 100 % | LMMOD3312RNNS · RLXDJ16018-3 |

*Candidats NATURE ou STATUT*

| Champ | Rempli | Exemples |
|---|---|---|
| `variants[].available` | 100 % | True · True |

### cwsellors

- brut lu : `2026-08-27T20-23-43.json.gz` (19 requêtes)
- 4187 objets analysés

**Famille `id, title`** — 4187 objets, 36 chemins de clés

*Candidats RÉFÉRENCE*

| Champ | Rempli | Exemples |
|---|---|---|
| `variants[].sku` | 100 % | DOX-333 · DOX-332 |

*Candidats NATURE ou STATUT*

| Champ | Rempli | Exemples |
|---|---|---|
| `variants[].available` | 100 % | True · True |

### everywatch

- brut lu : `2026-08-28T19-54-44.json.gz` (42 requêtes)
- 4692 objets analysés
- aucun bloc repete identifiable dans le DOM
- ni JSON-LD ni __NEXT_DATA__ — lecture du DOM

**Famille `auctionLotType, defaultManufacturerId, defaultManufacturerName`** — 4500 objets, 278 chemins de clés

*Candidats RÉFÉRENCE*

| Champ | Rempli | Exemples |
|---|---|---|
| `referenceNumberId` | 92 % | 592 · 339 |
| `referenceNumber` | 92 % | 1803 · 126334 |
| `referenceParentId` | 0 % | — |
| `referenceNumberSlug` | 0 % | — |
| `referenceNumberURL` | 0 % | — |
| `referenceNumberIsPending` | 0 % | — |
| `referenceEnrichmentName` | 0 % | — |
| `referenceEnrichmentNameFull` | 0 % | — |

*Candidats NATURE ou STATUT*

| Champ | Rempli | Exemples |
|---|---|---|
| `conditionName` | 100 % | Pre Owned · Pre Owned |
| `lotStatusId` | 100 % | 2 · 2 |
| `isActiveManufacturer` | 0 % | — |
| `isActiveModel` | 0 % | — |
| `isActiveReferenceNumber` | 0 % | — |
| `isActiveCaseMaterial` | 0 % | — |
| `isActiveBezelMaterial` | 0 % | — |
| `isActiveFunction` | 0 % | — |

**Famille `2 cles`** — 192 objets, 5 chemins de clés

*Candidats RÉFÉRENCE* — aucun champ candidat.

*Candidats NATURE ou STATUT* — aucun champ candidat.

### fortuna

- brut lu : `2026-08-28T16-54-35.json.gz` (21 requêtes)
- 2020 objets analysés

**Famille `guid, id, lot-category`** — 2020 objets, 59 chemins de clés

*Candidats RÉFÉRENCE* — aucun champ candidat.

*Candidats NATURE ou STATUT*

| Champ | Rempli | Exemples |
|---|---|---|
| `status` | 100 % | publish · publish |
| `acf.lot_status` | 100 % | sold · sold |
| `acf.auction_estimate_low` | 100 % | 4000 · 3000 |
| `acf.auction_estimate_high` | 100 % | 6000 · 4000 |
| `acf.sold` | 100 % | True · True |
| `acf.hammer_price` | 100 % | 2800 · 2000 |
| `acf.wavebid_id` | 0 % | — |
| `acf.retail_estimate` | 0 % | — |

### globalwatchshop

- brut lu : `2026-08-28T15-52-02.json.gz` (52 requêtes)
- 5136 objets analysés

**Famille `id, name, price_html`** — 5136 objets, 77 chemins de clés

*Candidats RÉFÉRENCE*

| Champ | Rempli | Exemples |
|---|---|---|
| `sku` | 100 % | 126710BLNRpre · 126333-Pre |

*Candidats NATURE ou STATUT*

| Champ | Rempli | Exemples |
|---|---|---|
| `is_in_stock` | 100 % | False · False |
| `sold_individually` | 100 % | True · True |

### hairspring

- brut lu : `2026-08-25T10-47-11.json.gz` (2 requêtes)
- 318 objets analysés

**Famille `id, title`** — 318 objets, 45 chemins de clés

*Candidats RÉFÉRENCE*

| Champ | Rempli | Exemples |
|---|---|---|
| `variants[].sku` | 0 % | — |

*Candidats NATURE ou STATUT*

| Champ | Rempli | Exemples |
|---|---|---|
| `variants[].available` | 100 % | True · False |

### hodinkee

- brut lu : `2026-08-28T15-30-40.json.gz` (76 requêtes)
- 18946 objets analysés

**Famille `id, title`** — 18946 objets, 36 chemins de clés

*Candidats RÉFÉRENCE*

| Champ | Rempli | Exemples |
|---|---|---|
| `variants[].sku` | 100 % | 03.3401.3610.21.C911 · UWK U1-HGMT |

*Candidats NATURE ou STATUT*

| Champ | Rempli | Exemples |
|---|---|---|
| `variants[].available` | 100 % | True · False |

### keystone

- brut lu : `2026-08-28T15-30-40.json.gz` (21 requêtes)
- 5081 objets analysés

**Famille `id, title`** — 5081 objets, 36 chemins de clés

*Candidats RÉFÉRENCE*

| Champ | Rempli | Exemples |
|---|---|---|
| `variants[].sku` | 100 % | 214628 · 214654 |

*Candidats NATURE ou STATUT*

| Champ | Rempli | Exemples |
|---|---|---|
| `variants[].available` | 100 % | True · True |

### liveauctioneers

- brut lu : `2026-08-11T00-21-41.json` (1 requêtes)
- 0 objets analysés
- aucun bloc repete identifiable dans le DOM
- ni JSON-LD ni __NEXT_DATA__ — lecture du DOM

Aucune famille d'objets exploitable dans ce brut.

### loupethis

- brut lu : `2026-08-28T15-52-02.json.gz` (172 requêtes)
- 4402 objets analysés

**Famille `id`** — 4068 objets, 28 chemins de clés

*Candidats RÉFÉRENCE* — aucun champ candidat.

*Candidats NATURE ou STATUT*

| Champ | Rempli | Exemples |
|---|---|---|
| `attributes.bids_count` | 100 % | 0 · 0 |
| `attributes.current_bid_price_cents` | 100 % | 0 · 0 |
| `attributes.next_bid_minimum_price_cents` | 100 % | 5000 · 5000 |
| `attributes.winning_bid_user_id` | 94 % | cf46864d-d3e8-432c-bf60-48270c4d6754 · 65bc2fcf-2e90-4ef5-9840-611d58b19029 |
| `attributes.sold_price_cents` | 87 % | 1649890 · 2799940 |

**Famille `id`** — 333 objets, 2 chemins de clés

*Candidats RÉFÉRENCE* — aucun champ candidat.

*Candidats NATURE ou STATUT* — aucun champ candidat.

### lyonandturnbull

- brut lu : `2026-08-25T13-31-58.json.gz` (51 requêtes)
- 102 objets analysés
- JSON-LD present : 2 blocs

**Famille `@id, name`** — 51 objets, 28 chemins de clés

*Candidats RÉFÉRENCE* — aucun champ candidat.

*Candidats NATURE ou STATUT* — aucun champ candidat.

**Famille `name`** — 50 objets, 32 chemins de clés

*Candidats RÉFÉRENCE* — aucun champ candidat.

*Candidats NATURE ou STATUT* — aucun champ candidat.

### monacolegend

- brut lu : `2026-08-28T23-11-21.json.gz` (20 requêtes)
- 79 objets analysés
- JSON-LD present : 3 blocs
- JSON-LD present : 4 blocs

**Famille `2 cles`** — 20 objets, 80 chemins de clés

*Candidats RÉFÉRENCE* — aucun champ candidat.

*Candidats NATURE ou STATUT*

| Champ | Rempli | Exemples |
|---|---|---|
| `@graph[].eventStatus` | 95 % | https://schema.org/EventPast · https://schema.org/EventPast |
| `@graph[].offers.offerCount` | 95 % | 48 · 166 |
| `@graph[].offers.availability` | 95 % | https://schema.org/Discontinued · https://schema.org/Discontinued |
| `@graph[].subEvent[].eventStatus` | 5 % | https://schema.org/EventPast |

**Famille `2 cles`** — 20 objets, 5 chemins de clés

*Candidats RÉFÉRENCE* — aucun champ candidat.

*Candidats NATURE ou STATUT* — aucun champ candidat.

**Famille `name`** — 19 objets, 10 chemins de clés

*Candidats RÉFÉRENCE* — aucun champ candidat.

*Candidats NATURE ou STATUT* — aucun champ candidat.

### montredo

- brut lu : `2026-08-25T12-31-48.json.gz` (74 requêtes)
- 18306 objets analysés

**Famille `id, title`** — 18306 objets, 36 chemins de clés

*Candidats RÉFÉRENCE*

| Champ | Rempli | Exemples |
|---|---|---|
| `variants[].sku` | 100 % | 58375 · 55923 |

*Candidats NATURE ou STATUT*

| Champ | Rempli | Exemples |
|---|---|---|
| `variants[].available` | 100 % | True · True |

### sworders

- brut lu : `2026-08-29T20-06-52.json.gz` (48 requêtes)
- 96 objets analysés
- bloc repete : .row (4 occurrences)
- ni JSON-LD ni __NEXT_DATA__ — lecture du DOM

**Famille `8 cles`** — 48 objets, 8 chemins de clés

*Candidats RÉFÉRENCE* — aucun champ candidat.

*Candidats NATURE ou STATUT* — aucun champ candidat.

**Famille `auction-grid-lot, auction-lot, auction-lot-text`** — 11 objets, 29 chemins de clés

*Candidats RÉFÉRENCE* — aucun champ candidat.

*Candidats NATURE ou STATUT*

| Champ | Rempli | Exemples |
|---|---|---|
| `active` | 100 % | Past lots (324) · Past lots (324) |
| `auction-tab-sold` | 100 % | Past lots (324) · Past lots (324) |

**Famille `auction-grid-lot, auction-lot, auction-lot-text`** — 8 objets, 28 chemins de clés

*Candidats RÉFÉRENCE* — aucun champ candidat.

*Candidats NATURE ou STATUT*

| Champ | Rempli | Exemples |
|---|---|---|
| `active` | 100 % | Past lots (324) · Past lots (830) |
| `auction-tab-sold` | 100 % | Past lots (324) · Past lots (830) |

### topper

- brut lu : `2026-08-28T15-30-40.json.gz` (15 requêtes)
- 3693 objets analysés

**Famille `id, title`** — 3693 objets, 36 chemins de clés

*Candidats RÉFÉRENCE*

| Champ | Rempli | Exemples |
|---|---|---|
| `variants[].sku` | 82 % | 136 · 1124 |

*Candidats NATURE ou STATUT*

| Champ | Rempli | Exemples |
|---|---|---|
| `variants[].available` | 100 % | True · True |

### wannabuyawatch

- brut lu : `2026-08-28T15-52-02.json.gz` (126 requêtes)
- 15881 objets analysés

**Famille `id, name, price_html`** — 9496 objets, 77 chemins de clés

*Candidats RÉFÉRENCE*

| Champ | Rempli | Exemples |
|---|---|---|
| `sku` | 100 % | 72215 · 71643 |

*Candidats NATURE ou STATUT*

| Champ | Rempli | Exemples |
|---|---|---|
| `is_in_stock` | 100 % | True · True |
| `sold_individually` | 100 % | True · True |

**Famille `id, name`** — 6365 objets, 3 chemins de clés

*Candidats RÉFÉRENCE* — aucun champ candidat.

*Candidats NATURE ou STATUT* — aucun champ candidat.

**Famille `id, name`** — 20 objets, 7 chemins de clés

*Candidats RÉFÉRENCE* — aucun champ candidat.

*Candidats NATURE ou STATUT* — aucun champ candidat.

### watchesofdistinction

- brut lu : `2026-09-02T15-03-49.json.gz` (58 requêtes)
- 5747 objets analysés

**Famille `id, name, price_html`** — 5747 objets, 71 chemins de clés

*Candidats RÉFÉRENCE*

| Champ | Rempli | Exemples |
|---|---|---|
| `sku` | 100 % | L198 · 1-1 |

*Candidats NATURE ou STATUT*

| Champ | Rempli | Exemples |
|---|---|---|
| `is_in_stock` | 100 % | True · True |
| `sold_individually` | 100 % | True · False |

### watchesofswitzerland

- brut lu : `2026-08-27T20-28-23.json.gz` (2501 requêtes)
- 12929 objets analysés
- aucun bloc repete identifiable dans le DOM
- ni JSON-LD ni __NEXT_DATA__ — lecture du DOM

**Famille `1 cles`** — 11758 objets, 1 chemins de clés

*Candidats RÉFÉRENCE* — aucun champ candidat.

*Candidats NATURE ou STATUT* — aucun champ candidat.

**Famille `name`** — 1169 objets, 3 chemins de clés

*Candidats RÉFÉRENCE* — aucun champ candidat.

*Candidats NATURE ou STATUT* — aucun champ candidat.

### watchrecon

- brut lu : `2026-08-27T20-23-43.json.gz` (632 requêtes)
- 2528 objets analysés
- bloc repete : .btn-group (4 occurrences)
- ni JSON-LD ni __NEXT_DATA__ — lecture du DOM

**Famille `name`** — 632 objets, 4 chemins de clés

*Candidats RÉFÉRENCE* — aucun champ candidat.

*Candidats NATURE ou STATUT*

| Champ | Rempli | Exemples |
|---|---|---|
| `active` | 100 % | Rolex · Rolex |

**Famille `name`** — 632 objets, 6 chemins de clés

*Candidats RÉFÉRENCE* — aucun champ candidat.

*Candidats NATURE ou STATUT*

| Champ | Rempli | Exemples |
|---|---|---|
| `active` | 100 % | 14 days · 14 days |

**Famille `name`** — 632 objets, 5 chemins de clés

*Candidats RÉFÉRENCE* — aucun champ candidat.

*Candidats NATURE ou STATUT*

| Champ | Rempli | Exemples |
|---|---|---|
| `active` | 100 % | 14 days · 14 days |

### watchtrader

- brut lu : `2026-08-28T15-30-40.json.gz` (42 requêtes)
- 4107 objets analysés

**Famille `id, name, price_html`** — 4091 objets, 58 chemins de clés

*Candidats RÉFÉRENCE*

| Champ | Rempli | Exemples |
|---|---|---|
| `sku` | 100 % | W12960 · W12761 |

*Candidats NATURE ou STATUT*

| Champ | Rempli | Exemples |
|---|---|---|
| `is_in_stock` | 100 % | True · True |
| `sold_individually` | 100 % | True · True |

**Famille `id, name`** — 16 objets, 7 chemins de clés

*Candidats RÉFÉRENCE* — aucun champ candidat.

*Candidats NATURE ou STATUT* — aucun champ candidat.

## 3. La structure complète, source par source

Tout ce que la source publie, pas seulement ce qu'on en tire aujourd'hui. C'est là qu'on voit ce qu'on laisse sur la table.

<details><summary><b>acollectedman</b> — famille <code>id, title</code>, 36 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `body_html` | 100 % | <p>This is one of the last examples of the Chronomètre à Rés… |
| `created_at` | 100 % | 2026-08-27T10:50:34+01:00 |
| `handle` | 100 % | f-p-journe-chronometre-a-resonance-brass |
| `id` | 100 % | 15739598471545 |
| `images[].created_at` | 100 % | 2026-08-27T10:54:24+01:00 |
| `images[].height` | 100 % | 3231 |
| `images[].id` | 100 % | 83180116574585 |
| `images[].position` | 100 % | 3 |
| `images[].product_id` | 100 % | 15739598471545 |
| `images[].src` | 100 % | https://cdn.shopify.com/s/files/1/0606/5325/files/F._P._Jour… |
| `images[].updated_at` | 100 % | 2026-08-27T10:54:30+01:00 |
| `images[].width` | 100 % | 2155 |
| `options[].name` | 100 % | Title |
| `options[].position` | 100 % | 1 |
| `product_type` | 100 % | Watch |
| `published_at` | 100 % | 2026-08-27T12:12:09+01:00 |
| `title` | 100 % | Chronomètre à Résonance - Brass | Ref. R | Platinum |
| `updated_at` | 100 % | 2026-08-28T15:26:34+01:00 |
| `variants[].available` | 100 % | True |
| `variants[].created_at` | 100 % | 2026-08-27T10:50:34+01:00 |
| `variants[].grams` | 100 % | 0 |
| `variants[].id` | 100 % | 64383009128825 |
| `variants[].option1` | 100 % | Default Title |
| `variants[].position` | 100 % | 1 |
| `variants[].price` | 100 % | 630000.00 |
| `variants[].product_id` | 100 % | 15739598471545 |
| `variants[].requires_shipping` | 100 % | True |
| `variants[].sku` | 100 % | CSCPT_F4197 |
| `variants[].taxable` | 100 % | True |
| `variants[].title` | 100 % | Default Title |
| `variants[].updated_at` | 100 % | 2026-08-28T15:26:34+01:00 |
| `vendor` | 100 % | F. P. Journe |
| `variants[].compare_at_price` | 0 % | — |
| `variants[].featured_image` | 0 % | — |
| `variants[].option2` | 0 % | Regular |
| `variants[].option3` | 0 % | — |

</details>

<details><summary><b>amsterdamvintage</b> — famille <code>id, name, price_html</code>, 58 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `add_to_cart.description` | 100 % | Add to cart: &ldquo;Cartier Tank 17002 &#8216;Jumbo&#8217;&r… |
| `add_to_cart.maximum` | 100 % | 1 |
| `add_to_cart.minimum` | 100 % | 1 |
| `add_to_cart.multiple_of` | 100 % | 1 |
| `add_to_cart.single_text` | 100 % | Add to cart |
| `add_to_cart.text` | 100 % | Add to cart |
| `add_to_cart.url` | 100 % | /wp-json/wc/store/v1/products?per_page=100&#038;page=1&#038;… |
| `attributes[].has_variations` | 100 % | False |
| `attributes[].id` | 100 % | 15 |
| `attributes[].name` | 100 % | Serial No. |
| `attributes[].taxonomy` | 100 % | pa_serial-no |
| `attributes[].terms[].id` | 100 % | 9970 |
| `attributes[].terms[].name` | 100 % | 170020064 |
| `attributes[].terms[].slug` | 100 % | 170020064 |
| `average_rating` | 100 % | 0 |
| `categories[].id` | 100 % | 10 |
| `categories[].link` | 100 % | https://amsterdamvintagewatches.com/product-category/wrist-w… |
| `categories[].name` | 100 % | Wrist Watches |
| `categories[].slug` | 100 % | wrist-watches |
| `has_options` | 100 % | False |
| `id` | 100 % | 1666250 |
| `is_in_stock` | 100 % | True |
| `is_on_backorder` | 100 % | False |
| `is_purchasable` | 100 % | True |
| `name` | 100 % | Cartier Tank 17002 &#8216;Jumbo&#8217; |
| `on_sale` | 100 % | False |
| `parent` | 100 % | 0 |
| `permalink` | 100 % | https://amsterdamvintagewatches.com/shop/cartier-tank-17002-… |
| `prices.currency_code` | 100 % | EUR |
| `prices.currency_decimal_separator` | 100 % | , |
| `prices.currency_minor_unit` | 100 % | 0 |
| `prices.currency_prefix` | 100 % | €  |
| `prices.currency_symbol` | 100 % | € |
| `prices.currency_thousand_separator` | 100 % | . |
| `prices.price` | 100 % | 38000 |
| `prices.regular_price` | 100 % | 38000 |
| `prices.sale_price` | 100 % | 38000 |
| `review_count` | 100 % | 0 |
| `sku` | 100 % | 8329 |
| `slug` | 100 % | cartier-tank-17002-jumbo-4 |
| `sold_individually` | 100 % | True |
| `stock_availability.class` | 100 % | in-stock |
| `type` | 100 % | simple |
| `stock_availability.text` | 94 % | In stock |
| `images[].id` | 80 % | 1666829 |

</details>

<details><summary><b>analogshift</b> — famille <code>id, title</code>, 36 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `body_html` | 100 % | <p><span>The Annual Calendar is a complication </span><i><sp… |
| `created_at` | 100 % | 2026-08-03T13:56:43-04:00 |
| `handle` | 100 % | patek-philippe-annual-calendar-moonphase-as12476 |
| `id` | 100 % | 7721647603799 |
| `images[].created_at` | 100 % | 2026-08-11T14:08:11-04:00 |
| `images[].height` | 100 % | 2500 |
| `images[].id` | 100 % | 35818884694103 |
| `images[].position` | 100 % | 3 |
| `images[].product_id` | 100 % | 7721647603799 |
| `images[].src` | 100 % | https://cdn.shopify.com/s/files/1/0809/1255/files/AS12476_40… |
| `images[].updated_at` | 100 % | 2026-08-11T14:08:13-04:00 |
| `images[].width` | 100 % | 2500 |
| `options[].name` | 100 % | Title |
| `options[].position` | 100 % | 1 |
| `published_at` | 100 % | 2026-08-24T09:43:17-04:00 |
| `title` | 100 % | Patek Philippe Annual Calendar Moonphase |
| `updated_at` | 100 % | 2026-08-25T07:29:05-04:00 |
| `variants[].available` | 100 % | True |
| `variants[].created_at` | 100 % | 2026-08-03T13:56:44-04:00 |
| `variants[].grams` | 100 % | 1361 |
| `variants[].id` | 100 % | 44099616505943 |
| `variants[].option1` | 100 % | Default Title |
| `variants[].position` | 100 % | 1 |
| `variants[].price` | 100 % | 67000.00 |
| `variants[].product_id` | 100 % | 7721647603799 |
| `variants[].requires_shipping` | 100 % | True |
| `variants[].taxable` | 100 % | True |
| `variants[].title` | 100 % | Default Title |
| `variants[].updated_at` | 100 % | 2026-08-25T07:29:05-04:00 |
| `vendor` | 100 % | Patek Philippe |
| `product_type` | 99 % | Watch |
| `variants[].sku` | 96 % | 40931072 |
| `variants[].compare_at_price` | 5 % | 39.00 |
| `variants[].featured_image` | 0 % | — |
| `variants[].option2` | 0 % | — |
| `variants[].option3` | 0 % | — |

</details>

<details><summary><b>artcurial</b> — famille <code>adjudicationPrice, finalPrice, publishLot</code>, 53 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `adjudicationDate` | 100 % | 2024-07-09T17:30:00Z |
| `adjudicationPrice` | 100 % | 5000.0 |
| `category` | 100 % | OTHER |
| `currency` | 100 % | EUR |
| `finalPrice` | 100 % | 6560.0 |
| `high` | 100 % | 6000.0 |
| `index` | 100 % | 309 |
| `low` | 100 % | 4000.0 |
| `pictures[].document.blobName` | 100 % | 70555/PICTURE_CATALOG/140_309_002.jpg |
| `pictures[].document.documentName` | 100 % | 140_309_002.jpg |
| `pictures[].document.mediaLink` | 100 % | https://storage.googleapis.com/download/storage/v1/b/art-fr-… |
| `pictures[].document.servingUrl` | 100 % | https://storage.googleapis.com/art-fr-maya-prod-inventory/70… |
| `pictures[].document.status` | 100 % | ACCEPTED |
| `pictures[].document.type` | 100 % | PICTURE_CATALOG |
| `pictures[].document.uuid` | 100 % | 4ca8a76c-d4ff-442f-bb69-3d0bccd5dd98 |
| `pictures[].document.visibility` | 100 % | PUBLIC |
| `pictures[].index` | 100 % | 2 |
| `pictures[].uuid` | 100 % | 4ca8a76c-d4ff-442f-bb69-3d0bccd5dd98 |
| `publishLot` | 100 % | True |
| `reserve` | 100 % | 4000.0 |
| `reserveType` | 100 % | FIRM |
| `saleRef` | 100 % | M1120 |
| `status` | 100 % | SOLD |
| `subIndex` | 100 % | a |
| `techId` | 100 % | 36597 |
| `tenant` | 100 % | mc |
| `type` | 100 % | OTHER |
| `uuid` | 100 % | 9a3e050b-def5-4ed3-a90a-8c7c90f63959 |
| `vacationRef` | 100 % | mc-M1120-1 |
| `descriptions.FRENCH.descriptionWithHtml` | 91 % | <p><br/>Vers 2010<br/><br/>Montre bracelet en or rose 18k (7… |
| `descriptions.FRENCH.locale` | 91 % | FRENCH |
| `descriptions.FRENCH.shortDescription` | 91 % | HERMES |
| `descriptions.FRENCH.titleWithHtml` | 91 % | HERMES  Kilim, ref. KL1 272, n° 2419580 |
| `pictures[].mediaType` | 76 % | PICTURE |
| `descriptions.FRENCH.comment` | 68 % | DEMANDE EN COURS (4.12.2023)
Ex Esti 7500/9000 |
| `descriptions.FRENCH.number` | 13 % | <p><br/>Vers 2010<br/><br/>Montre bracelet en or rose 18k (7… |
| `descriptions.ENGLISH.descriptionWithHtml` | 9 % | <p><br/>Vers 1910<br/><br/>Montre pendentif en platine (950)… |
| `descriptions.ENGLISH.locale` | 9 % | ENGLISH |
| `descriptions.ENGLISH.number` | 9 % | <p><br/>Vers 1910<br/><br/>Montre pendentif en platine (950)… |
| `descriptions.ENGLISH.titleWithHtml` | 9 % | BOUCHERON & FERNAND PAILLET  " Belle Époque " |
| `descriptions.ENGLISH.typeOfPiece` | 9 % | Autre |
| `descriptions.FRENCH.typeOfPiece` | 1 % | Autre |
| `descriptions.ENGLISH.author` | 0 % | — |
| `descriptions.ENGLISH.comment` | 0 % | — |
| `descriptions.ENGLISH.publishingDate` | 0 % | — |

</details>

<details><summary><b>artcurial</b> — famille <code>adjudicationPrice, artistName, finalPrice</code>, 35 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `adjudicationDate` | 100 % | 2023-12-15T15:00:00Z |
| `adjudicationPrice` | 100 % | 2800.0 |
| `artistName` | 100 % | BLANCPAIN |
| `category` | 100 % | ART_WORK |
| `currency` | 100 % | EUR |
| `descriptions.FRENCH.descriptionWithHtml` | 100 % | <p>Vers 2000<br/><br/>Montre bracelet en acier avec calendri… |
| `descriptions.FRENCH.locale` | 100 % | FRENCH |
| `descriptions.FRENCH.shortDescription` | 100 % | BLANCPAIN  N° 409 |
| `descriptions.FRENCH.titleWithHtml` | 100 % | N° 409 |
| `finalPrice` | 100 % | 3674.0 |
| `high` | 100 % | 3000.0 |
| `index` | 100 % | 3 |
| `low` | 100 % | 2000.0 |
| `pictures[].document.blobName` | 100 % | /413/10772413_Vue 03.jpg |
| `pictures[].document.documentName` | 100 % | 10772413_Vue 03.jpg |
| `pictures[].document.mediaLink` | 100 % | https://storage.googleapis.com/art-fr-maya-prod-inventory/FR… |
| `pictures[].document.servingUrl` | 100 % | https://storage.googleapis.com/art-fr-maya-prod-inventory/FR… |
| `pictures[].document.status` | 100 % | ACCEPTED |
| `pictures[].document.type` | 100 % | PICTURE_CATALOG |
| `pictures[].document.uuid` | 100 % | 151b11ac-ce1d-460e-813f-a458094b4804 |
| `pictures[].document.visibility` | 100 % | PUBLIC |
| `pictures[].index` | 100 % | 3 |
| `pictures[].uuid` | 100 % | 45a40ae5-dfa7-11ef-bd8e-9744e5e7258b |
| `publishLot` | 100 % | True |
| `reserve` | 100 % | 2000.0 |
| `reserveType` | 100 % | FIRM |
| `saleRef` | 100 % | IT4411 |
| `status` | 100 % | SOLD |
| `subIndex` | 100 % | a |
| `techId` | 100 % | 687759 |
| `tenant` | 100 % | fr |
| `type` | 100 % | OTHER |
| `uuid` | 100 % | 37b63868-a578-4c28-8599-c84860feceba |
| `vacationRef` | 100 % | fr-IT4411-1 |
| `descriptions.FRENCH.number` | 38 % | <p>Circa 1940<br/><br/>Pendulette de table en forme de briqu… |

</details>

<details><summary><b>artcurial</b> — famille <code>adjudicationPrice, finalPrice, publishLot</code>, 41 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `adjudicationDate` | 100 % | 2026-07-06T15:08:39.141299Z |
| `adjudicationPrice` | 100 % | 1500.0 |
| `category` | 100 % | JEWELRY |
| `currency` | 100 % | EUR |
| `descriptions.ENGLISH.brand` | 100 % | BREITLING  |
| `descriptions.ENGLISH.descriptionWithHtml` | 100 % | <p>Ref. C17391</p>
<p>N° 1453346</p>
<p>Vers 2015</p>
<p><br… |
| `descriptions.ENGLISH.locale` | 100 % | ENGLISH |
| `descriptions.ENGLISH.titleWithHtml` | 100 % | BREITLING  SuperOcean 44 |
| `finalPrice` | 100 % | 1986.0 |
| `high` | 100 % | 1500.0 |
| `index` | 100 % | 101 |
| `low` | 100 % | 1000.0 |
| `pictures[].document.blobName` | 100 % | 7f6be262-6994-11f1-b65a-8f795976a899/PICTURE_CATALOG/D 26201… |
| `pictures[].document.documentName` | 100 % | D 26201537-002 B_BT260503_026_BRI__RVB HDef.jpg |
| `pictures[].document.mediaLink` | 100 % | https://storage.googleapis.com/download/storage/v1/b/art-fr-… |
| `pictures[].document.servingUrl` | 100 % | https://storage.googleapis.com/art-fr-maya-prod-inventory/7f… |
| `pictures[].document.status` | 100 % | ACCEPTED |
| `pictures[].document.type` | 100 % | PICTURE_CATALOG |
| `pictures[].document.uuid` | 100 % | 7f6be262-6994-11f1-b65a-8f795976a899 |
| `pictures[].document.visibility` | 100 % | PUBLIC |
| `pictures[].index` | 100 % | 2 |
| `pictures[].mediaType` | 100 % | PICTURE |
| `pictures[].uuid` | 100 % | 199c23fe-5f6a-48f9-90cb-0bc2ab3ff331 |
| `properties.depthUnit` | 100 % | CM |
| `properties.heightUnit` | 100 % | CM |
| `properties.weightUnit` | 100 % | KILOGRAM |
| `properties.widthUnit` | 100 % | CM |
| `publishLot` | 100 % | True |
| `reserve` | 100 % | 1000.0 |
| `reserveType` | 100 % | FIRM |
| `saleRef` | 100 % | MC-6026 |
| `status` | 100 % | SOLD |
| `subIndex` | 100 % | a |
| `techId` | 100 % | 40157 |
| `tenant` | 100 % | mc |
| `type` | 100 % | WATCH_VARIOUS |
| `uuid` | 100 % | f6deacd0-63fb-11f1-88f2-cd4428fcbfa4 |
| `vacationRef` | 100 % | mc-MC-6026-1 |
| `descriptions.ENGLISH.model` | 82 % | SuperOcean 44 |
| `descriptions.ENGLISH.reference` | 0 % | — |
| `descriptions.ENGLISH.state` | 0 % | — |

</details>

<details><summary><b>awco</b> — famille <code>id, name, price_html</code>, 79 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `_links.collection[].href` | 100 % | https://awco.nl/wp-json/wc/store/v1/products |
| `_links.related[].embeddable` | 100 % | True |
| `_links.related[].href` | 100 % | https://awco.nl/wp-json/wc/store/v1/products?related=587614&… |
| `_links.self[].href` | 100 % | https://awco.nl/wp-json/wc/store/v1/products/587614 |
| `add_to_cart.description` | 100 % | Add to cart: &ldquo;Cartier Tank Allongee Ref.2443&rdquo; |
| `add_to_cart.maximum` | 100 % | 1 |
| `add_to_cart.minimum` | 100 % | 1 |
| `add_to_cart.multiple_of` | 100 % | 1 |
| `add_to_cart.single_text` | 100 % | Add to cart |
| `add_to_cart.text` | 100 % | Add to cart |
| `add_to_cart.url` | 100 % | /wp-json/wc/store/v1/products?per_page=100&#038;page=1&#038;… |
| `average_rating` | 100 % | 0 |
| `has_options` | 100 % | False |
| `id` | 100 % | 587614 |
| `images[].id` | 100 % | 587617 |
| `images[].name` | 100 % | Cartier-44378953-3 |
| `images[].sizes` | 100 % | (max-width: 1177px) 100vw, 1177px |
| `images[].src` | 100 % | https://awco.nl/wp-content/uploads/2026/08/Cartier-44378953-… |
| `images[].srcset` | 100 % | https://awco.nl/wp-content/uploads/2026/08/Cartier-44378953-… |
| `images[].thumbnail` | 100 % | https://awco.nl/wp-content/uploads/2026/08/Cartier-44378953-… |
| `images[].thumbnail_sizes` | 100 % | (max-width: 400px) 100vw, 400px |
| `images[].thumbnail_srcset` | 100 % | https://awco.nl/wp-content/uploads/2026/08/Cartier-44378953-… |
| `is_in_stock` | 100 % | True |
| `is_on_backorder` | 100 % | False |
| `is_password_protected` | 100 % | False |
| `is_purchasable` | 100 % | True |
| `name` | 100 % | Cartier Tank Allongee Ref.2443 |
| `on_sale` | 100 % | False |
| `parent` | 100 % | 0 |
| `permalink` | 100 % | https://awco.nl/shop/vintage-watches/cartier-tank-allongee-r… |
| `prices.currency_code` | 100 % | EUR |
| `prices.currency_decimal_separator` | 100 % | , |
| `prices.currency_minor_unit` | 100 % | 0 |
| `prices.currency_prefix` | 100 % | €  |
| `prices.currency_symbol` | 100 % | € |
| `prices.currency_thousand_separator` | 100 % | . |
| `prices.price` | 100 % | 6900 |
| `prices.regular_price` | 100 % | 6900 |
| `prices.sale_price` | 100 % | 6900 |
| `review_count` | 100 % | 0 |
| `slug` | 100 % | cartier-tank-allongee-ref-2443 |
| `sold_individually` | 100 % | False |
| `stock_availability.class` | 100 % | in-stock |
| `type` | 100 % | simple |
| `attributes[].has_variations` | 99 % | False |

</details>

<details><summary><b>awco</b> — famille <code>id, name</code>, 3 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `id` | 100 % | 6516 |
| `name` | 100 % | Aquarelle |
| `slug` | 100 % | aquarelle |

</details>

<details><summary><b>berrys</b> — famille <code>id, title</code>, 36 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `body_html` | 100 % | <p>FOPE Panorama 18ct Yellow Gold Triple Pavé Diamond Rondel… |
| `created_at` | 100 % | 2026-08-25T11:30:36+01:00 |
| `handle` | 100 % | fope-panorama-yellow-gold-triple-diamond-bracelet-58704bx |
| `id` | 100 % | 16059977138558 |
| `images[].created_at` | 100 % | 2026-08-25T11:44:37+01:00 |
| `images[].height` | 100 % | 1200 |
| `images[].id` | 100 % | 85685058797950 |
| `images[].position` | 100 % | 3 |
| `images[].product_id` | 100 % | 16059977138558 |
| `images[].src` | 100 % | https://cdn.shopify.com/s/files/1/0667/9340/6783/files/58704… |
| `images[].updated_at` | 100 % | 2026-08-25T11:44:40+01:00 |
| `images[].width` | 100 % | 1200 |
| `options[].name` | 100 % | Title |
| `options[].position` | 100 % | 1 |
| `product_type` | 100 % | Bracelets & Bangles |
| `published_at` | 100 % | 2026-08-25T12:26:29+01:00 |
| `title` | 100 % | Panorama 18ct Yellow Gold Triple Pavé Diamond Rondel Bracele… |
| `updated_at` | 100 % | 2026-08-25T12:31:02+01:00 |
| `variants[].available` | 100 % | True |
| `variants[].created_at` | 100 % | 2026-08-25T11:30:37+01:00 |
| `variants[].grams` | 100 % | 0 |
| `variants[].id` | 100 % | 57913259229566 |
| `variants[].option1` | 100 % | Default Title |
| `variants[].position` | 100 % | 1 |
| `variants[].price` | 100 % | 11250.00 |
| `variants[].product_id` | 100 % | 16059977138558 |
| `variants[].requires_shipping` | 100 % | True |
| `variants[].taxable` | 100 % | True |
| `variants[].title` | 100 % | Default Title |
| `variants[].updated_at` | 100 % | 2026-08-25T12:31:02+01:00 |
| `vendor` | 100 % | FOPE |
| `variants[].sku` | 98 % | 58704BX_PB_G_BBB_00M |
| `variants[].compare_at_price` | 7 % | 34900.00 |
| `variants[].featured_image` | 0 % | — |
| `variants[].option2` | 0 % | — |
| `variants[].option3` | 0 % | — |

</details>

<details><summary><b>bulangandsons</b> — famille <code>id, title</code>, 36 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `body_html` | 100 % | <p>The Rolex Air-King ref. 5500, produced from 1957 to 1989,… |
| `created_at` | 100 % | 2026-08-28T11:16:38+02:00 |
| `handle` | 100 % | rolex-oyster-perpetual-air-king-5500-silver-no-lume-arabic-n… |
| `id` | 100 % | 16542316265817 |
| `images[].created_at` | 100 % | 2026-08-28T11:21:13+02:00 |
| `images[].height` | 100 % | 2048 |
| `images[].id` | 100 % | 92171567890777 |
| `images[].position` | 100 % | 3 |
| `images[].product_id` | 100 % | 16542316265817 |
| `images[].src` | 100 % | https://cdn.shopify.com/s/files/1/0961/8613/8969/files/W-377… |
| `images[].updated_at` | 100 % | 2026-08-28T11:21:16+02:00 |
| `images[].width` | 100 % | 2048 |
| `options[].name` | 100 % | Title |
| `options[].position` | 100 % | 1 |
| `product_type` | 100 % | Watch |
| `published_at` | 100 % | 2026-08-28T11:27:42+02:00 |
| `title` | 100 % | Rolex Oyster Perpetual Air-King 5500 Silver no-lume Arabic N… |
| `updated_at` | 100 % | 2026-08-28T16:25:42+02:00 |
| `variants[].available` | 100 % | True |
| `variants[].created_at` | 100 % | 2026-08-28T11:16:38+02:00 |
| `variants[].grams` | 100 % | 0 |
| `variants[].id` | 100 % | 59195540439385 |
| `variants[].option1` | 100 % | Default Title |
| `variants[].position` | 100 % | 1 |
| `variants[].price` | 100 % | 4400.00 |
| `variants[].product_id` | 100 % | 16542316265817 |
| `variants[].requires_shipping` | 100 % | True |
| `variants[].sku` | 100 % | W-3776 |
| `variants[].taxable` | 100 % | False |
| `variants[].title` | 100 % | Default Title |
| `variants[].updated_at` | 100 % | 2026-08-28T16:25:42+02:00 |
| `vendor` | 100 % | Rolex |
| `variants[].compare_at_price` | 42 % | 0.00 |
| `variants[].option2` | 5 % | REGULAR |
| `variants[].featured_image` | 0 % | — |
| `variants[].option3` | 0 % | — |

</details>

<details><summary><b>christies</b> — famille <code>analytics_id, current_bid, lot_estimate_txt</code>, 33 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `analytics_id` | 100 % | 17561.1 |
| `description_txt` | 100 % | OMEGA, SEAMASTER 'ANAKIN SKYWALKER', REF. 145.023<br>
<br>
C… |
| `end_date` | 100 % | 2019-03-12T04:00Z |
| `estimate_high` | 100 % | 6000.0 |
| `estimate_low` | 100 % | 3000.0 |
| `estimate_on_request` | 100 % | False |
| `estimate_txt` | 100 % | USD 3,000 - 6,000 |
| `estimate_visible` | 100 % | True |
| `event_type` | 100 % | OnlineSale |
| `image.image_alt_text` | 100 % | OMEGA, SEAMASTER 'ANAKIN SKYWALKER', REF. 145.023 |
| `image.image_desktop_src` | 100 % | https://www.christies.com/img/lotimages/2019/NYR/2019_NYR_17… |
| `image.image_mobile_src` | 100 % | https://www.christies.com/img/lotimages/2019/NYR/2019_NYR_17… |
| `image.image_src` | 100 % | https://www.christies.com/img/lotimages/2019/NYR/2019_NYR_17… |
| `image.image_tablet_src` | 100 % | https://www.christies.com/img/lotimages/2019/NYR/2019_NYR_17… |
| `is_auction_over` | 100 % | True |
| `is_in_progress` | 100 % | False |
| `is_saved` | 100 % | False |
| `lot_id_txt` | 100 % | 1 |
| `lot_withdrawn` | 100 % | False |
| `object_id` | 100 % | 6191314 |
| `price_on_request` | 100 % | False |
| `price_realised` | 100 % | 4375.0 |
| `price_realised_txt` | 100 % | USD 4,375 |
| `show_save` | 100 % | True |
| `start_date` | 100 % | 2019-02-26T00:00Z |
| `title_primary_txt` | 100 % | OMEGA, SEAMASTER 'ANAKIN SKYWALKER', REF. 145.023 |
| `url` | 100 % | https://www.christies.com/en/sso?ObjectID=17561.1&LotNumber=… |
| `consigner_information` | 2 % | Property of an Elegant Lady |
| `current_bid` | 0 % | — |
| `current_bid_txt` | 0 % | — |
| `lot_estimate_txt` | 0 % | — |
| `title_secondary_txt` | 0 % | — |
| `title_tertiary_txt` | 0 % | — |

</details>

<details><summary><b>christies</b> — famille <code>analytics_id, event_id, subtitle_txt</code>, 29 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `analytics_id` | 100 % | Sale-18454 |
| `cta_txt` | 100 % | View Results |
| `date_display_txt` | 100 % | 29 May |
| `date_sr_txt` | 100 % | 29 May |
| `end_date` | 100 % | 2019-05-29T00:00:00 |
| `event_id` | 100 % | 28508 |
| `filter_ids` | 100 % | |category_5|location_35|event_0||event_live| |
| `image.alt_text` | 100 % | Four Masterpieces of Jun Ware |
| `image.breakpoints[].name` | 100 % | md |
| `image.breakpoints[].srcset[].src` | 100 % | https://www.christies.com/img/SaleImages/HGK-18454-05292019-… |
| `image.breakpoints[].srcset[].width` | 100 % | 1200 |
| `image.placeholder.name` | 100 % | px |
| `image.placeholder.srcset[].src` | 100 % | https://www.christies.com/img/SaleImages/HGK-18454-05292019-… |
| `image.placeholder.srcset[].width` | 100 % | 1 |
| `is_active` | 100 % | True |
| `is_followed` | 100 % | False |
| `is_in_progress` | 100 % | False |
| `is_live` | 100 % | True |
| `is_on_view` | 100 % | False |
| `landing_url` | 100 % | https://www.christies.com/en/auction/four-masterpieces-of-ju… |
| `location_txt` | 100 % | Hong Kong |
| `on_view_txt` | 100 % | On View |
| `sale_total_txt` | 100 % | Sale Total |
| `sale_total_value_txt` | 100 % | HKD 14,525,000 |
| `start_date` | 100 % | 2019-05-29T00:00:00 |
| `subtitle_txt` | 100 % | Live Auction 18454 | CLOSED |
| `title_id` | 100 % | month5 |
| `title_txt` | 100 % | Four Masterpieces of Jun Ware |
| `status_txt` | 0 % | — |

</details>

<details><summary><b>christies</b> — famille <code>analytics_id, id</code>, 6 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `analytics_id` | 100 % | Year-2026 |
| `id` | 100 % | 2026 |
| `label_txt` | 100 % | 2026 |
| `show` | 100 % | True |
| `total` | 100 % | 0 |
| `type` | 100 % | year |

</details>

<details><summary><b>chronofinder</b> — famille <code>id, name, price_html</code>, 79 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `_links.collection[].href` | 100 % | https://chronofinder.com/wp-json/wc/store/products |
| `_links.related[].embeddable` | 100 % | True |
| `_links.related[].href` | 100 % | https://chronofinder.com/wp-json/wc/store/products?related=1… |
| `_links.self[].href` | 100 % | https://chronofinder.com/wp-json/wc/store/products/18791 |
| `add_to_cart.description` | 100 % | Add to basket: &ldquo;Sky-Dweller 336933 (Champagne Dial) Oy… |
| `add_to_cart.maximum` | 100 % | 1 |
| `add_to_cart.minimum` | 100 % | 1 |
| `add_to_cart.multiple_of` | 100 % | 1 |
| `add_to_cart.single_text` | 100 % | Add to basket |
| `add_to_cart.text` | 100 % | Add to basket |
| `add_to_cart.url` | 100 % | /wp-json/wc/store/products?per_page=100&#038;page=1&#038;add… |
| `average_rating` | 100 % | 0 |
| `brands[].id` | 100 % | 1377 |
| `brands[].link` | 100 % | https://chronofinder.com/brand/rolex |
| `brands[].name` | 100 % | Rolex |
| `brands[].slug` | 100 % | rolex |
| `categories[].id` | 100 % | 1428 |
| `categories[].link` | 100 % | https://chronofinder.com/collections/mens-watches |
| `categories[].name` | 100 % | Men's Watches |
| `categories[].slug` | 100 % | mens-watches |
| `has_options` | 100 % | False |
| `id` | 100 % | 18791 |
| `images[].id` | 100 % | 18795 |
| `images[].name` | 100 % | Photoroom_20260827_53825?pm |
| `images[].sizes` | 100 % | (max-width: 1080px) 100vw, 1080px |
| `images[].src` | 100 % | https://chronofinder.com/wp-content/uploads/2026/08/Photoroo… |
| `images[].srcset` | 100 % | https://chronofinder.com/wp-content/uploads/2026/08/Photoroo… |
| `images[].thumbnail` | 100 % | https://chronofinder.com/wp-content/uploads/2026/08/Photoroo… |
| `images[].thumbnail_sizes` | 100 % | (max-width: 300px) 100vw, 300px |
| `images[].thumbnail_srcset` | 100 % | https://chronofinder.com/wp-content/uploads/2026/08/Photoroo… |
| `is_in_stock` | 100 % | True |
| `is_on_backorder` | 100 % | False |
| `is_password_protected` | 100 % | False |
| `is_purchasable` | 100 % | True |
| `name` | 100 % | Sky-Dweller 336933 (Champagne Dial) Oyster |
| `on_sale` | 100 % | False |
| `parent` | 100 % | 0 |
| `permalink` | 100 % | https://chronofinder.com/products/rolex-sky-dweller-336933-s… |
| `prices.currency_code` | 100 % | GBP |
| `prices.currency_decimal_separator` | 100 % | . |
| `prices.currency_minor_unit` | 100 % | 0 |
| `prices.currency_prefix` | 100 % | £ |
| `prices.currency_symbol` | 100 % | £ |
| `prices.currency_thousand_separator` | 100 % | , |
| `prices.price` | 100 % | 16995 |

</details>

<details><summary><b>craft_and_tailored</b> — famille <code>id, title</code>, 36 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `body_html` | 100 % | <p>Military-issued chronographs represent one of the most co… |
| `created_at` | 100 % | 2026-08-24T16:23:27-07:00 |
| `handle` | 100 % | 1960s-lemania-mono-pusher-chronograph-royal-navy-nuclear-sub… |
| `id` | 100 % | 8231853523053 |
| `images[].created_at` | 100 % | 2026-08-24T17:33:15-07:00 |
| `images[].height` | 100 % | 2560 |
| `images[].id` | 100 % | 39247884583021 |
| `images[].position` | 100 % | 3 |
| `images[].product_id` | 100 % | 8231853523053 |
| `images[].src` | 100 % | https://cdn.shopify.com/s/files/1/1104/9180/files/LSA_2494_5… |
| `images[].updated_at` | 100 % | 2026-08-24T17:33:17-07:00 |
| `images[].width` | 100 % | 1920 |
| `options[].name` | 100 % | Title |
| `options[].position` | 100 % | 1 |
| `product_type` | 100 % | Timepiece |
| `published_at` | 100 % | 2026-08-24T17:38:06-07:00 |
| `title` | 100 % | 1960s Lemania Mono-Pusher Chronograph (Royal Navy Nuclear Su… |
| `updated_at` | 100 % | 2026-08-25T01:05:07-07:00 |
| `variants[].available` | 100 % | True |
| `variants[].created_at` | 100 % | 2026-08-24T16:23:27-07:00 |
| `variants[].grams` | 100 % | 0 |
| `variants[].id` | 100 % | 45697663664237 |
| `variants[].option1` | 100 % | Default Title |
| `variants[].position` | 100 % | 1 |
| `variants[].price` | 100 % | 15000.00 |
| `variants[].product_id` | 100 % | 8231853523053 |
| `variants[].requires_shipping` | 100 % | True |
| `variants[].sku` | 100 % | LMMOD3312RNNS |
| `variants[].taxable` | 100 % | True |
| `variants[].title` | 100 % | Default Title |
| `variants[].updated_at` | 100 % | 2026-08-25T01:05:07-07:00 |
| `vendor` | 100 % | Other |
| `variants[].compare_at_price` | 5 % | 0.00 |
| `variants[].featured_image` | 0 % | — |
| `variants[].option2` | 0 % | — |
| `variants[].option3` | 0 % | — |

</details>

<details><summary><b>cwsellors</b> — famille <code>id, title</code>, 36 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `body_html` | 100 % | <p>Doxa Sub 200 II Sea Emerald Rubber Strap Watch</p>
The SU… |
| `created_at` | 100 % | 2026-08-25T14:08:26+01:00 |
| `handle` | 100 % | doxa-sub-200-ii-sea-emerald-rubber-strap-watch-795-10-131-26 |
| `id` | 100 % | 15736651645305 |
| `images[].created_at` | 100 % | 2026-08-25T16:07:44+01:00 |
| `images[].height` | 100 % | 762 |
| `images[].id` | 100 % | 83104844874105 |
| `images[].position` | 100 % | 3 |
| `images[].product_id` | 100 % | 15736651645305 |
| `images[].src` | 100 % | https://cdn.shopify.com/s/files/1/0248/7892/files/795.10.131… |
| `images[].updated_at` | 100 % | 2026-08-25T16:07:47+01:00 |
| `images[].width` | 100 % | 700 |
| `options[].name` | 100 % | Title |
| `options[].position` | 100 % | 1 |
| `product_type` | 100 % | Watch |
| `published_at` | 100 % | 2026-08-25T16:09:25+01:00 |
| `title` | 100 % | Doxa Sub 200 II Sea Emerald Rubber Strap  Watch |
| `updated_at` | 100 % | 2026-08-27T19:23:44+01:00 |
| `variants[].available` | 100 % | True |
| `variants[].compare_at_price` | 100 % | 1158.33 |
| `variants[].created_at` | 100 % | 2026-08-25T14:08:26+01:00 |
| `variants[].grams` | 100 % | 0 |
| `variants[].id` | 100 % | 64365357007225 |
| `variants[].option1` | 100 % | Default Title |
| `variants[].position` | 100 % | 1 |
| `variants[].price` | 100 % | 1158.33 |
| `variants[].product_id` | 100 % | 15736651645305 |
| `variants[].requires_shipping` | 100 % | True |
| `variants[].sku` | 100 % | DOX-333 |
| `variants[].taxable` | 100 % | True |
| `variants[].title` | 100 % | Default Title |
| `variants[].updated_at` | 100 % | 2026-08-27T19:23:44+01:00 |
| `vendor` | 100 % | Doxa |
| `variants[].featured_image` | 0 % | — |
| `variants[].option2` | 0 % | — |
| `variants[].option3` | 0 % | — |

</details>

<details><summary><b>everywatch</b> — famille <code>auctionLotType, defaultManufacturerId, defaultManufacturerName</code>, 278 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `auctionLotType` | 100 % | RESULT |
| `buyersPremiumRate` | 100 % | 22 |
| `certificationId` | 100 % | 0 |
| `conditionName` | 100 % | Pre Owned |
| `countryCode` | 100 % | GBR |
| `countryName` | 100 % | United Kingdom |
| `createdDate` | 100 % | 2026-08-22T06:36:47.417Z |
| `defaultManufacturerId` | 100 % | 257 |
| `defaultManufacturerName` | 100 % | Rolex |
| `eventCityName` | 100 % | Perth |
| `eventCountryName` | 100 % | United Kingdom |
| `eventPublishEndDate` | 100 % | 2026-08-27T00:00:00Z |
| `eventPublishTitle` | 100 % | Four Day Auction of Garden Furniture & Stoneware, Tools, Cer… |
| `eventPublistStartDate` | 100 % | 2026-08-27T00:00:00Z |
| `eventSlug` | 100 % | four-day-auction-of-garden-furniture-stoneware,-tools,-ceram… |
| `eventTypeId` | 100 % | 1 |
| `id` | 100 % | 0 |
| `infoSourceId` | 100 % | 1985 |
| `infoSourceName` | 100 % | Iain M. Smith Auctioneers & Valuers |
| `infoSourcePriority` | 100 % | 0 |
| `infoSourceSlug` | 100 % | iain-m.-smith-auctioneers-valuers--id1985 |
| `isBox` | 100 % | False |
| `isBuyersPremiumIncluded` | 100 % | False |
| `isPaper` | 100 % | False |
| `lotNumber` | 100 % | 2320 |
| `lotStatusId` | 100 % | 2 |
| `manufactureName` | 100 % | Rolex |
| `manufacturerId` | 100 % | 257 |
| `manufacturerSlug` | 100 % | /rolex |
| `maxEstChf` | 100 % | 874.18 |
| `maxEstEur` | 100 % | 933.53 |
| `maxEstGbp` | 100 % | 800 |
| `maxEstHkd` | 100 % | 8527.9 |
| `maxEstSgd` | 100 % | 1382.58 |
| `maxEstUsd` | 100 % | 1087.89 |
| `minEstChf` | 100 % | 546.36 |
| `minEstEur` | 100 % | 583.46 |
| `minEstGbp` | 100 % | 500 |
| `minEstHkd` | 100 % | 5329.94 |
| `minEstSgd` | 100 % | 864.11 |
| `minEstUsd` | 100 % | 679.93 |
| `netPayableAed` | 100 % | 7006.7162 |
| `netPayableChf` | 100 % | 1533.0886 |
| `netPayableEur` | 100 % | 1637.179 |
| `netPayableGbp` | 100 % | 1403 |

</details>

<details><summary><b>everywatch</b> — famille <code>2 cles</code>, 5 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `key` | 100 % | manufacturer |
| `value.count` | 100 % | 500 |
| `value.getAll` | 100 % | False |
| `value.getChild` | 100 % | False |
| `value.search` | 0 % | — |

</details>

<details><summary><b>fortuna</b> — famille <code>guid, id, lot-category</code>, 59 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `_links.about[].href` | 100 % | https://fortunaauction.com/wp-json/wp/v2/types/lots |
| `_links.acf:post[].embeddable` | 100 % | True |
| `_links.acf:post[].href` | 100 % | https://fortunaauction.com/wp-json/wp/v2/auction-results/855… |
| `_links.collection[].href` | 100 % | https://fortunaauction.com/wp-json/wp/v2/lots |
| `_links.curies[].href` | 100 % | https://api.w.org/{rel} |
| `_links.curies[].name` | 100 % | wp |
| `_links.curies[].templated` | 100 % | True |
| `_links.self[].href` | 100 % | https://fortunaauction.com/wp-json/wp/v2/lots/85518 |
| `_links.wp:attachment[].href` | 100 % | https://fortunaauction.com/wp-json/wp/v2/media?parent=85518 |
| `_links.wp:term[].embeddable` | 100 % | True |
| `_links.wp:term[].href` | 100 % | https://fortunaauction.com/wp-json/wp/v2/lot-category?post=8… |
| `_links.wp:term[].taxonomy` | 100 % | lot-category |
| `acf.auction_estimate_high` | 100 % | 6000 |
| `acf.auction_estimate_low` | 100 % | 4000 |
| `acf.bp_applies` | 100 % | True |
| `acf.hammer_price` | 100 % | 2800 |
| `acf.lot_number` | 100 % | 1015 |
| `acf.lot_status` | 100 % | sold |
| `acf.related_auction` | 100 % | 85516 |
| `acf.sold` | 100 % | True |
| `content.protected` | 100 % | False |
| `content.rendered` | 100 % | <p><strong>ESTIMATED RETAIL PRICE:</strong> $6,000*<br /> *T… |
| `date` | 100 % | 2026-07-24T20:08:19 |
| `date_gmt` | 100 % | 2026-07-24T20:08:19 |
| `featured_media` | 100 % | 85554 |
| `guid.rendered` | 100 % | https://fortunaauction.com/?post_type=lots&#038;p=85518 |
| `id` | 100 % | 85518 |
| `link` | 100 % | https://fortunaauction.com/lots/omega-ladies-diamond-watch-i… |
| `meta._acf_changed` | 100 % | False |
| `meta._kad_post_footer` | 100 % | False |
| `meta._kad_post_header` | 100 % | False |
| `meta._kadence_starter_templates_imported_post` | 100 % | False |
| `modified` | 100 % | 2026-07-24T20:08:19 |
| `modified_gmt` | 100 % | 2026-07-24T20:08:19 |
| `slug` | 100 % | omega-ladies-diamond-watch-in-14k-white-gold |
| `status` | 100 % | publish |
| `title.rendered` | 100 % | Omega Ladies&#8217; Diamond Watch in 14K White Gold |
| `type` | 100 % | lots |
| `_links.wp:featuredmedia[].embeddable` | 99 % | True |
| `_links.wp:featuredmedia[].href` | 99 % | https://fortunaauction.com/wp-json/wp/v2/media/85554 |
| `acf.lot_gallery` | 99 % | 85554,85555 |
| `acf.buyers_premium_amount` | 8 % | 784 |
| `acf.total_with_bp` | 8 % | 3584 |
| `acf.bp_percent` | 5 % | 25 |
| `acf.auction_mobility_lot_url` | 0 % | — |

</details>

<details><summary><b>globalwatchshop</b> — famille <code>id, name, price_html</code>, 77 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `_links.collection[].href` | 100 % | https://www.globalwatchshop.co.uk/wp-json/wc/store/products |
| `_links.related[].embeddable` | 100 % | True |
| `_links.related[].href` | 100 % | https://www.globalwatchshop.co.uk/wp-json/wc/store/products?… |
| `_links.self[].href` | 100 % | https://www.globalwatchshop.co.uk/wp-json/wc/store/products/… |
| `add_to_cart.description` | 100 % | Read more about &ldquo;Preowned Rolex GMT-Master II 'Batman'… |
| `add_to_cart.maximum` | 100 % | 1 |
| `add_to_cart.minimum` | 100 % | 1 |
| `add_to_cart.multiple_of` | 100 % | 1 |
| `add_to_cart.single_text` | 100 % | Add to basket |
| `add_to_cart.text` | 100 % | Read more |
| `add_to_cart.url` | 100 % | https://www.globalwatchshop.co.uk/product/preowned-rolex-gmt… |
| `attributes[].has_variations` | 100 % | False |
| `attributes[].id` | 100 % | 44 |
| `attributes[].name` | 100 % | Box |
| `attributes[].taxonomy` | 100 % | pa_box |
| `attributes[].terms[].id` | 100 % | 728 |
| `attributes[].terms[].name` | 100 % | Yes |
| `attributes[].terms[].slug` | 100 % | yes |
| `average_rating` | 100 % | 0 |
| `categories[].id` | 100 % | 532 |
| `categories[].link` | 100 % | https://www.globalwatchshop.co.uk/brands/ |
| `categories[].name` | 100 % | Brands |
| `categories[].slug` | 100 % | brands |
| `has_options` | 100 % | False |
| `id` | 100 % | 19483 |
| `images[].id` | 100 % | 15331 |
| `images[].name` | 100 % | Preowned Rolex GMT-Master II Batman 126710BLNR |
| `images[].sizes` | 100 % | (max-width: 800px) 100vw, 800px |
| `images[].src` | 100 % | https://www.globalwatchshop.co.uk/wp-content/uploads/nc/p/r/… |
| `images[].thumbnail` | 100 % | https://www.globalwatchshop.co.uk/wp-content/uploads/nc/p/r/… |
| `images[].thumbnail_sizes` | 100 % | (max-width: 300px) 100vw, 300px |
| `is_in_stock` | 100 % | False |
| `is_on_backorder` | 100 % | False |
| `is_password_protected` | 100 % | False |
| `is_purchasable` | 100 % | True |
| `name` | 100 % | Preowned Rolex GMT-Master II 'Batman' 126710BLNR |
| `on_sale` | 100 % | False |
| `parent` | 100 % | 0 |
| `permalink` | 100 % | https://www.globalwatchshop.co.uk/product/preowned-rolex-gmt… |
| `price_html` | 100 % | <span class="poa-price">POA</span> |
| `prices.currency_code` | 100 % | GBP |
| `prices.currency_decimal_separator` | 100 % | . |
| `prices.currency_minor_unit` | 100 % | 2 |
| `prices.currency_prefix` | 100 % | £ |
| `prices.currency_symbol` | 100 % | £ |

</details>

<details><summary><b>hairspring</b> — famille <code>id, title</code>, 45 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `body_html` | 100 % | <p>A ref. 405.034 Datograph Up/Down Lumen, the fourth Lumen … |
| `created_at` | 100 % | 2026-08-19T16:30:22-06:00 |
| `handle` | 100 % | 405-034-datograph-up-down-lumen-platinum-1 |
| `id` | 100 % | 15988936245329 |
| `images[].created_at` | 100 % | 2026-08-24T01:22:03-06:00 |
| `images[].height` | 100 % | 2880 |
| `images[].id` | 100 % | 69731173072977 |
| `images[].position` | 100 % | 3 |
| `images[].product_id` | 100 % | 15988936245329 |
| `images[].src` | 100 % | https://cdn.shopify.com/s/files/1/0617/0830/4465/files/Untit… |
| `images[].updated_at` | 100 % | 2026-08-24T01:22:05-06:00 |
| `images[].width` | 100 % | 5120 |
| `options[].name` | 100 % | Title |
| `options[].position` | 100 % | 1 |
| `published_at` | 100 % | 2026-08-24T04:00:05-06:00 |
| `title` | 100 % | 405.034, Datograph Up/Down Lumen, Platinum |
| `updated_at` | 100 % | 2026-08-25T02:52:29-06:00 |
| `variants[].available` | 100 % | True |
| `variants[].created_at` | 100 % | 2026-08-19T16:30:23-06:00 |
| `variants[].grams` | 100 % | 0 |
| `variants[].id` | 100 % | 60100523688017 |
| `variants[].option1` | 100 % | Default Title |
| `variants[].position` | 100 % | 1 |
| `variants[].price` | 100 % | 378000.00 |
| `variants[].product_id` | 100 % | 15988936245329 |
| `variants[].requires_shipping` | 100 % | True |
| `variants[].taxable` | 100 % | True |
| `variants[].title` | 100 % | Default Title |
| `variants[].updated_at` | 100 % | 2026-08-25T02:52:29-06:00 |
| `vendor` | 100 % | Hairspring |
| `variants[].featured_image.created_at` | 5 % | 2026-08-10T22:44:01-06:00 |
| `variants[].featured_image.height` | 5 % | 2880 |
| `variants[].featured_image.id` | 5 % | 69610396287057 |
| `variants[].featured_image.position` | 5 % | 1 |
| `variants[].featured_image.product_id` | 5 % | 15967975374929 |
| `variants[].featured_image.src` | 5 % | https://cdn.shopify.com/s/files/1/0617/0830/4465/files/Atlas… |
| `variants[].featured_image.updated_at` | 5 % | 2026-08-10T22:44:03-06:00 |
| `variants[].featured_image.width` | 5 % | 5120 |
| `product_type` | 3 % | Watch Bands |
| `variants[].option2` | 2 % | 19mm |
| `variants[].option3` | 2 % | Steel |
| `variants[].compare_at_price` | 0 % | — |
| `variants[].featured_image` | 0 % | — |
| `variants[].featured_image.alt` | 0 % | — |
| `variants[].sku` | 0 % | — |

</details>

<details><summary><b>hodinkee</b> — famille <code>id, title</code>, 36 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `created_at` | 100 % | 2024-08-26T16:15:02-04:00 |
| `handle` | 100 % | zenith-chronomaster-original-triple-calendar-limited-edition… |
| `id` | 100 % | 7200548290635 |
| `options[].name` | 100 % | Title |
| `options[].position` | 100 % | 1 |
| `published_at` | 100 % | 2024-10-17T14:35:25-04:00 |
| `title` | 100 % | Chronomaster Original Triple Calendar Limited Edition For Ho… |
| `updated_at` | 100 % | 2026-08-28T09:15:27-04:00 |
| `variants[].available` | 100 % | True |
| `variants[].created_at` | 100 % | 2024-08-26T16:15:02-04:00 |
| `variants[].grams` | 100 % | 0 |
| `variants[].id` | 100 % | 40991107547211 |
| `variants[].option1` | 100 % | Default Title |
| `variants[].position` | 100 % | 1 |
| `variants[].price` | 100 % | 13500.00 |
| `variants[].product_id` | 100 % | 7200548290635 |
| `variants[].requires_shipping` | 100 % | True |
| `variants[].sku` | 100 % | 03.3401.3610.21.C911 |
| `variants[].taxable` | 100 % | True |
| `variants[].title` | 100 % | Default Title |
| `variants[].updated_at` | 100 % | 2026-08-28T09:15:27-04:00 |
| `vendor` | 100 % | Zenith |
| `body_html` | 91 % | <p>Our latest collaboration with Zenith features a modern tr… |
| `images[].created_at` | 91 % | 2024-09-11T14:19:19-04:00 |
| `images[].height` | 91 % | 3000 |
| `images[].id` | 91 % | 31970931179595 |
| `images[].position` | 91 % | 3 |
| `images[].product_id` | 91 % | 7200548290635 |
| `images[].src` | 91 % | https://cdn.shopify.com/s/files/1/0146/0732/files/Zenith-Det… |
| `images[].updated_at` | 91 % | 2024-09-11T14:19:21-04:00 |
| `images[].width` | 91 % | 3000 |
| `product_type` | 91 % | Limited Editions : New Watches : New Watch |
| `variants[].compare_at_price` | 14 % | 5400.00 |
| `variants[].featured_image` | 0 % | — |
| `variants[].option2` | 0 % | — |
| `variants[].option3` | 0 % | — |

</details>

<details><summary><b>keystone</b> — famille <code>id, title</code>, 36 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `body_html` | 100 % |     
        <br><b>Brand</b>: Rolex
        <br><b>Model</b… |
| `created_at` | 100 % | 2026-08-27T17:36:28-07:00 |
| `handle` | 100 % | rolex-cosmograph-daytona-paul-newman-watch-ref-6239 |
| `id` | 100 % | 9587277070575 |
| `images[].created_at` | 100 % | 2026-08-27T22:07:25-07:00 |
| `images[].height` | 100 % | 2372 |
| `images[].id` | 100 % | 49298431115503 |
| `images[].position` | 100 % | 3 |
| `images[].product_id` | 100 % | 9587277070575 |
| `images[].src` | 100 % | https://cdn.shopify.com/s/files/1/0207/2436/files/214628-3.j… |
| `images[].updated_at` | 100 % | 2026-08-27T22:07:27-07:00 |
| `images[].width` | 100 % | 2372 |
| `options[].name` | 100 % | Material |
| `options[].position` | 100 % | 3 |
| `product_type` | 100 % | Watches |
| `published_at` | 100 % | 2026-08-27T17:36:35-07:00 |
| `title` | 100 % | Rolex Cosmograph Daytona Paul Newman Watch Ref. 6239 |
| `updated_at` | 100 % | 2026-08-28T05:14:11-07:00 |
| `variants[].available` | 100 % | True |
| `variants[].created_at` | 100 % | 2026-08-27T17:36:31-07:00 |
| `variants[].grams` | 100 % | 0 |
| `variants[].id` | 100 % | 50629860589807 |
| `variants[].option1` | 100 % | Black |
| `variants[].position` | 100 % | 1 |
| `variants[].price` | 100 % | 325000.00 |
| `variants[].product_id` | 100 % | 9587277070575 |
| `variants[].requires_shipping` | 100 % | True |
| `variants[].sku` | 100 % | 214628 |
| `variants[].taxable` | 100 % | True |
| `variants[].title` | 100 % | Black / 36.5 mm / Steel |
| `variants[].updated_at` | 100 % | 2026-08-28T05:14:11-07:00 |
| `vendor` | 100 % | Rolex |
| `variants[].option3` | 99 % | Steel |
| `variants[].option2` | 98 % | 36.5 mm |
| `variants[].compare_at_price` | 0 % | — |
| `variants[].featured_image` | 0 % | — |

</details>

<details><summary><b>loupethis</b> — famille <code>id</code>, 28 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `attributes.bids_count` | 100 % | 0 |
| `attributes.buyers_premium_percent` | 100 % | 10 |
| `attributes.cms_id` | 100 % | 5b9dfe04-f928-4b3a-822c-9b5716227c3e |
| `attributes.comments_story_id` | 100 % | 49f67e87-0e06-4834-93c9-07e20e610e1c |
| `attributes.current_bid_price_cents` | 100 % | 0 |
| `attributes.ends_at` | 100 % | 2026-09-11T16:10:00.000Z |
| `attributes.featured_image_url` | 100 % | https://loupethis-production.sfo2.cdn.digitaloceanspaces.com… |
| `attributes.is_closed` | 100 % | False |
| `attributes.listed_at` | 100 % | 2026-08-27T21:38:39.512Z |
| `attributes.lot` | 100 % | 5208 |
| `attributes.next_bid_minimum_price_cents` | 100 % | 5000 |
| `attributes.related_auctions_count` | 100 % | 0 |
| `attributes.slug` | 100 % | seiko-spacewalk |
| `attributes.starts_at` | 100 % | 2026-09-04T16:00:00.000Z |
| `attributes.timestamp` | 100 % | 1787925454800 |
| `attributes.title` | 100 % | Seiko Spacewalk |
| `attributes.updated_at` | 100 % | 2026-08-27T21:38:39.519Z |
| `id` | 100 % | 49f67e87-0e06-4834-93c9-07e20e610e1c |
| `relationships.brand.data.id` | 100 % | f1691e45-d1ef-41de-b81a-06931b8f6a05 |
| `relationships.brand.data.type` | 100 % | brands |
| `type` | 100 % | auctions |
| `attributes.winning_bid_user_id` | 94 % | cf46864d-d3e8-432c-bf60-48270c4d6754 |
| `attributes.sold_price_cents` | 87 % | 1649890 |
| `attributes.theme_overlay_image_url` | 6 % | https://loupethis-production.sfo2.cdn.digitaloceanspaces.com… |
| `relationships.collections.data[].id` | 6 % | f1623480-252f-42f5-a51a-5d6187b4f747 |
| `relationships.collections.data[].type` | 6 % | collections |
| `attributes.cms_data` | 0 % | — |
| `relationships.subbrand.data` | 0 % | — |

</details>

<details><summary><b>loupethis</b> — famille <code>id</code>, 2 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `id` | 100 % | cdf4cf0f-3521-4f92-adc1-3c1631b56af4 |
| `type` | 100 % | auctions |

</details>

<details><summary><b>lyonandturnbull</b> — famille <code>@id, name</code>, 28 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `@context` | 100 % | https://schema.org |
| `@id` | 100 % | https://www.lyonandturnbull.com/#website |
| `@type` | 100 % | WebSite |
| `creator.@id` | 100 % | https://www.auctionfusion.com/#organization |
| `creator.@type` | 100 % | Organization |
| `creator.description` | 100 % | Auction Fusion designs, builds and powers websites for aucti… |
| `creator.name` | 100 % | Auction Fusion |
| `creator.url` | 100 % | https://www.auctionfusion.com/ |
| `description` | 100 % | The Lyon & Turnbull website was created by Auction Fusion. I… |
| `hasPart.@type` | 100 % | WebApplication |
| `hasPart.applicationCategory` | 100 % | BusinessApplication |
| `hasPart.name` | 100 % | StreamBid live bidding |
| `hasPart.provider.@id` | 100 % | https://stream.bid/#organization |
| `hasPart.provider.@type` | 100 % | Organization |
| `hasPart.provider.description` | 100 % | StreamBid provides live online bidding technology for auctio… |
| `hasPart.provider.name` | 100 % | StreamBid |
| `hasPart.provider.url` | 100 % | https://stream.bid/ |
| `hasPart.url` | 100 % | https://stream.bid/ |
| `name` | 100 % | Lyon & Turnbull |
| `provider.@id` | 100 % | https://www.auctionfusion.com/#organization |
| `provider.@type` | 100 % | Organization |
| `provider.description` | 100 % | Auction Fusion designs, builds and powers websites for aucti… |
| `provider.name` | 100 % | Auction Fusion |
| `provider.url` | 100 % | https://www.auctionfusion.com/ |
| `publisher.@type` | 100 % | Organization |
| `publisher.name` | 100 % | Lyon & Turnbull |
| `publisher.url` | 100 % | https://www.lyonandturnbull.com |
| `url` | 100 % | https://www.lyonandturnbull.com |

</details>

<details><summary><b>lyonandturnbull</b> — famille <code>name</code>, 32 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `@context` | 100 % | http://schema.org |
| `@type` | 100 % | WebPage |
| `breadcrumb.@context` | 100 % | https://schema.org |
| `breadcrumb.@type` | 100 % | BreadcrumbList |
| `breadcrumb.itemListElement[].@type` | 100 % | ListItem |
| `breadcrumb.itemListElement[].item` | 100 % | https://www.lyonandturnbull.com/auctions/jewellery-902 |
| `breadcrumb.itemListElement[].name` | 100 % | jewellery-902 |
| `breadcrumb.itemListElement[].position` | 100 % | 2 |
| `mainEntity.@type` | 100 % | Event |
| `mainEntity.about[].@type` | 100 % | Thing |
| `mainEntity.about[].name` | 100 % | Auction |
| `mainEntity.about[].sameAs` | 100 % | https://www.wikidata.org/wiki/Q177923 |
| `mainEntity.image` | 100 % | https://motivated-card-12d34c19bf.media.strapiapp.com/902_TH… |
| `mainEntity.location[].@type` | 100 % | VirtualLocation |
| `mainEntity.location[].address.@type` | 100 % | PostalAddress |
| `mainEntity.location[].address.addressCountry` | 100 % | GB |
| `mainEntity.location[].address.addressLocality` | 100 % | Edinburgh |
| `mainEntity.location[].address.postalCode` | 100 % | EH1 3RR |
| `mainEntity.location[].address.streetAddress` | 100 % | 33 Broughton Place |
| `mainEntity.location[].name` | 100 % | Lyon & Turnbull |
| `mainEntity.location[].url` | 100 % | https://www.lyonandturnbull.com/auctions/jewellery-902 |
| `mainEntity.name` | 100 % |  Jewellery | 03 June 2026 | 3 June 2026 |
| `mainEntity.organizer.@type` | 100 % | Organization |
| `mainEntity.organizer.name` | 100 % | Lyon & Turnbull |
| `mainEntity.organizer.url` | 100 % | https://www.lyonandturnbull.com |
| `mainEntity.startDate` | 100 % | 2026-06-03T09:00:00.000Z |
| `mainEntity.url` | 100 % | https://www.lyonandturnbull.com/auctions/jewellery-902 |
| `name` | 100 % |  Jewellery | 03 June 2026 | 3 June 2026 |
| `url` | 100 % | https://www.lyonandturnbull.com/auctions/jewellery-902 |
| `description` | 98 % | Join us online for our Jewellery auction which takes place l… |
| `mainEntity.description` | 98 % | Join us online for our Jewellery auction which takes place l… |
| `mainEntity.location[].address.addressRegion` | 0 % | — |

</details>

<details><summary><b>monacolegend</b> — famille <code>2 cles</code>, 80 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `@context` | 100 % | https://schema.org |
| `@graph[].@type` | 100 % | BreadcrumbList |
| `@graph[].endDate` | 100 % | 2026-07-25T14:24:00+00:00 |
| `@graph[].itemListElement[].@type` | 100 % | ListItem |
| `@graph[].itemListElement[].item` | 100 % | https://www.monacolegendauctions.com/auction |
| `@graph[].itemListElement[].name` | 100 % | Auctions |
| `@graph[].itemListElement[].position` | 100 % | 1 |
| `@graph[].name` | 100 % | Exclusive Timepieces |
| `@graph[].organizer.@type` | 100 % | Organization |
| `@graph[].organizer.logo.@type` | 100 % | ImageObject |
| `@graph[].organizer.logo.height.@type` | 100 % | QuantitativeValue |
| `@graph[].organizer.logo.height.value` | 100 % | 60 |
| `@graph[].organizer.logo.url` | 100 % | https://www.monacolegendauctions.com/images/mlg.png |
| `@graph[].organizer.logo.width.@type` | 100 % | QuantitativeValue |
| `@graph[].organizer.logo.width.value` | 100 % | 600 |
| `@graph[].organizer.name` | 100 % | Monaco Legend Group |
| `@graph[].organizer.sameAs` | 100 % | https://www.instagram.com/monacolegendgroup/ |
| `@graph[].organizer.url` | 100 % | https://monacolegendgroup.com |
| `@graph[].startDate` | 100 % | 2019-07-17T15:00:00+00:00 |
| `@graph[].url` | 100 % | https://www.monacolegendauctions.com/auction |
| `@graph[].eventAttendanceMode` | 95 % | https://schema.org/MixedEventAttendanceMode |
| `@graph[].eventStatus` | 95 % | https://schema.org/EventPast |
| `@graph[].image` | 95 % | https://www.monacolegendauctions.com/storage/media/auctions/… |
| `@graph[].isAccessibleForFree` | 95 % | True |
| `@graph[].itemListElement[].image` | 95 % | https://www.monacolegendauctions.com/storage/media/auctions/… |
| `@graph[].itemListElement[].offers.@type` | 95 % | Offer |
| `@graph[].itemListElement[].offers.price` | 95 % | 2340 |
| `@graph[].itemListElement[].offers.priceCurrency` | 95 % | EUR |
| `@graph[].itemListElement[].url` | 95 % | https://www.monacolegendauctions.com/auction/the-goldberger-… |
| `@graph[].numberOfItems` | 95 % | 48 |
| `@graph[].offers.@type` | 95 % | AggregateOffer |
| `@graph[].offers.availability` | 95 % | https://schema.org/Discontinued |
| `@graph[].offers.highPrice` | 95 % | 65000 |
| `@graph[].offers.lowPrice` | 95 % | 1300 |
| `@graph[].offers.offerCount` | 95 % | 48 |
| `@graph[].offers.priceCurrency` | 95 % | EUR |
| `@graph[].offers.url` | 95 % | https://www.monacolegendauctions.com/auction/the-goldberger-… |
| `@graph[].offers.validFrom` | 95 % | 2026-07-25T14:30:00+02:00 |
| `@graph[].offers.validThrough` | 95 % | 2026-07-25T16:24:00+02:00 |
| `@graph[].superEvent.@type` | 95 % | EventSeries |
| `@graph[].superEvent.name` | 95 % | Exclusive Timepieces |
| `@graph[].superEvent.url` | 95 % | https://www.monacolegendauctions.com/auction |
| `@graph[].location[].@type` | 90 % | Place |
| `@graph[].location[].address.@type` | 90 % | PostalAddress |
| `@graph[].location[].address.addressCountry` | 90 % | Monaco |

</details>

<details><summary><b>monacolegend</b> — famille <code>2 cles</code>, 5 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `@type` | 100 % | BreadcrumbList |
| `itemListElement[].@type` | 100 % | ListItem |
| `itemListElement[].item` | 100 % | https://www.monacolegendauctions.com/auction |
| `itemListElement[].name` | 100 % | Auctions |
| `itemListElement[].position` | 100 % | 1 |

</details>

<details><summary><b>monacolegend</b> — famille <code>name</code>, 10 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `@type` | 100 % | ItemList |
| `itemListElement[].@type` | 100 % | Product |
| `itemListElement[].image` | 100 % | https://www.monacolegendauctions.com/storage/media/auctions/… |
| `itemListElement[].name` | 100 % | A sporty and massive, Seamaster, automatic wristwatch in sta… |
| `itemListElement[].offers.@type` | 100 % | Offer |
| `itemListElement[].offers.price` | 100 % | 2340 |
| `itemListElement[].offers.priceCurrency` | 100 % | EUR |
| `itemListElement[].url` | 100 % | https://www.monacolegendauctions.com/auction/the-goldberger-… |
| `name` | 100 % | The Goldberger Omega Time-Only Collection Lots |
| `numberOfItems` | 100 % | 48 |

</details>

<details><summary><b>montredo</b> — famille <code>id, title</code>, 36 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `body_html` | 100 % | <p>TAG HEUER Sel Chronometer 200M Automatic Mens WG5112</p> |
| `created_at` | 100 % | 2026-07-22T17:28:08+02:00 |
| `handle` | 100 % | tag-heuer-sel-automatic-silver-38-58375 |
| `id` | 100 % | 16349871833437 |
| `images[].created_at` | 100 % | 2026-07-22T17:28:19+02:00 |
| `images[].height` | 100 % | 2000 |
| `images[].id` | 100 % | 85016503648605 |
| `images[].position` | 100 % | 3 |
| `images[].product_id` | 100 % | 16349871833437 |
| `images[].src` | 100 % | https://cdn.shopify.com/s/files/1/1020/5534/6525/files/2000_… |
| `images[].updated_at` | 100 % | 2026-07-22T17:28:22+02:00 |
| `images[].width` | 100 % | 2000 |
| `options[].name` | 100 % | Title |
| `options[].position` | 100 % | 1 |
| `product_type` | 100 % | Watch |
| `published_at` | 100 % | 2026-08-24T17:30:28+02:00 |
| `title` | 100 % | TAG HEUER Sel Chronometer 200M Automatic Mens WG5112 |
| `updated_at` | 100 % | 2026-08-25T12:31:49+02:00 |
| `variants[].available` | 100 % | True |
| `variants[].created_at` | 100 % | 2026-07-22T17:28:08+02:00 |
| `variants[].grams` | 100 % | 0 |
| `variants[].id` | 100 % | 65338675200349 |
| `variants[].option1` | 100 % | Default Title |
| `variants[].position` | 100 % | 1 |
| `variants[].price` | 100 % | 749.00 |
| `variants[].product_id` | 100 % | 16349871833437 |
| `variants[].requires_shipping` | 100 % | True |
| `variants[].sku` | 100 % | 58375 |
| `variants[].taxable` | 100 % | True |
| `variants[].title` | 100 % | Default Title |
| `variants[].updated_at` | 100 % | 2026-08-25T12:31:49+02:00 |
| `vendor` | 100 % | TAG Heuer |
| `variants[].compare_at_price` | 0 % | 4830.00 |
| `variants[].featured_image` | 0 % | — |
| `variants[].option2` | 0 % | — |
| `variants[].option3` | 0 % | — |

</details>

<details><summary><b>sworders</b> — famille <code>8 cles</code>, 8 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `block` | 100 % | Select file Change Remove |
| `col-sm-4` | 100 % | LOCATIONS & CONTACT Stansted Auction Rooms T 01279 817778 | … |
| `fileinput` | 100 % | Select file Change Remove |
| `fileinput-exists` | 100 % | Change |
| `fileinput-new` | 100 % | Select file |
| `href` | 100 % | /contact-stansted |
| `input-group-addon` | 100 % | Select file Change |
| `new-file-upload` | 100 % | Select file Change Remove |

</details>

<details><summary><b>sworders</b> — famille <code>auction-grid-lot, auction-lot, auction-lot-text</code>, 29 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `active` | 100 % | Past lots (324) |
| `auction` | 100 % | Books & Maps (1) |
| `auction-grid-lot` | 100 % | SOLD Lot 599 A gentlemen's stainless steel Rolex Oyster mech… |
| `auction-lot` | 100 % | SOLD Lot 599 A gentlemen's stainless steel Rolex Oyster mech… |
| `auction-lot-text` | 100 % | Lot 599 A gentlemen's stainless steel Rolex Oyster mechanica… |
| `auction-lot-title` | 100 % | Lot 599 A gentlemen's stainless steel Rolex Oyster mechanica… |
| `auction-tab-sold` | 100 % | Past lots (324) |
| `block` | 100 % | Refine Your Results |
| `btn` | 100 % | Refine your results |
| `cat-chk` | 100 % | Books & Maps (1) |
| `contactUsForm` | 100 % | Subscribe To Receive Exclusive Content About Our Auctions, E… |
| `corner-flash` | 100 % | SOLD |
| `data-id` | 100 % | 3 |
| `fileinput` | 100 % | Select file Change Remove |
| `fileinput-exists` | 100 % | Change |
| `fileinput-new` | 100 % | Select file |
| `form-control` | 100 % | All words any order Any words any order Exact words exact or… |
| `form-group` | 100 % | All words any order Any words any order Exact words exact or… |
| `href` | 100 % | # |
| `input-group-addon` | 100 % | Select file Change |
| `lot-title` | 100 % | Lot 599 A gentlemen's stainless steel Rolex Oyster mechanica… |
| `nav` | 100 % | Past lots (324) |
| `new-file-upload` | 100 % | Select file Change Remove |
| `pagination` | 100 % | Page 1 (2 - 321) 2 (333 - 442) 3 (444 - 614) 4 (615 - 1544) … |
| `pull-left` | 100 % | Page |
| `pull-right` | 100 % | Sort by: |
| `req-tag` | 100 % | ▲ |
| `search-control-toggle` | 100 % | Refine your results |
| `sort-options-list` | 100 % | Lot number Estimate/Price - Low to High Estimate/Price - Hig… |

</details>

<details><summary><b>sworders</b> — famille <code>auction-grid-lot, auction-lot, auction-lot-text</code>, 28 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `active` | 100 % | Past lots (324) |
| `auction` | 100 % | Books & Maps (1) |
| `auction-grid-lot` | 100 % | SOLD Lot 356 A gentlemen's bi-metal Rolex Datejust automatic… |
| `auction-lot` | 100 % | SOLD Lot 356 A gentlemen's bi-metal Rolex Datejust automatic… |
| `auction-lot-text` | 100 % | Lot 356 A gentlemen's bi-metal Rolex Datejust automatic brac… |
| `auction-lot-title` | 100 % | Lot 356 A gentlemen's bi-metal Rolex Datejust automatic brac… |
| `auction-tab-sold` | 100 % | Past lots (324) |
| `block` | 100 % | Refine Your Results |
| `btn` | 100 % | Refine your results |
| `cat-chk` | 100 % | Books & Maps (1) |
| `contactUsForm` | 100 % | Subscribe To Receive Exclusive Content About Our Auctions, E… |
| `corner-flash` | 100 % | SOLD |
| `data-id` | 100 % | 3 |
| `fileinput` | 100 % | Select file Change Remove |
| `fileinput-exists` | 100 % | Change |
| `fileinput-new` | 100 % | Select file |
| `form-control` | 100 % | All words any order Any words any order Exact words exact or… |
| `form-group` | 100 % | All words any order Any words any order Exact words exact or… |
| `href` | 100 % | # |
| `input-group-addon` | 100 % | Select file Change |
| `lot-title` | 100 % | Lot 356 A gentlemen's bi-metal Rolex Datejust automatic brac… |
| `nav` | 100 % | Past lots (324) |
| `new-file-upload` | 100 % | Select file Change Remove |
| `pagination` | 100 % | Page 1 (2 - 321) 2 (333 - 442) 3 (444 - 614) 4 (615 - 1544) … |
| `pull-left` | 100 % | Page |
| `pull-right` | 100 % | Sort by: |
| `search-control-toggle` | 100 % | Refine your results |
| `sort-options-list` | 100 % | Lot number Estimate/Price - Low to High Estimate/Price - Hig… |

</details>

<details><summary><b>topper</b> — famille <code>id, title</code>, 36 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `body_html` | 100 % | <h2>The dual expression of time and date</h2>
<p>The Tangent… |
| `created_at` | 100 % | 2026-08-28T03:29:07-07:00 |
| `handle` | 100 % | nomos-glashutte-136 |
| `id` | 100 % | 15257130926452 |
| `images[].created_at` | 100 % | 2026-08-28T03:38:25-07:00 |
| `images[].height` | 100 % | 1201 |
| `images[].id` | 100 % | 57846627402100 |
| `images[].position` | 100 % | 3 |
| `images[].product_id` | 100 % | 15257130926452 |
| `images[].src` | 100 % | https://cdn.shopify.com/s/files/1/2930/0774/files/tangente-2… |
| `images[].updated_at` | 100 % | 2026-08-28T03:38:26-07:00 |
| `images[].width` | 100 % | 1800 |
| `options[].name` | 100 % | Title |
| `options[].position` | 100 % | 1 |
| `product_type` | 100 % | Watch |
| `published_at` | 100 % | 2026-08-28T03:41:33-07:00 |
| `title` | 100 % | Nomos Glashütte Tangente 2Date Blue 136 |
| `updated_at` | 100 % | 2026-08-28T06:37:47-07:00 |
| `variants[].available` | 100 % | True |
| `variants[].created_at` | 100 % | 2026-08-28T03:29:07-07:00 |
| `variants[].grams` | 100 % | 1361 |
| `variants[].id` | 100 % | 55248400548212 |
| `variants[].option1` | 100 % | Default Title |
| `variants[].position` | 100 % | 1 |
| `variants[].price` | 100 % | 3470.00 |
| `variants[].product_id` | 100 % | 15257130926452 |
| `variants[].requires_shipping` | 100 % | True |
| `variants[].taxable` | 100 % | True |
| `variants[].title` | 100 % | Default Title |
| `variants[].updated_at` | 100 % | 2026-08-28T06:37:47-07:00 |
| `vendor` | 100 % | Nomos Glashütte |
| `variants[].sku` | 82 % | 136 |
| `variants[].option2` | 18 % | Satin |
| `variants[].compare_at_price` | 10 % | 750.00 |
| `variants[].option3` | 2 % | 14K |
| `variants[].featured_image` | 0 % | — |

</details>

<details><summary><b>wannabuyawatch</b> — famille <code>id, name, price_html</code>, 77 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `_links.collection[].href` | 100 % | https://wannabuyawatch.com/wp-json/wc/store/v1/products |
| `_links.related[].embeddable` | 100 % | True |
| `_links.related[].href` | 100 % | https://wannabuyawatch.com/wp-json/wc/store/v1/products?rela… |
| `_links.self[].href` | 100 % | https://wannabuyawatch.com/wp-json/wc/store/v1/products/1455… |
| `add_to_cart.description` | 100 % | Add to cart: &ldquo;IWC Schauffhausen Automatic 18K YG R814A… |
| `add_to_cart.maximum` | 100 % | 1 |
| `add_to_cart.minimum` | 100 % | 1 |
| `add_to_cart.multiple_of` | 100 % | 1 |
| `add_to_cart.single_text` | 100 % | Add to cart |
| `add_to_cart.text` | 100 % | Add to cart |
| `add_to_cart.url` | 100 % | /wp-json/wc/store/v1/products?per_page=100&#038;page=1&#038;… |
| `average_rating` | 100 % | 0 |
| `categories[].id` | 100 % | 10110 |
| `categories[].link` | 100 % | https://wannabuyawatch.com/product-category/vintage-and-pre-… |
| `categories[].name` | 100 % | Vintage IWC Watches |
| `categories[].slug` | 100 % | vintage-and-pre-owned-iwc-watches |
| `has_options` | 100 % | False |
| `id` | 100 % | 145573 |
| `is_in_stock` | 100 % | True |
| `is_on_backorder` | 100 % | False |
| `is_password_protected` | 100 % | False |
| `is_purchasable` | 100 % | True |
| `name` | 100 % | IWC Schauffhausen Automatic 18K YG R814A circa 1970 |
| `on_sale` | 100 % | False |
| `parent` | 100 % | 0 |
| `permalink` | 100 % | https://wannabuyawatch.com/product/iwc-schauffhausen-automat… |
| `price_html` | 100 % | <span class="woocommerce-Price-amount amount"><bdi><span cla… |
| `prices.currency_code` | 100 % | USD |
| `prices.currency_decimal_separator` | 100 % | . |
| `prices.currency_minor_unit` | 100 % | 2 |
| `prices.currency_prefix` | 100 % | $ |
| `prices.currency_symbol` | 100 % | $ |
| `prices.currency_thousand_separator` | 100 % | , |
| `prices.price` | 100 % | 595000 |
| `prices.regular_price` | 100 % | 595000 |
| `prices.sale_price` | 100 % | 595000 |
| `review_count` | 100 % | 0 |
| `short_description` | 100 % | <p>An especially fine condition vintage IWC Schauffhausen 18… |
| `sku` | 100 % | 72215 |
| `slug` | 100 % | iwc-schauffhausen-automatic-18k-yg-r814a-circa-1970 |
| `sold_individually` | 100 % | True |
| `stock_availability.class` | 100 % | in-stock |
| `type` | 100 % | simple |
| `images[].id` | 98 % | 145716 |
| `images[].name` | 98 % | 72215back |

</details>

<details><summary><b>wannabuyawatch</b> — famille <code>id, name</code>, 3 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `id` | 100 % | 11158 |
| `name` | 100 % | A Lange &amp; Sohns |
| `slug` | 100 % | a-lange-sohns |

</details>

<details><summary><b>wannabuyawatch</b> — famille <code>id, name</code>, 7 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `has_variations` | 100 % | False |
| `id` | 100 % | 22 |
| `name` | 100 % | Maker/Brand |
| `taxonomy` | 100 % | pa_maker-brand |
| `terms[].id` | 100 % | 570 |
| `terms[].name` | 100 % | Rolex |
| `terms[].slug` | 100 % | rolex |

</details>

<details><summary><b>watchesofdistinction</b> — famille <code>id, name, price_html</code>, 71 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `_links.collection[].href` | 100 % | https://watchesofdistinction.com/wp-json/wc/store/v1/product… |
| `_links.related[].embeddable` | 100 % | True |
| `_links.related[].href` | 100 % | https://watchesofdistinction.com/wp-json/wc/store/v1/product… |
| `_links.self[].href` | 100 % | https://watchesofdistinction.com/wp-json/wc/store/v1/product… |
| `add_to_cart.description` | 100 % | Add to basket: &ldquo;Rolex EXPLORER II REF 216570 (2020) FU… |
| `add_to_cart.maximum` | 100 % | 1 |
| `add_to_cart.minimum` | 100 % | 1 |
| `add_to_cart.multiple_of` | 100 % | 1 |
| `add_to_cart.single_text` | 100 % | Add to basket |
| `add_to_cart.text` | 100 % | Add to basket |
| `add_to_cart.url` | 100 % | /wp-json/wc/store/v1/products?per_page=100&#038;page=1&#038;… |
| `attributes[].has_variations` | 100 % | False |
| `attributes[].id` | 100 % | 2 |
| `attributes[].name` | 100 % | Year |
| `attributes[].taxonomy` | 100 % | pa_manufactured-year |
| `attributes[].terms[].id` | 100 % | 1111 |
| `attributes[].terms[].name` | 100 % | 2010's |
| `attributes[].terms[].slug` | 100 % | 2010s |
| `average_rating` | 100 % | 0 |
| `categories[].id` | 100 % | 1304 |
| `categories[].link` | 100 % | https://watchesofdistinction.com/product-category/new-arriva… |
| `categories[].name` | 100 % | New Arrivals |
| `categories[].slug` | 100 % | new-arrivals |
| `has_options` | 100 % | False |
| `id` | 100 % | 44538 |
| `images[].id` | 100 % | 44541 |
| `images[].name` | 100 % | L198sde |
| `images[].sizes` | 100 % | (max-width: 2362px) 100vw, 2362px |
| `images[].src` | 100 % | https://watchesofdistinction.com/wp-content/uploads/L198sde.… |
| `images[].srcset` | 100 % | https://watchesofdistinction.com/wp-content/uploads/L198sde.… |
| `images[].thumbnail` | 100 % | https://watchesofdistinction.com/wp-content/uploads/L198sde-… |
| `images[].thumbnail_sizes` | 100 % | (max-width: 700px) 100vw, 700px |
| `images[].thumbnail_srcset` | 100 % | https://watchesofdistinction.com/wp-content/uploads/L198sde-… |
| `is_in_stock` | 100 % | True |
| `is_on_backorder` | 100 % | False |
| `is_password_protected` | 100 % | False |
| `is_purchasable` | 100 % | True |
| `name` | 100 % | Rolex EXPLORER II REF 216570 (2020) FULL SET |
| `on_sale` | 100 % | False |
| `parent` | 100 % | 0 |
| `permalink` | 100 % | https://watchesofdistinction.com/product/rolex-explorer-ii-r… |
| `prices.currency_code` | 100 % | GBP |
| `prices.currency_decimal_separator` | 100 % | . |
| `prices.currency_minor_unit` | 100 % | 2 |
| `prices.currency_prefix` | 100 % | £ |

</details>

<details><summary><b>watchesofswitzerland</b> — famille <code>1 cles</code>, 1 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `url` | 100 % | https://content.thewosgroup.com/productimage/17631061/176310… |

</details>

<details><summary><b>watchesofswitzerland</b> — famille <code>name</code>, 3 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `code` | 100 % | Brands |
| `name` | 100 % | Brands |
| `url` | 100 % | /c/Brands |

</details>

<details><summary><b>watchrecon</b> — famille <code>name</code>, 4 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `active` | 100 % | Rolex |
| `btn` | 100 % | Rolex |
| `href` | 100 % | . |
| `name` | 100 % | Rolex |

</details>

<details><summary><b>watchrecon</b> — famille <code>name</code>, 6 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `active` | 100 % | 14 days |
| `btn` | 100 % | 14 days |
| `btn-group` | 100 % | 14 days 1 day 2 days 3 days 4 days 5 days 6 days 7 days 14 d… |
| `dropdown-menu` | 100 % | 1 day 2 days 3 days 4 days 5 days 6 days 7 days 14 days 21 d… |
| `href` | 100 % | .?brand=rolex&last_days=1 |
| `name` | 100 % | 14 days |

</details>

<details><summary><b>watchrecon</b> — famille <code>name</code>, 5 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `active` | 100 % | 14 days |
| `btn` | 100 % | 14 days |
| `dropdown-menu` | 100 % | 1 day 2 days 3 days 4 days 5 days 6 days 7 days 14 days 21 d… |
| `href` | 100 % | .?brand=rolex&last_days=1 |
| `name` | 100 % | 14 days |

</details>

<details><summary><b>watchtrader</b> — famille <code>id, name, price_html</code>, 58 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `add_to_cart.description` | 100 % | Add to bag: &ldquo;Chopard Mille Miglia GMT Speed Black 2 Du… |
| `add_to_cart.maximum` | 100 % | 1 |
| `add_to_cart.minimum` | 100 % | 1 |
| `add_to_cart.multiple_of` | 100 % | 1 |
| `add_to_cart.single_text` | 100 % | Add to Bag |
| `add_to_cart.text` | 100 % | Add to bag |
| `add_to_cart.url` | 100 % | /wp-json/wc/store/products?per_page=100&#038;page=1&#038;add… |
| `attributes[].has_variations` | 100 % | False |
| `attributes[].id` | 100 % | 14 |
| `attributes[].name` | 100 % | Bezel |
| `attributes[].taxonomy` | 100 % | pa_bezel |
| `attributes[].terms[].id` | 100 % | 261 |
| `attributes[].terms[].name` | 100 % | Ceramic |
| `attributes[].terms[].slug` | 100 % | ceramic |
| `average_rating` | 100 % | 0 |
| `categories[].id` | 100 % | 88 |
| `categories[].link` | 100 % | https://www.watchtrader.co.uk/product-category/chopard/ |
| `categories[].name` | 100 % | Chopard |
| `categories[].slug` | 100 % | chopard |
| `description` | 100 % | <p>: Chopard <br />: 8992 <br />: Mille Miglia GMT Speed Bla… |
| `has_options` | 100 % | False |
| `id` | 100 % | 132674 |
| `images[].id` | 100 % | 132664 |
| `images[].name` | 100 % | 6c7f1c16-f68b-4d81-ac13-0f4c0f0a0e9f-1.jpg |
| `images[].sizes` | 100 % | (max-width: 1600px) 100vw, 1600px |
| `images[].src` | 100 % | https://www.watchtrader.co.uk/wp-content/uploads/2026/08/6c7… |
| `images[].srcset` | 100 % | https://www.watchtrader.co.uk/wp-content/uploads/2026/08/6c7… |
| `images[].thumbnail` | 100 % | https://www.watchtrader.co.uk/wp-content/uploads/2026/08/6c7… |
| `is_in_stock` | 100 % | True |
| `is_on_backorder` | 100 % | False |
| `is_purchasable` | 100 % | True |
| `low_stock_remaining` | 100 % | 1 |
| `name` | 100 % | Chopard Mille Miglia GMT Speed Black 2 Dubai Edition 8992 20… |
| `on_sale` | 100 % | False |
| `parent` | 100 % | 0 |
| `permalink` | 100 % | https://www.watchtrader.co.uk/product/chopard-mille-miglia-g… |
| `price_html` | 100 % | <span class="woocommerce-Price-amount amount"><span class="w… |
| `prices.currency_code` | 100 % | GBP |
| `prices.currency_decimal_separator` | 100 % | . |
| `prices.currency_minor_unit` | 100 % | 0 |
| `prices.currency_prefix` | 100 % | £ |
| `prices.currency_symbol` | 100 % | £ |
| `prices.currency_thousand_separator` | 100 % | , |
| `prices.price` | 100 % | 3750 |
| `prices.regular_price` | 100 % | 3750 |

</details>

<details><summary><b>watchtrader</b> — famille <code>id, name</code>, 7 champs</summary>

| Champ | Rempli | Exemple |
|---|---|---|
| `has_variations` | 100 % | False |
| `id` | 100 % | 1 |
| `name` | 100 % | Brand |
| `taxonomy` | 100 % | pa_brand |
| `terms[].id` | 100 % | 185 |
| `terms[].name` | 100 % | Hublot |
| `terms[].slug` | 100 % | hublot |

</details>

