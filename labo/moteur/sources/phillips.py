"""Phillips — maison de ventes. Prix REALISES dates, 2015 -> aujourd'hui.

Cent cinq ventes de montres pour cent six requetes : la page d'une vente porte
DEJA tous ses lots, prix realise compris. C'est le meilleur rapport
profondeur/cout du dossier apres Monaco Legend, et sur dix fois le volume.

Acces en deux niveaux, sans pagination et sans navigateur :

  1. /calendar/results porte le payload React Router du calendrier. Il liste
     les 896 ventes passees TOUS DEPARTEMENTS confondus avec leur code, leur
     ville, leur fuseau et leur date. On y garde celles dont `departments`
     nomme 'Watches' : 105, de mai 2015 a septembre 2026.
  2. /auction/{CODE}/overview porte le meme genre de payload, et son objet
     `auction.lots` contient TOUS les lots de la vente — jusqu'a 294 — avec
     `soldPrice`, `lotStatus`, `referenceNo`, `makerName`, `modelName` et la
     date de la session. Aucune page de lot n'est necessaire pour le socle.

SIX POINTS MESURES le 21/09/2026, dans l'ordre ou ils feraient mal :

  LE PIEGE DU JSON-LD. La page d'un lot porte bien un `Product` schema.org avec
  `availability: SoldOut` et un `offers.price`. Ce prix N'EST PAS le prix
  realise : c'est l'ESTIMATION BASSE. Lot 144448 (Daytona 116520, Geneve 2020) :
  JSON-LD `offers.price` 15 000 CHF, `estimate.lowEstimate` 15 000 CHF,
  `soldPrice` 23 940 CHF. Lire le JSON-LD comme un prix de vente sous-estime
  cette montre de 37 % — et rien, ni le champ ni l'availability, ne le signale.
  On ne lit donc JAMAIS le JSON-LD. On lit le payload de la vente.

  LE PRIX EST FRAIS ACHETEUR INCLUS. Mesure du 21/09/2026 sur 8 ventes, 3
  places et 1 175 lots vendus (detail dans essais/phillips/samples/
  mesure_frais_acheteur.json). Deux preuves independantes :

      Egalite directe, la ou les deux prix sont publies. Sur NY080126 et
      HK080226, `soldPrice` == `hammerPricePlusBP` sur 449/449 lots vendus, et
      `hammerPricePlusBP` / `hammerPrice` vaut 1,27 sur 443 — exactement les
      27 % annonces dans les conditions de vente.

      Divisibilite, la ou seul `soldPrice` existe. Diviser par le taux de frais
      publie A LA DATE DE LA VENTE rend un marteau propre (multiple
      d'increment d'enchere) sur 1 145 des 1 175 lots, soit 97,4 % :
          2015 Geneve  / 1,25 -> 49/60      2020 Geneve   / 1,26 -> 92/94
          2017 HongKong/ 1,25 -> 150/150    2022 NewYork  / 1,26 -> 167/170
          2019 NewYork / 1,25 -> 69/73      2024 NewYork  / 1,27 -> 175/179
      Sans diviser, `soldPrice` n'est propre que dans 29,5 % des cas, et le
      mauvais taux ne depasse jamais 3 %. Les frais Phillips sont donc passes
      de 25 % (2015-2019) a 26 % (2020-2022) puis 27 % (2024-2026), et
      `soldPrice` les porte a chaque epoque.

  `price_includes_premium=True`, comme Christie's et Monaco Legend, PAS comme
  Artcurial.

  LE MARTEAU NU N'EXISTE QUE SUR LES VENTES RECENTES. `hammerPrice` et
  `hammerPricePlusBP` sont presents sur les ventes de 2026 et absents de celles
  de 2015 et 2020, ou seul `soldPrice` subsiste. Charger le marteau quand il
  existe et le prix frais inclus sinon creerait une MARCHE DE 27 % au milieu de
  la courbe, a l'endroit precis ou le site a change de plateforme. On charge
  donc `soldPrice` partout — serie homogene sur onze ans — et le brut, qui
  n'est jamais jete, conserve `hammerPrice` pour qui voudra la serie marteau.

  LE FILTRE DE DEPARTEMENT N'EST PAS APPLIQUE PAR LE SERVEUR.
  /calendar/results?Departments=watches rend les 896 ventes de tous les
  departements : le tri se fait dans le navigateur. Prendre les ~900 codes de
  cette page pour ~900 ventes de montres — ce que faisait l'audit de juillet —
  surestime la source d'un facteur neuf. Le vrai compte est 105.

  LA DATE EST EN UTC, LA VENTE DANS SA VILLE. CH080115 porte
  `2015-05-08T22:00:00Z` et `Europe/Zurich` : la vente a eu lieu le 9 mai. Un
  simple `[:10]` decale d'un jour toutes les ventes de Geneve et de Hong Kong,
  celles du soir en particulier. On convertit avec `auctionTimezone`.

  TROIS DEVISES ET UNE SEULE PLATEFORME. Geneve vend en CHF, Hong Kong en HKD,
  New York en USD. `auctionCurrency` le dit vente par vente. Il n'y a pas de
  "site Hong Kong" separe : phillips.com sert les trois places, et un seul
  adaptateur les couvre sans aucun parametre de lieu.

Enrichissement facultatif (`collect(cap, enrichir=N)`) : la page d'un lot ajoute
`circa` (l'annee), `material`, `calibre` et `dimensions` en champs propres. Cela
coute une requete PAR LOT — 20 000 pour tout le fonds — donc c'est desactive par
defaut : le socle prix/date/reference ne le demande pas.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import zoneinfo

from schema import price_point, reference_dans, reference_libre
from utils import get

SOURCE = {
    "id": "phillips",
    "name": "Phillips",
    "type": "auction",
    "price_nature": "realised",
    "access": "payload React Router du calendrier, puis de chaque page de vente",
    "robots": "OK — /calendar et /auction autorises ; seuls /search, /Search, "
              "/SEARCH, /*/filter/, /bin/, /message/optin/ et /phillips/otis "
              "sont interdits, et aucun n'est utilise (lu le 21/09/2026)",
    # Les ventes retenues sont celles du departement 'Watches', et chaque lot
    # porte lotType='WatchAuctionLot' : le corpus est garanti horloger, R4 n'a
    # pas a exiger le mot "montre" dans le titre pour valider une marque.
    "corpus_horloger": True,
    "reserve": "soldPrice = prix FRAIS ACHETEUR INCLUS (mesure a 25/26/27 % "
               "selon l'epoque) ; le marteau nu n'est publie que depuis 2026",
}

BASE = "https://www.phillips.com"
CALENDRIER = f"{BASE}/calendar/results"

# Le payload de React Router : un tableau plat ou tout est un indice. Les objets
# s'y ecrivent {"_<indice de la cle>": <indice de la valeur>}.
_ENQUEUE = re.compile(r'streamController\.enqueue\("((?:[^"\\]|\\.)*)"\)', re.S)
_BALISES = re.compile(r"<[^>]+>")

# Ce qui, dans lotStatus, dit que le lot n'a jamais ete soumis aux encheres. Un
# lot retire ne dit rien du marche, contrairement a un invendu.
_JAMAIS_OFFERT = re.compile(r"withdraw|noloted|nolot", re.I)


# ---------------------------------------------------------------------------
# Le decodeur de payload. Un seul endroit, utilise par le calendrier, les
# ventes et les lots.
# ---------------------------------------------------------------------------
def _tableaux(html: str) -> list[list]:
    """Les tableaux plats du HTML, du plus gros au plus petit.

    Une page peut en emettre plusieurs (le flux resout ses promesses au fil de
    l'eau). Les indices d'un tableau ne valent que dans ce tableau : on ne les
    concatene jamais, on les essaie l'un apres l'autre.
    """
    trouves = []
    for morceau in _ENQUEUE.findall(html or ""):
        try:
            plat = json.loads(json.loads('"' + morceau + '"'))
        except (json.JSONDecodeError, ValueError):
            continue
        if isinstance(plat, list):
            trouves.append(plat)
    return sorted(trouves, key=len, reverse=True)


def _resolu(plat: list, indice, profondeur: int = 0):
    """Un indice du tableau plat -> la valeur Python qu'il represente."""
    if not isinstance(indice, int) or indice < 0 or indice >= len(plat) \
            or profondeur > 14:
        return None if isinstance(indice, int) and indice < 0 else indice
    valeur = plat[indice]
    if isinstance(valeur, dict):
        rendu = {}
        for cle, sous in valeur.items():
            nom = cle
            if isinstance(cle, str) and cle.startswith("_") and cle[1:].isdigit():
                pointe = int(cle[1:])
                nom = plat[pointe] if pointe < len(plat) else cle
            if isinstance(nom, str):
                rendu[nom] = _resolu(plat, sous, profondeur + 1)
        return rendu
    if isinstance(valeur, list):
        return [_resolu(plat, x, profondeur + 1) for x in valeur]
    return valeur


def _sous_la_cle(plat: list, nom: str, garde=None):
    """La valeur rangee sous la cle `nom`, ou qu'elle soit dans le tableau.

    On ne resout PAS la racine : sur le calendrier elle pese 12 000 elements et
    la resolution complete est inutilement couteuse. On cherche l'indice de la
    chaine `nom`, puis l'objet qui la porte comme cle, et on ne resout que sa
    valeur. `garde` permet de retenir le bon candidat quand la cle est
    ambigue — 'auction' apparait plusieurs fois sur une page de lot.
    """
    indices = [i for i, v in enumerate(plat) if v == nom]
    for cible in indices:
        pointeur = f"_{cible}"
        for valeur in plat:
            if isinstance(valeur, dict) and pointeur in valeur:
                rendu = _resolu(plat, valeur[pointeur])
                if garde is None or garde(rendu):
                    return rendu
    return None


def _texte(html) -> str:
    import html as _h
    return re.sub(r"\s+", " ", _h.unescape(_BALISES.sub(" ", str(html or "")))).strip()


def _jour_local(horodatage, fuseau) -> str | None:
    """'2015-05-08T22:00:00.000000Z' + 'Europe/Zurich' -> '2015-05-09'.

    La vente a eu lieu un jour donne dans sa ville. Garder l'UTC decale d'un
    jour toutes les ventes du soir de Geneve et de Hong Kong.
    """
    if not horodatage:
        return None
    brut = str(horodatage).replace("Z", "+00:00")
    # Les payloads portent six chiffres de fraction : datetime les accepte.
    try:
        moment = dt.datetime.fromisoformat(brut)
    except ValueError:
        trouve = re.search(r"\d{4}-\d{2}-\d{2}", brut)
        return trouve.group(0) if trouve else None
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=dt.timezone.utc)
    if fuseau:
        try:
            moment = moment.astimezone(zoneinfo.ZoneInfo(str(fuseau)))
        except (zoneinfo.ZoneInfoNotFoundError, ValueError):
            pass
    return moment.date().isoformat()


