# Certified Watch Store

Reconnaissance du 21/09/2026. Adaptateur : `moteur/sources/certifiedwatchstore.py`
(moteur generique `_shopify`, patron `berrys.py`).

## Identité
- **Source :** Certified Watch Store  ·  **URL :** <https://www.certifiedwatchstore.com/>
- **id :** `certifiedwatchstore`  ·  **Type :** `dealer` (revendeur de montres neuves)
- **Statut :** data récupérée — adaptateur écrit et validé

## Accès
- Shopify `/products.json?limit=250&page=N&currency=USD&country=US`. Pas de clé,
  pas de compte, pas de JavaScript.
- `robots.txt` (lu le 21/09/2026) : `User-agent: *` / `Allow: /`. Interdits :
  `/admin`, `/cart`, `/checkout`, `/account`, `/services`, `/cart.js`,
  `/recommendations/products`, `/collections/*sort_by*`.
  **`/products.json` n'est pas interdit.** Pas de `Crawl-delay`, rien sur ClaudeBot.
- En-têtes `utils.HEADERS` (ClaudeBot) : acceptés, HTTP 200 sur 9 requêtes,
  aucun 403 ni 429.

## Volume
- Page 1 pleine (250), page 5 pleine (offset 1 000), **page 12 vide**
  (offset 2 750), pages 28 et 40 vides.
  → **entre 1 250 et 2 750 fiches.** C'est la plus petite des trois boutiques,
  mais la plus propre.
- Composition, sur 250 fiches : 243 horlogères. `product_type` est la
  **taxonomie eBay** —
  `Jewelry & Watches:Watches, Parts & Accessories:Watches:Wristwatches` (232),
  `Collectibles:Disneyana:...:Watches, Timepieces` (6) — elle contient le mot
  « Watches », donc `_shopify.est_une_montre` la reconnaît. Le reste est
  résiduel et hétéroclite : lunettes de soleil, stylo Montblanc, couteaux,
  un jean. 3 % de bruit, affaire du filtre.
- **Pas de `chemin=` (collection) :** restreindre coûterait plus de volume que
  le bruit évité — leçon CW Sellors (191 montres dans la collection 'watches'
  sur ~3 000 au catalogue).

## Format de la data
- `vendor` rempli sur 250/250 : Casio (57), Timex (45), Luminox (44), Orient,
  Tissot, Citizen, Bulova, Victorinox. Prix médian 199 USD, maximum 1 375 USD
  sur la page 1 — segment accessible.
- `tags` : **vide sur 250/250**. Aucun garde-fou déclaré par la boutique
  (pas de `inquiry-only` comme chez Montredo) : la nature se déduit du statut.
- `compare_at_price` : `0.00` (donc inexploitable, pas de remise lisible).

## Les quatre champs qui décident

| Champ | Décision | Preuve |
|---|---|---|
| `price_amount` + `price_currency` | 235,00 **USD** | `products_limit3_US.json` vs `products_limit3_sans_pays.json` : prix **identiques** (235,00 / 309,00 / 345,00). 235,00 USD est bien le montant de la fiche publique `product_page.html` (`priceCurrency: USD`, `NewCondition`). |
| `price_date` | **`publication`** | Ici `published_at` == `created_at` sur **250/250** fiches : c'est une vraie date de mise en ligne, contrairement à Watches.com où la republication l'écrase. **Ce n'est pas une date de transaction** : le montant collecté est le prix du jour du relevé. |
| `price_nature` | **`asking`**, provenance `deduite_statut` | Revendeur de montres neuves sous emballage (`NewCondition` dans le JSON-LD de la fiche). Prix demandé par le marchand. |
| `reference` | **98 %** | 250 fiches : **245 références** propres lues dans le titre (`jeton_titre`), 5 sans référence. `CA0649-06X`, `AW0152-58H`, `NH8354-58A`, `EU6072-56D` : la boutique termine systématiquement son titre par la référence constructeur. Meilleur taux des trois sources de la vague. |

- **`sku_est_reference` reste FAUX**, et c'est un piège fin : le SKU
  *contient* la vraie référence mais préfixée d'un code maison —
  `CI2-CA0649-06X`. `_shopify._sans_prefixe` ne retire que des marqueurs
  d'état (`P-O`, `pre-owned`, `NOS`), pas un code fournisseur : l'activer
  écrirait 250 références `CI2-…` qui n'existent chez aucun constructeur.
  Le titre donne la référence nue — on laisse le moteur le lire.
- **`available=false` = RUPTURE DE STOCK**, `indisponible='inactive'`.
  Justification : ce sont des références de catalogue neuves et
  réapprovisionnables (`CI2-NJ0200-50M`, `CI2-NH8354-58A`…), pas des pièces
  uniques ; 95 fiches sur 250 sont indisponibles à un instant donné, toutes
  avec une référence de production courante. Les compter comme des ventes
  fabriquerait 38 % de fausses transactions.
- `cle='id'` : pas de reconstruction nocturne (identifiants et dates stables).

## Légal
- Données publiques, aucune protection franchie, aucun mur rencontré.
- `robots.txt` interdit l'automatisation du paiement : non touché.

## Trouvailles / notes de test
- `Shopify.country = "CH"` dans la page d'accueil : la localisation suisse est
  active côté vitrine mais ne change aucun prix (mono-marché USD).
  `country=US` conservé comme garde-fou.
- La sonde du 21/09 annonçait une année minimale de 1961 : sur l'échantillon
  de 250 fiches, aucune montre vintage — que du catalogue courant. Si un rayon
  d'occasion existe, il est ailleurs dans le catalogue ; à surveiller, car
  `indisponible='inactive'` deviendrait discutable pour des pièces uniques.
  En l'état, le choix prudent ne fabrique aucune fausse transaction.
- Réserve d'exploitation : `_shopify` écrit `condition="preowned"` en dur, faux
  pour un marchand de neuf. Non corrigé (fichier partagé), signalé.

## Échantillons (`samples/`)
- `robots.txt`, `sitemap.xml`, `home.html`
- `products_p1_US.json` (250 fiches, base de toutes les mesures)
- `products_limit3_US.json` / `products_limit3_sans_pays.json` (preuve devise)
- `product_page.html` (fiche publique Citizen CA0649-06X, 235,00 USD)
- `products_p40_US.json` (vide : plafond Shopify très loin)
- `records_echantillon.json` (5 enregistrements normalisés)

## Coût
13 requêtes pour cette source : robots.txt (×2), accueil, sitemap, page 1 de
products.json, 2 sondages de devise, fiche publique, 4 sondages de volume
(pages 40, 28, 12, 5), validation. **44 requêtes pour les trois boutiques.**
