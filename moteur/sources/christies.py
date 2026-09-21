"""Christie's — maison de ventes. Prix REALISES avec date : le socle historique.

Acces : API JSON interne du site (discoverywebsite). Deux appels enchaines —
le calendrier des ventes passees, puis les lots de chaque vente montres.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import pathlib
import re

import requests

from schema import parse_money, price_point, reference_dans
from utils import get

# Christie's est derriere Akamai, et Akamai n'aime pas qu'on se deguise.
# Mesure du 25/08/2026, meme URL, meme minute :
#
#     User-Agent Chrome (nos en-tetes communs)  ->  ReadTimeout a 20 s
#     User-Agent 'WatchpointBot/1.0'            ->  ReadTimeout a 20 s
#     User-Agent 'Mozilla/5.0' nu               ->  ReadTimeout a 20 s
#     User-Agent 'curl/8.4.0'                   ->  HTTP 200 en 0,09 s
#     User-Agent par defaut de python-requests  ->  HTTP 200 en 0,05 s
#
# Un client qui annonce un navigateur sans en avoir l'empreinte TLS est mis en
# attente ; un outil qui s'annonce comme outil passe. On dit donc ce qu'on est.
# Ce n'est pas un contournement, c'est l'inverse : on cesse de mentir.
ENTETES = {"User-Agent": requests.utils.default_user_agent()}

SOURCE = {
    "id": "christies",
    "name": "Christie's",
    "type": "auction",
    "price_nature": "realised",
    "access": "API JSON interne (discoverywebsite)",
    "robots": "OK — les Disallow visent */search, */AjaxPages… ; 'lotsearch' n'est pas '/search'",
    # Le corpus est garanti horloger (seules les ventes dont le titre porte 'watch' sont collectees) : R4 n'a pas
    # a exiger le mot "montre" dans le titre pour valider une marque ambigue.
    "corpus_horloger": True,
}

# Le calendrier des ventes passees ne bouge plus : on le garde sur disque.
CACHE = pathlib.Path(__file__).resolve().parents[2] / "data" / "cache" / "christies_calendrier.json"

COMPONENT = "e7d92272-7bcc-4dba-ae5b-28e4f3729ae8"
CALENDAR = "https://www.christies.com/api/discoverywebsite/auctioncalendar/auctionresults"
LOTSEARCH = "https://www.christies.com/api/discoverywebsite/auctionpages/lotsearch"

# 2020 -> 2026 : sept ans de resultats, contre trois auparavant. Le
# calendrier est interroge mois par mois, la profondeur ne coute que du temps.
YEARS = tuple(range(2026, 2019, -1))
# Les 12 mois : echantillonner 4 mois ne ramenait que 5 ventes montres sur les 14
# de 2025, soit ~36 % du "socle historique" — sans que rien ne le signale.
MONTHS = tuple(range(1, 13))
PAGES_PAR_VENTE = 4
TAILLE_PAGE = 84


def _deep_find(obj, key):
    """La liste utile est emboitee a une profondeur variable selon l'endpoint."""
    if isinstance(obj, dict):
        if isinstance(obj.get(key), list) and obj[key]:
            return obj[key]
        for value in obj.values():
            found = _deep_find(value, key)
            if found:
                return found
    elif isinstance(obj, list):
        for value in obj:
            found = _deep_find(value, key)
            if found:
                return found
    return None


def _split_estimate(text):
    """'USD 100,000 - 200,000' -> (100000.0, 200000.0)"""
    if not text:
        return None, None
    parts = re.split(r"\s*[-–]\s*", str(text))
    low, _ = parse_money(parts[0])
    high, _ = parse_money(parts[1]) if len(parts) > 1 else (None, None)
    return low, high


# La description de Christie's n'est pas de la prose : c'est une fiche technique
# etiquetee. Mesure du 25/08/2026 sur 3 006 lots : CIRCA 100 %, CASE MATERIAL
# 99 %, MOVEMENT 98 %, DIAL 98 %, CASE DIAMETER 80 %. Ces cinq champs etaient a
# zero dans la base alors que la source les publie sur presque chaque lot.
_ETIQUETTE = re.compile(r"([A-Z][A-Z /&-]{2,24}):\s*([^<\n]{1,120})")
_BALISES = re.compile(r"<[^>]+>")


def _specifications(description) -> dict:
    """'CASE MATERIAL: Stainless steel' -> {'CASE MATERIAL': 'Stainless steel'}"""
    if not description:
        return {}
    texte = _BALISES.sub("\n", str(description))
    return {cle.strip(): valeur.strip(" .,;")
            for cle, valeur in _ETIQUETTE.findall(texte) if valeur.strip(" .,;")}


def _millimetres(valeur):
    trouve = re.search(r"(\d{1,3}(?:[.,]\d)?)\s*mm", str(valeur or ""), re.I)
    return float(trouve.group(1).replace(",", ".")) if trouve else None


def _annee(valeur):
    trouve = re.search(r"\b(1[89]\d{2}|20[0-2]\d)\b", str(valeur or ""))
    return int(trouve.group(1)) if trouve else None


