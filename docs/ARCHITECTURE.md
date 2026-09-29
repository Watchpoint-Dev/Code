# Watchpoint — Architecture

Statut : en place depuis le 27/09/2026 (migration faite, vérifiée par rejeu du brut).
Ce document décrit la cible. Ce qui existe déjà est signalé **(existe)**, ce qui
reste à écrire **(à faire)**.

---

## 1. Le système en une image

```
  ~38 sources publiques                 BACKEND (Python)                          FRONTEND (Next.js, Vercel)
  maisons de ventes, marchands,  ┌──────────────────────────────────┐         ┌───────────────────────────┐
  marketplaces                   │ 1 collecte    adaptateurs, HTTP   │         │ pages (App Router)        │
        │                        │ 2 normalisation  schéma unique    │         │   server components       │
        └──── HTTP poli ───────► │ 3 filtre      montre ? oui/non    │         │ lib/db/queries (lecture)  │
                                 │ 4 stockage    brut + journal      │         │ API routes (auth, compte) │
                                 │ 5 chargement  → Postgres          │         └─────────────▲─────────────┘
                                 │ 6 métriques   cotes, indices      │                       │ SQL (lecture)
                                 └──────────────┬───────────────────┘                       │
                                                │ SQL (écriture)          ┌─────────────────┴───────────┐
                                                └───────────────────────► │ DATABASE  Postgres (Neon)   │
                                                                          │ schéma = LE CONTRAT         │
                                                                          │ migrations dans database/   │
                                                                          └─────────────────────────────┘
```

**La règle qui structure tout : le backend et le frontend ne se parlent pas
directement. Ils partagent une base de données, et le schéma de cette base est
leur contrat.**

- Le **backend écrit** : sources, montres, annonces, observations de prix, métriques calculées.
- Le **frontend lit** ces tables, et **écrit uniquement ce qui appartient à l'utilisateur**
  (compte, portefeuille, favoris).
- Le frontend **ne calcule aucune métrique**. S'il affiche « +12 % sur 1 an », ce chiffre
  est déjà dans une table remplie par le backend. Une seule vérité, testable côté Python.
- Le backend **n'expose pas d'API HTTP** pour l'instant. Le jour où une app mobile ou un
  partenaire consomme les données, on ajoute `backend/src/watchpoint/api/` (FastAPI) qui
  lit les mêmes tables — rien d'autre ne bouge.

Pourquoi ce choix plutôt qu'une API REST entre les deux dès maintenant : le site est
privé, les données changent une fois par jour, et Next.js lit Postgres nativement
depuis ses server components. Une API intermédiaire serait une couche de plus à
maintenir sans rien apporter. C'est aussi ce que la note RECAP du 26/09 avait conclu :
« le contrat entre moteur et site serait la base Postgres, pas le langage ».

---

## 2. L'arborescence

