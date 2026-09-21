"""Antiquorum — maison de ventes 100 % horlogere. Prix REALISES depuis 1989.

C'est le plus gros gisement date du dossier. Le catalogue en ligne couvre
1989 -> aujourd'hui, environ 380 ventes et de l'ordre de 100 000 lots vendus,
en HTML servi par le serveur, sans JavaScript, sans mur, sans cle.

  ATTENTION — LE SITE A DEMENAGE. L'audit de juillet 2026 donnait
  `www.antiquorum.swiss/en/auctions/{ID}/price-list`. Ce chemin rend 404 depuis
  que le site vitrine est passe sous WordPress : le catalogue vit maintenant sur
  le sous-domaine `catalog.antiquorum.swiss` (mesure du 21/09/2026). Meme
  arborescence, autre hote.

Trois routes, et il faut les trois :

  1. `GET /auctions?locale=en&year=AAAA` — la liste des ventes de l'annee, avec
     le titre, le lieu, la ou les DATES de vacation, le total de la vente, le
     numero de la price-list et le slug du catalogue. Le selecteur d'annee
     descend jusqu'a 1989 : 38 annees, donc 38 requetes pour enumerer TOUT.

  2. `GET /en/auctions/{ID}/price-list` — UNE requete rend TOUS les lots vendus
     d'une vente, avec le marteau. C'est la seule route qui publie le marteau nu.

  3. `GET /en/auctions/{slug}/lots?page=N` — le catalogue, 20 lots par page, et
     c'est la que vit l'identite : titre, description, marque en RDFa, devise, et
     sur les ventes modernes un bloc de CHAMPS DEDIES (Brand, Model, Reference,
     Year, Diameter, Caliber). C'est aussi la seule route qui donne la devise.

La collecte est une JOINTURE des routes 2 et 3 sur l'URL du lot.

Les pieges, tous mesures le 21/09/2026 et traites ici :

  LE MARTEAU N'EST PAS LE PRIX AFFICHE. La price-list porte deux colonnes,
  `hammer` et `+premium`, et l'audit avait raison de prevenir : la premiere
  colonne est le MARTEAU, pas l'estimation. Verifie sur 145 lots de la vente 388
  et 380 de la vente 14 : la seconde colonne vaut exactement la premiere
  multipliee par le taux de frais. Partout ailleurs sur le site — le `Sold: EUR
  406,720` de la fiche et du catalogue — c'est le prix FRAIS INCLUS qui est
  publie. On charge donc le marteau, `price_includes_premium=False`.

  LE TAUX DE FRAIS A CHANGE D'EPOQUE. Median mesure sur 1 119 lots de quatre
  price-lists : 1,150 en 1989, 1,150 en 2001, 1,250 en 2015, 1,312 en 2026. Et il
  est DEGRESSIF sur les gros lots — 540 000 -> 597 500, soit 1,104, dans la vente
  de 2001. On ne peut donc PAS retrouver le marteau en divisant un prix frais
  inclus par un taux : il faut la price-list.

  `schema:price` EST L'ESTIMATION BASSE, PAS LE PRIX VENDU. Le RDFa de chaque
  lot annonce `schema:price` = 300000 sur un lot parti a 406 720, et 500 sur un
  lot parti a 1 115. Le prendre pour un prix realise diviserait la base par
  trois. Il n'entre ici que dans `estimate_low`.

  `priceValidUntil` EST UN BOUCHON. Il vaut 2026/09/30 sur un lot vendu en 2001.
  Jamais une date de vente.

  LA DEVISE N'EST PAS SUR LA PRICE-LIST. Elle change avec la ville : CHF a
  Geneve, EUR a Monaco et Milan, HKD a Hong Kong, USD a New York, JPY a Tokyo.
  On ne la devine pas : on la lit dans `schema:priceCurrency` de chaque lot du
  catalogue. Une price-list lue seule rend des montants sans devise — inutilisables.

  LES INVENDUS SONT ABSENTS DE LA PRICE-LIST. Vente 388 : 145 lignes pour des
  lots numerotes jusqu'a 217. Biais de survie assume et signale, comme chez
  Artcurial. Le catalogue, lui, porte bien les invendus — sans prix.

  LES VENTES A VACATIONS MULTIPLES ONT PLUSIEURS DATES. Geneve, mai 2026 :
  « Session 1: Lots 1-285, May 09, 2026 / Session 2: Lots 286-445, May 10, 2026 ».
  La date est donc affectee PAR TRANCHE DE NUMERO DE LOT, pas en bloc.

  LES GUILLEMETS NE SONT PAS ECHAPPES DANS LES ATTRIBUTS. Le site ecrit
  `content="ROLEX, ... DAYTONA "PAUL NEWMAN", STAINLESS STEEL "`. Un motif
  `content="([^"]*)"` coupe le titre au premier guillemet interne. On termine
  donc sur `"></div>`, et on prefere le texte du lien, lui correctement echappe.

  LES SLUGS ANCIENS NE PORTENT AUCUNE IDENTITE. `/en/lots/lot-14-2` en 2001
  contre `/en/lots/rolex-ref-6264-daytona-paul-newman-lot-388-217` en 2026. Sur
  les ventes anciennes, la price-list seule ne donne ni marque ni reference :
  le catalogue est indispensable.

  LE CATALOGUE MODERNE N'AFFICHE PAS SA PAGINATION. `?page=2` fonctionne mais
  aucun lien de page n'est rendu sur les ventes recentes, alors qu'il l'est sur
  les anciennes. On avance donc jusqu'a la premiere page vide.

robots.txt de catalog.antiquorum.swiss nous nomme : une section `User-agent:
ClaudeBot` avec `Crawl-delay: 5`, `Allow: /en/lots/`, et trois Disallow que l'on
respecte (`/en/users/`, et les URL portant `lot_id=`, `from_btn=` ou `fbclid=`
— d'ou le fait qu'on n'appelle jamais les liens « favori » des fiches).
`live.antiquorum.swiss` (AuctionMobility) rend 403 : on n'y touche pas.
"""
from __future__ import annotations

