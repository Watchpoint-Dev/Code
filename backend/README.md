# backend — le moteur de données

Tout ce qui touche aux **données de prix** : les collecter sur ~38 sources, les
ramener à un format unique, décider ce qui est une montre, les normaliser et
les charger dans Postgres, puis (à venir) en calculer les métriques que le site affiche.

## Le flux

```
http/commun ─► sources/ ─► schema ─► filtrage/ ─► collecte/ ─► data/ ─► normalisation ─► db/ ─► metriques/
 poli, retry   1 adaptateur  30 champs   montre ?    verrou,      brut +    référence,       Postgres  cotes,
               par source    validés     oui/non     dédoublon,   journal   état, date                indices
                                                     manifeste                                         (à faire)
                         qualite/ et rapports/ : lisent, ne modifient rien
```

```
backend/
├── pyproject.toml           dépendances et outils (pip install -e "backend[dev]")
├── config/filtres/          Filtres_scrapping.xlsx (la couche humaine) + filters.json (compilé)
├── src/watchpoint/
│   ├── __main__.py          python -m watchpoint <commande>
│   ├── config.py            LE seul module qui connaît l'arborescence
│   ├── schema.py            le point de prix : champs, natures, parse_money, parse_date
│   ├── commun/utils.py      client HTTP poli (UA honnête, retry, Retry-After), registre des sources
│   ├── sources/             un adaptateur par source + moteurs _shopify, _woo ; registre ALL
│   ├── filtrage/            filtre.py (le verdict), compile.py (Excel → JSON)
│   ├── collecte/            run.py (orchestrateur), rejoue.py (rejouer le brut sans réseau)
│   ├── qualite/             verifie, controle_source, sonde, robots
│   ├── rapports/            les générateurs d'états → docs/rapports/ et docs/livrables/
│   ├── registre/            données statiques : sources prouvées, à négocier, écartées, bloquées
│   ├── normalisation.py     référence normalisée, état sur 5 niveaux, sens de la date
│   ├── db/                  connexion, migrations, chargement jsonl → Postgres
│   └── metriques/           (à faire) socle, courbes par référence, indices
└── tests/                   pytest
```

## Installer

```bash
python3 -m venv backend/.venv
backend/.venv/bin/pip install -e "backend[dev]"
```

## Les commandes

Toutes passent par `python -m watchpoint` (liste complète : `python -m watchpoint aide`).

| Commande | Ce qu'elle fait |
|---|---|
| `collecte [source …] [--force]` | collecte, marque, range. Sans argument : toutes les sources non gelées |
| `rejoue [source …]` | re-normalise depuis le brut, sans une requête réseau |
| `filtre` / `filtre --base` / `filtre --marquer` | banc de tests / effet sur la base / re-marquage de tout l'historique |
| `compile-filtre` | Excel → `config/filtres/filters.json` |
| `verifie` | invariants de la base ; sort en erreur si quelque chose ne va pas |
| `sonde [--historique]` | accessibilité des sources |
| `db migrate` / `db etat` | applique les migrations de `database/migrations/` / ce que contient la base |
| `charge` | normalise le journal et le charge dans Postgres (`price_observation`), sans doublon |
| `rapports` | régénère tous les états de `docs/rapports/` |
| `rapport export [source]` | CSV + Excel dans `docs/livrables/donnees/` |

Pour une collecte longue, passer par `scripts/collecte.sh` : une source par
processus, pas de mise en veille, un journal par jour dans `data/logs/`.

```bash
scripts/collecte.sh antiquorum:2010-2019 phillips
```

**Une seule collecte à la fois** : un verrou (`data/.collecte-en-cours`) refuse la
seconde. Trois collectes simultanées ont épuisé la mémoire le 21/09/2026.

Relancer n'écrit jamais deux fois le même prix : la collecte est **idempotente**.

## La base Postgres

`DATABASE_URL` dans `backend/.env` (ignoré par git) : en développement, la branche
Neon `dev`. Le pipeline quotidien enchaîne :

```bash
python -m watchpoint collecte        # le brut et le journal
python -m watchpoint charge          # normalisé, dans price_observation
```

`charge` relit tout le journal : une ligne est identifiée par (source, annonce, jour
du relevé), donc rien n'est jamais dupliqué, et une règle de normalisation
modifiée (`normalisation.VERSION`) réécrit les lignes concernées au chargement suivant.
La table `reference` (une fiche par marque et référence) est recalculée à chaque fois.

## Les données

```
data/
├── price_points.jsonl        LE journal : 1 ligne = 1 prix       (hors git — trop gros)
├── price_points.jsonl.gz     son instantané compressé            (dans git)
├── runs/{date}.json          manifeste de chaque collecte        (dans git)
├── raw/{source}/{date}.json.gz  ce que le site a renvoyé, jamais jeté   (hors git)
├── normalized/{source}.json  dernier run, lisible, régénérable    (hors git)
└── logs/                     journaux de collecte                (hors git)
```

Le brut n'est **jamais** jeté : c'est lui qui permet de rejouer un filtre ou un
adaptateur corrigé sur tout l'historique sans une requête. `scripts/sauvegarde.sh`
refait l'instantané `.gz` ; `scripts/restaure.sh` reconstruit le `.jsonl` après un clone.

## Le filtre — est-ce une montre ?

L'Excel est la couche humaine, la seule qu'on édite ; il se compile en JSON, et
le moteur ne lit que le JSON. **Il n'est jamais figé.** Chaque changement suit la
même boucle :

```bash
python -m watchpoint compile-filtre       # 1. Excel -> JSON
python -m watchpoint filtre               # 2. les cas de test (76)
python -m watchpoint filtre --base        # 3. l'effet sur la base, avant/après
python -m watchpoint filtre --marquer     # 4. rejoue le verdict sur tout l'historique
```

L'onglet `JOURNAL` du classeur garde la trace datée de chaque changement et de son effet.

## Ajouter une source

1. L'explorer dans `research/sources/<source>/` (gabarit : `research/_modele/`).
2. Écrire `src/watchpoint/sources/<source>.py` :

```python
SOURCE = {"id", "name", "type", "price_nature", "access", "robots"}
def collect(cap: int = ...) -> tuple[list[dict], list[dict], list[str]]:
    """(brut, points de prix, journal)"""
```

3. L'ajouter à `ALL` dans `sources/__init__.py`.

Une boutique Shopify ne demande qu'un module de dix lignes (voir `sources/_shopify.py`).
Une source qui plante n'interrompt pas les autres ; une source muette ou qui
s'effondre fait sortir la collecte en erreur.

## Les règles de la maison

- **robots.txt lu avant toute autre requête**, paramètres interdits respectés.
- **Pause d'au moins 1 seconde** entre requêtes, davantage si la source le demande.
- **User-Agent honnête. Aucun contournement d'anti-bot.** Une source qui se protège
  est marquée bloquée et bascule sur la liste à négocier : c'est un résultat.
- **Données publiques uniquement.**
- **Ne jamais annoncer un volume qu'on n'a pas mesuré.**
- **Ne jamais reconstituer un marteau par division** ; les frais acheteur sont
  mesurés source par source (`price_includes_premium`).
