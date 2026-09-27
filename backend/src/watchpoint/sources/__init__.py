"""Adaptateurs de collecte — un module par source, meme interface.

Chaque module expose :
    SOURCE            dict : id, name, type, price_nature, access, robots
    collect(cap:int)  -> (raw, records, journal)

`raw`     ce que la source a renvoye, non retouche (conserve pour re-traitement)
`records` enregistrements normalises (schema.price_point)
`journal` lignes de trace lisibles (pages vues, erreurs HTTP, comptes)
"""
from . import (acollectedman, amsterdamvintage, analogshift, antiquorum,
               artcurial, awco, berrys,  # noqa: E402
               bezel, bulangandsons, certifiedwatchstore, christies,
               chronofinder, cottone, craft_and_tailored,
               cwsellors, everywatch, fortuna, globalwatchshop, grailzee,
               hairspring,
               hodinkee, keystone, knightsbridge, liveauctioneers, loupethis,
               lyonandturnbull, monacolegend, montredo, morphy, phillips,
               topper, wannabuyawatch, watchesdotcom,
               watchesofswitzerland,
               sworders, watchesofdistinction, watchrecon, watchtrader)

# Ordre d'execution : les sources a historique date d'abord — ce sont elles qui
# donnent la profondeur, et c'est sur elles qu'on veut voir une panne en premier.
ALL = [everywatch,
       # Les maisons de ventes, par profondeur datee decroissante. Antiquorum
       # remonte a 1989 et Phillips a 2015 : ce sont elles qui portent la cote,
       # et une panne chez elles doit se voir avant tout le reste.
       antiquorum, artcurial, christies, phillips, monacolegend,
       lyonandturnbull, morphy, fortuna, loupethis, grailzee, cottone,
       liveauctioneers,
       craft_and_tailored, analogshift, montredo, cwsellors, berrys, hairspring,
       hodinkee, keystone, watchtrader, wannabuyawatch, awco, globalwatchshop,
       chronofinder, bulangandsons, acollectedman, amsterdamvintage,
       watchesofdistinction, knightsbridge,
       sworders,
       watchesofswitzerland, topper, certifiedwatchstore, watchesdotcom,
       bezel, watchrecon]
