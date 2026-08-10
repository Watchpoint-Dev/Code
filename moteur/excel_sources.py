"""Produit l'Excel des sources dans output/referentiels/ — genere, date.

    cd ~/Desktop/WP/labo
    shared/.venv/bin/python moteur/excel_sources.py

Meme source de verite que `notes/SOURCES.md` : les adaptateurs, les volumes reels
et `moteur/catalogue.py`. La difference est le public — le Markdown est pour toi,
l'Excel part chez les associes.

Six onglets :
  Synthese       les chiffres et le message
  Branchees      ce qui collecte aujourd'hui
  Prouvees       valide par recuperation reelle, pas encore branche
  A demarcher    ferme techniquement, classe par priorite
  Ecartees       mort ou sans issue
  Registre       les 210 sources recensees, ENRICHIES des verdicts d'aout

L'onglet Registre est celui qui repond a « pour chaque source : exploitable ou
non, quel type de prix, quel historique, quel blocage, faut-il negocier ».
"""
from __future__ import annotations

import collections
import datetime as dt
import json
import pathlib
import sys

import pandas as pd

ICI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))

import catalogue  # noqa: E402
import sources as paquet_sources  # noqa: E402

LABO = ICI.parent
RACINE = LABO.parent
BASE = LABO / "data" / "price_points.jsonl"
REGISTRE = RACINE / "output" / "referentiels" / "DataSources.xlsx"
SORTIE = RACINE / "output" / "referentiels"

NATURES = {"realised": "réalisé", "sold": "vendu", "asking": "demandé",
           "estimate": "estimation", "msrp": "prix neuf"}


def reduit(texte: str) -> str:
    return "".join(c for c in str(texte).lower() if c.isalnum())


def verdicts_aout() -> dict[str, dict]:
    """Ce que la campagne du 09/08 a etabli, indexe par nom reduit."""
    v: dict[str, dict] = {}

    for module in paquet_sources.ALL:
        s = module.SOURCE
        bloquee = "statut" in s
        v[reduit(s["name"])] = {
            "Exploitable": "NON — bloquée" if bloquee else "OUI — branchée",
            "Type de prix": NATURES.get(s["price_nature"], s["price_nature"]),
            "Accès": s["access"],
            "Action": "négocier" if bloquee else "aucune, elle tourne",
        }

    for p in catalogue.PROUVEES:
        for morceau in [p["nom"], *p["nom"].replace("—", ",").split(",")]:
            if morceau.strip():
                v.setdefault(reduit(morceau), {
                    "Exploitable": "OUI — prouvée, à brancher",
                    "Type de prix": p["nature"],
                    "Historique": p["historique"],
                    "Volume atteignable": p["volume"],
                    "Accès": p["acces"],
                    "Action": "brancher un adaptateur",
                })

    for n in catalogue.A_NEGOCIER:
        for morceau in [n["nom"], *n["nom"].replace("—", ",").split(",")]:
            if morceau.strip():
                v.setdefault(reduit(morceau), {
                    "Exploitable": "NON — fermée",
                    "Blocage": n["blocage"],
                    "Action": f"négocier (priorité {n['priorite']}) : {n['demande']}",
                })

    for e in catalogue.ECARTEES:
        for morceau in [e["nom"], *e["nom"].replace("/", ",").split(",")]:
            if morceau.strip():
                v.setdefault(reduit(morceau), {
                    "Exploitable": "NON — écartée",
                    "Blocage": e["raison"],
                    "Action": "retirer des listes",
                })
    return v


def ajuste(writer, feuille: str, cadre: pd.DataFrame) -> None:
    ws = writer.sheets[feuille]
    ws.freeze_panes = "A2"
    for i, colonne in enumerate(cadre.columns, start=1):
        # une colonne entierement vide donne un max NaN
        longueurs = cadre[colonne].astype(str).str.len().head(400).max()
        largeur = max(len(str(colonne)),
                      0 if pd.isna(longueurs) else int(longueurs))
        ws.column_dimensions[ws.cell(1, i).column_letter].width = min(largeur + 2, 52)


