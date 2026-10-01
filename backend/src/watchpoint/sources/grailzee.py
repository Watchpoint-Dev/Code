"""Grailzee — plateforme d'ENCHERES horlogeres sur socle Shopify. Prix VENDUS.

Socle Shopify, mais ce n'est PAS une boutique : c'est une salle des ventes.
Le moteur generique `_shopify` ne peut pas la collecter, et il ne faut surtout
pas l'y brancher — pour une raison mesuree le 21/09/2026 :

  LE PRIX SHOPIFY EST LA COMMISSION, PAS LE PRIX DE LA MONTRE. La variante ne
  sert qu'a encaisser les frais d'acheteur (5 %, minimum 250, maximum 5 000 —
  bareme lu dans l'app : `fee:{minimum:250,maximum:5e3,percentage:.05}`). Sur
  la page 99 de products.json, 67 lots vendus sur 120 portent exactement
  250,00 : le plancher de commission. Un Tag Heuer Carrera Tourbillon sortait
  a 550,00 — c'est 5 % de 11 000, le vrai prix marteau. Brancher `_shopify`
  ici aurait donc ecrit 25 000 prix de montres compris entre 250 et 3 412 $.
  Les lots en cours, eux, portent 0,00 : aucun prix du tout.

  Le VRAI prix se lit dans l'API publique de l'app d'encheres, sans compte et
  sans cookie : /apps/auctioneer/api/auctions/<id_produit>. Elle rend
  `currentBid` (le marteau), `completedAt` (LA DATE DE LA TRANSACTION),
  `hasAuctionSold`, `make`, `model` et — champ dedie, chose rare —
  `referenceNumber.referenceNumber` : '126610LN', 'CAR5A8K.FT6172'.
  Verifications du 21/09/2026 : frais 550 -> currentBid 11 000 ; frais 1 350 ->
  27 000. La reconstitution frais/0,05 n'est PAS fiable (un Datejust a 15 000
  ne portait que 550 de frais) : seule l'API dit le prix.

  L'interface web affiche « log in to see current bid » : c'est un habillage,
  l'API repond a tout le monde. On ne franchit donc aucune protection et on ne
  se fait passer pour personne — les frais publics restent publics.

COUT : UNE REQUETE PAR LOT. C'est le prix a payer pour la nature `realised`,
la plus rare du dossier. Le journal l'annonce a chaque collecte.

FRAIS D'ACHETEUR : `currentBid` est le MARTEAU NU, hors commission de 5 %.
`price_includes_premium=False`, verifie par l'arithmetique des frais ci-dessus.

INVENDUS : un lot peut finir `auctioneer-completed` avec un `currentBid` eleve
et `hasAuctionSold=false` — une Submariner 126610LN s'est arretee a 11 800 sans
vendeur ni acheteur declare. Ce n'est PAS une transaction : ces lots sont
comptes et ecartes, pas charges.

VOLUME : 110 fichiers sitemap produits, mais products.json est plafonne par la
plateforme a page*limit = 25 000, et la page 99 repond encore 250 lots : le
catalogue accessible sature ce plafond. La page 1 n'est que du direct (250 lots
a 0,00), la page 99 porte 229 lots conclus sur 250. Le rang exact ou les lots
conclus commencent n'est PAS mesure (budget de requetes) : a faire avant la
vague 4, sinon les premieres pages coutent des requetes pour rien.

ROBOTS (lu le 21/09/2026) : `Disallow: /collections/all` et
`Disallow: /apps/auctioneer/members/*`. On ne touche ni l'un ni l'autre.
/products.json et /apps/auctioneer/api/ ne sont pas interdits.

Reconnaissance du 21/09/2026 — essais/grailzee/notes.md
"""
from __future__ import annotations

import json
import os
import re

from watchpoint.schema import price_point, reference_dans, reference_libre
from watchpoint.commun.utils import get

SOURCE = {
    "id": "grailzee",
    "name": "Grailzee",
    "type": "auction",
    "price_nature": "realised",
    "access": "products.json (liste des lots) + /apps/auctioneer/api/auctions/<id> (prix marteau)",
    "robots": "OK — /collections/all et /apps/auctioneer/members/* interdits, evites ; lu le 21/09/2026",
    "corpus_horloger": True,
    "reserve": "une requete API par lot ; le prix Shopify est la commission d'acheteur, "
               "jamais le prix de la montre",
}

