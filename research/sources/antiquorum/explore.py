"""Antiquorum — le banc de reconnaissance, et la preuve du marteau.

    cd ~/Desktop/WP/labo/essais/antiquorum
    ../../shared/.venv/bin/python explore.py            # rejeu, ZERO requete
    ../../shared/.venv/bin/python explore.py --reseau   # 5 requetes, une vente

Le mode par defaut ne touche pas au reseau : il relit les echantillons de
`samples/` et refait la jointure. C'est la meme fonction `lots_du_brut()` que
`moteur/rejoue.py` appelle, donc le rejeu prouve aussi le contrat de rejeu.

Ce que ce script demontre, chiffres a l'appui :
  1. la premiere colonne de la price-list est le MARTEAU, pas l'estimation —
     parce que le `Sold:` du catalogue vaut la SECONDE colonne, exactement ;
  2. le taux de frais a change d'epoque (1,15 -> 1,25 -> 1,312) et il est
     degressif : on ne peut pas reconstituer un marteau par division ;
  3. `schema:price` du RDFa est l'estimation basse, pas le prix vendu ;
  4. OU commence la profondeur utile : le rendement du filtre par annee de
     vente, en separant ce qui n'est pas une montre cotable de ce qui manque
     seulement au dictionnaire de marques.
"""
import collections
import json
import pathlib
import re
import statistics
import sys

RACINE = next(p for p in pathlib.Path(__file__).resolve().parents
              if (p / "shared" / "utils.py").exists())

from watchpoint.sources import antiquorum as aq  # noqa: E402
from watchpoint.commun.utils import samples_dir, save_text  # noqa: E402

SAMPLES = pathlib.Path(__file__).resolve().parent / "samples"

# (fichier, URL d'origine) — l'URL compte : c'est elle qui dit a `lots_du_brut`
# de quelle route vient la page.
ECHANTILLONS = [
    ("auctions-year-2026.html", f"{aq.BASE}/auctions?locale=en&year=2026"),
    ("auctions-year-2015.html", f"{aq.BASE}/auctions?locale=en&year=2015"),
    ("auctions-year-2005.html", f"{aq.BASE}/auctions?locale=en&year=2005"),
    ("auctions-year-2001.html", f"{aq.BASE}/auctions?locale=en&year=2001"),
    ("auctions-year-1995.html", f"{aq.BASE}/auctions?locale=en&year=1995"),
    ("auctions-year-1989.html", f"{aq.BASE}/auctions?locale=en&year=1989"),
    ("price-list-388-monaco-2026.html", f"{aq.BASE}/en/auctions/388/price-list"),
    ("price-list-292-hongkong-2015.html", f"{aq.BASE}/en/auctions/292/price-list"),
    ("price-list-100-generaliste-2005.html", f"{aq.BASE}/en/auctions/100/price-list"),
    ("price-list-14-sandberg-geneve-2001.html", f"{aq.BASE}/en/auctions/14/price-list"),
    ("price-list-118-generaliste-1995.html", f"{aq.BASE}/en/auctions/118/price-list"),
    ("price-list-175-hongkong-1989.html", f"{aq.BASE}/en/auctions/175/price-list"),
    ("lots-monaco_june_2026-p2.html",
     f"{aq.BASE}/en/auctions/monaco_june_2026/lots?page=2"),
    ("lots-hongkong-2015-p1.html",
     f"{aq.BASE}/en/auctions/hong-kong-2015-06-27/lots?page=1"),
    ("lots-sandberg-2001-p1.html",
     f"{aq.BASE}/en/auctions/hotel-richemond-geneva-2001-03-31/lots?page=1"),
    # Les deux ventes GENERALISTES, sur plusieurs pages chacune. Une seule page
    # ne veut rien dire : dans la vente de 2005, la page 1 est la section Rolex
    # (94 % gardes, 100 % de reference) et la page 3 la section montres de poche
    # (7 % et 0 %). Antiquorum organise ses catalogues par sections.
] + [(f"lots-generaliste-1995-p{p}.html",
      f"{aq.BASE}/en/auctions/geneva-hotel-des-bergues-1995-04-22/lots?page={p}")
     for p in (1, 2, 3)] + [
    (f"lots-generaliste-2005-p{p}.html",
     f"{aq.BASE}/en/auctions/geneva-hotel-noga-hilton-2005-10-16/lots?page={p}")
    for p in (1, 2, 3, 10, 11)]

