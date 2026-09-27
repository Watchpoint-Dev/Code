# Watchpoint — Point d'étape

**23 août 2026** · Support de réunion associés

---

## En une minute

- On sait **d'où viendront les prix**. Les 210 sources du registre ont été testées une par une.
- On a **3 345 prix réels en base**, collectés automatiquement, tous datés.
- Le site est **en ligne** mais affiche encore des **données fictives**. C'est l'écart à combler.
- **Trois décisions bloquent la suite**, et aucune n'est technique.

---

## 1. Ce qui est fait

### La plateforme

- Site en ligne sur Vercel, authentification et base de données fonctionnelles
- Dépôt de code privé, intégration continue qui vérifie chaque modification
- Deux environnements séparés : production et préproduction
- **Limite connue** : toutes les montres et tous les prix affichés sont fictifs

### Le moteur de collecte

- Un modèle de données unique : chaque prix porte sa **nature**, sa **date**, sa **devise** et sa **source**
- Cinq adaptateurs écrits, trois qui collectent aujourd'hui
- Collecte **relançable et idempotente** : on peut la jouer tous les jours sans doublon
- Le moteur **signale ses pannes** au lieu de rendre un résultat vide en silence
- Données brutes conservées, pour pouvoir tout re-traiter sans re-télécharger

### La base actuelle

| Source | Prix | Nature | Période |
|---|---:|---|---|
| Christie's | 1 356 | réalisé en enchère | 2024 → 2026 |
| Craft & Tailored | 1 000 | demandé chez un marchand | 2024 → 2026 |
| WatchRecon | 989 | demandé sur forums | 14 derniers jours |

- **3 345 prix**, 99 % datés, 256 marques distinctes
- Montants de 27 à 889 000, toutes devises conservées telles que publiées

### La cartographie des sources

- **210 sources testées**, la totalité du registre
- **122 ouvertes** en profondeur, **44 creusées** en détail avec extraction réelle
- **5 093 fiches téléchargées** pour mesurer la qualité réelle des données
- Chaque source porte son **niveau de preuve** : vérifiée à la main, analyse dédiée, page ouverte, ou accessibilité seule

**Résultat du tri :**

| Catégorie | Sources |
|---|---:|
| Exploitables | **24** |
| À creuser | 36 |
| À démarcher | **69** |
| Fermées ou sans intérêt | 81 |

### Les erreurs corrigées

Ce point compte autant que le reste : plusieurs conclusions antérieures étaient fausses.

- **Le prix neuf n'est pas récupérable.** Une analyse d'août affirmait le contraire ; vérification faite, ce qu'elle prenait pour 266 prix Patek étaient des adresses d'images.
- **Trois sources du batch validé en juillet sont mortes** : LiveAuctioneers, Antiquorum, WatchBox.
- **Un bug de devise faussait 51 % de la base de −17,8 %.** Corrigé, données recollectées.
- **Deux adaptateurs rendaient des dates fausses.** Corrigés, données purgées.

---

## 2. Où on en est vraiment

### Les cinq natures de prix

| Nature | Ce que c'est | Statut |
|---|---|---|
| **Réalisé** | le marteau d'une enchère | acquis, 2 sources |
| **Demandé** | ce qu'un vendeur affiche | acquis, 3 sources |
| **Vendu** | une transaction hors enchère | acquis, source à brancher |
| **Prix neuf** | le tarif catalogue de la marque | **négociation obligatoire** |
| **Indice** | la courbe de tendance du marché | **négociation obligatoire** |

**Trois natures sur cinq sont couvertes par la collecte directe.** Les deux autres ne s'obtiendront jamais sans accord commercial.

### La profondeur historique

- **Aujourd'hui en base : deux ans**
- **Accessible sans négocier : dix-neuf ans**

Deux maisons de ventes analysées en détail remontent bien plus loin :

| Source | Historique prouvé | Volume | Effort |
|---|---|---:|---|
| **Artcurial** | 2007 | 8 454 lots | 1 jour |
| **Cottone** | 2009 | 33 750 lots | 1 jour |

C'est le meilleur rapport travail/valeur du dossier. Deux jours de développement font passer la profondeur de 2 ans à 19.

---

## 3. Ce qui bloque

### Décision 1 — TypeScript ou Python

- Ouverte depuis le **12 juillet**
- Conditionne l'outil de base de données, les bibliothèques de collecte, l'hébergement
- **Rien de la phase suivante ne démarre proprement sans elle**
- Le site reste en TypeScript quoi qu'il arrive : la question ne porte que sur le moteur de données

### Décision 2 — Que fait-on du prix demandé ?

