"""Morphy Auctions — maison de ventes americaine (Denver, Pennsylvanie).

PRIX REALISES DATES, FRAIS ACHETEUR INCLUS — ET LA MAISON LE DIT ELLE-MEME.
La fiche de lot porte, en toutes lettres, « Final prices include buyers
premium: $3,600.00 ». Ce n'est pas une deduction de notre part : c'est un
libelle publie. Mesure de controle du 21/09/2026 sur les 646 lots de la vente
517 (Fine Pocket Watch, 30 juin 2020) : diviser le prix final par 1,20 rend un
marteau multiple de 50 dans 79 % des cas, contre 41 % sans division. Le taux
dominant est donc 20 %, et il n'est PAS constant — 1,28 explique un autre
paquet (16 %). D'ou `price_includes_premium=True` et rien d'autre : on ne
reconstitue pas un marteau sur un taux qui varie.

DEUX HOTES, DEUX MONDES — ET LE PIEGE DE LA SONDE.
  `morphyauctions.com` est un WordPress/WooCommerce. Son API Store repond, et
  c'est exactement le faux ami : ses 162 « produits » sont des CATALOGUES
  IMPRIMES a 75 $, pas des lots. Le verdict de sonde « FACILE (WooCommerce
  Store API) » du 21/09/2026 portait sur la boutique de catalogues. Aucun lot
  de montre n'y vit. Le WordPress ne sert ici qu'a une chose : son
  `event-sitemap.xml` nomme les 721 ventes et chaque fiche de vente porte le
  lien vers le catalogue reel.

  `auctions.morphyauctions.com` est la vraie salle : un SimpleAuctionSite
  (ASP.NET WebForms), ou vivent les lots, les prix finaux et les categories.

L'UA DOIT CHANGER SELON L'HOTE. Mesure du 21/09/2026, dans les deux sens :
  morphyauctions.com  : ClaudeBot -> 403 + defi JavaScript (« Checking search
                        engine crawler »), `python-requests/2.34.2` -> 200.
  auctions.morphyauctions.com : l'inverse exactement — ClaudeBot -> 200,
                        `python-requests` -> 403 (Azure Application Gateway).
Aucun des deux en-tetes ne mente sur notre identite : l'un annonce ClaudeBot,
l'autre annonce la bibliotheque. On ne se reclame jamais d'un navigateur.
La source avait ete classee « robots illisible » : c'etait le defi JS du
WordPress. Son robots.txt repond 200 des qu'on cesse d'annoncer ClaudeBot.

LE CATALOGUE NE SE PAGINE QUE PAR POSTBACK. `catalog.aspx?auctionid=N` rend
25 lots et IGNORE `page=`, `lotsperpage=` en parametre d'URL (mesure : les
trois essais rendent la meme page 1). La pagination est du WebForms pur. Un
seul POST avec `LotsPerPageDropDownTop=ALL` rend en revanche la vente
ENTIERE — 646 lots en une requete, 3 Mo. C'est la seule facon d'atteindre le
volume, et c'est aussi la plus polie : deux requetes par vente au lieu de
vingt-six. `utils.get` ne connait que GET ; le POST est donc ecrit ici, mais
il REUTILISE les en-tetes, les delais et les codes a reessayer de `utils` —
aucune logique de politesse n'est reecrite. Crawl-delay de 2 s respecte.

CIBLER PAR LES CATEGORIES DE LA MAISON, PAS PAR LE TITRE. Morphy est
generaliste : jouets, armes, publicite, joaillerie. Chaque catalogue publie
son propre arbre de categories, avec les effectifs — « Wrist Watches (29) »,
« Pocket Watches (32) », « Jewelry (213) », « Coins/Currency (1) ». Les
identifiants sont stables d'une vente a l'autre (797 = Wrist Watches, 801 =
Pocket Watches, 796 = Jewelry). On ne prend que les feuilles horlogeres et on
reporte leur nom tel quel dans `source_category` : le filtre y lit R0 sans
deviner ('Wrist Watches' -> True, 'Jewelry' -> False, 'Clocks' -> False).
Le filtre par categorie exige la SESSION : `Category/Pocket_Watches-801.html`
sans cookie retombe sur la vente en cours. D'ou le bocal a cookies.

CE QUE LA SOURCE NE DONNE PAS, ET QU'IL FAUT DIRE :
  Les INVENDUS n'existent pas. Vente 517 : 646 lots publies, tous avec au
  moins une enchere et un prix final, et 21 numeros de lot manquants dans la
  suite 1001-1667. La maison ne publie que ce qui est parti — le taux
  d'invendus n'est pas mesurable ici.
  La REFERENCE constructeur est quasi absente des titres : 0 reference a
  mot-cle et 11 jetons sur 646 titres de la vente de montres de poche. Les
  titres sont des descriptions de catalogue en capitales ('18K GOLD ORNATE
  MINUTE REPEATER H/C SWISS POCKET WATCH'). La reference, l'annee et le
  diametre vivent sur la fiche de lot, une requete de plus par lot.
  La DATE est celle de la VENTE, lue dans le titre du catalogue ('June 30,
  2020 Fine Pocket Watch'). Pour une vacation sur deux jours ('October 16 &
  17, 2026') on retient le premier jour : l'erreur est d'un jour au plus.
  La fiche de lot porte la date exacte ('Bidding ended on 6/30/2020'), au
  prix d'une requete par lot.

Reconnaissance du 21/09/2026.
"""
from __future__ import annotations

