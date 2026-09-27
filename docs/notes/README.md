# docs/notes/ — ce que tu penses

Tes documents de travail. Le brouillon, pas le livrable — ce qui part chez
quelqu'un vit dans `docs/livrables/`. Les états chiffrés sont **générés** et
vivent dans `docs/rapports/`.

## Les fichiers

| Fichier | Quand tu l'ouvres | Qui l'écrit |
|---|---|---|
| **`CARNET.md`** | une idée, un truc à faire, une question | toi, en une ligne |
| **`PROGRESS.md`** | fin de session : ce qui a avancé | toi, daté |
| **`tools.md`** | la stack, les outils, les choix techniques | toi |
| `../rapports/ETAT_DATA.md` | « on a quoi comme données ? » | **généré** |
| `../rapports/SOURCES.md` | « on a quelles sources ? qui démarcher ? » | **généré** |
| `../ARCHITECTURE.md` | comment le système est construit, et pourquoi | toi, à chaque décision |

## Comment ça circule

```
une idée / un truc à faire   →  CARNET.md
       ↓ (une fois fait)
   PROGRESS.md
       ↓ (quand c'est diffusable)
   docs/livrables/documents/
```

Une ligne du carnet qui est faite **disparaît du carnet** et va dans
`PROGRESS.md`. C'est ce qui empêche le carnet de gonfler jusqu'à devenir
illisible.

## La règle qui fait la différence

**Ce qui peut être généré ne s'écrit jamais à la main.**

```bash
backend/.venv/bin/python -m watchpoint rapports            # tous les états de docs/rapports/
backend/.venv/bin/python -m watchpoint rapport etat        # -> ETAT_DATA.md
backend/.venv/bin/python -m watchpoint rapport inventaire  # -> SOURCES.md
```

À relancer après chaque collecte. Pour corriger un fait sur une source, éditer
`backend/src/watchpoint/registre/catalogue.py` — c'est le seul endroit à la main —
puis régénérer. Un récap écrit à la main devient faux en deux semaines, et à
partir de là on cesse de s'y fier.

## Pas de nouveau fichier sans raison

Si tu hésites à créer un fichier ici : ne le crée pas, écris une ligne dans
`CARNET.md`. Une décision tranchée mérite sa page dans `docs/decisions/`.