- **59 % de la base** est du prix demandé
- Un prix demandé n'est pas un prix, c'est une opinion : un marchand peut afficher 40 000 pendant deux ans sans vendre
- Il devient exploitable dans trois cas : **suivi dans le temps**, **en masse**, ou **rapporté au réalisé**
- Trois questions produit en découlent :
  - affiche-t-on jamais un prix demandé seul à l'utilisateur ?
  - comment le distingue-t-on visuellement d'une vraie valeur ?
  - garde-t-on l'historique des révisions de prix ? (cela change le modèle de données)

### Décision 3 — Engage-t-on les démarchages ?

- Sans accord sur les indices, **cette fonctionnalité n'existera pas** dans le produit
- Ce n'est pas un manque de volume, c'est une brique absente

---

## 4. Les sources à démarcher

69 lignes au registre, mais **une vingtaine d'interlocuteurs réels** (certaines sources sont listées par région).

### Priorité 1 — ce qu'aucune autre source ne remplace

| Interlocuteur | Ce qu'on demande |
|---|---|
| **WatchCharts** (partenaire Morgan Stanley) | licence de données ou API d'indices |
| **Chrono24 / ChronoPulse** | API ou partenariat data |

### Priorité 2 — ce qui débloque une nature de prix

| Interlocuteur | Ce qu'on demande |
|---|---|
| **eBay** | API Marketplace Insights, les prix réellement vendus |
| **Patek Philippe, Grand Seiko, AP, Omega, Cartier, IWC, Tudor** | accès au tarif catalogue |
| **EveryWatch** | l'antériorité avant 2024 (2,5 ans sont gratuits) |

### Priorité 3 — de la profondeur historique

| Interlocuteur | Ce qu'on demande |
|---|---|
| **Barnebys** | flux licencié d'enchères |
| **Phillips, Sotheby's** | accès aux résultats de ventes |
| **Invaluable, the-saleroom, LiveAuctioneers** | prix réalisés |

### Priorité 4 — les forums

- WatchUSeek, Rolex Forums, WatchProSite, TimeZone, plus la clé API Reddit
- **Impact limité** : WatchRecon les agrège déjà et nous est accessible
- Remonte en priorité 2 si l'indice de sentiment devient un objectif

---

## 5. La semaine prochaine

### À décider en réunion

| Décision | Temps |
|---|---|
| TypeScript ou Python pour le moteur | 30 min |
| Liste des sources à brancher en premier | 30 min |
| Feu vert sur les démarchages, et qui s'en charge | 30 min |

### À faire côté développement

| Tâche | Temps | Dépend de |
|---|---|---|
| Brancher Artcurial et Cottone | 2 jours | décision 2 |
| Créer la base de développement | 0,5 jour | décision 1 |
| Concevoir le modèle de données | 2 jours | décisions 1 et 2 |
| Débloquer les clés eBay production | 0,5 jour | rien |

**Sans les décisions, le chantier principal — le modèle de données — ne peut pas commencer.**

---

## 6. Les directions ouvertes

Trois pistes identifiées pendant l'analyse, à arbitrer plus tard.

### Un indice de sentiment, façon fear & greed

- Personne ne le fait sur ce marché, et la matière existe déjà
- Quatre signaux mesurables **sans analyse de texte** : volume d'annonces, durée avant disparition, baisses de prix, écart demandé/réalisé
- Question ouverte : à quelle maille ? par marque, par type de montre, ou par segment de prix

### Déduire les ventes à partir des disparitions

- Une annonce relevée chaque jour qui disparaît a été vendue ou retirée
- Croisée avec une baisse de prix juste avant, on approche le prix de transaction
- **Transformerait 59 % de la base** de prix demandé en signal de prix vendu

### Un adaptateur générique pour les boutiques

- 28 boutiques répondent au même point d'accès standard
- Un seul adaptateur, un dictionnaire de domaines : ajouter une boutique devient une ligne

---

## Le mot de la fin

**Trois sources sont mortes en trois semaines.** LiveAuctioneers, Antiquorum, WatchBox. Deux faisaient partie de nos cinq sources validées en juillet.

Ce marché se ferme progressivement. Ce qui est accessible aujourd'hui ne le sera pas forcément dans six mois.

C'est l'argument pour **engager les démarchages maintenant** plutôt qu'après avoir fini la technique : un accord signé prend de la valeur pendant que les portes se ferment.

---

_Tous les chiffres de ce document sont vérifiables. Chaque source porte son niveau de preuve dans le fichier `DECISION_SOURCES_2026-08-11.xlsx`. Les verdicts techniques ont une date de péremption : ils sont rejouables en une commande._