import datetime as dt
import html as _html
import re

from filtre import filtre
from schema import price_point, reference_dans
from utils import get

SOURCE = {
    "id": "antiquorum",
    "name": "Antiquorum",
    "type": "auction",
    "price_nature": "realised",
    "access": "HTML serveur sur catalog.antiquorum.swiss — jointure price-list "
              "(marteau) x catalogue /lots (identite, devise)",
    "robots": "OK — section ClaudeBot dediee, Crawl-delay: 5, Allow /en/lots/ ; "
              "Disallow /en/users/ et les URL a lot_id=/from_btn=/fbclid= "
              "(jamais appelees). robots.txt relu le 21/09/2026",
    # Maison exclusivement horlogere depuis 1974 : dans une vente Antiquorum,
    # exiger le mot « montre » dans le titre du lot n'a pas de sens (R4c).
    "corpus_horloger": True,
    "reserve": "la price-list ne liste que les lots VENDUS : biais de survie "
               "assume. Les ventes mixtes (titres portant 'Jewelry') font "
               "entrer quelques bijoux, que R1 rejette.",
}

BASE = "https://catalog.antiquorum.swiss"
# Le selecteur d'annee du catalogue descend a 1989 (releve le 21/09/2026).
ANNEE_MIN = 1989
LOTS_PAR_PAGE = 20
# robots.txt : `User-agent: ClaudeBot / Crawl-delay: 5`. On l'applique.
PAUSE = 5.0
# Un catalogue n'a jamais 200 pages ; ce garde-fou evite une boucle infinie si
# le site se mettait a servir la meme page indefiniment.
PAGES_MAX = 120


# ---------------------------------------------------------------------------
# petits outils de lecture HTML
# ---------------------------------------------------------------------------
_BALISES = re.compile(r"<[^>]+>")


def _texte(brut) -> str:
    if not brut:
        return ""
    return _html.unescape(_BALISES.sub(" ", str(brut))).replace("\xa0", " ").strip()


def _un_espace(texte: str) -> str:
    return re.sub(r"\s+", " ", texte or "").strip()


_MOIS = ("jan", "feb", "mar", "apr", "may", "jun",
         "jul", "aug", "sep", "oct", "nov", "dec")
