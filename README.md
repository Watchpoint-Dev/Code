# Watchpoint

Local app workspace.

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
