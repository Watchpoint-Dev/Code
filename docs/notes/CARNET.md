# Note et todo

Idées, tâches, questions. Tu ouvres, tu écris une ligne, tu fermes.
Aucune mise en forme demandée. Une ligne mal rangée vaut mieux qu'une ligne
jamais écrite.

Quand c'est fait, ça sort d'ici et ça va dans `PROGRESS.md`.

---

## À FAIRE

- [ ] **Choisir les sources et tout collecter.** Le dossier d'analyse est clos, il faut trancher la liste et lancer la collecte.
- [ ] **Design des objets.** Le modèle de données : ce qu'est une montre, un prix, une source, une annonce, et comment ils se lient.
- [ ] **Bien vérifier les points de la section « Questions en suspens »** avant de figer quoi que ce soit. Ils portent tous sur des choses qui corrompent les données en silence.
- [ ] Trancher **TypeScript ou Python** pour le moteur. Ouvert depuis le 12/07, bloque la phase 2.
- [ ] **Connecter l'API eBay.** Deux étapes : débloquer les clés production (conformité « suppression de compte »), puis brancher la Browse API. Elle donne du prix demandé, pas du vendu : le vendu passe par Marketplace Insights, sur approbation.
- [ ] Créer la base de dev. Aujourd'hui, tester la base revient à écrire en production.
- [ ] Relancer l'analyse du lot qui a échoué : The Keystone, A Collected Man, Bulang & Sons, Tropical Watch, Right Time, Watchdeal.
- [ ] Refaire la vérification des 13 boutiques Shopify limitées par le 429.
- [ ] Valider les conditions d'utilisation source par source avant toute collecte à l'échelle.

---

## À DÉMARCHER

**À décider.**

---

## IDÉES

### Indice de sentiment horloger, façon fear & greed

Un indice de peur et d'avidité construit sur ce que les gens disent, pas sur ce
qu'ils paient. Personne ne le fait sur ce marché, et la matière existe déjà :
WatchRecon agrège Reddit et les forums, c'est notre accès légal à ces deux mondes.

**La question ouverte, c'est la maille.** Un indice global ne dit pas grand-chose.
Trois découpages possibles :

- par marque, le plus parlant commercialement (« le sentiment Rolex se dégrade »)
- par type : plongeuse, chronographe, habillée, sport de luxe
- par segment de prix, souvent là que le signal est le plus net, parce que le
  haut de gamme et l'entrée de gamme ne réagissent jamais ensemble

**Quatre signaux mesurables tout de suite, sans analyse de texte :**

1. le volume d'annonces. Beaucoup de vendeurs d'un coup, c'est de la peur.
2. la durée avant disparition d'une annonce. Ça part vite, c'est de l'avidité.
3. les baisses de prix sur une annonce qui traîne. Le vendeur capitule.
4. l'écart entre prix demandé et prix réalisé sur un même modèle.

Le ton des messages viendrait en dernier. C'est le plus lourd à construire et le
moins fiable.

Deux réserves à écrire noir sur blanc si l'indice sort du projet. WatchRecon ne
montre que 14 jours, donc l'indice se construit à partir de maintenant, sans
antériorité. Et une communauté de forum n'est pas le marché : c'est un segment de
passionnés, plutôt masculin, plutôt occidental, plutôt vintage.

### Déduire les ventes à partir des disparitions

On manque cruellement de prix « vendu ». Mais si on relève les annonces chaque
jour, une annonce qui disparaît a été vendue ou retirée. Croisée avec une baisse
de prix juste avant, on approche le prix de transaction.

Ça transformerait nos sources de prix demandé en source de prix vendu, la nature
qui nous manque le plus après l'indice. À creuser sérieusement.

### Un adaptateur Shopify et WooCommerce générique

28 boutiques répondent au même endpoint standard. Un seul adaptateur, un
dictionnaire de domaines, et ajouter une boutique devient une ligne de config.

### Plus petit, mais qui traîne

- Vérification automatique hebdomadaire des sources. Trois sont mortes en trois semaines.
- Garder le prix en devise native ET converti. EveryWatch ne donne que du converti.
- Un budget de requêtes partagé par domaine entre tous les scripts. Ils se comptent
  poliment chacun dans leur coin, mais rien ne compte le total. C'est comme ça qu'on
  s'est fait limiter par treize boutiques d'un coup.

---

## QUESTIONS EN SUSPENS

### Le prix demandé, c'est exploitable ou c'est du bruit ?

C'est la question la plus importante du projet, et elle n'a jamais été tranchée.
Elle porte sur **1 989 de nos 3 345 prix, soit 59 %**.

