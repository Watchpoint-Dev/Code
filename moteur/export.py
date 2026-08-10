"""Exporte la base de prix vers output/ — CSV et Excel, datés.

    cd ~/Desktop/WP/labo
    source shared/.venv/bin/activate

    python moteur/export.py              # CSV + Excel de toute la base
    python moteur/export.py christies    # une seule source
    python moteur/export.py --csv        # CSV seulement (plus rapide)

Tout atterrit dans `output/donnees/`. Rien n'est jamais ecrase : chaque export
porte sa date, on peut donc comparer deux etats de la base.
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import sys

import pandas as pd

RACINE = pathlib.Path(__file__).resolve().parents[2]      # ~/Desktop/WP
BASE = RACINE / "labo" / "data" / "price_points.jsonl"
SORTIE = RACINE / "output" / "donnees"

# Ordre des colonnes dans le fichier livre : le plus parlant en premier.
COLONNES = [
    "brand", "model", "reference", "year",
    "price_amount", "price_currency", "price_nature", "price_date",
    "estimate_low", "estimate_high",
    "case_material", "case_size_mm", "movement", "dial_color", "condition",
    "seller", "source_id", "source_type", "source_url",
    "external_id", "collected_at",
]

# Noms lisibles pour la version Excel, qui est destinee a etre partagee.
ENTETES_FR = {
    "brand": "Marque", "model": "Modele", "reference": "Reference", "year": "Annee",
    "price_amount": "Prix", "price_currency": "Devise", "price_nature": "Nature du prix",
    "price_date": "Date du prix", "estimate_low": "Estimation basse",
    "estimate_high": "Estimation haute", "case_material": "Matiere boitier",
    "case_size_mm": "Taille (mm)", "movement": "Mouvement", "dial_color": "Cadran",
    "condition": "Etat", "seller": "Vendeur", "source_id": "Source",
    "source_type": "Type de source", "source_url": "Lien", "external_id": "Id source",
    "collected_at": "Collecte le",
}

NATURES_FR = {
    "realised": "realise (enchere)", "sold": "vendu", "asking": "demande",
    "estimate": "estimation", "msrp": "prix neuf",
}


def charger(source: str | None) -> pd.DataFrame:
    if not BASE.exists():
        sys.exit(f"Base introuvable : {BASE}\n  -> lance d'abord une collecte "
                 f"(python moteur/run.py)")
    lignes = [json.loads(x) for x in BASE.open(encoding="utf-8")]
    df = pd.DataFrame(lignes)
    if source:
        df = df[df["source_id"] == source]
        if df.empty:
            sources = sorted(pd.DataFrame(lignes)["source_id"].unique())
            sys.exit(f"Aucun prix pour {source!r}. Sources disponibles : {', '.join(sources)}")
    return df.reindex(columns=COLONNES)


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    csv_seul = "--csv" in sys.argv
    source = args[0] if args else None

    df = charger(source)
    SORTIE.mkdir(parents=True, exist_ok=True)
    jour = dt.date.today().isoformat()
    nom = f"prix_{source}_{jour}" if source else f"prix_{jour}"

    # --- CSV : pour un tableur, un script, un import en base
    chemin_csv = SORTIE / f"{nom}.csv"
    df.to_csv(chemin_csv, index=False, encoding="utf-8-sig")  # sig = accents OK dans Excel
    print(f"CSV   : output/donnees/{chemin_csv.name}  ({len(df):,} lignes)".replace(",", " "))

    if csv_seul:
        return

    # --- Excel : pour etre partage et lu par quelqu'un d'autre
    lisible = df.copy()
    lisible["price_nature"] = lisible["price_nature"].map(NATURES_FR).fillna(lisible["price_nature"])
    lisible = lisible.rename(columns=ENTETES_FR)

    # La devise fait PARTIE de la cle de regroupement : une mediane qui melange USD
    # et HKD ne veut rien dire, et ce resume part chez des tiers.
    resume = (df.groupby(["source_id", "price_nature", "price_currency"], dropna=False)
                .agg(prix=("price_amount", "size"),
                     montant_median=("price_amount", "median"),
                     date_min=("price_date", "min"),
                     date_max=("price_date", "max"))
                .reset_index()
                .sort_values(["source_id", "prix"], ascending=[True, False])
                .rename(columns={"source_id": "Source", "price_nature": "Nature",
                                 "price_currency": "Devise",
                                 "prix": "Nombre de prix", "montant_median": "Montant median",
                                 "date_min": "Du", "date_max": "Au"}))

    chemin_xlsx = SORTIE / f"{nom}.xlsx"
    with pd.ExcelWriter(chemin_xlsx, engine="openpyxl") as writer:
        resume.to_excel(writer, sheet_name="Resume", index=False)
        lisible.to_excel(writer, sheet_name="Prix", index=False)
        for feuille, cadre in (("Resume", resume), ("Prix", lisible)):
            ws = writer.sheets[feuille]
            ws.freeze_panes = "A2"
            for i, colonne in enumerate(cadre.columns, start=1):
                largeur = max(len(str(colonne)),
                              cadre[colonne].astype(str).str.len().head(300).max() or 0)
                ws.column_dimensions[ws.cell(1, i).column_letter].width = min(largeur + 2, 46)

    print(f"Excel : output/donnees/{chemin_xlsx.name}  (onglets Resume + Prix)")


if __name__ == "__main__":
    main()