# ---------------------------------------------------------------------------
# Le calendrier
# ---------------------------------------------------------------------------
def ventes_montres(html: str) -> list[dict]:
    """Les ventes passees du departement Montres, la plus recente d'abord.

    `?Departments=watches` ne filtre RIEN cote serveur : le payload porte les
    896 ventes de tous les departements. Le tri se fait ici.
    """
    for plat in _tableaux(html):
        passees = _sous_la_cle(
            plat, "pastAuctions",
            garde=lambda v: isinstance(v, list) and v
            and isinstance(v[0], dict) and "auctionCode" in v[0])
        if not passees:
            continue
        montres = [v for v in passees
                   if any("watch" in str((d or {}).get("departmentName", "")).lower()
                          for d in (v.get("departments") or []))]
        return sorted(montres, key=lambda v: str(v.get("auctionStartDateTime") or ""),
                      reverse=True)
    return []


def _vente_du_payload(html: str) -> dict | None:
    """L'objet `auction` d'une page de vente, avec ses lots."""
    for plat in _tableaux(html):
        vente = _sous_la_cle(
            plat, "auction",
            garde=lambda v: isinstance(v, dict) and isinstance(v.get("lots"), list))
        if vente:
            return vente
    return None


def _estimation(lot: dict, devise: str | None) -> tuple[float | None, float | None]:
    """L'estimation DANS LA DEVISE DE LA VENTE.

    `estimate.otherEstimates` porte la meme fourchette convertie en cinq
    devises. Prendre la premiere venue melangerait des HKD a des CHF dans la
    meme colonne.
    """
    bloc = lot.get("estimate") or {}
    candidats = []
    principale = bloc.get("mainEstimate")
    if isinstance(principale, dict):
        candidats.append(principale)
    candidats += [e for e in (bloc.get("otherEstimates") or []) if isinstance(e, dict)]
    for entree in candidats:
        if devise is None or entree.get("currencyCode") == devise:
            return entree.get("lowEstimate"), entree.get("highEstimate")
    return None, None


