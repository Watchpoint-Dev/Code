"""Cottone Auctions (Geneseo, NY) — prix realises DATES, frais acheteur inclus.

Maison generaliste americaine : peinture, mobilier, argenterie, horloges de
parquet. Les montres y sont un rayon parmi douze. Tout l'enjeu est donc de la
prendre par le bon bout, et la reconnaissance du 21/09/2026 a trouve trois
choses qui ne se devinent pas.

1. LA DATE EST DANS UN COMMENTAIRE HTML. Les pages `/prices-realized/...`
   affichent la vignette, le titre et le montant adjuge. Le nom de la vente et
   sa DATE sont bien envoyes par le serveur, mais commentes :

       <!--<a href="/auction/177/important-timepieces...">...</a><br />-->
       <!--<br /><strong>Mar 31, 2023</strong>-->

   Un navigateur ne les montre pas ; nous, nous les lisons. C'est ce qui fait
   de cette source une source DATEE sans une seule requete de plus : 50 lots
   dates par page. Verification croisee sur 4 lots pris en 2009, 2014, 2016 et
   2022 : la date du commentaire est, au jour pres, l'`Auction Date` publiee
   sur la fiche du lot. Ce n'est pas une date de mise en ligne.

2. LE PRIX EST FRAIS INCLUS, ET LA MAISON LE DIT. La fiche de lot titre son
   montant `Hammer Price w/ BP` — marteau AVEC buyer's premium. Mesure sur 5
   fiches allant de 2009 a 2025 : le libelle ne change jamais.
   `price_includes_premium=True` n'est donc pas une deduction arithmetique,
   c'est une lecture. Et c'est heureux : le taux de frais des maisons
   americaines n'est pas constant a l'interieur d'une meme vente (×1,25 sur un
   lot, ×1,30 sur un autre, mesure chez New Orleans), de sorte que le marteau
   nu n'est PAS reconstituable par division. On ne le tente pas.

3. LA CATEGORIE DE LA SOURCE, ICI, NE SERT PAS LE FILTRE — ELLE LE SABOTE.
   Cottone classe par MATIERE, pas par fonction : toutes ses montres-bracelets
   sont rangees sous `Jewelry`, avec les bagues et les colliers. Or `Jewelry`
   n'est ni un libelle horloger ni un libelle muet : la regle R0 le lit comme
   « ce n'est pas une montre » et rejette le lot avant tout examen du titre.
   Mesure sur 334 lots de cette categorie :

       sans categorie_source : 27 GARDER, 307 REJETER
       avec categorie_source :  0 GARDER, 334 REJETER

   Les 27 sont des Rolex Day-Date, Omega, Patek, Vacheron, Heuer Seafarer. On
   ne passe donc PAS `categorie_source` au filtre pour cette source — le titre
   decide. Le libelle est tout de meme enregistre dans `source_category`, ou il
   reste utile en aval : c'est lui qui permet d'ecarter les montres de poche.

CE QUE CETTE SOURCE DONNE MAL : la reference. Mesure sur les 45 lots gardes
d'un echantillon de 412 : 4 references seulement, soit 9 %. Les titres sont
descriptifs (« 18K Gold Omega Automatic Watch »), pas catalographiques. La
fiche de lot en porte parfois une en clair (« Reference no. 18038 »), mais elle
coute une requete par lot et le rendement est mince : sur 8 fiches ouvertes,
UNE reference gagnee. Ce qu'elle rapporte vraiment, c'est le diametre (5 fois
sur 8) et l'etat. `collect(fiches=N)` le fait donc sur demande, jamais par
defaut.

RENDEMENT MESURE, categorie par categorie — c'est ce qui commande l'ordre de
passage ci-dessous :

    pocket-watches       128 lots ->  22 gardes (17 %)   3 pages
    jewelry            1 584 lots -> 150 gardes (~9 %)  32 pages   [extrapole]
    clocks-timepieces ~3 350 lots ->  40 gardes (1,2 %) 67 pages   [mesure 08/2026]

Soit environ 210 prix realises dates pour une centaine de requetes. La derniere
categorie est de l'horlogerie d'ameublement — regulateurs, orreries, horloges
de parquet — et elle passe en dernier pour cette raison : un plafond atteint
avant elle ne perd presque rien.

Reconnaissance et mise en service le 21/09/2026.
"""
from __future__ import annotations

import datetime as _dt
import html as _html
import re

from watchpoint.filtrage.filtre import filtre
from watchpoint.schema import parse_money, price_point, reference_dans, reference_libre
from watchpoint.commun.utils import get