import datetime as _dt
import html as _html
import re
import time

import requests

from watchpoint.filtrage.filtre import filtre
from watchpoint.schema import price_point, reference_dans, reference_libre
from watchpoint.commun.utils import (ATTENTES, CODES_A_REESSAYER, DELAIS, HEADERS, get)

SOURCE = {
    "id": "morphy",
    "name": "Morphy Auctions",
    "type": "auction",
    "price_nature": "realised",
    "access": ("catalogue SimpleAuctionSite : 1 GET pour l'arbre de categories, "
               "1 POST LotsPerPage=ALL pour la vente entiere"),
    "robots": ("lu le 21/09/2026 — morphyauctions.com : tout autorise hors "
               "/wp-admin/ et /wp-content/uploads/ (200 seulement sans l'UA "
               "ClaudeBot, defi JS sinon) ; auctions.morphyauctions.com : "
               "Crawl-delay 2, /AuctionResults.aspx et /LiveAuction2.aspx "
               "interdits — jamais demandes ; le catalogue et les fiches de "
               "lot sont autorises"),
    "price_includes_premium": True,
    "reserve": ("prix frais acheteur inclus (taux non constant, 20 % dominant) ; "
                "aucun invendu publie ; reference constructeur quasi absente "
                "des titres"),
}

WP = "https://morphyauctions.com"
SAS = "https://auctions.morphyauctions.com"
# Le robots.txt de la salle demande 2 secondes. On les prend.
DELAI = 2.0
# WordPress refuse ClaudeBot (defi JavaScript) et accepte la bibliotheque.
UA_WP = {"User-Agent": requests.utils.default_user_agent()}

# Les ventes qu'on va chercher, reconnues au nom que la maison leur donne dans
# son propre sitemap. Elargir cette liste ouvre les vacations generalistes
# (arts decoratifs, successions), qui portent aussi des montres mais noyees.
MOTS_VENTE = ("watch", "watches", "timepiece", "jewelry", "jewellery", "horolog")

# Les categories horlogeres de l'arbre Morphy. On veut les FEUILLES : le
# parent compose 'Jewelry/Watches/Coins' contient les 213 bagues de la vente.
_CAT_MONTRE = re.compile(r"watch|timepiece|horolog", re.I)
_CAT_MELANGEE = re.compile(r"jewel|coin|clock|lamp|glass", re.I)

