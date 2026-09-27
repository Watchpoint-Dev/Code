# Watchpoint — récapitulatif complet du projet (26/09/2026)

Document destiné à une IA à qui l'on demande de **proposer une structure cible**
(organisation des dossiers, découpage front / back / data / tests, contrat de
données, base). Tout ce qui suit décrit l'existant, tel qu'il est sur le disque.

---

## 1. Le produit

Plateforme de **prix de montres** (marché secondaire : enchères, marchands,
marketplaces, prix neufs). Objectif : pour une montre donnée (marque + référence),
montrer l'historique de ses prix réels, leur nature, leur source, et à terme des
indices de marché (par marque, segment, type) et un indice de sentiment.

L'idée centrale : **un prix n'a de sens qu'avec sa nature, sa date, sa devise et
sa source.** Cinq natures de prix :

| Nature | Sens | Lignes en base |
|---|---|---:|
| `realised` | prix d'adjudication (maison de ventes) | 67 349 |
| `sold` | vendu (marchand / marketplace) | 41 361 |
| `asking` | prix demandé (annonce en cours) | 84 109 |
| `msrp` | prix neuf catalogue | 6 106 |
| `estimate` | estimation avant vente | 2 732 |

Utilisateurs : pour l'instant l'équipe (quelques associés). Site privé, tout est
derrière authentification.

---

## 2. Organisation actuelle sur le disque

Racine : `~/Desktop/WP/`

```
WP/
├── README.md        point d'entrée (les 4 endroits, les commandes, l'état)
├── wp-3-main/       LE SITE — Next.js, dépôt git séparé, remote GitHub, déployé Vercel
├── labo/            LE MOTEUR DE DONNÉES — Python, dépôt git séparé, AUCUN remote
│   ├── moteur/      le code (≈ 30 scripts + sources/ avec 38 adaptateurs)
│   ├── filtres/     le filtre « est-ce une montre ? » (Excel → JSON)
│   ├── data/        les données (raw, normalized, cumul, manifestes, logs)
│   ├── essais/      bac à sable, un dossier par source testée (~15)
│   ├── preuves/     échantillons, robots.txt, pages de blocage archivées
│   └── shared/      venv Python + utils.py (requêtes polies, pause, robots)
├── notes/           brouillons + rapports GÉNÉRÉS (ETAT_DATA.md, PANORAMA.md…)
├── output/          livrables datés (CSV/Excel, présentations, référentiels)
└── _archive/        historique rangé par mois (2026-07, 2026-08, 2026-09)
```

Règles de rangement déjà en place :
- un seul document vivant par question, le reste part daté dans `_archive/AAAA-MM/`
- ce qui peut être généré ne s'écrit pas à la main (`ETAT_DATA.md`, `SOURCES.md`, `ETAT_CHAMPS.md`…)
- on ne travaille jamais dans `output/`

Trois dépôts git indépendants : `wp-3-main` (GitHub `Watchpoint-Dev/WPV3`,
branches `main` → prod et `dev` → preview), `labo` (local uniquement, jamais
poussé), `carnet` (privé). Le dossier personnel `~` est lui-même un dépôt git,
dont `WP/` apparaît comme non suivi — accident à nettoyer.

---

## 3. Front — `wp-3-main/`

### Stack
- **Next.js 16.2 (App Router)**, React 18, TypeScript 5.8
- **Tailwind 3** + **shadcn/ui** (Radix UI), lucide-react, recharts, sonner
- react-hook-form + zod, @tanstack/react-query (installé, peu ou pas utilisé)
- Auth : **Clerk** (`@clerk/nextjs` 7)
- Base : **Neon** (Postgres serverless, `@neondatabase/serverless`)
- Déploiement : **Vercel** (main = production, dev = preview)
- Origine : projet généré avec Lovable puis migré vers Next (reste `lovable-tagger` en devDep)

### Pages (`src/app/`)
| Route | Lignes | État |
|---|---:|---|
| `/marketplace` | 519 | écran complet sur données fictives (filtres, listings) |
| `/auctions` | 430 | écran complet sur données fictives |
| `/top-performers` | 256 | idem |
| `/watch/[watchid]` | 239 | fiche montre, graphique de tendance, données fictives |
| `/compare` | 230 | comparateur, données fictives |
| `/market-index` | 111 | indices par marque, fictifs |
| `/market-news` | 108 | actualités fictives |
| `/investment`, `/my-assets`, `/community` | 20 chacune | coquilles vides |
| `/sign-in`, `/sign-up` | — | Clerk, publiques |
| `api/auth/sync` (POST) | 42 | seule route API : synchronise l'utilisateur Clerk dans Neon |

