# Le filtre : est-ce une montre ?

Une maison de ventes vend aussi des bijoux, des pendules, des boîtes vides, des
bracelets seuls. Un marchand vend des remontoirs et des enseignes de vitrine. Le
filtre répond à une seule question pour chaque annonce : est-ce une montre
complète, oui ou non ?

Il ne vérifie ni la référence ni la nature du prix. Ce sont d'autres contrôles.

## Les trois verdicts

| Verdict | Sens |
|---|---|
| `GARDER` | l'annonce entre dans les calculs |
| `REJETER` | elle n'y entre pas, mais la ligne reste en base avec la règle qui l'a rejetée |
| `QUARANTAINE` | le texte ne permet pas de trancher ; à échantillonner à la main |

**Le filtre ne supprime jamais rien, il marque.** Chaque ligne porte
`filter_verdict`, `filter_rule` et `filter_version`. Comme le brut est conservé,
un filtre corrigé se rejoue sur tout l'historique en quelques secondes, sans une
requête réseau.

## L'arbre de décision

Les règles s'appliquent dans cet ordre ; la première qui conclut l'emporte.

| Règle | Question | Conclusion |
|---|---|---|
| **R0** | la source a-t-elle classé l'objet elle-même (« Necklaces », « Mens Watches ») ? | `REJETER` si la catégorie nomme une famille non horlogère |
| **R1** | le titre contient-il une exclusion dure (bijou, pendule, contrefaçon, lot mélangé) ? | `REJETER` |
| R1b | … sauf un réveil *au poignet*, qui reste une montre | exception |
| **R2** | le titre nie-t-il la catégorie (« no watch », « sans montre », « ohne Uhr ») ? | `REJETER` |
| **R3** | une marque connue apparaît-elle ? | `REJETER` sinon : sans marque, on ne garde pas |
| R3b | montre de poche chez une marque qui n'en a jamais fait ? | `REJETER` |
| **R4** | marque au nom ambigu (Universal, Hamlet…) sans le mot « montre » ? | `REJETER` |
| R4b | … sauf si le titre porte une référence | exception |
| R4c | … sauf si la source ne vend que des montres (`corpus_horloger`) | exception |
| **R5** | l'objet est-il vendu seul (« bracelet only », « cadran seul ») ? | `REJETER` |
| **R6** | « no box no papers » : décrit l'accompagnement d'une montre | `GARDER` |
| R6b | « white dial », « cadran tropical » : un qualificatif descriptif | `GARDER` |
| R6c | deux accessoires cités ensemble décrivent une montre complète | `GARDER` |
| **R7a** | le texte ne tranche pas : la catégorie de la source tranche | `GARDER` ou `QUARANTAINE` |
| **R8** | rien ne s'oppose à l'entrée | `GARDER` |

Le détail et les cas limites de chaque règle sont commentés dans
`backend/src/watchpoint/filtrage/filtre.py`, avec la mesure qui a justifié chaque
ajustement.

## Où vit la configuration

```
backend/config/filtres/
├── Filtres_scrapping.xlsx   la couche humaine : la SEULE qu'on édite
└── filters.json             compilé depuis l'Excel ; le moteur ne lit que lui
```

Les onglets du classeur :

| Onglet | Contenu |
|---|---|
| `README` | la spécification de l'arbre |
| `BRANDS` | les 242 marques, leurs alias, leur portée (enchères, marchands), `accept_pocket`, `requires_category_token` |
| `CATEGORY_TOKENS` | les mots qui disent « montre » dans chaque langue |
| `EXCLUSIONS` | les termes d'exclusion, par concept (bijou, pendule, pièce détachée…) |
| `MARKERS` | les marqueurs d'accompagnement et de description (R6) |
| `ATTRIBUTES` | le vocabulaire d'extraction des attributs (matière, mouvement…) |
| `TEST_CASES` | les 76 cas de test, avec le verdict attendu |
| `JOURNAL` | chaque modification datée, son motif et son effet mesuré |

## Modifier le filtre

Le filtre n'est jamais figé. Chaque modification suit la même boucle, et aucune
étape ne se saute :

```bash
# 0. l'état avant
backend/.venv/bin/python -m watchpoint filtre --base > /tmp/avant.txt

# 1. modifier l'Excel, puis compiler
backend/.venv/bin/python -m watchpoint compile-filtre

# 2. les cas de test : tous doivent passer
backend/.venv/bin/python -m watchpoint filtre

# 3. l'effet sur la base réelle, source par source
backend/.venv/bin/python -m watchpoint filtre --base > /tmp/apres.txt
diff /tmp/avant.txt /tmp/apres.txt

# 4. si l'effet est celui attendu, re-marquer tout l'historique
backend/.venv/bin/python -m watchpoint filtre --marquer

# 5. consigner dans l'onglet JOURNAL : date, motif, effet mesuré
```

L'étape 3 est celle qui compte. Un correctif qui fait passer les tests peut
faire entrer des centaines de lignes de déchet ailleurs : c'est arrivé le 21/09,
quand une règle assouplie a laissé entrer 166 enseignes de vitrine et 59 objets
promotionnels. Seule la comparaison sur le brut l'a montré.

Ajouter un cas de test dans `TEST_CASES` pour chaque erreur corrigée, afin
qu'elle ne revienne pas.

## Ce que le filtre ne sait pas encore bien faire

- Les montres de poche : gardées à 19 % seulement, contre 90 % pour les
  montres-bracelets (mesure du 21/09 sur Antiquorum et Morphy). Le
  dictionnaire manque d'horlogers d'avant 1900.
- Les marchands dont le titre ne cite pas la marque : chez Hairspring, la
  marque n'est retrouvée dans la description que pour une fiche sur deux.
