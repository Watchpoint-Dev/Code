# Grailzee

Reconnaissance du 21/09/2026. Adaptateur : `moteur/sources/grailzee.py`
— **adaptateur dédié, PAS le moteur `_shopify`**. La raison est mesurée plus bas :
le prix Shopify de cette boutique est la commission d'acheteur, pas le prix de
la montre.

## Identité
- **Source :** Grailzee  ·  **URL :** <https://grailzee.com/>
- **id :** `grailzee`  ·  **Type :** `auction` (plateforme d'enchères en ligne
  sur socle Shopify, lots consignés par des particuliers et des marchands)
- **Statut :** data récupérée — **prix VENDUS avec date de transaction**

## Accès
1. `https://grailzee.com/products.json?limit=250&page=N&currency=USD&country=US`
   → la **liste des lots** et leurs tags (`auctioneer-live`,
   `auctioneer-completed`, `auctioneer-sold`, `auctioneer-marketplace`).
2. `https://grailzee.com/apps/auctioneer/api/auctions/<id_produit>`
   → **le prix**. API publique de l'app d'enchères, sans compte ni cookie.
   Réponse JSON : `currentBid`, `completedAt`, `hasAuctionSold`, `hasWinner`,
   `hasReserve`, `isMarketplace`, `make`, `model`,
   `referenceNumber.referenceNumber`, `startsAt`, `endsAt`, `bidIncrement`.
3. Bonus vu au passage : `/apps/auctioneer/bids/latest?max=N` rend les
   dernières enchères portées, tous lots confondus, avec montant, titre, handle
   et date de clôture prévue (`samples/bids_latest.json`).
   `/apps/auctioneer/api/auctions/<id>/bids` rend la liste des enchères d'un lot.

- `robots.txt` (lu le 21/09/2026) : `User-agent: *` avec
  **`Disallow: /collections/all`** et **`Disallow: /apps/auctioneer/members/*`**
  — les deux sont respectés et évités par l'adaptateur. `/products.json` et
  `/apps/auctioneer/api/` ne sont pas interdits. Pas de `Crawl-delay` pour
  `*` (10 s pour AhrefsBot / MJ12bot, 1 s pour Pinterest, nommément).
- En-têtes `utils.HEADERS` (ClaudeBot) : acceptés, HTTP 200 partout, aucun 403
  ni 429 sur 18 requêtes.
- **Aucune protection franchie.** La vitrine affiche « log in to see current
  bid » avec un cadenas, mais l'API de l'app répond sans authentification :
  c'est un habillage d'interface, pas un mur. Rien n'a été contourné, aucun
  compte créé, aucun UA falsifié.

## LE PIÈGE CENTRAL : le prix Shopify est la commission

`variants[0].price` **n'est pas le prix de la montre.** La variante Shopify ne
sert qu'à encaisser les frais d'acheteur.

- Lots en cours : `price = 0.00` sur **250/250** fiches de la page 1.
- Lots conclus (page 99, 229 lots `auctioneer-completed` sur 250) : 120 fiches
  portent un prix > 10, dont **67 exactement à 250,00**.
- 250,00 est le **plancher de commission** de l'app, lu dans son propre
  bundle : `fee:{minimum:250,maximum:5e3,percentage:.05}`
  (`samples/auctioneer-endpoints.txt`). Maximum observé : 3 412,50.
- Vérification directe contre l'API :

| Lot | prix Shopify | frais/0,05 | `currentBid` (API) |
|---|---|---|---|
| Tag Heuer Carrera 02T Tourbillon | 550,00 | 11 000 | **11 000** ✓ |
| Rolex GMT-Master II « Pepsi » 126710BLRO | 1 350,00 | 27 000 | **27 000** ✓ |
| Rolex Datejust 41 126333 | 550,00 | 11 000 | **15 000** ✗ |

→ **Brancher `_shopify` ici aurait écrit des « prix de montres » entre 250 et
3 412 $** pour des Rolex et des tourbillons. Et la reconstitution
arithmétique frais/0,05 n'est pas fiable non plus (3ᵉ ligne) : **seule l'API
dit le prix.** C'est la raison d'être de l'adaptateur dédié.

## Les quatre champs qui décident

| Champ | Décision | Preuve |
|---|---|---|
| `price_amount` + `price_currency` | `currentBid` en **USD** | Boutique mono-marché USD (`Shopify.currency` USD, `Shopify.country = "US"` — la seule des trois qui ne nous localise pas en Suisse). L'API rend un nombre nu, jamais converti. |
| `price_date` | **`completedAt`** — *la date de la transaction* | `completedAt: "2026-06-12T15:47:48+00:00"` sur un lot vendu. C'est la nature de date qui manque partout ailleurs : ni mise en ligne, ni relevé, mais **clôture de vente**. `endsAt` sert de repli. |
| `price_nature` | **`realised`** (adjudication), `sold` si `isMarketplace` | provenance `champ_dedie` : c'est la source qui déclare `hasAuctionSold`, pas nous. Les lots passés par la place de marché intégrée (négociation de gré à gré, tag `auctioneer-marketplace`) sont des ventes conclues mais pas des adjudications. |
| `reference` | **champ dédié** | `referenceNumber: {id: 104, referenceNumber: "126610LN"}` — une vraie table de références, pas un texte libre : `CAR5A8K.FT6172`, `310.30.40.50.06.001`, `5513`. Sur l'échantillon validé : 2/2 en `champ_dedie`. Repli titre/jeton prévu. |

