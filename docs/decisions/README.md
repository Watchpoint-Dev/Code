# Décisions

Une décision tranchée = une ligne ici, avec sa date et sa raison. Quand elle
change, on ajoute une ligne, on ne réécrit pas l'ancienne.

| Date | Décision | Pourquoi |
|---|---|---|
| 2026-09-27 | **Monorepo** `Watchpoint-Dev/Code` : backend, frontend, database, research, docs | un seul endroit, un historique, une CI ; l'historique de `labo` et de `WPV3` est conservé (`git subtree`) |
| 2026-09-27 | **Le contrat backend ↔ frontend est la base Postgres**, pas une API | site privé, données quotidiennes, Next.js lit Postgres nativement ; une API (FastAPI) s'ajoutera le jour où un tiers consomme les données |
| 2026-09-27 | **Moteur en Python** (ouvert depuis le 12/07) | tout le moteur existe en Python ; le site reste en TypeScript ; le contrat est le schéma, pas le langage |
| 2026-09-27 | **Journal d'observations, pas un état** : une ligne par annonce et par jour, jamais écrasée | seul moyen de déduire une vente par disparition et de construire l'indice de sentiment ; à fixer AVANT de collecter massivement |
| 2026-09-27 | **`price_points.jsonl` versionné compressé** (`gzip -9n`, 13 Mo pour 202 Mo) | GitHub refuse > 100 Mo ; LFS ajoute une dépendance, hors-git perd le versionnement de l'actif |
| 2026-09-27 | **Migrations SQL pures, pas d'ORM** | le backend écrit en SQL, le frontend lit en SQL : un ORM d'un côté ne sert pas l'autre |
| 2026-09-27 | **Base de dev = branche Neon `dev`** | plus jamais de test qui écrit en production |
| 2026-09-27 | **Les documents personnels restent hors du dépôt** | ils ne concernent pas le code et n'ont pas à être partagés |
