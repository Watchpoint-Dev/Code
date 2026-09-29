# Glossaire

Les termes du projet, dans le sens où le code et la documentation les emploient.

**Adaptateur** — un module de `backend/src/watchpoint/sources/` qui sait lire
une source précise et la ramener au format du point de prix. Il expose `SOURCE`
et `collect()`.

**Brut** — la réponse d'un site telle que reçue, conservée compressée dans
`data/raw/`. Jamais jeté : c'est lui qui permet de rejouer un adaptateur ou un
filtre corrigé sans refaire une seule requête.

**Collecte** (ou run) — une exécution du moteur sur une ou plusieurs sources.
Chaque collecte laisse un manifeste dans `data/runs/`.

**Corpus horloger** — se dit d'une source qui ne vend que des montres. Le filtre
y est moins exigeant (règle R4c).

**Cumul** — l'ancien nom de `data/price_points.jsonl`, encore présent dans le
code. Désigne le journal de tous les prix.

**Effondrement** — alarme de fin de collecte : une source a rendu moins de 30 %
de ce qu'elle avait rendu au dernier run complet.

**Estimation** (`estimate`) — la fourchette qu'une maison de ventes publie avant
la vente. Ce n'est pas un prix de transaction.

**Frais acheteur** (buyer's premium) — la commission qu'une maison de ventes
ajoute au prix marteau, de 20 à 30 % selon les maisons et les montants. Voir
*marteau*.

**Gelée** — une source qu'on ne collecte plus parce qu'elle refuse notre robot
(403 à notre User-Agent, 200 à un navigateur). Ses données déjà collectées sont
conservées. Liste dans `GELEES`, `collecte/run.py`.

**Journal d'observations** — la forme cible de la base : une ligne par annonce
et par jour de relevé, jamais écrasée. Permet de voir un prix baisser, puis une
annonce disparaître.

**Marteau** (hammer price) — le prix auquel le commissaire-priseur adjuge le lot,
hors frais. Certaines maisons publient le marteau, d'autres le prix frais inclus.
On ne passe jamais de l'un à l'autre par calcul : les barèmes sont dégressifs.

**Nature du prix** — ce que le montant représente : réalisé, vendu, demandé,
estimation ou prix neuf. Obligatoire sur chaque ligne. Voir [donnees.md](donnees.md#les-natures-de-prix).

**Point de prix** — une ligne de la base : un montant, avec sa nature, sa date,
sa devise, sa source et l'identité de la montre. Défini dans `schema.py`.

**Prix demandé** (`asking`) — le prix affiché par un vendeur. Une intention, pas
une transaction.

**Prix neuf** (`msrp`) — le prix catalogue d'une montre neuve chez un détaillant agréé.

**Prix réalisé** (`realised`) — le résultat d'une enchère conclue.

**Provenance** — d'où vient une information : la nature du prix ou la référence
peuvent être publiées par la source, déduites, ou devinées dans le titre. La
fiabilité n'est pas la même, et le schéma l'enregistre.

**Quarantaine** — verdict du filtre quand le texte ne permet pas de trancher.

**Référence** — le code constructeur d'un modèle (`116610LN` chez Rolex,
`5711/1A` chez Patek Philippe). C'est la clé qui permet de rapprocher les prix
d'une même montre entre sources.

**Rejeu** (`rejoue`) — refaire la normalisation d'une source à partir de son
brut, sans réseau.

**Socle** — le sous-ensemble de la base sur lequel on peut calculer une cote :
gardé par le filtre, avec une référence sûre, une date, et une nature de
transaction.

**Sonde** — le contrôle d'accessibilité des sources (`python -m watchpoint sonde`) :
robots.txt, réponse du site, présence d'un anti-bot.

**Tranche** — une plage d'années collectée d'un coup chez une maison à long
historique (`antiquorum:2008-2009`). Une source n'est écrite qu'une fois
terminée, d'où l'intérêt de tranches courtes.

**Vendu** (`sold`) — une vente conclue hors enchères, publiée par un marchand ou
une place de marché.

**Verdict** — la conclusion du filtre sur une annonce : garder, rejeter ou
quarantaine. Il est inscrit sur la ligne, jamais appliqué par suppression.
