"""Modele normalise unique — tout ce qui est collecte passe par ici.

Principe (cf. _archive/2026-09/notes/Plan2_28-07.md) : un prix n'a de sens qu'accompagne de sa
NATURE, sa DATE, sa DEVISE et sa SOURCE. Les 5 adaptateurs produisent tous des
enregistrements de cette forme, quelle que soit la tete de la source.
"""
from __future__ import annotations

import datetime as _dt
import html as _html
import re

# Les natures de prix du projet. Un enregistrement sans nature est invalide.
NATURES = {
    "realised",  # prix marteau, enchere conclue (maisons de ventes)
    "sold",      # vendu sur une marketplace
    "asking",    # prix demande (marchand, annonce en cours)
    "estimate",  # estimation avant vente
    "msrp",      # prix neuf catalogue
}

# D'ou vient la nature du prix. La question n'est pas cosmetique : une nature
# declaree une fois pour toutes dans l'adaptateur ne sait pas distinguer un lot
# vendu d'un lot invendu, ni une montre en vitrine d'une montre partie.
PROVENANCES_NATURE = {
    "constante_source",   # l'adaptateur la declare pour toute la source
    "deduite_statut",     # lue sur l'annonce (disponibilite, prix marteau absent)
    "champ_dedie",        # la source publie explicitement la nature
    "declaree_tag",       # la boutique etiquette la fiche : 'sold-watches-archive'
                          # chez Bulang & Sons, 'inquiry-only' chez Montredo. Plus
                          # sur que la deduction par `available`, qui confondait
                          # 3 319 « nous consulter » avec autant de ventes.
}

# D'ou vient la reference. Meme raisonnement : une reference extraite d'un titre
# porte un taux d'erreur qu'un champ publie par la source n'a pas.
PROVENANCES_REFERENCE = {
    "champ_dedie",         # la source publie la reference constructeur
    "extrait_titre",       # devinee par expression reguliere dans le titre
    "extrait_description", # devinee dans le corps de l'annonce, moins sur
    "jeton_titre",         # reconnue a sa FORME dans le titre, sans mot-cle :
                           # 99 % de precision et 92 % de rappel, mesures contre
                           # les 4 086 references en champ dedie de Watchtrader
    "sku",                 # code interne du vendeur, souvent PAS la reference
}

FIELDS = [
    # --- provenance
    "source_id", "source_type", "source_url", "external_id", "collected_at",
    # --- le prix
    "price_nature", "price_amount", "price_currency", "price_date",
    "estimate_low", "estimate_high",
    # Comment la nature a ete obtenue. Une constante d'adaptateur et un statut
    # lu sur l'annonce ne se valent pas : Craft & Tailored declarait 1 000 prix
    # "demandes" alors que 92 % de ses fiches sont des ventes conclues.
    "price_nature_provenance",   # constante_source | deduite_statut | champ_dedie
    "listing_status",            # active | inactive | sold | withdrawn | unknown
    # Un prix d'enchere se publie de deux facons, et l'ecart est de 25 a 30 %.
    # Christie's affiche le prix FRAIS INCLUS : mesure du 25/08/2026 sur 4 001
    # lots, 97 % des montants se divisent par un taux de frais (1,26 dans 58 %
    # des cas) en donnant un marteau multiple de 50. Artcurial publie le marteau
    # nu dans adjudicationPrice. Comparer les deux sans le savoir surevalue
    # Christie's d'un quart. True/False pour une enchere, None ailleurs : chez
    # un marchand la question n'a pas de sens.
    "price_includes_premium",
    # --- identite de la montre
    "brand", "model", "reference", "title",
    # Une reference publiee par la source et une reference devinee dans le titre
    # n'ont pas le meme taux d'erreur. Un SKU est souvent un code interne.
    "reference_provenance",      # champ_dedie | extrait_titre | extrait_description | sku
    # La categorie telle que la source la nomme. Berry's publie 'Mens Watches'
    # ou 'Necklaces' : c'est une classification faite par le vendeur, infiniment
    # plus sure que ce qu'on devine d'un titre. Quand elle existe, elle dit a
    # elle seule si l'objet est une montre.
    "source_category",
    # --- technique
    "year", "case_material", "case_size_mm", "movement", "dial_color", "condition",
    # --- contexte
    "seller",
    # --- le filtre, appose a l'ingestion. On ne supprime rien : on marque.
    # Comme le brut est conserve, une correction du filtre se rejoue sur tout
    # l'historique sans une seule requete reseau.
    "filter_verdict",    # GARDER | REJETER | QUARANTAINE
    "filter_rule",       # la regle qui a tranche
    "filter_version",    # horodatage du filters.json utilise
]

