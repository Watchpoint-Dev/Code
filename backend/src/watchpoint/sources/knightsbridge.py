"""Watches of Knightsbridge — maison de ventes londonienne, boutique WooCommerce.

CE QUE CETTE SOURCE N'EST PAS. L'audit de juillet l'annoncait en prix realises,
2014 -> aujourd'hui, 10 000 a 25 000 lots. Mesure du 21/09/2026 : la boutique
WooCommerce ne porte PAS l'archive d'encheres. Elle porte les 573 fiches de
la branche detail de la maison — « CURATED » et « OYSTERBAR » : 456 des 573 SKU
commencent par `CUR`, la categorie est `Watches` (555) ou `Watch Accessories`
(18), les fiches sont achetables au panier, `on_sale` est faux partout et le mot
« hammer » n'apparait dans aucune des 573 descriptions (« auction » dans zero,
« lot » dans trois, en prose). Ce sont des PRIX DEMANDES de marchand, pas des
prix realises. Le sitemap ne declare que `page` et `product` : aucun type de
contenu « lot » ou « resultat ». La page /auctions/ existe au menu mais rend 403
a tout agent honnete, et n'est pas au sitemap — l'archive d'encheres n'est donc
pas atteignable ici. `price_includes_premium` reste None : chez un marchand la
question n'a pas de sens, et rien dans l'API ne parle de frais acheteur.

D'ou `type = dealer` et `price_nature = asking`. Classer cette source en
`auction`/`realised` sur la foi de l'enseigne aurait injecte 573 prix de vitrine
dans le socle des ventes conclues.

L'UA. `utils.HEADERS` annonce ClaudeBot et le pare-feu rend « Your request was
blocked » (HTTP 403, 25 octets) sur l'API Store. Le meme appel avec l'UA par
defaut de la bibliotheque — `python-requests/2.34.2` — rend 200 et 33 ko.
robots.txt (lu le 21/09/2026) ne porte AUCUNE regle ClaudeBot : il n'interdit
que `/p/watches/?filter_` et `/p/watches/?query_type_`. Le 403 est un filtre
d'UA, pas une consigne du site ; on ne le contourne pas, on cesse simplement
d'annoncer un nom que ce pare-feu rejette, sans jamais se reclamer d'un
navigateur. Le blocage vise aussi TOUTES les pages HTML sauf l'accueil
(/about/, /product/<slug>/ : 403 avec les deux UA) — on s'y arrete, l'API suffit.

LA DATE. L'API Store de cette boutique ne publie pas `date_created` : le
generique `_woo` sortirait 573 lignes sans date. La date vit ailleurs, dans
/wp-json/wp/v2/product, et c'est une date de MISE EN LIGNE, jamais une date de
transaction. Profondeur mesuree : 2021-12-28 -> 2026-08-24, 573/573 fiches
datees (2024 : 219, 2023 : 215, 2022 : 65, 2026 : 55, 2025 : 14, 2021 : 5).

LE PIEGE DE LA REFERENCE. L'attribut `REFERENCE` est renseigne sur 465 des 573
fiches — vraie reference constructeur (3538, 16030, 118238, WSSA0055). Mais le
generique essaie `reference` PUIS `model`, et l'attribut `MODEL` de cette
boutique porte des noms commerciaux chiffres : « Datejust 36 OysterQuartz »,
« British Military RAF Mark 11 », « Scafograf 300M ». Mesure : 12 fiches
sortaient avec un nom de modele enregistre comme reference constructeur en
provenance `champ_dedie`. Ici la reference ne vient que de `REFERENCE`, et le
titre prend le relais.

Autres mesures du 21/09/2026 : 100 % GBP, `currency_minor_unit` = 0 sur les 573
fiches (prix en livres entieres, aucune division), aucun prix negatif, 11 prix a
zero (« prix sur demande », ecartes), median 7 500 GBP, 80 -> 76 000 GBP.
501 fiches sur 573 sont epuisees : chez un marchand de pieces uniques la piece
est partie, mais le montant affiche reste le dernier prix DEMANDE.
"""
from __future__ import annotations

