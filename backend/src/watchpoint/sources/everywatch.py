"""EveryWatch — agregateur de resultats d'encheres. La plus grosse source.

573 015 lots annonces en `auctionType=result`, dont **environ 210 000 portent
reellement une date et un prix**. C'est du prix REALISE DATE, la matiere la plus
rare et la plus utile du dossier, et c'est plus que tout le reste de la base
reuni.

Acces : Next.js SSR. Le `buildId` fait partie de l'URL et change a chaque
deploiement du site — il se lit dans le HTML de la page d'accueil, jamais en dur.

    https://everywatch.com/_next/data/{buildId}/watch-listing.json
        ?auctionType=result&brand={slug}&pageSize=1000&pageNumber=1

QUATRE PIEGES, tous mesures le 28/08/2026, tous silencieux :

  LA FENETRE DE 24 MOIS. Au-dela de deux ans, l'API continue de renvoyer les
  lots — avec leur reference, leur maison de vente, leur estimation — mais
  AMPUTES de leur date de vente et de tous leurs montants. Aucune erreur, aucun
  signal : `isRestrictedAccessToListing` passe simplement a true. Sur la tranche
  Hublot, 1 309 lots sur 3 528 seulement sont datés et prixes. Un collecteur
  naif croirait avoir 573 015 lots et n'en aurait qu'un tiers d'utilisables.

  `page` EST IGNORE. Le parametre s'appelle `pageNumber`. Passer `page=2`
  renvoie la page 1 en HTTP 200 : on peut aspirer indefiniment le meme lot.

  `pageNumber` PLAFONNE A 10. Au-dela, le serveur rend 200 avec une page de
  cache perimee de 48 lignes. Le plafond reel d'une requete est donc
  pageSize x 10, d'ou le decoupage par marque.

  LE PRIX PUBLIE EST FRAIS INCLUS. `netPayableUsd` est ce que l'acheteur a paye.
  Le marteau n'est expose que sur la fiche detail — mais `buyersPremiumRate` est
  present a 100 %, donc le marteau se reconstruit sans une requete de plus. On
  charge le prix publie, et le drapeau `price_includes_premium` le dit.

RESERVES : les invendus ne sont pas publies (lotStatusId vaut 2 partout), donc
biais de survie. Et `currencyName` est nul : les montants sont pre-convertis par
EveryWatch en huit devises. On prend l'USD, et cette conversion n'est pas la
notre.

Reconnaissance du 28/08/2026.
"""
from __future__ import annotations

import json
import re

from watchpoint.schema import price_point
from watchpoint.commun.utils import get

SOURCE = {
    "id": "everywatch",
    "name": "EveryWatch",
    "type": "aggregator",
    "price_nature": "realised",
    "access": "endpoint Next.js /_next/data/{buildId}/watch-listing.json",
    "robots": "OK — 'User-agent: * / Allow: /', seul Amazonbot est banni",
    "corpus_horloger": True,
    "reserve": "fenetre glissante de 24 mois ; invendus non publies ; montants "
               "pre-convertis en USD par la source",
}

BASE = "https://everywatch.com"
_BUILD = re.compile(r'"buildId"\s*:\s*"([^"]+)"')
PAGE = 500           # charge utile raisonnable, et rythme lent : le site
                     # nous a bloques une premiere fois le 28/08 pour avoir
                     # demande 1 000 lots par requete sans pause suffisante
PAGES_MAX = 10       # plafond dur : au-dela, le serveur rend du cache perime

# Le decoupage se fait par marque, en slug. Les marques les plus echangees
# d'abord : c'est la ou sont les volumes et les references.
MARQUES = (
    "rolex", "patek-philippe", "omega", "cartier", "audemars-piguet",
    "jaeger-lecoultre", "breitling", "iwc", "tudor", "vacheron-constantin",
    "panerai", "longines", "heuer", "tag-heuer", "zenith", "hublot",
    "a-lange-sohne", "chopard", "piaget", "blancpain", "breguet", "seiko",
    "grand-seiko", "universal-geneve", "girard-perregaux", "ulysse-nardin",
    "bulgari", "montblanc", "baume-mercier", "eberhard-co", "movado",
    "tissot", "glashutte-original", "franck-muller", "richard-mille",
    "f-p-journe", "roger-dubuis", "hermes", "chanel", "gucci",
)


def _build_id(raw: list, journal: list) -> str | None:
    """Le buildId change a chaque deploiement : on le relit a chaque collecte."""
    try:
        resp = get(BASE, pause=1.0)
    except Exception as exc:
        journal.append(f"page d'accueil: {type(exc).__name__}")
        return None
    raw.append({"url": resp.url, "status": resp.status_code, "payload": resp.text[:4000]})
    trouve = _BUILD.search(resp.text)
    if not trouve:
        journal.append("buildId introuvable dans la page d'accueil — le site a change")
        return None
    journal.append(f"buildId {trouve.group(1)}")
    return trouve.group(1)


