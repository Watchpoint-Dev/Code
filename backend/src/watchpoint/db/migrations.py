"""Appliquer les migrations SQL de database/migrations/, dans l'ordre, une seule fois.

Une table `schema_migrations` retient ce qui est passé. Chaque fichier
s'applique dans sa propre transaction : une migration qui échoue n'est pas
enregistrée et ne laisse rien à moitié fait.

Une migration appliquée ne se modifie plus : on en écrit une nouvelle.
"""
from __future__ import annotations

import sys

from watchpoint import config
from watchpoint.db import connexion, hote


def appliquees(cur) -> set[str]:
    cur.execute("""CREATE TABLE IF NOT EXISTS public.schema_migrations (
                     version TEXT PRIMARY KEY,
                     applied_at TIMESTAMPTZ NOT NULL DEFAULT now())""")
    cur.execute("SELECT version FROM public.schema_migrations")
    return {ligne[0] for ligne in cur.fetchall()}


def migrer() -> list[str]:
    fichiers = sorted(config.MIGRATIONS.glob("*.sql"))
    faites = []
    with connexion() as c:
        with c.cursor() as cur:
            deja = appliquees(cur)
        c.commit()
        for fichier in fichiers:
            if fichier.stem in deja:
                continue
            with c.transaction(), c.cursor() as cur:
                cur.execute(fichier.read_text(encoding="utf-8"))
                cur.execute("INSERT INTO public.schema_migrations (version) VALUES (%s)",
                            (fichier.stem,))
            faites.append(fichier.stem)
    return faites


def etat() -> None:
    with connexion() as c, c.cursor() as cur:
        deja = sorted(appliquees(cur))
        print(f"base : {hote()}")
        print(f"migrations appliquées : {', '.join(deja) or 'aucune'}")
        cur.execute("""SELECT relname, n_live_tup FROM pg_stat_user_tables
                       WHERE schemaname = 'public' ORDER BY relname""")
        for table, lignes in cur.fetchall():
            print(f"  {table:<22} ~{lignes:>9} lignes")
        cur.execute("SELECT pg_size_pretty(pg_database_size(current_database()))")
        print(f"taille : {cur.fetchone()[0]}")


def main() -> None:
    action = sys.argv[1] if len(sys.argv) > 1 else "etat"
    if action == "migrate":
        print(f"base : {hote()}")
        faites = migrer()
        print("appliquées : " + (", ".join(faites) if faites else "rien, la base est à jour"))
    elif action == "etat":
        etat()
    else:
        sys.exit("usage : python -m watchpoint db [migrate | etat]")


if __name__ == "__main__":
    main()
