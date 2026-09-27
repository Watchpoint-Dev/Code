# Cottone Auctions

Reconnaissance du 21/09/2026. 39 requêtes réseau au total, aucune collecte
complète. Tout ce qui est écrit ici est mesuré sur les fichiers de `samples/`.

## Identité
- **Source :** Cottone Auctions (Geneseo, NY, USA) · **URL :** <https://www.cottoneauctions.com/>
- **Type :** enchères (`auction`), maison **généraliste** — peinture, mobilier,
  argenterie, horloges, bijoux. La montre-bracelet y est un rayon parmi douze.
- **Statut :** adaptateur écrit et prouvé (`moteur/sources/cottone.py`).
  **Volume horloger faible** — lire la section « Ce que ça vaut » avant d'y
  investir des requêtes.

## Accès
- `robots.txt` lu le 21/09/2026 : `User-agent: *` / `Disallow:` (vide). **Aucune
  restriction, aucun `Crawl-delay`.** Copie dans `samples/robots.txt`.
  Le module prend quand même 1,5 s entre deux pages.
- `utils.HEADERS` (ClaudeBot) passe partout, HTTP 200 sur les 39 requêtes. Aucun
  429, aucun 403, aucun anti-bot, aucun mur. Pas besoin d'essayer un autre UA.
- HTML rendu serveur, pas une ligne de JavaScript nécessaire. Pas de compte, pas
  de clé, pas d'endpoint JSON (la sonde disait vrai : « sitemap seul »).
- Le sitemap (28 URL, `samples/sitemap.xml`) ne liste aucune fiche de lot, mais
  il livre la porte d'entrée : `/pricesRealized?PricesRealizedForm[category_id]=…`.
  De là on remonte à la vraie arborescence.

## Les trois voies du site, et laquelle on retient

| Voie | Ce qu'elle donne | Lots/requête | Date ? |
|---|---|---|---|
| `/prices-realized/category/<slug>?page=N` | titre, prix adjugé, **date**, lien lot | 50 | **oui** |
| `/search?term=X` | titre, prix adjugé, **catégorie source**, id de vente | tous d'un coup (634 pour « watch ») | **non** |
| `/lots/<id>/<slug>` | description, référence, diamètre, état, date, libellé du prix | 1 | oui |

**On retient la première.** Elle est la seule à porter la date sans requête
supplémentaire, et c'est la date qui fait la valeur d'une enchère.

La deuxième est spectaculaire et trompeuse : `/search?term=watch` rend **634
lignes en une seule requête**, sans pagination ni plafond apparent, avec la
catégorie publiée par la source et la mention `SOLD: $12,000` (ou une fourchette
d'estimation quand le lot n'est pas parti). Mais elle ne date rien. Elle ne donne
qu'un `/auction/<id>/` — et l'index des ventes, lui, n'expose que des slugs
(`/prices-realized/auction/fine-art-antiques-15`), jamais l'identifiant
numérique. **Les deux systèmes d'URL ne se recollent pas.** Dater par cette voie
coûterait une requête de fiche par ligne, soit un lot daté par requête contre
5 à 8 par la voie catégorie. Elle reste conservée comme voie de contrôle
(`samples/search-*.html`).

## La trouvaille : la date est dans un commentaire HTML

Sur les pages `/prices-realized/…`, le gabarit envoie le nom de la vente et sa
date, **mais commentés** :

```html
<div class="title"><small>153</small><br />
  <a href="/lots/79134/rolex-day-date-reference-18038">Rolex Day-Date, Reference…</a></div>
<!--<a href="/auction/195/art-antiques-online-only">Art & Antiques…</a><br />-->
<!--<br /><strong>Jan 30, 2025</strong>-->
<p class="est_price_grid">$12,000</p>
```

Un navigateur ne les affiche pas ; le serveur les envoie quand même. C'est ce qui
transforme cette source en source datée : **50 lots datés par requête**, 100 %
de remplissage sur les 462 blocs lus.

