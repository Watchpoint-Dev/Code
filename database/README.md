# database/ — le contrat entre le backend et le frontend

Le backend et le frontend ne se parlent pas directement : **ils partagent cette
base, et ce schéma est leur contrat.** Aucun code applicatif ici — seulement le
schéma, versionne.

| Qui | Ecrit | Lit |
|---|---|---|
| **backend** (Python) | sources, montres, annonces, observations de prix, metriques calculees | tout |
| **frontend** (Next.js) | ce qui appartient a l'utilisateur : `app_users`, portefeuille | tout |

Le frontend ne calcule aucune metrique : s'il affiche une variation sur un an,
elle est deja dans une table remplie par `backend/src/watchpoint/metriques/`.

## Migrations

`migrations/NNNN_description.sql`, SQL pur, numerote, **jamais modifie une fois
applique** : on corrige par une nouvelle migration. Pas d'ORM : le backend ecrit
en SQL, le frontend lit en SQL, un ORM d'un cote ne servirait pas l'autre.

Application : `python -m watchpoint db migrate`. Une table `schema_migrations`
retient ce qui est passe.

| Migration | Contenu | Etat |
|---|---|---|
| `0001_app_users.sql` | comptes du site | existe deja en prod (cree au runtime par le front) |
| `0002_price_observation.sql` | `source`, `price_observation` (une ligne par point de prix et par jour de releve), `reference` (fiche consolidee) | appliquee sur la branche `dev` le 01/10/2026 |

## Environnements

- **prod** : la base Neon branchee a Vercel (`DATABASE_URL` dans les variables Vercel).
- **dev** : une **branche Neon `dev`**, copie instantanee de prod. Son URL va dans
  les `.env` locaux. Plus jamais de test qui ecrit en production.

`seeds/` : donnees de reference a charger une fois (sources depuis
`backend/src/watchpoint/registre/`, marques depuis `backend/config/filtres/filters.json`).