Les quatre natures, pour fixer le vocabulaire :

| Nature | Ce que c'est | Fiabilité |
|---|---|---|
| réalisé | le marteau d'une enchère | une transaction, incontestable |
| vendu | un échange conclu hors enchère | une transaction aussi |
| demandé | ce qu'un vendeur affiche | **une opinion, pas un prix** |
| prix neuf | le tarif catalogue du fabricant | une référence, pas un marché |

**Pourquoi ces natures ne sont pas comparables entre elles**, et c'est ce qu'il
faut documenter source par source :

- Un **réalisé** est le résultat d'une enchère publique. Il intègre l'émotion du
  moment, la concurrence dans la salle, et souvent les frais acheteur. Il peut
  dépasser l'estimation de 30 % comme rester en dessous.
- Un **vendu** hors enchère sort d'une négociation privée. Il est presque toujours
  inférieur au prix affiché au départ, de 5 à 15 % selon les marchands.
- Un **demandé** est un point de départ de négociation. Le marchand y intègre sa
  marge, son coût de stockage, et son espoir. Il ne devient un prix que le jour
  où quelqu'un l'accepte.
- Un **prix neuf** est fixé par la marque, pas par le marché. Sur les modèles
  recherchés, le marché de l'occasion se traite au-dessus du neuf ; sur les autres,
  bien en dessous. Il sert de repère, jamais de valeur.

Donc un écart entre deux prix de la même montre ne veut rien dire tant qu'on ne
sait pas de quelles natures il s'agit. **C'est à écrire dans la documentation de
chaque source** : quelle nature elle produit, si les frais sont inclus, et ce que
le chiffre recouvre exactement.

Un prix demandé peut être n'importe quoi. Un marchand peut afficher 40 000 pendant
deux ans sans jamais vendre. Pris isolément, c'est du bruit.

Il devient exploitable dans trois cas :

1. **Suivi dans le temps.** Une baisse de 12 % en trois mois est un signal fort,
   même si le prix affiché est faux dans l'absolu.
2. **En masse.** La médiane de 200 annonces d'une même référence approche le marché
   bien mieux qu'une annonce isolée.
3. **Rapporté au réalisé.** L'écart demandé/réalisé sur un même modèle est sans
   doute l'indicateur le plus intéressant qu'on puisse produire.

Trois décisions en découlent, à écrire dans la doc de chaque source :

- affiche-t-on jamais un prix demandé seul, ou toujours accompagné du réalisé ?
- comment le signale-t-on visuellement pour qu'il ne soit pas lu comme une valeur ?
- garde-t-on l'historique complet des révisions de prix d'une annonce ? C'est ce
  qui rend le premier cas possible, et ça change le modèle de données.

### Les prix ne sont pas comparables entre eux

Trois pièges trouvés pendant l'analyse. Tous silencieux, aucun ne lève d'erreur.

**Les frais acheteur.** Chez les maisons américaines, aucun prix n'est un marteau
nu. Tout inclut les frais, à un taux qui n'est même pas constant : chez New Orleans,
×1,25 sur un lot et ×1,30 sur un autre, dans la même vente. Le marteau n'est donc
pas reconstituable par division. Artcurial, elle, expose les deux séparément.
Il faut un champ « frais inclus : oui / non / inconnu » dans le modèle.

**Le biais de survivance.** Les maisons purgent les invendus des vieilles ventes.
Lyon & Turnbull 2019 affiche 411 vendus sur 411, Artcurial 416 sur 416. Tout taux
de vente ou prix moyen calculé sur l'historique profond sera surestimé.

**La devise.** EveryWatch ne publie qu'un montant converti, jamais la devise
d'origine. Bezel n'a aucun champ de devise du tout, USD est une déduction.

### La déduplication

La référence n'est renseignée qu'à 59 %. Et chez Bezel, elle identifie un modèle,
pas un exemplaire : trois annonces différentes partagent la même.

On ne sait donc ni rapprocher deux sources de façon fiable, ni distinguer deux
exemplaires du même modèle. C'est un chantier à part entière : extraction depuis
les titres, table de correspondance des références, et une clé qui accepte
l'incertitude.

### Plus court

- Que dit la licence eBay sur la durée de rétention ? Critique, puisque le cœur du
  produit est l'historique de prix.
- Stocke-t-on le vendeur ? Ça décide de la voie eBay : exemption ou endpoint.
- Le cumul stocke-t-il l'état courant ou un journal d'observations ? Le README
  annonce les deux, d'où environ 1 200 lignes redondantes à chaque run.
