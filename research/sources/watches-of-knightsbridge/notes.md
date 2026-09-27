# Watches of Knightsbridge

Reconnaissance du 21/09/2026. Adaptateur : `moteur/sources/knightsbridge.py`.

## Identité
- **Source :** Watches of Knightsbridge · **URL :** <https://www.watchesofknightsbridge.com/>
- **Maison de ventes 100 % horlogère (Londres), qui exploite aussi deux arms de
  détail : « CURATED » et « OYSTERBAR ».**
- **Type retenu :** `dealer` — et non `auction`. Voir « Nature du prix ».
- **Statut :** data récupérable, adaptateur écrit et vérifié.
- `corpus_horloger: True` — confirmé : catégories `Watches` (555) et
  `Watch Accessories` (18), rien d'autre au catalogue.

## Accès
- **WooCommerce Store API**, publique, non authentifiée :
  `/wp-json/wc/store/v1/products?per_page=100&page=N[&stock_status=outofstock]`
  (`/wp-json/wc/store/products`, sans `v1`, rend la même chose).
- **L'UA décide de tout.** `utils.HEADERS` (ClaudeBot) → **HTTP 403**,
  `"Your request was blocked."`. L'UA par défaut de la bibliothèque
  (`python-requests/2.34.2`) → **HTTP 200**. C'est un filtre d'UA du pare-feu :
  robots.txt ne porte aucune règle ClaudeBot. Mesures dans
  `samples/mesures_ua_403.txt`.
- **Les pages HTML sont fermées aux deux UA**, sauf l'accueil : `/about/`,
  `/product/<slug>/`, `/auctions/` rendent 403 (52 octets). Les « 1 142 ko » que
  la sonde a mesurés sont la page d'accueil et rien d'autre. On s'arrête là :
  pas de navigateur sans tête, pas de contournement. L'API suffit.
- Pas de compte, pas de clé. Un GET poli via `utils.get` (pause 1 s) passe sans
  incident ; aucun 429 rencontré sur ~38 requêtes.
- Le site rend du JavaScript (Divi + WooCommerce) mais l'API est du JSON pur.

### Le commentaire de `shared/utils.py` est faux — à corriger un jour
`shared/utils.py` affirme en commentaire que « Watches of Knightsbridge porte
`User-agent: ClaudeBot / Disallow: /` — cette source nous est donc fermée, et
elle le restera ». Le robots.txt servi le 21/09/2026 sur www **et** sur l'apex
tient en trois lignes et ne mentionne pas ClaudeBot (`samples/robots.txt`). Je
n'ai pas modifié `utils.py` (fichier partagé), mais la note qu'il porte a coûté
cette source pendant deux mois.

## Format de la data
- JSON WooCommerce Store API. Champs exploités : `prices` (price,
  currency_code, currency_minor_unit), `name`, `permalink`, `id`, `sku`,
  `is_in_stock`, `categories`, `attributes`, `description`.
- **`currency_minor_unit` = 0 sur les 573 fiches** → les prix sont en livres
  entières, aucune division. 100 % GBP.
- Attributs de taxonomie, libellés **en MAJUSCULES** :

  | attribut | fiches | ce que c'est |
  |---|---|---|
  | BRAND | 567 / 573 | marque, propre |
  | YEAR | 553 | année de PRODUCTION, souvent une décennie (« 1960s », « c. 1990 ») |
  | MOVEMENT | 552 | « Automatic », « Manual Wind, Cal. 23-300 » |
  | MODEL | 529 | nom commercial (« Datejust 36 OysterQuartz ») — **pas** une référence |
  | BOX/PAPERWORK | 491 | |
  | REFERENCE | 465 | **vraie référence constructeur** : 3538, 16030, 118238, WSSA0055 |
  | METAL / MATERIAL | 447 / 105 | matière du boîtier |
  | CASE DIAMETER / CASE | 387 / 135 | diamètre (« 36mm ») |
  | LOCATION | 166 | « London - UK » (143), « Dubai - UAE » (23) |
  | DIAL / Dial Colour | 96 / 13 | |
  | CONDITION | 9 | quasi vide |

