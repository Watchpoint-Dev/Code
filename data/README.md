# data — les données de prix

La plupart de ce dossier n'est pas dans git : trop volumineux, ou régénérable.

| Chemin | Dans git | Contenu |
|---|---|---|
| `price_points.jsonl` | non (plus de 200 Mo) | le journal de tous les prix, une ligne JSON par prix |
| `price_points.jsonl.gz` | **oui** | son instantané compressé ; `scripts/restaure.sh` le décompresse |
| `runs/` | **oui** | un manifeste par collecte : volumes, période, complétude, erreurs |
| `raw/<source>/` | non (environ 500 Mo) | la réponse brute de chaque collecte, jamais jetée |
| `normalized/<source>.json` | non | le dernier run de chaque source, lisible ; régénéré par `rejoue` |
| `cache/` | en partie | caches de collecte (calendrier des ventes Christie's) |
| `logs/` | non | les journaux de `scripts/collecte.sh` |
| `sonde.json`, `controle_*.json`, `audit_champs.json`… | oui | résultats des contrôles et audits de sources |
| `.collecte-en-cours` | non | le verrou d'une collecte en cours |

Après un clone :

```bash
scripts/restaure.sh
backend/.venv/bin/python -m watchpoint verifie
```

Le brut ne se recollecte pas à l'identique, les sites évoluent. Il se récupère
depuis la sauvegarde disque du projet.

Le sens de chaque champ d'une ligne : [docs/donnees.md](../docs/donnees.md).

Regarder à la main :

```bash
wc -l data/price_points.jsonl
head -1 data/price_points.jsonl | python3 -m json.tool
python3 -c "import json,collections;print(collections.Counter(json.loads(l)['source_id'] for l in open('data/price_points.jsonl')).most_common(10))"
```
