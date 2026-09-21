# eBay — API officielle

Fiche écrite le 21/09/2026 depuis les quatre diagnostics du 07/09/2026. Les
mesures étaient dans `diagnostic_output/` sans qu'aucun document ne les
rapporte : c'est réparé ici.

## Identité

- **Source :** eBay · **URL :** <https://api.ebay.com>
- **Type :** marketplace, API officielle (pas de scraping)
- **Statut :** accès partiel obtenu, **bridé sur ce qui compte**

## Accès — mesuré, pas supposé

| API | HTTP | Ce qu'elle donne |
|---|---|---|
| **Browse** (annonces actives) | **200** | prix **demandé**, disponible tout de suite |
| Taxonomy (métadonnées) | 200 | 46 attributs, `Reference Number` présent |
| Developer Analytics | 200 | les quotas |
| **Marketplace Insights** (prix **VENDUS**) | **403** | la donnée qui compte — sur approbation |
| Feed (téléchargement en masse) | 403 | idem |

Clés dans `.env` (ignoré par git). `ebay_client.py` porte l'authentification
OAuth ; les quatre `ebay_diagnostic*.py` sont les passes successives.

## Les chiffres qui décident

- **Quota : ~5 000 appels/jour** (mesuré : 100 appels consomment 100 unités).
- **Plafond de 10 000 résultats par requête**, mesuré au lot près : 10 062
  passe, 10 093 refusé. Toute marque plus grosse doit être découpée par bandes
  de prix.
- **Balayage complet du luxe projeté à 1 894 appels**, soit **38 % du quota
  quotidien** — extrapolé d'un balayage TUDOR réel : 6 599 annonces annoncées,
  6 732 trouvées, **102 % de couverture en 70 appels**.
- Stock : **GB 2,5 M** montres, **US 2,9 M**, DE 747 k.
- Rotation : 43 k nouvelles annonces/24 h, 309 k/7 j, 787 k/30 j.
- Formats : 2,54 M à prix fixe, 1,21 M avec offre, 58 k aux enchères.
- Pureté du champ marque, sur les marques de luxe : **90 à 100 %**.
- Complétude sur le haut de gamme : référence 50 %, marque 92 %, matière 58 %.
  Elle **baisse** quand le prix monte — 27 champs en moyenne sur le milieu de
  gamme contre 15,7 sur le très haut de gamme.

## Ce que ça veut dire pour le projet

**Browse est faisable dès demain, mais donne du prix demandé — la nature dont
le projet a déjà trop** (49 805 lignes sur 136 377). Un prix affiché seul est
une opinion, pas une transaction.

La valeur est dans **Marketplace Insights**, et l'obtenir est une **démarche
administrative, pas du code** : il faut d'abord satisfaire la conformité
« suppression de compte » (endpoint de notification côté nous), puis candidater.

Browse devient en revanche très intéressant **le jour où le journal
d'observations existe** : 43 k annonces qui tournent par jour, c'est de la
matière à « l'annonce a disparu, donc elle s'est vendue ». Aujourd'hui la base
ne stocke qu'un état, pas un journal — donc ce levier reste hors de portée.

## Légal

API officielle sous contrat développeur : pas de question de robots.txt. Deux
points à trancher avant toute collecte à l'échelle, tous deux notés dans
`notes/CARNET.md` :

- **Que dit la licence sur la durée de RÉTENTION des données ?** Critique,
  puisque le cœur du produit est l'historique de prix.
- **Stocke-t-on le vendeur ?** La réponse décide de la voie : exemption ou
  endpoint de conformité.

## Prochain pas

Candidater à Marketplace Insights. Tant que c'est 403, brancher Browse
n'ajouterait que du prix demandé à une base qui en déborde.
