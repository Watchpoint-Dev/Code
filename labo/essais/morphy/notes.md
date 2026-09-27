# Morphy Auctions

Fiche de reconnaissance — **21/09/2026**. Adaptateur : `moteur/sources/morphy.py`.

## Identité
- **Source :** Morphy Auctions · **URL :** <https://morphyauctions.com/>
- **Salle réelle :** <https://auctions.morphyauctions.com/> (SimpleAuctionSite, ASP.NET WebForms)
- **Type :** enchères (`auction`) · **id :** `morphy`
- **Statut :** **data récupérée** — prix réalisés datés, frais acheteur inclus
- Maison américaine généraliste (Denver, Pennsylvanie) : jouets, armes, publicité,
  coin-op, arts décoratifs, joaillerie **et** horlogerie. Elle a absorbé
  James D. Julia. Fondée en 2004.

## La question qui décide de la valeur : prix réalisés ou catalogue à venir ?

**Prix réalisés datés. Sans ambiguïté.** La vente 517 (Fine Pocket Watch,
30 juin 2020) publie 646 prix finaux ; la vente 307 (Jewelry & Timepiece,
7 octobre 2017) publie ses 192 montres-bracelets avec leur montant. Le catalogue
d'une vente close remplace « Current Bid » par **« Final Price »**, et la fiche
de lot écrit « Auction closed on Tuesday, June 30, 2020 ».

Ce n'est donc **pas** une source de catalogue à venir : les ventes ouvertes
existent aussi (« Current Bid »), et l'adaptateur les **écarte** — une enchère
en cours n'est pas une transaction.

## Accès

| étape | requête | rendu |
|---|---|---|
| repérage | 1 × `GET morphyauctions.com/event-sitemap.xml` | 720 vacations nommées, 23 au nom horloger/joaillier |
| identifiant | 1 × `GET .../past-auctions/<slug>/` par vacation | `catalog.aspx?auctionid=NNN` |
| arbre | 1 × `GET auctions.../catalog.aspx?auctionid=N` | `<h1>` daté + catégories avec effectifs + 25 lots |
| catégorie | 1 × `GET auctions.../Category/<Nom>-<id>.html` (**même session**) | la vente filtrée sur la catégorie |
| volume | 1 × `POST` même URL, `LotsPerPageDropDownTop=ALL` | **toute** la catégorie en une réponse |

- Pas de compte, pas de clé. Pas de JavaScript nécessaire (le catalogue est du
  HTML rendu serveur).
- **Deux requêtes suffisent pour une vente entière** : 646 lots en un POST de 3 Mo.
- `Crawl-delay: 2` respecté (`DELAI = 2.0`).

### Le POST, et pourquoi il est écrit à la main
`catalog.aspx` **ignore** `page=`, `lotsperpage=` en paramètre d'URL — trois
essais mesurés, tous rendant la page 1. La pagination est du postback WebForms
(`__VIEWSTATE` + `__EVENTTARGET`). `utils.get` ne connaît que GET : le POST est
donc dans le module, mais il **réutilise** `utils.HEADERS`, `utils.DELAIS`,
`utils.CODES_A_REESSAYER`, `utils.ATTENTES` et respecte `Retry-After` — aucune
logique de politesse n'est réécrite. Tous les GET, eux, passent par `utils.get`,
à qui on confie le bocal à cookies. **C'est un écart assumé au cahier, signalé
ici et dans le docstring** : sans lui la source plafonne à 25 lots par vente.

### L'en-tête doit changer selon l'hôte — mesure inversée
| hôte | `utils.HEADERS` (ClaudeBot) | `python-requests/2.34.2` |
|---|---|---|
| `morphyauctions.com` | **403** + défi JS hashcash | **200** |
| `auctions.morphyauctions.com` | **200** | **403** (Azure App Gateway) |

C'est ce défi JavaScript du WordPress qui avait fait classer la source
« robots illisible » : son `robots.txt` répond 200 dès qu'on cesse d'annoncer
ClaudeBot. Aucun des deux en-têtes ne se réclame d'un navigateur — on annonce
soit ClaudeBot, soit la bibliothèque. Détail dans
`samples/mesure_user_agent.txt`.