SOURCE = {
    "id": "cottone",
    "name": "Cottone Auctions",
    "type": "auction",
    "price_nature": "realised",
    "access": "pages /prices-realized/category/<slug>, 50 lots par page ; "
              "la date de vente est servie par le serveur dans un commentaire HTML",
    "robots": "OK — 'User-agent: * / Disallow:' lu le 21/09/2026 : aucune "
              "restriction, aucun Crawl-delay",
    "reserve": "prix FRAIS INCLUS (la fiche de lot titre 'Hammer Price w/ BP') ; "
               "le marteau nu n'est pas publie et n'est pas reconstituable",
}

BASE = "https://www.cottoneauctions.com"
# Aucun Crawl-delay au robots.txt. On prend quand meme une seconde et demie :
# c'est un site de maison de ventes, pas une plateforme.
DELAI = 1.5
PAR_PAGE = 50   # fixe : `num_per_page` est ignore sur les vues prices-realized

# (slug, libelle publie par la source). Ordre = rendement mesure decroissant.
CATEGORIES = (
    ("pocket-watches", "Pocket Watches"),
    ("jewelry", "Jewelry"),
    ("clocks-timepieces", "Clocks & Timepieces"),
)

_BLOC = re.compile(r'class="[^"]*\bpr_item\b[^"]*">(.*?)<p class="est_price_grid">(.*?)</p>',
                   re.S)
# Le titre COMPLET vit dans l'attribut alt de la vignette. Le texte du lien,
# lui, est tronque par le gabarit a une cinquantaine de signes et finit en
# « ... » : s'en servir couperait la reference quand elle est en fin de titre.
_LOT = re.compile(r'<a href="(/lots/(\d+)/[^"]*)"><img[^>]*alt="([^"]*)"')
_DATE = re.compile(r'<!--\s*<br />\s*<strong>\s*([A-Z][a-z]+\.?\s+\d{1,2},\s*\d{4})\s*</strong>\s*-->')
_DERNIERE_PAGE = re.compile(r'class="last"><a href="[^"]*[?&]page=(\d+)')
# Une fourchette d'estimation, pas un prix adjuge : '$300-$500', '$75 - $125'.
_FOURCHETTE = re.compile(r'\d\s*(?:-|–|to)\s*\$?\s*\d')

# Fiche de lot (enrichissement optionnel).
_LABEL_PRIX = re.compile(r'class="sold_realized">\s*(.*?)\s*</h2>', re.S)
_DESCRIPTION = re.compile(r'<div class="lot-item-info">(.*?)</table>', re.S)
_CONDITION = re.compile(r'<u>Condition</u>\s*<br />\s*(.*?)\s*</td>', re.S)
_DIAMETRE = re.compile(r'(\d{2}(?:\.\d)?)\s*mm\b', re.I)
_BALISES = re.compile(r"<[^>]+>")

# Une annee d'epoque dans le titre : « Chronograph Wristwatch, 1948 ». On ne la
# retient que si le titre n'en porte QU'UNE : « Raingo (1775 - 1847) » sont des
# dates de biographie, pas l'annee d'un objet, et il y en a deux.
_ANNEE = re.compile(r"(?<!\d)(1[89]\d{2}|20[0-2]\d)(?!\d)")


def _texte(brut) -> str:
    return re.sub(r"\s+", " ", _html.unescape(_BALISES.sub(" ", str(brut or "")))).strip()


def _date_iso(ecrit: str | None) -> str | None:
    """'Mar 31, 2023' / 'Sep 26, 2009' / 'May 06, 2022' -> '2023-03-31'."""
    if not ecrit:
        return None
    ecrit = re.sub(r"\s+", " ", ecrit.replace(".", "")).strip()
    for forme in ("%b %d, %Y", "%B %d, %Y"):
        try:
            return _dt.datetime.strptime(ecrit, forme).date().isoformat()
        except ValueError:
            continue
    return None


def _annee(titre: str | None) -> int | None:
    trouves = set(_ANNEE.findall(titre or ""))
    return int(trouves.pop()) if len(trouves) == 1 else None


def _reference(texte):
    """(valeur, provenance) — le mot-cle d'abord, la forme ensuite."""
    valeur = reference_dans(texte)
    if valeur:
        return valeur, "extrait_titre"
    valeur = reference_libre(texte)
    return (valeur, "jeton_titre") if valeur else (None, None)