# 'Jun 28, 2026' · 'May 09, 2026' · 'Dec 15, 1989'. L'en-tete d'une price-list
# de vente a deux vacations ecrit 'Hong Kong, June 27&28, 2015' : on retient le
# PREMIER jour, sinon la vente entiere ressort sans date.
_DATE_US = re.compile(
    r"([A-Za-z]{3,9})\.?\s+(\d{1,2})(?:st|nd|rd|th)?"
    r"(?:\s*(?:&|and|-|–|/)\s*\d{1,2}(?:st|nd|rd|th)?)*"
    r"\s*,\s*(\d{4})", re.I)
# '31st March 2001', en-tete de la price-list
_DATE_GB = re.compile(r"(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]{3,9})\.?\s+(\d{4})")


def _iso(jour: int, mois: str, annee: int) -> str | None:
    try:
        numero = _MOIS.index(mois[:3].lower()) + 1
        return dt.date(annee, numero, jour).isoformat()
    except (ValueError, IndexError):
        return None


def _date_dans(texte) -> str | None:
    """La premiere date d'un texte, quel que soit son ordre, en ISO."""
    texte = _texte(texte)
    trouve = _DATE_US.search(texte)
    if trouve:
        return _iso(int(trouve.group(2)), trouve.group(1), int(trouve.group(3)))
    trouve = _DATE_GB.search(texte)
    if trouve:
        return _iso(int(trouve.group(1)), trouve.group(2), int(trouve.group(3)))
    return None


# 'Session 1: Lots 286-445, May 10, 2026'
_SESSION = re.compile(r"Lots?\s*(\d+)\s*[-–]\s*(\d+)\s*,\s*([A-Za-z]{3,9}\.?\s+\d{1,2},\s*\d{4})",
                      re.I)


def _vacations(bloc: str) -> list[tuple[int | None, int | None, str | None]]:
    """[(lot_min, lot_max, date)] — une vente peut avoir plusieurs vacations.

    Sans cela, les 672 lots d'une vente de Geneve etalee sur deux jours
    recevraient tous la date du premier jour.
    """
    texte = _texte(bloc)
    tranches = [(int(a), int(b), _date_dans(d)) for a, b, d in _SESSION.findall(texte)]
    if tranches:
        return [(a, b, d) for a, b, d in tranches if d]
    date = _date_dans(texte)
    return [(None, None, date)] if date else []


def _date_du_lot(vacations, numero_lot) -> str | None:
    """La date de la vacation qui contient ce numero de lot."""
    if not vacations:
        return None
    if numero_lot is not None:
        for debut, fin, date in vacations:
            if debut is not None and debut <= numero_lot <= fin:
                return date
    return vacations[0][2]


# ---------------------------------------------------------------------------
# route 1 — les ventes d'une annee
# ---------------------------------------------------------------------------
_CARTE_VENTE = '<div class="card shadow mb-3 p-4"'
_PRICELIST = re.compile(r"/en/auctions/(\d+)/price-list")
_CATALOGUE = re.compile(r"/en/auctions/([^/\"]+)/lots")


def ventes_de_la_page(html_page: str, annee: int | None = None) -> list[dict]:
    """Les ventes decrites par une page `/auctions?year=AAAA`. Fonction pure."""
    trouvees = []
    for carte in html_page.split(_CARTE_VENTE)[1:]:
        titre = re.search(r"<h5>(.*?)</h5>", carte, re.S)
        if not titre:
            continue
        # <h5>titre</h5> <p>lieu</p> <h6><p>date(s)</p></h6>
        lieu = re.search(r"</h5>\s*<p>(.*?)</p>", carte, re.S)
        bloc_date = re.search(r"<h6>(.*?)</h6>", carte, re.S)
        pl = _PRICELIST.search(carte)
        # Le slug du catalogue est nomme ('monaco_june_2026') sur les ventes
        # passees et NUMERIQUE ('389') sur la plus recente, avant qu'un slug lui
        # soit attribue. Les deux sont valides : /lots ne designe rien d'autre.
        cat = next(iter(_CATALOGUE.findall(carte)), None)
        total = re.search(r"Sale Totaled:\s*([^<]+)<", carte)
        trouvees.append({
            "annee": annee,
            "titre": _un_espace(_texte(titre.group(1))),
            "lieu": _un_espace(_texte(lieu.group(1))) if lieu else None,
            "vacations": _vacations(bloc_date.group(1)) if bloc_date else [],
            "pricelist": pl.group(1) if pl else None,
            "catalogue": cat,
            "total": _un_espace(total.group(1)) if total else None,
        })
    return trouvees


