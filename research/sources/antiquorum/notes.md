# Antiquorum

Fiche de reconnaissance remplie le 21/09/2026. Adaptateur : `moteur/sources/antiquorum.py`.

## Identité
- **Source :** Antiquorum Genève SA · **URL vitrine :** <https://www.antiquorum.swiss/>
- **URL du catalogue :** <https://catalog.antiquorum.swiss/> ← **c'est là que vivent les données**
- **Type :** enchères (maison de ventes **exclusivement horlogère**, depuis 1974)
- **Statut :** data récupérée — mécanisme prouvé sur 3 ventes (1989/2001/2015/2026), collecte
  complète non lancée (vague 4)

### Le site a déménagé
L'audit de juillet 2026 donnait `www.antiquorum.swiss/en/auctions/{ID}/price-list`.
**Ce chemin rend 404** : le site vitrine est passé sous WordPress et le catalogue
a été déplacé sur le sous-domaine `catalog.antiquorum.swiss` (application Rails).
Même arborescence, autre hôte. Les deux sitemaps de `www` ne contiennent que des
pages et des articles — **aucun lot**. Le sitemap de `catalog`
(`/sitemap.xml.gz`) est annoncé par robots.txt mais n'a pas été ouvert : on n'en
a pas besoin, l'énumération par année suffit et elle est datée.

`live.antiquorum.swiss` (plateforme AuctionMobility) rend **403 Access Restricted**.
On n'y touche pas.

## Accès
Trois routes HTML servies par le serveur. Aucun JavaScript, aucun compte, aucune clé.

| # | Route | Ce qu'elle rend | Coût |
|---|---|---|---|
| 1 | `GET /auctions?locale=en&year=AAAA` | les ventes de l'année : titre, lieu, **date(s) de vacation**, total, id de price-list, slug de catalogue | 1 req/année, **38 années (1989→2026)** |
| 1′ | `GET /` (la racine du catalogue) | **les 30 ventes les plus récentes** (2022→2026) dans le même format, en **une seule requête** — l'entrée idéale pour une mise à jour quotidienne, qui n'a pas besoin de remonter l'historique | 1 req |
| 2 | `GET /en/auctions/{ID}/price-list` | **TOUS les lots vendus** d'une vente : n° de lot, **marteau**, marteau frais inclus | **1 req/vente** |
| 3 | `GET /en/auctions/{slug}/lots?page=N` | l'identité : titre, description, marque (RDFa), **devise**, estimations, grade, et sur les ventes récentes un bloc de **champs dédiés** (Brand, Model, Reference, Year, Diameter, Caliber) | 1 req/20 lots |

**La collecte est une jointure des routes 2 et 3 sur l'URL du lot.** Ni l'une ni
l'autre ne suffit : la route 2 est la seule à publier le marteau nu, la route 3
la seule à publier la devise et l'identité.

- **robots.txt** (`catalog.antiquorum.swiss`, relu le 21/09/2026, copie dans
  `samples/robots-catalog-2026-09-21.txt`) : une section **`User-agent: ClaudeBot`
  nous nomme explicitement**, avec `Crawl-delay: 5`, `Allow: /en/lots/`,
  `Allow: /assets/`, et trois interdictions — `/en/users/`, et toute URL portant
  `lot_id=`, `from_btn=` ou `fbclid=`. L'adaptateur applique la pause de 5 s et
  n'appelle **jamais** les liens « favori » des fiches, qui portent `lot_id=`.
- UA : `utils.HEADERS` (ClaudeBot) passe partout, 200 sur les 39 requêtes de
  reconnaissance. Aucun 403, aucun 429, aucun mur.
- Pas de rate limit observé. Pas de pagination JS.

## Format de la data

