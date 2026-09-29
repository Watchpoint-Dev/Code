"""Verifie le moteur et la base — hors ligne, en une seconde.

    cd ~/Desktop/WP
    python -m watchpoint verifie

Sort en erreur (code 1) si quelque chose ne va pas. C'est LA commande du chantier
donnees : si elle est verte, on peut se fier aux chiffres.

Deux familles de controles :
  1. le PARSING — des cas connus pour avoir casse par le passe, figes ici pour
     qu'ils ne reviennent jamais (formats europeen, suisse, anglo-saxon, epoch).
  2. les INVARIANTS de la base — ce qui doit etre vrai de toute ligne stockee.

Aucune dependance externe, aucun reseau : elle doit pouvoir tourner dans le train.
"""
from __future__ import annotations

from watchpoint import config

import collections
import datetime as dt
import json
import sys

from watchpoint.schema import FIELDS, NATURES, parse_date, parse_money, price_point  # noqa: E402

BASE = config.DATA / "price_points.jsonl"

echecs: list[str] = []
avertissements: list[str] = []


def verifie(condition: bool, message: str, *, bloquant: bool = True) -> None:
    if condition:
        return
    (echecs if bloquant else avertissements).append(message)


# ---------------------------------------------------------------- 1. parsing

def controle_parsing() -> None:
    """Chaque cas ici a deja casse en vrai, ou pourrait casser demain."""
    cas_money = [
        # (entree,            montant attendu, devise attendue)
        ("USD 189,000",       189000.0, "USD"),   # anglo-saxon, milliers
        ("$3,495",            3495.0,   "USD"),
        ("237727.00",         237727.0, None),    # decimales nues (Shopify)
        ("16400",             16400.0,  None),
        ("€ 25.000",          25000.0,  "EUR"),   # europeen — a divise les prix par 1000
        ("1.234.567 EUR",     1234567.0, "EUR"),
        ("Fr. 6'250",         6250.0,   "CHF"),   # suisse — devise non detectee
        ("CHF 5'000",         5000.0,   "CHF"),
        ("16,50",             16.5,     None),    # virgule decimale
        ("16.50",             16.5,     None),
        ("HKD 1,020,000",     1020000.0, "HKD"),
        ("£1,200",            1200.0,   "GBP"),
        ("sur demande",       None,     None),
        ("",                  None,     None),
        (None,                None,     None),
    ]
    for entree, montant, devise in cas_money:
        obtenu = parse_money(entree)
        verifie(obtenu == (montant, devise),
                f"parse_money({entree!r}) = {obtenu}, attendu {(montant, devise)}")

    cas_date = [
        ("2024-05-30T00:00Z",            "2024-05-30"),
        ("2026-07-30T17:06:37-07:00",    "2026-07-30"),
        ("2022-05-26T17:09:27.000+00:00", "2022-05-26"),
        (1785076200,                     "2026-07-26"),   # epoch secondes
        (None,                           None),
        ("",                             None),
    ]
    for entree, attendu in cas_date:
        obtenu = parse_date(entree)
        verifie(obtenu == attendu,
                f"parse_date({entree!r}) = {obtenu!r}, attendu {attendu!r}")

    # les champs qui arrivent tantot en texte, tantot en dict
    r = price_point(source_id="t", price_nature="asking", price_amount=1,
                    brand={"name": "Rolex"}, dial_color={"id": 2, "name": "Black"},
                    case_material=[{"name": "Steel"}], movement={"name": "Automatic"})
    for champ in ("brand", "dial_color", "case_material", "movement"):
        verifie(isinstance(r[champ], str),
                f"price_point n'aplatit pas {champ} : {r[champ]!r}")

    # une nature inconnue doit etre refusee, pas stockee en silence
    try:
        price_point(source_id="t", price_nature="inventee", price_amount=1)
        verifie(False, "price_point accepte une price_nature inconnue")
    except ValueError:
        pass


# ------------------------------------------------------------- 2. invariants

def controle_base() -> None:
    if not BASE.exists():
        echecs.append(f"base absente : {BASE}")
        return

    lignes, illisibles = [], 0
    for numero, brut in enumerate(BASE.open(encoding="utf-8"), start=1):
        try:
            lignes.append(json.loads(brut))
        except json.JSONDecodeError:
            illisibles += 1
    verifie(illisibles == 0, f"{illisibles} ligne(s) JSON illisible(s) dans le cumul")
    if not lignes:
        echecs.append("cumul vide")
        return

    aujourdhui = dt.date.today().isoformat()
    sans_montant = sans_devise = sans_date = 0
    futures = negatives = nature_ko = colonnes_ko = 0

    for r in lignes:
        if set(r) - set(FIELDS):
            colonnes_ko += 1
        if r.get("price_nature") not in NATURES:
            nature_ko += 1
        montant = r.get("price_amount")
        if montant is None:
            sans_montant += 1
        elif montant <= 0:
            negatives += 1
        elif not r.get("price_currency"):
            sans_devise += 1
        date = r.get("price_date")
        if not date:
            sans_date += 1
        elif date > aujourdhui:
            futures += 1

    n = len(lignes)
    verifie(colonnes_ko == 0, f"{colonnes_ko} ligne(s) avec des champs hors schema")
    verifie(nature_ko == 0, f"{nature_ko} ligne(s) avec une price_nature invalide")
    verifie(negatives == 0, f"{negatives} ligne(s) avec un montant negatif ou nul")
    verifie(futures == 0, f"{futures} ligne(s) datee(s) dans le futur")
    # un prix sans devise n'est pas comparable : c'est grave, mais pas bloquant
    # tant que la proportion reste marginale (lots invendus, prix "sur demande").
    verifie(sans_devise <= n * 0.05,
            f"{sans_devise} prix sans devise ({100*sans_devise//n} %) — non comparables",
            bloquant=False)
    verifie(sans_montant <= n * 0.10,
            f"{sans_montant} ligne(s) sans montant ({100*sans_montant//n} %)",
            bloquant=False)
    verifie(sans_date <= n * 0.10,
            f"{sans_date} ligne(s) sans date ({100*sans_date//n} %)",
            bloquant=False)

    # doublons stricts : meme source, meme identifiant, meme prix, meme date
    cles = collections.Counter(
        (r["source_id"], r.get("external_id"), r.get("price_amount"), r.get("price_date"))
        for r in lignes if r.get("external_id"))
    doublons = sum(c - 1 for c in cles.values() if c > 1)
    verifie(doublons == 0,
            f"{doublons} doublon(s) strict(s) dans le cumul — l'idempotence fuit",
            bloquant=False)

    # une source qui disparait du cumul est un signal, pas un detail
    par_source = collections.Counter(r["source_id"] for r in lignes)
    print(f"  base : {n:,} prix · {len(par_source)} sources · "
          f"{len(set(r.get('price_currency') for r in lignes))} devises".replace(",", " "))
    for src, c in par_source.most_common():
        print(f"         {src:<22} {c:>6}")


# ------------------------------------------------------------------- sortie

def main() -> None:
    print("Verification du moteur de donnees\n")
    print("  parsing…")
    controle_parsing()
    print("  base…")
    controle_base()

    print()
    for a in avertissements:
        print(f"  ATTENTION  {a}")
    for e in echecs:
        print(f"  ECHEC      {e}")

    if echecs:
        print(f"\n{len(echecs)} echec(s) — ne pas se fier aux chiffres du moteur.")
        sys.exit(1)
    if avertissements:
        print(f"\nOK, avec {len(avertissements)} avertissement(s).")
    else:
        print("\nTout est vert.")


if __name__ == "__main__":
    main()
