-- 0001 — les comptes du site (ecrits par le frontend, synchronises depuis Clerk).
--
-- Reprise a l'identique du DDL que frontend/src/lib/db/users.ts execute encore
-- a chaque synchronisation (CREATE ... IF NOT EXISTS). La table existe donc deja
-- en production : cette migration est idempotente et ne fait que l'officialiser.
-- Quand le runner de migrations tournera, l'appel ensureUsersTable() cote site
-- pourra disparaitre.

CREATE TABLE IF NOT EXISTS public.app_users (
  id            BIGSERIAL PRIMARY KEY,
  clerk_user_id TEXT NOT NULL UNIQUE,
  email         TEXT,
  first_name    TEXT,
  last_name     TEXT,
  image_url     TEXT,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_seen_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_app_users_email ON public.app_users (email);