Autres :
- `src/proxy.ts` : middleware Clerk, toutes les routes protégées sauf sign-in/up
- `src/app/components/` : `ui/` (shadcn + quelques composants maison : PageHeader,
  ContentCard, TrendAreaChart), `layout/` (AppLayout, AppSidebar), `auth/`
- `src/lib/` : `neon.ts` (client SQL), `clerk-neon-user.ts` (upsert utilisateur,
  crée la table à la volée), `dummy-data.ts` et `market-data.ts` (hydratent les JSON
  fictifs), `watch-insights.ts`, `flags.ts`, `utils.ts`

### Données du front : 100 % fictives
`src/data/dummy-data/` : JSON statiques importés directement dans les composants.
Modèle **relationnel normalisé par identifiants** :
- `marketplace/brands.json`, `models.json`, `watches.json`, `listings.json`
- `watches/watches.json`, `auctions/auctions.json`, `market-index/brand-indices.json`,
  `market-news/news.json`, `watch-insights/insights.json`
- `lookups/` : materials, dial-colors, movement-types, strap-types, conditions,
  availability-statuses, sellers, locations, segments

Exemple de listing fictif : `{ id, brandId: "br-rolex", modelId, reference:
"126610LN", price, currency: "USD", conditionId, year, caseSizeMm, materialId,
movementTypeId, dialColorId, strapTypeId, locationId, availabilityId, sellerId,
description, tags, featured }`.

**Ce modèle n'a rien à voir avec celui que produit le moteur** (section 5) :
le front attend des entités liées (marque → modèle → montre → annonce avec
lookups), le moteur produit une ligne plate par prix observé. Aucun contrat
entre les deux n'a été défini.

### Base Neon (réelle)
Une seule table : `public.app_users` (id, clerk_user_id unique, email, first_name,
last_name, image_url, created_at, updated_at, last_seen_at), créée par
`CREATE TABLE IF NOT EXISTS` au premier appel. Pas de migrations, pas d'outil de
schéma (ni Prisma, ni Drizzle), **pas de base de dev** : tester la base revient à
écrire en production.

---

## 4. Back

Il n'y a **pas de back applicatif** au sens API métier :
- une seule route (`/api/auth/sync`)
- aucune API qui sert des prix, des montres ou des indices
- aucune table de données de marché dans Neon

Le « back » réel aujourd'hui, c'est le moteur Python local (section 5), qui écrit
des fichiers JSONL sur le disque, sans lien avec Neon ni avec le site.

---

## 5. Moteur de données — `labo/`

### Stack
Python 3, `requests`, `beautifulsoup4`, `lxml`, `pandas` (venv dans `labo/shared/.venv`).
Aucun framework, aucun ordonnanceur, lancé à la main. ~16 800 lignes de Python.

### Chaîne
```
sources (38 adaptateurs)
   → raw/{source}/*.json.gz        brut, jamais jeté, compressé
   → normalisation (schema.py)
   → filtre (apposé à l'ingestion, marque sans supprimer)
   → price_points.jsonl            LE cumul, 1 ligne = 1 prix
   → rapports générés (notes/*.md, Excel, HTML) + exports CSV/Excel (output/)
```

### Le contrat d'un adaptateur (`moteur/sources/ma_source.py`)
```python
SOURCE = {"id", "name", "type", "price_nature", "access", "robots"}
def collect(cap) -> (raw, records, journal)
```
Enregistré dans `sources/__init__.py`. Une source qui plante n'interrompt pas les
autres. Deux adaptateurs génériques : `_shopify.py` et `_woo.py` (WooCommerce) —
une boutique de plus = un module de ~10 lignes (domaine, devise, pays).

### Le schéma normalisé (`moteur/schema.py`) — 1 ligne = 1 prix
- **provenance** : source_id, source_type, source_url, external_id, collected_at
- **prix** : price_nature, price_amount, price_currency, price_date, estimate_low,
  estimate_high, price_nature_provenance (constante_source | deduite_statut |
  champ_dedie | declaree_tag), listing_status (active | inactive | sold | withdrawn |
  unknown), price_includes_premium (frais acheteur inclus ou non, enchères seulement)
- **identité montre** : brand, model, reference, title, reference_provenance
  (champ_dedie | extrait_titre | extrait_description | jeton_titre | sku),
  source_category
- **technique** : year, case_material, case_size_mm, movement, dial_color, condition
- **contexte** : seller
- **filtre** : filter_verdict (GARDER | REJETER | QUARANTAINE), filter_rule, filter_version