```
WP/                                   = dépôt Watchpoint-Dev/Code
├── backend/                          tout le Python, un seul package installable
│   ├── pyproject.toml                dépendances, pytest, ruff ; `pip install -e backend`
│   ├── src/watchpoint/
│   │   ├── config.py                 LE seul module qui connaît l'arborescence        (existe)
│   │   ├── __main__.py               `python -m watchpoint collecte|rejoue|filtre|verifie|rapports…`
│   │   ├── commun/utils.py           client HTTP poli : UA, retry, pause ; registre     (existe)
│   │   ├── sources/                  les 38 adaptateurs + moteurs _shopify, _woo      (existe)
│   │   │   └── __init__.py           registre ALL, sources gelées
│   │   ├── schema.py                 le point de prix : champs, natures, parse_money  (existe)
│   │   ├── filtrage/                 filtre.py (verdict) + compile.py (Excel → JSON)  (existe)
│   │   ├── collecte/                 run.py : orchestrateur, verrou, manifeste, dédup (existe)
│   │   │                             + rejoue.py (rejouer le brut sans réseau)
│   │   ├── db/                       connexion Postgres + chargeur jsonl → tables     (à faire, étape 6)
│   │   ├── metriques/                socle, courbes par référence, indices, écart neuf/occasion
│   │   │                             (extrait de vues.py / page_sources.py)          (à faire)
│   │   ├── qualite/                  verifie.py, controle_source.py, sonde.py, robots (existe)
│   │   ├── rapports/                 les générateurs d'états → docs/rapports/          (existe)
│   │   └── registre/                 sources prouvées / à négocier / écartées / bloquées (existe)
│   ├── config/filtres/               Filtres_scrapping.xlsx + filters.json            (existe)
│   └── tests/                        pytest                                           (à faire, léger)
│       ├── test_filtre.py            les 76 cas du banc
│       ├── test_schema.py            parse_money, natures, colonnes du point de prix
│       └── test_architecture.py      pas d'import de research/, pas de chemin absolu, pas de sys.path
│
├── frontend/                         le site Next.js (ex wp-3-main), déployé par Vercel
│   ├── package.json
│   ├── src/app/                      les routes (pages + api/auth/sync)               (existe)
│   ├── src/components/               layout/, auth/, ui/ (sortis de src/app/)         (existe)
│   ├── src/lib/db/                   client.ts, users.ts (existent) ; queries/*.ts   (à faire)
│   └── src/fixtures/                 les JSON fictifs, tant que la base n'est pas branchée
│
├── database/                         le contrat
│   ├── migrations/                   0001_app_users.sql (existe), 0002_… (à faire, étape 3)
│   ├── seeds/                        sources, marques (depuis catalogue.py, filters.json)
│   └── README.md                     le schéma expliqué, qui écrit quoi
│
├── data/                             la donnée locale — IGNORÉE par git sauf :
│   ├── price_points.jsonl.gz         l'actif, versionné compressé
│   └── runs/                         les manifestes de collecte (petits, précieux)
│   (raw/, normalized/, cache/, logs/ : sur le disque seulement)
│
├── research/                         l'exploration — jamais importée par la production
│   ├── README.md                     tableau : expérience | but | statut | équivalent en prod
│   ├── _modele/                      le gabarit d'une fiche source
│   ├── sources/<source>/             un dossier par source étudiée (ex essais/*)
│   ├── ebay/                         client API + diagnostics (son .env reste local)
│   ├── outils/                       audits ponctuels (sonde_profonde, reconnaissance…)
│   └── preuves/                      IGNORÉ : 186 Mo d'échantillons, reste sur le disque
│
├── scripts/                          l'exploitation
│   ├── collecte.sh                   la file de collecte (paramétrée, sans chemin absolu)
│   ├── sauvegarde.sh                 instantané gzip de la base
│   └── restaure.sh                   gzip -dc → price_points.jsonl
│
├── docs/
│   ├── ARCHITECTURE.md               ce document
│   ├── decisions/                    une page par décision tranchée (ADR)
│   ├── notes/                        PROGRESS, CARNET, tools… (écrit à la main)
│   ├── rapports/                     ETAT_DATA, ENTONNOIR, VUES… (GÉNÉRÉS, ne pas éditer)
│   └── livrables/                    ce qui part chez quelqu'un (ex output/)
│
├── .github/workflows/
│   ├── backend.yml                   ruff + pytest, sur les changements de backend/
│   └── frontend.yml                  typecheck + lint + build, sur frontend/
├── .env.example                      toutes les variables, sans valeur
├── .gitignore
└── README.md                         quoi, comment installer, comment lancer chaque partie
```

Les documents personnels qui vivaient dans ce dossier en sont sortis. **Ignorés mais
gardés sur le disque** : `_archive/`, `.claude/`, `.remember/`.

---

## 3. Le backend en détail

### Les couches, dans l'ordre du flux

| # | Couche | Rôle | Entrée → sortie |
|---|---|---|---|
| 1 | `commun/utils.py` | parler poliment aux sites | URL → réponse (UA honnête, retry, Retry-After, pause) |
| 2 | `sources/` | un adaptateur par source | réponses → `(brut, points de prix, journal)` |
| 3 | `schema.py` | un seul format de point de prix | champs bruts → dict validé, 30 colonnes |
| 4 | `filtrage/` | est-ce une montre ? | titre + catégorie → GARDER / REJETER / QUARANTAINE |
| 5 | `collecte/` | orchestrer, dédoublonner, tracer | sources → brut + journal + manifeste |
| 6 | `db/` | charger dans Postgres | journal → tables (idempotent, rejouable) |
| 7 | `metriques/` | calculer ce que le site affiche | tables → tables de métriques |

`qualite/` et `rapports/` sont transverses : ils lisent, ils ne modifient rien.

### Le contrat d'un adaptateur (existe, inchangé)

```python
SOURCE = {"id", "name", "type", "price_nature", "access", "robots", ...}
def collect(cap: int = ...) -> tuple[list[dict], list[dict], list[str]]:
    """(brut, points_de_prix, journal)"""
```

### Ce qui change dans le code, et ce qui ne change pas

