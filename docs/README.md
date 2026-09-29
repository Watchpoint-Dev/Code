# Documentation

## Pour comprendre

| Document | Contenu |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | le système entier : les couches, comment backend et frontend communiquent, le schéma de base cible, et les raisons de chaque choix |
| [donnees.md](donnees.md) | le modèle de données : chaque champ d'un point de prix, les natures, les provenances, les pièges connus |
| [decisions/](decisions/README.md) | les décisions tranchées, datées, avec leur raison |

## Pour faire

| Guide | Quand |
|---|---|
| [guides/installation.md](guides/installation.md) | installer un poste, de zéro |
| [guides/collecte.md](guides/collecte.md) | lancer, suivre, interrompre et relire une collecte |
| [guides/ajouter-une-source.md](guides/ajouter-une-source.md) | explorer puis brancher une nouvelle source |
| [guides/filtre.md](guides/filtre.md) | comprendre et modifier le filtre « est-ce une montre ? » |
| [guides/deploiement.md](guides/deploiement.md) | Vercel, Neon, la CI |
| [../CONTRIBUTING.md](../CONTRIBUTING.md) | branches, commits, revue |

## Le reste

| Dossier | Contenu | Qui l'écrit |
|---|---|---|
| [notes/](notes/README.md) | avancement (`PROGRESS.md`), idées et questions (`CARNET.md`), outils | à la main |
| `rapports/` | l'état chiffré de la base, source par source | **généré** par `make rapports`, ne pas éditer |
| [livrables/](livrables/README.md) | ce qui part chez quelqu'un : exports, référentiels, présentations | déposé, daté |

Les README de chaque partie décrivent son contenu et ses commandes :
[backend](../backend/README.md), [frontend](../frontend/README.md),
[database](../database/README.md), [research](../research/README.md).
