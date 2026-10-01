"""Normalisation : du point de prix brut d'un adaptateur à la ligne standard de la base.

Les adaptateurs ramènent déjà chaque source au même format (schema.py). Ce
module ajoute ce qui ne peut se décider qu'en regardant TOUTES les sources à la
fois : une référence écrite de la même façon partout, une échelle d'état commune,
et le sens de la date de chaque source.

Il s'applique au CHARGEMENT, jamais à la collecte. Le brut et le journal jsonl
restent tels quels ; une règle corrigée ici se rejoue sur toute la base en
rechargeant. `VERSION` est écrite sur chaque ligne : on sait toujours quelle
règle a produit quoi.
"""
from __future__ import annotations

import re

# À incrémenter à chaque modification d'une règle : le chargeur réécrit alors
# les lignes produites par une version antérieure.
VERSION = "2026-10-01.1"


# ---------------------------------------------------------------- références
#
# Mesure du 01/10/2026 sur les 175 904 prix gardés porteurs d'une référence :
# 58 843 références distinctes avant, 52 982 après ; les références à au moins
# 20 prix (une courbe exploitable) passent de 658 à 738. Patek 5711/1A : 12 -> 88.

_PREFIXE = re.compile(r"^(REF\.?|REFERENCE|NO\.?|NR\.?|N°)\s*")
# Les suffixes de VARIANTE (cadran, bracelet) d'une même référence de modèle.
# Ils restent dans reference_raw ; la cote se calcule au niveau du modèle.
_SUFFIXES = {
    "Rolex": re.compile(r"-\d{4}$"),                  # 116610LN-0001
    "Patek Philippe": re.compile(r"-\d{3}$"),         # 5227G-010
    "Audemars Piguet": re.compile(r"\.OO\..*$"),      # 15400ST.OO.1220ST.01
}
# Ce qui n'est pas une référence : un anniversaire (« 50th »), un nombre trop
# court, un code produit à 8 chiffres et plus (souvent un SKU de marchand).
# L'ordinal est borné à 3 chiffres : « 15400ST » est une référence (ST = acier).
_PAS_UNE_REFERENCE = (
    re.compile(r"\d{1,3}(TH|ST|ND|RD)"),
    re.compile(r"\d{8,}"),
)


# Les notes de catalogue collées à la référence, chez Phillips surtout :
# « 1806; interior case back stamped 1803 », « 16520 inside case back stamped ».
_NOTE_CATALOGUE = re.compile(r"[,;]|\s(INSIDE|INTERIOR|CASE ?BACK|WITH|AND)\b")
# Au-delà, ce n'est plus une référence : SKU de marchand (« PLBRFA88778-PT-IDBR »)
# ou titre entier (« VINTAGE 1950S ALUMINIUM DESK JET PLANE »). Mesure du
# 01/10/2026 : 99,6 % des références font 20 caractères ou moins ; une seule
# dépassant 5 000 caractères avait fait échouer le premier chargement.
LONGUEUR_MAX_REFERENCE = 25


# Les provenances jugées sûres : c'est la définition du socle depuis août
# (rapports/vues.py, entonnoir.py). Un SKU de repli (`sku`) est un code interne
# du marchand : il reste dans reference_raw, mais ne sert pas de clé de courbe.
# Une boutique dont le SKU EST la référence la déclare en `champ_dedie`.
REFERENCE_SURE = frozenset({"champ_dedie", "extrait_titre", "extrait_description", "jeton_titre"})


def reference(marque: str | None, brute: str | None, provenance: str | None = None) -> str | None:
    """La référence normalisée, ou None si ce qu'on a n'en est pas une.

    `provenance` vide : on juge sur la seule forme (usage hors chargement).
    """
    if not brute or (provenance is not None and provenance not in REFERENCE_SURE):
        return None
    ref = str(brute).upper().strip()
    ref = _NOTE_CATALOGUE.split(ref, maxsplit=1)[0]
    ref = _PREFIXE.sub("", ref)
    ref = re.sub(r"\s+", "", ref)               # « 116710 LN » -> « 116710LN »
    suffixe = _SUFFIXES.get(marque or "")
    if suffixe:
        ref = suffixe.sub("", ref)
    if len(ref) < 3 or len(ref) > LONGUEUR_MAX_REFERENCE or not re.search(r"\d", ref):
        return None
    if any(motif.fullmatch(ref) for motif in _PAS_UNE_REFERENCE):
        return None
    return ref


# ---------------------------------------------------------------- marque
#
# Les adaptateurs canonisent la marque par le dictionnaire du filtre, mais
# rendent le texte de la source quand il n'y figure pas. Certaines sources
# remplissent ce champ avec leur liste de marques entière (1 771 caractères chez
# Wanna Buy A Watch) ou un nom de boutique. Une marque tient en une ligne courte.

LONGUEUR_MAX_MARQUE = 60


def marque(brute: str | None) -> str | None:
    if not brute:
        return None
    nom = " ".join(str(brute).split())
    return nom if len(nom) <= LONGUEUR_MAX_MARQUE else None


# ---------------------------------------------------------------- état
#
# 34 formulations distinctes relevées le 01/10/2026. L'échelle d'Antiquorum
# (AAA > AA > A > B) se range sur celle des marchands. « preowned » ne dit rien
# de l'état : c'est inconnu, pas « bon ».

_ETATS = {
    "neuf": ("new", "unworn", "new unworn", "new old stock", "brand new", "unworn condition"),
    "excellent": ("excellent", "aaa", "mint", "like new", "mint condition",
                  "excellent unpolished", "excellent (not polished)"),
    "tres_bon": ("aa", "very good"),
    "bon": ("a", "b", "good", "fair", "used", "good patina'd"),
}
_ETAT_PAR_LIBELLE = {libelle: niveau for niveau, libelles in _ETATS.items() for libelle in libelles}


def etat(brut: str | None) -> str:
    """L'état sur l'échelle commune : neuf, excellent, tres_bon, bon ou inconnu."""
    if not brut:
        return "inconnu"
    return _ETAT_PAR_LIBELLE.get(str(brut).strip().lower(), "inconnu")


# ---------------------------------------------------------------- sens de la date
#
# Mesuré source par source le 01/10/2026 (part des dates égales au jour du relevé).
# Une enchère est datée du jour de la vente ; un marchand Shopify ou WooCommerce
# de la mise en ligne de l'annonce ; quatre sources sans date propre, du relevé.

_DATE_RELEVE = {"montredo", "bulangandsons", "watchesdotcom", "bezel"}
_DATE_VENTE_HORS_ENCHERES = {"everywatch"}      # agrégateur de résultats d'enchères


def sens_de_la_date(source: dict) -> str:
    """Ce que signifie price_date pour cette source : vente, mise_en_ligne ou releve."""
    if source["id"] in _DATE_RELEVE:
        return "releve"
    if source["type"] == "auction" or source["id"] in _DATE_VENTE_HORS_ENCHERES:
        return "vente"
    return "mise_en_ligne"