DOMAINE = "grailzee.com"
API = f"https://{DOMAINE}/apps/auctioneer/api/auctions"
PAR_PAGE = 250
PLAFOND_SHOPIFY = 25000     # page * limit ; au-dela la plateforme repond 400
TAG_CONCLU = "auctioneer-completed"
# 'No Reserve - 2023 Rolex Submariner...' : le prefixe precede l'annee.
_ANNEE = re.compile(r"^\s*(?:no reserve\s*-\s*)?(19\d{2}|20[0-2]\d)\b", re.I)


def _annee(titre) -> int | None:
    trouve = _ANNEE.match(str(titre or ""))
    return int(trouve.group(1)) if trouve else None


def _tags(produit: dict) -> set:
    etiquettes = produit.get("tags") or []
    if isinstance(etiquettes, str):
        etiquettes = etiquettes.split(",")
    return {str(t).strip().lower() for t in etiquettes}


def fiche(enchere: dict) -> dict | None:
    """Une reponse de /api/auctions/<id> -> un enregistrement, ou None.

    None couvre deux cas distincts et tous deux legitimes : le lot n'a pas
    trouve preneur (`hasAuctionSold` faux), ou il n'a recu aucune enchere.
    """
    if not isinstance(enchere, dict) or not enchere.get("id"):
        return None
    if not enchere.get("hasAuctionSold"):
        return None
    try:
        montant = float(enchere.get("currentBid") or 0)
    except (TypeError, ValueError):
        return None
    if montant <= 0:
        return None

    titre = enchere.get("title") or None
    # La reference est un CHAMP DEDIE ici — une table de references, pas un
    # texte libre : {'id': 104, 'referenceNumber': '126610LN'}.
    bloc = enchere.get("referenceNumber") or {}
    reference = (bloc.get("referenceNumber") or "").strip() or None if isinstance(bloc, dict) \
        else str(bloc).strip() or None
    provenance = "champ_dedie" if reference else None
    if not reference:
        reference = reference_dans(titre)
        provenance = "extrait_titre" if reference else None
    if not reference:
        reference = reference_libre(titre)
        provenance = "jeton_titre" if reference else None

    # `completedAt` est la date de CLOTURE DE LA TRANSACTION, pas une mise en
    # ligne : c'est exactement ce qui manque partout ailleurs dans le dossier.
    conclu = str(enchere.get("completedAt") or enchere.get("endsAt") or "")[:10] or None

    return price_point(
        source_id=SOURCE["id"], source_type=SOURCE["type"],
        source_url=f"https://{DOMAINE}/products/{enchere.get('handle')}",
        external_id=str(enchere["id"]),
        # Une vente aux encheres rend un prix `realised`. Les lots passes par
        # la place de marche integree (tag `auctioneer-marketplace`, negociation
        # de gre a gre) sont des ventes conclues mais pas des adjudications :
        # `sold`. La source declare elle-meme lequel des deux.
        price_nature="sold" if enchere.get("isMarketplace") else "realised",
        price_nature_provenance="champ_dedie",
        listing_status="sold",
        # Marteau NU : la commission de 5 % est encaissee a part, par la
        # variante Shopify du lot. Mesure : frais 550 -> marteau 11 000.
        price_includes_premium=False,
        price_amount=montant, price_currency="USD",
        price_date=conclu,
        brand=(enchere.get("make") or "").strip() or None,
        model=(enchere.get("model") or "").strip() or None,
        reference=reference, reference_provenance=provenance,
        title=titre,
        year=_annee(titre),
        seller=SOURCE["name"],
    )


def lots_du_brut(entrees: list) -> list:
    """Les reponses d'API contenues dans le brut, pour le rejeu hors ligne.

    Les pages products.json sont conservees elles aussi, mais elles ne portent
    aucun prix de montre : seules les reponses /api/auctions/ sont rejouables.
    """
    trouves = []
    for entree in entrees:
        if "/api/auctions/" not in str(entree.get("url", "")):
            continue
        try:
            trouves.append(json.loads(entree.get("payload", "")))
        except (json.JSONDecodeError, AttributeError, TypeError):
            continue
    return trouves