def _devise_estimation(text):
    """La devise d'un invendu ne peut venir que de son estimation."""
    if not text:
        return None
    _, devise = parse_money(str(text).split("-")[0])
    return devise


def _brand_from_title(title):
    """Heuristique : Christie's titre ses lots 'ROLEX, A STAINLESS STEEL...'.

    Le fabricant est le segment en capitales avant la premiere virgule. On ne
    devine rien au-dela : mieux vaut un champ vide qu'une marque inventee.
    """
    if not title:
        return None
    head = str(title).split(",")[0].strip()
    return head.title() if 0 < len(head) <= 30 and head.isupper() else None


def _reference_from_title(title):
    """'... REF. 116509, NO. 1/1' -> '116509'"""
    return reference_dans(title)


def _annees() -> tuple:
    """Les annees a parcourir, surchargeables pour collecter par tranches.

        WP_CHRISTIES_ANNEES=2020,2021 python moteur/run.py christies

    Sept ans d'un coup font une collecte longue ; la couper en tranches permet
    de la reprendre la ou elle s'est arretee.
    """
    brut = os.environ.get("WP_CHRISTIES_ANNEES", "").strip()
    if not brut:
        return YEARS
    return tuple(int(a) for a in brut.split(",") if a.strip().isdigit())


def _cache_calendrier() -> dict:
    if CACHE.exists():
        try:
            return json.loads(CACHE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def _ventes_montres(raw, journal):
    """Repere les ventes montres, mois par mois, et retient ce qu'elle a trouve.

    Le calendrier d'une annee passee ne change plus : le redemander a chaque
    collecte, c'est 84 requetes jetees. On le garde donc sur disque, et une
    collecte interrompue reprend la ou elle s'etait arretee au lieu de tout
    recommencer.
    """
    cache = _cache_calendrier()
    ventes = []
    annee_courante = dt.date.today().year
    mois_courant = dt.date.today().month
    nouveaux_mois = 0

    for year in _annees():
        for month in MONTHS:
            cle = f"{year}-{month:02d}"
            # Le mois en cours et le suivant peuvent encore bouger ; le reste
            # du passe est definitif.
            fige = (year, month) < (annee_courante, mois_courant)
            if fige and cle in cache:
                ventes.extend(cache[cle])
                continue
            params = {"language": "en", "month": month, "year": year, "component": COMPONENT}
            try:
                resp = get(CALENDAR, params=params, pause=1.0, headers=ENTETES)
            except Exception as exc:
                # Un mois perdu est un mois perdu ; ce n'est pas une raison pour
                # jeter les six annees deja parcourues.
                journal.append(f"calendrier {month}/{year}: {type(exc).__name__}")
                continue
            raw.append({"url": resp.url, "status": resp.status_code, "payload": resp.text})
            if resp.status_code != 200:
                journal.append(f"calendrier {month}/{year}: HTTP {resp.status_code}")
                continue
            try:
                events = _deep_find(json.loads(resp.text), "events") or []
            except json.JSONDecodeError:
                journal.append(f"calendrier {month}/{year}: JSON illisible")
                continue
            du_mois = []
            for event in events:
                if not re.search(r"watch", str(event.get("title_txt", "")), re.I):
                    continue
                landing = event.get("landing_url", "")
                sale_id = re.search(r"SaleID=(\d+)", landing)
                sale_no = re.search(r"SaleNumber=(\d+)", landing)
                if sale_id and sale_no:
                    du_mois.append({"titre": event.get("title_txt"), "sale_id": sale_id.group(1),
                                    "sale_number": sale_no.group(1), "annee": year})
            ventes.extend(du_mois)
            cache[cle] = du_mois
            nouveaux_mois += 1
            # Ecriture apres CHAQUE mois : une collecte tuee en cours de route
            # garde ce qu'elle a deja decouvert.
            CACHE.parent.mkdir(parents=True, exist_ok=True)
            CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1),
                             encoding="utf-8")

    journal.append(f"calendrier : {nouveaux_mois} mois interroges, "
                   f"{len(cache)} mois en cache")
    return ventes


