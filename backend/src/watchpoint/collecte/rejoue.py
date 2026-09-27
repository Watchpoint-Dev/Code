"""Rejouer la normalisation sur le brut deja collecte, sans une seule requete.

    cd ~/Desktop/WP
    python -m watchpoint rejoue              # toutes les boutiques
    python -m watchpoint rejoue berrys       # une seule

Conserver le brut n'a de valeur que si l'on sait s'en resservir. Quand on
decouvre qu'une source publiait un champ qu'on ne lisait pas — la categorie chez
Berry's, la reference dans le corps de l'annonce chez Montredo — il ne faut pas
redemander 18 000 pages : il faut relire celles qu'on a.

Toutes les sources sont rejouables : les six boutiques Shopify, plus
Christie's, Artcurial et Lyon & Turnbull. Chacune expose deux fonctions pures,
`lots_du_brut()` et `fiche()`, que la collecte et le rejeu appellent
indifferemment. Seul WatchRecon melange encore lecture et normalisation.

Les lignes de la source sont remplacees dans le cumul, pas ajoutees. Le filtre
est reapplique dans la foulee.
"""
from __future__ import annotations

from watchpoint import config

import datetime as dt
import gzip
import inspect
import json
import pathlib
import sys


from watchpoint import sources  # noqa: E402
from watchpoint.filtrage.filtre import filtre  # noqa: E402
from watchpoint.sources import _shopify  # noqa: E402

DATA = config.DATA
CUMUL = DATA / "price_points.jsonl"

# Les reglages passes a _shopify.collecte par chaque module. On les redonne ici
# parce que le brut ne les porte pas : une page collectee ne dit pas dans quelle
# devise elle a ete demandee.
# Les boutiques Shopify. Leurs reglages ne sont PAS recopies ici : chaque
# adaptateur porte son `NORMALISATION`, et le rejeu le lit. La copie qui vivait
# a cet endroit avait divergé des adaptateurs sans que rien ne le signale.
SHOPIFY = ("analogshift", "berrys", "montredo", "cwsellors", "hairspring",
           "craft_and_tailored", "hodinkee", "keystone", "topper",
           "bulangandsons", "acollectedman", "certifiedwatchstore",
           "watchesdotcom")

# Les boutiques WooCommerce : leur normalisation vit dans sources/_woo.py.
WOO = ("watchtrader", "wannabuyawatch", "awco", "globalwatchshop", "chronofinder",
       "amsterdamvintage", "watchesofdistinction")


def produits_du_brut(source_id: str) -> tuple[list[dict], str | None]:
    """(produits, moment de la capture) de la derniere collecte.

    Le moment est rendu avec les produits parce qu'une source datee « au
    releve » n'a pas d'autre date que celle-la. Sans lui, chaque rejeu posait
    la date DU JOUR : Montredo, collectee le 25/08, ressortait datee du 02/09
    apres quelques relectures, et le pic de l'annee en cours grossissait a
    chaque fois. Mesure du 02/09/2026 : 19 707 lignes portaient une date
    posterieure a leur propre collecte.
    """
    dossier = DATA / "raw" / source_id
    fichiers = sorted([*dossier.glob("*.json"), *dossier.glob("*.json.gz")]) \
        if dossier.exists() else []
    if not fichiers:
        return [], None
    chemin = fichiers[-1]
    moment = _moment_du_fichier(chemin)
    ouvre = gzip.open if chemin.suffix == ".gz" else open
    try:
        with ouvre(chemin, "rt", encoding="utf-8") as flux:
            entrees = json.load(flux)
    except (json.JSONDecodeError, OSError):
        return [], None

    tout = []
    for entree in entrees:
        try:
            tout.extend(json.loads(entree.get("payload", "")).get("products", []))
        except (json.JSONDecodeError, AttributeError):
            continue
    return tout, (moment.date().isoformat() if moment else None)


def _moment_du_fichier(chemin: pathlib.Path):
    """'2026-08-25T06-21-31.json.gz' -> datetime UTC."""
    try:
        return dt.datetime.strptime(chemin.name[:19], "%Y-%m-%dT%H-%M-%S").replace(
            tzinfo=dt.timezone.utc)
    except ValueError:
        return None


