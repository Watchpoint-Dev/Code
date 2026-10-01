"""Postgres : connexion, migrations, chargement du journal jsonl dans les tables.

    python -m watchpoint db migrate     applique les migrations de database/migrations/
    python -m watchpoint db etat        ce que contient la base
    python -m watchpoint charge         normalise data/price_points.jsonl et le charge

La base visée est celle de DATABASE_URL (variable d'environnement, sinon
backend/.env). En développement : la branche Neon `dev`, jamais la production.
"""
from __future__ import annotations

import re

import psycopg

from watchpoint import config


def connexion() -> psycopg.Connection:
    return psycopg.connect(config.database_url(), connect_timeout=20)


def hote() -> str:
    """L'hôte de la base, sans identifiants : pour dire où l'on écrit."""
    trouve = re.search(r"@([^/:?]+)", config.database_url())
    return trouve.group(1) if trouve else "?"
