"""Point d'entree unique du moteur.

    python -m watchpoint collecte [source ...] [--force]   collecter (toutes, ou celles nommees)
    python -m watchpoint rejoue [source ...]               rejouer le brut, sans reseau
    python -m watchpoint filtre [--base | --marquer]       banc de tests du filtre / effet sur la base / re-marquage
    python -m watchpoint compile-filtre                    Excel -> filters.json
    python -m watchpoint verifie                           invariants de la base (sortie 1 si KO)
    python -m watchpoint sonde [--historique]              accessibilite des sources
    python -m watchpoint controle                          reverifie un echantillon sur les sites
    python -m watchpoint robots                            lecture des robots.txt
    python -m watchpoint db [migrate | etat]               applique les migrations / ce que contient la base
    python -m watchpoint charge                            normalise le journal et le charge dans Postgres
    python -m watchpoint rapports                          regenere tous les etats de docs/rapports/
    python -m watchpoint rapport <nom>                     un seul generateur (etat, entonnoir, vues…)

Chaque commande delegue au bloc `__main__` du module concerne : la logique
reste dans le module, ce fichier ne fait qu'aiguiller.
"""
from __future__ import annotations

import runpy
import sys

from watchpoint import config

COMMANDES = {
    "collecte": "watchpoint.collecte.run",
    "rejoue": "watchpoint.collecte.rejoue",
    "filtre": "watchpoint.filtrage.filtre",
    "compile-filtre": "watchpoint.filtrage.compile",
    "verifie": "watchpoint.qualite.verifie",
    "sonde": "watchpoint.qualite.sonde",
    "controle": "watchpoint.qualite.controle_source",
    "robots": "watchpoint.qualite.robots",
    "db": "watchpoint.db.migrations",
    "charge": "watchpoint.db.charge",
}

# Les generateurs qui ecrivent un etat markdown ou html. L'ordre compte peu :
# chacun relit la base de son cote.
RAPPORTS = ("etat", "entonnoir", "panorama", "vues", "toutes_les_sources",
            "rapport_source", "inventaire", "page_sources")


def _lance(module: str, arguments: list[str]) -> None:
    sys.argv = [module, *arguments]
    runpy.run_module(module, run_name="__main__", alter_sys=True)


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "aide"):
        print(__doc__)
        return
    commande, arguments = sys.argv[1], sys.argv[2:]

    if commande == "compile-filtre" and not arguments:
        arguments = [str(config.FILTRES / "Filtres_scrapping.xlsx"), str(config.CONFIG_FILTRE)]
    if commande in COMMANDES:
        _lance(COMMANDES[commande], arguments)
    elif commande == "rapport" and arguments:
        _lance(f"watchpoint.rapports.{arguments[0]}", arguments[1:])
    elif commande == "rapports":
        for nom in RAPPORTS:
            print(f"--- {nom}")
            _lance(f"watchpoint.rapports.{nom}", [])
    else:
        sys.exit(f"commande inconnue : {commande}\n{__doc__}")


if __name__ == "__main__":
    main()
