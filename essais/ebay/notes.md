# eBay — Browse API

## Identité
- **Source :** eBay  ·  **URL :** <https://developer.ebay.com>
- **Type :** marketplace
- **Statut :** en test — auth à valider en sandbox, production bloquée
- **Nature du prix :** **demandé** (annonces actives) — voir « Le piège » plus bas

## Accès
- **API officielle**, pas de scraping. Browse API (`/buy/browse/v1`).
- Compte développeur + keyset requis : <https://developer.ebay.com/my/keys>
  - App ID (Client ID), Cert ID (Client Secret). Le Dev ID ne sert pas ici.
  - Deux jeux séparés : **Sandbox** et **Production**.
- **Auth : OAuth2 `client_credentials`.** Token applicatif valable ~2h.
  Pas de consentement utilisateur, pas de redirect URI — c'est ce qui rend
  cette source simple comparée aux autres API eBay.
- Le scope s'écrit `https://api.ebay.com/oauth/api_scope` **même en sandbox**
  (identifiant de permission, pas une adresse à appeler). Piège classique.
- Header `X-EBAY-C-MARKETPLACE-ID` obligatoire sur chaque appel (`EBAY_US`…).
- **Rate limit :** quota journalier par keyset, à lire sur le dashboard
  développeur. À confirmer et à noter ici : `____ appels/jour`.
- Pas de JavaScript, pas d'anti-bot : c'est une API.

## État actuel du keyset
- **Sandbox : actif.** Mais c'est une fausse boutique quasi vide → sert
  uniquement à valider la plomberie (auth + parsing), pas à juger la data.
- **Production : DISABLED.** eBay exige la conformité « marketplace account
  deletion / closure notification » avant d'activer. Deux voies :
  1. **Exemption** — valable seulement si on ne stocke aucune donnée
     d'utilisateur eBay. Or un **vendeur est un utilisateur eBay** : si on
     garde `seller`, on n'est probablement pas exemptable.
  2. **Endpoint de notification** — une route HTTPS qui répond au challenge
     eBay (SHA-256 de `challengeCode + verificationToken + endpointURL`).
     Faisable sur le Vercel existant. **Voie retenue.**
     Attention : `proxy.ts` protège toutes les routes par défaut → la route
     doit être déclarée publique côté Clerk, sinon le GET de vérification
     d'eBay part en redirect vers `/sign-in` et la validation échoue.

## Format de la data
- JSON propre. Deux niveaux :
  - `item_summary/search` → liste paginée (limit ≤ 200, offset).
  - `item/{itemId}` → fiche complète, **seul endroit où vivent les
    `localizedAspects`** (marque, référence, année, mouvement, matériau…).
- Champs : titre, prix + devise, état, vendeur, localisation, images, aspects.
- **Historique : aucun.** Browse ne donne que l'instant présent. L'historique
  se construit par snapshots répétés (même conclusion que pour les marchands,
  cf. `audit_durabilite.md`).

### Complétude mesurée (à remplir après le pilote en production)
| Champ | % rempli |
|---|---|
| Brand | |
| Model | |
| Reference Number | |
| Year Manufactured | |
| Movement | |
| Case Material | |

C'est **le** chiffre qui décide de la valeur de la source. Un prix sans
référence identifiable n'entre pas dans le modèle.

## Le piège (important pour le Plan2)
Le `Plan2` classe eBay en nature de prix « **vendu** ». C'est inexact pour ce
qui est accessible aujourd'hui :

| API | Donne | Nature | Accès |
|---|---|---|---|
| **Browse** | annonces actives | **demandé** | ouvert, token app |
| **Marketplace Insights** | ventes conclues 90j | **vendu** | sur approbation |
| Feed | dumps bulk | demandé | partenaire, gros volume |

- La **Finding API** (`findCompletedItems`), qui donnait historiquement les
  ventes, a été dépréciée puis retirée → pas de plan B officiel.
- Donc : Browse nous donne la même nature de prix que les marchands déjà
  acquis (Amsterdam VW, Hodinkee). **Candidater à Marketplace Insights dès
  maintenant**, délai long et réponse incertaine.

## Légal
- Usage encadré par l'**API License Agreement** (à lire, lien en pied du
  portail développeur). Point critique pour nous : les **restrictions de
  rétention** des données eBay. À trancher **avant** de figer le schéma DB,
  puisque le cœur du produit est l'historique de prix.
- Bandeau du portail : *« Usernames will be replaced with immutable user
  IDs »* → si on stocke un vendeur, **clé sur l'ID immuable, jamais sur le
  username**, sinon la table est à reconstruire.
- Pas de robots.txt à respecter ici : c'est une API officielle, pas du scraping.

## Trouvailles / notes de test
- (à remplir)

## Échantillons
- `samples/search_*.json` — sortie brute de `explore.py search`
- `samples/pilot_summaries.json` — lot d'annonces du pilote
- `samples/pilot_items.json` — fiches détaillées (avec aspects)
