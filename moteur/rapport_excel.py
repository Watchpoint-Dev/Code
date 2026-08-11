"""L'Excel complet — tout ce qu'on sait sur les sources, en un fichier.

    cd ~/Desktop/WP/labo
    shared/.venv/bin/python moteur/rapport_excel.py

Consolide en un seul classeur ce qui vivait dans trois fichiers separes :
le diagnostic des 200 sites, le catalogue des verdicts, la base collectee et
le registre partage.

Genere : ne pas editer a la main. Pour corriger un fait, editer catalogue.py
ou relancer la sonde, puis regenerer.
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
import sources as paquet  # noqa: E402

LABO = ICI.parent
RACINE = LABO.parent
SONDE = LABO / "data" / "sonde.json"
BASE = LABO / "data" / "price_points.jsonl"
REGISTRE = RACINE / "output" / "referentiels" / "DataSources.xlsx"
SORTIE = RACINE / "output" / "referentiels"

NATURES = {"realised": "réalisé (enchère)", "sold": "vendu", "asking": "demandé",
           "estimate": "estimation", "msrp": "prix neuf"}


def reduit(t) -> str:
    return "".join(c for c in str(t).lower() if c.isalnum())


def ajuste(writer, feuille, cadre, largeur_max=52):
    ws = writer.sheets[feuille]
    ws.freeze_panes = "A2"
    for i, col in enumerate(cadre.columns, 1):
        lg = cadre[col].astype(str).str.len().head(400).max()
        ws.column_dimensions[ws.cell(1, i).column_letter].width = min(
            max(len(str(col)), 0 if pd.isna(lg) else int(lg)) + 2, largeur_max)


def main() -> None:
    aujourdhui = dt.date.today().isoformat()

    # ---------------------------------------------------------------- sources
    lignes = ([json.loads(l) for l in BASE.open(encoding="utf-8")]
              if BASE.exists() else [])
    volumes = collections.Counter(r["source_id"] for r in lignes)
    mesures = (json.load(SONDE.open(encoding="utf-8"))["mesures"]
               if SONDE.exists() else [])

    # ------------------------------------------------------- 1. lire d'abord
    mode_emploi = pd.DataFrame([
        ("Ce que contient ce fichier",
         "Tout ce qu'on sait des sources de prix de montres au " + aujourdhui),
        ("", ""),
        ("Onglet Synthèse", "les chiffres clés en une page"),
        ("Onglet Diagnostic 200", "chaque site testé automatiquement : accessible ou non, et pourquoi"),
        ("Onglet Branchées", "les sources qui collectent aujourd'hui"),
        ("Onglet Prouvées", "testées avec succès, pas encore branchées"),
        ("Onglet À démarcher", "fermées techniquement — il faut un accord"),
        ("Onglet Écartées", "mortes ou sans issue"),
        ("Onglet Registre 210", "le recensement complet, enrichi des verdicts"),
        ("Onglet Données collectées", "ce qu'il y a réellement en base"),
        ("", ""),
        ("Les 5 natures de prix", "réalisé (enchère) · vendu · demandé · estimation · prix neuf"),
        ("Pourquoi ça compte",
         "Un prix demandé par un marchand n'est pas un prix de vente. "
         "Chaque prix stocké porte sa nature, sa date, sa devise et sa source."),
        ("", ""),
        ("Comment lire le score du diagnostic",
         "Faisabilité = mesurée (robots, HTTP, anti-bot, endpoints). Fiable. "
         "Valeur = devinée depuis la page d'accueil seulement. Indicative. "
         "Un score bas veut dire « à regarder de plus près », jamais « sans intérêt »."),
        ("Limite connue",
         "La sonde ne regarde que la page d'accueil. Christie's est mal notée alors "
         "que son API est la meilleure source du projet."),
        ("", ""),
        ("Fichier généré", "python moteur/rapport_excel.py — ne pas éditer à la main"),
    ], columns=["", " "])

    # ---------------------------------------------------------- 2. diagnostic
    diagnostic = pd.DataFrame()
    if mesures:
        diagnostic = pd.DataFrame(mesures)[[
            "source", "url", "verdict", "score", "faisabilite", "valeur",
            "robots", "crawl_delay", "params_interdits", "http", "antibot",
            "mecanismes", "endpoint", "sitemap", "volume_indice",
            "signal_prix", "signal_date", "annee_min",
        ]].rename(columns={
            "source": "Source", "url": "URL", "verdict": "Verdict",
            "score": "Score", "faisabilite": "Faisabilité", "valeur": "Valeur",
            "robots": "robots.txt", "crawl_delay": "Crawl-delay",
            "params_interdits": "Paramètres interdits", "http": "HTTP",
            "antibot": "Anti-bot détecté", "mecanismes": "Données structurées",
            "endpoint": "Endpoint standard", "sitemap": "Sitemap",
            "volume_indice": "Indice de volume", "signal_prix": "Prix repérés",
            "signal_date": "Dates repérées", "annee_min": "Année la + ancienne",
        }).sort_values("Score", ascending=False)

    # ----------------------------------------------------------- 3. branchées
    branchees = pd.DataFrame([{
        "Source": s["name"], "Catégorie": s["type"],
        "Nature du prix": NATURES.get(s["price_nature"], s["price_nature"]),
        "Prix en base": volumes.get(s["id"], 0),
        "Accès": s["access"], "robots.txt": s["robots"],
        "État": "BLOQUÉE" if "statut" in s else "active",
    } for s in (m.SOURCE for m in paquet.ALL)]).sort_values(
        "Prix en base", ascending=False)

    prouvees = pd.DataFrame([{
        "Source": p["nom"], "Catégorie": p["categorie"],
        "Nature du prix": p["nature"], "Volume atteignable": p["volume"],
        "Historique": p["historique"], "Accès": p["acces"],
        "Point d'attention": p.get("note", ""),
    } for p in catalogue.PROUVEES])

    demarcher = pd.DataFrame([{
        "Priorité": n["priorite"], "Source": n["nom"], "Catégorie": n["categorie"],
        "Ce qu'on demande": n["demande"], "Blocage": n["blocage"],
    } for n in catalogue.A_NEGOCIER]).sort_values(["Priorité", "Source"])

    ecartees = pd.DataFrame([{"Source": e["nom"], "Raison": e["raison"]}
                             for e in catalogue.ECARTEES])

    # ------------------------------------------------------------ 4. registre
    registre = pd.DataFrame()
    enrichies = 0
    if REGISTRE.exists():
        registre = pd.read_excel(REGISTRE, sheet_name="Toutes les sources")
        par_nom = {reduit(m["source"]): m for m in mesures}
        # colonnes en 'object' : pandas refuse d'ecrire un entier dans une
        # colonne typee str, et le score en est un
        for col in ["Verdict sonde", "Score sonde", "Anti-bot", "Endpoint"]:
            registre[col] = pd.Series([""] * len(registre), dtype="object")
        for i, r in registre.iterrows():
            m = par_nom.get(reduit(r["Source"]))
            if not m:
                continue
            enrichies += 1
            registre.at[i, "Verdict sonde"] = m["verdict"]
            registre.at[i, "Score sonde"] = m["score"]
            registre.at[i, "Anti-bot"] = m["antibot"]
            registre.at[i, "Endpoint"] = m["endpoint"]

    # ------------------------------------------------------------- 5. données
    donnees = pd.DataFrame()
    if lignes:
        cadre = pd.DataFrame(lignes)
        donnees = (cadre.groupby(["source_id", "price_nature", "price_currency"],
                                 dropna=False)
                   .agg(prix=("price_amount", "size"),
                        median=("price_amount", "median"),
                        mini=("price_amount", "min"), maxi=("price_amount", "max"),
                        du=("price_date", "min"), au=("price_date", "max"))
                   .reset_index()
                   .rename(columns={"source_id": "Source", "price_nature": "Nature",
                                    "price_currency": "Devise", "prix": "Nb de prix",
                                    "median": "Médiane", "mini": "Min", "maxi": "Max",
                                    "du": "Du", "au": "Au"})
                   .sort_values(["Source", "Nb de prix"], ascending=[True, False]))

    # ------------------------------------------------------------ 6. synthèse
    exploitables = sum(1 for m in mesures if m["score"] >= 40)
    interdits = sum(1 for m in mesures if "INTERDIT" in m["verdict"])
    illisibles = sum(1 for m in mesures if "illisible" in m["verdict"])
    bloques = sum(1 for m in mesures if "BLOQUE" in m["verdict"])
    synthese = pd.DataFrame([
        ("Prix collectés et stockés", f"{len(lignes)}"),
        ("Sources qui collectent aujourd'hui", f"{len(branchees)}"),
        ("Sources prouvées, pas encore branchées", f"{len(prouvees)}"),
        ("", ""),
        ("Sites testés automatiquement", f"{len(mesures)}"),
        ("  dont exploitables", f"{exploitables}"),
        ("  dont bloqués par un anti-bot", f"{bloques}"),
        ("  dont robots.txt illisible (on s'abstient)", f"{illisibles}"),
        ("  dont nous interdisent explicitement", f"{interdits}"),
        ("", ""),
        ("Sources à démarcher", f"{len(demarcher)}"),
        ("Sources écartées", f"{len(ecartees)}"),
        ("Registre enrichi par la sonde", f"{enrichies} / {len(registre)}"),
        ("", ""),
        ("Natures de prix couvertes", "4 sur 5"),
        ("La seule manquante", "l'indice de marché — négociation obligatoire"),
        ("", ""),
        ("À retenir", catalogue.AVERTISSEMENT),
    ], columns=["Indicateur", "Valeur"])

    # ------------------------------------------------------------- écriture
    SORTIE.mkdir(parents=True, exist_ok=True)
    chemin = SORTIE / f"ANALYSE_SOURCES_{aujourdhui}.xlsx"
    feuilles = [
        ("Lire d'abord", mode_emploi), ("Synthèse", synthese),
        ("Diagnostic 200", diagnostic), ("Branchées", branchees),
        ("Prouvées", prouvees), ("À démarcher", demarcher),
        ("Écartées", ecartees), ("Registre 210", registre),
        ("Données collectées", donnees),
    ]
    with pd.ExcelWriter(chemin, engine="openpyxl") as writer:
        for nom, cadre in feuilles:
            if cadre.empty:
                continue
            cadre.to_excel(writer, sheet_name=nom, index=False)
            ajuste(writer, nom, cadre, largeur_max=80 if nom == "Lire d'abord" else 52)

    print(f"écrit : output/referentiels/{chemin.name}")
    for nom, cadre in feuilles:
        if not cadre.empty:
            print(f"  {nom:<22} {len(cadre):>4} lignes")


if __name__ == "__main__":
    main()
