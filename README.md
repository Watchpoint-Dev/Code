# L'établi

Tout ce qui touche aux **données de prix** : le moteur qui les collecte, les
données elles-mêmes, et le bac à sable où on teste de nouvelles sources.

**Local uniquement.** Rien de ce dossier ne part sur le repo d'équipe.

```
labo/
├── moteur/     le code qui tourne
├── data/       les données collectées  ← consultables à la main
├── essais/     le bac à sable, un dossier par source
├── preuves/    les échantillons qui justifient chaque verdict
└── shared/     l'environnement Python partagé
```

---

## moteur/ — le code qui tourne

```
moteur/
├── schema.py    le modèle unique : nature, date, devise, source
├── run.py       l'orchestrateur
└── sources/     un adaptateur par source
```

**Lancer une collecte :**

```bash
cd ~/Desktop/WP/labo
source shared/.venv/bin/activate

python moteur/run.py                 # toutes les sources
python moteur/run.py bezel christies # seulement celles-ci
```

Relancer n'écrit jamais deux fois le même prix : la collecte est **idempotente**,
elle peut tourner tous les jours pour construire l'historique par relevés.

**Ajouter une source** — créer `moteur/sources/ma_source.py` qui expose :

```python
SOURCE = {"id", "name", "type", "price_nature", "access", "robots"}
def collect(cap) -> (raw, records, journal)
```

puis l'ajouter à la liste `ALL` dans `moteur/sources/__init__.py`. Le reste
(rangement, dédoublonnage, rapport) est automatique. Une source qui plante
n'interrompt pas les autres.

---

## data/ — les données, consultables à la main

```
data/
├── price_points.jsonl      LE fichier : 1 ligne = 1 prix, tout l'historique
├── normalized/{source}.json  dernier run par source, JSON indenté et lisible
├── raw/{source}/{date}.json  ce que le site a renvoyé, non retouché
└── runs/{date}.json          manifeste : comptes, période, complétude, erreurs
```

**`normalized/`** est fait pour être ouvert et lu. **`raw/`** sert à
re-normaliser sans re-télécharger le jour où le modèle change.

**Regarder rapidement :**

```bash
head -3 data/price_points.jsonl                    # 3 premiers prix
wc -l  data/price_points.jsonl                     # combien au total
python -c "import json,collections;print(collections.Counter(json.loads(l)['source_id'] for l in open('data/price_points.jsonl')))"
```

**Sortir un CSV ou un Excel** — pour partager, pas pour travailler :

```bash
python moteur/export.py              # CSV + Excel de toute la base
python moteur/export.py christies    # une seule source
```

Les fichiers partent dans `../output/donnees/`, datés, jamais écrasés.

---

## essais/ — le bac à sable

Un dossier par source, ~30 aujourd'hui. C'est ici qu'on **explore avant de
brancher** : on bricole, on regarde à quoi ressemble la donnée, on documente.

```
essais/ma-source/
├── explore.py   le script de test
├── notes.md     la fiche : accès, format, légal, trouvailles
└── samples/     la donnée brute récupérée
```

**Nouvelle source :** `cp -r essais/_modele essais/ma-source`

Quand un essai est concluant, il devient un adaptateur dans `moteur/sources/`.

---

## preuves/ — pourquoi on croit ce qu'on affirme

Les échantillons rapportés par la campagne du 09/08, un dossier par cluster :
`auction/`, `marketplace/`, `dealer/`, `aggregator/`, `community/`, `retail_msrp/`.

On y trouve les données extraites, **les robots.txt lus**, et **les pages de
blocage archivées**. C'est ce qui justifie la liste des sources à démarcher :
chaque « bloqué » a sa pièce à l'appui.

---

## Les règles de la maison

- **robots.txt lu avant toute autre requête**, paramètres interdits respectés.
- **Pause d'au moins 1 seconde** entre requêtes (`shared/utils.py` s'en charge).
- **Aucun contournement d'anti-bot.** Une source qui se protège est marquée
  bloquée et bascule sur la liste à négocier. C'est un résultat, pas un échec.
- **Données publiques uniquement.**
- Les conditions d'utilisation restent à valider source par source avant toute
  collecte à grande échelle.

---

## État des sources branchées

| Source | Type | Nature du prix | État |
|---|---|---|---|
| Christie's | maison de ventes | réalisé | OK |
| Craft & Tailored | marchand | demandé | OK |
| Bezel | marketplace | demandé | OK — passer à l'API interne (×366) |
| WatchRecon | communauté | demandé | OK |
| LiveAuctioneers | agrégateur | réalisé | **bloqué** — anti-bot depuis 08/2026 |

**Prouvées mais pas encore branchées** (échantillons dans `preuves/`) :
Monaco Legend, EveryWatch, Loupe This, Hodinkee, Watchtrader, Wanna Buy A Watch,
Patek Philippe, Grand Seiko.