Fonctions de parsing robustes : `parse_money` (formats US, européen, suisse
« 5'000 », symboles, codes), `parse_date` (ISO, epoch s/ms…).

### Le filtre « est-ce une montre ? » (`labo/filtres/`)
```
Filtres_scrapping.xlsx  (couche humaine, seule éditée : dictionnaires de marques,
        │                familles de mots, règles R0…R8, onglet JOURNAL daté,
        │                colonnes ACTIF / AXE, cas de test)
        ▼ export_json.py  (échoue si une règle nomme un concept absent)
filters.json
        ▼
moteur/filtre.py   (verdict + règle + version sur chaque ligne)
```
Principe : jamais figé. Toute modification se rejoue sur le brut déjà collecté
(`filtre.py --marquer`), sans requête réseau, et se mesure (taux de rejet /
quarantaine / répartition des règles par source).

### Scripts de `moteur/` (tous au même niveau, à plat)
- **collecte** : `run.py` (orchestrateur), `sources/`, `rejoue.py` (re-normalise depuis le brut), `robots.py`
- **modèle / qualité** : `schema.py`, `filtre.py`, `extraction.py`, `catalogue.py`, `reconnaissance.py`
- **contrôles** : `verifie.py`, `verifie_sources.py`, `controle_source.py`, `controle_final.py`, `audit_champs.py`
- **sondes d'accès** (200 domaines) : `sonde.py`, `sonde_profonde.py`, `page_blocages.py`
- **rapports générés** : `etat.py` → ETAT_DATA.md, `panorama.py` → PANORAMA.md,
  `entonnoir.py`, `vues.py`, `toutes_les_sources.py`, `page_sources.py`,
  `rapport_source.py`, `rapport_excel.py`, `excel_sources.py`, `presentation.py`,
  `inventaire.py`, `catalogue_essais.py`
- **export** : `export.py` → CSV + Excel datés dans `output/donnees/`

### Données (`labo/data/`)
| Élément | Taille | Rôle |
|---|---:|---|
| `price_points.jsonl` | 190 Mo | le cumul, **201 657 lignes** au 26/09 |
| `price_points.jsonl.avant-*` (×3) | 120–170 Mo chacun | sauvegardes manuelles avant chaque vague |
| `raw/{source}/*.json.gz` | 445 Mo | brut compressé, 38 sources |
| `normalized/{source}.json` | 144 Mo | dernier run par source, lisible, régénérable |
| `runs/*.json` | 428 Ko | un manifeste par run (comptes, période, complétude, erreurs) |
| `logs/`, `cache/`, `sonde*.json`, `audit_champs.json` | petits | journaux et états |

État de la base au 26/09 (collecte en cours) :
- **201 657 prix**, **36 sources** qui rendent des données, période **2007 → 2026**
- filtre : 164 422 GARDER, 36 474 REJETER, 761 QUARANTAINE
- au 21/09 : ~48 000 lignes au « socle » (référence + date + transaction réelle)
- ~2 000 marques distinctes ; devises USD, EUR, GBP, CHF, HKD
- plus gros contributeurs : Montredo 43 938, Hodinkee 18 945, Phillips 16 347,
  Christie's 12 507, Antiquorum 10 691, Artcurial 8 631, Analog:Shift 8 360

Types de sources : maisons de ventes (Christie's, Phillips, Antiquorum,
Artcurial, Morphy, Cottone, Lyon & Turnbull, Sworders, Fortuna, Monaco Legend,
Loupe This, Grailzee…), marchands (Shopify / WooCommerce : Analog:Shift, Craft &
Tailored, Bulang, Montredo, Keystone, Topper…), communauté (WatchRecon),
agrégateurs. Bloquées : LiveAuctioneers (anti-bot), Bezel (CGU, drapeau
`ARBITRAGE_CGU`). API eBay : Browse accessible, Marketplace Insights (le vendu)
refusée tant que la démarche administrative n'est pas faite.

Règles de collecte : robots.txt lu avant tout, ≥ 1 s entre requêtes, aucun
contournement d'anti-bot, User-Agent honnête, données publiques uniquement.

---

## 6. Tests et contrôles

| Chantier | Commande | Ce qu'elle vérifie | État |
|---|---|---|---|
| Données | `python moteur/verifie.py` | cas de parsing figés (argent, dates) + invariants de chaque ligne de la base ; hors ligne, sort en code 1 si échec | OK |
| Sources | `python moteur/sonde.py --historique` | accessibilité des ~200 domaines, alerte sur changement d'état | OK |
| Filtre | `python moteur/filtre.py` | banc de 76 cas de test définis dans l'Excel | 76/76 |
| Front | `npm run check` | typecheck + lint + build | OK |
| CI | GitHub Actions (`wp-3-main/.github/workflows/ci.yml`) | typecheck, lint, build, npm audit (non bloquant) sur main/dev | OK |
| Back | `npm run test:back` | — | **n'existe pas** |
| Base | `npm run db:check` | — | **n'existe pas** |

Pas de pytest, pas de tests unitaires par adaptateur, pas de tests front
(composants ou end-to-end), pas de CI côté moteur (le dépôt n'est même pas poussé).

---

## 7. Problèmes connus et dette

1. **Le site affiche des données fictives.** C'est l'écart principal au produit.
2. **Aucun contrat de données entre moteur et front.** Deux modèles incompatibles
   (plat par prix côté moteur, relationnel par ids côté front).
3. **Le cumul stocke un ÉTAT, pas un journal d'observations.** Au 21/09 :
   136 051 annonces distinctes pour 136 377 lignes (326 ré-observations).
   Impossible donc de suivre un prix demandé dans le temps, de déduire les ventes
   par disparition d'annonce, ou de construire l'indice de sentiment.
4. **Stockage en fichiers plats** : un JSONL de 190 Mo réécrit à chaque run,
   copies de sauvegarde manuelles de 120–170 Mo, trop gros pour GitHub (limite
   dépassée). `run.py` charge tout en mémoire.
5. **Le moteur n'existe qu'en un exemplaire** : pas de remote git.
6. **Pas de base de dev** ; pas de migrations ; table créée à la volée.
7. **Pas de budget de requêtes partagé par domaine** entre scripts (13 boutiques
   Shopify ont bloqué d'un coup en 429).
8. **`moteur/` à plat** : collecte, contrôle, sondes et ~12 générateurs de
   rapports mélangés au même niveau.
9. **Pas d'ordonnancement** : collecte lancée à la main ; chaque jour sans relevé
   est un jour d'historique perdu pour les sources à prix demandé.
10. Pas de référentiel canonique des montres (marque → modèle → référence) :
    la référence est tantôt un champ dédié, tantôt extraite du titre.
11. Pas de gestion des devises : prix stockés en devise native uniquement.

---

## 8. Décisions en attente

1. **Langage du moteur** : Python (recommandé — le contrat entre moteur et site
   serait la base Postgres, pas le langage) ou TypeScript pour tout unifier.
2. **Journal d'observations** plutôt qu'état courant (recommandé : journal).
3. **Contrat de données du front** : quelles entités, quelles vues, quelles API.
4. **Base de dev** (branche Neon ? Postgres local ?).
5. Bezel (CGU) et quelques sites qui ne répondent qu'à un faux User-Agent
   navigateur : arbitrage humain.

Prochaines vagues prévues : ouvrir 54 sources « indéterminées », re-tester 27
fermées, construire le budget de requêtes partagé puis la collecte profonde
(Antiquorum 2010-2019 en priorité).

---

## 9. Ce que j'attends de toi (l'IA qui lit ce document)

Propose une **structure cible** pour ce projet, en justifiant chaque choix :

1. **Organisation des dépôts et dossiers** : monorepo ou non, où vivent le site,
   le moteur, le filtre, les données, les rapports, les tests.
2. **Découpage du moteur** : collecte / normalisation / filtre / stockage /
   rapports / exports, et comment ranger les ~30 scripts actuels.
3. **Stockage** : passer du JSONL à Postgres (Neon) ? Schéma proposé pour
   observations brutes, annonces, montres de référence (marque / modèle /
   référence), prix, sources, avec le journal d'observations.
4. **Contrat moteur ↔ site** : tables ou vues SQL consommées par Next.js, API
   (route handlers / server actions), types partagés.
5. **Back** : quelles routes, quelle couche d'accès aux données, migrations
   (Drizzle ? Prisma ? SQL brut ?), base de dev.
6. **Tests** : quoi tester à chaque niveau (parsing, adaptateurs avec fixtures
   tirées du brut, filtre, invariants de base, API, front), et la CI des deux côtés.
7. **Exploitation** : ordonnancement quotidien de la collecte, budget de requêtes
   par domaine, stockage du brut (445 Mo et croissant) hors git.
8. **Ordre de migration** : par où commencer sans casser ce qui marche.

Contraintes à respecter : le brut n'est jamais jeté ; le filtre marque et ne
supprime pas, et doit rester modifiable via l'Excel et rejouable sur tout
l'historique ; une petite équipe, budget faible (Vercel + Neon déjà en place) ;
collecte éthique (robots.txt, pas de contournement d'anti-bot).
