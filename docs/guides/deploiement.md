# Déployer

## Vue d'ensemble

| Partie | Où elle tourne | Comment elle se déploie |
|---|---|---|
| frontend | Vercel | automatiquement, à chaque push sur `main` (production) ou `dev` (preview) |
| base de données | Neon (Postgres) | les migrations de `database/migrations/`, appliquées à la main pour l'instant |
| backend | le poste de l'équipe | `scripts/collecte.sh` ; un planificateur viendra plus tard |

## Le frontend sur Vercel

Le projet Vercel pointe sur le dépôt `Watchpoint-Dev/Code` avec ces réglages :

| Réglage | Valeur |
|---|---|
| Root Directory | `frontend` |
| Framework | Next.js (détecté) |
| Install Command | `npm ci` |
| Build Command | `npm run build` |
| Production Branch | `main` |

Les variables d'environnement se règlent dans *Settings > Environment Variables*,
séparément pour *Production* et *Preview* :

| Variable | Production | Preview (`dev`) |
|---|---|---|
| `DATABASE_URL` | branche Neon `main` | branche Neon `dev` |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY` | clés de production Clerk | clés de test Clerk |
| `NEXT_PUBLIC_CLERK_SIGN_IN_URL` | `/sign-in` | `/sign-in` |
| `NEXT_PUBLIC_CLERK_SIGN_UP_URL` | `/sign-up` | `/sign-up` |

Une preview ne doit jamais écrire dans la base de production.

### Première mise en place, depuis l'ancien dépôt WPV3

1. Vercel, projet existant, *Settings > Git* : déconnecter `Watchpoint-Dev/WPV3`,
   connecter `Watchpoint-Dev/Code`.
2. *Settings > General* : Root Directory = `frontend`.
3. Vérifier que les variables d'environnement sont toujours là.
4. Redéployer `main`, vérifier la connexion et la page d'accueil.
5. Archiver le dépôt `WPV3` sur GitHub (lecture seule, historique conservé).

## La base Neon

Deux branches Neon :

- `main` : la production, branchée à Vercel Production.
- `dev` : une copie instantanée de `main`, pour le développement et les previews.
  Elle se recrée depuis `main` quand on veut repartir de données fraîches.

Appliquer une migration, en attendant le runner `python -m watchpoint db migrate` :

```bash
psql "$DATABASE_URL" -f database/migrations/0002_xxx.sql
```

Toujours sur `dev` d'abord, puis sur `main` une fois la pull request fusionnée.
Une migration appliquée ne se modifie plus : on en écrit une nouvelle.

## Le backend

Il tourne aujourd'hui sur un poste, à la demande :

```bash
scripts/collecte.sh <sources>
```

Deux évolutions sont prévues, dans cet ordre : le chargement du journal dans
Postgres (étape 6 du plan), puis une collecte planifiée chaque jour. Le choix du
planificateur (cron sur une petite machine, GitHub Actions, service géré) reste
ouvert ; la contrainte est une collecte qui dure plusieurs heures et respecte les
délais de chaque source.

## La CI

`.github/workflows/` contient deux jobs, déclenchés sur `main`, `dev` et les pull
requests, chacun seulement si ses fichiers ont changé :

| Workflow | Déclenché par | Ce qu'il vérifie |
|---|---|---|
| `backend.yml` | `backend/**` | installation du package, `pytest` |
| `frontend.yml` | `frontend/**` | `npm ci`, typecheck, lint, build, `npm audit` (non bloquant) |

Une pull request ne se fusionne pas si la CI est rouge.
