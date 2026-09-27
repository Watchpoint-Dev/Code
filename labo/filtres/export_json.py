# -*- coding: utf-8 -*-
"""
Compilation du fichier maitre Excel vers config/filters.json.

Chaine complete :
    Filtres_scrapping.xlsx  ->  ce script  ->  config/filters.json  ->  scrapper

Le fichier Excel est la couche humaine, la seule que l'on edite. Ce script le compile
en JSON, et le scrapper ne connait que le JSON : aucune dependance openpyxl en
production, et un diff Git lisible en revue de PR.

Le script echoue volontairement (code de sortie 1) si le schema est invalide.
Une sevrite mal orthographiee ou un scope inconnu doit casser le build, pas etre
avale en silence par le scrapper.

Usage :
    python export_json.py Filtres_scrapping.xlsx config/filters.json
"""

import json
import sys
from datetime import datetime, timezone

import openpyxl

# ---------------------------------------------------------------------------
# Domaines de valeurs autorises. Toute valeur hors de ces ensembles fait
# echouer le build en nommant l'onglet et le numero de ligne fautif.
# ---------------------------------------------------------------------------
SEVERITES = {"HARD", "CONDITIONAL"}
SCOPES = {"ALL", "AUCTION", "MARKETPLACE"}
BOOLS = {"TRUE", "FALSE"}
VERDICTS = {"GARDER", "REJETER", "QUARANTAINE"}

# Concepts et familles de marqueurs qu'une regle de l'arbre nomme explicitement.
# Sans ce controle, une regle peut pointer vers un concept absent du classeur :
# elle ne se declenche alors jamais, en silence, et le build reste vert. C'est
# exactement ce qui est arrive a R1b (alarm_complication) et R3b (case_pocket),
# restees mortes pendant que 213 lignes de la colonne MONTRE DE POCHE ACCEPTEE
# etaient renseignees a la main pour rien.
CONCEPTS_REQUIS = {
    "case_pocket": "R3b",
    "alarm_complication": "R1b",
}
MARQUEURS_REQUIS = {
    "EXCLUSIVITY": "R5",
    "NEGATION_CATEGORY": "R2",
    "COMPLETENESS": "R6",
    "DESCRIPTIVE": "R6b",
}


def read(wb, sheet):
    """Lit un onglet et renvoie une liste de dictionnaires {EN_TETE: valeur}.

    La premiere ligne sert d'en-tete. Les lignes entierement vides sont ignorees,
    ce qui evite qu'un appui malencontreux sur Entree en bas de l'onglet ne cree
    une entree fantome dans le JSON.
    """
    ws = wb[sheet]
    head = [cell.value for cell in ws[1]]
    lignes = []
    for row in ws.iter_rows(min_row=2):
        rec = dict(zip(head, [cell.value for cell in row]))
        if any(v not in (None, "") for v in rec.values()):
            lignes.append(rec)
    return lignes


def split_terms(valeur):
    """Eclate une cellule 'terme A | terme B | terme C' en liste de termes.

    Le separateur est la barre verticale. Les espaces autour sont supprimes,
    et les segments vides sont ecartes, ce qui rend le fichier tolerant a une
    barre en fin de cellule.
    """
    if not valeur:
        return []
    return [t.strip() for t in str(valeur).split("|") if t.strip()]


