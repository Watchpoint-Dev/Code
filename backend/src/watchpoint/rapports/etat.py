"""Ecrit un etat des lieux de la base dans docs/rapports/ETAT_DATA.md.

    cd ~/Desktop/WP
    source backend/.venv/bin/activate
    python -m watchpoint rapport etat

Ce fichier est GENERE : ne jamais l'editer a la main, il sera ecrase. C'est
justement l'interet — un recap ecrit a la main devient faux en deux semaines
et on cesse de s'y fier.

A relancer apres chaque collecte.
"""
from __future__ import annotations

from watchpoint import config

import collections
import datetime as dt
import json
import pathlib
import sys

RACINE = config.RACINE
BASE = config.DATA / "price_points.jsonl"
CIBLE = config.RAPPORTS / "ETAT_DATA.md"

# Sources prouvees par la campagne du 09/08 mais pas encore branchees au moteur.
# (echantillons dans research/preuves/)
PROUVEES_NON_BRANCHEES = [
    ("EveryWatch",        "agregateur",      "realise", "218 000", "2,5 ans glissants"),
    ("Bezel — API interne", "marketplace",   "demande", "32 620",  "releve"),
    ("Hodinkee Shop",     "marchand",        "demande", "18 946",  "date"),
    ("Wanna Buy A Watch", "marchand",        "vendu",   "6 477",   "date"),
    ("Loupe This",        "encheres en ligne", "realise", "4 145", "2021 -> 2026"),
    ("Watchtrader",       "marchand",        "demande", "3 916",   "date"),
    ("Monaco Legend",     "maison de ventes", "realise", "3 738",  "2019 -> 2026"),
    ("Patek Philippe",    "marque",          "prix neuf", "266",   "hebdomadaire"),
    ("Grand Seiko",       "marque",          "prix neuf", "~150/marche", "hebdomadaire"),
]

NATURES = {"realised": "realise", "sold": "vendu", "asking": "demande",
           "estimate": "estimation", "msrp": "prix neuf"}

CHAMPS_CLES = ["price_amount", "price_currency", "price_date", "brand",
               "reference", "model", "year", "case_material", "movement"]


def taux(lignes, champ):
    if not lignes:
        return 0
    return round(100 * sum(1 for r in lignes if r.get(champ) not in (None, "", [], {})) / len(lignes))


def main() -> None:
    if not BASE.exists():
        sys.exit(f"Base introuvable : {BASE}\n  -> lance une collecte : python -m watchpoint collecte")
    lignes = [json.loads(x) for x in BASE.open(encoding="utf-8")]

    par_source = collections.Counter(r["source_id"] for r in lignes)
    par_nature = collections.Counter(r["price_nature"] for r in lignes)
    dates = sorted(r["price_date"] for r in lignes if r.get("price_date"))
    montants = sorted(r["price_amount"] for r in lignes if r.get("price_amount"))
    marques = collections.Counter(r["brand"] for r in lignes if r.get("brand"))
    devises = collections.Counter(r["price_currency"] for r in lignes if r.get("price_currency"))

    out = []
    A = out.append
    A("# État de la base")
    A("")
    A(f"**Généré le {dt.date.today().isoformat()}** par `python -m watchpoint rapport etat` — "
      "ne pas éditer à la main, ce fichier est écrasé à chaque exécution.")
    A("")
    A("## En un coup d'œil")
    A("")
    A(f"- **{len(lignes):,} prix** en base".replace(",", " "))
    A(f"- **{len(par_source)} sources** branchées sur le moteur")
    A(f"- **{taux(lignes, 'price_date')} %** des prix sont datés")
    A(f"- période : **{dates[0]} → {dates[-1]}**" if dates else "- aucune date")
    A(f"- **{len(marques)} marques** distinctes")
    if montants:
        med = montants[len(montants) // 2]
        A(f"- montants : {montants[0]:,.0f} → {montants[-1]:,.0f}, médiane {med:,.0f}".replace(",", " "))
    A(f"- devises : {', '.join(f'{d} ({n})' for d, n in devises.most_common())}")
    A("")

    A("## Par source")
    A("")
    A("| Source | Prix | Nature | Période | Prix | Date | Marque | Réf. |")
    A("|---|---:|---|---|---:|---:|---:|---:|")
    for src, n in par_source.most_common():
        sous = [r for r in lignes if r["source_id"] == src]
        d = sorted(r["price_date"] for r in sous if r.get("price_date"))
        periode = f"{d[0]} → {d[-1]}" if d else "sans date"
        nat = NATURES.get(collections.Counter(r["price_nature"] for r in sous).most_common(1)[0][0], "?")
        A(f"| {src} | {n} | {nat} | {periode} | {taux(sous,'price_amount')} % | "
          f"{taux(sous,'price_date')} % | {taux(sous,'brand')} % | {taux(sous,'reference')} % |")
    A("")

    # Une mediane qui melange USD et HKD ne veut rien dire : on ventile.
    A("## Montants, par source ET par devise")
    A("")
    A("| Source | Devise | Prix | Médiane | Min | Max |")
    A("|---|---|---:|---:|---:|---:|")
    couples = collections.Counter((r["source_id"], r.get("price_currency"))
                                  for r in lignes if r.get("price_amount"))
    for (src, dev), n in sorted(couples.items(), key=lambda x: (x[0][0], -x[1])):
        m = sorted(r["price_amount"] for r in lignes
                   if r["source_id"] == src and r.get("price_currency") == dev
                   and r.get("price_amount"))
        if not m:
            continue
        A(f"| {src} | {dev or '_manquante_'} | {n} | {m[len(m)//2]:,.0f} | "
          f"{m[0]:,.0f} | {m[-1]:,.0f} |".replace(",", " "))
    A("")
    A("**Ne jamais comparer deux lignes de devises différentes.** Aucune conversion "
      "n'est appliquée : les montants sont ceux de la source.")
    A("")

    A("## Par nature de prix")
    A("")
    A("| Nature | Prix |")
    A("|---|---:|")
    for nat, n in par_nature.most_common():
        A(f"| {NATURES.get(nat, nat)} | {n} |")
    A("")

    A("## Complétude globale")
    A("")
    A("| Champ | Rempli |")
    A("|---|---:|")
    for champ in CHAMPS_CLES:
        A(f"| `{champ}` | {taux(lignes, champ)} % |")
    A("")
    A("La **référence** est le champ qui limite la déduplication entre sources : "
      "sans elle, impossible de rapprocher une même montre vue chez deux vendeurs.")
    A("")

    A("## Top marques")
    A("")
    A(" · ".join(f"**{m}** {n}" for m, n in marques.most_common(8)))
    A("")

    A("## Prouvées, pas encore branchées")
    A("")
    A("Sources validées par récupération réelle (échantillons dans `research/preuves/`) "
      "mais pas encore reliées au moteur.")
    A("")
    A("| Source | Catégorie | Nature | Volume | Historique |")
    A("|---|---|---|---:|---|")
    for nom, cat, nat, vol, hist in PROUVEES_NON_BRANCHEES:
        A(f"| {nom} | {cat} | {nat} | {vol} | {hist} |")
    A("")

    CIBLE.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"écrit : notes/{CIBLE.name}  ({len(lignes):,} prix, {len(par_source)} sources)".replace(",", " "))


if __name__ == "__main__":
    main()
