"""Fortuna — maison de ventes new-yorkaise. API WordPress ouverte, 2016.

2 020 lots horlogers sur 145 ventes, de 2016 a 2026, pour 23 requetes. C'est le
meilleur rapport profondeur/cout du lot apres Monaco Legend.

    /wp-json/wp/v2/lots?per_page=100&lot-category=79&page=N   (79 = 'watch')
    /wp-json/wp/v2/auction-results/{id}                       (la date de vente)

LE CHAMP `hammer_price` EST BIEN LE MARTEAU — et cela merite d'etre ecrit,
parce que l'analyse par arithmetique concluait l'inverse. Le raisonnement etait
seduisant : 96,5 % des montants divises par 1,25 tombent sur un multiple de 50.
Mais la source publie aussi `buyers_premium_amount` et `total_with_bp`, et la
verification directe est sans appel — sur 34 lots, `hammer + premium = total`
au centime pres : 2 800 + 784 = 3 584, 3 500 + 875 = 4 375.

La lecon vaut au-dela de cette source : quand deux methodes se contredisent, la
verification directe l'emporte sur l'inference statistique. Le marteau tombe sur
des multiples ronds APRES division par 1,25 simplement parce que les encheres
progressent par paliers de 100 et que 1,25 conserve cette regularite.

SECOND PIEGE : le champ `date` de WordPress est la date d'IMPORT dans le CMS —
2026 pour une vente de 2025. La vraie date est `acf.auction_date`, au format
AAAAMMJJ, qu'il faut aller chercher sur la vente liee.

RESERVE : les invendus ne sont pas publies. `lot_status` vaut "sold" sur
2 020 lots sur 2 020. Biais de survie assume.

Reconnaissance du 28/08/2026.
"""
from __future__ import annotations

import json
import re

from watchpoint.schema import parse_money, price_point, reference_dans, reference_libre
from watchpoint.commun.utils import get

SOURCE = {
    "id": "fortuna",
    "name": "Fortuna",
    "type": "auction",
    "price_nature": "realised",
    "access": "API REST WordPress /wp-json/wp/v2/lots",
    "robots": "OK — /wp-json/ n'est pas interdit, verifie le 28/08/2026",
    "corpus_horloger": True,
    "reserve": "invendus non publies ; 5 ventes sur 145 ont un bareme de frais degressif",
}

BASE = "https://fortunaauction.com/wp-json/wp/v2"
CATEGORIES = (79,)      # 'watch' ; une categorie 'pocket-watch' existe a part
PAR_PAGE = 100
_BALISES = re.compile(r"<[^>]+>")


def _texte(html) -> str:
    return _BALISES.sub(" ", str(html or ""))


def _valeur(bloc) -> str:
    """Les champs WordPress arrivent tantot en texte, tantot en {'rendered': ...}."""
    if isinstance(bloc, dict):
        return str(bloc.get("rendered") or "")
    return str(bloc or "")


def _date_de_vente(acf: dict, ventes: dict, journal: list, raw: list | None = None) -> str | None:
    """La date vient de la VENTE liee, jamais du champ `date` du lot."""
    liee = acf.get("related_auction")
    identifiant = liee.get("ID") if isinstance(liee, dict) else liee
    if not identifiant:
        return None
    if identifiant not in ventes:
        try:
            resp = get(f"{BASE}/auction-results/{identifiant}", pause=1.0)
            # Le brut doit contenir CES reponses aussi : sans elles, le rejeu
            # reconstruit des lots sans date, donc hors du socle.
            if raw is not None:
                raw.append({"url": resp.url, "status": resp.status_code,
                            "payload": resp.text})
            vente = json.loads(resp.text) if resp.status_code == 200 else {}
        except Exception:
            vente = {}
        brut = str((vente.get("acf") or {}).get("auction_date") or "")
        ventes[identifiant] = (f"{brut[:4]}-{brut[4:6]}-{brut[6:8]}"
                               if len(brut) == 8 and brut.isdigit() else None)
    return ventes[identifiant]


