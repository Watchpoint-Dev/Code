# scripts — l'exploitation

Des scripts shell autonomes : ils trouvent la racine du dépôt tout seuls et
peuvent se lancer depuis n'importe où.

| Script | Rôle |
|---|---|
| `collecte.sh [source[:années] …]` | lance une file de collecte, une source par processus, sans mise en veille |
| `sauvegarde.sh` | refait l'instantané `data/price_points.jsonl.gz` à partir de la base |
| `restaure.sh [--ecrase]` | reconstruit `data/price_points.jsonl` depuis l'instantané, après un clone |

## collecte.sh

```bash
scripts/collecte.sh                                   # toutes les sources non gelées
scripts/collecte.sh morphy grailzee                   # celles-ci, dans cet ordre
scripts/collecte.sh antiquorum:2008-2009 antiquorum:2006-2007
```

- Une source par processus : trois collectes parallèles ont épuisé la mémoire
  le 21/09/2026.
- `caffeinate` empêche la mise en veille du Mac tant que la file tourne. Le
  26/09, une mise en veille a fait échouer toutes les sources suivantes. Pour
  s'en passer : `WP_SANS_CAFFEINE=1 scripts/collecte.sh …`.
- La syntaxe `source:années` règle `WP_ANTIQUORUM_ANNEES` ou
  `WP_CHRISTIES_ANNEES` pour cette source seulement.
- Tout va dans `data/logs/collecte_<date>.log`, un fichier par jour.

Le détail (lire le résultat, interrompre, les alarmes) : [docs/guides/collecte.md](../docs/guides/collecte.md).

## sauvegarde.sh

À lancer après une collecte, avant de commiter. `gzip -9n` rend un fichier
déterministe : deux instantanés d'une même base sont identiques octet pour
octet, et git ne voit pas de changement. Seules les lignes complètes sont prises,
pour ne pas capturer une ligne qu'une collecte serait en train d'écrire.

## restaure.sh

Refuse d'écraser une base existante sans `--ecrase`. La base locale peut être
plus récente que l'instantané versionné : l'écraser ferait perdre les collectes
qui n'ont pas encore été sauvegardées.