# Ce qui distingue une montre de poche d'une montre-bracelet dans un titre
# Antiquorum. Le motif sert a mesurer, pas a filtrer : c'est le filtre du projet
# qui tranche, et c'est son rendement qu'on veut ventiler par famille.
POCHE = re.compile(r"pocket|hunting[- ]cas|open[- ]fac|savonnette|\bfob\b"
                   r"|pendant watch|carriage clock|\bclock\b|form watch|verge|fusee", re.I)
BRACELET = re.compile(r"wrist|bracelet watch", re.I)
# Un lot dont le titre commence par un lieu, une nationalite ou 'Not signed'
# n'a PAS de fabricant a trouver : son rejet n'est pas une lacune du dictionnaire.
ANONYME = re.compile(r"^\s*(not signed|unsigned|swiss\b|geneva\b|russian|german"
                     r"|french\b|very fine|fine\b|attributed)", re.I)
SURNOM = re.compile(r"^\s*[\"“”?«][^\"“”?»]{2,60}"
                    r"[\"“”?»]\s*")


def brut_des_echantillons() -> list[dict]:
    entrees = []
    for nom, url in ECHANTILLONS:
        chemin = SAMPLES / nom
        if not chemin.exists():
            print(f"  manquant: {nom}")
            continue
        entrees.append({"url": url, "status": 200,
                        "payload": chemin.read_text(encoding="utf-8")})
    return entrees


def preuve_du_marteau(entrees) -> None:
    """Le `Sold:` du catalogue == colonne 2 de la price-list. Donc colonne 1 = marteau."""
    rapports, ecarts = [], 0
    for carte, prix, _ in aq.lots_du_brut(entrees):
        vendu = carte.get("vendu_frais_inclus")
        if not (prix and vendu and prix.get("frais_inclus")):
            continue
        if abs(vendu[0] - prix["frais_inclus"]) > 0.5:
            ecarts += 1
        rapports.append(vendu[0] / prix["marteau"])
    if not rapports:
        print("  aucun recoupement")
        return
    print(f"  {len(rapports)} lots recoupes entre price-list et catalogue")
    print(f"  ecarts entre 'Sold:' et la colonne 2 : {ecarts}  <- doit valoir 0")
    print(f"  rapport colonne2/colonne1 : median {statistics.median(rapports):.3f} "
          f"(de {min(rapports):.3f} a {max(rapports):.3f})")
    print("  => la colonne 1 est le MARTEAU ; on la charge, frais EXCLUS")


def taux_par_epoque() -> None:
    for nom, _ in ECHANTILLONS:
        if "price-list" not in nom:
            continue
        chemin = SAMPLES / nom
        if not chemin.exists():
            continue
        lots = aq.marteaux_de_la_page(chemin.read_text(encoding="utf-8"))
        taux = [x["frais_inclus"] / x["marteau"] for x in lots.values()
                if x["frais_inclus"]]
        if not taux:
            continue
        print(f"  {nom:44} {len(lots):>4} lots vendus  "
              f"taux {statistics.median(taux):.3f} "
              f"(degressif jusqu'a {min(taux):.3f})")


def rejeu(entrees) -> list[dict]:
    records = [aq.fiche(c, p, v) for c, p, v in aq.lots_du_brut(entrees)]
    return [r for r in records if r]