def fiche(lot: dict, date_vente=None, devise=None, fuseau=None,
          detail: dict | None = None) -> dict | None:
    """Un lot du payload d'une vente -> un enregistrement normalise."""
    if not isinstance(lot, dict):
        return None
    statut = str(lot.get("lotStatus") or "")
    # Un lot retire n'a jamais ete soumis aux encheres.
    if lot.get("isNoLot") or _JAMAIS_OFFERT.search(statut):
        return None

    detail = detail or {}
    montant = lot.get("soldPrice")
    if isinstance(montant, (int, float)) and montant <= 0:
        montant = None
    # Le statut et le prix sont deux choses. Un lot peut etre 'Sold' sans que
    # son prix soit publie — un sur 74 dans la vente NY080119 — et le ranger
    # en invendu mentirait sur le marche. On garde alors le statut vendu, mais
    # la nature tombe a 'estimate' : on n'a que la fourchette.
    adjuge = statut.lower() == "sold"
    vendu = adjuge and montant is not None

    devise = ((lot.get("auctionCurrency") or {}).get("currencyCode")
              or devise)
    bas, haut = _estimation(lot, devise)
    if montant is None and bas is None:
        return None

    # La session porte sa propre date : une vente sur deux jours a deux dates,
    # et c'est celle de la session qui est la date de la transaction.
    jour = _jour_local(lot.get("sessionStartDateTime"), fuseau) or date_vente

    marque = lot.get("makerName")
    modele = lot.get("modelName")
    description = _texte(lot.get("description"))
    # Le titre du projet : ce que le catalogue nomme, puis ce qu'il decrit. La
    # description porte presque toujours le mot 'wristwatch' ou 'pocket watch',
    # ce dont le filtre a besoin pour trancher.
    titre = ", ".join(p for p in (" ".join(p for p in (marque, modele) if p) or None,
                                  description or None) if p) or None

    # `referenceNo` est un CHAMP PUBLIE par la maison, pas une devinette de
    # titre : c'est la meilleure provenance possible. On ne retombe sur
    # l'extraction que s'il est vide.
    reference = (lot.get("referenceNo") or "").strip() or None
    provenance_ref = "champ_dedie" if reference else None
    if not reference:
        reference = reference_dans(titre)
        provenance_ref = "extrait_titre" if reference else None
    if not reference:
        reference = reference_libre(modele or "")
        provenance_ref = "jeton_titre" if reference else None

    annee = None
    circa = str(detail.get("circa") or "")
    trouve = re.search(r"\b(1[89]\d{2}|20[0-3]\d)\b", circa)
    if trouve:
        annee = int(trouve.group(1))

    return price_point(
        source_id=SOURCE["id"], source_type=SOURCE["type"],
        source_url=lot.get("detailLink"),
        external_id=str(lot.get("objectNumber") or "") or None,
        # `lotStatus` est publie lot par lot : la nature n'est pas une
        # constante d'adaptateur, elle est lue.
        price_nature="realised" if vendu else "estimate",
        price_nature_provenance="champ_dedie",
        listing_status="sold" if adjuge else "unsold",
        # Mesure du 21/09/2026 : soldPrice == hammerPricePlusBP sur 156/156
        # lots de NY080126, et se divise par le taux de frais de l'epoque en
        # rendant un marteau propre sur les ventes de 2015 et 2020.
        price_includes_premium=True if vendu else None,
        price_amount=montant if vendu else bas,
        price_currency=devise,
        price_date=jour,
        estimate_low=bas, estimate_high=haut,
        brand=marque, model=modele, title=titre,
        reference=reference, reference_provenance=provenance_ref,
        # La maison classe elle-meme le lot. 'WatchAuctionLot' vaut mieux que
        # tout ce qu'on devinerait d'un titre.
        source_category=lot.get("lotType"),
        year=annee,
        case_material=detail.get("material") or None,
        case_size_mm=detail.get("dimensions") or None,
        movement=_texte(detail.get("calibre")) or None,
        seller=SOURCE["name"],
    )


