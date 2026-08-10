"""Adaptateurs de collecte — un module par source, meme interface.

Chaque module expose :
    SOURCE            dict : id, name, type, price_nature, access, robots
    collect(cap:int)  -> (raw, records, journal)

`raw`     ce que la source a renvoye, non retouche (conserve pour re-traitement)
`records` enregistrements normalises (schema.price_point)
`journal` lignes de trace lisibles (pages vues, erreurs HTTP, comptes)
"""
import pathlib
import sys

_COLLECT = pathlib.Path(__file__).resolve().parents[1]
_LAB = _COLLECT.parent
for _path in (str(_COLLECT), str(_LAB / "shared")):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from . import bezel, christies, craft_and_tailored, liveauctioneers, watchrecon  # noqa: E402

# ordre d'execution : les sources a historique date d'abord
ALL = [christies, liveauctioneers, craft_and_tailored, bezel, watchrecon]