def _pages_demandees() -> tuple[int, int] | None:
    """La tranche de pages a parcourir, pour collecter le catalogue par morceaux.

        WP_GRAILZEE_PAGES=31-36 python -m watchpoint collecte grailzee

    Meme motif que WP_ANTIQUORUM_ANNEES, et pour la meme raison mesuree : une
    source n'est ecrite qu'une fois terminee. Le catalogue complet coute une
    requete par lot conclu, soit environ 230 par page profonde et une dizaine
    d'heures en tout ; d'un seul bloc, une coupure reseau a la neuvieme heure
    perdrait tout. Une tranche de quelques pages (moins d'une heure) borne la
    perte. Le 01/10/2026, le plafond de 1 200 lots a ete atteint en page 31.
    """
    brut = os.environ.get("WP_GRAILZEE_PAGES", "").strip()
    debut, _, fin = brut.partition("-")
    if debut.strip().isdigit() and fin.strip().isdigit():
        return int(debut), int(fin)
    return None


def collect(cap: int = 1200, depart: int = 1, pause: float = 2.0):
    """Les lots CONCLUS, page par page, avec un appel d'API par lot.

    `depart` permet de reprendre a une page donnee : la page 1 n'est que du
    direct (aucun lot conclu), les pages profondes en sont pleines. Il sert
    aussi a prouver la source sur un echantillon sans parcourir le catalogue.
    """
    raw: list[dict] = []
    records: list[dict] = []
    journal: list[str] = []
    en_cours = invendus = pages = 0
    tranche = _pages_demandees()
    fin = None
    if tranche:
        depart, fin = tranche
        cap = 10 ** 9      # une tranche est bornee par ses pages, pas par un plafond de lots
        journal.append(f"TRANCHE demandee : pages {depart} -> {fin}")
    page = depart

    while len(records) < cap:
        if fin is not None and page > fin:
            break
        if page * PAR_PAGE > PLAFOND_SHOPIFY:
            journal.append(
                f"PLAFOND SHOPIFY: page*limit > {PLAFOND_SHOPIFY} — la plateforme "
                f"refuse d'aller plus loin, les lots plus anciens sont inaccessibles")
            break
        try:
            resp = get(f"https://{DOMAINE}/products.json",
                       params={"limit": PAR_PAGE, "page": page,
                               "currency": "USD", "country": "US"}, pause=pause)
        except Exception as exc:
            journal.append(f"products.json p{page}: {type(exc).__name__}")
            break
        raw.append({"url": resp.url, "status": resp.status_code, "payload": resp.text})
        if resp.status_code != 200:
            journal.append(f"products.json p{page}: HTTP {resp.status_code}")
            break
        try:
            produits = json.loads(resp.text).get("products", [])
        except json.JSONDecodeError:
            journal.append(f"products.json p{page}: JSON illisible")
            break
        if not produits:
            journal.append(f"products.json p{page}: catalogue epuise")
            break
        pages += 1

        for produit in produits:
            if TAG_CONCLU not in _tags(produit):
                en_cours += 1          # enchere en cours : aucun prix conclu
                continue
            try:
                rep = get(f"{API}/{produit.get('id')}", pause=pause)
            except Exception as exc:
                journal.append(f"api/auctions/{produit.get('id')}: {type(exc).__name__}")
                continue
            raw.append({"url": rep.url, "status": rep.status_code, "payload": rep.text})
            if rep.status_code != 200:
                journal.append(f"api/auctions/{produit.get('id')}: HTTP {rep.status_code}")
                if rep.status_code in (401, 403, 429):
                    journal.append("MUR: l'API refuse — on s'arrete, pas de reessai en boucle")
                    return raw, records[:cap], journal
                continue
            try:
                enchere = json.loads(rep.text)
            except json.JSONDecodeError:
                continue
            enregistrement = fiche(enchere)
            if enregistrement is None:
                invendus += 1
                continue
            records.append(enregistrement)
            if len(records) >= cap:
                break

        if len(produits) < PAR_PAGE:
            break
        page += 1

    journal.append(f"pages products.json parcourues: {pages} (depart p{depart})")
    journal.append(f"{en_cours} lots en cours de vente ecartes (aucun prix conclu)")
    journal.append(f"{invendus} lots termines SANS vente ecartes (enchere haute mais pas d'acheteur)")
    journal.append(f"COUT: une requete API par lot conclu — {len(records)} lots charges")
    if len(records) >= cap:
        journal.append(f"TRONQUE: plafond de {cap} atteint — il reste des donnees a prendre")
    return raw, records[:cap], journal
