# Everest Horology

Reconnaissance du 21/09/2026. **Verdict : pas d'adaptateur. Source à retirer du
registre.** Le marchand ne vend aucune montre — il fabrique des bracelets pour
Rolex. Mesuré sur son catalogue entier, pas déduit de son nom de domaine.

## Identité
- **Source :** Everest Horology Products, LLC · **URL :** <https://everestbands.com/>
  (sert sur `www.everestbands.com`)
- **Type :** fabricant / détaillant d'accessoires — *pas* un marchand de montres
- **Statut :** abandonné — mesuré, documenté, à désinscrire du registre
- **id / slug proposés à la sonde :** `everest` / `everest` — non créés

## Accès
- Shopify `/products.json`, public, sans compte, sans JavaScript. Mécanisme
  identique à Berry's ou Craft & Tailored : l'adaptateur aurait tenu en dix
  lignes. Ce n'est pas la faisabilité qui bloque, c'est le contenu.
- **robots.txt (lu le 21/09/2026, `samples/robots.txt`)** : `User-agent: *` /
  `Allow: /`. `/products.json` n'est pas visé. Sont interdits `/cart.js`,
  `/recommendations/products`, `/services`, `/sf_*`, `/checkout*`,
  `/collections/*sort_by*`. Rien qui gêne une collecte de catalogue.
  Le fichier ajoute une consigne explicite aux agents : le paiement et la
  commande passent par UCP/MCP avec approbation humaine, jamais en script.
  Hors de notre périmètre — on ne lit qu'un catalogue public.
- Pas de rate limit rencontré. 4 requêtes au total, pause 2 s, aucun 429/403.
- UA `utils.HEADERS` (ClaudeBot) accepté du premier coup, HTTP 200.

## Format de la data
- 4 requêtes ont épuisé la source : **page 1 = 248 produits, page 2 = 0**.
  Le catalogue entier tient dans `samples/products_page1.json`. Ce n'est pas un
  échantillon, c'est le tout.
- Champs Shopify habituels (title, vendor, product_type, variants[].price,
  variants[].sku, published_at, body_html). Prix demandé en USD avec
  `currency=USD&country=US`.
- **Aucune date de transaction.** `published_at` = mise en ligne de la fiche.
- Profondeur datée : nulle. L'« année min 1911 » vue par la sonde le 21/09 est
  un faux positif : c'est l'année citée dans le texte marketing des pages, pas
  la date d'un prix.

## Ce que vend réellement la boutique — la mesure

`product_type` déclaré par le marchand sur ses 248 fiches
(`samples/mesure_filtre.txt`, rejouable par `explore.py` sans réseau) :

| n | product_type | nature |
|---|---|---|
| 55 | Rubber Bands | bracelet |
| 55 | *(vide)* | bracelets Oyster, boucles déployantes, maillons, un couteau suisse, un mug |
| 50 | Leather Bands | bracelet |
| 30 | Spring Bars | barrettes à ressort |
| 14 | Nylon Bands | bracelet |
| 9 | Universal Leather Bands | bracelet |
| 8 | Watch Pouch | pochette |
| 8 | Tool Kits | outillage |
| 6 | Watch Buckle | boucle |
| 3 | Watch Pouches / 3 Watch Rolls / 2 Watch Accessories / 1 Bracelet Links / 1 Universal Rubber Bands / 1 Watch Boxes / 1 Watch Portfolios / 1 Gift Cards | rangement, accessoires, carte cadeau |

**Montres : 0 sur 248.** Les 55 fiches sans `product_type` ont été relues une
par une : bracelets Oyster ($595), boucles déployantes ($395), maillons ($55–65),
plus un couteau Victorinox co-marqué et un mug isotherme. Aucune montre.

Prix pratiqués : 55 à 595 USD. Un marché de montres ne se compose pas de lignes
à 55 USD ; leur seule présence dans `price_points.jsonl` fausserait toute
statistique de niveau de prix.

## Pourquoi la source serait NUISIBLE, et non simplement inutile

Le soupçon de départ était que le filtre nous protégerait par R5/R6. **La mesure
dit autre chose, et c'est plus grave.** Filtre appelé exactement comme
`moteur/run.py` l'appelle (marque + catégorie publiée) sur les 246 fiches
normalisables :

| verdict / règle | n |
|---|---|
| REJETER / R0 (catégorie publiée non horlogère) | 169 |
| QUARANTAINE / R7a | 50 |
| REJETER / R3 (aucune marque reconnue) | 21 |
| **GARDER / R7a** | **4** |
| **GARDER / R8** | **1** |
| REJETER / R1 | 1 |

**R5 ne se déclenche pas une seule fois sur les 248 fiches.** Le garde-fou réel
est R0 — la catégorie que le marchand publie lui-même — et il laisse passer
55 accessoires : 5 en GARDER, 50 en quarantaine.