def fiche(bloc: str, prix_brut: str, categorie: str) -> dict | None:
    """Un bloc `pr_item` d'une page prices-realized -> un enregistrement.

    Rend None quand le bloc ne porte pas de prix ADJUGE : la vue prices-realized
    laisse passer quelques lots restes sur une fourchette d'estimation ou un
    « No Estimate ». Un lot sans montant conclu ne dit rien d'une transaction.
    """
    lot = _LOT.search(bloc)
    if not lot:
        return None
    prix_texte = _texte(prix_brut)
    if not prix_texte or _FOURCHETTE.search(prix_texte):
        return None
    montant, devise = parse_money(prix_texte)
    if not montant:
        return None

    titre = _html.unescape(lot.group(3)).strip()
    # On ne passe PAS `categorie_source` : voir l'en-tete du module, la regle R0
    # lit 'Jewelry' comme « pas une montre » et rejetterait toutes les
    # montres-bracelets de la maison.
    tranche = filtre().verdict(titre, "AUCTION")
    reference, provenance_ref = _reference(titre)
    date = _DATE.search(bloc)
    return price_point(
        source_id=SOURCE["id"], source_type=SOURCE["type"],
        source_url=BASE + lot.group(1),
        external_id=lot.group(2),
        price_nature="realised",
        # La nature vient du STATUT : le lot figure dans la section « Prices
        # Realized » avec un montant unique, non une fourchette. La fiche de lot
        # la publie en toutes lettres ('Hammer Price w/ BP') — `collect(fiches=N)`
        # remonte alors la provenance a `champ_dedie`.
        price_nature_provenance="deduite_statut",
        # FRAIS ACHETEUR INCLUS. Lu sur la fiche, pas deduit : 'Hammer Price
        # w/ BP', libelle identique de 2009 a 2025 sur les 8 fiches controlees.
        price_includes_premium=True,
        listing_status="sold",
        price_amount=montant,
        price_currency=devise or "USD",
        # La vraie date de transaction, lue dans le commentaire du gabarit.
        price_date=_date_iso(date.group(1) if date else None),
        # La maison ne publie aucun champ de marque : elle vit en tete de titre.
        # On la lit avec le dictionnaire du filtre.
        brand=tranche.get("brand"),
        title=titre,
        reference=reference, reference_provenance=provenance_ref,
        # Le libelle de la source. Inutilisable par R0 ici, mais precieux en
        # aval : c'est lui qui distingue une montre de poche d'un bracelet.
        source_category=categorie,
        year=_annee(titre),
        seller=SOURCE["name"],
        filter_verdict=tranche.get("verdict"),
        filter_rule=tranche.get("rule"),
        filter_version=tranche.get("filter_version"),
    )


def lots_du_brut(entrees: list) -> list[tuple]:
    """(bloc, prix, categorie) pour chaque lot d'une collecte deja stockee.

    Le brut est conserve entier : une correction du filtre se rejoue dessus sans
    une seule requete reseau.
    """
    trouves = []
    for entree in entrees:
        if entree.get("genre") != "liste":
            continue
        categorie = entree.get("categorie")
        for bloc in _BLOC.finditer(entree.get("payload") or ""):
            trouves.append((bloc.group(1), bloc.group(2), categorie))
    return trouves


def _enrichir(enregistrement: dict, page: str) -> list[str]:
    """La fiche de lot : reference en clair, diametre, etat, nature publiee."""
    notes = []
    label = _LABEL_PRIX.search(page)
    if label and "BP" in label.group(1):
        # La maison publie la nature : on remonte la provenance.
        enregistrement["price_nature_provenance"] = "champ_dedie"
        enregistrement["price_includes_premium"] = True
        notes.append(f"label={_texte(label.group(1))}")
    corps = _DESCRIPTION.search(page)
    texte = _texte(corps.group(1)) if corps else ""
    if not enregistrement.get("reference"):
        # SEULEMENT l'extracteur a mot-cle. `reference_libre` reconnait un jeton
        # a sa FORME et retient le dernier du texte : sur un titre de trois mots
        # c'est fiable, sur une description de catalogue c'est une catastrophe.
        # Mesure du 21/09/2026, premier essai de cet enrichissement : les deux
        # « references » gagnees sur trois fiches etaient '22.8' et '118.6' —
        # un poids d'or et un diametre de boitier de montre de poche. Le
        # mot-cle ('Reference no. 18038') est la seule voie sure ici.
        valeur = reference_dans(texte)
        if valeur:
            enregistrement["reference"] = valeur
            enregistrement["reference_provenance"] = "extrait_description"
            notes.append(f"ref={valeur}")
    diametre = _DIAMETRE.search(texte)
    if diametre:
        enregistrement["case_size_mm"] = float(diametre.group(1))
    etat = _CONDITION.search(page)
    if etat:
        enregistrement["condition"] = _texte(etat.group(1))[:200]
    return notes