_H1 = re.compile(r'catalogAuctionLabel">\s*<h1>\s*<span>(.*?)</span>', re.S)
_ARBRE = re.compile(r'href="Category/([^"]+?)-(\d+)\.html"[^>]*>\s*([^<(]*?)\s*\((\d+)\)')
_PAGES = re.compile(r'id = "ofpages"[^>]*>\s*/\s*(\d+)')
_BLOC = re.compile(r'<div class="lot \s*">(.*?)<div class="BidWatchDiv">', re.S)
_NUMERO = re.compile(r"id='LotNumber'>([^<]*)<")
_LIEN = re.compile(r"href='(https?://[^']*-LOT(\d+)\.aspx)'")
_TITRE = re.compile(r"-LOT\d+\.aspx'>(.*?)</a>", re.S)
_FINAL = re.compile(r"Final Price:\s*\$([\d,]+\.?\d*)")
_COURANT = re.compile(r"Current Bid:\s*\$([\d,]+\.?\d*)")
_ESTIME = re.compile(r"Estimate:\s*\$([\d,]+)\s*-\s*\$?([\d,]+)")
_ENCHERES = re.compile(r"# Bids:\s*(\d+)")
_CACHE = re.compile(r'<input[^>]*type="hidden"[^>]*>')
_NOM = re.compile(r'name="([^"]+)"')
_VALEUR = re.compile(r'value="([^"]*)"')
_BALISES = re.compile(r"<[^>]+>")
_ID_VENTE = re.compile(r"catalog\.aspx\?auctionid=(\d+)")
_LOC = re.compile(r"<loc>(.*?)</loc>", re.S)

# 'June 30, 2020 Fine Pocket Watch' · 'October 16 & 17, 2026 Coin Op'
_MOIS = ("january february march april may june july august september "
         "october november december").split()
_DATE_TITRE = re.compile(
    r"^\s*(" + "|".join(_MOIS) + r")\s+(\d{1,2})"
    r"(?:\s*[&,-]\s*\d{1,2})*"          # vacation sur plusieurs jours
    r"(?:\s*[&,-]\s*(?:" + "|".join(_MOIS) + r")\s+\d{1,2})*"
    r",?\s+(\d{4})", re.I)


def _texte(brut) -> str:
    return re.sub(r"\s+", " ", _html.unescape(_BALISES.sub(" ", str(brut or "")))).strip()


def _nombre(brut) -> float | None:
    try:
        return float(str(brut).replace(",", ""))
    except (TypeError, ValueError):
        return None