_MARQUES: dict = {}


def _charge_marques(journal: list, raw: list | None = None) -> None:
    """La taxonomie des marques : le lot ne porte que des identifiants.

    Ses reponses sont CONSERVEES dans le brut. Sans elles, rejouer la source
    hors ligne rendait 2 010 lots sans aucune marque — donc rejetes par R3 —
    alors que la collecte en direct en resolvait 92 %. Une donnee qui n'est
    pas dans le brut n'est pas rejouable, meme si elle a bien ete lue.
    """
    if _MARQUES:
        return
    for page in (1, 2, 3):
        try:
            resp = get(f"{BASE}/brand", params={"per_page": 100, "page": page}, pause=1.0)
            if raw is not None:
                raw.append({"url": resp.url, "status": resp.status_code,
                            "payload": resp.text})
            termes = json.loads(resp.text) if resp.status_code == 200 else []
        except Exception:
            break
        if not isinstance(termes, list) or not termes:
            break
        for t in termes:
            if t.get("id") and t.get("name"):
                _MARQUES[t["id"]] = t["name"]
    journal.append(f"{len(_MARQUES)} marques resolues depuis la taxonomie")


def _marque(lot: dict, acf: dict) -> str | None:
    """La marque, resolue depuis la taxonomie : le lot ne porte que des ids."""
    for identifiant in (lot.get("brand") or []):
        if isinstance(identifiant, int) and identifiant in _MARQUES:
            return _MARQUES[identifiant]
        if isinstance(identifiant, dict) and identifiant.get("name"):
            return identifiant["name"]
    return None


def fiche(lot: dict, date_vente=None) -> dict | None:
    acf = lot.get("acf") or {}
    montant = acf.get("hammer_price")
    try:
        montant = float(str(montant).replace(",", "").replace("$", "").strip())
    except (TypeError, ValueError):
        return None
    if not montant:
        return None

    titre = _valeur(lot.get("title")).strip()
    description = _texte(_valeur(lot.get("content")))
    reference = reference_dans(titre)
    provenance = "extrait_titre" if reference else None
    if not reference:
        reference = reference_dans(description[:1500])
        provenance = "extrait_description" if reference else None
    if not reference:
        reference = reference_libre(titre)
        provenance = "jeton_titre" if reference else None

    # LE REGIME DE FRAIS SE LIT LOT PAR LOT, et il change de sens d'un lot a
    # l'autre. `bp_applies` vaut vrai sur 34 lots seulement : ceux-la publient
    # aussi `buyers_premium_amount`, et `marteau + frais = total` s'y verifie
    # 34/34. Sur les 1 976 autres, le champ nomme `hammer_price` porte deja les
    # frais : ses 471 montants non entiers deviennent TOUS des entiers exacts
    # apres division par 1,25 — 43,75 = 35 x 1,25, 62,50 = 50 x 1,25. Aucun
    # marteau ne tombe sur 43,75 $.
    #
    # C'est exactement l'erreur qu'on avait faite ici : la verification directe
    # ne portait que sur les 34 lots ou elle etait possible, c'est-a-dire la
    # seule population qui se comporte autrement que les 98,3 % restants.
    frais_inclus = str(acf.get("bp_applies")).lower() not in ("1", "true", "yes")

    bas, _ = parse_money(acf.get("auction_estimate_low"))
    haut, _ = parse_money(acf.get("auction_estimate_high"))


    return price_point(
        source_id=SOURCE["id"], source_type=SOURCE["type"],
        source_url=lot.get("link"),
        external_id=str(lot.get("id")),
        price_nature="realised",
        price_nature_provenance="champ_dedie",
        listing_status="sold",
        price_includes_premium=frais_inclus,
        price_amount=montant, price_currency="USD",
        price_date=date_vente,
        # La marque est une taxonomie WordPress (92,4 % de couverture), pas un
        # champ ACF : `brand_name` n'existe pas et rendait la source sans marque,
        # donc integralement rejetee par R3.
        brand=_marque(lot, acf),
        reference=reference,
        reference_provenance=provenance,
        estimate_low=bas, estimate_high=haut,
        title=titre or None,
        seller="Fortuna",
    )