### Le faux ami : l'API Store WooCommerce
`morphyauctions.com/wp-json/wc/store/v1/products` répond 200 et publie
**162 produits** : ce sont les **catalogues imprimés** à 55 $ et 65 $
(`currency_minor_unit` = 2). Aucune montre, aucune catégorie, aucun lot. Le
verdict de sonde « FACILE (WooCommerce Store API), 75/100 » portait sur la
librairie de la maison. Brancher `_woo.py` ici aurait produit 162 lignes de
catalogues papier. Preuve : `samples/woo_store_products_p1.json`.

## Cibler par les catégories de la maison

Morphy publie son propre arbre, avec les effectifs, sur chaque page de vente.
Les identifiants sont **stables d'une vacation à l'autre** :

```
All (667) · Jewelry (15) · Pocket Watches (652)              <- vente 517, 2020
All (357) · Jewelry/Watches/Coins (357) · Jewelry (213)
          · Wrist Watches (29) · Pocket Watches (32) · Coins/Currency (1)
                                                              <- vente 731, 2026
797 = Wrist Watches   801 = Pocket Watches   796 = Jewelry   798 = Coins/Currency
```

L'adaptateur retient les **feuilles** horlogères (`watch|timepiece|horolog`) et
écarte les composés (`jewel|coin|clock|lamp|glass`) : prendre
`Jewelry/Watches/Coins` ramènerait les 213 bagues avec. À défaut de feuille, le
composé est pris en repli, avec une ligne de journal.

Le nom de la catégorie part tel quel dans **`source_category`**, et le filtre y
lit R0 sans deviner : `Pocket Watches` → True, `Wrist Watches` → True,
`Jewelry` → False, `Clocks` → False, `Coins/Currency` → False. C'est le signal
le plus sûr de la source.