# ---------------------------------------------------------------------------
# route 2 — la price-list : le marteau, et lui seul
# ---------------------------------------------------------------------------
_LIGNE_PRIX = re.compile(
    r'<a class="lotnumber"[^>]*href="([^"]+)"[^>]*>\s*([^<]*?)\s*</a>\s*'
    r"<h3>([^<]*)</h3>\s*<span></span>\s*<h3>([^<]*)</h3>")


def _nombre(texte) -> float | None:
    texte = re.sub(r"[\s',]", "", str(texte or ""))
    try:
        return float(texte)
    except ValueError:
        return None


def marteaux_de_la_page(html_page: str) -> dict[str, dict]:
    """{chemin du lot: {lot, marteau, frais_inclus}} — fonction pure.

    Les deux colonnes sont conservees : la premiere est le marteau, la seconde
    le meme marteau frais inclus. Leur rapport est ce qui prouve que la
    premiere colonne n'est pas une estimation.
    """
    lots = {}
    for chemin, numero, marteau, avec_frais in _LIGNE_PRIX.findall(html_page):
        valeur = _nombre(marteau)
        if valeur is None or valeur <= 0:
            continue
        lots[chemin.strip()] = {
            "lot": numero.strip(),
            "marteau": valeur,
            "frais_inclus": _nombre(avec_frais),
        }
    return lots


def entete_price_list(html_page: str) -> dict:
    """Le titre, le lieu, la date et le total portes par la price-list."""
    entete = re.search(r'class="catalogName">(.*?)</h1>', html_page, re.S)
    if not entete:
        return {}
    lignes = [_un_espace(_texte(x)) for x in re.split(r"<br\s*/?>", entete.group(1))]
    lignes = [x for x in lignes if x]
    return {
        "lieu_et_date": lignes[0] if lignes else None,
        "titre": lignes[1] if len(lignes) > 1 else None,
        "date": _date_dans(lignes[0]) if lignes else None,
        "total": _un_espace(lignes[-1]) if len(lignes) > 2 else None,
    }


# ---------------------------------------------------------------------------
# route 3 — le catalogue : l'identite du lot
# ---------------------------------------------------------------------------
_CARTE_LOT = '<div class="shadow mt-4">'
# Les attributs `content` du site portent des guillemets NON echappes : on
# termine sur `"></div>` plutot que sur le premier guillemet.
_RDFA_NOM = re.compile(r'property="schema:name" content="(.*?)"></div>', re.S)
_RDFA_DESC = re.compile(r'property="schema:description" content="(.*?)"></div>', re.S)
_RDFA_MARQUE = re.compile(
    r'(?s)rel="schema:brand">\s*<div typeof="schema:Brand">\s*'
    r'<div property="schema:name" content="(.*?)"></div>')
_RDFA_URL = re.compile(r'rel="schema:url" resource="([^"]+)"')
_RDFA_DEVISE = re.compile(r'property="schema:priceCurrency" content="([A-Z]{3})"')
_RDFA_PRIX = re.compile(r'property="schema:price" content="([^"]+)"')
_RDFA_SKU = re.compile(r'property="schema:sku" content="([^"]+)"')
_NUMERO_LOT = re.compile(r"<h4>\s*LOT\s*([0-9]+[A-Za-z]?)")
_TITRE_LIEN = re.compile(
    r'(?s)class="N_lots_description col">.*?<p><a href="[^"]*">(.*?)</a></p>')
_ESTIMATION = re.compile(r"N_lots_estimation'\s*>\s*([^<]+)<")
_VENDU = re.compile(r"Sold:\s*([A-Z]{3})\s*([\d,.']+)")
_GRADE = re.compile(r"Grading System:\s*([^<]*)<")
_CHAMP = re.compile(r"<strong>([^<]{2,24})</strong>&emsp;([^<]*)</p>")