- **Ne change pas** : la logique de chaque adaptateur, du filtre, du schéma. Aucune
  réécriture fonctionnelle pendant la migration.
- **Change** : les imports. Aujourd'hui, ~20 scripts bricolent `sys.path` et
  s'importent « à plat » (`from filtre import …`). Demain, un vrai package :
  `from watchpoint.filtrage.filtre import filtre`. C'est ce qui rend le code testable,
  installable et lançable depuis n'importe où.
- **Change** : les chemins. Un seul `config.py` sait où sont `data/`, `docs/rapports/`,
  `backend/config/filtres/`. Plus aucun `../notes` ni `../output` codé en dur.
- **Constantes dédoublées** : `REFERENCE_SURE`, `TRANSACTIONNELLES` et les libellés de
  natures sont copiés dans ~8 modules et ont déjà divergé (panorama n'a pas la même
  définition que vues). Ils iront une fois dans `schema.py` (à faire : la migration n'a volontairement rien changé à la logique).

### La vérification qui prouve que rien n'a cassé

Le brut n'est jamais jeté : on peut **rejouer tout le brut** avec l'ancien code puis le
nouveau, et comparer les lignes produites. Identiques = migration correcte. C'est plus
fort qu'une batterie de tests écrite après coup. S'y ajoutent le banc du filtre (76/76),
`verifie.py`, et une vraie collecte sur une petite source.

---

## 4. La base de données (étape 3 du plan)

Schéma v1 proposé — il tranche la décision « journal ou état » : **journal**.

```
source           id, nom, type, nature_par_defaut, frais_inclus_par_defaut, statut
brand            id, nom canonique, alias[]
watch_model      id, brand_id, reference_normalisee, reference_affichee, nom
                 UNIQUE (brand_id, reference_normalisee)           ← LA clé de rapprochement
listing          id, source_id, external_id, url, titre, watch_model_id (nullable),
                 reference_brute, reference_provenance, vendeur, etat, specs…,
                 premiere_vue, derniere_vue
                 UNIQUE (source_id, external_id)                   ← l'annonce à travers le temps
observation      id, listing_id, run_id, observe_le, prix, devise, nature,
                 nature_provenance, date_prix, frais_inclus (vrai/faux/inconnu),
                 estimation_basse/haute, statut_annonce,
                 filtre_verdict, filtre_regle, filtre_version
                 UNIQUE (listing_id, observe_le)                   ← LE JOURNAL, jamais écrasé
ingestion_run    id, debut, fin, complet
run_source       run_id, source_id, lignes, nouvelles, erreur, completude (jsonb)
fx_rate          jour, devise, taux_usd       ← conversion à l'AFFICHAGE, jamais à l'ingestion

-- calculé par backend/metriques, lu par le site
reference_stats  watch_model_id, mois, groupe_nature, devise, n, mediane, p25, p75, nb_sources
brand_index      brand_id, mois, valeur, variation

-- écrit par le site
app_users        (existe, créé aujourd'hui au runtime par le front → passe en migration)
user_asset       user_id, watch_model_id, prix_achat, date_achat
```

Les points durs déjà mesurés, traités dans le schéma et pas après :

- **Référence fiable à ~80 %** → `watch_model_id` nullable + `reference_provenance`.
  Le « socle dur » (référence en champ dédié) et le « socle large » (déduite) restent
  distinguables en SQL.
- **Frais acheteur** → `frais_inclus` à trois états. On ne reconstitue **jamais** le
  marteau par division (CARNET.md).
- **Devises** → toujours stockées natives. `fx_rate` sert l'affichage.
- **Journal** → une observation par annonce et par jour. C'est ce qui rend possibles
  « l'annonce a disparu, donc elle s'est vendue » et l'indice de sentiment.

Migrations : SQL pur numéroté dans `database/migrations/`, appliqué par
`python -m watchpoint db migrate` (une table `schema_migrations` retient ce qui est
passé). Pas d'ORM : le backend écrit en SQL, le front lit en SQL — un ORM d'un côté
ne servirait pas l'autre.

Base de dev : **une branche Neon `dev`** (copie instantanée de prod, gratuite).
`DATABASE_URL` diffère entre `.env` de dev et variables Vercel de prod. Plus jamais de
test qui écrit en production.

---

## 5. Le frontend en détail

Ce qui existe et se garde :

- **Authentification Clerk complète** : `proxy.ts` (protection des routes), pages
  sign-in/up, `AuthShell`, synchronisation Clerk → table `app_users`. Fonctionne.
- **Les pages** marketplace, auctions, top-performers, compare, watch/[id],
  market-index, market-news : l'UI est faite, elle lit du JSON fictif.
- Layout, sidebar, composants shadcn utilisés, `TrendAreaChart`.

Ce qui change :

- `src/app/components/` → `src/components/` (convention Next : `app/` ne contient que
  des routes).
- `src/lib/db/` : **la seule porte vers la base**, `server-only`.
  `queries/watches.ts`, `queries/listings.ts`, `queries/indices.ts`… Les pages
  deviennent des server components qui appellent ces requêtes ; le filtrage se fait en
  SQL via `searchParams`, plus dans le navigateur sur un JSON embarqué.
- Les trois jeux de données fictifs **ne se correspondent pas entre eux** (`marketPrice`
  vs `marketValueUsd` vs `price`, `aw-` vs `mw-` vs `mpw-`). Ils partent dans
  `src/fixtures/` et disparaissent page par page à mesure que les requêtes réelles arrivent.
- Le `CREATE TABLE app_users` exécuté à chaque connexion part dans
  `database/migrations/0001_app_users.sql`.

Ce que le moteur ne pourra pas fournir (à décider plus tard, pas bloquant) : news,
communauté, enchères en direct, specs riches (calibre, réserve de marche).

Nettoyage différé (commit séparé, après la migration) : ~25 dépendances inutilisées
(`lovable-tagger`, `recharts`, `react-hook-form`, une vingtaine de `@radix-ui/*`…),
deux systèmes de toast en double, un `QueryClientProvider` que rien n'utilise.

---

## 6. Données, secrets, configuration

| | Dans git | Hors git | Comment le récupérer |
|---|---|---|---|
| Code, config filtre, migrations | oui | | `git clone` |
| `price_points.jsonl` (202 Mo) | `.gz` (13 Mo) | le `.jsonl` | `scripts/restaure.sh` |
| Manifestes `data/runs/` | oui | | |
| Brut `data/raw/` (499 Mo) | | oui | ne se recollecte pas à l'identique → sauvegarde disque externe |
| `data/normalized/` (135 Mo) | | oui | régénéré par `rejoue` |
| `research/preuves/` (186 Mo) | | oui | sauvegarde disque |
| Secrets | **jamais** | `.env`, `frontend/.env.local` | `.env.example` liste les noms |

Variables (`.env.example`) : `DATABASE_URL`, `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`,
`CLERK_SECRET_KEY`, `NEXT_PUBLIC_CLERK_SIGN_IN_URL`, `NEXT_PUBLIC_CLERK_SIGN_UP_URL`,
`EBAY_CLIENT_ID`, `EBAY_CLIENT_SECRET`, `WP_ANTIQUORUM_ANNEES`, `WP_CHRISTIES_ANNEES`.

Aucun secret n'a été trouvé dans le code ni dans l'historique des trois dépôts.

---

## 7. Règles

**Recherche / production**
- La production n'importe **jamais** depuis `research/`. (Déjà vrai aujourd'hui.)
- Une expérience validée est **réécrite** dans `backend/src/watchpoint/sources/`, pas copiée.
- Les échantillons récupérés restent hors git ; on garde les scripts et les notes.