# Symboles et codes rencontres dans les sources du batch 1.
_SYMBOLS = {"$": "USD", "£": "GBP", "€": "EUR", "¥": "JPY"}
_CODES = ("USD", "EUR", "GBP", "CHF", "HKD", "JPY", "AUD", "CAD", "SGD")


def parse_money(raw) -> tuple[float | None, str | None]:
    """'USD 189,000' -> (189000.0, 'USD') · '$3,495' -> (3495.0, 'USD')

    Gere aussi les nombres nus ('237727.00', 16400) et le separateur suisse
    ("5'000"). Retourne (None, None) si rien d'exploitable.
    """
    if raw is None or raw == "":
        return None, None
    if isinstance(raw, (int, float)):
        return float(raw), None

    text = str(raw).strip()
    currency = None

    for code in _CODES:
        if re.search(rf"\b{code}\b", text, re.I):
            currency = code
            break
    if currency is None:
        # 'Fr. 6250' / 'SFr.' : notation suisse du franc, frequente a Geneve
        if re.search(r"\bS?Fr\.?\b", text):
            currency = "CHF"
    if currency is None:
        for symbol, code in _SYMBOLS.items():
            if symbol in text:
                currency = code
                break

    # on isole le premier nombre, apostrophe suisse et espaces fines comprises
    match = re.search(r"\d[\d\s.,'  ]*", text)
    if not match:
        return None, currency

    number = re.sub(r"[\s'  ]", "", match.group(0)).rstrip(".,")
    # 189,000 -> milliers ; 237727.00 -> decimales ; 1.234,56 -> europeen
    if "," in number and "." in number:
        number = (number.replace(",", "") if number.rfind(".") > number.rfind(",")
                  else number.replace(".", "").replace(",", "."))
    # Un seul type de separateur : 3 chiffres apres le dernier => milliers.
    # '189,000' et '25.000' sont des milliers ; '237727.00' et '16,50' des decimales.
    elif "," in number:
        parts = number.split(",")
        number = (number.replace(",", "") if len(parts) > 2 or len(parts[-1]) == 3
                  else number.replace(",", "."))
    elif "." in number:
        parts = number.split(".")
        if len(parts) > 2 or len(parts[-1]) == 3:
            number = number.replace(".", "")

    try:
        return float(number), currency
    except ValueError:
        return None, currency


def parse_date(raw) -> str | None:
    """Ramene toute date de source a 'YYYY-MM-DD'. Accepte l'epoch Unix."""
    if raw is None or raw == "":
        return None
    if isinstance(raw, (int, float)) or (isinstance(raw, str) and raw.isdigit() and len(raw) >= 9):
        try:
            seconds = float(raw)
            if seconds > 1e11:  # millisecondes
                seconds /= 1000
            return _dt.datetime.fromtimestamp(seconds, _dt.timezone.utc).date().isoformat()
        except (ValueError, OSError, OverflowError):
            return None
    match = re.search(r"(\d{4})-(\d{2})-(\d{2})", str(raw))
    return match.group(0) if match else None


# Un titre de vente peut contenir des separateurs de ligne invisibles. Le cumul
# etant du JSONL, un seul de ces caracteres coupe une ligne en deux pour tout
# lecteur qui decoupe avec splitlines() — et la ligne devient du JSON invalide.
# Un exemplaire s'etait glisse dans la base, venu d'un titre Christie's.
_SEPARATEURS = re.compile(r"[\r\n  ]+")


def _une_seule_ligne(texte: str) -> str:
    return _SEPARATEURS.sub(" ", texte).strip()