### Ce que la price-list publie (route 2)
```
<h1 class="catalogName">Monaco, June 28, 2026<br>Important Modern & Vintage Timepieces<br>
   Auction Total: (incl. Buyers Premium)  4,141,699</h1>
<div class="header"><div class="lot">lot</div><div class="hammer">hammer</div><div class="hammer">+premium</div></div>
<div class="row"><a class="lotnumber" href="/en/lots/rolex-ref-6264-daytona-paul-newman-lot-388-217">217</a>
  <h3>310,000</h3><span></span><h3>406,720</h3></div>
```
Le piège annoncé par l'audit est **confirmé et mesuré** : la première colonne est
le **MARTEAU**, pas l'estimation. Les en-têtes le disent (`hammer` / `+premium`)
et la vérification numérique le prouve (voir plus bas).

### Ce que le catalogue publie (route 3), par lot
RDFa `schema:Product` + un bloc lisible :
`schema:name` (titre), `schema:description`, `schema:brand`,
`schema:priceCurrency`, `schema:availability` (=`OutOfStock` sur un lot vendu),
`schema:sku` (= id vente + id lot, unique), `schema:mpn`, `Grading System: A/AA/AAA`,
les estimations en 1 à 5 devises, et `Sold: EUR 406,720`.
Sur les ventes récentes s'ajoute un bloc de **champs dédiés** :
`Brand`, `Model`, `Reference`, `Year`, `Diameter`, `Caliber`, `Case No.`,
`Movement No.`, `Bracelet`, `Signature`, `Accessories`, `Limited Edition`.

### Profondeur et volume
- Le sélecteur d'année descend à **1989** → **38 ans d'historique daté**.
- Identifiants de price-list observés : 14–24 (2001), 175–182 (1989), 288–296
  (2015), 386–388 (2026), le plus haut étant 389 (vente à venir).
  **Les identifiants ne sont PAS chronologiques** : 1989 porte les id 175–182 et
  2001 les id 14–24. Itérer les id de 14 à 388 comme le suggérait l'audit
  fonctionne, mais dans un ordre incompréhensible et sans les dates — **il faut
  énumérer par année**, c'est la route 1 qui date les ventes.
- Ventes par année, mesuré : 1989 → 5 (4 avec price-list) · 2001 → 11 (8) ·
  2015 → 9 (9) · 2026 → 5 (3, + 1 à venir). Soit **≈ 7 ventes à price-list par an,
  ≈ 265 ventes sur 38 ans**.
- **Toutes les ventes n'ont pas de résultats publiés** : 1 sur 5 en 1989, 3 sur 11
  en 2001, 0 sur 9 en 2015. Ces ventes ont un catalogue mais aucun prix — ni
  price-list, ni « Sale Totaled », ni `Sold:` sur les lots. L'adaptateur les
  écarte sur ce signal, avant de dépenser la moindre requête de catalogue.
- Lots **vendus** par vente, mesuré : 380 (vente 14) · 317 (23) · 106 (175) ·
  488 (292) · 145 (388). Moyenne ≈ 287.
- **Volume atteignable ≈ 85 000 à 100 000 prix réalisés datés.** L'audit annonçait
  100 000–150 000 lots : l'écart s'explique, il comptait les lots du catalogue,
  invendus compris (217 lots au catalogue pour 145 vendus sur la vente 388).

## Légal
- Données publiques, aucune authentification, aucun contournement.
- robots.txt nous autorise nommément et impose un `Crawl-delay: 5` que l'on
  applique ; ses trois `Disallow` sont respectés.
- Prix d'adjudication publiés par la maison elle-même sur ses pages de résultats.

## Trouvailles / notes de test

### 1. Le marteau, prouvé et non supposé
Sur **109 lots** où les deux routes se recoupent (45 en 2026, 47 en 2001, 17 en
2015) : le `Sold: DEVISE X` du catalogue vaut **exactement**, au franc près, la
seconde colonne de la price-list — jamais la première. Rapport colonne 2 /
colonne 1, médiane sur les 1 119 lots des quatre price-lists échantillonnées :
**1,150 en 1989 · 1,150 en 2001 · 1,250 en 2015 · 1,312 en 2026**.

Conclusion : la colonne 1 est le marteau nu, la colonne 2 et tout le reste du
site (fiche, catalogue, total de vente « incl. Buyers Premium ») sont **frais
inclus**. On charge la colonne 1 → `price_includes_premium = False`, **mesuré**.

