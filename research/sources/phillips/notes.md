# Phillips (Bacs & Russo)

Fiche de reconnaissance remplie le **21/09/2026**. Adaptateur :
`moteur/sources/phillips.py`. Échantillons : `samples/`.

## Identité
- **Source :** Phillips · **URL :** <https://www.phillips.com/>
- **Type :** maison de ventes (`auction`) · `id` = `phillips`
- **Nature du prix :** `realised`, **frais acheteur INCLUS** (mesuré, cf. plus bas)
- **Statut :** data récupérée · adaptateur écrit et vérifié sur 8 ventes
- **Une seule plateforme pour trois places.** Genève (41 ventes, CHF),
  Hong Kong (44, HKD), New York (20, USD) sont servies par `phillips.com` avec
  le même gabarit de page et le même payload. Il n'y a **pas** de site Hong Kong
  séparé et **aucun paramètre de lieu ou de devise n'est nécessaire** :
  `auctionCurrency` et `auctionTimezone` sont publiés vente par vente. Un seul
  adaptateur couvre les trois.

## Accès
Deux niveaux, aucune pagination, aucun navigateur sans tête, aucun compte.

1. `GET /calendar/results` → le HTML porte le **payload React Router**
   (`window.__reactRouterContext.streamController.enqueue("…")`, encodage
   turbo-stream : un tableau plat où tout est un indice, les objets s'écrivant
   `{"_<indice de la clé>": <indice de la valeur>}`). Sous la clé
   `pastAuctions` : **896 ventes passées, tous départements confondus**, avec
   code, nom, ville, fuseau et date. On garde celles dont `departments` nomme
   `Watches` → **105 ventes, 2015-05-09 → 2026-09-04**.
