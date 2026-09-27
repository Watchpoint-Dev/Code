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