def main() -> None:
    volumes = collections.Counter()
    if BASE.exists():
        volumes = collections.Counter(
            json.loads(l)["source_id"] for l in BASE.open(encoding="utf-8"))

    # --- Branchees
    branchees = pd.DataFrame([{
        "Source": s["name"], "Catégorie": s["type"],
        "Type de prix": NATURES.get(s["price_nature"], s["price_nature"]),
        "Prix en base": volumes.get(s["id"], 0),
        "Accès": s["access"], "robots.txt": s["robots"],
        "État": "BLOQUÉE" if "statut" in s else "active",
    } for s in (m.SOURCE for m in paquet_sources.ALL)]).sort_values(
        "Prix en base", ascending=False)

    # --- Prouvees
    prouvees = pd.DataFrame([{
        "Source": p["nom"], "Catégorie": p["categorie"], "Type de prix": p["nature"],
        "Volume atteignable": p["volume"], "Historique": p["historique"],
        "Accès": p["acces"], "Point d'attention": p.get("note", ""),
    } for p in catalogue.PROUVEES])

    # --- A demarcher
    demarcher = pd.DataFrame([{
        "Priorité": n["priorite"], "Source": n["nom"], "Catégorie": n["categorie"],
        "Ce qu'on demande": n["demande"], "Blocage": n["blocage"],
    } for n in catalogue.A_NEGOCIER]).sort_values(["Priorité", "Source"])

    # --- Ecartees
    ecartees = pd.DataFrame([{"Source": e["nom"], "Raison": e["raison"]}
                             for e in catalogue.ECARTEES])

    # --- Registre enrichi
    verdicts = verdicts_aout()
    registre, enrichies = None, 0
    if REGISTRE.exists():
        registre = pd.read_excel(REGISTRE, sheet_name="Toutes les sources")
        colonnes = ["Exploitable", "Type de prix", "Historique", "Volume atteignable",
                    "Accès", "Blocage", "Action"]
        for c in colonnes:
            registre[f"{c} (08/2026)"] = ""
        for i, ligne in registre.iterrows():
            v = verdicts.get(reduit(ligne["Source"]))
            if not v:
                continue
            enrichies += 1
            for c in colonnes:
                if c in v:
                    registre.at[i, f"{c} (08/2026)"] = v[c]

    # --- Synthese
    total = int(sum(volumes.values()))
    synthese = pd.DataFrame([
        ("Prix collectés et stockés", total),
        ("Sources branchées sur le moteur", len(branchees)),
        ("Sources prouvées, pas encore branchées", len(prouvees)),
        ("Sources à démarcher", len(demarcher)),
        ("Sources écartées (mortes ou sans issue)", len(ecartees)),
        ("Sources du registre enrichies d'un verdict d'août", enrichies),
        ("", ""),
        ("Natures de prix couvertes", "4 sur 5"),
        ("La seule manquante", "l'indice de marché — négociation obligatoire"),
        ("", ""),
        ("À retenir", catalogue.AVERTISSEMENT),
    ], columns=["Indicateur", "Valeur"])

    SORTIE.mkdir(parents=True, exist_ok=True)
    chemin = SORTIE / f"sources_{dt.date.today().isoformat()}.xlsx"
    with pd.ExcelWriter(chemin, engine="openpyxl") as writer:
        feuilles = [("Synthèse", synthese), ("Branchées", branchees),
                    ("Prouvées", prouvees), ("À démarcher", demarcher),
                    ("Écartées", ecartees)]
        if registre is not None:
            feuilles.append(("Registre 210", registre))
        for nom, cadre in feuilles:
            cadre.to_excel(writer, sheet_name=nom, index=False)
            ajuste(writer, nom, cadre)

    print(f"écrit : output/referentiels/{chemin.name}")
    print(f"  {len(branchees)} branchées ({total} prix) · {len(prouvees)} prouvées · "
          f"{len(demarcher)} à démarcher · {len(ecartees)} écartées")
    if registre is not None:
        print(f"  registre : {enrichies}/{len(registre)} sources enrichies d'un verdict d'août")


if __name__ == "__main__":
    main()
