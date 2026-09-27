"""Orchestrateur de collecte — lance les adaptateurs et range la data.

    source backend/.venv/bin/activate
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

from watchpoint import config

import datetime as dt
import gzip
import json
import os
import pathlib
import sys

from watchpoint import sources
from watchpoint.filtrage.filtre import filtre
from watchpoint.schema import FIELDS, completeness

# data/ vit a la racine de l'etabli, a cote du moteur : consultable a la main
DATA = config.DATA
CUMUL = DATA / "price_points.jsonl"

CLES_COMPLETUDE = ["price_amount", "price_currency", "price_date", "brand",
                   "reference", "model", "year", "case_material", "movement"]


def _cle(record: dict) -> tuple:
    """Identifie un prix de maniere stable entre deux executions.

    Le titre ne fait PAS partie de l'identite : un vendeur peut le reecrire
    sans toucher a son prix. Mesure du 27/08/2026 — la meme annonce WatchRecon
    (cid 7546849, 123 175 $) est entree deux fois parce que 'CHRONO' etait
    devenu 'CHRONOGRAPH ... FULL'. Il ne sert de repli que pour les sources
    qui ne fournissent aucun identifiant.
    """
    if record.get("external_id"):
        return (record["source_id"], record["external_id"],
                record.get("price_amount"), record.get("price_date"))
    return (record["source_id"], None, record.get("price_amount"),
            record.get("price_date"), (record.get("title") or "")[:80])


def _volumes_du_dernier_run() -> dict[str, int]:
    """Ce que chaque source a rendu la derniere fois — la reference de comparaison."""
    runs = sorted((DATA / "runs").glob("*.json")) if (DATA / "runs").exists() else []
    for chemin in reversed(runs):
        try:
            manifeste = json.loads(chemin.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        # Un manifeste partiel — collecte interrompue — n'est pas une reference :
        # les sources qu'elle n'a pas atteintes y valent zero, et toutes
        # paraitraient effondrees au run suivant. Les manifestes d'avant le
        # 22/09/2026 ne portent pas le drapeau : leur absence vaut « complet ».
        if manifeste.get("complet") is False:
            continue
        volumes = {s["id"]: s["records"] for s in manifeste.get("sources", [])
                   if s.get("records")}
        if volumes:
            return volumes
    return {}


def _cles_existantes() -> set[int]:
    """Les cles deja en base, stockees en EMPREINTES et non en tuples.

    Un tuple (source, id, montant, date) pese quelques centaines d'octets une
    fois ses chaines comptees ; un entier en pese 28. Sur 165 000 lignes, la
    difference se voit — et cet ensemble vit en memoire pendant toute la
    collecte, a cote du brut de la source en cours.

    Le risque d'une empreinte est la collision : deux prix differents rendant le
    meme entier seraient confondus, et le second jete. A 165 000 cles sur les
    2^64 valeurs de `hash`, la probabilite est de l'ordre de 10^-9 — sans
    commune mesure avec le doublon que cet ensemble sert justement a eviter.
    """
    if not CUMUL.exists():
        return set()
    cles = set()
    with CUMUL.open(encoding="utf-8") as flux:
        for ligne in flux:
            try:
                cles.add(hash(_cle(json.loads(ligne))))
            except (json.JSONDecodeError, KeyError):
                continue
    return cles


class _Verrou:
    """Empeche deux collectes simultanees. C'est ce qui a manque le 21/09/2026.

    Trois `run.py` ont ete lances en parallele ce soir-la, en pensant que des
    domaines disjoints suffisaient a rendre l'operation sure. La politesse
    reseau l'etait ; la MEMOIRE ne l'etait pas. Chaque processus garde en RAM le
    brut de la source en cours — 6 050 pages pour Antiquorum — plus son propre
    jeu de cles. Le systeme a tue les deux plus gros, et Antiquorum, Phillips,
    Grailzee et Morphy n'ont rien ramene.

    Le verrou refuse la seconde collecte au lieu de laisser le systeme choisir
    laquelle tuer. `--force` existe pour le cas ou un verrou survit a un plantage.
    """

    def __init__(self):
        self.chemin = DATA / ".collecte-en-cours"

    def __enter__(self):
        if self.chemin.exists() and "--force" not in sys.argv:
            detail = self.chemin.read_text(encoding="utf-8").strip()
            sys.exit(
                f"une collecte tourne deja ({detail}).\n"
                "Deux collectes simultanees ont epuise la memoire le 21/09/2026 et "
                "ont ete tuees toutes les deux.\n"
                "Attends la fin, ou relance avec --force si ce verrou est orphelin "
                f"(supprime alors data/{self.chemin.name}).")
        self.chemin.write_text(
            f"pid {os.getpid()} depuis {dt.datetime.now().isoformat(timespec='seconds')}",
            encoding="utf-8")
        return self

    def __exit__(self, *_):
        self.chemin.unlink(missing_ok=True)
        return False


# Les sources qu'on ne rappelle plus, et pourquoi. Elles restent dans le
# dossier avec leur brut et leurs lignes deja collectees : geler une collecte
# n'est pas effacer une donnee. Une collecte generale ne doit pas rejouer un
# refus toutes les nuits.
# Mesure du 02/09/2026, faite en comparant les deux en-tetes sur la MEME URL :
# ces trois sites servent la page a un navigateur et la refusent a un robot
# declare. Leur robots.txt ne nous interdit pourtant rien — c'est le serveur
# qui tranche, pas la politique publiee. On honore le refus : le contourner
# demanderait de mentir a nouveau sur qui nous sommes, et c'est precisement ce
# qu'on a arrete de faire.
GELEES = {
    "watchesofdistinction":
        "403 a ClaudeBot, 200 a Chrome. 496 montres deja en base, conservees.",
    "wannabuyawatch":
        "403 a ClaudeBot, 200 a Chrome. 5 812 montres deja en base, conservees.",
    "watchesofswitzerland":
        "404 a ClaudeBot, 200 a Chrome sur la MEME URL — un refus deguise en "
        "page absente. 2 029 prix neufs deja en base, conserves.",
}


def _ecrit_manifeste(manifeste: dict, horodatage: str, nouveaux: int,
                     *, partiel: bool) -> None:
    """Ecrit le manifeste, en le marquant INCOMPLET tant que la collecte court.

    Le drapeau compte : `_volumes_du_dernier_run()` lit le dernier manifeste
    pour detecter les effondrements de volume. Un manifeste partiel pris pour
    une reference ferait crier a l'effondrement sur toutes les sources que la
    collecte n'avait pas encore atteintes.
    """
    manifeste["total_records"] = sum(s["records"] for s in manifeste["sources"])
    manifeste["total_nouveaux"] = nouveaux
    manifeste["complet"] = not partiel
    (DATA / "runs" / f"{horodatage}.json").write_text(
        json.dumps(manifeste, ensure_ascii=False, indent=1), encoding="utf-8")


def main() -> None:
    # Sans cela, une collecte de plusieurs heures redirigee vers un fichier
    # n'ecrit rien avant sa fin : on ne peut pas la suivre, ni voir ou elle
    # a cale. Mesure du 02/09/2026.
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except AttributeError:
        pass
    # Les drapeaux ne sont pas des noms de source : sans ce filtre, `--force`
    # serait cherche dans sources.ALL et la collecte sortirait a vide.
    demandees = [a.lower() for a in sys.argv[1:] if not a.startswith("-")]
    modules = [m for m in sources.ALL if not demandees or m.SOURCE["id"] in demandees]
    # Une source gelee ne repart que si on la nomme explicitement.
    if not demandees:
        for identifiant, raison in GELEES.items():
            avant = len(modules)
            modules = [m for m in modules if m.SOURCE["id"] != identifiant]
            if len(modules) < avant:
                print(f"GELEE  {identifiant} — {raison}")
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
    effondrees: list[tuple] = []   # sources dont le volume s'est effondre
    derniers_volumes = _volumes_du_dernier_run()

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

        # Le filtre est appose ici, une fois pour toutes, a l'entree. Il ne
        # supprime rien : chaque ligne repart avec son verdict, la regle qui l'a
        # produit et la version du filtre utilisee. Rejouer un filtre corrige sur
        # tout l'historique ne demande alors aucune requete reseau.
        tri = filtre()
        for record in records:
            record["collected_at"] = instant
            type_source = "AUCTION" if record.get("source_type") == "auction" else "MARKETPLACE"
            verdict = tri.verdict(record.get("title") or "", type_source,
                                  maker=record.get("brand"),
                                  corpus_horloger=meta.get("corpus_horloger", False),
                                  categorie_source=record.get("source_category"))
            record["filter_verdict"] = verdict["verdict"]
            record["filter_rule"] = verdict["rule"]
            record["filter_version"] = verdict["filter_version"]

        # 1. brut, horodate, jamais ecrase. Compresse : une page Shopify pese
        #    2 Mo, un catalogue en fait cent. Le JSON se comprime d'un facteur 10
        #    et reste lisible d'une ligne (gzip.open). Conserver le brut ne doit
        #    pas devenir une raison de ne plus le conserver.
        if raw:
            piste = DATA / "raw" / meta["id"]
            piste.mkdir(parents=True, exist_ok=True)
            with gzip.open(piste / f"{horodatage}.json.gz", "wt", encoding="utf-8") as flux:
                json.dump(raw, flux, ensure_ascii=False)

        # 2. normalise, dernier run
        if records:
            (DATA / "normalized" / f"{meta['id']}.json").write_text(
                json.dumps(records, ensure_ascii=False, indent=1), encoding="utf-8")

        # 3. cumul dedoublonne
        nouveaux = [r for r in records if hash(_cle(r)) not in deja_vu]
        for record in nouveaux:
            deja_vu.add(hash(_cle(record)))
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

        # Rendre 1 prix quand on en rendait 90 n'est pas un succes. L'alarme a zero
        # laissait passer un adaptateur devenu inutile : Bezel est tombe de 89 a 1
        # sans un mot, alors que 32 670 annonces restaient accessibles ailleurs.
        precedent = derniers_volumes.get(meta["id"])
        if (precedent and precedent >= 20 and len(records) < precedent * 0.3
                and not bloquee):
            effondrees.append((meta["name"], precedent, len(records)))

        resume = {
            "id": meta["id"], "name": meta["name"], "type": meta["type"],
            "price_nature": meta["price_nature"], "access": meta["access"],
            "robots": meta["robots"],
            "records": len(records), "nouveaux": len(nouveaux),
            "requetes_http": len(raw),
            "periode": [dates[0], dates[-1]] if dates else None,
            "completude": completeness(records, CLES_COMPLETUDE),
            "filtre": {v: sum(1 for r in records if r["filter_verdict"] == v)
                       for v in ("GARDER", "REJETER", "QUARANTAINE")},
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

        # Le manifeste est ecrit APRES CHAQUE SOURCE, pas seulement a la fin.
        # Le 21/09/2026 deux collectes ont ete tuees en cours : leurs lignes
        # etaient bien en base — le cumul s'ecrit source par source — mais le
        # journal de ce qui avait ete collecte, avec ses completudes, ses
        # plafonds et ses erreurs, n'a jamais ete ecrit. On savait ce qu'on
        # avait, on ne savait plus comment on l'avait eu.
        _ecrit_manifeste(manifeste, horodatage, nouveaux_total, partiel=True)

        # Le brut de la source est desormais sur le disque, compresse. Le garder
        # en memoire pendant que la source suivante accumule le sien est ce qui
        # a fait tuer le processus : `del` rend la place tout de suite au lieu
        # d'attendre la reaffectation de la boucle.
        del raw, records, nouveaux

    _ecrit_manifeste(manifeste, horodatage, nouveaux_total, partiel=False)

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

    if effondrees:
        print("\n" + "!" * 78)
        for nom, avant, apres in effondrees:
            chute = round(100 * (1 - apres / avant))
            print(f"EFFONDREMENT — {nom} : {avant} -> {apres} prix ({chute} % de chute)")
        print("  l'adaptateur rend encore quelque chose, mais bien trop peu :")
        print("  le site a probablement change de structure. A verifier avant de se")
        print("  fier a cette collecte.")
        print("!" * 78)

    if silencieuses or plantees or effondrees:
        print("\n" + "!" * 78)
        if plantees:
            print(f"ECHEC — {len(plantees)} source(s) en erreur : {', '.join(plantees)}")
        if silencieuses:
            print(f"ECHEC — {len(silencieuses)} source(s) vivante(s) n'ont RIEN ramene : "
                  f"{', '.join(silencieuses)}")
            print("  soit le site a change, soit l'adaptateur est casse. Ne pas se fier")
            print("  aux chiffres de ce run tant que ce n'est pas elucide.")
        print("!" * 78)
    if silencieuses or plantees or effondrees:
        sys.exit(1)


if __name__ == "__main__":
    with _Verrou():
        main()