### 2. Le taux de frais a changé d'époque — et il est dégressif
1,15 (1989, 2001) → 1,25 (2015) → 1,312 (2026). Et **dégressif** sur les gros
lots : dans la vente de 2001, 540 000 → 597 500, soit **1,104** au lieu de 1,15 ;
la vente 292 de 2015 descend de 1,25 à 1,207 et la 175 de 1989 de 1,15 à 1,133.
**On ne peut donc pas reconstituer un marteau en divisant un prix frais inclus
par un taux** : il faut la price-list. C'est ce qui rend la route 2 obligatoire.

### 3. `schema:price` est l'ESTIMATION BASSE, pas le prix vendu
Le RDFa de chaque lot annonce `schema:price`. Mesuré :
- lot 388-217 : `schema:price` = **300 000**, estimation affichée `EUR 300,000 - 500,000`,
  marteau **310 000**, vendu **406 720**.
- lot 388-7 : `schema:price` = **500**, estimation `EUR 500 - 1,000`, vendu **1 115**.

Le prendre pour un prix réalisé **diviserait la base par trois**. Il n'entre ici
que dans `estimate_low` — et il vaut `0` sur les lots sans estimation publiée,
ce qui n'est pas une estimation basse mais une absence (traité).

### 4. `priceValidUntil` est un bouchon
Il vaut `2026/09/30` sur un lot **vendu en 2001**. Jamais une date de vente.
La date de vente vient de la route 1 (ou de l'en-tête de la price-list).

### 5. La devise n'est nulle part sur la price-list
Elle change avec la ville : **CHF** Genève · **EUR** Monaco et Milan · **HKD**
Hong Kong · **USD** New York · **JPY** Tokyo. Elle n'est **pas devinée** : elle
est lue dans `schema:priceCurrency` de chaque lot du catalogue. Une price-list
lue seule rend des montants **sans devise**, donc inutilisables — et un total de
vente « 176 Million » (Tokyo 1989) passerait pour un record mondial si on le
lisait en francs.

### 6. Les invendus sont absents de la price-list
Vente 388 : 145 lignes pour des lots numérotés jusqu'à 217. **Biais de survie
assumé et signalé** (même situation qu'Artcurial). Le catalogue, lui, porte bien
les invendus — sans prix, donc ils ne produisent aucun enregistrement.

### 7. Une vente peut avoir plusieurs dates
Genève, mai 2026 : « Session 1: Lots 1-285, May 09 · Session 2: Lots 286-445,
May 10 · Session 3: Lots 446-672, May 10 ». La date est donc affectée **par
tranche de numéro de lot**, pas en bloc. Sans cela les 672 lots recevraient tous
la date du premier jour. C'est bien la date de **transaction**, pas de mise en
ligne.

### 8. Les guillemets ne sont pas échappés dans les attributs
Le site écrit `content="ROLEX, ... DAYTONA "PAUL NEWMAN", STAINLESS STEEL "`.
Un motif `content="([^"]*)"` **coupe le titre au premier guillemet interne**. On
termine donc sur `"></div>`, et on préfère le texte du lien `<a>`, lui
correctement échappé.

### 9. Les slugs anciens ne portent aucune identité
`/en/lots/lot-14-2` (2001) contre
`/en/lots/rolex-ref-6264-daytona-paul-newman-lot-388-217` (2026). Sur les ventes
anciennes, la price-list seule ne donne **ni marque ni référence** — le catalogue
est indispensable. Sur les ventes récentes le slug porte marque et référence,
mais il est slugifié (minuscules, points perdus) : la référence lue dans le champ
dédié ou dans le titre est meilleure, on n'utilise pas le slug.

### 10. Le catalogue moderne n'affiche pas sa pagination
`?page=2` fonctionne, mais **aucun lien de page n'est rendu** sur les ventes
récentes, alors qu'un bloc `<div class="pagination">` complet l'est sur les
anciennes. On avance donc jusqu'à la première page vide. 20 lots par page,
partout.

### 11. Deux gardes-fous de budget
- Une vente **à venir** n'a ni price-list ni « Sale Totaled » : son catalogue est
  publié sans aucun prix. Sans garde-fou, la collecte dépensait une dizaine de
  requêtes par vente future pour rien.
- Une vente **conclue mais sans price-list** existe (Hong Kong, 13/03/2026,
  « Only Online Auction » de Milan et Genève) : on se rabat alors sur le
  `Sold:` du catalogue, qui est **frais inclus**, et
  `price_includes_premium = True` le dit. Si la première page de catalogue ne
  porte aucun prix réalisé, la vente est abandonnée.

### 12. Le piège du sous-chaîne sur la matière
`Manufactures of Jewelry, **Silverware** and Gas Fixtures` rangeait une montre
en or 18K sous `case_material = silver`. Corrigé : bornes de mot, et on retient
la **dernière** matière citée — Antiquorum écrit la matière du boîtier en fin de
titre.

## Ce que la source rend, mesuré

Sur 92 enregistrements (40 lots de Monaco 2026 + 47 de New York 2001 + rejeu) :

| Champ | Remplissage |
|---|---|
| `price_amount`, `price_currency`, `price_date` | **100 %** |
| `price_nature` (+ provenance), `price_includes_premium` | **100 %** |
| `brand`, `title`, `external_id` | 100 % |
| `year` · `case_material` · `condition` (grade) | 98 % |
| `estimate_low` / `estimate_high` | 99 % |
| `reference` (+ provenance) | 41 % toutes époques confondues |
| `model` · `movement` (calibre) | 39 % |
| `case_size_mm` | 36 % |
| `dial_color` | 23 % |

## Où commence la profondeur UTILE — mesuré sur 5 ventes témoins

Le taux de référence et le rendement du filtre dépendent **entièrement de
l'époque et du type de vente**. Cinq ventes échantillonnées, 236 lots :

| Vente témoin | Type | Lots | GARDER | Référence |
|---|---|---:|---:|---:|
| Monaco 388, juin 2026 | moderne, champs dédiés | 45 | **98 %** | **76 %** (`champ_dedie`) |
| Hong Kong 292, juin 2015 | moderne | 17 | 71 % | **82 %** (`extrait_titre`) |
| Genève 100, oct. 2005 | **généraliste** bracelets + poche | 78 | **53 %** | 28 % |
| Genève 118, avr. 1995 | **généraliste** bracelets + poche | 39 | **54 %** | 5 % |
| New York 23, nov. 2001 | thématique horlogerie américaine XIXᵉ | 47 | 0 % | 9 % |

La qualité du prix, elle, **ne bouge pas d'un pouce sur 38 ans** : montant,
devise, date de transaction et marteau hors frais sont à **100 %** sur les cinq
ventes, 1989 comme 2026. Ce qui varie n'est pas la donnée, c'est **la proportion
de montres de poche dans le catalogue**.

### Pourquoi un lot est rejeté — trois seaux, pas un
Il faut distinguer ce qui n'est pas une montre cotable de ce qui manque au
dictionnaire de marques. Mesuré sur les deux ventes généralistes :

| | 1995 (39 lots) | 2005 (78 lots) |
|---|---:|---:|
| GARDER | 54 % | 53 % |
| **vrai non** (R1 pendule/bijou/chronomètre de marine, R3b) | **0 %** | **9 %** |
| **lacune du dictionnaire** (R3, mais le titre NOMME l'horloger) | **36 %** | **29 %** |
| anonyme (« Not signed », « Swiss, circa 1890 ») | 10 % | 9 % |
| **plafond si le dictionnaire est complété** | **90 %** | **82 %** |

**Un tiers des rejets est du volume récupérable**, pas un jugement sur la source.
Et les deux époques ne se récupèrent pas de la même façon :

- **1995 — 14 lacunes, dont 10 marques horlogères du XXᵉ siècle** : *Vixa*,
  *Airain* (les deux Type 20, chronographes militaires activement cotés),
  *Universal*, *Solvil Watch Co.*, *Paul Ditisheim*, *Tempor Watch*, *Roskopf*,
  *Volta*, *Hamlet*, *Foucher*. **Ce sont de vraies montres cotables** : les
  ajouter à l'Excel ferait passer cette vente de 54 % à 90 %.
- **2005 — 23 lacunes, dont 18 horlogers de montres de poche des XVIIIᵉ-XIXᵉ** :
  *Lépine*, *Ilbery*, *William Anthony*, *Bronnikov*, *Charles Frodsham*,
  *Léo Juvet*, *Cugnier Leschot*, *Mugnier*, *T. Benson*… Récupérables aussi,
  mais ce sont des pièces uniques sans référence ni série comparable : du volume
  pour l'histoire, pas pour une cote.

### Le motif poche / bracelet, confirmé sur une deuxième source
| | bracelet | montre de poche |
|---|---:|---:|
| Antiquorum 1995 (39 lots) | 82 % gardés | **29 %** |
| Antiquorum 2005 (78 lots) | 97 % gardés | **16 %** |
| Antiquorum, les 5 ventes réunies (165 lots classables) | **90 %** (52/58) | **19 %** (8/42) |
| Morphy (mesuré ailleurs dans cette vague) | 92 % | **19 %** |

Deux sources indépendantes, **le même 19 % au point de pourcentage près**, et le
même écart de 4 à 5 fois. **C'est une lacune du
dictionnaire sur les horlogers d'avant 1900, pas un défaut des sources** — et
elle se corrige dans `filtres/Filtres_scrapping.xlsx`, sans une seule requête,
puisque le brut est conservé.

### La conclusion chiffrée
**La profondeur utile commence en 1989, pas en 2005** — mais elle n'est pas de la
même nature selon la décennie :

- pour de l'**historique de prix par marque et modèle** (marque + date + prix
  réalisé, sans référence), **les 38 ans sont exploitables**, de 54 % de rétention
  dans les années 1990 à 98 % dans les années 2020 ;
- pour de la **cote par référence**, la profondeur commence vers **2005** (28 %)
  et devient forte à partir de **2010** (82 %). Avant 2005, la référence
  n'existe presque pas — non pas parce que le site la cache, mais parce que la
  maison ne l'écrivait pas dans ses titres.

L'échantillonnage page par page est **très bruité** : dans la même vente de 2005,
la page 1 (section Rolex) rend 94 % de GARDER et 100 % de référence, la page 3
(section montres de poche) 7 % et 0 %. Antiquorum organise ses catalogues par
sections, pas au hasard. Les chiffres ci-dessus portent donc sur 3 à 5 pages par
vente, soit 15 à 27 % des lots de chaque vente, jamais sur une seule page.

## Ce qu'on récolte par tranche

Ventes à price-list par an, mesuré : 1989 → 4 · 1995 → 5 · 2001 → 8 · 2005 → 11 ·
2015 → 9 · 2026 → 3 (année incomplète). Lots vendus par vente, mesuré sur
6 price-lists : 106 (1989) · 367 (1995) · 380 et 317 (2001) · 293 (2005) ·
488 (2015) · 145 (2026).

| Tranche | Ventes | Lots vendus | GARDER aujourd'hui | avec le dictionnaire complété | dont **avec référence** |
|---|---:|---:|---:|---:|---:|
| 1989-1999 | ≈ 50 | ≈ 12 000 | ≈ 6 500 (54 %) | ≈ 10 800 (90 %) | ≈ 600 (5 %) |
| 2000-2009 | ≈ 95 | ≈ 31 000 | ≈ 16 400 (53 %) | ≈ 25 400 (82 %) | ≈ 8 700 (28 %) |
| 2010-2019 | ≈ 90 | ≈ 40 000 | ≈ 28 400 (71 %) | ≈ 32 800 (82 %) | ≈ 32 800 (82 %) |
| 2020-2026 | ≈ 32 | ≈ 5 600 | ≈ 5 500 (98 %) | ≈ 5 500 | ≈ 4 300 (76 %) |
| **Total** | **≈ 267** | **≈ 89 000** | **≈ 57 000** | **≈ 74 000** | **≈ 46 000** |

Les colonnes « ventes » et « lots vendus » sont extrapolées de 1 à 2 années
échantillonnées par tranche : à ±25 %. Les taux de rétention et de référence,
eux, sont mesurés.

**Ce que ça décide** : la tranche 2010-2019 est à elle seule **la moitié du
volume utile et 71 % des lignes référencées** — c'est par là qu'il faut
commencer la vague 4. La tranche 1989-1999 ne pèse que 7 000 lignes et presque
aucune référence : à collecter en dernier, et son intérêt double si le
dictionnaire est complété d'abord.

`corpus_horloger: True` est renseigné (R4c) : Antiquorum est 100 % horloger.
Réserve honnête : quelques ventes mixtes existent (titres portant « Jewelry »,
une vente « A collection of Watch Holders »), donc R4c est ici un peu plus
permissif que sur une vente de spécialité pure. R1 rejette les bijoux et les
horloges. Le titre de la vente **n'est pas** passé en `source_category` : « A
collection of Watch Holders » contient le mot *watch* sans contenir une seule
montre, et R0 aurait forcé le jeton de catégorie sur des porte-montres.

## Coût d'une collecte complète (vague 4)

| Poste | Requêtes |
|---|---|
| Énumération des ventes, 1989→2026 | **38** |
| Price-lists (≈ 265 ventes) | **≈ 265** |
| Catalogue, 20 lots/page, ≈ 115 000 lots au catalogue | **≈ 5 750** |
| **Total** | **≈ 6 050 requêtes** |

À `Crawl-delay: 5` → **≈ 8 h 30 de collecte d'affilée**, pour ≈ 85 000 à 100 000
prix réalisés datés sur 38 ans. À découper par année : chaque année est
indépendante et re-jouable.

Variante économique : les price-lists seules coûtent **≈ 300 requêtes** et
rendent les ≈ 90 000 marteaux datés — mais **sans devise et sans identité**,
donc inexploitables. L'identité représente 95 % du coût et c'est elle qu'on paie.

## Comment rejouer tout cela sans une seule requête

```bash
cd ~/Desktop/WP/labo/essais/antiquorum
../../shared/.venv/bin/python explore.py            # rejeu des échantillons, 0 requête
../../shared/.venv/bin/python explore.py --reseau    # + une vente réelle, 5 requêtes
```
`explore.py` relit `samples/` par la même fonction `lots_du_brut()` que
`moteur/rejoue.py` : le rejeu du filtre sur l'historique déjà collecté est donc
prouvé, pas promis.

## Échantillons (`samples/`)
- `robots-catalog-2026-09-21.txt` — la section ClaudeBot
- `auctions-year-{1989,1995,2001,2005,2015,2026}.html` — route 1, l'énumération datée
- `auctions-racine-30-dernieres-ventes.html` — route 1′, les 30 dernières ventes
- `price-list-118-generaliste-1995.html` (367 lots) et
  `price-list-100-generaliste-2005.html` (293 lots) — les deux ventes
  **généralistes** qui tranchent la question de la profondeur utile
- `lots-generaliste-1995-p1.html`, `lots-generaliste-2005-p{1,10}.html` —
  la page 1 de 2005 est la section Rolex (94 % gardés), la page 10 la section
  montres de poche : la démonstration du bruit de l'échantillonnage par page
- `price-list-{175-hongkong-1989,14-sandberg-geneve-2001,292-hongkong-2015,388-monaco-2026}.html`
  — route 2, les époques et leurs taux de frais (1 119 lots)
- `lots-{sandberg-2001-p1,hongkong-2015-p1,monaco_june_2026-p2}.html` — route 3
- `lot-388-217-daytona-paul-newman.html` — la fiche qui prouve que
  `schema:price` (300 000) n'est pas le prix vendu (406 720)
- `lot-14-2-unsigned-1790.html` — la même fiche en 2001, sans champs dédiés
- `records-2026-monaco.json`, `records-2001-newyork.json` — 40 + 40
  enregistrements normalisés