def lots_du_brut(entrees: list) -> list[tuple]:
    """(lot, date, devise, fuseau) pour chaque lot du brut deja stocke.

    Le brut porte le calendrier ET les pages de vente : la date et le fuseau se
    relisent donc sans une seule requete.
    """
    trouves: list[tuple] = []
    for entree in entrees:
        payload = entree.get("payload") or ""
        if "/auction/" not in (entree.get("url") or ""):
            continue
        vente = _vente_du_payload(payload)
        if not vente:
            continue
        fuseau = vente.get("auctionTimezone")
        devise = (vente.get("auctionCurrency") or {}).get("currencyCode")
        jour = _jour_local(vente.get("auctionStartDateTime"), fuseau)
        for lot in (vente.get("lots") or []):
            trouves.append((lot, jour, devise, fuseau))
    return trouves


def _detail(lot: dict, journal: list) -> dict:
    """La page d'un lot : `circa`, `material`, `calibre`, `dimensions`.

    Une requete par lot. Reserve a l'enrichissement explicite.
    """
    lien = lot.get("detailLink")
    if not lien:
        return {}
    try:
        resp = get(str(lien), pause=1.5)
    except Exception as exc:
        journal.append(f"detail {lot.get('objectNumber')}: {type(exc).__name__}")
        return {}
    if resp.status_code != 200:
        journal.append(f"detail {lot.get('objectNumber')}: HTTP {resp.status_code}")
        return {}
    for plat in _tableaux(resp.text):
        fiche_lot = _sous_la_cle(
            plat, "lot",
            garde=lambda v: isinstance(v, dict) and "objectNumber" in v)
        if fiche_lot:
            return {"_url": resp.url, "_payload": resp.text, **fiche_lot}
    return {}


