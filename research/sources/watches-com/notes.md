# Watches.com

Reconnaissance du 21/09/2026. Adaptateur : `moteur/sources/watchesdotcom.py`
(moteur generique `_shopify`, patron `berrys.py`).

## Identité
- **Source :** Watches.com  ·  **URL :** <https://www.watches.com/>
- **id :** `watchesdotcom`  ·  **Type :** `retail` (detaillant agree multimarque, neuf)
- **Statut :** data récupérée — adaptateur écrit et validé

## Accès
- Shopify `/products.json?limit=250&page=N&currency=USD&country=US`. Pas de clé,
  pas de compte, pas de JavaScript.
- `robots.txt` (lu le 21/09/2026) : `User-agent: *` / `Allow: /`. Interdits :
  `/admin`, `/cart`, `/checkout`, `/account`, `/services`, `/cart.js`,
  `/recommendations/products`, les pièges de tri `/collections/*sort_by*`.
  **`/products.json` n'est pas interdit.** Pas de `Crawl-delay`. Aucune règle
  nommant ClaudeBot.
- En-têtes `utils.HEADERS` (ClaudeBot) : acceptés, HTTP 200 sur 10 requêtes,
  aucun 403 ni 429.

## Volume
- Page 1 pleine (250), page 10 pleine (offset 2 250), **page 30 vide**
  (offset 7 250), pages 80 et 100 vides.
  → **entre 2 500 et 7 250 fiches**, très loin du plafond Shopify de 25 000.
  Le sitemap annonce 5 fichiers produits, mais Shopify les découpe par plage
  d'identifiants et non par paquets de 5 000 : le compte de fichiers ne dit
  rien du volume (piège à noter).
- Composition, sur 250 fiches : 238 `product_type` 'Watch'/'Watches',
  11 'Strap', 1 vide. **Aucune collection dédiée n'est nécessaire** ; les 4 %
  d'accessoires sont l'affaire du filtre.

## Format de la data
- Champs utiles : `title`, `vendor` (100 % rempli), `product_type`, `tags`,
  `variants[0].price`, `available`, `sku`, `published_at`, `created_at`.
- `compare_at_price` : **vide sur 250/250**. Le thème contient pourtant un
  script « Hide product MSRP » qui masque le prix barré aux visiteurs de
  Californie et d'Oregon : le champ existe donc dans le modèle, mais il n'est
  pas alimenté sur l'échantillon. Aucune remise mesurable.
- Marques : micro-marques et marques accessibles — Oceaneva, Xeric, G-Shock,
  Hemel, Duxot, Nubeo, Thomas Earnshaw, Shinola, RZE, Nsquare. Prix médian
  440 USD, maximum 49 680 USD.

## Les quatre champs qui décident

| Champ | Décision | Preuve |
|---|---|---|
| `price_amount` + `price_currency` | 279,00 **USD** | `products_limit3_US.json` vs `products_limit3_sans_pays.json` : prix **identiques** (279,00 / 1 769,00 / 42 800,00). Et 279,00 USD est bien le montant de la fiche publique `product_page.html` (`priceCurrency: USD`). |
| `price_date` | **`releve`** (date du jour de collecte) | `published_at` est un horodatage de **republication** : 223 fiches sur 250 l'ont postérieur à `created_at`, médiane +26 j, maximum **+1 148 j** (créée le 11/03/2025, republiée le 11/09/2026). La page 1 ne contient que des republications de juillet-septembre 2026. Cette date ne date rien. |
| `price_nature` | **`asking`**, provenance `deduite_statut` | Détaillant **agréé** (« Authorized Dealer », « we're an authorized retailer » sur la fiche), catalogue neuf en dropship. Le prix est celui demandé par le marchand. On n'écrit **pas** `msrp` : on ne peut pas prouver que le prix affiché est le tarif officiel, `compare_at_price` étant vide. |
| `reference` | 22 % seulement | 250 fiches : 56 références lues dans le titre (`jeton_titre` 55 + `extrait_titre` 1), **179 retombent sur le SKU** (provenance `sku`), 15 sans référence. Les micro-marques ne publient pas de référence au sens horloger. |

- **`sku_est_reference` reste FAUX.** `RZE-UTD-STG-NY-P` pour une
  « RZE UTD-8000-STG » : le SKU cite la marque mais n'est pas la référence
  constructeur. `Olto-8` → `O6-9999`. L'activer écrirait 179 fausses références.
- **`available=false` = RUPTURE DE STOCK**, `indisponible='inactive'`.
  Justification : références de catalogue neuves livrées par la marque (tags
  'drop ship' / 'dropship' sur 134 fiches sur 250, 'new' sur 171) ; la même
  référence revient en stock. 83 fiches sur 250 indisponibles à l'instant du
  relevé — les compter comme des ventes fabriquerait 33 % de fausses
  transactions (l'erreur payée chez Topper).
- `cle='id'` : les identifiants sont stables, `created_at` remonte à 2023 sur
  des fiches encore en ligne. Pas de reconstruction nocturne comme Montredo.

## Légal
- Données publiques, aucune protection franchie, aucun mur rencontré.
- `robots.txt` demande de ne jamais automatiser un paiement (`Checkouts are for
  humans`) : nous ne touchons ni panier ni checkout.

## Trouvailles / notes de test
- `Shopify.country = "CH"` dans la page d'accueil : la localisation suisse est
  bien active côté vitrine. Elle ne change aucun prix ici (boutique
  mono-marché USD), mais `country=US` est conservé comme garde-fou — c'est
  exactement la configuration qui a coûté −17,8 % chez Craft & Tailored.
- Le `robots.txt` propose un endpoint « UCP/MCP » (`/api/ucp/mcp`) pour les
  agents. Non exploré : `products.json` suffit et reste le chemin le moins
  intrusif.
- Réserve d'exploitation : le moteur `_shopify` écrit `condition="preowned"`
  en dur pour toutes les boutiques. Pour un détaillant de neuf comme celui-ci,
  ce champ est faux. Non corrigé ici (fichier partagé), signalé.

## Échantillons (`samples/`)
- `robots.txt`, `sitemap.xml`, `home.html` (localisation `Shopify.country`)
- `products_p1_US.json` (250 fiches, base de toutes les mesures)
- `products_limit3_US.json` / `products_limit3_sans_pays.json` (preuve devise)
- `product_page.html` (fiche publique `utd-8000-stg`, 279,00 USD, « Authorized Dealer »)
- `products_p100_US.json` (vide : le plafond Shopify n'est pas atteint)
- `records_echantillon.json` (5 enregistrements normalisés)

## Coût
13 requêtes pour cette source : robots.txt (×2, la première sans sauvegarde),
accueil, sitemap, page 1 de products.json, 2 sondages de devise, fiche
publique, 4 sondages de volume (pages 100, 80, 30, 10), validation de
l'adaptateur. **44 requêtes pour les trois boutiques de la vague.**