def cartes_de_la_page(html_page: str) -> list[dict]:
    """Un lot du catalogue -> un dict de champs bruts lus. Fonction pure."""
    cartes = []
    for bloc in html_page.split(_CARTE_LOT)[1:]:
        url = _RDFA_URL.search(bloc)
        if not url:
            continue
        chemin = url.group(1).strip().replace(BASE, "")
        marque = _RDFA_MARQUE.search(bloc)
        numero = _NUMERO_LOT.search(bloc)
        titre = _TITRE_LIEN.search(bloc) or _RDFA_NOM.search(bloc)
        vendu = _VENDU.search(bloc)
        estimations = _ESTIMATION.findall(bloc)
        champs = {c.strip().rstrip("."): _un_espace(_html.unescape(v))
                  for c, v in _CHAMP.findall(bloc)}
        grade = _GRADE.search(bloc)
        cartes.append({
            "chemin": chemin,
            "lot": numero.group(1) if numero else None,
            "titre": _un_espace(_html.unescape(titre.group(1))) if titre else None,
            "description": _un_espace(_html.unescape(
                _RDFA_DESC.search(bloc).group(1))) if _RDFA_DESC.search(bloc) else None,
            "marque_rdfa": _un_espace(_html.unescape(marque.group(1))) if marque else None,
            "devise": _RDFA_DEVISE.search(bloc).group(1) if _RDFA_DEVISE.search(bloc) else None,
            # C'est l'ESTIMATION BASSE, jamais un prix realise.
            "estimation_rdfa": _RDFA_PRIX.search(bloc).group(1) if _RDFA_PRIX.search(bloc) else None,
            "sku": _RDFA_SKU.search(bloc).group(1) if _RDFA_SKU.search(bloc) else None,
            "estimation": _un_espace(estimations[0]) if estimations else None,
            "vendu_frais_inclus": (_nombre(vendu.group(2)), vendu.group(1)) if vendu else None,
            "champs": champs,
            "grade": _un_espace(grade.group(1)) if grade else None,
        })
    return cartes


# ---------------------------------------------------------------------------
# normalisation
# ---------------------------------------------------------------------------
# Les matieres telles qu'Antiquorum les ecrit en fin de titre.
_MATIERES = (
    ("stainless steel", "stainless steel"), ("pink gold", "pink gold"),
    ("rose gold", "pink gold"), ("yellow gold", "yellow gold"),
    ("white gold", "white gold"), ("platinum", "platinum"),
    ("titanium", "titanium"), ("ceramic", "ceramic"),
    ("silver", "silver"), ("bronze", "bronze"), ("brass", "brass"),
    ("gilt metal", "gilt metal"), ("gold", "gold"), ("steel", "steel"),
)
_COULEURS = ("black", "white", "silvered", "silver", "blue", "grey", "gray",
             "green", "brown", "champagne", "salmon", "cream", "ivory",
             "tropical", "gilt", "gold", "copper", "red", "pink", "yellow")
_ANNEE = re.compile(r"\b(1[5-9]\d{2}|20[0-4]\d)\b")
_DIAL = re.compile(r"\b(" + "|".join(_COULEURS) + r")(?:\s+\w+){0,2}?\s+dial\b", re.I)


# La matiere se lit en FIN de titre chez Antiquorum ('..., STAINLESS STEEL').
# Deux garde-fous, tous deux mesures necessaires le 21/09/2026 :
#   les bornes de mot — sans elles, 'Manufactures of Jewelry, SILVERWARE and
#   Gas Fixtures' rangeait une montre en or 18K sous 'silver' ;
#   la DERNIERE occurrence — un titre cite parfois une matiere de bracelet
#   avant celle du boitier.
_MOTIF_MATIERE = re.compile(
    r"\b(" + "|".join(sorted({m for m, _ in _MATIERES}, key=len, reverse=True)) + r")\b",
    re.I)
_MATIERE_PROPRE = dict(_MATIERES)


def _matiere(titre) -> str | None:
    trouvees = _MOTIF_MATIERE.findall(str(titre or "").lower())
    return _MATIERE_PROPRE.get(trouvees[-1]) if trouvees else None


def _couleur_cadran(texte) -> str | None:
    trouve = _DIAL.search(str(texte or ""))
    return trouve.group(1).lower() if trouve else None


def _annee(valeur) -> int | None:
    trouve = _ANNEE.search(str(valeur or ""))
    return int(trouve.group(1)) if trouve else None


