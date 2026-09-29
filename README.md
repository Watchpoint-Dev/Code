# Watchpoint

Plateforme de prix de montres. Pour une montre donnée (marque + référence) :
l'historique de ses prix réels, leur nature, leur source — et à terme des
indices de marché et un indice de sentiment.

> Un prix n'a de sens qu'avec sa nature, sa date, sa devise et sa source.

## Comment ça marche

```
~38 sources publiques ──► BACKEND (Python) ──écrit──► DATABASE (Postgres/Neon) ◄──lit── FRONTEND (Next.js, Vercel)
maisons de ventes,        collecte → filtre →          le schéma = le contrat          pages + comptes (Clerk)
marchands, marketplaces   chargement → métriques       entre les deux
```

Le backend et le frontend ne se parlent pas directement : **ils partagent une
base, et son schéma est leur contrat.** Le détail, les choix et leurs raisons :
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Structure

| Dossier | Ce que c'est |
|---|---|
| [`backend/`](backend/) | le moteur de données en Python : collecte, normalisation, filtre, (chargement, métriques) |
| [`frontend/`](frontend/) | le site Next.js, déployé par Vercel |
| [`database/`](database/) | le schéma Postgres versionné — le contrat entre les deux |
| `data/` | les données locales. Dans git : seulement `price_points.jsonl.gz` et les manifestes `runs/` |
| [`research/`](research/) | l'exploration : une source étudiée par dossier, jamais importée par la production |
| `scripts/` | l'exploitation : file de collecte, sauvegarde, restauration |
| [`docs/`](docs/README.md) | architecture, modèle de données, guides, décisions, rapports générés, livrables |

## Installer

Prérequis : Python ≥ 3.12, Node 20, npm. Le pas-à-pas complet, avec les
problèmes fréquents : [`docs/guides/installation.md`](docs/guides/installation.md).

```bash
git clone git@github.com:Watchpoint-Dev/Code.git watchpoint && cd watchpoint

# backend
python3 -m venv backend/.venv
backend/.venv/bin/pip install -e "backend[dev]"
scripts/restaure.sh                       # reconstruit data/price_points.jsonl depuis le .gz

# frontend
cd frontend && npm ci && cd ..
```

Ou simplement `make install`. `make` sans argument liste toutes les commandes.

## Configurer

Toutes les variables sont listées, sans valeur, dans [`.env.example`](.env.example).
Les secrets ne sont **jamais** commités :

- `frontend/.env.local` — Clerk + `DATABASE_URL` (en prod : variables Vercel)
- `research/ebay/.env` — clés eBay

Base de dev : une branche Neon `dev`, jamais la production.

## Lancer

```bash
# backend — une commande, des sous-commandes (liste : python -m watchpoint aide)
backend/.venv/bin/python -m watchpoint collecte morphy     # collecter une source
scripts/collecte.sh antiquorum:2000-2009 grailzee          # une file, sans mise en veille
backend/.venv/bin/python -m watchpoint verifie             # invariants de la base
backend/.venv/bin/python -m watchpoint rapports            # régénère docs/rapports/

# frontend
cd frontend && npm run dev                                  # http://localhost:3000
```

## Tester

```bash
make test        # backend : filtre (76 cas), schéma, règles d'architecture
make lint        # backend : ruff
make check       # frontend : typecheck + lint + build
```

La CI (`.github/workflows/`) lance l'un ou l'autre selon les fichiers modifiés.

## Branches

- `main` — production : Vercel déploie le site depuis `main`.
- `dev` — travail : Vercel fait une preview à chaque push.

On travaille sur `dev` (ou une branche courte), on fusionne dans `main` quand la CI est verte.

## Documentation

| | |
|---|---|
| [Architecture](docs/ARCHITECTURE.md) | les couches, le contrat par la base, le schéma cible, les raisons |
| [Modèle de données](docs/donnees.md) | les 30 champs d'un point de prix, les natures, les pièges |
| [Faire tourner une collecte](docs/guides/collecte.md) | lancer, suivre, interrompre, relire |
| [Ajouter une source](docs/guides/ajouter-une-source.md) | de l'exploration à l'adaptateur |
| [Le filtre](docs/guides/filtre.md) | l'arbre R0 à R8 et la boucle de modification |
| [Déployer](docs/guides/deploiement.md) | Vercel, Neon, CI |
| [Contribuer](CONTRIBUTING.md) | branches, commits, revue |
| [Glossaire](docs/glossaire.md) | les termes du projet |
| [Journal des versions](CHANGELOG.md) | ce qui a changé, daté |

## Où en est le projet

- État chiffré de la base : [`docs/rapports/ETAT_DATA.md`](docs/rapports/ETAT_DATA.md) (généré).
- Avancement, décisions, blocages : [`docs/notes/PROGRESS.md`](docs/notes/PROGRESS.md).
- Le site affiche encore des **données fictives** (`frontend/src/fixtures/`) :
  le schéma complet, le chargeur et les métriques sont les prochaines étapes
  ([`docs/ARCHITECTURE.md` §10](docs/ARCHITECTURE.md#10-la-suite)).

## Règles

- Le brut n'est jamais jeté. Le filtre marque, il ne supprime pas ; toute
  modification du filtre se rejoue sur le brut et se mesure.
- On n'annonce pas un volume qu'on n'a pas mesuré.
- On ne reconstitue jamais un prix marteau par division, et on ne compare
  jamais deux montants de devises différentes.
- User-Agent honnête, robots.txt lu, aucun contournement d'anti-bot.
- La production n'importe jamais depuis `research/` (un test le vérifie).
- `docs/rapports/` est généré : on ne l'édite pas à la main.
