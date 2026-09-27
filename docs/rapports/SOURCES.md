# Les sources

**Généré le 2026-08-11** par `python moteur/inventaire.py`.
Ne pas éditer à la main — ce fichier est écrasé. Pour corriger un fait,
modifier `labo/moteur/catalogue.py`, puis relancer la commande.

> Trois sources sont mortes en trois semaines (LiveAuctioneers, Antiquorum, WatchBox), dont deux faisaient partie des cinq sources validees en juillet. Ce marche se ferme progressivement : les verdicts ci-dessous ont une date de peremption, et les accords commerciaux prennent de la valeur avec le temps.

## 1. Branchées sur le moteur

Elles collectent aujourd'hui. Le volume est ce qui est **réellement en base**.

| Source | Catégorie | Nature | En base | Accès | État |
|---|---|---|---:|---|---|
| Christie's | auction | realise | 1356 | API JSON interne (discoverywebsite) | active |
| Craft & Tailored | dealer | demande | 1000 | Shopify products.json | active |
| WatchRecon | community | demande | 989 | HTML structure (.galleryItemContainer) | active |
| LiveAuctioneers | aggregator | realise | 0 | window.__data (price guide) | **bloquée** |
| Bezel | marketplace | demande | 0 | API interne /api/marketplace/listings + jointure catalogue | **bloquée** |

**3 345 prix** collectés au total.

## 2. Prouvées, pas encore branchées

Validées par récupération réelle de données — échantillons dans `labo/preuves/`.
Le volume est ce qui est **atteignable**, pas ce qui est collecté.

| Source | Catégorie | Nature | Atteignable | Historique | Accès |
|---|---|---|---:|---|---|
| **EveryWatch** | agregateur | realise | 218 000 | 2,5 ans glissants | endpoint JSON Next.js, auctionType=result |
| **Bezel — API interne** | marketplace | demande | 32 620 | releve | /api/marketplace/listings?active=true |
| **Hodinkee Shop** | marchand | demande | 18 946 | date | Shopify /products.json |
| **Wanna Buy A Watch** | marchand | vendu | 6 477 | date | WooCommerce Store API |
| **Loupe This** | encheres en ligne | realise | 4 145 | 2021 -> 2026 | API JSON publique, sans authentification |
| **Watchtrader** | marchand | demande | 3 916 | date | WooCommerce Store API |
| **Monaco Legend** | maison de ventes | realise | 3 738 | 2019 -> 2026 | JSON-LD + attributs data- des pages de vente |
| **Menta Watches** | marchand | demande | 2 882 | date | WooCommerce Store API |
| **Amsterdam Vintage Watches** | marchand | demande | 2 482 | date | WooCommerce Store API |

Points d'attention :

- **EveryWatch** — mur payant avant 2024 ; devise convertie, pas native
- **Bezel — API interne** — remplace la voie sitemap actuelle, 366x plus de volume
- **Hodinkee Shop** — 94 % des SKU sont des codes internes — extraire la reference du titre
- **Wanna Buy A Watch** — l'archive conserve les prix ET la categorie SOLD — vrai prix vendu
- **Loupe This** — robots le plus permissif du dossier ; specs a 100 %
- **Watchtrader** — meilleure completude de specs du projet (~100 % sur tout)
- **Monaco Legend** — deux devises : EUR (Monaco) et CHF (Geneve)
- **Menta Watches** — prix purges de l'archive ; Crawl-delay 10
- **Amsterdam Vintage Watches** — 33 % de « prix sur demande » ; archive sans prix

## 3. À démarcher

Fermées techniquement. Aucune quantité de travail ne les ouvre : il faut
un accord commercial ou un accès officiel.

### Priorité 1 — le type de prix qui manque totalement

| Source | Ce qu'on demande | Blocage |
|---|---|---|
| **WatchCharts** | licence de donnees ou API d'indices | Cloudflare, blocage total |
| **Chrono24 — ChronoPulse** | API ou partenariat data | Cloudflare, blocage total |

### Priorité 2 — accès officiels à obtenir

| Source | Ce qu'on demande | Blocage |
|---|---|---|
| **eBay** | API Marketplace Insights (prix vendus) | acces restreint sur approbation ; nos cles production sont bloquees par une mise en conformite a realiser |
| **EveryWatch — historique** | l'anteriorite avant 2024 | mur payant ; 2,5 ans glissants sont gratuits |
| **Reddit** | cle d'API officielle | robots interdit tout le domaine |

