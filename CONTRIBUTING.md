# Contribuer

## Les branches

```
main    la production. Vercel déploie le site depuis main. On n'y pousse jamais directement.
dev     la branche de travail commune. Vercel en fait une preview.
<type>/<sujet>   une branche courte par tâche, partie de dev
```

Préfixes de branche en usage :

| Préfixe | Pour |
|---|---|
| `source/` | une nouvelle source ou la correction d'un adaptateur (`source/tajan`) |
| `filtre/` | une modification du filtre (`filtre/montres-de-poche`) |
| `front/` | le site (`front/page-reference`) |
| `db/` | le schéma ou une migration (`db/0002-observations`) |
| `fix/` | une correction |
| `docs/` | la documentation seule |

## Le cycle

```bash
git switch dev && git pull
git switch -c source/tajan
# ... travail ...
make test && make check          # les deux doivent passer
git push -u origin source/tajan
```

Puis une pull request vers `dev`. Quand `dev` est stable et vérifié en preview,
une pull request `dev` vers `main` met en production.

## Les messages de commit

En français, au présent, et qui disent **ce qui change et pourquoi**, pas
seulement quel fichier a bougé :

```
Source Tajan : 1 840 lots réalisés 2012-2026, frais inclus mesurés sur 40 lots

Le catalogue publie l'estimation dans le JSON-LD et le résultat dans le HTML
du lot ; c'est le second qui est lu. Frais acheteur : 1,30 constant, mesuré.
```

Une première ligne de 72 caractères au plus. Un corps quand le pourquoi ne tient
pas dans le titre, ce qui est souvent le cas pour une source ou le filtre.

## Ce qu'on vérifie en revue

- **Une source** : sa nature de prix est-elle mesurée, pas supposée ? Les frais
  acheteur ? Le sens de la date ? Les mesures sont-elles dans
  `research/sources/<source>/notes.md` ?
- **Le filtre** : l'effet sur la base est-il mesuré (`filtre --base` avant et
  après) et consigné dans l'onglet `JOURNAL` ?
- **Une migration** : est-elle nouvelle (on ne modifie jamais une migration
  appliquée) ? A-t-elle tourné sur la branche Neon `dev` ?
- **Partout** : pas de secret, pas de chemin absolu, pas d'import depuis
  `research/` dans le code de production. Les tests le vérifient en partie.

## Style de code

**Python** : la configuration de ruff est dans `backend/pyproject.toml`
(`make lint`). Les commentaires et docstrings disent pourquoi le code est ainsi,
en particulier quand une mesure l'a imposé : on y date la mesure et on donne le
chiffre. C'est ce qui permet de ne pas défaire une correction six mois plus tard.

**TypeScript** : ESLint et `tsc` (`npm run check` dans `frontend/`). Les accès à
la base passent uniquement par `frontend/src/lib/db/`, marqué `server-only`.

## Les données

- Ne jamais commiter `data/price_points.jsonl` : c'est l'instantané `.gz` qui est
  versionné (`scripts/sauvegarde.sh`).
- Ne jamais supprimer de brut dans `data/raw/`.
- Un rapport de `docs/rapports/` ne s'édite pas à la main : on corrige le
  générateur, ou la donnée, puis on régénère.

## Les secrets

Aucun secret dans le dépôt. Les noms des variables sont dans `.env.example`, les
valeurs dans des fichiers `.env` ignorés par git, ou dans Vercel. Si un secret a
été commité par erreur, le considérer comme compromis : le révoquer chez le
fournisseur d'abord, nettoyer l'historique ensuite.
