# Watchpoint

Watch data platform — Next.js (App Router) + TypeScript, Clerk auth, Neon (Postgres).

## Getting started (local development)

Requirements: **Node.js 20+** and **npm** (this project standardizes on npm — do
not use bun/pnpm).

```bash
npm install            # install dependencies
cp .env.example .env.local   # then fill in the values (see below)
npm run dev            # start the dev server on http://localhost:3000
```

Useful scripts:

```bash
npm run build       # production build
npm run typecheck   # TypeScript check
npm run lint        # ESLint
```

### Environment variables

Copy `.env.example` to `.env.local` and fill in your own values (never commit
`.env.local` — it is git-ignored):

- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` — from the Clerk dashboard (API Keys)
- `CLERK_SECRET_KEY` — from the Clerk dashboard (API Keys)
- `NEXT_PUBLIC_CLERK_SIGN_IN_URL` = `/sign-in`
- `NEXT_PUBLIC_CLERK_SIGN_UP_URL` = `/sign-up`
- `DATABASE_URL` — Neon connection string (pooled)

### Branches & deployment

- `main` → production (auto-deploys to Vercel).
- `dev` → shared testing branch (Vercel preview). Work on a feature branch, open
  a pull request into `dev`/`main`, get it reviewed, then merge.

> Note: watch/price data shown in the UI is still **dummy JSON** (`src/data/`).
> Only auth + user records are real (in Neon). Real data pipeline comes later.

## Clerk + Neon Authentication

The app now includes a complete Clerk authentication flow with Neon user sync.

### What is implemented

- Route protection with `proxy.ts` (all app routes protected by default)
- Public auth pages:
  - `/sign-in`
  - `/sign-up`
- Sidebar session UI:
  - signed-in state with Clerk `UserButton`
  - signed-out state with `Sign in` action
- Automatic user sync to Neon on login via `POST /api/auth/sync`
- Upserted user records in `public.app_users`

### Required environment variables

Copy `.env.example` to `.env.local` and fill in your values:

- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
- `CLERK_SECRET_KEY`
- `DATABASE_URL`

### Notes

- The sync endpoint creates `public.app_users` if it does not exist yet.
- `getFlagEmoji` in `src/lib/flags.ts` converts a location string (for example, `New York, USA` or `Paris, FR`) into a flag emoji by mapping the country code in the last comma-separated segment to its regional indicator symbol. It returns a white flag for unknown or unsupported codes.