def _estimations(texte) -> tuple[float | None, float | None]:
    """'EUR 1,200 - 2,200' -> (1200.0, 2200.0)."""
    nombres = re.findall(r"[\d][\d,.']*", str(texte or ""))
    valeurs = [v for v in (_nombre(n) for n in nombres) if v]
    if not valeurs:
        return None, None
    return valeurs[0], (valeurs[1] if len(valeurs) > 1 else None)


def fiche(carte: dict, prix: dict | None, vente: dict) -> dict | None:
    """Un lot du catalogue + sa ligne de price-list -> un enregistrement.

    `prix` vient de la price-list : c'est le MARTEAU. S'il manque (vente sans
    price-list publiee), on se rabat sur le `Sold:` du catalogue, qui est frais
    inclus — et `price_includes_premium` le dit.

    Isolee de la collecte pour que moteur/rejoue.py refasse la normalisation sur
    le brut deja stocke.
    """
    titre = carte.get("titre")
    devise = carte.get("devise")
    champs = carte.get("champs") or {}

    if prix and prix.get("marteau"):
        montant, frais_inclus = prix["marteau"], False
    elif carte.get("vendu_frais_inclus") and carte["vendu_frais_inclus"][0]:
        montant, frais_inclus = carte["vendu_frais_inclus"][0], True
        devise = devise or carte["vendu_frais_inclus"][1]
    else:
        return None  # lot invendu ou sans prix publie : rien a enregistrer
    if not devise:
        # Un montant sans devise n'est pas exploitable : mieux vaut le perdre
        # que le ranger sous une devise devinee a la ville.
        return None

    numero = carte.get("lot") or (prix or {}).get("lot")
    try:
        numero_int = int(re.sub(r"\D", "", numero or "") or 0) or None
    except ValueError:
        numero_int = None

    # La reference : champ dedie quand la vente en publie un (ventes modernes),
    # sinon lue dans le titre, ou Antiquorum ecrit 'REF. 6264' en clair.
    reference = champs.get("Reference") or None
    provenance_ref = "champ_dedie" if reference else None
    if not reference:
        reference = reference_dans(titre)
        provenance_ref = "extrait_titre" if reference else None
    if not reference:
        reference = reference_dans(carte.get("description"))
        provenance_ref = "extrait_description" if reference else None

    # La marque : le champ dedie d'abord, le RDFa ensuite. 'Unsigned' est la
    # reponse honnete du catalogue sur une montre de poche du XVIIIe : on la
    # garde telle quelle et on laisse R3 trancher.
    marque = (champs.get("Brand") or "").split(",")[0].strip() or None
    marque = marque or carte.get("marque_rdfa")
    if not marque or marque.lower().startswith("unsigned"):
        devine = filtre().verdict(titre or "", "AUCTION").get("brand")
        marque = devine or marque

    bas, haut = _estimations(carte.get("estimation"))
    if bas is None and carte.get("estimation_rdfa"):
        # `schema:price` vaut '0' sur les lots sans estimation publiee : zero
        # n'est pas une estimation basse, c'est une absence.
        bas = _nombre(carte["estimation_rdfa"]) or None

    return price_point(
        source_id=SOURCE["id"], source_type=SOURCE["type"],
        source_url=f"{BASE}{carte['chemin']}",
        external_id=carte.get("sku") or f"{vente.get('pricelist') or vente.get('catalogue')}-{numero}",
        price_nature="realised",
        # La source etiquette elle-meme la colonne `hammer` et ecrit `Sold: EUR X`
        # sur la fiche : la nature est publiee, pas deduite.
        price_nature_provenance="champ_dedie",
        listing_status="sold",
        price_includes_premium=frais_inclus,
        price_amount=montant,
        price_currency=devise,
        # La date de la VACATION qui contient ce lot, pas celle de la vente.
        price_date=_date_du_lot(vente.get("vacations"), numero_int) or vente.get("date"),
        estimate_low=bas, estimate_high=haut,
        brand=marque,
        model=champs.get("Model"),
        reference=reference,
        reference_provenance=provenance_ref,
        # Antiquorum ne publie aucune categorie par lot : le titre de la vente
        # n'en est pas une ('A collection of Watch Holders' contient le mot
        # watch sans contenir une seule montre). On laisse le champ vide et
        # c'est `corpus_horloger` qui porte l'information.
        source_category=None,
        year=_annee(champs.get("Year")) or _annee(titre),
        case_material=_matiere(titre),
        case_size_mm=champs.get("Diameter"),
        movement=champs.get("Caliber"),
        dial_color=_couleur_cadran(carte.get("description")) or _couleur_cadran(titre),
        condition=carte.get("grade"),
        title=titre,
        seller=f"Antiquorum {vente.get('lieu')}" if vente.get("lieu") else "Antiquorum",
    )


