"""L'Excel de decision — une ligne par source, toutes les mesures reunies.

    cd ~/Desktop/WP/labo
    shared/.venv/bin/python moteur/rapport_excel.py

Reunit quatre couches de mesure, du plus large au plus profond :

  1. TON REGISTRE       WatchDataSources_v3.xlsx — les 210 sources recensees
  2. ACCESSIBILITE      sonde.py       — robots, anti-bot, HTTP (200 sites)
  3. NATURE DE LA DATA  sonde_profonde.py — prix reels, mecanisme, profondeur (71)
  4. EXTRACTION REELLE  verifie_sources.py — fiches telechargees, completude (30)

Plus le catalogue des verdicts humains et la base reellement collectee.

Le but : une ligne par source, assez d'information pour trancher entre
SCRAPER, NEGOCIER ou ABANDONNER.

Genere : ne pas editer. Corriger catalogue.py ou relancer une sonde, puis regenerer.
"""
from __future__ import annotations

import collections
import datetime as dt
import json
import pathlib
import sys
import warnings

import pandas as pd

warnings.filterwarnings("ignore")

ICI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
import catalogue  # noqa: E402
import sources as paquet  # noqa: E402

LABO = ICI.parent
RACINE = LABO.parent
DATA = LABO / "data"
REF = RACINE / "output" / "referentiels"
REGISTRE = REF / "WatchDataSources_v3.xlsx"

NATURES = {"realised": "réalisé (enchère)", "sold": "vendu", "asking": "demandé",
           "estimate": "estimation", "msrp": "prix neuf"}


def reduit(t) -> str:
    return "".join(c for c in str(t).lower() if c.isalnum())


def cles(nom: str) -> list[str]:
    """Toutes les formes sous lesquelles une source peut etre nommee.

    Le registre ecrit « Bezel (getbezel.com / shop.getbezel.com) » la ou le code
    dit « Bezel » : sans ca, une source branchee passe pour non testee.
    """
    brut = str(nom)
    formes = [brut, brut.split("(")[0], brut.split("—")[0], brut.split("/")[0]]
    return [c for c in dict.fromkeys(reduit(f) for f in formes) if c]


def trouve(table: dict, nom: str):
    for c in cles(nom):
        if c in table:
            return table[c]
    return {}


def charge(nom, cle):
    f = DATA / nom
    if not f.exists():
        return {}
    d = json.load(f.open(encoding="utf-8"))
    return {reduit(x["source"]): x for x in d[cle]}


def ajuste(writer, feuille, cadre, maxi=50):
    ws = writer.sheets[feuille]
    ws.freeze_panes = "B2"
    for i, col in enumerate(cadre.columns, 1):
        lg = cadre[col].astype(str).str.len().head(400).max()
        ws.column_dimensions[ws.cell(1, i).column_letter].width = min(
            max(len(str(col)), 0 if pd.isna(lg) else int(lg)) + 2, maxi)


