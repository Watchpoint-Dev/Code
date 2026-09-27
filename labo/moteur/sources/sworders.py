"""Sworders — maison de ventes anglaise. Prix MARTEAU, sans date.

Une source qu'on atteint par la porte de service. Son index de resultats ne
publie que les 57 ventes recentes, et ses pages de vente sont a 80 % de la
joaillerie : les prendre entieres couterait des heures pour le rendement de
Lyon & Turnbull. Mais sa RECHERCHE, elle, interroge toute l'archive — et elle
rend 96 lots par page, chacun avec son prix adjuge.

On interroge donc marque par marque. Ce n'est pas un pis-aller : c'est la seule
facon d'atteindre les vingt et un ans d'archive sans ramener cinquante mille
bagues avec.

CE QUE CETTE SOURCE NE DONNE PAS : la date de vente. Elle vit sur la fiche du
lot, une requete de plus par lot, et le site impose un `Crawl-delay: 10`. A
huit cents lots pour la seule marque Omega, ce serait plus de deux heures pour
une seule marque. Ces lignes rejoignent donc Watchtrader : une reference et un
prix, mais aucun socle. C'est dit, et c'est mesure.

Le delai de politesse est respecte : 10 secondes entre deux pages, comme le
robots.txt le demande.

Reconnaissance et mise en service le 29/08/2026.
"""
from __future__ import annotations

import html as _html
import re

from filtre import filtre
from schema import parse_money, price_point, reference_dans, reference_libre
from utils import get

SOURCE = {
    "id": "sworders",
    "name": "Sworders",
    "type": "auction",
    "price_nature": "realised",
    "access": "recherche par marque, 96 lots par page",
    "robots": "OK — Crawl-delay: 10 respecte",
    "reserve": "aucune date de vente : la source ne la publie que sur la fiche du lot",
}

BASE = "https://www.sworder.co.uk"
RECHERCHE = f"{BASE}/auction/search"
PAR_PAGE = 96
# Le robots.txt demande 10 secondes. On les prend.
DELAI = 10.0

# Les marques interrogees. Ce n'est pas le dictionnaire complet du filtre —
# huit cents pages a dix secondes seraient deux heures pour rien : ce sont les
# marques que la maison vend reellement, mesurees sur son archive le 29/08/2026.
MARQUES = ("rolex", "omega", "cartier", "longines", "jaeger", "tudor", "breitling",
           "iwc", "patek", "tag heuer", "heuer", "zenith", "seiko", "tissot",
           "vacheron", "audemars", "panerai", "hublot", "bremont", "smiths",
           "garrard", "eterna", "movado", "universal geneve", "girard perregaux",
           "baume", "raymond weil", "bulova", "accurist", "j w benson")

_BLOC = re.compile(r'<div class="auction-lot">(.*?)<div class="clearfix"></div>', re.S)
_IDENTIFIANT = re.compile(r'\?lot=(\d+)')
# Le titre court jusqu'a la fin du lien, pas jusqu'au premier </span> : le
# balisage insere un <span class="req-tag"></span> VIDE juste apres le numero
# de lot, et s'arreter la ne capturait rien. Mesure du 29/08/2026 — les 2 506
# lignes sortaient sans titre, donc sans marque, donc toutes rejetees par R3.
_TITRE = re.compile(r"lot-title[^>]*>(.*?)</a>", re.S)
_NUMERO_EN_TETE = re.compile(r"^Lot\s*[\w\d]*\s*", re.I)
_PRIX = re.compile(r'Sold for\s*([£€$])\s*([\d,]+)', re.S)
_LIEN = re.compile(r'href="(/auction/lot/[^"?]+)')
_VENDU = re.compile(r'corner-flash-sold')
_BALISES = re.compile(r"<[^>]+>")
_DEVISES = {"£": "GBP", "€": "EUR", "$": "USD"}


def _texte(brut) -> str:
    return re.sub(r"\s+", " ", _html.unescape(_BALISES.sub(" ", str(brut or "")))).strip()