# ---------------------------------------------------------------------------
# relecture du brut — pour moteur/rejoue.py, sans une seule requete
# ---------------------------------------------------------------------------
def lots_du_brut(entrees: list) -> list[tuple]:
    """(carte, prix, vente) pour chaque lot d'une collecte deja stockee.

    La jointure est refaite ici : le brut porte les trois routes, et c'est
    l'URL du lot qui les relie.
    """
    ventes_par_pl, ventes_par_cat = {}, {}
    marteaux, cartes = {}, []

    for entree in entrees:
        url, page = entree.get("url", ""), entree.get("payload") or ""
        if "/auctions?" in url or re.search(r"/auctions$", url.split("?")[0]):
            annee = re.search(r"year=(\d{4})", url)
            for vente in ventes_de_la_page(page, int(annee.group(1)) if annee else None):
                if vente["pricelist"]:
                    ventes_par_pl[vente["pricelist"]] = vente
                if vente["catalogue"]:
                    ventes_par_cat[vente["catalogue"]] = vente
        elif "/price-list" in url:
            identifiant = _PRICELIST.search(url)
            entete = entete_price_list(page)
            for chemin, prix in marteaux_de_la_page(page).items():
                prix["pricelist"] = identifiant.group(1) if identifiant else None
                prix["entete"] = entete
                marteaux[chemin] = prix
        elif "/lots" in url:
            slug = _CATALOGUE.search(url)
            for carte in cartes_de_la_page(page):
                carte["catalogue"] = slug.group(1) if slug else None
                cartes.append(carte)

    trouves = []
    for carte in cartes:
        prix = marteaux.get(carte["chemin"])
        vente = ventes_par_cat.get(carte.get("catalogue"))
        if vente is None and prix:
            vente = ventes_par_pl.get(prix.get("pricelist"))
        if vente is None:
            entete = (prix or {}).get("entete") or {}
            vente = {"titre": entete.get("titre"), "lieu": None,
                     "vacations": [(None, None, entete.get("date"))]
                     if entete.get("date") else [],
                     "pricelist": (prix or {}).get("pricelist"),
                     "catalogue": carte.get("catalogue")}
        trouves.append((carte, prix, vente))
    return trouves


# ---------------------------------------------------------------------------
# collecte
# ---------------------------------------------------------------------------
def _page(url, raw, journal, etiquette, params=None):
    """Une requete polie, tracee dans le brut. Rend le texte, ou None."""
    try:
        resp = get(url, params=params, pause=PAUSE)
    except Exception as exc:                                   # noqa: BLE001
        journal.append(f"{etiquette}: {type(exc).__name__}")
        return None
    raw.append({"url": resp.url, "status": resp.status_code, "payload": resp.text})
    if resp.status_code != 200:
        journal.append(f"{etiquette}: HTTP {resp.status_code}")
        return None
    return resp.text