**Données** (règles du projet, conservées telles quelles)
- Le brut n'est jamais jeté. Le filtre marque, il ne supprime pas.
- Le filtre n'est jamais figé : toute modification se rejoue sur le brut et se mesure.
- Ne jamais annoncer un volume qu'on n'a pas mesuré.
- Ne jamais reconstituer un marteau par division. Ne jamais comparer deux devises.
- User-Agent honnête, robots.txt lu, aucun contournement d'anti-bot.

**Git**
- `main` = production (Vercel déploie). `dev` = travail (Vercel fait des previews).
- On travaille sur `dev` ou sur une branche courte, on fusionne dans `main` quand c'est vert.
- `docs/rapports/` est généré : on ne l'édite jamais à la main.

---

## 8. Correspondance : ancien → nouveau

| Aujourd'hui | Demain |
|---|---|
| `wp-3-main/` | `frontend/` (historique conservé) |
| `wp-3-main/src/app/components/` | `frontend/src/components/` |
| `wp-3-main/src/lib/neon.ts` | `frontend/src/lib/db/client.ts` |
| `wp-3-main/src/lib/clerk-neon-user.ts` | `frontend/src/lib/db/users.ts` |
| `wp-3-main/src/data/dummy-data/` | `frontend/src/fixtures/` |
| `wp-3-main/.github/workflows/ci.yml` | `.github/workflows/frontend.yml` |
| `labo/moteur/run.py` | `backend/src/watchpoint/collecte/run.py` |
| `labo/moteur/rejoue.py` | `backend/src/watchpoint/collecte/rejoue.py` |
| `labo/moteur/sources/` | `backend/src/watchpoint/sources/` |
| `labo/moteur/schema.py` | `backend/src/watchpoint/schema.py` |
| `labo/moteur/filtre.py` | `backend/src/watchpoint/filtrage/filtre.py` |
| `labo/filtres/export_json.py` | `backend/src/watchpoint/filtrage/compile.py` |
| `labo/filtres/*.xlsx, filters.json` | `backend/config/filtres/` |
| `labo/shared/utils.py` | `backend/src/watchpoint/commun/utils.py` |
| `labo/shared/requirements.txt` | `backend/pyproject.toml` (+ openpyxl, python-dotenv) |
| `labo/moteur/verifie.py, controle_source.py, sonde.py, robots.py` | `backend/src/watchpoint/qualite/` |
| `labo/moteur/etat, entonnoir, panorama, vues, page_sources, presentation, rapport_*, inventaire, toutes_les_sources, excel_sources, export, audit_champs` | `backend/src/watchpoint/rapports/` |
| `labo/moteur/catalogue.py, catalogue_essais.py, page_blocages.py` | `backend/src/watchpoint/registre/` (puis seeds SQL) |
| `labo/moteur/sonde_profonde, verifie_sources, controle_final, reconnaissance, extraction` | `research/outils/` |
| `labo/essais/<source>/` | `research/sources/<source>/` |
| `labo/essais/ebay/`, `eu_auctions/`, `_modele/` | `research/ebay/`, `research/sources/eu_auctions/`, `research/_modele/` |
| `labo/preuves/` | `research/preuves/` (ignoré) |
| `labo/data/` | `data/` |
| `labo/data/logs/file_*.sh` | `scripts/collecte.sh` (paramétré : `antiquorum:2000-2009 grailzee`) |
| `notes/` | `docs/notes/` (écrit main) + `docs/rapports/` (générés) |
| `labo/README.md` | `backend/README.md` (réécrit) |
| `output/` | `docs/livrables/` |
| `README.md` | `README.md` (réécrit) |
| `_archive/` | reste, ignoré |