def main(source, destination):
    wb = openpyxl.load_workbook(source, data_only=True)
    erreurs = []

    # -----------------------------------------------------------------------
    # BRANDS. Porte positive du filtrage : une annonce sans marque de cette
    # liste est rejetee (regle R3).
    # -----------------------------------------------------------------------
    brands = []
    for i, r in enumerate(read(wb, "BRANDS"), start=2):
        if r["SCOPE"] not in SCOPES:
            erreurs.append(f"BRANDS ligne {i} : SCOPE invalide '{r['SCOPE']}'")
        for col in ("TOKEN CATEGORIE REQUIS", "MONTRE DE POCHE ACCEPTEE", "ACTIF"):
            if r[col] not in BOOLS:
                erreurs.append(f"BRANDS ligne {i} : {col} doit valoir TRUE ou FALSE")

        # La colonne ACTIF permet de neutraliser une marque sans supprimer sa
        # ligne, pour tester un elargissement ou un retrecissement du perimetre.
        if r["ACTIF"] != "TRUE":
            continue

        brands.append({
            "name": r["MARQUE"],
            "tier": int(r["TIER"]),
            "aliases": split_terms(r["ALIAS"]),
            # Marques dont le nom est ambigu (Chanel, Cartier, Zodiac) : le mot
            # montre doit etre present dans le titre pour valider la detection.
            "requires_category_token": r["TOKEN CATEGORIE REQUIS"] == "TRUE",
            # Tier 1 ou 2 ET production historique averee de montres de poche.
            "accept_pocket": r["MONTRE DE POCHE ACCEPTEE"] == "TRUE",
            "scope": r["SCOPE"],
        })

    # Tri par longueur de libelle decroissante. C'est ce qui garantit que
    # TAG Heuer est teste avant Heuer, et Grand Seiko avant Seiko. Le scrapper
    # peut donc parcourir la liste dans l'ordre et s'arreter au premier match.
    brands.sort(key=lambda b: -max(len(x) for x in [b["name"]] + b["aliases"]))

    # -----------------------------------------------------------------------
    # CATEGORY_TOKENS. Le mot montre dans chaque langue. Sert a valider les
    # marques ambigues (R4) et a arbitrer les cas conditionnels (R7a).
    # Structure : dictionnaire langue -> liste, car le seul acces est une
    # recherche par langue.
    # -----------------------------------------------------------------------
    category_tokens = {
        r["LANGUE"]: split_terms(r["TERMES"]) for r in read(wb, "CATEGORY_TOKENS")
    }

    # -----------------------------------------------------------------------
    # EXCLUSIONS. HARD rejette immediatement (R1). CONDITIONAL ne rejette que
    # combine a un marqueur d'exclusivite (R5), voir l'onglet MARKERS.
    # Structure : liste, car l'ordre de parcours et les metadonnees comptent.
    # -----------------------------------------------------------------------
    exclusions = []
    for i, r in enumerate(read(wb, "EXCLUSIONS"), start=2):
        if r["SEVERITE"] not in SEVERITES:
            erreurs.append(f"EXCLUSIONS ligne {i} : SEVERITE invalide '{r['SEVERITE']}'")
        if r["SCOPE"] not in SCOPES:
            erreurs.append(f"EXCLUSIONS ligne {i} : SCOPE invalide '{r['SCOPE']}'")
        if r["ACTIF"] != "TRUE":
            continue
        exclusions.append({
            "concept": r["CONCEPT"],
            # AXE est un simple libelle de regroupement. Il n'est jamais lu par
            # l'algorithme de decision, il sert a desactiver une famille entiere
            # le temps d'un test.
            "axis": r["AXE"],
            "severity": r["SEVERITE"],
            "lang": r["LANGUE"],
            "terms": split_terms(r["TERMES"]),
            "scope": r["SCOPE"],
        })

    # -----------------------------------------------------------------------
    # MARKERS. Les trois familles qui decident du sort d'un terme conditionnel.
    # EXCLUSIVITY rejette, NEGATION_CATEGORY rejette, COMPLETENESS conserve.
    # Structure : dictionnaire type -> langue -> liste.
    # -----------------------------------------------------------------------
    markers = {}
    for r in read(wb, "MARKERS"):
        markers.setdefault(r["TYPE"], {})[r["LANGUE"]] = split_terms(r["TERMES"])

    # -----------------------------------------------------------------------
    # ATTRIBUTES. Extraction pure, aucun effet filtrant. Le scrapper les cherche
    # dans toutes les langues a la fois, sans se limiter a la langue de la source.
    # -----------------------------------------------------------------------
    attributes = [{
        "key": r["CLE ATTRIBUT"],
        "group": r["GROUPE"],
        "lang": r["LANGUE"],
        "terms": split_terms(r["TERMES"]),
    } for r in read(wb, "ATTRIBUTES")]

    # -----------------------------------------------------------------------
    # TEST_CASES. Le banc que le runner execute contre l'implementation reelle.
    # Un echec ici doit rendre le build rouge.
    # -----------------------------------------------------------------------
    tests = []
    for i, r in enumerate(read(wb, "TEST_CASES"), start=2):
        if r["VERDICT ATTENDU"] not in VERDICTS:
            erreurs.append(f"TEST_CASES ligne {i} : verdict inconnu '{r['VERDICT ATTENDU']}'")
        tests.append({
            "id": r["ID"],
            "title": r["TITRE DU LOT"],
            "source": r["SOURCE"],
            "source_type": r["TYPE DE SOURCE"],
            "lang": r["LANGUE"],
            "expected": r["VERDICT ATTENDU"],
            # Sans la regle visee, un test rouge dit qu'il echoue mais pas ce
            # qu'il defendait. On la transporte jusqu'au runner.
            "rule": r["REGLE TESTEE"],
            # Un cas de test doit declarer le contexte dans lequel il tourne,
            # exactement comme l'appel reel : R4c ne se declenche que si la
            # source annonce un corpus exclusivement horloger.
            "watch_corpus": r.get("CORPUS HORLOGER") == "TRUE",
            # La categorie telle que la source la publierait, pour les cas qui
            # defendent R0. Vide = la source ne publie pas de categorie.
            "source_category": r.get("CATEGORIE SOURCE"),
        })

    # -----------------------------------------------------------------------
    # Les regles nomment des concepts : ils doivent exister et etre actifs.
    # -----------------------------------------------------------------------
    concepts_actifs = {e["concept"] for e in exclusions}
    for concept, regle in CONCEPTS_REQUIS.items():
        if concept not in concepts_actifs:
            erreurs.append(f"la regle {regle} nomme le concept '{concept}', "
                           f"absent de l'onglet EXCLUSIONS ou entierement inactif "
                           f"— la regle ne se declencherait jamais")
    for famille, regle in MARQUEURS_REQUIS.items():
        if not markers.get(famille):
            erreurs.append(f"la regle {regle} nomme la famille de marqueurs "
                           f"'{famille}', absente de l'onglet MARKERS")

    # -----------------------------------------------------------------------
    # Aucune ecriture tant qu'une erreur de schema subsiste.
    # -----------------------------------------------------------------------
    if erreurs:
        print("BUILD ECHOUE, schema invalide :")
        for e in erreurs:
            print("  -", e)
        sys.exit(1)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_file": str(source),
        # Rappel de la mecanique de matching, pour que le scrapper n'ait pas a
        # la deviner et pour que toute divergence saute aux yeux en revue.
        "matching": {
            "default": "word_boundary",
            "case_insensitive": True,
            # Accents latins uniquement : un NFKD applique aux kana transforme
            # パ en ハ et fait echouer toutes les marques japonaises.
            "accent_insensitive": "latin_only",
            "cjk_autodetect_substring": True,
            "brand_order": "longest_label_first",
            # R4b : une reference dans le titre tient lieu de token de categorie
            # pour les marques a nom ambigu, quel que soit le type de source.
            "reference_counts_as_token": True,
            # R6b : distance maximale, en caracteres, entre un qualificatif
            # descriptif et le terme conditionnel qu'il qualifie.
            "descriptive_window_chars": 30,
        },
        # Regles terminales, celles qu'une implementation peut renvoyer. R7 n'y figure
        # pas : c'est la question dont R7a est la reponse, elle ne conclut jamais seule.
        "rules_order": ["R0", "R1", "R1b", "R2", "R3", "R3b", "R4", "R4b", "R4c", "R5", "R6",
                        "R6b", "R6c", "R7a", "R8"],
        "brands": brands,
        "category_tokens": category_tokens,
        "exclusions": exclusions,
        "markers": markers,
        "attributes": attributes,
        "test_cases": tests,
    }

    with open(destination, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"OK  {destination}")
    print(f"    {len(brands)} marques, {len(exclusions)} exclusions, "
          f"{len(attributes)} attributs, {len(tests)} cas de test")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
