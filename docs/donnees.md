# Le modèle de données

Tout ce qui est collecté, quelle que soit la source, est ramené à une seule
forme : le **point de prix**, défini dans `backend/src/watchpoint/schema.py`.
Ce document en est le dictionnaire.

Le principe qui guide chaque champ : **un prix n'a de sens qu'avec sa nature, sa
date, sa devise et sa source.** Un montant seul ne vaut rien.

## Où sont les données

```
data/
├── price_points.jsonl        le journal : une ligne JSON = un point de prix
├── price_points.jsonl.gz     son instantané compressé, versionné dans git
├── raw/<source>/<horodatage>.json.gz   la réponse brute de chaque collecte
├── normalized/<source>.json  le dernier run de chaque source, lisible
├── runs/<horodatage>.json    le manifeste de chaque collecte
└── cache/                    caches de collecte (calendrier Christie's)
```

Seuls le `.gz` et `runs/` sont dans git. Le reste est local (voir
[installation](guides/installation.md#3-les-données)).

## Le point de prix, champ par champ

### Provenance

| Champ | Type | Sens |
|---|---|---|
| `source_id` | texte | identifiant de l'adaptateur (`antiquorum`, `hodinkee`…) |
| `source_type` | texte | `auction`, `dealer`, `retail`, `marketplace`, `aggregator`, `community` |
| `source_url` | texte | l'URL de l'annonce ou du lot |
| `external_id` | texte | l'identifiant de l'annonce chez la source ; sert à la déduplication |
| `collected_at` | horodatage ISO, UTC | le moment de la collecte |

### Le prix

| Champ | Type | Sens |
|---|---|---|
| `price_nature` | texte, **obligatoire** | voir [les natures](#les-natures-de-prix) |
| `price_amount` | nombre | le montant, **dans la devise d'origine**, jamais converti |
| `price_currency` | code ISO | `USD`, `EUR`, `GBP`, `CHF`, `HKD`… |
| `price_date` | `AAAA-MM-JJ` | la date du prix. Attention : son sens dépend de la source (voir plus bas) |
| `estimate_low`, `estimate_high` | nombres | la fourchette d'estimation d'un lot d'enchères |
| `price_nature_provenance` | texte | comment la nature a été établie (voir plus bas) |
| `listing_status` | texte | `active`, `inactive`, `sold`, `unsold`, `withdrawn`, `unknown` |
| `price_includes_premium` | vrai / faux / vide | pour une enchère : frais acheteur inclus ou marteau nu. Vide chez un marchand |

### La montre

| Champ | Type | Sens |
|---|---|---|
| `brand` | texte | la marque, sous son nom canonique (voir le filtre) |
| `model` | texte | le nom du modèle, quand la source le publie |
| `reference` | texte | la référence constructeur (`116610LN`, `5711/1A`) |
| `reference_provenance` | texte | d'où vient la référence (voir plus bas) |
| `title` | texte | le titre de l'annonce, sur une ligne |
| `source_category` | texte | la catégorie telle que la source la nomme |
| `year`, `case_material`, `case_size_mm`, `movement`, `dial_color`, `condition` | | les caractéristiques, quand elles sont publiées |
| `seller` | texte | le vendeur, sur une place de marché |

### Le filtre

| Champ | Sens |
|---|---|
| `filter_verdict` | `GARDER`, `REJETER` ou `QUARANTAINE` |
| `filter_rule` | la règle qui a tranché (`R0` … `R8`) |
| `filter_version` | l'horodatage du `filters.json` utilisé |

Voir [le guide du filtre](guides/filtre.md).

## Les natures de prix

| Nature | Sens | Qui la produit |
|---|---|---|
| `realised` | enchère conclue : le lot est parti à ce prix | maisons de ventes |
| `sold` | vente conclue hors enchères | marchands qui archivent leurs ventes, places de marché |
| `asking` | prix demandé, annonce en cours | marchands |
| `estimate` | estimation avant vente | maisons de ventes |
| `msrp` | prix neuf catalogue | détaillants agréés |

Seules `realised` et `sold` sont des transactions. Un prix demandé est une
opinion : il ne devient une information qu'observé dans le temps (baisse, puis
disparition de l'annonce) ou comparé aux prix réalisés de la même référence. Le
rapport mesuré entre les deux, sur 275 paires, est de 0,87.

## Provenance de la nature

| Valeur | Sens | Fiabilité |
|---|---|---|
| `champ_dedie` | la source publie explicitement la nature | la meilleure |
| `declaree_tag` | la boutique étiquette la fiche (`sold-watches-archive`) | bonne |
| `deduite_statut` | déduite d'un statut (disponible ou non, marteau présent ou non) | moyenne |
| `constante_source` | déclarée pour toute la source par l'adaptateur | la plus faible : ne distingue pas un vendu d'un invendu |

## Provenance de la référence

| Valeur | Sens |
|---|---|
| `champ_dedie` | la source publie la référence dans un champ à part |
| `extrait_titre` | trouvée par mot-clé dans le titre (« ref. 16710 ») |
| `jeton_titre` | reconnue à sa forme dans le titre, sans mot-clé ; 99 % de précision mesurée |
| `extrait_description` | trouvée dans le corps de l'annonce ; moins sûre |
| `sku` | le code interne du vendeur ; souvent **pas** une référence |

Le schéma refuse une référence sans provenance.

## Le socle

Une ligne appartient au **socle**, la base sur laquelle une cote peut être
calculée, quand elle réunit quatre conditions :

- le filtre l'a gardée ;
- elle porte une référence sûre (champ dédié, titre ou jeton) ;
- elle a une date ;
- sa nature est une transaction (`realised` ou `sold`).

## Les pièges connus

**La date n'a pas le même sens partout.** Pour une enchère, c'est le jour de la
vente. Pour un marchand Shopify, c'est la mise en ligne de l'annonce, pas la
vente. Pour certaines sources sans date, c'est le jour du relevé. Comparer des
dates entre natures sans le savoir fausse les courbes.

**Les frais acheteur.** Christie's, Phillips, Monaco Legend, Cottone et Morphy
publient le prix frais inclus ; Artcurial, Lyon & Turnbull, Sworders et Grailzee
le marteau nu ; Antiquorum et Fortuna le précisent lot par lot. L'écart est de
25 à 30 %. On ne reconstitue **jamais** un marteau en divisant par un taux : les
barèmes sont dégressifs et changent selon les ventes.

**Les devises.** Les montants restent dans leur devise d'origine. Ne jamais
comparer deux lignes de devises différentes ; la conversion se fera à
l'affichage, avec une table de taux datée.

**Le biais de survie.** Un marchand retire ses annonces vendues. Ce qui reste en
ligne est ce qui ne s'est pas vendu, souvent parce que c'est trop cher.

## Le manifeste d'une collecte

Chaque `data/runs/<horodatage>.json` décrit un run : pour chaque source, le
nombre de lignes rendues et nouvelles, le nombre de requêtes, la période
couverte, la complétude de chaque champ en pour cent, la répartition du filtre,
l'erreur éventuelle et le journal de l'adaptateur. Le drapeau `complet` vaut
`false` tant que la collecte court : un manifeste partiel ne sert jamais de
référence pour détecter un effondrement de volume.

## La suite : la base Postgres

Le journal JSONL est la forme actuelle. La forme cible est une base Postgres dont
le schéma est décrit dans [ARCHITECTURE.md §4](ARCHITECTURE.md#4-la-base-de-données-étape-3-du-plan) :
une table d'annonces, et une table d'**observations** qui garde une ligne par
annonce et par jour de relevé. C'est ce journal qui permettra de déduire une
vente de la disparition d'une annonce.