def collect(cap: int = 6000, fiches: int = 0):
    """Les prix realises des categories horlogeres, dates.

    `fiches` : nombre de lots GARDES dont on ouvre en plus la fiche, pour la
    reference en clair, le diametre et l'etat. Coute une requete par lot, donc
    zero par defaut : mesure du 21/09/2026 sur 8 fiches — une seule reference
    gagnee, cinq diametres, et le libelle 'Hammer Price w/ BP' confirme 8 fois
    sur 8.
    """
    raw: list[dict] = []
    journal: list[str] = []
    records: list[dict] = []
    vus: set[str] = set()
    sans_prix = 0

    for slug, libelle in CATEGORIES:
        if len(records) >= cap:
            journal.append(f"{slug} : non visitee, plafond deja atteint")
            continue
        avant, page, total_pages = len(records), 1, None
        lots_vus, pages_lues = 0, 0
        while len(records) < cap:
            url = f"{BASE}/prices-realized/category/{slug}"
            try:
                resp = get(url, params={"page": page} if page > 1 else None,
                           pause=DELAI)
            except Exception as exc:
                journal.append(f"{slug} p{page}: {type(exc).__name__} — arret de la categorie")
                break
            pages_lues += 1
            raw.append({"genre": "liste", "categorie": libelle, "url": resp.url,
                        "status": resp.status_code, "payload": resp.text})
            if resp.status_code != 200:
                journal.append(f"{slug} p{page}: HTTP {resp.status_code} — arret de la categorie")
                break
            if total_pages is None:
                derniere = _DERNIERE_PAGE.search(resp.text)
                total_pages = int(derniere.group(1)) if derniere else 1

            blocs = list(_BLOC.finditer(resp.text))
            if not blocs:
                break
            for bloc in blocs:
                lots_vus += 1
                enregistrement = fiche(bloc.group(1), bloc.group(2), libelle)
                if enregistrement is None:
                    sans_prix += 1
                    continue
                if enregistrement["external_id"] in vus:
                    continue
                vus.add(enregistrement["external_id"])
                # Le filtre a tranche dans `fiche` ; seuls les lots retenus
                # deviennent des prix. Le verdict reste inscrit dans la ligne.
                if enregistrement["filter_verdict"] == "REJETER":
                    continue
                records.append(enregistrement)
                if len(records) >= cap:
                    break
            if len(blocs) < PAR_PAGE or page >= total_pages:
                break
            page += 1
        journal.append(f"{libelle} : {lots_vus} lots lus en {pages_lues}/{total_pages or '?'} page(s), "
                       f"{len(records) - avant} montres gardees")

    if sans_prix:
        journal.append(f"{sans_prix} lots sans prix adjuge (fourchette d'estimation "
                       f"ou 'No Estimate') — ecartes, ils ne disent aucune transaction")

    # Enrichissement optionnel, une requete par lot.
    if fiches:
        cibles = [r for r in records if not r.get("reference")][:fiches]
        gagnees = 0
        for enregistrement in cibles:
            try:
                resp = get(enregistrement["source_url"], pause=DELAI)
            except Exception as exc:
                journal.append(f"fiche {enregistrement['external_id']}: {type(exc).__name__}")
                continue
            raw.append({"genre": "fiche", "categorie": None, "url": resp.url,
                        "status": resp.status_code, "payload": resp.text})
            if resp.status_code != 200:
                continue
            avant_ref = enregistrement.get("reference")
            _enrichir(enregistrement, resp.text)
            if enregistrement.get("reference") and not avant_ref:
                gagnees += 1
        journal.append(f"fiches ouvertes : {len(cibles)}, references gagnees : {gagnees}")

    dates = [r["price_date"] for r in records if r.get("price_date")]
    if dates:
        journal.append(f"profondeur datee : {min(dates)} -> {max(dates)} "
                       f"({len(dates)}/{len(records)} lignes datees)")
    journal.append("PRIX FRAIS INCLUS : la fiche de lot titre 'Hammer Price w/ BP', "
                   "libelle constant de 2009 a 2026. Le marteau nu n'est pas publie, "
                   "et le taux de frais americain n'etant pas constant, il n'est pas "
                   "reconstituable par division.")
    journal.append("categorie_source NON transmise au filtre : Cottone range ses "
                   "montres-bracelets sous 'Jewelry', que R0 lit comme 'pas une "
                   "montre' (mesure : 27 montres gardees sans, 0 avec sur 334 lots)")
    if len(records) >= cap:
        journal.append(f"TRONQUE: plafond de {cap} atteint — il reste des donnees a prendre")
    return raw, records, journal