def fiche(lot: dict) -> dict | None:
    """Un lot Christie's -> un enregistrement normalise.

    Isolee de la collecte pour que moteur/rejoue.py puisse refaire toute la
    normalisation sur le brut deja stocke, sans redemander une page.

    Deux champs longtemps ignores et repris ici :

      `description_txt` porte une reference dans 88 % des lots, contre 68 %
      pour le titre seul (mesure du 25/08/2026 sur 3 006 lots). On lit donc le
      titre d'abord, la description ensuite, avec des provenances distinctes.

      `lot_withdrawn` distingue un lot RETIRE d'un lot invendu. Les deux n'ont
      pas de prix marteau, mais ils ne disent pas la meme chose : l'un n'a
      jamais ete presente, l'autre a ete refuse par la salle.
    """
    titre = lot.get("title_primary_txt")
    if not titre:
        return None
    description = lot.get("description_txt") or ""

    # Les champs numeriques existent : inutile de reparser le texte affiche.
    # PIEGE : quand ils sont absents, Christie's rend la CHAINE VIDE et non
    # null. Tester `is None` ne mord donc jamais, et un '' traverse tout le
    # pipeline pour finir en montant absent. On teste la faussete.
    montant = lot.get("price_realised") or None
    if montant is None:
        montant, _ = parse_money(lot.get("price_realised_txt"))
    bas = lot.get("estimate_low") or None
    haut = lot.get("estimate_high") or None
    if bas is None:
        bas, haut = _split_estimate(lot.get("estimate_txt"))

    vendu = bool(montant)
    retire = bool(lot.get("lot_withdrawn"))
    # Un lot retire avant la vente n'a ni marteau ni estimation : il n'a pas de
    # prix du tout. Le garder ferait entrer une ligne sans montant ni devise
    # dans une base de prix. On le laisse dans le brut, pas dans le cumul.
    if not montant and not bas:
        return None
    _, devise = parse_money(lot.get("price_realised_txt") or lot.get("estimate_txt"))

    reference = _reference_from_title(titre)
    provenance = "extrait_titre" if reference else None
    if not reference:
        reference = _reference_from_title(description)
        provenance = "extrait_description" if reference else None

    specs = _specifications(description)

    return price_point(
        source_id=SOURCE["id"], source_type=SOURCE["type"],
        # Le champ `url` du lot est un lien de CONNEXION (/en/sso?ObjectID=...)
        # qui rend 404 : verifie le 25/08/2026 sur quatre lots tires au hasard.
        # La vraie fiche est /en/lot/lot-{object_id}, qui redirige vers la page
        # publique du lot.
        source_url=(f"https://www.christies.com/en/lot/lot-{lot.get('object_id')}"
                    if lot.get("object_id") else lot.get("url")),
        external_id=str(lot.get("object_id") or lot.get("lot_id_txt")),
        # Un lot sans prix marteau n'a pas ete vendu. L'appeler "realise"
        # etiquetait des invendus comme des transactions : c'est le contraire
        # qu'ils disent, le marche a refuse ce prix.
        price_nature="realised" if vendu else "estimate",
        price_nature_provenance="deduite_statut",
        listing_status="sold" if vendu else ("withdrawn" if retire else "unsold"),
        # Christie's publie le prix FRAIS INCLUS, pas le marteau : mesure du
        # 25/08/2026, 39 % seulement des montants sont des marteaux ronds contre
        # 97 % chez Artcurial.
        price_includes_premium=True,
        price_amount=montant if vendu else bas,
        price_currency=devise,
        price_date=lot.get("start_date"),
        estimate_low=bas, estimate_high=haut,
        brand=_brand_from_title(titre),
        reference=reference, reference_provenance=provenance,
        year=_annee(specs.get("CIRCA")),
        case_material=specs.get("CASE MATERIAL"),
        case_size_mm=_millimetres(specs.get("CASE DIAMETER") or specs.get("DIAMETER")),
        movement=specs.get("MOVEMENT"),
        dial_color=specs.get("DIAL"),
        title=titre, seller="Christie's",
    )


def lots_du_brut(entrees: list) -> list[dict]:
    """Tous les lots contenus dans une collecte brute deja stockee."""
    lots = []
    for entree in entrees:
        try:
            trouves = _deep_find(json.loads(entree.get("payload", "")), "lots")
        except (json.JSONDecodeError, AttributeError):
            continue
        if trouves:
            lots.extend(trouves)
    return lots


def collect(cap: int = 25000):
    raw: list[dict] = []
    journal: list[str] = []
    records: list[dict] = []

    ventes = _ventes_montres(raw, journal)
    journal.append(f"{len(ventes)} ventes montres reperees sur {_annees()}")

    for vente in ventes:
        if len(records) >= cap:
            break
        for page in range(1, PAGES_PAR_VENTE + 1):
            params = {"language": "en", "saleid": vente["sale_id"], "salenumber": vente["sale_number"],
                      "page": page, "pagesize": TAILLE_PAGE, "saletype": "Sale", "component": COMPONENT}
            try:
                resp = get(LOTSEARCH, params=params, pause=1.2, headers=ENTETES)
            except Exception as exc:
                journal.append(f"lots {vente['sale_number']} p{page}: {type(exc).__name__}")
                break
            raw.append({"url": resp.url, "status": resp.status_code, "payload": resp.text})
            if resp.status_code != 200:
                journal.append(f"lots {vente['sale_number']} p{page}: HTTP {resp.status_code}")
                break
            try:
                lots = _deep_find(json.loads(resp.text), "lots") or []
            except json.JSONDecodeError:
                break
            if not lots:
                break

            for lot in lots:
                enregistrement = fiche(lot)
                if enregistrement is not None:
                    records.append(enregistrement)
            if len(lots) < TAILLE_PAGE or len(records) >= cap:
                break

    # Un plafond atteint = collecte partielle. Le dire, sinon le chiffre passe
    # pour un total alors qu'il est un plancher.
    if len(records) >= cap:
        journal.append(f"TRONQUE: plafond de {cap} atteint — il reste des donnees a prendre")
    return raw, records[:cap], journal
