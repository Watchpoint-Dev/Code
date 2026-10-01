"""Ou vivent les choses. Le SEUL module qui connait l'arborescence du depot.

Avant le 27/09/2026, une vingtaine de scripts reconstruisaient chacun leurs
chemins a partir de `__file__` (`parent.parent / "data"`, `LABO.parent / "notes"`,
`RACINE / "labo" / "data"`…). Deplacer un dossier cassait les rapports en
silence. Tout chemin passe desormais par ici.

La racine est celle du depot (le dossier qui contient backend/, data/, docs/).
`WATCHPOINT_RACINE` la surcharge, par exemple pour faire tourner le moteur sur
une copie des donnees.
"""
from __future__ import annotations

import os
import pathlib

# backend/src/watchpoint/config.py -> parents[3] = la racine du depot
RACINE = pathlib.Path(
    os.environ.get("WATCHPOINT_RACINE") or pathlib.Path(__file__).resolve().parents[3]
)

DATA = RACINE / "data"                      # brut, normalise, runs, cache (hors git sauf .gz et runs)
CUMUL = DATA / "price_points.jsonl"         # le journal des prix, l'actif
FILTRES = RACINE / "backend" / "config" / "filtres"
CONFIG_FILTRE = FILTRES / "filters.json"    # compile depuis Filtres_scrapping.xlsx

RAPPORTS = RACINE / "docs" / "rapports"     # etats GENERES : ne pas editer a la main
LIVRABLES = RACINE / "docs" / "livrables"   # ce qui part chez quelqu'un
REFERENTIELS = LIVRABLES / "referentiels"   # classeurs de sources (lus ET ecrits)

RESEARCH = RACINE / "research"              # l'exploration : jamais importee par la production

MIGRATIONS = RACINE / "database" / "migrations"
FICHIER_ENV = RACINE / "backend" / ".env"   # local, ignoré par git : les secrets du backend


def database_url() -> str:
    """L'adresse de la base Postgres : la variable d'environnement, sinon backend/.env.

    Pas de dépendance pour lire un .env : une ligne `CLE=valeur` suffit. La
    variable d'environnement l'emporte, ce qui permet de viser une autre base
    le temps d'une commande (DATABASE_URL=... python -m watchpoint charge).
    """
    url = os.environ.get("DATABASE_URL")
    if not url and FICHIER_ENV.exists():
        for ligne in FICHIER_ENV.read_text(encoding="utf-8").splitlines():
            cle, _, valeur = ligne.partition("=")
            if cle.strip() == "DATABASE_URL":
                url = valeur.strip().strip("'\"")
    if not url:
        raise SystemExit("DATABASE_URL absente : la définir, ou la mettre dans backend/.env "
                         "(voir docs/guides/installation.md)")
    return url