### Priorité 3 — enchères et archives fermées

| Source | Ce qu'on demande | Blocage |
|---|---|---|
| **Barnebys** | flux licencie d'encheres | robots interdit tout le site, permission ecrite exigee |
| **Phillips** | resultats de ventes | 403 par URL ; la page listant les ventes montres est interdite |
| **Sotheby's** | resultats de ventes | la seule route portant les donnees est interdite par robots |
| **the-saleroom** | resultats multi-maisons | pare-feu applicatif AWS |
| **Invaluable** | prix realises | joignable, mais le seul chemin vers les resultats est interdit |
| **LiveAuctioneers** | prix realises dates | anti-bot Incapsula installe vers le 08/2026 — marchait le 01/08 |

### Priorité 4 — marques (prix neuf)

| Source | Ce qu'on demande | Blocage |
|---|---|---|
| **Patek Philippe** | acces au tarif catalogue | CONTROLE DU 11/08 : les 266 fiches produit sont accessibles mais ne portent AUCUN prix en HTTP simple. Le tarif est derriere un bouton « Display the product price ». Une campagne anterieure affirmait l'inverse — c'etait faux, elle avait pris des URL d'images pour des prix. |
| **Grand Seiko** | acces au tarif catalogue | CONTROLE DU 11/08 : aucun prix sur la page collection ni sur la fiche produit, quel que soit le marche teste. |
| **Rolex, Omega, Cartier, TAG Heuer, IWC, Tudor** | tarif catalogue | protection Akamai |
| **Audemars Piguet** | tarif catalogue | endpoint de prix verrouille cote serveur |

### Priorité 5 — forums

| Source | Ce qu'on demande | Blocage |
|---|---|---|
| **WatchUSeek** | acces aux archives | epreuve de calcul anti-robot |
| **WatchProSite** | acces aux archives | Cloudflare Turnstile |
| **Rolex Forums** | acces aux archives | challenge JS Cloudflare |
| **TimeZone** | acces aux archives | robots interdit tout |

Les forums ont un impact limité : **WatchRecon les agrège déjà** et nous est
accessible. Les démarcher n'apporterait que de la profondeur, pas du volume.

## 4. Écartées

| Source | Raison |
|---|---|
| WatchAnalytics | le site a ferme — sert une page d'arret d'activite |
| Antiquorum | le site a disparu — redirige vers une vitrine sans archives |
| WatchBox / 1916 Company | eteint — plus aucun catalogue en ligne |
| Chronext | SPA, catalogue non enumerable ; quelques centaines de fiches au mieux |
| 1stDibs | annonces en JavaScript ; 29 % de completude, remplace par Bezel |
| Lot-Art | robots.txt interdit explicitement notre outil — a evaluer autrement |

## 5. Bac à sable

`labo/essais/` contient **31 dossiers** de sources explorées.
Un dossier n'est pas un verdict : c'est une piste ouverte un jour.

<details><summary>Voir la liste</summary>

`aguttes` · `antiquorum` · `artcurial` · `barnebys` · `bezel` · `bobs-watches` · `bonhams` · `christies` · `chronext` · `chrono24` · `crown-and-caliber` · `dorotheum` · `dr-crott` · `ebay` · `eu_auctions` · `everywatch` · `fellows` · `heritage` · `ineichen` · `invaluable` · `koller` · `liveauctioneers` · `monaco-legend` · `phillips` · `sothebys` · `the-saleroom` · `watchbox-1916` · `watchcharts` · `watches-of-knightsbridge` · `watchfinder` · `watchrecon`

</details>

Dont **15** sans verdict enregistré ni dans le catalogue ni dans le moteur — à trancher ou à archiver :

`aguttes` · `artcurial` · `bobs-watches` · `bonhams` · `crown-and-caliber` · `dorotheum` · `dr-crott` · `eu_auctions` · `fellows` · `heritage` · `ineichen` · `koller` · `watchbox-1916` · `watches-of-knightsbridge` · `watchfinder`

---

Le registre complet des 210 sources recensées reste dans
`output/referentiels/DataSources.xlsx` — c'est le document de travail partagé
avec les associés, avec ses colonnes « assigné à » et « feedback ».
Ce fichier-ci est la vue technique : ce qui marche, ce qui est prouvé, ce qui est fermé.