# ---------------------------------------------------------------------------
# L'extraction de reference, en UN SEUL endroit.
#
# Elle etait dupliquee dans cinq adaptateurs, avec la meme faute dans chacun :
# le motif `\bref` matche l'interieur de "refined", "reflective", "referenced",
# et le motif `no\.?` l'interieur de "chronographe". Mesure du 28/08/2026 :
# 9 770 fausses references en base, dont 3 810 fois le mot "ined".
#
# Deux garde-fous, tous deux necessaires :
#   le mot-cle doit etre un MOT ENTIER, d'ou les regards autour
#   la valeur capturee doit contenir AU MOINS UN CHIFFRE — une reference
#   constructeur en porte toujours, un fragment de mot jamais
# ---------------------------------------------------------------------------
def _sans_entites(texte) -> str:
    """Decode les entites HTML avant toute extraction.

    Sans cela, l'apostrophe typographique `&#8217;` d'un titre WordPress devient
    le jeton '8217' et se retrouve enregistree comme reference constructeur sur
    des centaines de lignes. Mesure du 28/08/2026 chez Fortuna.
    """
    return _html.unescape(str(texte))


_MOT_CLE_REFERENCE = re.compile(
    r"(?<![A-Za-z])"
    r"(?:ref|réf|reference|référence|referenz|model|modell|mod)"
    r"\.?(?![A-Za-z])"
    r"\s*(?:n[o°]\.?|nr\.?|#|:)?\s*"
    r"([A-Z0-9][A-Z0-9./\-]{2,17})",
    re.I)


def reference_dans(texte) -> str | None:
    """La reference constructeur citee dans un texte, ou None.

    On ne rend une valeur que si elle porte un chiffre : c'est ce qui distingue
    une vraie reference d'un morceau de mot.
    """
    if not texte:
        return None
    texte = _sans_entites(texte)
    for trouve in _MOT_CLE_REFERENCE.finditer(str(texte)):
        valeur = trouve.group(1).rstrip(".,;:)")
        if len(valeur) >= 3 and re.search(r"\d", valeur):
            return valeur
    return None


# Beaucoup de sources n'ecrivent AUCUN mot-cle devant leur reference : Hodinkee
# titre 'Rolex Datejust 279173', Loupe This 'Patek Philippe Calatrava Pilot
# Travel Time 7234A'. L'extracteur a mot-cle ne voit rien, alors que la
# reference est la, en clair. Il faut donc un second mecanisme, plus risque, qui
# reconnait un JETON de reference a sa forme — et sa provenance distincte dit
# qu'il est moins sur.
# Jusqu'a 24 signes : une reference Omega en fait 19 (329.30.44.51.01.003).
_JETON = re.compile(r"(?<![\w./-])([A-Z0-9][A-Z0-9./-]{3,23})(?![\w-])", re.I)
# Ce qu'un jeton peut etre d'autre qu'une reference.
_PAS_UNE_REFERENCE = re.compile(
    r"^(1[89]\d{2}|20[0-3]\d)s?$"                 # une annee ou une decennie
    r"|^\d{1,2}([.,]\d)?\s*mm$"                    # un diametre
    r"|^\d{1,2}(k|ct|kt)$"                          # un titre d'or
    r"|^(750|925|585|375|900|999)$"                 # un poincon
    # Une cote d'etancheite. Mesure du 28/08/2026 : 247 lignes gardees rangeaient
    # '300m', '1000M' ou le '300T' des Doxa dans le champ reference — un tiers
    # des jetons de titre chez CW Sellors et Analog:Shift. Les cotes en T sont
    # enumerees une a une : '242T' et '3647T' sont, eux, de vraies references.
    r"|^\d{2,4}\s*(m|mm|ft|atm|bar)$"
    r"|^(100|120|150|200|250|300|500|600|750|1000|1200|1500|2000|3000|4000|6000)t$"
    r"|^(no|nr|lot|circa|ca|vers|cal|caliber|calibre)$", re.I)


def reference_libre(texte) -> str | None:
    """La reference ecrite sans mot-cle, reconnue a sa forme.

    Deux garde-fous : le jeton doit porter au moins deux chiffres, et ne pas
    etre une annee, un diametre, un titre d'or ou un poincon. On retient le
    DERNIER jeton du texte : une reference suit la marque et le modele, elle
    ne les precede pas.
    """
    if not texte:
        return None
    texte = _sans_entites(texte)
    retenu = None
    for trouve in _JETON.finditer(str(texte)):
        jeton = trouve.group(1).strip(".,;:-")
        if len(jeton) < 4 or len(re.findall(r"\d", jeton)) < 2:
            continue
        if _PAS_UNE_REFERENCE.match(jeton):
            continue
        retenu = jeton
    return retenu


