# docs/livrables/ — ce qui sort du projet

Tout ce qui est **destiné à quelqu'un d'autre** : un associé, l'équipe, une
réunion. Si tu produis un CSV, un Excel, un rapport fini — il vient ici.

La distinction avec `docs/notes/` :

| | |
|---|---|
| **`docs/notes/`** | ce que tu penses — brouillons, plans, journal de bord. Pour toi. |
| **`docs/livrables/`** | ce que tu montres — fini, daté, partageable. Pour les autres. |

```
docs/livrables/
├── donnees/       exports de la base (CSV, Excel)
├── documents/     rapports et présentations finis
└── referentiels/  les registres de travail partagés
```

---

## donnees/ — générés par une commande

Ne pas créer ces fichiers à la main. Une commande les produit depuis la base :

```bash
source shared/.venv/bin/activate

backend/.venv/bin/python -m watchpoint rapport export            # CSV + Excel de toute la base
backend/.venv/bin/python -m watchpoint rapport export christies  # une seule source
backend/.venv/bin/python -m watchpoint rapport export --csv      # CSV seulement
```

**Chaque export porte sa date et rien n'est jamais écrasé** — on peut donc
comparer deux états de la base à un mois d'écart.

Le CSV sert aux imports et aux scripts. L'Excel sert à être **partagé** : noms
de colonnes en français, natures de prix explicites, et un onglet **Résumé**
qui donne le nombre de prix, le montant médian et la période par source.

## documents/ — les livrables écrits

Rapports et présentations terminés, à diffuser. Chaque nom porte sa date.

## referentiels/ — les registres partagés

`DataSources.xlsx` — le registre des 210 sources, avec les colonnes
collaboratives (assigné à, feedback) que les associés remplissent.

---

## La règle

**On ne travaille jamais dans `docs/livrables/`.** On y dépose une version finie et
datée. Le brouillon vit dans `docs/notes/`, la donnée brute dans `data/`.

Si un fichier de `docs/livrables/` doit être modifié, on régénère ou on redépose une
nouvelle version datée — on ne retouche pas l'ancienne, elle est peut-être déjà
partie chez quelqu'un.