def rendement_par_epoque(records) -> None:
    """Le rendement du filtre par annee de vente, et POURQUOI un lot est rejete.

    Trois seaux, et la distinction est tout l'interet de la mesure :
      vrai non        — R1/R5/R3b : pendule, bijou, montre de poche chez une
                        marque qui n'en a jamais fait. Ce lot ne doit pas entrer.
      lacune          — R3, mais le titre NOMME un horloger. Le lot est bon, il
                        manque la marque au dictionnaire. C'est du volume
                        recuperable, et on le chiffre.
      anonyme         — R3 et le titre n'annonce aucun fabricant ('Not signed',
                        'Swiss, circa 1890'). Rien a recuperer.
    """
    from watchpoint.filtrage.filtre import filtre
    tri = filtre()
    par_annee = collections.defaultdict(collections.Counter)
    familles = collections.defaultdict(collections.Counter)
    for enregistrement in records:
        if not enregistrement.get("price_date"):
            continue
        annee = enregistrement["price_date"][:4]
        titre = enregistrement.get("title") or ""
        verdict = tri.verdict(titre, "AUCTION", maker=enregistrement.get("brand"),
                              corpus_horloger=True)
        compte = par_annee[annee]
        compte["lots"] += 1
        compte["reference"] += 1 if enregistrement.get("reference") else 0
        famille = ("bracelet" if BRACELET.search(titre)
                   else "poche" if POCHE.search(titre) else "indetermine")
        familles[famille][verdict["verdict"]] += 1
        if verdict["verdict"] == "GARDER":
            compte["garde"] += 1
        elif verdict["rule"] != "R3":
            compte["vrai_non"] += 1
        elif ANONYME.match(SURNOM.sub("", titre)):
            compte["anonyme"] += 1
        else:
            compte["lacune"] += 1

    print(f"  {'vente':>6} {'lots':>5} {'garde':>7} {'ref':>6} {'vrai non':>9} "
          f"{'lacune':>7} {'anonyme':>8} {'plafond':>8}")
    for annee, c in sorted(par_annee.items()):
        n = c["lots"]
        print(f"  {annee:>6} {n:>5} {100*c['garde']/n:>6.0f}% {100*c['reference']/n:>5.0f}% "
              f"{c['vrai_non']:>9} {c['lacune']:>7} {c['anonyme']:>8} "
              f"{100*(c['garde']+c['lacune'])/n:>7.0f}%")
    print("  'plafond' = ce que le filtre garderait si les horlogers nommes dans "
          "les titres\n  entraient au dictionnaire de marques.")
    print("  rendement par famille, toutes epoques :")
    for famille, c in familles.items():
        n = sum(c.values())
        print(f"    {famille:<12} {c['GARDER']:>3}/{n:<3} = {100*c['GARDER']/n:.0f} % gardes")


def bilan(records) -> None:
    from watchpoint.schema import completeness
    print(f"  {len(records)} enregistrements")
    for champ in ("price_currency", "price_includes_premium",
                  "reference_provenance", "price_nature_provenance"):
        print(f"  {champ:26} {dict(collections.Counter(r[champ] for r in records))}")
    taux = completeness(records)
    for champ in ("price_amount", "price_currency", "price_date", "brand",
                  "reference", "model", "year", "case_material", "condition",
                  "estimate_low"):
        print(f"    {champ:16} {taux[champ]:>3} %")
    annees = collections.Counter(r["price_date"][:4] for r in records if r["price_date"])
    print(f"  annees de vente : {dict(sorted(annees.items()))}")


def une_vente_en_direct() -> None:
    """6 requetes : l'annee, la price-list, et 4 pages de catalogue."""
    raw, records, journal = aq.collect(cap=40, annees=[2026])
    print(f"  {len(raw)} requetes, {len(records)} records")
    for ligne in journal:
        print(f"    {ligne}")
    save_text(samples_dir(__file__) / "direct-records.json",
              json.dumps(records, ensure_ascii=False, indent=1))


def main() -> None:
    entrees = brut_des_echantillons()
    print(f"\n== brut relu : {len(entrees)} pages, 0 requete ==")
    print("\n== 1. la premiere colonne est-elle le marteau ? ==")
    preuve_du_marteau(entrees)
    print("\n== 2. le taux de frais par epoque ==")
    taux_par_epoque()
    records = rejeu(entrees)
    print("\n== 3. ce que le rejeu produit ==")
    bilan(records)
    print("\n== 4. ou commence la profondeur UTILE ? ==")
    rendement_par_epoque(records)
    if "--reseau" in sys.argv:
        print("\n== 5. une vente en direct (5 requetes, Crawl-delay 5 s) ==")
        une_vente_en_direct()
    else:
        print("\n(ajouter --reseau pour une collecte reelle de 40 lots)")


if __name__ == "__main__":
    main()