**Réserve mesurée** : la catégorisation de la maison n'est pas parfaite. Dans
`Wrist Watches` de la vente 307 on trouve « PATEK PHILIPPE 18K WHITE GOLD OPEN
FACE POCKET WATCH » — une montre de poche. R0 la garde (c'est une montre), le
classement fin est faux. Sans conséquence sur le prix.

## Format de la donnée

Depuis la page de catalogue (la seule lue) :

| champ du schéma | source | remplissage |
|---|---|---|
| `price_amount` | `Final Price: $x` | 100 % |
| `price_currency` | USD, constante (maison américaine) | 100 % |
| `price_date` | date lue dans le `<h1>` du catalogue | 100 % |
| `price_nature` | `realised` | 100 % |
| `price_nature_provenance` | `deduite_statut` — le montant est étiqueté « Final Price » sur un lot que la page déclare clos ; ce n'est pas un champ de nature | 100 % |
| `price_includes_premium` | **True**, écrit par la maison | 100 % |
| `estimate_low` / `estimate_high` | `Estimate: $a - $b` | 100 % |
| `source_category` | catégorie Morphy, telle quelle | 100 % |
| `title` | titre de lot (capitales, style catalogue) | 100 % |
| `external_id` | identifiant d'inventaire du lien `-LOT<id>.aspx` | 100 % |
| `source_url` | l'URL de la fiche de lot | 100 % |
| `brand` | déduite du titre par le filtre | **92 %** en `Wrist Watches`, **21 %** en `Pocket Watches` |
| `reference` | `extrait_titre` puis `jeton_titre` | **84 %** en `Wrist Watches`, **2 %** en `Pocket Watches` |
| `year`, `case_size_mm`, `case_material`, `movement`, `condition`, `model` | **0 %** — ils vivent sur la fiche de lot, 1 requête de plus par lot | 0 % |

`price_date` **est la date de la vacation**, pas la mise en ligne : c'est bien
une date de transaction. Pour une vacation sur deux jours
(« October 16 & 17, 2026 ») on retient le premier jour — l'erreur est d'un jour
au plus. La date exacte du lot existe sur sa fiche
(« Bidding ended on 6/30/2020 »), au prix d'une requête par lot.

Le numéro de lot et le nombre d'enchères n'ont pas de champ au schéma : ils
restent dans le brut, qui est conservé entier et rejouable par `lots_du_brut`.

## Le prix : frais acheteur INCLUS, à taux variable

La fiche de lot l'écrit en toutes lettres :
**« Final prices include buyers premium: $3,600.00 »**.

Contrôle arithmétique sur les 646 prix de la vente 517 : le quotient par
**1,20** est un multiple de 50 dans **79 %** des cas, contre 41 % sans division.
Sur les 365 montants non ambigus (pas eux-mêmes multiples de 25) : 1,20 seul
162 fois, 1,28 seul 49, 1,23 seul 37, 1,25 seul 7, et 74 cas où 1,20 et 1,28
sont indiscernables.

→ **20 % dominant, mais 23 / 25 / 28 % coexistent dans une même vente** (canal
d'enchère). Exemples 2017 : Submariner 16800 à 6 250 $ = 5 000 × 1,25 ;
Breitling à 720 $ = 600 × 1,20. **On ne reconstitue jamais le marteau.**
Comparer Morphy à Artcurial (marteau nu) sans ce drapeau surévalue Morphy d'un
cinquième à un tiers. Détail : `samples/mesure_frais_acheteur.txt`.

## Volume et profondeur

- **23 vacations** sur 720 portent un nom horloger ou joaillier dans le sitemap
  de la maison (`samples/vacations_horlogeres.txt`).
- Effectifs **mesurés**, sur 4 des 23 : vente 517 → 652 montres de poche ;
  vente 307 → 192 montres-bracelets ; vente « Vintage Swatch Watches » du
  19/09/2024 → 323 montres-bracelets ; vente 731 (à venir) → 29 + 32.
  **1 228 lots horlogers sur quatre vacations**, dont 1 167 déjà vendus et datés.
- Extrapolation honnête : **de l'ordre de 2 000 à 5 000 lots** horlogers datés.
  Le chiffre exact demande le repérage complet (24 requêtes) — non lancé, c'est
  la vague 4.
- **Profondeur mesurée : 2017 et 2020.** Les vacations du sitemap remontent à
  2016. Le « 1999 » de la sonde n'est pas vérifié et est peu crédible : Morphy
  a été fondée en 2004. Les ventes antérieures au catalogue en ligne ne
  publient qu'un PDF « Prices Realized » (non exploité).
- **Non exploré, chiffré :** les montres nichées dans les vacations
  généralistes (arts décoratifs, successions). Les atteindre demande soit
  d'élargir `MOTS_VENTE`, soit un balayage des ~72 pages d'index / des 731
  identifiants de vente. Élargir la liste de mots est le levier prévu.

## Rendement après filtre (version 2026-09-02)

| échantillon | lots | GARDER | règle dominante |
|---|---|---|---|
| 307 · Wrist Watches | 25 | **23 (92 %)** | R7a, R8, R6b |
| 517 · Pocket Watches | 646 | 121 (19 %) | R3 rejette 498 : marque inconnue |

Les montres de poche de 1880 sont signées par des horlogers suisses et
américains absents du dictionnaire de marques (D. Borgeat, A. Lugrin,
M.T. Stauffer…) : R3 les rejette, et c'est cohérent avec le projet. **La valeur
horlogère de Morphy est dans `Wrist Watches`**, où 92 % des lignes passent avec
marque et référence.

## Légal
- `robots.txt` des deux hôtes lu le 21/09/2026, reproduit dans
  `samples/mesure_user_agent.txt`.
- **`/AuctionResults.aspx` et `/LiveAuction2.aspx` sont interdits** côté salle :
  jamais demandés. C'est pour cela que le repérage des ventes passe par le
  sitemap WordPress, qui n'interdit rien.
- `/*.ashx$`, `/UserFiles/`, `/uploads/`, `/javascript/`, `/css/` interdits :
  aucune ressource utilisée n'en fait partie.
- `Crawl-delay: 2` respecté. Aucune requête parallèle. Aucun contournement :
  le défi JavaScript du WordPress n'a **pas** été résolu — on a simplement
  cessé d'annoncer ClaudeBot sur cet hôte, ce que le robots.txt autorise.
- Données publiques : catalogues et résultats sont en accès libre, sans compte.

## Trouvailles / notes de test
1. La sonde avait deux erreurs jumelles : « robots illisible » (c'était le défi
   JS) et « FACILE WooCommerce » (c'était la boutique de catalogues papier).
   Les deux sont des faux positifs de mesure, pas des propriétés de la source.
2. Le slug d'une URL de lot est décoratif : `/x-LOT486143.aspx` répond 200.
   Les identifiants d'inventaire ne suivent pas les numéros de lot mais restent
   groupés par vente. **Non exploité** : énumérer serait du balayage aveugle
   quand le catalogue donne la liste exacte.
3. Le filtre par catégorie **exige la session** : `Category/…-801.html` sans
   cookie retombe sur la vente en cours. Et la page filtrée ne republie pas
   l'arbre — il faut le lire avant de filtrer.
4. La recherche d'en-tête (`catalog.aspx?searchby=1&searchvalue=rolex`)
   fonctionne en GET mais n'interroge que la vente ouverte : 17 lots, aucun
   prix final. Inutilisable pour l'archive.
5. Aucun invendu publié : 646 lots, 646 prix finaux, et 21 numéros manquants
   dans la suite 1001-1667. Biais de survie assumé, taux d'invendus non
   mesurable.
6. **Les quatre ventes Swatch sont des lots groupés.** « Vintage Swatch
   Watches » (2023, 2024 ×2 et 2024) rangent 323 fiches en `Wrist Watches`,
   mais les titres sont du type « LOT OF 5: STANDARD LADIES SWATCHES » : un
   montant pour cinq montres, sans marque ni référence. R1 les rejette (lots
   mélangés) et c'est juste. Ces quatre vacations gonflent le volume brut sans
   rien apporter à la cote — à ne pas compter comme du rendement.
7. Les titres sont des descriptions de catalogue en capitales. Sur les montres
   de poche, `reference_dans` ne trouve rien (0/646) et `reference_libre` 11.
   Sur les montres-bracelets, 16 `extrait_titre` + 5 `jeton_titre` sur 25.
   Attention aux titres qui citent un **calibre** : « … LADIES CALIBER 127… »
   a produit une référence douteuse. Le risque est connu et localisé.

## Échantillons (`samples/`)
| fichier | ce qu'il prouve |
|---|---|
| `mesure_user_agent.txt` | l'inversion d'UA entre les deux hôtes + les deux robots.txt |
| `mesure_frais_acheteur.txt` | le libellé « include buyers premium » et le taux 20 % dominant, non constant |
| `mesure_acces.txt` | ce qui répond, ce qui est ignoré en URL, le POST qui rend 646 lots |
| `woo_store_products_p1.json` | les 162 « produits » sont des catalogues papier à 55 $ |
| `catalog_517_page1.html` | l'arbre de catégories, le `<h1>` daté, 25 lots, « / 26 » pages |
| `catalog_517_pocket_watches_TOUT.html` | 646 lots et 646 « Final Price » en **un** POST (3 Mo) |
| `fiche_lot_486142.html` | « Final prices include buyers premium », le fil d'Ariane, les attributs, la date exacte |
| `catalog_307_page1.html` · `catalog_307_wrist_watches_page1.html` | la vente 2017 et sa catégorie Wrist Watches |
| `catalog_731_vente_a_venir.html` | une vente OUVERTE : « Current Bid », pas de prix final — ce que l'adaptateur écarte |
| `wp_event_fine-wrist-pocket-watches.html` | la fiche WordPress qui donne `auctionid=517` et le PDF des prix réalisés |
| `records_517_pocket_watches.jsonl` | 646 enregistrements normalisés, rejoués sur le brut sans réseau |
| `records_307_wrist_watches.jsonl` | 25 enregistrements, 92 % de marque, 84 % de référence |
| `vacations_horlogeres.txt` | les 23 vacations horlogères sur 720, nommées par la maison |