def main() -> None:
    jour = dt.date.today().isoformat()
    acces = charge("sonde.json", "mesures")
    profond = charge("sonde_profonde.json", "sources")
    extrait = charge("verification_sources.json", "sources")

    # Couche 5 : les fiches detaillees redigees par les analystes, une par source.
    fiches = {}
    for f in sorted((LABO / "preuves" / "fiches").glob("*.json")):
        try:
            d = json.load(f.open(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        fiches[reduit(d.get("source", f.stem))] = d

    base = DATA / "price_points.jsonl"
    lignes = [json.loads(l) for l in base.open(encoding="utf-8")] if base.exists() else []
    volumes = collections.Counter(r["source_id"] for r in lignes)

    branchees = {reduit(m.SOURCE["name"]): m.SOURCE for m in paquet.ALL}

    # Un adaptateur qui existe n'est pas un adaptateur qui collecte. Bezel rend 0
    # et LiveAuctioneers est bloque : les dire "branchees" serait faux.
    dernier_run = {}
    runs = sorted((DATA / "runs").glob("*.json"))
    for f in runs:
        try:
            m = json.load(f.open(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        for s in m.get("sources", []):
            dernier_run[s["id"]] = s
    prouvees = {reduit(p["nom"].split(" —")[0]): p for p in catalogue.PROUVEES}
    negocier = {}
    for n in catalogue.A_NEGOCIER:
        for morceau in [n["nom"], *n["nom"].replace("—", ",").split(",")]:
            negocier.setdefault(reduit(morceau), n)
    ecartees = {reduit(e["nom"]): e for e in catalogue.ECARTEES}

    # ------------------------------------------------- la table de decision
    reg = pd.read_excel(REGISTRE, sheet_name="Sources")
    lignes_sortie = []
    for _, r in reg.iterrows():
        nom = str(r["source_name"]).strip()
        cle = reduit(nom)
        a, p, e = trouve(acces, nom), trouve(profond, nom), trouve(extrait, nom)
        comp = e.get("completude", {})
        fi = trouve(fiches, nom)
        fcomp = fi.get("completude", {}) or {}

        # que faire de cette source ? La fiche detaillee prime : c'est la seule
        # couche ou quelqu'un est alle chercher un enregistrement ancien.
        # L'ETAT REEL d'un adaptateur prime sur toute recommandation : un
        # adaptateur casse doit apparaitre comme casse, meme si une fiche
        # explique par ailleurs comment le reconstruire.
        if trouve(branchees, nom):
            etat = dernier_run.get(trouve(branchees, nom)["id"], {})
            meta_src = trouve(branchees, nom)
            statut = str(meta_src.get("statut", ""))
            if etat.get("records"):
                action = "COLLECTE — adaptateur actif"
            elif statut.startswith("EN ATTENTE"):
                # adaptateur reecrit et fonctionnel, mais une decision humaine
                # conditionne son lancement
                action = "PRÊT — en attente d'arbitrage"
            elif statut:
                action = "IRRÉPARABLE — source bloquée"
            else:
                action = "ADAPTATEUR HS — à réparer"
        elif fi.get("verdict") == "a brancher":
            action = "À BRANCHER — fiche détaillée"
        elif fi.get("verdict") == "a creuser":
            action = "À CREUSER — fiche détaillée"
        elif fi.get("verdict") in ("ferme", "mort"):
            action = "NÉGOCIER — fiche détaillée"
        elif trouve(prouvees, nom):
            action = "À BRANCHER — prouvée"
        elif trouve(negocier, nom):
            action = f"NÉGOCIER — priorité {trouve(negocier, nom)['priorite']}"
        elif trouve(ecartees, nom):
            action = "ABANDONNER"
        elif e.get("verdict") == "SOLIDE":
            action = "À BRANCHER — extraction validée"
        elif str(p.get("verdict", "")).startswith("RICHE"):
            action = "À CREUSER — données riches"
        elif p.get("verdict", "").startswith("prix en clair"):
            action = "À CREUSER — parsing HTML"
        elif a and "BLOQUE" in a.get("verdict", ""):
            action = "NÉGOCIER — anti-bot"
        elif a and "INTERDIT" in a.get("verdict", ""):
            action = "NÉGOCIER — robots interdit"
        elif a and "illisible" in a.get("verdict", ""):
            action = "à revoir — robots illisible"
        elif a.get("endpoint"):
            # un endpoint standard qui repond est une piste serieuse, meme si la
            # sonde profonde n'est pas passee : c'est du volume a portee de main
            action = "À CREUSER — endpoint standard"
        elif not p:
            # ne jamais juger une source qu'on n'a pas ouverte
            action = "non approfondi"
        elif p.get("verdict", "").startswith("pas de prix"):
            action = "peu prometteur — rendu JS"
        else:
            action = "peu prometteur"

        if action.startswith(("COLLECTE", "PRÊT", "À BRANCHER", "ADAPTATEUR HS")):
            groupe = "BONNE"
        elif action.startswith("À CREUSER"):
            groupe = "À CREUSER"
        elif action.startswith(("NÉGOCIER", "IRRÉPARABLE")):
            groupe = "À NÉGOCIER"
        elif action.startswith(("non approfondi", "à revoir")):
            groupe = "NON TESTÉE"
        else:
            groupe = "NON RETENUE"

        lignes_sortie.append({
            "Source": nom,
            "GROUPE": groupe,
            "ACTION": action,
            "Catégorie": r.get("type_canonical"),
            "URL": r.get("url"),
            # --- couche 1 : ton registre
            "Nature du prix (registre)": r.get("price_semantics"),
            "Historique (registre, ans)": r.get("history_depth_years"),
            "Verdict (registre)": r.get("verdict"),
            "Tier": r.get("tier"),
            # --- couche 2 : accessibilité
            "Accessible ?": a.get("verdict", "non testé"),
            "Score accès": a.get("score"),
            "robots.txt": a.get("robots"),
            "Crawl-delay": a.get("crawl_delay"),
            "Anti-bot": a.get("antibot"),
            "Endpoint standard": a.get("endpoint"),
            # --- couche 3 : nature de la donnée
            "Données trouvées ?": p.get("verdict", ""),
            "Page testée": p.get("page_testee"),
            "Mécanisme": p.get("mecanisme"),
            "Prix sur la page": p.get("prix_sur_la_page"),
            "Objets structurés": p.get("objets_structures"),
            "Pagination": p.get("pagination"),
            "URLs au sitemap": p.get("urls_sitemap"),
            "Année min (page)": p.get("annee_min"),
            "Année max (page)": p.get("annee_max"),
            "Prix médian (page)": p.get("prix_median"),
            "Devises repérées": p.get("devises"),
            "Références repérées": p.get("references_reperees"),
            # --- couche 4 : extraction réelle
            "Fiches extraites": e.get("fiches_extraites"),
            "Extraction — verdict": e.get("verdict"),
            "% prix": comp.get("price_amount"),
            "% référence": comp.get("reference"),
            "% date": comp.get("price_date"),
            "% marque": comp.get("brand"),
            "Part horlogère %": e.get("part_horlogere"),
            # --- ce qu'on en fait
            "Prix en base": volumes.get((trouve(branchees, nom) or {}).get("id", ""), 0),
            "Volume atteignable": trouve(prouvees, nom).get("volume", ""),
            "Ce qu'on demande": trouve(negocier, nom).get("demande", ""),
            "Blocage": trouve(negocier, nom).get("blocage", "")
                       or trouve(ecartees, nom).get("raison", ""),
            # --- couche 5 : fiche detaillee (analyse dediee)
            "FICHE — verdict": fi.get("verdict", ""),
            "FICHE — nature du prix": fi.get("nature_prix", ""),
            "FICHE — mécanisme": fi.get("mecanisme", ""),
            "FICHE — endpoint": fi.get("endpoint", ""),
            "FICHE — volume estimé": fi.get("volume_estime", ""),
            "FICHE — pagination": fi.get("pagination", ""),
            "FICHE — historique PROUVÉ": fi.get("historique_prouve", ""),
            "FICHE — preuve historique": fi.get("preuve_historique", ""),
            "FICHE — la date est une vente ?": fi.get("date_est_une_vente", ""),
            "FICHE — n échantillon": fcomp.get("n", ""),
            "FICHE — % marque": fcomp.get("brand", ""),
            "FICHE — % référence": fcomp.get("reference", ""),
            "FICHE — % prix": fcomp.get("price", ""),
            "FICHE — % date": fcomp.get("date", ""),
            "FICHE — % specs": fcomp.get("specs", ""),
            "FICHE — devise": fi.get("devise", ""),
            "FICHE — effort": fi.get("effort", ""),
            "FICHE — pièges": " · ".join(fi.get("pieges", []) or []),
            "FICHE — recommandation": fi.get("recommandation", ""),
        })

    decision = pd.DataFrame(lignes_sortie)
    rang = {"COLLECTE — adaptateur actif": 0,
            "PRÊT — en attente d'arbitrage": 0.2,
            "ADAPTATEUR HS — à réparer": 0.3,
            "IRRÉPARABLE — source bloquée": 5.4,
            "À BRANCHER — fiche détaillée": 0.5,
            "À BRANCHER — prouvée": 1, "À CREUSER — fiche détaillée": 2.5,
            "NÉGOCIER — fiche détaillée": 5.5,
            "À BRANCHER — extraction validée": 2, "À CREUSER — données riches": 3,
            "À CREUSER — parsing HTML": 4, "À CREUSER — endpoint standard": 4.5, "NÉGOCIER — priorité 1": 5,
            "NÉGOCIER — priorité 2": 6, "NÉGOCIER — priorité 3": 7}
    decision["_r"] = decision["ACTION"].map(lambda x: rang.get(x, 9))
    decision = decision.sort_values(["_r", "Prix sur la page"],
                                    ascending=[True, False]).drop(columns="_r")

    # ------------------------------------------------------------ synthèse
    c = collections.Counter(decision["ACTION"])
    synthese = pd.DataFrame(
        [("Sources au registre", len(decision)),
         ("Prix collectés à ce jour", len(lignes)), ("", "")]
        + [(k, v) for k, v in c.most_common()]
        + [("", ""),
           ("Natures de prix couvertes", "4 sur 5"),
           ("La seule manquante", "l'indice de marché — négociation obligatoire"),
           ("", ""), ("À retenir", catalogue.AVERTISSEMENT)],
        columns=["Indicateur", "Valeur"])

    mode = pd.DataFrame([
        ("Comment lire ce fichier", ""),
        ("", ""),
        ("Onglet Décision", "UNE LIGNE PAR SOURCE."),
        ("  colonne GROUPE", "la lecture rapide : BONNE / À CREUSER / À NÉGOCIER / NON TESTÉE / NON RETENUE"),
        ("  colonne ACTION", "le détail : ce qu'il faut faire précisément"),
        ("", ""),
        ("BONNE", "on peut en tirer des données : ça collecte, c'est prêt, ou l'adaptateur reste à écrire"),
        ("", ""),
        ("COLLECTE", "un adaptateur existe ET son dernier run a produit des données"),
        ("ADAPTATEUR HS", "un adaptateur existe mais ne rend plus rien — à réparer, prioritaire"),
        ("À BRANCHER", "prouvée par une extraction réelle, mais aucun adaptateur écrit"),
        ("À CREUSER", "des données ont été trouvées, le mécanisme reste à établir"),
        ("NÉGOCIER", "fermée techniquement — seul un accord ouvre la porte"),
        ("NON APPROFONDI", "jamais ouverte : ce n'est PAS un jugement de valeur"),
        ("Onglet Synthèse", "les compteurs"),
        ("Onglet Collecté", "ce qu'il y a réellement en base aujourd'hui"),
        ("", ""),
        ("Les 4 couches de mesure", ""),
        ("  1. Registre", "ce que tu avais recensé en juillet (v3)"),
        ("  2. Accessibilité", "robots, anti-bot, HTTP — 200 sites testés automatiquement"),
        ("  3. Nature de la donnée", "prix réels trouvés sur une page de liste — 71 sources"),
        ("  4. Extraction réelle", "fiches téléchargées et champs mesurés — boutiques à endpoint standard"),
        ("", ""),
        ("Ce en quoi on peut avoir confiance", ""),
        ("  Fiable", "robots, anti-bot, endpoint, fiches extraites, % de champs remplis"),
        ("  Indicatif", "« Année min/max (page) » = années lues sur la page. Ce peut être "
                        "l'année de fabrication d'une montre, pas la date d'une vente. "
                        "Une profondeur apparente n'est PAS une profondeur d'historique prouvée."),
        ("  Non mesuré", "les sources bloquées ne sont pas re-sollicitées : leur colonne "
                         "« Données trouvées » reste vide, ce n'est pas un jugement de valeur."),
        ("", ""),
        ("Régénérer", "python moteur/rapport_excel.py — ne pas éditer à la main"),
    ], columns=["", " "])

    collecte = pd.DataFrame()
    if lignes:
        cadre = pd.DataFrame(lignes)
        collecte = (cadre.groupby(["source_id", "price_nature", "price_currency"],
                                  dropna=False)
                    .agg(prix=("price_amount", "size"), median=("price_amount", "median"),
                         du=("price_date", "min"), au=("price_date", "max"))
                    .reset_index()
                    .rename(columns={"source_id": "Source", "price_nature": "Nature",
                                     "price_currency": "Devise", "prix": "Nb de prix",
                                     "median": "Médiane", "du": "Du", "au": "Au"}))

    chemin = REF / f"DECISION_SOURCES_{jour}.xlsx"
    with pd.ExcelWriter(chemin, engine="openpyxl") as w:
        for nom, cadre, maxi in [("Lire d'abord", mode, 96), ("Synthèse", synthese, 90),
                                 ("Décision", decision, 40), ("Collecté", collecte, 30)]:
            if cadre.empty:
                continue
            cadre.to_excel(w, sheet_name=nom, index=False)
            ajuste(w, nom, cadre, maxi)

    print(f"écrit : output/referentiels/{chemin.name}")
    print(f"  {len(decision)} sources × {len(decision.columns)} colonnes\n")
    for k, v in c.most_common():
        print(f"  {v:>4}  {k}")


if __name__ == "__main__":
    main()