import json

import requests

from watchpoint.schema import price_point, reference_dans, reference_libre
from watchpoint.commun.utils import get

from . import _woo

# L'UA par defaut de la bibliotheque. Honnete : il ne se reclame d'aucun
# navigateur. Mesure du 21/09/2026 : ClaudeBot -> 403, celui-ci -> 200.
UA = requests.utils.default_user_agent()

SOURCE = {
    "id": "knightsbridge",
    "name": "Watches of Knightsbridge",
    "type": "dealer",
    "price_nature": "asking",
    "access": "WooCommerce Store API + wp/v2 pour la date, UA python-requests obligatoire",
    "robots": "OK, lu le 21/09/2026 — seuls /p/watches/?filter_ et ?query_type_ "
              "sont interdits ; aucune regle ClaudeBot, /wp-json/ est libre",
    "corpus_horloger": True,
    "reserve": "l'archive d'encheres n'est PAS dans WooCommerce : 573 fiches de "
               "la branche detail (CURATED/OYSTERBAR), prix demandes, date de mise en ligne",
}

BASE = "https://www.watchesofknightsbridge.com"
PRODUITS = "/wp-json/wc/store/v1/products"
DATES = "/wp-json/wp/v2/product"
PAR_PAGE = 100


def _attribut(produit: dict, *libelles) -> str | None:
    """Les libelles d'attributs sont en MAJUSCULES chez cette boutique."""
    return _woo._attribut(produit, libelles)


def fiche(produit: dict, date: str | None = None) -> dict | None:
    """Un produit -> un enregistrement. Le generique, puis les corrections.

    `date` est la date de mise en ligne lue dans wp/v2 : l'API Store de cette
    boutique ne la porte pas.
    """
    record = _woo.fiche(produit, SOURCE)
    if record is None:
        return None

    # La reference ne vient QUE de l'attribut dedie. Le generique retomberait
    # sur `MODEL`, qui porte ici des noms commerciaux chiffres.
    reference = _attribut(produit, "reference")
    if reference and reference.strip().lower() not in ("n/a", "na", "-"):
        record["reference"] = reference.strip()
        record["reference_provenance"] = "champ_dedie"
    else:
        titre = produit.get("name") or ""
        trouve, provenance = reference_dans(titre), "extrait_titre"
        if not trouve:
            trouve, provenance = reference_libre(titre), "jeton_titre"
        record["reference"] = trouve or None
        record["reference_provenance"] = provenance if trouve else None

    # Champs que le generique ne va pas chercher sous ces libelles.
    record["model"] = _attribut(produit, "model")
    record["case_material"] = _attribut(produit, "metal", "material")
    record["case_size_mm"] = _attribut(produit, "case diameter", "case",
                                       "case size", "case dimensions")
    record["movement"] = _attribut(produit, "movement")
    record["dial_color"] = _attribut(produit, "dial colour", "dial")
    record["condition"] = _attribut(produit, "condition")

    # Date de MISE EN LIGNE, pas de transaction. La source ne publie pas la
    # seconde ; l'ecrire ici serait une invention.
    record["price_date"] = date

    # On repasse par le modele : c'est lui qui decode les entites HTML, ramene
    # « 36mm » a 36.0 et la date ISO a 'YYYY-MM-DD'. Le faire a la main ici
    # laisserait entrer des '18k Yellow-Gold &amp; Steel' et des diametres
    # en texte.
    return price_point(**record)


def lots_du_brut(entrees: list) -> list[tuple]:
    """(produit, date de mise en ligne) — les deux familles de payload du brut."""
    dates: dict[str, str] = {}
    produits: list[dict] = []
    for entree in entrees:
        try:
            charge = json.loads(entree.get("payload", ""))
        except (json.JSONDecodeError, AttributeError):
            continue
        if not isinstance(charge, list):
            continue
        if DATES in (entree.get("url") or ""):
            for poste in charge:
                if isinstance(poste, dict) and poste.get("id"):
                    dates[str(poste["id"])] = poste.get("date")
        else:
            produits.extend(p for p in charge if isinstance(p, dict))
    return [(p, dates.get(str(p.get("id")))) for p in produits]