def rejoue_encheres(source_id: str) -> list[dict]:
    """Les maisons de ventes : chaque adaptateur sait relire son propre brut."""
    module = next((m for m in sources.ALL if m.SOURCE["id"] == source_id), None)
    if module is None or not hasattr(module, "lots_du_brut"):
        return []
    dossier = DATA / "raw" / source_id
    fichiers = sorted([*dossier.glob("*.json"), *dossier.glob("*.json.gz")]) \
        if dossier.exists() else []
    if not fichiers:
        print(f"  {source_id} : aucun brut")
        return []

    tri = filtre()
    records, vus = [], set()
    for chemin in fichiers:
        ouvre = gzip.open if chemin.suffix == ".gz" else open
        try:
            with ouvre(chemin, "rt", encoding="utf-8") as flux:
                entrees = json.load(flux)
        except (json.JSONDecodeError, OSError):
            continue

        # Le nom du fichier porte l'instant de la collecte. Certaines sources en
        # ont besoin : WatchRecon date ses annonces en relatif ('3 days ago'),
        # et rejouer avec l'heure du jour les daterait toutes d'aujourd'hui.
        moment = _moment_du_fichier(chemin)
        lots = (module.lots_du_brut(entrees, moment)
                if "moment" in inspect.signature(module.lots_du_brut).parameters
                else module.lots_du_brut(entrees))
        for element in lots:
            lot, extra = (element[0], element[1:]) if isinstance(element, tuple) else (element, ())
            fabrique = getattr(module, "fiche", None) or module.fiche_produit
            record = fabrique(lot, *extra)
            if record is None:
                continue
            # Le brut cumule plusieurs collectes : un lot deja vu ne doit pas
            # entrer deux fois. La DATE ne fait pas partie de la cle : chez
            # WatchRecon, qui date en relatif, la meme annonce lue le 9 et le
            # 25 aout ressort a deux dates absolues legerement differentes et
            # entrait deux fois — 1 709 annonces comptees en double. Une meme
            # annonce au meme prix est la meme offre, quel que soit le jour ou
            # on l'a vue ; un changement de prix, lui, fait bien une ligne de
            # plus, et c'est ce qu'on veut.
            cle = (record["external_id"], record["price_amount"])
            if cle in vus:
                continue
            vus.add(cle)
            # Chaque ligne garde la date du fichier brut d'ou elle vient. Le
            # cumul en reecrivait une seule pour toute la source — la premiere
            # rencontree — et les six captures WatchRecon du 9 au 27 aout
            # ressortaient toutes datees du 9, ce qui faisait paraitre 4 091
            # annonces publiees APRES avoir ete collectees.
            if moment:
                record["collected_at"] = moment.isoformat()
            type_source = "AUCTION" if module.SOURCE["type"] == "auction" else "MARKETPLACE"
            verdict = tri.verdict(record.get("title") or "", type_source,
                                  maker=record.get("brand"),
                                  corpus_horloger=module.SOURCE.get("corpus_horloger", False),
                                  categorie_source=record.get("source_category"))
            record["filter_verdict"] = verdict["verdict"]
            record["filter_rule"] = verdict["rule"]
            record["filter_version"] = verdict["filter_version"]
            records.append(record)
    return records


# Toutes les sources dont l'adaptateur expose `lots_du_brut()` et une fabrique.
ENCHERES = ("christies", "artcurial", "lyonandturnbull", "monacolegend",
            "watchesofswitzerland", "watchrecon", "fortuna", "loupethis", "sworders",
            # Vague 1, 21/09/2026. `knightsbridge` figure ici bien qu'il s'agisse
            # d'une boutique WooCommerce : son adaptateur ne passe pas par
            # `_woo.collecte` (l'API Store n'y publie pas de date, il faut la
            # joindre depuis /wp-json/wp/v2/product), il expose donc sa propre
            # fabrique comme une maison de ventes.
            "phillips", "antiquorum", "cottone", "morphy", "grailzee",
            "knightsbridge")