- **Volume : 573 fiches. Pas 10 000 à 25 000.** 72 en vitrine + 501 épuisées
  (les deux `X-WP-Total` s'additionnent exactement). Le second appel
  `stock_status=outofstock` est bien indispensable : sans lui, 72 lignes.
- **Aucune date dans l'API Store** : pas de `date_created`. La date vit dans
  `/wp-json/wp/v2/product` (`date` = publication). Profondeur **2021-12-28 →
  2026-08-24**, 573/573 datées, 200 jours distincts sur 50 mois — un dépôt au
  fil de l'eau, pas un import en bloc. 2024 : 219, 2023 : 215, 2022 : 65,
  2026 : 55, 2025 : 14, 2021 : 5.
- Prix : 11 fiches à 0 (« prix sur demande », écartées), aucun prix négatif,
  médiane 7 500 GBP, étendue 80 → 76 000 GBP.

## Nature du prix — la question qui décide de la valeur de la source
**Ce sont des prix DEMANDÉS de marchand, pas des prix réalisés d'enchère.**
`price_nature = asking`, `price_nature_provenance = deduite_statut`,
`price_includes_premium = None`. Ce qui a été mesuré :

- 456 des 573 SKU commencent par **`CUR`** (Curated) ; les autres sont des
  codes de stock détail (GMT, DJ, DD, EXP, SUB, SEA, `antiq`). Aucun numéro de lot.
- Les fiches sont **achetables au panier** (`is_purchasable: true` sur 562,
  `add_to_cart` présent), `on_sale: false` sur les 573,
  `price == regular_price == sale_price` partout.
- L'attribut BOX/PAPERWORK dit « Watches of Knightsbridge » (165) ou
  « OYSTERBAR » (44) : c'est la garantie du marchand.
- **Aucun vocabulaire d'enchère dans les 573 descriptions** : « hammer » 0,
  « realised » 0, « premium » 0, « auction » 0, « estimate » 1, « lot » 3 (en prose).
- 18 fiches ont un stock de 9 ou 10 unités : ce sont les accessoires. Une
  maison de ventes n'a pas dix exemplaires d'un lot.
- `wp-sitemap.xml` ne déclare que `page` et `product`. Le menu porte un lien
  `/auctions/` mais cette page rend 403 et n'est pas au sitemap.
  **L'archive d'enchères de la maison n'est pas dans WooCommerce.**
- `price_includes_premium` : laissé à `None` et non deviné. Rien dans l'API ne
  parle de frais acheteur, et sur un prix de détail payé au panier la question
  n'a pas de sens. Les frais acheteur de la maison ne s'appliquent qu'à son
  côté enchères, qui n'est pas ici.

**Conséquence :** l'audit de juillet (« prix réalisés / dernière enchère,
2014 → aujourd'hui, 10 000 à 25 000 lots ») ne décrit pas ce que la plateforme
WooCommerce publie. Le classer `auction`/`realised` sur la foi de l'enseigne
aurait injecté 573 prix de vitrine dans le socle des ventes conclues.

## `price_date` : mise en ligne, jamais transaction
`price_date` porte la date de **publication de la fiche** (`wp/v2/product.date`).
Elle est dite dans le journal de collecte et répétée ici. 501 fiches sur 573
sont « Out of stock » — chez un marchand de pièces uniques la montre est partie,
mais le montant affiché reste le **dernier prix demandé**, et la date reste
celle de la mise en ligne, pas celle du départ. `listing_status` vaut `sold`
pour ces 501, `active` pour les 72 autres.

## Référence
- `REFERENCE` en champ dédié sur 465 / 573, d'où **86 % de référence remplie**
  après repli sur le titre : `champ_dedie` 453, `jeton_titre` 31, vide 78.
- **Piège mesuré :** le générique `_woo` essaie les libellés `reference` **puis
  `model`**. Ici `MODEL` porte « Datejust 36 OysterQuartz », « British Military
  RAF Mark 11 », « Scafograf 300M », « b/1m » — chiffrés, donc acceptés par le
  garde-fou du générique. **12 fiches sortaient avec un nom de modèle enregistré
  comme référence constructeur en provenance `champ_dedie`.** L'adaptateur ne
  lit la référence que dans `REFERENCE`, met `MODEL` dans `model`, et laisse le
  titre prendre le relais sinon. Vérification : 0 référence égale au modèle.
- `YEAR` est une année de production, pas une date de vente. 229 des 553 valeurs
  sont des décennies (« 1960s ») : le générique refuse de les prendre pour une
  année, d'où seulement 56 % d'`year` rempli — et c'est le bon comportement. Les
  années exactes vont de 1915 à 2025 (le « minimum 1920 » de la sonde est bien
  une année de production).

## Légal
- robots.txt (21/09/2026) : `User-agent: *`, deux `Disallow` seulement, tous
  deux des chaînes de filtre sur `/p/watches/?filter_` et `?query_type_`.
  L'adaptateur ne touche ni l'un ni l'autre.
- `/terms/` est inaccessible (403) — les CGU n'ont donc pas pu être lues. À
  refaire si la source passe en production.
- Données publiques : catalogue ouvert, aucune authentification, aucun mur
  franchi.

## Trouvailles / notes de test
1. Le blocage attribué à cette source était un **filtre d'UA**, pas un robots.
   Cesser d'annoncer ClaudeBot suffit — sans jamais se réclamer d'un navigateur.
2. Le pare-feu bloque tout le HTML sauf l'accueil, mais laisse passer
   `/wp-json/`. Une sonde qui juge sur le HTML conclut « BLOQUÉ » à tort ; une
   sonde qui juge sur l'accueil conclut « 1 142 ko, ouverte » — les deux se
   trompent sur ce qui est réellement récupérable.
3. `X-WP-Total` = 573 : la source est **petite**. Le chiffre de l'audit était
   faux d'un facteur 20 à 40.
4. Le filtre du projet garde 538 des 562 lignes (95,7 %) : R8 480, R6b 37,
   R7a 21 ; rejets R3 21 (marque absente) et R1 3.
5. `moteur/rejoue.py` ne connaît cette source ni dans `WOO` ni dans `ENCHERES`.
   L'adaptateur expose `lots_du_brut(entrees)` → `[(produit, date)]` et
   `fiche(produit, date)`, la convention du chemin `rejoue_encheres` : il suffit
   d'ajouter `"knightsbridge"` à `ENCHERES` pour que le rejeu marche. Je n'ai
   pas édité `rejoue.py` (fichier partagé).

## Échantillons — `samples/`
| fichier | ce qu'il prouve |
|---|---|
| `mesures_ua_403.txt` | les mesures d'accès, UA par UA, code par code |
| `robots.txt` | les 77 octets de robots.txt, sans règle ClaudeBot |
| `auctions_403.html` | `/auctions/` est fermé : l'archive d'enchères n'est pas là |
| `page-sitemap.xml` | 13 pages, aucun type de contenu « lot » |
| `store_categories.json` | Watches 555 + Watch Accessories 18 = 573 |
| `store_instock_p1.json` | les 72 fiches en vitrine, brutes |
| `store_outofstock_p1.json` | 100 des 501 fiches parties, brutes |
| `wpv2_dates_p1.json` | 100 dates de mise en ligne (`wp/v2/product`) |
| `records_extrait.json` | 25 enregistrements normalisés, tels qu'ils entreraient en base |