---

## 9. La migration du 27/09/2026 (faite)

0. Attendre la fin de la collecte. Sauvegarde : copie complète de `WP/` + commits dans
   les deux dépôts (dont les 35 modifications en attente du site).
1. Créer le dépôt à la racine, importer l'historique de `labo` et `wp-3-main`
   (`git subtree`).
2. **Frontend** : déplacer → `npm ci && npm run check`.
3. **Backend** : déplacer, passer en package, corriger imports et chemins →
   banc du filtre 76/76, `verifie`, rejeu du brut identique, collecte d'une petite source.
4. **Research, docs, scripts** : déplacer, corriger les chemins absolus → les
   générateurs de rapports tournent et écrivent dans `docs/rapports/`.
5. `database/` : `0001_app_users.sql` (le reste du schéma = étape 3 du plan).
6. `.gitignore`, `.env.example`, READMEs, CI.
7. Branches `main` + `dev`, push sur `Watchpoint-Dev/Code`.
8. (Toi) Vercel : relier le projet à `Watchpoint-Dev/Code`, Root Directory = `frontend`.
   Archiver `WPV3`.

---

## 10. La suite

Dans l'ordre, chaque étape débloquant la suivante :

1. **Schéma v1** : `database/migrations/0002_…sql` avec sources, marques,
   modèles, annonces, observations (le journal) et runs, tel que décrit au §4.
   Appliqué sur la branche Neon `dev`.
2. **Chargeur** : `backend/src/watchpoint/db/`, qui lit `data/price_points.jsonl`
   et remplit les tables, de façon idempotente. Commande `python -m watchpoint db charge`.
3. **Métriques** : `backend/src/watchpoint/metriques/`, à partir des calculs déjà
   écrits dans `rapports/vues.py` et `rapports/page_sources.py` : médiane et
   dispersion par référence et par mois, écart neuf/occasion, puis indices par marque.
4. **Le site sur du réel** : `frontend/src/lib/db/queries/`, puis les pages une à
   une, en commençant par la fiche d'une référence (`/watch/[id]`).
5. **Collecte quotidienne planifiée**, qui alimente le journal d'observations.

En parallèle, hors code : l'accès eBay Marketplace Insights, l'arbitrage des
conditions d'utilisation de Bezel.
