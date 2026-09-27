import "server-only";

import { getNeonSql } from "@/lib/neon";

type ClerkUserPayload = {
  clerkUserId: string;
  email: string | null;
  firstName: string | null;
  lastName: string | null;
  imageUrl: string | null;
};

async function ensureUsersTable() {
  const sql = getNeonSql();

  await sql`
    CREATE TABLE IF NOT EXISTS public.app_users (
      id BIGSERIAL PRIMARY KEY,
      clerk_user_id TEXT NOT NULL UNIQUE,
      email TEXT,
      first_name TEXT,
      last_name TEXT,
      image_url TEXT,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      last_seen_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )
  `;

  await sql`
    CREATE INDEX IF NOT EXISTS idx_app_users_email
    ON public.app_users (email)
  `;
}

export async function upsertClerkUser(payload: ClerkUserPayload) {
  const sql = getNeonSql();

  await ensureUsersTable();

  await sql`
    INSERT INTO public.app_users (
      clerk_user_id,
      email,
      first_name,
      last_name,
      image_url,
      last_seen_at,
      updated_at
    )
    VALUES (
      ${payload.clerkUserId},
      ${payload.email},
      ${payload.firstName},
      ${payload.lastName},
      ${payload.imageUrl},
      now(),
      now()
    )
    ON CONFLICT (clerk_user_id)
    DO UPDATE SET
      email = EXCLUDED.email,
      first_name = EXCLUDED.first_name,
      last_name = EXCLUDED.last_name,
      image_url = EXCLUDED.image_url,
      last_seen_at = now(),
      updated_at = now()
  `;
}
