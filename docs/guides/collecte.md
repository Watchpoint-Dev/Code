# Faire tourner une collecte

## Ce que fait une collecte

Pour chaque source demandée, l'orchestrateur (`collecte/run.py`) :

1. appelle `collect()` de l'adaptateur, qui interroge le site et rend trois
   choses : le brut tel que reçu, les points de prix normalisés, un journal ;
2. passe chaque point de prix au filtre, qui y inscrit son verdict (il ne
   supprime rien) ;
3. écrit le brut dans `data/raw/<source>/<horodatage>.json.gz` ;
4. écrit le dernier état lisible dans `data/normalized/<source>.json` ;
5. ajoute au journal `data/price_points.jsonl` les seules lignes nouvelles ;
6. met à jour le manifeste `data/runs/<horodatage>.json` : volumes, période
   couverte, complétude des champs, répartition du filtre, erreurs.

Une ligne est « nouvelle » si sa clé n'est pas déjà en base. La clé est
`(source, identifiant de l'annonce, montant, date du prix)`. Le titre n'en fait
pas partie : un vendeur qui reformule son annonce sans changer le prix ne crée
pas de doublon. Relancer une collecte est donc toujours sans risque.

## Lancer

Une source, ou quelques-unes :

```bash
backend/.venv/bin/python -m watchpoint collecte morphy
backend/.venv/bin/python -m watchpoint collecte christies artcurial
```

Sans argument, toutes les sources enregistrées sauf les sources gelées (celles
qui refusent notre robot, listées dans `GELEES` de `collecte/run.py`).

Pour tout ce qui dure plus de quelques minutes, passer par la file :

```bash
scripts/collecte.sh antiquorum:2008-2009 antiquorum:2006-2007 grailzee
```

La file lance chaque source dans son propre processus, l'une après l'autre,
empêche le Mac de se mettre en veille et écrit tout dans
`data/logs/collecte_<date>.log`. Suivre en direct :

```bash
tail -f data/logs/collecte_$(date +%Y-%m-%d).log
```

## Les tranches d'années

Antiquorum (1989 à aujourd'hui) et Christie's se collectent par tranches :

```bash
scripts/collecte.sh antiquorum:2010-2019        # une plage
scripts/collecte.sh antiquorum:2015,2016        # une liste
```

Une source n'est écrite qu'une fois terminée. Une tranche de dix ans d'Antiquorum
prend plus d'une heure au rythme d'une requête toutes les cinq secondes (le
délai que demande son robots.txt) ; si la connexion coupe à la cinquantième
minute, tout est perdu. Des tranches de deux ou trois ans limitent la perte à
un quart d'heure. C'est la leçon du 27/09.

## Interrompre proprement

```bash
pkill -f scripts/collecte.sh                 # la file : plus de nouvelle source
pkill -TERM -f "watchpoint collecte"         # la source en cours
rm -f data/.collecte-en-cours                # si le verrou est resté
```

La base n'est jamais corrompue par un arrêt : les lignes sont ajoutées en fin de
fichier, une source à la fois. Seule la source en cours est perdue.

## Lire le résultat

À la fin, la console (ou le journal) affiche un tableau par source, puis la
complétude par champ. Trois alarmes font sortir la collecte en erreur :

| Alarme | Ce qu'elle veut dire |
|---|---|
| `ECHEC — … n'ont RIEN ramene` | la source a répondu vide. Site changé, adaptateur cassé, ou coupure réseau |
| `EFFONDREMENT — X : 2855 -> 0` | le volume est tombé sous 30 % du dernier run complet |
| `TRONQUE` dans le journal | l'adaptateur a atteint son plafond `cap` : la source a plus à donner |

Un `ConnectionError` sur toutes les pages est presque toujours une coupure
réseau, pas un blocage. Vérifier avec `curl -I <url du site>` avant de toucher
à l'adaptateur.

## Après une collecte

```bash
backend/.venv/bin/python -m watchpoint verifie     # invariants de la base
backend/.venv/bin/python -m watchpoint rapports    # régénère docs/rapports/
scripts/sauvegarde.sh                              # instantané data/price_points.jsonl.gz
git add data/price_points.jsonl.gz data/runs docs/rapports
git commit -m "Collecte du <date> : <sources>, <n> prix"
```

## Règles

- Une seule collecte à la fois. Le verrou refuse la seconde : trois collectes
  lancées ensemble le 21/09 ont épuisé la mémoire et le système les a tuées.
- Ne jamais baisser un délai entre requêtes en dessous de ce que demande le
  robots.txt de la source, ni en dessous d'une seconde.
- Une source qui répond 403 à notre User-Agent et 200 à un navigateur refuse
  notre robot. On la gèle, on ne se déguise pas.