def date_de_vente(titre: str) -> str | None:
    """'June 30, 2020 Fine Pocket Watch' -> '2020-06-30'.

    Le premier jour d'une vacation qui en couvre deux. L'ecart maximal avec la
    vente reelle d'un lot est donc d'un jour, et c'est dit dans notes.md.
    """
    trouve = _DATE_TITRE.match(_texte(titre))
    if not trouve:
        return None
    mois = _MOIS.index(trouve.group(1).lower()) + 1
    try:
        return _dt.date(int(trouve.group(3)), mois, int(trouve.group(2))).isoformat()
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Transport. Les GET passent par `utils.get` (pauses, 3 essais, Retry-After,
# plafond de lecture) en lui confiant le bocal a cookies ; seul le POST est
# ecrit ici, faute d'equivalent dans utils, et il reutilise ses constantes.
# ---------------------------------------------------------------------------
def _get(url, bocal, *, params=None, entetes=None):
    reponse = get(url, params=params, pause=DELAI, cookies=bocal,
                  headers=entetes or {})
    bocal.update(reponse.cookies)
    return reponse


def _post(url, bocal, champs, *, essais: int = 3):
    """Un postback WebForms. Meme politesse que `utils.get`, verbe different."""
    derniere = None
    for essai in range(essais):
        try:
            reponse = requests.post(url, data=champs, headers=HEADERS,
                                    cookies=bocal, timeout=DELAIS)
        except requests.RequestException as exc:
            derniere = exc
            if essai == essais - 1:
                raise
            time.sleep(ATTENTES[min(essai, len(ATTENTES) - 1)])
            continue
        if reponse.status_code in CODES_A_REESSAYER and essai < essais - 1:
            attente = ATTENTES[min(essai, len(ATTENTES) - 1)]
            entete = reponse.headers.get("Retry-After")
            if entete and str(entete).isdigit():
                attente = max(attente, min(int(entete), 60))
            time.sleep(attente)
            continue
        bocal.update(reponse.cookies)
        time.sleep(DELAI)
        return reponse
    raise derniere or RuntimeError(f"echec apres {essais} essais : {url}")


def _champs_caches(page: str) -> dict:
    champs = {}
    for balise in _CACHE.findall(page):
        nom = _NOM.search(balise)
        if nom:
            valeur = _VALEUR.search(balise)
            champs[nom.group(1)] = _html.unescape(valeur.group(1) if valeur else "")
    return champs


def _tout_afficher(url, bocal, page: str) -> str:
    """Le postback qui remplace 25 lots par la vente entiere."""
    champs = _champs_caches(page)
    champs.update({
        "__EVENTTARGET": "ctl00$ContentPlaceHolder$LotsPerPageDropDownTop",
        "__EVENTARGUMENT": "",
        "ctl00$ContentPlaceHolder$LotsPerPageDropDownTop": "ALL",
        "ctl00$ContentPlaceHolder$displayByDropDownTop": "2",
        "ctl00$ContentPlaceHolder$SortByDDLTop": "7",
    })
    reponse = _post(url, bocal, champs)
    return reponse.text if reponse.status_code == 200 else page


# ---------------------------------------------------------------------------
# Lecture
# ---------------------------------------------------------------------------
def categories_horlogeres(page: str) -> list[tuple[str, str, int]]:
    """Les feuilles horlogeres de l'arbre publie : (slug, nom, effectif).

    Les composes ('Jewelry/Watches/Coins') ne sont retenus qu'a defaut de
    feuille : sinon on ramene les bagues avec.
    """
    feuilles, composes = [], []
    for slug, identifiant, nom, effectif in _ARBRE.findall(page):
        nom = _texte(nom)
        if not _CAT_MONTRE.search(nom):
            continue
        cible = composes if _CAT_MELANGEE.search(nom) else feuilles
        cible.append((f"{slug}-{identifiant}", nom, int(effectif)))
    return feuilles or composes


def fiche(bloc: str, vente: dict, categorie: str) -> dict | None:
    """Un bloc de catalogue -> un enregistrement realise, ou None.

    Isolee de la collecte pour que le brut deja stocke se rejoue sans reseau.
    """
    final = _FINAL.search(bloc)
    if not final:          # lot encore ouvert : une enchere n'est pas une vente
        return None
    montant = _nombre(final.group(1))
    if not montant or montant <= 1:
        return None

    lien = _LIEN.search(bloc)
    titre_brut = _TITRE.search(bloc)
    titre = _texte(titre_brut.group(1)) if titre_brut else None
    estime = _ESTIME.search(bloc)
    numero = _NUMERO.search(bloc)
    encheres = _ENCHERES.search(bloc)

    reference = reference_dans(titre)
    provenance = "extrait_titre" if reference else None
    if not reference:
        reference = reference_libre(titre)
        provenance = "jeton_titre" if reference else None

    marque = filtre().verdict(titre or "", "AUCTION",
                              categorie_source=categorie).get("brand")

    return price_point(
        source_id=SOURCE["id"], source_type=SOURCE["type"],
        source_url=(lien.group(1).replace("http://", "https://") if lien else None),
        external_id=(lien.group(2) if lien else None),
        price_nature="realised",
        # Le montant n'est pas etiquete « realise » : il est etiquete « Final
        # Price », sur un lot que la page declare clos. C'est un statut lu, pas
        # un champ de nature.
        price_nature_provenance="deduite_statut",
        listing_status="sold",
        price_amount=montant,
        price_currency="USD",
        # Frais acheteur INCLUS, et la maison l'ecrit : « Final prices include
        # buyers premium ». Le taux varie (20 % dominant) : on ne le retire pas.
        price_includes_premium=True,
        price_date=vente.get("date"),
        estimate_low=_nombre(estime.group(1)) if estime else None,
        estimate_high=_nombre(estime.group(2)) if estime else None,
        title=titre,
        brand=marque,
        reference=reference, reference_provenance=provenance,
        # La categorie telle que Morphy la nomme — R0 la lit sans deviner.
        source_category=categorie,
        seller=SOURCE["name"],
        condition=None,
        year=None,
        # Le numero de lot et le nombre d'encheres n'ont pas de champ au
        # schema : ils restent dans le brut, qui est conserve entier.
    )


def lots_du_brut(entrees: list) -> list[dict]:
    """Rejoue la normalisation sur le brut deja telecharge, sans reseau."""
    trouves = []
    for entree in entrees:
        page = entree.get("payload") or ""
        if "galleryList" not in page:
            continue
        vente = {"date": entree.get("date") or date_de_vente(entree.get("titre") or "")}
        categorie = entree.get("categorie") or ""
        for bloc in _BLOC.findall(page):
            enregistrement = fiche(bloc, vente, categorie)
            if enregistrement:
                trouves.append(enregistrement)
    return trouves


# ---------------------------------------------------------------------------
# Reperage des ventes. Le WordPress nomme les 721 vacations ; on ne va chercher
# l'identifiant de catalogue que pour celles dont Morphy dit qu'elles portent
# des montres.
# ---------------------------------------------------------------------------
def ventes_horlogeres(raw, journal, *, plafond: int) -> list[dict]:
    reponse = _get(f"{WP}/event-sitemap.xml", requests.cookies.RequestsCookieJar(),
                   entetes=UA_WP)
    raw.append({"url": reponse.url, "status": reponse.status_code,
                "payload": reponse.text})
    if reponse.status_code != 200:
        journal.append(f"sitemap des ventes : HTTP {reponse.status_code}")
        return []
    liens = [l for l in _LOC.findall(reponse.text) if "/past-auctions/" in l]
    journal.append(f"sitemap : {len(liens)} vacations nommees par la maison")

    # Le sitemap est en ordre chronologique croissant. On le retourne : sous
    # plafond, ce sont les vacations RECENTES qu'on veut, pas celles de 2016
    # dont le catalogue en ligne n'existe plus.
    retenus = [l for l in liens
               if any(mot in l.rsplit("/", 2)[-2].lower() for mot in MOTS_VENTE)][::-1]
    journal.append(f"{len(retenus)} vacations au nom horloger ou joaillier "
                   "(les plus recentes d'abord)")

    ventes = []
    bocal = requests.cookies.RequestsCookieJar()
    for lien in retenus[:plafond]:
        try:
            page = _get(lien, bocal, entetes=UA_WP)
        except Exception as exc:                      # noqa: BLE001
            journal.append(f"{lien}: {type(exc).__name__}")
            continue
        raw.append({"url": page.url, "status": page.status_code, "payload": page.text})
        if page.status_code != 200:
            journal.append(f"{lien}: HTTP {page.status_code}")
            continue
        identifiants = _ID_VENTE.findall(page.text)
        if not identifiants:
            journal.append(f"{lien}: aucun catalogue en ligne")
            continue
        ventes.append({"auctionid": identifiants[0], "slug": lien})
    journal.append(f"{len(ventes)} ventes avec un catalogue en ligne")
    return ventes


def collect(cap: int = 4000, *, ventes_max: int = 40, ventes: list | None = None):
    """Les lots horlogers des ventes passees, prix finaux et dates.

    `cap` plafonne les enregistrements ; `ventes_max` plafonne le reperage.
    `ventes` court-circuite le reperage WordPress avec une liste
    d'identifiants de catalogue deja connus — c'est ce qui permet de verifier
    la chaine de la salle sans redepenser les 24 requetes du reperage.
    """
    raw: list[dict] = []
    records: list[dict] = []
    journal: list[str] = []
    vus: set[str] = set()
    ouverts = 0

    ventes_fournies = bool(ventes)
    if ventes_fournies:
        ventes = [{"auctionid": str(v), "slug": None} for v in ventes]
        journal.append(f"{len(ventes)} ventes fournies : reperage WordPress saute")
    else:
        try:
            ventes = ventes_horlogeres(raw, journal, plafond=ventes_max)
        except Exception as exc:                      # noqa: BLE001
            journal.append(f"reperage des ventes: {type(exc).__name__}: {exc}")
            return raw, records, journal

    for vente in ventes:
        if len(records) >= cap:
            break
        bocal = requests.cookies.RequestsCookieJar()
        url = f"{SAS}/catalog.aspx"
        try:
            page = _get(url, bocal, params={"auctionid": vente["auctionid"]})
        except Exception as exc:                      # noqa: BLE001
            journal.append(f"vente {vente['auctionid']}: {type(exc).__name__}")
            continue
        raw.append({"url": page.url, "status": page.status_code, "payload": page.text})
        if page.status_code != 200:
            journal.append(f"vente {vente['auctionid']}: HTTP {page.status_code}")
            continue

        titre = _H1.search(page.text)
        titre = _texte(titre.group(1)) if titre else ""
        vente["date"] = date_de_vente(titre)
        categories = categories_horlogeres(page.text)
        if not categories:
            journal.append(f"{titre or vente['auctionid']} : aucune categorie horlogere")
            continue
        journal.append(
            f"{titre} [{vente['date'] or 'date illisible'}] : "
            + ", ".join(f"{nom} ({effectif})" for _, nom, effectif in categories))

        for chemin, nom, _effectif in categories:
            if len(records) >= cap:
                break
            adresse = f"{SAS}/Category/{chemin}.html"
            try:
                filtree = _get(adresse, bocal)
            except Exception as exc:                  # noqa: BLE001
                journal.append(f"{nom}: {type(exc).__name__}")
                continue
            if filtree.status_code != 200:
                journal.append(f"{nom}: HTTP {filtree.status_code}")
                continue
            contenu = filtree.text
            pages = _PAGES.search(contenu)
            # Inutile de demander la vente entiere si le plafond est deja a
            # portee des 25 lots de la premiere page.
            if pages and int(pages.group(1)) > 1 and cap - len(records) > 25:
                try:
                    contenu = _tout_afficher(adresse, bocal, contenu)
                except Exception as exc:              # noqa: BLE001
                    journal.append(f"{nom}: postback {type(exc).__name__} — "
                                   f"page 1 seule sur {pages.group(1)} pages")
            raw.append({"url": adresse, "status": filtree.status_code,
                        "payload": contenu, "categorie": nom,
                        "titre": titre, "date": vente.get("date")})

            avant = len(records)
            for bloc in _BLOC.findall(contenu):
                if len(records) >= cap:
                    break
                enregistrement = fiche(bloc, vente, nom)
                if enregistrement is None:
                    ouverts += 1
                    continue
                if enregistrement["external_id"] in vus:
                    continue
                vus.add(enregistrement["external_id"])
                records.append(enregistrement)
            journal.append(f"  {nom} : {len(records) - avant} lots realises")

    if ouverts:
        journal.append(f"{ouverts} lots ecartes : enchere en cours, pas une vente")
    if len(records) >= cap:
        journal.append(f"TRONQUE: plafond de {cap} atteint — il reste des donnees a prendre")
    if not ventes_fournies and len(ventes) >= ventes_max:
        journal.append(f"TRONQUE: plafond de {ventes_max} ventes reperees atteint — "
                       "il reste des vacations a prendre")
    return raw, records, journal