# 105 ventes x jusqu'a 294 lots : le plafond par defaut laisse passer tout le
# fonds. Il reste un plafond, et il se dit dans le journal quand il mord.
def collect(cap: int = 30000, enrichir: int = 0):
    raw: list[dict] = []
    journal: list[str] = []
    records: list[dict] = []
    invendus = 0
    enrichis = 0

    try:
        index = get(CALENDRIER, params={"Departments": "watches"}, pause=1.5)
    except Exception as exc:
        return raw, records, [f"calendrier: {type(exc).__name__}"]
    raw.append({"url": index.url, "status": index.status_code, "payload": index.text})
    if index.status_code != 200:
        return raw, records, [f"calendrier: HTTP {index.status_code}"]

    ventes = ventes_montres(index.text)
    if not ventes:
        return raw, records, ["calendrier: aucune vente 'Watches' — "
                              "le payload a change de forme"]
    annees = sorted({str(v.get("auctionStartDateTime") or "")[:4] for v in ventes})
    journal.append(f"{len(ventes)} ventes du departement Montres, "
                   f"{annees[0]} -> {annees[-1]} "
                   f"(le calendrier en porte 896, tous departements confondus : "
                   f"'?Departments=watches' ne filtre pas cote serveur)")

    for vente in ventes:
        if len(records) >= cap:
            break
        code = vente.get("auctionCode")
        try:
            resp = get(f"{BASE}/auction/{code}/overview", pause=1.5)
        except Exception as exc:
            journal.append(f"{code}: {type(exc).__name__}")
            continue
        raw.append({"url": resp.url, "status": resp.status_code, "payload": resp.text})
        if resp.status_code != 200:
            journal.append(f"{code}: HTTP {resp.status_code}")
            continue

        detail_vente = _vente_du_payload(resp.text) or {}
        lots = detail_vente.get("lots") or []
        fuseau = detail_vente.get("auctionTimezone") or vente.get("auctionTimezone")
        devise = ((detail_vente.get("auctionCurrency") or {}).get("currencyCode")
                  or (vente.get("auctionCurrency") or {}).get("currencyCode"))
        jour = _jour_local(detail_vente.get("auctionStartDateTime")
                           or vente.get("auctionStartDateTime"), fuseau)
        if not lots:
            journal.append(f"{code} {jour}: page lue, 0 lot dans le payload")
            continue

        avant = len(records)
        for lot in lots:
            if len(records) >= cap:
                break
            supplement = {}
            if enrichis < enrichir:
                supplement = _detail(lot, journal)
                if supplement:
                    raw.append({"url": supplement.pop("_url", None),
                                "status": 200,
                                "payload": supplement.pop("_payload", None)})
                    enrichis += 1
            enregistrement = fiche(lot, jour, devise, fuseau, supplement)
            if enregistrement is None:
                continue
            if enregistrement["price_nature"] == "estimate":
                invendus += 1
            records.append(enregistrement)
        annonce = detail_vente.get("totalLotCount")
        journal.append(
            f"{jour} {code} {str(vente.get('auctionLocation') or '')[:11]:<11} "
            f"{devise or '?'} : {len(records) - avant} lots"
            + (f" (la vente en annonce {annonce})"
               if annonce and annonce != len(lots) else ""))

    if invendus:
        journal.append(f"{invendus} lots SANS PRIX REALISE gardes en nature "
                       f"'estimate' avec leur statut (invendu, retourne au "
                       f"proprietaire, ou adjuge sans prix publie) — savoir ou "
                       f"le marche a refuse de suivre vaut le detour")
    if enrichis:
        journal.append(f"{enrichis} lots enrichis par leur page (annee, matiere, "
                       f"calibre, diametre) — une requete chacun")
    journal.append("prix = soldPrice, FRAIS ACHETEUR INCLUS (mesure sur 1 175 "
                   "lots : 25 % de 2015 a 2019, 26 % de 2020 a 2022, 27 % "
                   "depuis 2024) ; le marteau nu n'est publie que sur les "
                   "ventes de 2026 et reste dans le brut")
    if len(records) >= cap:
        journal.append(f"TRONQUE: plafond de {cap} atteint — il reste des donnees a prendre")
    return raw, records, journal