- **`price_includes_premium = False`** : `currentBid` est le **marteau nu**.
  Les 5 % de commission acheteur sont encaissés à part, par la variante Shopify
  du lot — c'est précisément ce qui permet de le prouver (550 = 5 % de 11 000).
- **Invendus écartés.** Un lot peut être `auctioneer-completed` avec un
  `currentBid` élevé et `hasAuctionSold=false` : une Submariner 126610LN s'est
  arrêtée à 11 800 sans acheteur déclaré (`samples/api_auction_completed.json`).
  Ce n'est pas une transaction. Ces lots sont comptés dans le journal et
  **jamais chargés**.
- `highestBid` / `winningBid` reviennent vides (`{}` / `null`) : l'identité des
  enchérisseurs n'est pas publiée. Seul le montant l'est. Très bien ainsi.
- Les titres sont d'une qualité rare : `1966 (1.2 Mill Serial) Rolex Submariner
  No-Date 40MM Black "Swiss Only" Dial Oyster Bracelet (5513)` — année, marque,
  modèle, diamètre, cadran, bracelet, référence.

## Volume et coût
- 110 fichiers sitemap produits ; `products.json` reste plafonné par la
  plateforme à `page*limit = 25 000`. La page 99 (offset 24 500) répond encore
  **250 lots** : **le catalogue accessible sature le plafond Shopify**, et il y
  a des lots plus anciens hors d'atteinte par ce chemin.
- Composition : page 1 = 100 % de lots en cours (0,00 $) ; page 99 = 229 lots
  `auctioneer-completed` sur 250, dont 118 `auctioneer-sold`.
  → **ordre de grandeur : 20 000 lots conclus atteignables**, dont un peu moins
  de la moitié réellement vendus.
- **COÛT : une requête API par lot.** ~100 pages products.json + une requête
  par lot conclu. C'est un budget de vague 4 à arbitrer explicitement : c'est
  cher, mais c'est la nature `realised` datée, celle qui manque le plus.
- L'adaptateur expose `lots_du_brut()` + `fiche()` : le brut conserve les
  réponses d'API, donc la source est **rejouable hors ligne** dès que
  l'orchestrateur ajoutera `grailzee` au tuple `ENCHERES` de `moteur/rejoue.py`
  (fichier partagé, non touché ici).
- `collect(cap, depart=N)` permet de reprendre à une page donnée. La page 1
  n'est que du direct (0 lot conclu) et la page 99 en contient 229 sur 250 :
  le rang exact où les lots conclus commencent n'a **pas** été mesuré, faute de
  budget de requêtes. À mesurer avant la collecte de vague 4, sinon les
  premières pages coûtent des requêtes pour rien.

## Validation
`collect(cap=2, depart=99)` → 3 requêtes, 2 enregistrements :
Rolex Submariner 5513 (1966) **vendue 8 500 USD le 07/06/2026**, `realised`,
référence `champ_dedie`, marteau nu ; et un lot marketplace en `sold`.
Journal, natures, provenances et dates tous remplis
(`samples/records_echantillon.json`).

## Légal
- Données publiques (montants d'enchères affichés sur la plateforme, identités
  non publiées). Aucune protection franchie, aucun compte, aucun contournement.
- `robots.txt` respecté à la lettre, y compris `/collections/all` et
  `/apps/auctioneer/members/*`.

## Échantillons (`samples/`)
- `robots.txt`, `sitemap.xml` (110 sitemaps produits), `home.html`
- `products_p1_US.json` (250 lots en cours, tous à 0,00 — la preuve du piège)
- `products_p99_US.json` (250 lots dont 229 conclus, prix = commissions)
- `api_auction.json` (lot en cours : structure complète de l'API)
- `api_auction_completed.json` (lot terminé **invendu** à 11 800)
- `api_auctions_sold.json` (3 lots vendus : marteau, `completedAt`, référence)
- `api_auction_bids.json`, `bids_latest.json` (les enchères publiques)
- `auctioneer-endpoints.txt` (barème de frais et chemins d'API extraits du
  bundle de l'app ; le bundle de 4 Mo n'a pas été conservé)
- `product_live.html` (la vitrine, où le prix est masqué derrière un cadenas)
- `records_echantillon.json`

## Coût
18 requêtes pour cette source : robots.txt (×2), accueil, sitemap, bundle de
l'app d'enchères, fiche publique d'un lot en cours, 2 pages products.json
(1 et 99), 6 appels d'API (lot en cours, ses enchères, `bids/latest`, 1 lot
invendu, 3 lots vendus), et 3 requêtes de validation.
**44 requêtes pour les trois boutiques de la vague.**
