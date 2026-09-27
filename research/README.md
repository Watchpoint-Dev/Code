# research — l'exploration

Ici on **explore avant de brancher** : on teste une source, on regarde à quoi
ressemble la donnée, on documente ce qu'on a trouvé — accès, format, légal,
pièges. Le code de production vit dans `backend/`.

## Les règles

- **La production n'importe jamais depuis `research/`.** (Vérifié par
  `backend/tests/test_architecture.py`.) L'inverse est permis : un script
  d'exploration peut utiliser `watchpoint` pour réutiliser le client HTTP ou le filtre.
- **Une expérience validée est réécrite** dans `backend/src/watchpoint/sources/`,
  pas copiée. Son dossier reste ici comme preuve.
- **Les données récupérées restent hors git** (`samples/`, `preuves/`) : on garde
  les scripts et les notes qui permettent de les régénérer.
- **Aucune clé dans le code** : les secrets vont dans un `.env` local (voir `ebay/`).

## Organisation

```
research/
├── _modele/             le gabarit : cp -r research/_modele research/sources/ma-source
├── sources/<source>/    une source étudiée : explore.py, notes.md (la fiche), samples/ (hors git)
├── ebay/                client de l'API officielle + 4 diagnostics ; clés dans ebay/.env
├── outils/              audits ponctuels sortis du moteur (sonde profonde, reconnaissance…)
└── preuves/             HORS GIT (186 Mo) : la campagne du 09/08 — échantillons,
                         robots.txt lus, pages de blocage archivées, fiches de verdict
```

Lancer un script : `backend/.venv/bin/python research/sources/<source>/explore.py`.

## Les expériences

| Expérience | But | Statut | En production |
|---|---|---|---|
| `sources/antiquorum` | maison horlogère, 1989 → 2026, catalogue déménagé sur catalog.antiquorum.swiss | **validée** | `sources/antiquorum.py` |
| `sources/phillips` | résultats Genève / HK / NY via le payload React Router | **validée** | `sources/phillips.py` |
| `sources/morphy` | maison US généraliste, « Final Price » frais inclus | **validée** | `sources/morphy.py` |
| `sources/cottone` | généraliste, montres-bracelets rangées sous Jewelry | **validée** (~210 lots) | `sources/cottone.py` |
| `sources/grailzee` | app d'enchères : le prix Shopify est la COMMISSION, pas la montre | **validée** | `sources/grailzee.py` |
| `sources/certified-watch-store` | marchand Shopify de neuf | **validée** | `sources/certifiedwatchstore.py` |
| `sources/watches-com` | détaillant agréé Shopify | **validée**, valeur faible (3 % gardés) | `sources/watchesdotcom.py` |
| `sources/watches-of-knightsbridge` | WooCommerce Store API | **validée** | `sources/knightsbridge.py` |
| `sources/eu_auctions` | 22 sondes : Artcurial, Tajan, Lempertz, Cortrie, Koller | Artcurial **validée** ; Tajan à brancher ; Koller à creuser ; Lempertz, Cortrie écartées | `sources/artcurial.py` |
| `sources/christies` | première sonde (juillet) | remplacée par l'adaptateur | `sources/christies.py` |
| `ebay` | API officielle : Browse (demandé) OK, Marketplace Insights (vendu) 403 | **en cours** — attend l'accès Marketplace Insights | — |
| `sources/barnebys` | agrégateur de résultats d'enchères | **abandonnée** (robots `Disallow: /`) — piste licence | — |
| `sources/everest` | fabricant de bracelets : 0 montre sur 248 | **abandonnée** | — |
| `sources/roni-madhvani` | site WooCommerce de démonstration | **abandonnée** | — |

## Les outils (`outils/`)

Scripts d'audit ponctuels, datés de la campagne d'août : `sonde_profonde.py`,
`verifie_sources.py`, `controle_final.py`, `reconnaissance.py`, `extraction.py`.
Ils écrivent dans `data/` ou `outils/sortie/`. Ils ne font pas partie de la
chaîne de production ; les contrôles récurrents sont dans `backend/src/watchpoint/qualite/`.
