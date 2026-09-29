# frontend — le site Watchpoint

Next.js 16 (App Router) et TypeScript, Tailwind et shadcn/ui, authentification
Clerk, base Postgres chez Neon. Déployé par Vercel.

## Démarrer

Prérequis : Node.js 20 et npm. Le lockfile est celui de npm ; ne pas utiliser
pnpm ni bun.

```bash
npm ci
cp .env.example .env.local     # puis remplir les valeurs
npm run dev                    # http://localhost:3000
```

| Script | Rôle |
|---|---|
| `npm run dev` | serveur de développement |
| `npm run build` | build de production |
| `npm run typecheck` | vérification TypeScript |
| `npm run lint` | ESLint |
| `npm run check` | les trois à la suite : ce que lance la CI |

## Variables d'environnement

Dans `.env.local` (ignoré par git) en local, dans Vercel en production.

| Variable | Valeur |
|---|---|
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Clerk, *API Keys* |
| `CLERK_SECRET_KEY` | Clerk, *API Keys* |
| `NEXT_PUBLIC_CLERK_SIGN_IN_URL` | `/sign-in` |
| `NEXT_PUBLIC_CLERK_SIGN_UP_URL` | `/sign-up` |
| `DATABASE_URL` | Neon, chaîne *pooled*. En local : la branche `dev`, jamais la production |

## Organisation

```
src/
├── app/                 les routes, et rien d'autre (convention Next.js)
│   ├── api/auth/sync/   POST : copie l'utilisateur Clerk dans app_users
│   ├── marketplace/ auctions/ top-performers/ compare/ market-index/ market-news/
│   ├── watch/[watchid]/ la fiche d'une montre
│   ├── my-assets/ investment/ community/   pages encore vides
│   └── sign-in/ sign-up/
├── components/
│   ├── layout/          AppLayout, AppSidebar
│   ├── auth/            AuthShell, synchronisation Clerk → Neon, apparence Clerk
│   └── ui/              composants shadcn, ContentCard, PageHeader, TrendAreaChart
├── lib/
│   ├── db/              LA seule porte vers la base, server-only
│   │   ├── client.ts    connexion Neon (lazy, lit DATABASE_URL)
│   │   └── users.ts     upsert des comptes dans app_users
│   ├── dummy-data.ts, market-data.ts, watch-insights.ts   assemblage des fixtures
│   └── utils.ts, flags.ts
├── fixtures/            données fictives, en attendant la vraie base
├── hooks/
└── proxy.ts             protection des routes par Clerk (le middleware de Next 16)
```

## L'authentification

Toutes les routes sont protégées par `proxy.ts`, sauf `/sign-in` et `/sign-up`.
À la première page vue après connexion, `ClerkNeonSync` appelle une fois par
session `POST /api/auth/sync`, qui crée ou met à jour la ligne de l'utilisateur
dans `public.app_users`. Sans `DATABASE_URL`, cette route répond 503 et le reste
du site fonctionne.

La table est décrite dans `database/migrations/0001_app_users.sql`. Pour
l'instant, `users.ts` la crée encore lui-même si elle n'existe pas ; cet appel
disparaîtra quand les migrations seront appliquées par le runner.

## Les données

Toutes les montres, prix, enchères et indices affichés viennent de
`src/fixtures/`, des données fictives. Ils seront remplacés page par page par
des requêtes dans `src/lib/db/queries/`, qui liront les tables remplies par le
backend. Le site ne calcule aucune métrique : il affiche ce que le backend a
calculé. Voir [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md) §5.

Attention : les trois jeux de fixtures ne se correspondent pas entre eux
(`marketPrice`, `marketValueUsd` et `price` désignent la même chose selon le
fichier). Ne pas s'en servir comme modèle pour le schéma réel.

## Chantiers connus

- Environ 25 dépendances ne sont plus utilisées (`lovable-tagger`, `recharts`,
  `react-hook-form`, une vingtaine de `@radix-ui/*`…).
- Deux systèmes de toast coexistent (radix et sonner).
- `QueryClientProvider` est monté mais aucune requête ne l'utilise.
