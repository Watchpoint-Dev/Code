"""L'Excel de decision — une ligne par source, toutes les mesures reunies.

    cd ~/Desktop/WP
    python -m watchpoint rapport rapport_excel

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

from watchpoint import config

import collections
import datetime as dt
import json
import pathlib
import re
import sys
import warnings

import pandas as pd

warnings.filterwarnings("ignore")

ICI = pathlib.Path(__file__).resolve().parent
from watchpoint.registre import catalogue  # noqa: E402
from watchpoint import sources as paquet  # noqa: E402

LABO = config.RACINE
RACINE = config.RACINE
DATA = LABO / "data"
REF = config.REFERENTIELS
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
    """Apparie un nom du registre a une entree, malgre les variantes d'ecriture.

    Le registre dit « Lempertz », la fiche dit « Kunsthaus Lempertz ». Sans
    tolerance, six analyses detaillees ne remontaient pas du tout.
    """
    for c in cles(nom):
        if c in table:
            return table[c]
    # inclusion dans un sens ou dans l'autre, sur des cles assez longues pour
    # que « Christie's » ne capture pas « Christie's Hong Kong » par hasard
    for c in cles(nom):
        if len(c) < 6:
            continue
        for k, v in table.items():
            if len(k) >= 6 and (c.startswith(k) or k.startswith(c)):
                return v
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
    for f in sorted((config.RESEARCH / "preuves" / "fiches").glob("*.json")):
        try:
            d = json.load(f.open(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        # Deux schemas de fiche coexistent : le riche (imbrique) de la premiere
        # campagne et le plat des lots. On ramene le riche au plat pour que
        # toutes les fiches remontent dans les memes colonnes.
        if "acces" in d and isinstance(d.get("acces"), dict):
            a, pr, h = d.get("acces", {}), d.get("prix", {}), d.get("historique", {})
            vol, ded = d.get("volume", {}), d.get("deduplication", {})
            ad, comp = d.get("adaptateur", {}), d.get("completude", {})
            d = {
                "source": d.get("source"), "verdict": d.get("verdict"),
                "nature_prix": pr.get("nature"), "mecanisme": a.get("mecanisme"),
                "endpoint": a.get("endpoint_exact"), "pagination": a.get("pagination"),
                "volume_estime": vol.get("atteignable_reellement") or vol.get("total_annonce"),
                # Une date n'est un historique QUE si la source publie un historique.
                # Chez Bezel, la date la plus ancienne est celle de creation d'une
                # annonce revisee 11 fois depuis : ce n'est pas un prix de 2021.
                "historique_prouve": (
                    h.get("plus_ancienne_prouvee")
                    if "construire" not in str(h.get("methode", "")).lower() else ""),
                "historique_note": (
                    f"pas d'historique natif : {h.get('methode')}. La date la plus "
                    f"ancienne vue ({h.get('plus_ancienne_prouvee')}) est celle du champ "
                    f"« {str(h.get('champ_date', ''))[:60]} », pas celle d'un prix."
                    if "construire" in str(h.get("methode", "")).lower() else ""),
                "preuve_historique": h.get("preuve_anciennete"),
                "date_est_une_vente": h.get("date_presente"),
                "devise": pr.get("devise_native"), "effort": ad.get("effort"),
                "pieges": ad.get("pieges", []),
                "recommandation": d.get("recommandation"),
                "completude": {"n": comp.get("n_echantillon"),
                               **{k: v for k, v in (comp.get("champs") or {}).items()}},
            }
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
        exact = next((s for c in cles(nom) for k, s in branchees.items() if k == c), None)
        if exact:
            etat = dernier_run.get(exact["id"], {})
            meta_src = exact
            statut = str(meta_src.get("statut", ""))
            if etat.get("records"):
                action = "Collecte, adaptateur actif"
            elif statut.startswith("EN ATTENTE"):
                # adaptateur reecrit et fonctionnel, mais une decision humaine
                # conditionne son lancement
                action = "Prêt, en attente d'arbitrage"
            elif statut:
                action = "Irréparable, source bloquée"
            else:
                action = "Adaptateur en panne, à réparer"
        elif fi.get("verdict") == "a brancher":
            action = "À brancher, analyse détaillée"
        elif fi.get("verdict") == "a creuser":
            action = "À creuser, analyse détaillée"
        elif fi.get("verdict") in ("ferme", "mort"):
            action = "À négocier, analyse détaillée"
        elif trouve(prouvees, nom):
            action = "À brancher, source prouvée"
        elif trouve(negocier, nom):
            action = f"À négocier, priorité {trouve(negocier, nom)['priorite']}"
        elif trouve(ecartees, nom):
            action = "À abandonner"
        elif e.get("verdict") == "SOLIDE":
            action = "À brancher, extraction validée"
        elif str(p.get("verdict", "")).startswith("RICHE"):
            action = "À creuser, données riches"
        elif p.get("verdict", "").startswith("prix en clair"):
            action = "À creuser, parsing HTML"
        elif a and "BLOQUE" in a.get("verdict", ""):
            action = "À négocier, bloqué par anti-bot"
        elif a and "INTERDIT" in a.get("verdict", ""):
            action = "À négocier, interdit par robots"
        elif a and "illisible" in a.get("verdict", ""):
            action = "À revoir, robots illisible"
        elif a.get("endpoint"):
            # un endpoint standard qui repond est une piste serieuse, meme si la
            # sonde profonde n'est pas passee : c'est du volume a portee de main
            action = "À creuser, endpoint standard"
        elif not p:
            # ne jamais juger une source qu'on n'a pas ouverte
            action = "Non approfondi"
        elif p.get("verdict", "").startswith("pas de prix"):
            action = "Peu prometteur, rendu en JavaScript"
        else:
            action = "Peu prometteur"

        if action.startswith(("Collecte", "Prêt", "À brancher", "Adaptateur")):
            groupe = "BONNE"
        elif action.startswith("À creuser"):
            groupe = "À CREUSER"
        elif action.startswith(("À négocier", "Irréparable")):
            groupe = "À NÉGOCIER"
        elif action.startswith(("Non approfondi", "À revoir")):
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
            # Volume attribue UNIQUEMENT sur un nom exact : l'appariement tolerant
            # faisait heriter « Christie's Hong Kong » des 1 356 prix de Christie's,
            # et le total affiche passait a 4 701 au lieu de 3 345.
            "Prix en base": volumes.get(
                next((s["id"] for c in cles(nom) for k, s in branchees.items() if k == c), ""), 0),
            "Volume atteignable": trouve(prouvees, nom).get("volume", ""),
            # Les sources prouvees en juillet n'ont pas de fiche au format des lots :
            # leur historique vit dans le catalogue, avec les echantillons dans preuves/.
            "Historique (campagne)": trouve(prouvees, nom).get("historique", ""),
            "Accès (campagne)": trouve(prouvees, nom).get("acces", ""),
            "Point d'attention (campagne)": trouve(prouvees, nom).get("note", ""),
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
            "FICHE — note sur l'historique": fi.get("historique_note", ""),
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
    rang = {"Collecte, adaptateur actif": 0, "Prêt, en attente d'arbitrage": 0.2,
            "Adaptateur en panne, à réparer": 0.3, "À brancher, analyse détaillée": 1,
            "À brancher, source prouvée": 1.1, "À brancher, extraction validée": 1.2,
            "À creuser, données riches": 3, "À creuser, analyse détaillée": 3.1,
            "À creuser, parsing HTML": 4, "À creuser, endpoint standard": 4.5,
            "À négocier, priorité 1": 5, "À négocier, priorité 2": 5.1,
            "À négocier, priorité 3": 5.2, "Irréparable, source bloquée": 5.4,
            "À négocier, analyse détaillée": 5.5}
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
        ("Régénérer", "python -m watchpoint rapport rapport_excel — ne pas éditer à la main"),
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

    print(f"écrit : docs/livrables/referentiels/{chemin.name}")
    print(f"  {len(decision)} sources × {len(decision.columns)} colonnes\n")
    for k, v in c.most_common():
        print(f"  {v:>4}  {k}")


if __name__ == "__main__":
    main()