2. `GET /auction/{CODE}/overview` → même genre de payload. L'objet `auction`
   porte `auctionCurrency`, `auctionTimezone`, `totalLotCount` et **`lots` :
   TOUS les lots de la vente** (60 à 294 dans l'échantillon, `len(lots) ==
   totalLotCount` sur les 8 ventes testées), chacun avec son prix réalisé.

**Coût total du fonds : 1 + 105 = 106 requêtes.** Aucune page de lot n'est
nécessaire pour le socle prix/date/référence.

- Pas de clé, pas de compte, pas de rate-limit rencontré (8 pages à 1,5 s de
  pause, aucun 429, aucun 403).
- **L'UA n'est pas un sujet ici** : `utils.HEADERS` (ClaudeBot) passe en 200 sur
  toutes les pages testées. Rien à mesurer côté `python-requests`.
- Le site est une SPA (Vite/React Router) mais **tout est rendu côté serveur**
  dans le payload : pas de Playwright.

## Légal
`robots.txt` lu le **21/09/2026** (`samples/robots.txt`), 155 octets, un seul
groupe `User-agent: *` :

```
Disallow: /bin/   /message/optin/   /Search   /phillips/otis   /*/filter/   /search   /SEARCH
```

Aucune règle nominative ClaudeBot. `/calendar/*`, `/auction/*/overview` et
`/detail/*` sont **autorisés** ; `/search` et `/*/filter/` sont interdits et
**ne sont pas utilisés** — la navigation passe par le calendrier, pas par l'UI
de recherche. Données publiques (résultats d'enchères publiés). Aucun mur,
aucune protection contournée.

## Format de la data

Champs lus dans `auction.lots[]`, et remplissage mesuré sur **1 199 lots de
8 ventes** (`samples/records_echantillon.json`) :

| champ du projet | source | remplissage |
|---|---|---|
| `price_amount` | `soldPrice` | 100 % des lots retenus |
| `price_currency` | `auctionCurrency.currencyCode` (CHF/HKD/USD) | 100 % |
| `price_date` | `sessionStartDateTime`, sinon `auctionStartDateTime`, **converti dans le fuseau de la vente** | **100 %** |
| `price_nature` / `…_provenance` | `lotStatus` → `champ_dedie` | 100 % |
| `price_includes_premium` | mesuré : `True` | 98 % (`None` sur les invendus) |
| `reference` / `…_provenance` | **`referenceNo`, champ dédié** → `champ_dedie` | **86 %** (85 % `champ_dedie`, 1 % extrait) |
| `brand` | `makerName` | 100 % |
| `model` | `modelName` | 84 % |
| `title` | `makerName` + `modelName` + `description` | 100 % |
| `estimate_low` / `high` | `estimate`, **dans la devise de la vente** | 100 % |
| `source_category` | `lotType` = `WatchAuctionLot` | 100 % |
| `external_id` / `source_url` | `objectNumber` / `detailLink` | 100 % |
| `year`, `case_material`, `case_size_mm`, `movement` | page du lot uniquement (`circa`, `material`, `dimensions`, `calibre`) | 0 % sans enrichissement |

Historique : **onze ans et quatre mois**, 5 à 14 ventes par an (2015 : 5 ;
2023 : 14). Format brut : HTML porteur d'un payload JSON.

## Les six pièges trouvés

### 1. Le JSON-LD d'une page de lot publie l'ESTIMATION BASSE, pas le prix réalisé
Le piège le plus coûteux, et c'est exactement la méthode que recommandait
l'audit de juillet 2026. Lot **144448** (Rolex Daytona 116520, Genève 2020,
`samples/detail_rolex_144448.html`) :

```
JSON-LD Product : offers.price 15000, priceCurrency CHF, availability SoldOut
payload         : estimate.lowEstimate 15000 · soldPrice 23940
```

`offers.price` **est** l'estimation basse. Avec `availability: SoldOut` à côté,
rien ne signale l'erreur : la montre serait entrée en base sous-évaluée de 37 %,
et la source entière avec elle. **On ne lit jamais le JSON-LD de Phillips.**

### 2. Le prix est frais acheteur inclus — mesuré, pas deviné
Deux preuves indépendantes sur 8 ventes, 3 places, 1 175 lots vendus
(`samples/mesure_frais_acheteur.json`) :

*Égalité directe*, là où les deux prix sont publiés (ventes 2026) :
`soldPrice == hammerPricePlusBP` sur **449/449** lots, et
`hammerPricePlusBP / hammerPrice == 1,27` sur 443 — les 27 % des conditions de
vente.

*Divisibilité*, là où seul `soldPrice` existe : diviser par le taux de frais
publié **à la date de la vente** rend un marteau propre (multiple d'incrément
d'enchère) sur **1 145 / 1 175 = 97,4 %** des lots.

| vente | date | taux | marteau propre |
|---|---|---|---|
| CH080115 Genève | 2015-05-09 | /1,25 | 49/60 |
| HK080217 Hong Kong | 2017-11-28 | /1,25 | **150/150** |
| NY080119 New York | 2019-12-10 | /1,25 | 69/73 |
| CH080320 Genève | 2020-11-08 | /1,26 | 92/94 |
| NY080322 New York | 2022-12-10 | /1,26 | 167/170 |
| NY080424 New York | 2024-12-07 | /1,27 | 175/179 |
| NY080126 New York | 2026-06-13 | /1,27 | 152/156 |
| HK080226 Hong Kong | 2026-05-31 | /1,27 | 291/293 |

Sans diviser, `soldPrice` n'est « propre » que dans 29,5 % des cas, et un
mauvais taux ne dépasse jamais 3 %. Les frais Phillips sont passés de **25 %
(2015-2019) à 26 % (2020-2022) puis 27 % (depuis 2024)**, et `soldPrice` les
porte à chaque époque. → `price_includes_premium = True`, convention de
Christie's et Monaco Legend, **pas** celle d'Artcurial.

### 3. Le marteau nu n'existe que sur les ventes de 2026
`hammerPrice` et `hammerPricePlusBP` sont présents sur HK080226 et NY080126
(2026) et **absents** de 2015, 2017, 2019, 2020, 2022 et 2024, où seul
`soldPrice` subsiste. Le cahier demande de charger le marteau quand la source
publie les deux — ici elle ne les publie que sur les six derniers mois d'un
historique de onze ans. Charger le marteau là où il existe et le prix frais
inclus ailleurs créerait une **marche de 27 % au milieu de la courbe**, à
l'endroit précis du changement de plateforme : exactement l'erreur que le champ
`price_includes_premium` existe pour empêcher.

**Décision :** on charge `soldPrice` partout, série homogène 2015 → 2026,
`price_includes_premium = True`. Le brut n'étant jamais jeté, `hammerPrice`
reste disponible dans les payloads conservés pour qui voudra bâtir la série
marteau le jour où Phillips l'aura rétropublié.

### 4. `?Departments=watches` ne filtre rien côté serveur
La page rend les **896** ventes de tous les départements (Contemporary 420,
Online 192, Design 161, Editions 119, **Watches 105**, Photographs 89,
Jewelry 87) ; le tri se fait dans le navigateur. Les « ~900 codes de vente »
que l'audit de juillet 2026 a comptés sur cette page sont donc **900 ventes
toutes catégories, pas 900 ventes de montres** — un facteur **9** de
surestimation. Le vrai compte est 105, et le tri par département se fait chez
nous.

### 5. Les dates sont en UTC, les ventes ont lieu dans leur ville
`CH080115` porte `2015-05-08T22:00:00Z` avec `Europe/Zurich` : la vente a eu
lieu le **9 mai**. `HK080217` porte `2017-11-27T16:00:00Z` avec
`Asia/Hong_Kong` : le **28 novembre**. Un `[:10]` naïf décale d'un jour toutes
les ventes du soir de Genève et toutes celles de Hong Kong. L'adaptateur
convertit avec `auctionTimezone`.

À partir de 2022, `sessionStartDateTime` date chaque **session** : une vente sur
deux jours donne bien deux dates (NY080126 → 79 lots le 13 juin, 77 le 14).
Avant 2022 le champ est absent, on retombe sur la date de la vente.

### 6. Trois devises, et l'estimation en publie cinq
`estimate.otherEstimates` donne la même fourchette convertie en GBP, CHF, EUR,
USD et HKD. Prendre la première venue mélangerait des HKD et des CHF dans la
même colonne. L'adaptateur ne retient que l'entrée dont `currencyCode` est
celui de la vente.

## Autres mesures

- **Statuts de lot rencontrés :** `Sold`, `BoughtIn`, `ReturnToOwner`. Les deux
  derniers sont des **invendus** : ils entrent en nature `estimate` avec
  `listing_status=unsold` (24 sur 1 199 dans l'échantillon, soit un taux de
  vente de 98 %). Un lot `Withdrawn` ou `isNoLot` n'a jamais été soumis aux
  enchères : il est écarté.
- **Les 14 % de lots sans référence ne sont pas un défaut d'extraction.** Ce
  sont des pièces qui n'ont pas de référence constructeur : F.P. Journe,
  Voutilainen, Philippe Dufour, De Bethune, pièces uniques, pendulettes. Le
  champ `referenceNo` est vide **à la source**. Rien à gratter dans les titres.
- **Le filtre du projet rejette 7,8 %** de l'échantillon (93/1 199) — et ce sont
  des montres. R3 (47) sur des marques indépendantes absentes de la liste
  (Romain Gauthier, Ludovic Ballouard, Urban Jürgensen, Lang & Heyne, Konstantin
  Chaykin, Philippe Dufour, Moritz Grossmann), R1 (33) sur des Day-Date
  « diamond-set » prises pour de la joaillerie, R5 (11). C'est une affaire de
  filtre, pas d'adaptateur : rien n'a été touché dans `filtres/`.
- **Enrichissement facultatif.** `collect(cap, enrichir=N)` va chercher la page
  des N premiers lots, qui publie `circa` (l'année), `material`, `calibre` et
  `dimensions` en champs propres — vérifié en vrai sur 2 lots : `year=2025`,
  `case_material='18k white gold'`, `case_size_mm=29.0`,
  `movement='Manual, cal. 215, 23 jewels'`. Coût : **une requête par lot**, soit
  ~15 750 pour tout le fonds. Désactivé par défaut. Réserve : `dimensions` peut
  porter deux cotes sur un boîtier asymétrique, et `schema` retient la
  première.
- **Rejouable sans réseau :** `lots_du_brut()` + `fiche()` relisent le brut
  conservé. Les 1 199 lignes de l'échantillon ont été produites ainsi, **zéro
  requête**, à partir des 8 pages de `samples/`.

## Volume atteignable

| | |
|---|---|
| ventes du département Montres | **105** (2015-05-09 → 2026-09-04) |
| lots par vente (8 ventes mesurées) | 60 · 74 · 95 · 156 · 167 · 175 · 179 · 294 — **moyenne 150** |
| **projection du fonds** | **~15 750 lots**, dont ~98 % avec prix réalisé |
| coût en requêtes | **106** pour tout, soit ~150 lots la requête |

L'audit de juillet annonçait « ~900 ventes » et « des dizaines de milliers de
lots » : c'est **105 ventes et de l'ordre de 15 000 lots**. Le compte de ventes
est faux d'un facteur 9 ; le compte de lots est du bon ordre mais par le haut.
Corrigé, Phillips reste la deuxième source la plus profonde du dossier après
Christie's, et la moins chère en requêtes par lot.

## Échantillons (`samples/`)
- `robots.txt` — lu le 21/09/2026
- `calendar_results_watches.html` — la page d'index (715 Ko)
- `calendar_105_ventes_montres.json` — les 105 ventes montres décodées
- `auction_{CH080115,HK080217,NY080119,CH080320,NY080322,NY080424,NY080126,HK080226}_overview.html`
  — 8 ventes, une par époque et une par place
- `auction_CH080115_decode.json`, `auction_NY080126_decode.json` — payloads décodés
- `mesure_frais_acheteur.json` — la mesure des frais, vente par vente
- `detail_rolex_144448.html` + `_lot_decode.json` — la preuve du piège JSON-LD
- `records_echantillon.json` — les 1 199 enregistrements normalisés