**Ce n'est pas une date de mise en ligne.** Contrôle croisé sur 4 lots pris en
2009, 2014, 2016 et 2022 : la date du commentaire est, au jour près, l'`Auction
Date` publiée sur la fiche du lot (`samples/lot-2009-705.html` et suivants).

Autre détail du même ordre : le texte du lien est **tronqué** par le gabarit
(« Rolex Day-Date, Reference… »), alors que l'attribut `alt` de la vignette porte
le titre **complet**. On lit donc `alt`. Se tromper coûterait les références, qui
vivent en fin de titre.

## Nature du prix — mesurée, pas supposée

`price_includes_premium = True`, et ce n'est **pas** une déduction arithmétique.

La fiche de lot titre son montant en toutes lettres :

```html
<h2 class="sold_realized">Hammer Price w/ BP</h2>
<p class="price_realized">$12,000</p>
```

« Hammer Price **w/ BP** » = marteau **avec** buyer's premium. Libellé relevé
identique sur **8 fiches** allant de **2009 à 2025** (`samples/lot-*.html`). Il
ne varie pas.

Le piège des maisons américaines est donc contourné par le haut : on n'a pas
besoin de deviner. Et on ne tente **pas** de reconstituer le marteau nu par
division — le taux de frais américain n'est pas constant à l'intérieur d'une même
vente (×1,25 sur un lot, ×1,30 sur un autre, mesuré chez New Orleans), et Cottone
ne publie nulle part son barème par tranche. Le marteau nu n'est pas disponible
sur cette source, et c'est définitif.

Conséquence pour la base : les montants Cottone sont comparables à ceux de
Christie's (frais inclus) et **surévalués d'un quart** par rapport à Artcurial
ou Sworders (marteau nu). Le champ `price_includes_premium` est là pour ça.

`price_nature_provenance` :
- `deduite_statut` sur les lignes issues des listes — le lot figure dans la
  section « Prices Realized » avec un montant **unique** et non une fourchette ;
- `champ_dedie` sur les lignes enrichies par leur fiche, où le libellé
  `Hammer Price w/ BP` est lu directement.

## Le piège du filtre : la catégorie de la source le sabote

Cottone classe **par matière, pas par fonction**. Toutes ses montres-bracelets
sont rangées sous `Jewelry`, avec les bagues et les colliers. Or `Jewelry` n'est
ni un libellé horloger ni un libellé muet : la règle **R0** le lit comme « ce
n'est pas une montre » et rejette le lot **avant** tout examen du titre.

Mesure sur 334 lots de la catégorie `Jewelry` (`samples/cat-jewelry*.html`) :

```
sans categorie_source :  27 GARDER   307 REJETER
avec categorie_source :   0 GARDER   334 REJETER
```

Les 27 perdus sont des Rolex Day-Date, Omega, Patek Philippe, Vacheron
Constantin, Heuer Seafarer. **L'adaptateur ne passe donc pas `categorie_source`
au filtre.** Le libellé est tout de même enregistré dans `source_category`, où il
reste utile en aval : c'est lui, et lui seul, qui permet d'écarter les montres de
poche d'une série de prix de montres-bracelets.

Ce que `filtre().categorie()` répond, pour mémoire :
`Pocket Watches` → True · `Jewelry` → **False** · `Clocks & Timepieces` → True
(ce dernier ferait entrer les régulateurs et les horloges de parquet).

## Format de la data

Champs disponibles sur la liste, donc sans surcoût : titre complet, numéro de
lot, prix adjugé (USD), **date de vente**, identifiant et slug de la vente,
catégorie de la source, URL et identifiant du lot.

Sur la fiche de lot en plus : description, numéro de série, diamètre de boîtier,
état, provenance, et parfois l'estimation d'avant-vente.

Complétude mesurée sur les 46 lignes gardées de l'échantillon
(`samples/records_cap40.json`) :

| Champ | Remplissage |
|---|---|
| `price_amount` + `price_currency` | 46/46 — 100 %, USD natif, jamais converti |
| `price_date` | 46/46 — **100 %**, date de transaction |
| `price_nature` + provenance | 46/46 (`realised`) |
| `price_includes_premium` | 46/46 = True |
| `brand` | 46/46 (lue au dictionnaire du filtre, la source n'a pas de champ marque) |
| `reference` | **5/46 = 11 %** (4 `extrait_titre`, 1 `jeton_titre`) |
| `year` | 1/46 — l'année d'époque n'est presque jamais dans le titre |

## Volume et profondeur

Comptes de pages relevés directement dans les pagineurs :

| Catégorie | Lots | Pages | Gardés (mesuré) | Rendement |
|---|---|---|---|---|
| `pocket-watches` | 128 | 3 | 22 | 17 % |
| `jewelry` | 1 584 | 32 | 27 sur 334 lus | ~9 % |
| `clocks-timepieces` | ~3 350 | 67 | 0 sur 50 lus · 40 sur 3 323 (mesure 11/08/2026) | **1,2 %** |

**Total atteignable : ≈ 210 prix réalisés datés pour ≈ 102 requêtes.**

Profondeur datée **prouvée** : `2009-09-26` → `2026-03-19` sur l'échantillon, et
l'échantillon complet des listes descend à `2009-01-01`. Dix-sept ans.

`num_per_page=100` fonctionne sur la vue catalogue `/auction/<id>/` mais est
**ignoré** sur les vues `prices-realized` : 50 par page, sans recours (testé,
`samples/` avant nettoyage). Il n'y a pas de raccourci sur le nombre de requêtes.

## Ce que ça vaut, franchement

La note de travail qui estimait Cottone à « 33 750 lots remontant à 2009 » et
l'un des deux meilleurs retours sur effort du dossier **confond le volume de la
maison avec le volume horloger**. Les 33 750 lots existent probablement ; 1 à
17 % sont des montres selon la catégorie, et l'essentiel de l'« horlogerie » de
cette maison est de l'horlogerie d'ameublement — régulateurs, orreries, horloges
de parquet, comtoises.

Mais l'inverse est vrai aussi : la fiche `ECARTEES["cottone"]` de
`moteur/catalogue_essais.py` (« 3 323 lots aspirés, le filtre n'en garde que
40 ») a **aspiré la mauvaise catégorie**. 3 323 ≈ 67 pages × 50, c'est exactement
`clocks-timepieces`. Les montres-bracelets de Cottone n'étaient pas là : elles
sont sous `Jewelry`. La conclusion « écartée » reposait sur une mesure juste
appliquée au mauvais rayon. **Cette ligne du catalogue est à corriger.**

Verdict honnête : ce n'est pas un gisement, c'est un **complément de qualité**.
~210 lignes, mais chacune avec une vraie date de transaction, une devise native,
une nature de prix lue et non devinée, et 17 ans de recul. À comparer à Sworders,
qui rend 2 500 lignes sans aucune date. Pour une base dont la valeur est la
profondeur datée, 210 lignes datées valent mieux que 2 500 lignes muettes.

À prendre dans cet ordre, et sans la troisième catégorie si les requêtes sont
comptées : `pocket-watches` (3 requêtes, 22 lignes), `jewelry` (32 requêtes,
~150 lignes). `clocks-timepieces` coûte 67 requêtes pour ~40 lignes.

## Trouvailles / notes de test

- **Bug attrapé sur soi-même.** Le premier jet de l'enrichissement par fiche
  appelait `reference_libre` sur la **description**. Sur 3 fiches il a rendu
  deux « références » : `22.8` et `118.6` — un poids d'or et un diamètre de
  boîtier. `reference_libre` reconnaît un jeton à sa forme et retient le
  **dernier** du texte : fiable sur un titre de trois mots, désastreux sur une
  description de catalogue. Corrigé : sur une description, **seul**
  `reference_dans` (à mot-clé) est autorisé, provenance `extrait_description`.
  C'est la même faute que les 9 770 fausses références de l'historique.
- Enrichissement par fiche, rendement réel mesuré sur 8 fiches : **1** référence
  gagnée, 5 diamètres, 8 confirmations du libellé `Hammer Price w/ BP`. Une
  requête par lot pour ça : `fiches=0` par défaut, et c'est justifié.
- La vue `prices-realized` d'une catégorie est triée par **prix décroissant**,
  pas par date : la page 1 est le haut du marché (donc, sous `Jewelry`, des
  bagues en diamant), les montres à quatre chiffres vivent pages 2 à 25.
  Échantillonner la seule page 1 sous-estime le rendement — c'est pourquoi les
  pages 2, 9, 17, 25 et 32 ont été tirées.
- Quelques lots des vues `prices-realized` portent une fourchette
  (`$300-$500`) ou `No Estimate` au lieu d'un montant : invendus ou retirés.
  L'adaptateur les écarte — ils ne disent aucune transaction. Aucun n'est
  apparu dans les 462 blocs des trois catégories horlogères, mais la garde est
  là ; ils sont visibles dans `samples/search-watch-p1.html` (72 fourchettes + 20 « No Estimate » sur 634 lignes).
- Les montres de poche entrent par R8 (« rien ne s'oppose ») : 17 des 22 lignes
  de `pocket-watches` sont littéralement des montres de poche. Ce n'est pas au
  module de trancher contre le filtre ; `source_category` = `Pocket Watches`
  rend le tri possible en aval, sans requête.
- `/auction/<id>/<slug>` est la vue **catalogue** : elle affiche les
  **estimations**, pas les prix réalisés, et ne porte pas de date. Ne pas la
  confondre avec `/prices-realized/auction/<slug>`.

## Légal
- `robots.txt` entièrement permissif au 21/09/2026, relu à chaque exécution du
  projet. Rien de contourné, aucune protection franchie, aucun compte.
- Données publiques : les prix réalisés sont la vitrine commerciale de la maison
  (« Our prices realized are consistently higher than our competitors », meta
  description de `/prices-realized/start`).
- Le site publie aussi des PDF de prix réalisés par vente
  (`/uploads/auction/prices_realized_doc/*.pdf`) : non exploités ici, voie de
  secours si le gabarit HTML change.

## Échantillons (`samples/`)

| Fichier | Ce qu'il prouve |
|---|---|
| `robots.txt`, `sitemap.xml` | l'ouverture, et les 28 URL du sitemap |
| `prices-realized-start.html` | l'index des ventes : 14 pages, slugs + dates |
| `cat-pocket-watches*.html` (3) | les 128 lots de la catégorie, 3 pages |
| `cat-jewelry*.html` (6) | pages 1, 2, 9, 17, 25, 32 — le rendement en profondeur |
| `category-clocks-timepieces-p1.html` | 67 pages, 0 montre-bracelet sur 50 |
| `lot-79134.html`, `lot-2009-705.html`, `lot-2014-22520.html`, `lot-2016-37977.html`, `lot-2022-72011.html` | `Hammer Price w/ BP` et `Auction Date`, de 2009 à 2025 |
| `search-rolex-p1.html`, `search-watch-p1.html`, `search-wristwatch-p1.html` | la voie de recherche : 634 lignes sans pagination, catégories publiées |
| `auction-195.html`, `pr-auction-art-antiques-online-only-2.html` | la vue catalogue (estimations) contre la vue prix réalisés |
| `records_cap40.json` | les 46 lignes normalisées, rejouées sur le brut après correction du bug de référence |
