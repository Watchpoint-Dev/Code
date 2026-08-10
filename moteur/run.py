"""Orchestrateur de collecte — lance les adaptateurs et range la data.

    source ../shared/.venv/bin/activate
    python run.py                 # toutes les sources
    python run.py bezel christies # seulement celles-ci

Rangement (dossier data/) :
    raw/{source}/{horodatage}.json   ce que la source a renvoye, non retouche
    normalized/{source}.json         dernier run, normalise et lisible
    price_points.jsonl               cumul append-only, 1 ligne = 1 prix
    runs/{horodatage}.json           manifeste : comptes, erreurs, completude

Le cumul est dedoublonne : relancer le script n'ecrit pas deux fois le meme
prix. La collecte est donc idempotente et peut tourner tous les jours.
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import sys

import sources
from schema import FIELDS, completeness

# data/ vit a la racine de l'etabli, a cote du moteur : consultable a la main
DATA = pathlib.Path(__file__).resolve().parent.parent / "data"
CUMUL = DATA / "price_points.jsonl"

CLES_COMPLETUDE = ["price_amount", "price_currency", "price_date", "brand",
                   "reference", "model", "year", "case_material", "movement"]


def _cle(record: dict) -> tuple:
    """Identifie un prix de maniere stable entre deux executions."""
    return (record["source_id"], record.get("external_id"),
            record.get("price_amount"), record.get("price_date"),
            (record.get("title") or "")[:80])


def _cles_existantes() -> set[tuple]:
    if not CUMUL.exists():
        return set()
    cles = set()
    with CUMUL.open(encoding="utf-8") as flux:
        for ligne in flux:
            try:
                cles.add(_cle(json.loads(ligne)))
            except (json.JSONDecodeError, KeyError):
                continue
    return cles


def main() -> None:
    demandees = [a.lower() for a in sys.argv[1:]]
    modules = [m for m in sources.ALL if not demandees or m.SOURCE["id"] in demandees]
    if not modules:
        sys.exit(f"Sources connues : {', '.join(m.SOURCE['id'] for m in sources.ALL)}")

    horodatage = dt.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    instant = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    for dossier in (DATA / "raw", DATA / "normalized", DATA / "runs"):
        dossier.mkdir(parents=True, exist_ok=True)

    deja_vu = _cles_existantes()
    print(f"cumul existant : {len(deja_vu)} prix deja stockes\n")

    manifeste = {"run": horodatage, "collected_at": instant, "sources": []}
    nouveaux_total = 0
    silencieuses: list[str] = []   # sources vivantes qui n'ont rien ramene
    plantees: list[str] = []       # sources qui ont leve une exception

    for module in modules:
        meta = module.SOURCE
        print(f"--- {meta['name']} ({meta['type']}, prix {meta['price_nature']})")
        try:
            raw, records, journal = module.collect()
            erreur = None
        except Exception as exc:  # une source qui casse ne doit pas tuer le run...
            raw, records, journal, erreur = [], [], [], f"{type(exc).__name__}: {exc}"
            plantees.append(meta["name"])       # ...mais elle doit etre criee a la fin
            print(f"    ECHEC — {erreur}")

        for record in records:
            record["collected_at"] = instant

        # 1. brut, horodate, jamais ecrase
        if raw:
            piste = DATA / "raw" / meta["id"]
            piste.mkdir(parents=True, exist_ok=True)
            (piste / f"{horodatage}.json").write_text(
                json.dumps(raw, ensure_ascii=False), encoding="utf-8")

        # 2. normalise, dernier run
        if records:
            (DATA / "normalized" / f"{meta['id']}.json").write_text(
                json.dumps(records, ensure_ascii=False, indent=1), encoding="utf-8")

        # 3. cumul dedoublonne
        nouveaux = [r for r in records if _cle(r) not in deja_vu]
        for record in nouveaux:
            deja_vu.add(_cle(record))
        if nouveaux:
            with CUMUL.open("a", encoding="utf-8") as flux:
                for record in nouveaux:
                    flux.write(json.dumps(record, ensure_ascii=False) + "\n")
        nouveaux_total += len(nouveaux)

        dates = sorted(r["price_date"] for r in records if r.get("price_date"))
        # Une source qu'on sait bloquee (anti-bot) n'est pas une anomalie ;
        # une source vivante qui ne ramene rien en est une.
        bloquee = "statut" in meta
        muette = not records and not bloquee
        if muette:
            silencieuses.append(meta["name"])

        resume = {
            "id": meta["id"], "name": meta["name"], "type": meta["type"],
            "price_nature": meta["price_nature"], "access": meta["access"],
            "robots": meta["robots"],
            "records": len(records), "nouveaux": len(nouveaux),
            "requetes_http": len(raw),
            "periode": [dates[0], dates[-1]] if dates else None,
            "completude": completeness(records, CLES_COMPLETUDE),
            "erreur": erreur, "journal": journal,
            "bloquee_connue": bloquee, "silencieuse": muette,
            # un adaptateur signale son plafond par une ligne de journal "TRONQUE:"
            "tronque": any(str(l).startswith("TRONQUE") for l in journal),
        }
        manifeste["sources"].append(resume)

        if records:
            print(f"    {len(records)} prix ({len(nouveaux)} nouveaux) · "
                  f"{len(raw)} requetes · periode {resume['periode']}")
        for ligne in journal[-3:]:
            print(f"      · {ligne}")
        print()

    manifeste["total_records"] = sum(s["records"] for s in manifeste["sources"])
    manifeste["total_nouveaux"] = nouveaux_total
    (DATA / "runs" / f"{horodatage}.json").write_text(
        json.dumps(manifeste, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---- rapport final
    print("=" * 78)
    print(f"{'SOURCE':<20}{'NATURE':<11}{'PRIX':>7}{'NEUF':>7}  PERIODE")
    for s in manifeste["sources"]:
        periode = f"{s['periode'][0]} -> {s['periode'][1]}" if s["periode"] else "sans date"
        print(f"{s['name']:<20}{s['price_nature']:<11}{s['records']:>7}{s['nouveaux']:>7}  {periode}")
    print("-" * 78)
    print(f"{'TOTAL':<20}{'':<11}{manifeste['total_records']:>7}{nouveaux_total:>7}")

    print(f"\nCOMPLETUDE par champ (%)")
    entete = f"{'':<20}" + "".join(f"{c[:9]:>10}" for c in CLES_COMPLETUDE)
    print(entete)
    for s in manifeste["sources"]:
        if not s["completude"]:
            continue
        ligne = f"{s['name'][:19]:<20}" + "".join(
            f"{s['completude'].get(c, 0):>9}%" for c in CLES_COMPLETUDE)
        print(ligne)

    print(f"\ncumul : {CUMUL.relative_to(DATA.parent)} — {len(deja_vu)} prix au total")
    print(f"manifeste : data/runs/{horodatage}.json")

    # ---- alarme : un run muet ne doit JAMAIS passer pour un succes.
    # Une source qui casse en silence produit une base partielle qu'on croit
    # complete — c'est le pire des deux mondes. On sort en erreur pour que
    # l'appelant (toi, ou un cron) le voie.
    tronquees = [s["name"] for s in manifeste["sources"] if s.get("tronque")]
    if tronquees:
        print(f"\nATTENTION — collecte TRONQUEE (plafond atteint) : {', '.join(tronquees)}")
        print("  la base est partielle sur ces sources ; augmente le cap si besoin.")

    if silencieuses or plantees:
        print("\n" + "!" * 78)
        if plantees:
            print(f"ECHEC — {len(plantees)} source(s) en erreur : {', '.join(plantees)}")
        if silencieuses:
            print(f"ECHEC — {len(silencieuses)} source(s) vivante(s) n'ont RIEN ramene : "
                  f"{', '.join(silencieuses)}")
            print("  soit le site a change, soit l'adaptateur est casse. Ne pas se fier")
            print("  aux chiffres de ce run tant que ce n'est pas elucide.")
        print("!" * 78)
        sys.exit(1)


if __name__ == "__main__":
    main()
