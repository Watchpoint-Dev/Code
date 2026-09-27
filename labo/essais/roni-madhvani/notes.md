# Roni Madhvani

Reconnaissance du 21/09/2026. **Verdict : pas d'adaptateur. Source à retirer du
registre.** Le site n'est pas une boutique : c'est une installation WordPress
sous « Coming Soon » dont le catalogue est le jeu de démonstration livré avec
WooCommerce. 18 fiches, 18 appartiennent à la démo, 0 montre.

## Identité
- **Source :** Roni Madhvani · **URL :** <https://ronimadhvani.com/>
- **Type :** aucun — site en construction (hébergement Hostinger, LiteSpeed Cache)
- **Statut :** abandonné — à désinscrire du registre
- **id / slug proposés à la sonde :** `ronimadhvani` / `roni-madhvani` — non créés

## Accès
- WooCommerce Store API publique et fonctionnelle :
  `GET /wp-json/wc/store/v1/products?per_page=100&page=1` → HTTP 200,
  `X-WP-Total: 18`.
- Second appel obligatoire du cahier des charges, fait :
  `&stock_status=outofstock` → HTTP 200, `X-WP-Total: 0`, corps `[]`.
  **Aucune fiche épuisée** : il n'y a pas d'historique caché derrière le stock
  courant. Les 18 fiches sont tout ce que le site contient.
- **Pas de robots.txt.** `GET /robots.txt` renvoie HTTP 200 avec le HTML de la
  page « Coming Soon » (`samples/robots_txt_reponse.html`) : le serveur sert le
  gabarit pour toute URL. Même réponse sur `/wp-sitemap.xml`
  (`samples/wp_sitemap_reponse.html`). Rien n'est donc interdit — et rien n'est
  publié non plus.
- Aucun blocage, aucun 429/403. 4 requêtes, UA `utils.HEADERS` (ClaudeBot).

## Format de la data — ce que la sonde avait vu, expliqué
La sonde du 21/09 notait `signal_prix: 0`, `signal_date: 1`, `annee_min: 2026`,
2 068 octets de page d'accueil, score 33. **Les trois signaux disaient la même
chose et nous avions supposé un rendu JavaScript ou des prix sur demande. Non :**
- `signal_prix: 0` — la page d'accueil est le gabarit « Coming Soon » de
  Hostinger. Il n'y a aucun montant parce qu'il n'y a aucune vitrine.
- `annee_min: 2026` — c'est l'horodatage du cache LiteSpeed en pied de page
  (`Page cached by LiteSpeed Cache 7.8 on 2026-09-21`), pas une montre.
- 2 068 octets — la taille du gabarit, identique sur `/`, `/robots.txt` et
  `/wp-sitemap.xml`.

Les montants existent bel et bien dans l'API (`prices.price` renseigné sur 18/18,
`currency_minor_unit = 2`, `USD`) : la question du cahier des charges est
tranchée, ce ne sont **pas** des prix masqués. Ce sont les prix de la démo.

## Le catalogue, en clair
`samples/store_v1_products.json` (brut intégral) contient :

| catégorie | n |
|---|---|
| Clothing | 9 |
| Accessories | 5 |
| Footwear | 4 |

Titres : *WordPress Pennant, Logo Collection, Beanie with Logo, T-Shirt with
Logo, Single, Album, Polo, Long Sleeve Tee, Sunglasses, Cap, Beanie, T-Shirt,
Hoodie with Zipper, Hoodie with Pocket, Belt, Hoodie with Logo, Hoodie, V-Neck
T-Shirt*.

**18 sur 18 sont le jeu `woocommerce/sample-data`** livré avec le plugin
(`explore.py` le vérifie nom par nom). Les descriptions sont du lorem ipsum —
*« Pellentesque habitant morbi tristique senectus… »*. Le SKU de la première
fiche est `wp-pennant`.

## Les quatre champs qui décident
- `price_amount` / `price_currency` : présents, USD, `currency_minor_unit = 2`
  (il faudrait diviser par 100). Mais ce sont les prix d'un t-shirt de démo.
- `price_date` : **`date_created` est `null` sur 18 fiches sur 18.** Zéro date,
  ni transaction ni mise en ligne. Profondeur datée : néant.
- `reference` : aucun attribut de référence. Les seuls attributs publiés sont
  `color` (11), `size` (1), `Logo` (1). Taux de référence constructeur : 0 %.
- `price_nature` : indéterminable, et sans objet.

Le moteur `_woo.py` normaliserait ces 18 lignes sans broncher — c'est bien le
risque : le générique est robuste, il ne sait pas qu'une boutique est vide.
Le filtre les rejetterait ensuite (R0 sur *Clothing* / *Footwear*), mais faire
tourner un adaptateur pour produire 18 rejets n'a aucun intérêt.

## Légal
- Contenu public, aucune authentification, aucune protection contournée. Sans
  objet : il n'y a pas de donnée.

## Conclusion
- **Aucun adaptateur écrit.** `moteur/sources/ronimadhvani.py` n'existe pas.
  `moteur/sources/__init__.py` n'a pas été touché.
- **À retirer du registre** — feuille « Toutes les sources » du classeur que lit
  `moteur/sonde.py --registre` (`WP/output/referentiels/DataSources.xlsx`, absent
  de l'arbre de travail actuel). Retrait à faire par le détenteur du registre,
  pas ici. Motif : *site en construction, catalogue = jeu de démonstration
  WooCommerce, 18 fiches, 0 montre, 0 date — mesuré le 21/09/2026*.
- **Réexamen possible** si le site s'ouvre un jour : relancer `explore.py`
  après un nouvel appel à l'API Store. Le signal à guetter est simple —
  `X-WP-Total` supérieur à 18 et des titres hors du jeu de démonstration.
- **Enseignement pour la sonde** : un score de 33 avec `signal_prix: 0`,
  `signal_date: 1` et une page d'accueil de ~2 ko n'est pas une boutique à prix
  masqués, c'est la signature d'un gabarit « Coming Soon ». Deux tests à faible
  coût la reconnaissent : la même réponse sur `/` et `/robots.txt`, et un
  catalogue dont les titres sont ceux de `woocommerce/sample-data`.

## Échantillons
- `samples/store_v1_products.json` — les 18 fiches, brut intégral, `X-WP-Total: 18`
- `samples/store_v1_products_outofstock.json` — `[]`, second appel obligatoire
- `samples/accueil.html` — la page « Coming Soon »
- `samples/robots_txt_reponse.html` — ce que renvoie `/robots.txt` (le gabarit)
- `samples/wp_sitemap_reponse.html` — idem sur `/wp-sitemap.xml`
- `samples/mesure_api.txt` — sortie de `explore.py`
- `explore.py` — rejoue la décision depuis les échantillons, sans réseau