def _lots(charge) -> list:
    donnee = charge.get("pageProps", {}) if isinstance(charge, dict) else {}
    listing = donnee.get("listingData") or {}
    lots = listing.get("listing")
    return lots if isinstance(lots, list) else []


def fiche(lot: dict) -> dict | None:
    """Un lot EveryWatch -> un enregistrement, ou None s'il est hors fenetre.

    Un lot au-dela de 24 mois revient sans date ni montant : il n'est pas une
    observation de prix, seulement une fiche de catalogue. On ne l'ingere pas.
    """
    montant = lot.get("netPayableUsd")
    date = lot.get("eventPublistStartDate")
    if not montant or not date:
        return None

    reference = (lot.get("referenceNumber") or "").strip() or None
    if reference and not re.search(r"\d", reference):
        reference = None
    titre = " ".join(x for x in (lot.get("manufactureName"), lot.get("modelName"),
                                 lot.get("title"), reference) if x)[:300]

    return price_point(
        source_id=SOURCE["id"], source_type=SOURCE["type"],
        source_url=lot.get("sourceLink") or f"{BASE}/watch-{lot.get('id')}",
        external_id=str(lot.get("id")),
        price_nature="realised",
        price_nature_provenance="champ_dedie",
        listing_status="sold",
        # `netPayable*` est le prix PAYE, frais acheteur compris. Le marteau
        # se reconstruit par `buyersPremiumRate`, present a 100 %, mais on
        # charge la valeur publiee et on la qualifie.
        price_includes_premium=True,
        price_amount=float(montant),
        # `currencyName` est nul : la source pre-convertit en huit devises.
        # On prend l'USD en sachant que la conversion n'est pas la notre.
        price_currency="USD",
        price_date=date,
        estimate_low=lot.get("estimateLowUsd"), estimate_high=lot.get("estimateHighUsd"),
        brand=lot.get("manufactureName"),
        model=lot.get("modelName"),
        reference=reference,
        reference_provenance="champ_dedie" if reference else None,
        title=titre or None,
        seller=lot.get("organizationName"),
    )


def lots_du_brut(entrees: list) -> list[tuple]:
    trouves = []
    for entree in entrees:
        if "watch-listing.json" not in entree.get("url", ""):
            continue
        try:
            charge = json.loads(entree.get("payload", ""))
        except (json.JSONDecodeError, AttributeError):
            continue
        trouves.extend((lot,) for lot in _lots(charge) if isinstance(lot, dict))
    return trouves


def collect(cap: int = 120000):
    raw: list[dict] = []
    journal: list[str] = []
    records: list[dict] = []
    vus: set[str] = set()

    build = _build_id(raw, journal)
    if not build:
        return raw, records, journal
    url = f"{BASE}/_next/data/{build}/watch-listing.json"

    hors_fenetre = 0
    for marque in MARQUES:
        if len(records) >= cap:
            break
        avant = len(records)
        for page in range(1, PAGES_MAX + 1):
            if len(records) >= cap:
                break
            params = {"auctionType": "result", "brand": marque,
                      "pageSize": PAGE, "pageNumber": page}
            try:
                resp = get(url, params=params, pause=3.0)
            except Exception as exc:
                journal.append(f"{marque} p{page}: {type(exc).__name__}")
                break
            raw.append({"url": resp.url, "status": resp.status_code, "payload": resp.text})
            if resp.status_code != 200:
                journal.append(f"{marque} p{page}: HTTP {resp.status_code}")
                break
            try:
                lots = _lots(json.loads(resp.text))
            except json.JSONDecodeError:
                journal.append(f"{marque} p{page}: JSON illisible")
                break
            if not lots:
                break

            nouveaux = 0
            for lot in lots:
                enregistrement = fiche(lot)
                if enregistrement is None:
                    hors_fenetre += 1
                    continue
                if enregistrement["external_id"] in vus:
                    continue
                vus.add(enregistrement["external_id"])
                records.append(enregistrement)
                nouveaux += 1

            # Le serveur rend du cache perime au lieu d'une erreur : si une page
            # n'apporte plus rien de neuf, on arrete cette marque.
            if len(lots) < PAGE or nouveaux == 0:
                break

        journal.append(f"{marque} : {len(records) - avant} lots dates et prixes")

    journal.append(f"{hors_fenetre} lots ecartes : hors de la fenetre de 24 mois, "
                   f"servis sans date ni montant")
    if len(records) >= cap:
        journal.append(f"TRONQUE: plafond de {cap} atteint — il reste des donnees a prendre")
    return raw, records, journal