def lots_du_brut(entrees: list) -> list[tuple]:
    """(lot, date de vente) pour chaque lot du brut.

    Deux choses ne vivent PAS dans la reponse d'un lot et doivent etre relues
    a part : la taxonomie des marques, et la date de vente — qui se trouve
    dans /auction-results/{related_auction}, un lot ne portant qu'un
    identifiant. Sans elles le rejeu rendait 2 010 lots sans marque et sans
    date, donc sans valeur. Elles sont conservees dans le brut depuis le
    28/08/2026 : la source est desormais rejouable de bout en bout.
    """
    trouves = []
    ventes: dict = {}
    for entree in entrees:
        if "auction-results" not in entree.get("url", ""):
            continue
        try:
            vente = json.loads(entree.get("payload", ""))
        except (json.JSONDecodeError, AttributeError):
            continue
        if isinstance(vente, dict) and vente.get("id"):
            brut = str((vente.get("acf") or {}).get("auction_date") or "")
            ventes[vente["id"]] = (f"{brut[:4]}-{brut[4:6]}-{brut[6:8]}"
                                   if len(brut) == 8 and brut.isdigit() else None)
    # La taxonomie d'abord : les lots ne portent que des identifiants de marque.
    for entree in entrees:
        if "/brand" not in entree.get("url", ""):
            continue
        try:
            termes = json.loads(entree.get("payload", ""))
        except (json.JSONDecodeError, AttributeError):
            continue
        for t in termes if isinstance(termes, list) else []:
            if isinstance(t, dict) and t.get("id") and t.get("name"):
                _MARQUES[t["id"]] = t["name"]
    for entree in entrees:
        if "/lots" not in entree.get("url", ""):
            continue
        try:
            lots = json.loads(entree.get("payload", ""))
        except (json.JSONDecodeError, AttributeError):
            continue
        for l in lots if isinstance(lots, list) else []:
            if not isinstance(l, dict):
                continue
            liee = (l.get("acf") or {}).get("related_auction")
            date = None
            for i in (liee if isinstance(liee, list) else [liee]):
                if isinstance(i, dict):
                    i = i.get("ID")
                if isinstance(i, str) and i.isdigit():
                    i = int(i)
                if i in ventes:
                    date = ventes[i]
                    break
            trouves.append((l, date))
    return trouves


def collect(cap: int = 6000):
    raw: list[dict] = []
    journal: list[str] = []
    records: list[dict] = []
    ventes: dict = {}

    _charge_marques(journal)

    for categorie in CATEGORIES:
        page = 1
        while len(records) < cap:
            try:
                resp = get(f"{BASE}/lots", pause=1.0,
                           params={"per_page": PAR_PAGE, "lot-category": categorie,
                                   "page": page})
            except Exception as exc:
                journal.append(f"categorie {categorie} p{page}: {type(exc).__name__}")
                break
            raw.append({"url": resp.url, "status": resp.status_code, "payload": resp.text})
            if resp.status_code != 200:
                journal.append(f"categorie {categorie} p{page}: HTTP {resp.status_code}")
                break
            try:
                lots = json.loads(resp.text)
            except json.JSONDecodeError:
                break
            if not isinstance(lots, list) or not lots:
                break
            if page == 1:
                journal.append(f"categorie {categorie} : "
                               f"{resp.headers.get('X-WP-Total')} lots annonces")

            for lot in lots:
                date = _date_de_vente(lot.get("acf") or {}, ventes, journal, raw)
                enregistrement = fiche(lot, date)
                if enregistrement is not None:
                    records.append(enregistrement)

            if len(lots) < PAR_PAGE:
                break
            page += 1

    journal.append(f"{len(ventes)} ventes interrogees pour leur date")
    if len(records) >= cap:
        journal.append(f"TRONQUE: plafond de {cap} atteint — il reste des donnees a prendre")
    return raw, records, journal
