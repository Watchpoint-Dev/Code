# Journal des versions

Les changements notables, du plus récent au plus ancien. Le détail au jour le
jour, avec les mesures et les blocages, est dans
[`docs/notes/PROGRESS.md`](docs/notes/PROGRESS.md).

## 2026-10-01 — La base de prix dans Postgres

- Migration `0002` : table `price_observation`, une ligne par point de prix et par
  jour de relevé, les mêmes colonnes pour toutes les sources ; tables `source` et
  `reference` (une fiche consolidée par marque et référence).
- `normalisation.py` : référence normalisée (suffixes de variante Rolex, Patek,
  Audemars Piguet ; notes de catalogue ; SKU de repli écartés), état sur cinq
  niveaux, sens de la date de chaque source. En base : 744 références portent au
  moins 20 prix, 4 946 au moins 5 (contre 658 et 4 812 sans normalisation).
- `python -m watchpoint db migrate` et `python -m watchpoint charge` : 261 192 prix
  chargés sur la branche Neon `dev` en moins d'une minute, sans doublon au
  rechargement, comptes identiques au journal.
- Antiquorum collecté en entier, de 1989 à 2026. Grailzee collecté par tranches de pages.

## 2026-09-27 à 29 — Monorepo

- Les dépôts `labo` (moteur de données) et `WPV3` (site) sont réunis dans
  `Watchpoint-Dev/Code`, historiques conservés.
- Le moteur devient un package Python installable, `backend/src/watchpoint`,
  découpé par couche, avec un point d'entrée unique `python -m watchpoint`.
  Tous les chemins passent par `config.py`. Aucune logique modifiée : le rejeu
  complet du brut donne une empreinte identique sur les 35 sources rejouables.
- Nouveaux dossiers `database/` (schéma et migrations, contrat entre backend et
  frontend), `research/` (exploration séparée de la production), `scripts/`,
  `docs/` (architecture, décisions, guides, rapports générés).
- Tests pytest et ruff pour le backend ; CI séparée pour le backend et le frontend.
- Côté site : composants sortis de `app/`, accès à la base regroupés dans
  `src/lib/db/`, données fictives isolées dans `src/fixtures/`.
- Décisions tranchées : Python pour le moteur, la base Postgres comme contrat,
  journal d'observations plutôt qu'état, pas d'ORM, branche Neon pour le dev
  (voir [`docs/decisions/`](docs/decisions/README.md)).
- Collecte : Antiquorum 2004-2025 et 1993, reprise des 27 sources existantes.
  La base passe de 187 096 à 241 061 prix.

## 2026-09-21 à 22 — Vague 1 de collecte

- 8 nouveaux adaptateurs : Antiquorum, Phillips, Grailzee, Morphy, Cottone,
  Knightsbridge, Certified Watch Store, Watches.com. Everest et Roni Madhvani
  écartées après mesure.
- Phillips collectée : 16 347 lots réalisés, 2015 à 2026, 86 % avec référence.
- Antiquorum 2013-2019 collectée : 5 839 lots.
- Sonde des 200 sources réparée (User-Agent, ordre du verdict, robots.txt
  illisible) : 119 sources ouvertes au lieu d'une cinquantaine.
- Filtre : cinq corrections mesurées sur le brut, 22 horlogers ajoutés, +758
  lignes gardées. Banc de tests 76/76.
- Orchestrateur : verrou de collecte, manifeste incrémental, déduplication par
  empreintes, collecte d'Antiquorum par tranches d'années.

## 2026-09-07 — API eBay

- Quatre diagnostics de l'API officielle : Browse (prix demandés) accessible,
  Marketplace Insights (prix vendus) refusé tant que l'accès n'est pas accordé.
  Balayage complet du luxe estimé à 1 894 appels par jour.

## 2026-08-11 au 09-02 — Campagne de collecte

- De 11 à 30 adaptateurs, dont 28 qui rendent des données.
- La base passe de 42 154 à 136 377 prix.
- Le filtre de scrapping devient un classeur Excel compilé en JSON, rejouable
  sur tout l'historique.

## 2026-07-20 à 21 — Recherche de sources

- Audit de 50 sources, registre maître des sources, pilotes d'échelle.
- Conclusion : l'historique daté ne se trouve que chez les maisons de ventes.

## 2026-07-19 — Le site en ligne

- Dépôt `WPV3`, déploiement Vercel, authentification Clerk, base Neon.
- CI (typecheck, lint, build), branches `main` (production) et `dev` (preview).
