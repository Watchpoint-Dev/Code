# Barnebys

## Identité
- **Source :** Barnebys  ·  **URL :** https://www.barnebys.com
- **Type :** enchères (agrégateur de résultats de maisons de ventes)
- **Statut :** à explorer

## Accès
- A priori scraping HTML (pas d'API publique connue à ce stade).
- À vérifier : le site charge-t-il les résultats en JavaScript (→ playwright) ou
  le HTML brut contient-il déjà les données / du JSON embarqué (`__NEXT_DATA__`,
  JSON-LD) ?
- Respecter un rythme de requêtes raisonnable.

## Format de la data (à confirmer par les tests)
- Attendu : lots d'enchères montres — titre, maison de vente, prix
  estimé/adjugé, date, lieu, image.
- Historique : Barnebys agrège des résultats passés → potentiellement riche en
  **prix réalisés** datés.

## Légal
- Vérifier les Conditions d'utilisation de Barnebys (scraping autorisé ou non).
- Données de résultats d'enchères = publiques, mais valider le cadre avant usage.

## Trouvailles / notes de test
- (à remplir : ce que renvoie explore.py, où sont les données dans la page)

## Échantillons
- Dans `samples/`