def _first_name(value):
    """Bezel renvoie parfois [{'name': 'Steel'}] ou {'name': 'Automatic'}."""
    if isinstance(value, list):
        value = value[0] if value else None
    if isinstance(value, dict):
        return value.get("name") or value.get("slug")
    return value


def price_point(**kwargs) -> dict:
    """Construit un enregistrement normalise, valide et complet.

    Tous les champs de FIELDS sont presents (None si absent) : le fichier de
    sortie a donc des colonnes stables, directement chargeables en base.
    """
    nature = kwargs.get("price_nature")
    if nature not in NATURES:
        raise ValueError(f"price_nature invalide: {nature!r} (attendu: {sorted(NATURES)})")

    provenance = kwargs.get("price_nature_provenance")
    if provenance is not None and provenance not in PROVENANCES_NATURE:
        raise ValueError(f"price_nature_provenance invalide: {provenance!r} "
                         f"(attendu: {sorted(PROVENANCES_NATURE)})")
    provenance_ref = kwargs.get("reference_provenance")
    if provenance_ref is not None and provenance_ref not in PROVENANCES_REFERENCE:
        raise ValueError(f"reference_provenance invalide: {provenance_ref!r} "
                         f"(attendu: {sorted(PROVENANCES_REFERENCE)})")
    if kwargs.get("reference") and not provenance_ref:
        raise ValueError("une reference sans provenance n'est pas exploitable : "
                         "un champ dedie et un SKU n'ont pas le meme taux d'erreur")

    record = {field: kwargs.get(field) for field in FIELDS}

    # Normalisations transverses. Les sources renvoient ces champs tantot en
    # texte, tantot en {"id":2,"name":"Black"}, tantot en liste de dicts.
    for champ in ("brand", "model", "case_material", "movement", "dial_color", "condition"):
        record[champ] = _first_name(record[champ])

    # Les entites HTML etaient decodees pour EXTRAIRE la reference, mais pas
    # dans les champs qu'on enregistre : 4 370 titres de dix sources partaient
    # en base avec 'Cartier Tank 17002 &#8216;Jumbo&#8217;'. Mesure du
    # 29/08/2026. Une base qui sert de support de lecture ne peut pas publier
    # des entites brutes, et un titre mal decode fausse aussi les rapprochements.
    for key in ("title", "model", "reference", "seller", "condition", "dial_color",
                "brand", "case_material", "movement"):
        if isinstance(record[key], str):
            record[key] = _une_seule_ligne(_sans_entites(record[key])) or None

    # La marque est ramenee a sa graphie canonique. Les sources en ecrivent
    # jusqu'a neuf pour la meme maison, et deux graphies font deux modeles
    # distincts pour la meme montre — la cote se couperait en deux.
    if record["brand"]:
        from watchpoint.filtrage.filtre import filtre as _filtre
        record["brand"] = _filtre().marque_canonique(record["brand"])

    if isinstance(record["case_size_mm"], str):
        size = re.search(r"\d+(?:\.\d+)?", record["case_size_mm"])
        record["case_size_mm"] = float(size.group(0)) if size else None

    # Les montants doivent etre des nombres, pas des chaines. Lyon & Turnbull
    # publie ses estimations en texte ("3000.00") : sans cette conversion, la
    # ligne entre en base et fait exploser la premiere comparaison numerique.
    for champ in ("price_amount", "estimate_low", "estimate_high", "case_size_mm"):
        valeur = record[champ]
        if isinstance(valeur, str):
            nombre, _ = parse_money(valeur)
            record[champ] = nombre
        elif isinstance(valeur, (int, float)):
            record[champ] = float(valeur)

    record["price_date"] = parse_date(record["price_date"])
    return record


def completeness(records: list[dict], fields: list[str] | None = None) -> dict[str, int]:
    """% de remplissage par champ — le chiffre qui juge une source."""
    if not records:
        return {}
    fields = fields or FIELDS
    return {
        field: round(100 * sum(1 for r in records if r.get(field) not in (None, "", [], {}))
                     / len(records))
        for field in fields
    }