def rejoue_woo(source_id: str) -> list[dict]:
    """Les boutiques WooCommerce : une fabrique commune, comme pour Shopify."""
    from watchpoint.sources import _woo
    module = next((m for m in sources.ALL if m.SOURCE["id"] == source_id), None)
    if module is None:
        return []
    dossier = DATA / "raw" / source_id
    fichiers = sorted([*dossier.glob("*.json"), *dossier.glob("*.json.gz")]) \
        if dossier.exists() else []
    if not fichiers:
        print(f"  {source_id} : aucun brut")
        return []

    tri = filtre()
    records, vus = [], set()
    for chemin in fichiers:
        ouvre = gzip.open if chemin.suffix == ".gz" else open
        try:
            with ouvre(chemin, "rt", encoding="utf-8") as flux:
                entrees = json.load(flux)
        except (json.JSONDecodeError, OSError):
            continue
        for produit in _woo.lots_du_brut(entrees):
            record = _woo.fiche(produit, module.SOURCE)
            if record is None or record["external_id"] in vus:
                continue
            vus.add(record["external_id"])
            verdict = tri.verdict(record.get("title") or "", "MARKETPLACE",
                                  maker=record.get("brand"),
                                  corpus_horloger=module.SOURCE.get("corpus_horloger", False),
                                  categorie_source=record.get("source_category"))
            record["filter_verdict"] = verdict["verdict"]
            record["filter_rule"] = verdict["rule"]
            record["filter_version"] = verdict["filter_version"]
            records.append(record)
    return records


def rejoue(source_id: str) -> list[dict]:
    module = next((m for m in sources.ALL if m.SOURCE["id"] == source_id), None)
    if module is None or source_id not in SHOPIFY:
        return []
    reglages = dict(getattr(module, "NORMALISATION", {}))
    produits, moment = produits_du_brut(source_id)
    if not produits:
        print(f"  {source_id} : aucun brut lisible")
        return []

    tri = filtre()
    records, vus = [], set()
    for produit in produits:
        # La date du RELEVE est celle de la capture, pas celle du rejeu.
        record = _shopify.fiche(produit, module.SOURCE, moment=moment, **reglages)
        if record is None:
            continue
        # Les collections d'une meme boutique se recoupent : CW Sellors range
        # la meme montre dans 'mens-watches' et 'luxury-watches'. La collecte
        # ecarte ces doublons, le rejeu doit faire pareil.
        if record["external_id"] in vus:
            continue
        vus.add(record["external_id"])
        # La categorie publiee par la boutique est passee telle quelle : c'est
        # R0 qui l'interprete, pas l'appelant.
        verdict = tri.verdict(record.get("title") or "", "MARKETPLACE",
                              maker=record.get("brand"),
                              corpus_horloger=module.SOURCE.get("corpus_horloger", False),
                              categorie_source=record.get("source_category"))
        record["filter_verdict"] = verdict["verdict"]
        record["filter_rule"] = verdict["rule"]
        record["filter_version"] = verdict["filter_version"]
        records.append(record)
    return records


def remplace_dans_le_cumul(source_id: str, records: list[dict]) -> tuple[int, int]:
    """Substitue les lignes de la source. Ecriture atomique par fichier temporaire."""
    instant = None
    provisoire = CUMUL.with_suffix(".jsonl.tmp")
    retirees = 0
    with CUMUL.open(encoding="utf-8") as entree, provisoire.open("w", encoding="utf-8") as sortie:
        for ligne in entree:
            if not ligne.strip():
                continue
            r = json.loads(ligne)
            if r["source_id"] == source_id:
                retirees += 1
                instant = instant or r.get("collected_at")
                continue
            sortie.write(ligne)
        for record in records:
            # Pose seulement si le rejeu n'a pas su dater la ligne lui-meme.
            record.setdefault("collected_at", None)
            if not record["collected_at"]:
                record["collected_at"] = instant
            sortie.write(json.dumps(record, ensure_ascii=False) + "\n")
    provisoire.replace(CUMUL)
    return retirees, len(records)


def main() -> None:
    demandees = [a for a in sys.argv[1:] if not a.startswith("-")]
    cibles = [s for s in (*SHOPIFY, *WOO, *ENCHERES) if not demandees or s in demandees]
    if not cibles:
        sys.exit(f"Sources rejouables : {', '.join((*SHOPIFY, *WOO, *ENCHERES))}")

    for source_id in cibles:
        records = (rejoue_encheres(source_id) if source_id in ENCHERES
                   else rejoue_woo(source_id) if source_id in WOO
                   else rejoue(source_id))
        if not records:
            continue
        avant, apres = remplace_dans_le_cumul(source_id, records)
        with_ref = sum(1 for r in records if r["reference"])
        with_marque = sum(1 for r in records if r["brand"])
        gardes = sum(1 for r in records if r["filter_verdict"] == "GARDER")
        print(f"  {source_id:<20} {avant} -> {apres} lignes · "
              f"reference {100 * with_ref // len(records)} % · "
              f"marque {100 * with_marque // len(records)} % · "
              f"gardees {100 * gardes // len(records)} %")


if __name__ == "__main__":
    main()