Trois mécanismes précis, tous mesurés :

1. **La catégorie du marchand retourne le filtre contre nous.** `categorie()`
   reconnaît une montre dès que le libellé contient `watch`. Or ce marchand
   nomme ses rayons *Watch Buckle*, *Watch Pouch*, *Watch Rolls*, *Watch Boxes*,
   *Watch Accessories*, *Watch Portfolios*. Pour le filtre, `Watch Buckle` = True
   = montre, donc `token` est vrai, donc R7a conclut GARDER au lieu de mettre en
   quarantaine. Les 4 GARDER/R7a sont **tous** des `Watch Buckle` : la boucle
   déployante à 395 USD passe **parce que** la boutique a écrit « watch » dans le
   nom de son rayon d'accessoires. Le 5ᵉ GARDER est un couteau suisse
   co-marqué (R8, aucun marqueur d'accessoire horloger dans son titre).

2. **Les références sont de vraies références Rolex.** 245 fiches sur 246
   portent une « référence » (168 `sku`, 60 `jeton_titre`, 12 `extrait_titre`,
   5 `extrait_description`). Les titres sont bâtis sur la référence de la montre
   destinataire : *Everest Deployant Buckle for Rolex Oyster Bracelet – Daytona
   116500*. Les quatre lignes qui entreraient en base porteraient donc, avec
   `reference` renseignée et `price_amount = 395 USD` :
   **116500** et **116520** (Daytona), **16570** (Explorer II), **14270**
   (Explorer I). Le champ `brand` dirait « Everest Bands », mais une base de prix
   se recoupe sur la **référence** : on attacherait 395 USD à une Daytona 116500
   qui se négocie deux ordres de grandeur au-dessus. C'est le cas irréductible
   L1 — non plus comme limite théorique, mais comme ligne qui franchit
   réellement le filtre.

3. **43 fausses ventes.** Chez un fabricant de série, `available=false` est une
   rupture de stock : le même bracelet reviendra. Le moteur Shopify en déduit
   `sold` (paramètre `indisponible`) : 43 des 246 fiches sortent en
   `price_nature=sold`, la nature la plus rare et la plus précieuse du dossier.
   On fabriquerait 43 transactions qui n'ont pas eu lieu.

La source est déjà connue du dossier par effet de bord : `data/price_points.jsonl`
contient des bracelets **Everest** revendus par Bulang & Sons, tous étiquetés
marque `Everest Bands` et affectés de la référence Rolex **16800** lue dans leur
description (`filter_rule: R0`, rejetés). Le mécanisme de contamination est donc
attesté deux fois, sur deux sources différentes.

## Légal
- Catalogue public, aucune authentification, aucune protection contournée.
- robots.txt permissif sur le catalogue ; les consignes agent du fichier portent
  sur l'achat, jamais sollicité ici.

## Conclusion
- **Aucun adaptateur écrit.** `moteur/sources/everest.py` n'existe pas et ne
  doit pas exister. `moteur/sources/__init__.py` n'a pas été touché.
- **À retirer du registre** — feuille « Toutes les sources » du classeur que lit
  `moteur/sonde.py --registre` (`WP/output/referentiels/DataSources.xlsx`, absent
  de l'arbre de travail actuel ; la copie archivée est
  `WP/_archive/2026-08-campagne/DataSources.xlsx`, à ne pas toucher). Retrait à
  faire par le détenteur du registre, pas ici. Sans cela la sonde continuera de
  la noter 78/100 à chaque campagne et un futur agent refera ce travail. Motif à
  inscrire : *fabricant d'accessoires, 0 montre sur 248 fiches, mesuré le
  21/09/2026*.
- **Enseignement réutilisable pour le filtre** — à verser au dossier du filtre,
  pas corrigé ici (`moteur/filtre.py` est partagé) : `categorie()` traite
  `Watch Buckle`, `Watch Pouch`, `Watch Roll`, `Watch Box` comme des montres.
  Toute boutique d'accessoires nommant ainsi ses rayons produit des GARDER. Un
  test rouge du banc devrait le figer : `('Everest Deployant Buckle for Rolex
  Oyster Bracelet – Daytona 116500', 'Watch Buckle') -> REJETER`.

## Échantillons
- `samples/robots.txt` — robots.txt intégral, lu le 21/09/2026
- `samples/products_page1.json` — **catalogue entier**, 248 fiches, brut non retouché
- `samples/products_page2_vide.json` — la preuve que la page 2 est vide
- `samples/mesure_filtre.txt` — sortie de `explore.py` : composition + verdicts
- `explore.py` — rejoue toute la décision depuis les échantillons, sans réseau