def fiche(bloc: str) -> dict | None:
    """Un bloc de resultat -> un enregistrement, ou None si le lot n'est pas vendu."""
    # Un lot sans 'SOLD' est retire ou en cours : il ne dit rien d'une
    # transaction, et la recherche n'en publie pas le montant.
    if not _VENDU.search(bloc):
        return None
    prix = _PRIX.search(bloc)
    identifiant = _IDENTIFIANT.search(bloc)
    if not (prix and identifiant):
        return None
    montant, _ = parse_money(prix.group(2))
    if not montant:
        return None

    trouve = _TITRE.search(bloc)
    titre = _NUMERO_EN_TETE.sub("", _texte(trouve.group(1))) if trouve else None
    lien = _LIEN.search(bloc)

    reference = reference_dans(titre)
    provenance = "extrait_titre" if reference else None
    if not reference:
        reference = reference_libre(titre)
        provenance = "jeton_titre" if reference else None

    return price_point(
        source_id=SOURCE["id"], source_type=SOURCE["type"],
        source_url=f"{BASE}{lien.group(1)}" if lien else None,
        external_id=identifiant.group(1),
        price_nature="realised",
        # MARTEAU NU, verifie et non suppose. Les conditions disent que
        # l'acheteur paie « the hammer price, plus a buyer's premium » de 27 %,
        # mais cela dit ce qu'on paie, pas ce que la page affiche. Le controle
        # arithmetique tranche : sur 96 montants, 77 % tombent sur un echelon
        # d'enchere tels quels, contre 8 % apres division par 1,27. C'est donc
        # un marteau, comme Artcurial et l'inverse de Christie's.
        price_nature_provenance="deduite_statut",
        price_includes_premium=False,
        listing_status="sold",
        price_amount=montant,
        price_currency=_DEVISES.get(prix.group(1), "GBP"),
        # La source ne date pas ses ventes ici. On ne fabrique pas de date :
        # une date de releve ferait passer une vente de 2005 pour recente.
        price_date=None,
        # La maison ne publie aucun champ de marque : elle vit en tete de
        # titre, quand elle y est. On la lit avec le dictionnaire du filtre,
        # comme le fait le moteur Shopify pour les boutiques sans `vendor`.
        brand=filtre().verdict(titre or "", "AUCTION").get("brand"),
        title=titre,
        reference=reference, reference_provenance=provenance,
        condition="preowned",
        seller=SOURCE["name"],
    )


def lots_du_brut(entrees: list) -> list[tuple]:
    """(bloc,) pour chaque lot d'une collecte deja stockee."""
    trouves = []
    for entree in entrees:
        for bloc in _BLOC.finditer(entree.get("payload") or ""):
            trouves.append((bloc.group(1),))
    return trouves


def collect(cap: int = 12000):
    raw: list[dict] = []
    journal: list[str] = []
    records: list[dict] = []
    vus: set[str] = set()

    for marque in MARQUES:
        if len(records) >= cap:
            break
        avant, page = len(records), 1
        while len(records) < cap:
            try:
                resp = get(RECHERCHE, params={"st": marque, "ic": "True",
                                              "pp": PAR_PAGE, "pn": page},
                           pause=DELAI)
            except Exception as exc:
                journal.append(f"{marque} p{page}: {type(exc).__name__}")
                break
            raw.append({"url": resp.url, "status": resp.status_code,
                        "payload": resp.text})
            if resp.status_code != 200:
                journal.append(f"{marque} p{page}: HTTP {resp.status_code}")
                break

            blocs = list(_BLOC.finditer(resp.text))
            if not blocs:
                break
            nouveaux = 0
            for bloc in blocs:
                enregistrement = fiche(bloc.group(1))
                if enregistrement is None:
                    continue
                # Une meme montre remonte sur plusieurs marques : 'Jaeger' et
                # 'Universal Geneve' partagent des lots co-signes.
                if enregistrement["external_id"] in vus:
                    continue
                vus.add(enregistrement["external_id"])
                records.append(enregistrement)
                nouveaux += 1
            if len(blocs) < PAR_PAGE or nouveaux == 0 and page > 1:
                break
            page += 1
        journal.append(f"{marque} : {len(records) - avant} lots en {page} page(s)")

    journal.append("AUCUNE DATE : la source ne publie la date de vente que sur "
                   "la fiche du lot, inatteignable a 10 s de delai par requete")
    if len(records) >= cap:
        journal.append(f"TRONQUE: plafond de {cap} atteint — il reste des donnees a prendre")
    return raw, records, journal