def _pages(cap: int, raw: list, journal: list) -> None:
    """Le stock courant PUIS les fiches epuisees — sans elles, 72 au lieu de 573."""
    lus = 0
    for statut, libelle in (("instock", "en vitrine"), ("outofstock", "parties")):
        page = 1
        while lus < cap:
            try:
                resp = get(f"{BASE}{PRODUITS}",
                           params={"per_page": PAR_PAGE, "page": page,
                                   "stock_status": statut},
                           headers={"User-Agent": UA})
            except Exception as exc:
                journal.append(f"{libelle} p{page}: {type(exc).__name__}")
                break
            raw.append({"url": resp.url, "status": resp.status_code,
                        "payload": resp.text})
            if resp.status_code != 200:
                journal.append(f"{libelle} p{page}: HTTP {resp.status_code} "
                               f"— {resp.text[:60]!r}")
                break
            if page == 1 and resp.headers.get("X-WP-Total"):
                journal.append(f"{libelle} : {resp.headers['X-WP-Total']} fiches annoncees")
            try:
                produits = json.loads(resp.text)
            except json.JSONDecodeError:
                break
            if not isinstance(produits, list) or not produits:
                break
            lus += len(produits)
            if len(produits) < PAR_PAGE:
                break
            page += 1


def _dates(ids: list[str], raw: list, journal: list) -> None:
    """La date de mise en ligne, par paquets de 100 identifiants."""
    for depart in range(0, len(ids), PAR_PAGE):
        paquet = ids[depart:depart + PAR_PAGE]
        try:
            resp = get(f"{BASE}{DATES}",
                       params={"include": ",".join(paquet), "per_page": PAR_PAGE,
                               "_fields": "id,date"},
                       headers={"User-Agent": UA})
        except Exception as exc:
            journal.append(f"dates paquet {depart // PAR_PAGE + 1}: {type(exc).__name__}")
            return
        raw.append({"url": resp.url, "status": resp.status_code, "payload": resp.text})
        if resp.status_code != 200:
            journal.append(f"dates paquet {depart // PAR_PAGE + 1}: HTTP {resp.status_code}")
            return


def collect(cap: int = 700):
    raw: list[dict] = []
    journal: list[str] = []

    _pages(cap, raw, journal)
    lots = lots_du_brut(raw)
    journal.append(f"{len(lots)} produits lus dans le brut")

    ids = []
    vus = set()
    for produit, _ in lots:
        identifiant = str(produit.get("id"))
        if identifiant not in vus:
            vus.add(identifiant)
            ids.append(identifiant)
    _dates(ids[:cap], raw, journal)

    records: list[dict] = []
    retenus: set[str] = set()
    sans_prix = 0
    for produit, date in lots_du_brut(raw):
        record = fiche(produit, date)
        if record is None:
            sans_prix += 1
            continue
        if record["external_id"] in retenus:
            continue
        retenus.add(record["external_id"])
        records.append(record)
        if len(records) >= cap:
            break

    datees = sum(1 for r in records if r.get("price_date"))
    journal.append(f"{len(records)} fiches retenues, {datees} datees "
                   f"(MISE EN LIGNE, pas la vente)")
    journal.append(f"{sans_prix} fiches ecartees : prix nul ou sentinelle "
                   f"(« prix sur demande »)")
    journal.append("prix DEMANDES de la branche detail (CURATED/OYSTERBAR) : "
                   "l'archive d'encheres de la maison n'est pas dans WooCommerce")
    if len(records) >= cap:
        journal.append(f"TRONQUE: plafond de {cap} atteint — il reste des donnees a prendre")
    return raw, records, journal
