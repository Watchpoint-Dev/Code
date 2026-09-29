# Ajouter une source

Une source passe par deux étapes : on l'**explore** dans `research/`, puis, si
elle vaut la peine, on écrit son **adaptateur** dans le backend. On ne branche
jamais une source directement : presque toutes les erreurs coûteuses du projet
venaient d'un champ qui avait l'air d'être le bon prix et ne l'était pas.

## 1. Explorer

```bash
cp -r research/_modele research/sources/ma-source
```

Remplir `notes.md` au fil des tests, et y répondre au moins à ces questions :

- **Accès.** API, JSON embarqué dans la page, HTML serveur ? Le site charge-t-il
  en JavaScript ? Que dit le robots.txt, et quel délai demande-t-il ?
- **Le prix.** Quel champ porte le prix, et quelle est sa **nature** : réalisé
  (enchère conclue), vendu, demandé, estimation, prix neuf ? Pour une enchère,
  frais acheteur inclus ou marteau nu ? Le mesurer sur un lot dont on connaît le
  résultat, ne pas le supposer.
- **La référence.** Est-elle publiée dans un champ dédié, ou faut-il la deviner
  dans le titre ?
- **La date.** Date de vente, ou date de mise en ligne ? Chez un marchand, c'est
  presque toujours la seconde.
- **Le volume réel.** Compter, ne pas estimer. Toutes les estimations d'avant
  mesure du projet se sont révélées fausses, et toujours par le haut.

Les pièges déjà rencontrés, à vérifier sur chaque nouvelle source :

| Piège | Où on l'a vu |
|---|---|
| le JSON-LD donne l'estimation basse, pas le prix réalisé | Phillips, Antiquorum |
| le prix Shopify est la commission de l'acheteur, pas la montre | Grailzee |
| les montres-bracelets sont rangées sous « Jewelry » | Cottone |
| un site entier sans une montre (bracelets, démo WooCommerce) | Everest, Roni Madhvani |
| « nous consulter » confondu avec « vendu » | Montredo |

Garder les échantillons dans `samples/` (ignoré par git) et les scripts à côté.

## 2. Écrire l'adaptateur

Un adaptateur est un module de `backend/src/watchpoint/sources/` qui expose deux
choses :

```python
SOURCE = {
    "id": "ma_source",            # identifiant stable, en minuscules
    "name": "Ma Source",
    "type": "auction",            # auction | dealer | retail | marketplace | aggregator | community
    "price_nature": "realised",   # la nature par défaut, voir docs/donnees.md
    "access": "comment on lit la source, en une ligne",
    "robots": "ce que dit le robots.txt, et la date de lecture",
}

def collect(cap: int = 5000) -> tuple[list[dict], list[dict], list[str]]:
    """Rend (brut, points_de_prix, journal)."""
```

- **le brut** : ce que le site a renvoyé, sans retouche, sous la forme
  `{"url", "status", "payload"}`. Il est conservé pour toujours.
- **les points de prix** : construits par `schema.price_point(...)`, qui valide
  la nature, exige une provenance pour toute référence et remplit les 30 colonnes.
- **le journal** : des lignes lisibles (pages vues, erreurs, comptes). Il finit
  dans le manifeste du run.

Les requêtes passent par `commun.utils.get()`, qui gère le User-Agent, les
reprises et le `Retry-After`. Jamais `requests` directement.

### Le cas simple : une boutique Shopify ou WooCommerce

Dix lignes suffisent. Exemple réel, `sources/hairspring.py` :

```python
from . import _shopify

SOURCE = {
    "id": "hairspring", "name": "Hairspring", "type": "dealer",
    "price_nature": "asking",
    "access": "Shopify products.json (country=US obligatoire)",
    "robots": "OK — verifie le 11/08/2026",
    "corpus_horloger": True,   # le marchand ne vend que des montres
}

NORMALISATION = dict(devise="USD", domaine="hairspring.com", etat="preowned")

def collect(cap: int = 400):
    return _shopify.collecte(SOURCE, cap, pays="US", **NORMALISATION)
```

`_shopify.collecte()` accepte d'autres réglages : collection dédiée aux montres
(`chemin`), SKU qui vaut référence (`sku_est_reference`), étiquettes qui disent
la nature (`tags_nature`). Voir sa docstring. Pour WooCommerce, `_woo.collecte()`.

### Le cas général : une maison de ventes

Séparer la lecture de la normalisation, en deux fonctions **pures** :

```python
def lots_du_brut(entrees: list[dict]) -> list[dict]:
    """Extrait les lots des réponses brutes. Aucune requête ici."""

def fiche(lot: dict) -> dict:
    """Un lot -> un point de prix (schema.price_point)."""

def collect(cap: int = 5000):
    raw, journal = [], []
    ...  # les requêtes, qui remplissent raw
    records = [fiche(l) for l in lots_du_brut(raw)]
    return raw, records[:cap], journal
```

C'est ce découpage qui rend la source rejouable : le jour où l'on découvre un
champ mal lu, `python -m watchpoint rejoue ma_source` refait la normalisation
sur tout le brut déjà collecté, sans une requête.

## 3. Enregistrer

1. Ajouter le module à la liste `ALL` de `sources/__init__.py`. L'ordre compte :
   les maisons à historique profond passent en premier, pour qu'une panne chez
   elles se voie avant le reste.
2. Si la source est rejouable, ajouter son identifiant au bon tuple de
   `collecte/rejoue.py` (`SHOPIFY`, `WOO` ou `ENCHERES`).
3. Mettre à jour son statut dans `registre/catalogue.py` : c'est ce que lisent
   les rapports.

## 4. Mesurer avant d'intégrer

```bash
backend/.venv/bin/python -m watchpoint collecte ma_source
```

Puis regarder, dans cet ordre :

- le tableau de fin de collecte : volume, période, complétude par champ ;
- `data/normalized/ma_source.json` : ouvrir une dizaine de lignes à la main et
  les comparer au site ;
- la répartition du filtre : si beaucoup de montres sont rejetées, la cause est
  presque toujours une marque absente du dictionnaire ou une catégorie mal lue
  (voir [le guide du filtre](filtre.md)) ;
- `python -m watchpoint verifie`.

Noter les mesures dans `research/sources/ma-source/notes.md`, avec la date.

## 5. Tester et livrer

```bash
make test
git switch -c source/ma-source dev
git add backend/src/watchpoint/sources/ma_source.py research/sources/ma-source
git commit -m "Source Ma Source : <volume>, <période>, <nature>"
```

Puis une pull request vers `dev` (voir [CONTRIBUTING](../../CONTRIBUTING.md)).