def collect(cap: int = 20000, annees=None):
    """Les ventes des annees demandees, de la plus recente a la plus ancienne.

    `annees` sert aux essais (une annee precise) ; par defaut on remonte de
    l'annee courante a 1989.
    """
    raw: list[dict] = []
    journal: list[str] = []
    records: list[dict] = []
    if annees is None:
        annees = range(dt.date.today().year, ANNEE_MIN - 1, -1)

    ventes_vues = 0
    sans_price_list = 0
    controles: list[float] = []

    for annee in annees:
        if len(records) >= cap:
            break
        page = _page(f"{BASE}/auctions", raw, journal, f"ventes {annee}",
                     params={"locale": "en", "year": annee})
        if page is None:
            continue
        ventes = ventes_de_la_page(page, annee)
        journal.append(f"{annee}: {len(ventes)} ventes annoncees, "
                       f"{sum(1 for v in ventes if v['pricelist'])} avec price-list")

        for vente in ventes:
            if len(records) >= cap:
                break
            if not vente["catalogue"]:
                journal.append(f"vente '{vente['titre'][:40]}' {annee}: pas de catalogue, ignoree")
                continue
            # Une vente sans price-list NI total annonce n'a pas de resultats
            # publies : soit elle est a venir, soit la maison ne les a jamais
            # mis en ligne (3 ventes sur 11 en 2001, 1 sur 5 en 1989). Son
            # catalogue existe, sans aucun prix. Sans ce garde-fou, la collecte
            # depensait une dizaine de requetes par vente muette pour rien.
            if not vente["pricelist"] and not vente["total"]:
                journal.append(f"vente '{vente['titre'][:40]}' {annee}: ni price-list ni "
                               f"total annonce — aucun resultat publie, ignoree")
                continue
            ventes_vues += 1

            # 1. le marteau, en une requete pour toute la vente
            marteaux = {}
            if vente["pricelist"]:
                page_prix = _page(f"{BASE}/en/auctions/{vente['pricelist']}/price-list",
                                  raw, journal, f"price-list {vente['pricelist']}")
                if page_prix:
                    marteaux = marteaux_de_la_page(page_prix)
                    entete = entete_price_list(page_prix)
                    if not vente["vacations"] and entete.get("date"):
                        vente["vacations"] = [(None, None, entete["date"])]
                    journal.append(f"price-list {vente['pricelist']} "
                                   f"({vente['lieu']}, {vente['titre'][:40]}): "
                                   f"{len(marteaux)} lots vendus")
            else:
                sans_price_list += 1
                journal.append(f"vente '{vente['titre'][:40]}' {annee}: pas de price-list "
                               f"— on se rabat sur le prix FRAIS INCLUS du catalogue")

            # 2. l'identite, 20 lots par page, jusqu'a la premiere page vide
            numero_page, lots_vus = 1, 0
            while numero_page <= PAGES_MAX and len(records) < cap:
                page_lots = _page(f"{BASE}/en/auctions/{vente['catalogue']}/lots",
                                  raw, journal,
                                  f"catalogue {vente['catalogue']} p{numero_page}",
                                  params={"page": numero_page})
                if page_lots is None:
                    break
                cartes = cartes_de_la_page(page_lots)
                if not cartes:
                    break
                lots_vus += len(cartes)
                for carte in cartes:
                    carte["catalogue"] = vente["catalogue"]
                    prix = marteaux.get(carte["chemin"])
                    # Le controle qui prouve que la colonne 1 est bien le
                    # marteau : le `Sold:` du catalogue doit valoir la colonne 2.
                    if prix and carte.get("vendu_frais_inclus") and prix["frais_inclus"]:
                        controles.append(carte["vendu_frais_inclus"][0] / prix["marteau"])
                    enregistrement = fiche(carte, prix, vente)
                    if enregistrement is not None:
                        records.append(enregistrement)
                        if len(records) >= cap:
                            break
                # Second garde-fou : une premiere page sans le moindre prix
                # realise signifie que la vente n'a pas de resultats publies.
                if (numero_page == 1 and not marteaux
                        and not any(c.get("vendu_frais_inclus") for c in cartes)):
                    journal.append(f"catalogue {vente['catalogue']}: aucun prix realise "
                                   f"sur la premiere page — vente abandonnee")
                    break
                if len(cartes) < LOTS_PAR_PAGE:
                    break
                numero_page += 1
            journal.append(f"catalogue {vente['catalogue']}: {lots_vus} lots lus "
                           f"en {numero_page} page(s), {len(records)} records cumules")

    if controles:
        controles.sort()
        milieu = controles[len(controles) // 2]
        journal.append(
            f"controle frais: le 'Sold' du catalogue vaut {milieu:.3f} fois la colonne 1 "
            f"de la price-list (n={len(controles)}, {min(controles):.3f}-{max(controles):.3f}) "
            f"— la colonne 1 est donc le MARTEAU, et le prix charge est hors frais")
    journal.append(f"{ventes_vues} ventes traitees, {sans_price_list} sans price-list "
                   f"(prix frais inclus), {len(records)} records")
    if len(records) >= cap:
        journal.append(f"TRONQUE: plafond de {cap} atteint — il reste des donnees a prendre")
    return raw, records[:cap], journal
