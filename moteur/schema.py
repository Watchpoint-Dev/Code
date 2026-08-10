"""Modele normalise unique — tout ce qui est collecte passe par ici.

Principe (cf. notes/Plan2_28-07.md) : un prix n'a de sens qu'accompagne de sa
NATURE, sa DATE, sa DEVISE et sa SOURCE. Les 5 adaptateurs produisent tous des
enregistrements de cette forme, quelle que soit la tete de la source.
"""
from __future__ import annotations

import datetime as _dt
import re

# Les natures de prix du projet. Un enregistrement sans nature est invalide.
NATURES = {
    "realised",  # prix marteau, enchere conclue (maisons de ventes)
    "sold",      # vendu sur une marketplace
    "asking",    # prix demande (marchand, annonce en cours)
    "estimate",  # estimation avant vente
    "msrp",      # prix neuf catalogue
}

FIELDS = [
    # --- provenance
    "source_id", "source_type", "source_url", "external_id", "collected_at",
    # --- le prix
    "price_nature", "price_amount", "price_currency", "price_date",
    "estimate_low", "estimate_high",
    # --- identite de la montre
    "brand", "model", "reference", "title",
    # --- technique
    "year", "case_material", "case_size_mm", "movement", "dial_color", "condition",
    # --- contexte
    "seller",
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

    record = {field: kwargs.get(field) for field in FIELDS}

    # Normalisations transverses. Les sources renvoient ces champs tantot en
    # texte, tantot en {"id":2,"name":"Black"}, tantot en liste de dicts.
    for champ in ("brand", "model", "case_material", "movement", "dial_color", "condition"):
        record[champ] = _first_name(record[champ])

    for key in ("title", "model", "reference", "seller", "condition", "dial_color"):
        if isinstance(record[key], str):
            record[key] = record[key].strip() or None

    if isinstance(record["case_size_mm"], str):
        size = re.search(r"\d+(?:\.\d+)?", record["case_size_mm"])
        record["case_size_mm"] = float(size.group(0)) if size else None

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
