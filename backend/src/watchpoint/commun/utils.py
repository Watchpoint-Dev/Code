"""Utilitaires communs pour le labo data-sourcing.

Import depuis un script de source :

    import sys, pathlib
    from watchpoint.commun.utils import get, save_html, save_json, SAMPLES
"""
from __future__ import annotations

from watchpoint import config

import json
import time
import pathlib
import requests

# On s'identifie POUR CE QU'ON EST. L'en-tete a longtemps annonce Chrome, et
# cela s'est retourne contre nous deux fois : Christie's paraissait nous bloquer
# alors qu'elle bloquait le faux navigateur (0,05 s avec un UA honnete contre
# 20 s d'expiration), et DavidSW nous rangeait sous `User-agent: *` — qui
# interdit son API — alors que son robots.txt autorise ClaudeBot en toutes
# lettres sur son catalogue.
#
# La contrepartie est entiere et assumee : s'annoncer ClaudeBot, c'est aussi
# devoir obeir aux regles qui visent ClaudeBot, quand elles existent. Un en-tete
# honnete n'est pas une cle, c'est une signature.
#
# CETTE NOTE PORTAIT UN EXEMPLE FAUX, corrige le 21/09/2026. Elle affirmait que
# Watches of Knightsbridge porte `User-agent: ClaudeBot / Disallow: /` et que la
# source nous etait donc fermee « et le resterait ». Relecture du fichier servi
# ce jour, 77 octets en tout :
#
#     User-agent: *
#     Disallow: /p/watches/?filter_
#     Disallow: /p/watches/?query_type_
#
# Aucune regle ClaudeBot. Le 403 venait d'un filtre d'UA de son pare-feu, pas
# d'une consigne du site — et la source est bien accessible. Une note de ce
# genre ecarte une source sans que personne ne la reverifie : un constat sur le
# robots.txt d'un tiers se date, et se relit.
#
# Le meme UA se retourne d'ailleurs contre nous ailleurs : mesure du 21/09/2026,
# 19 sources sur 69 repondaient 403 a ClaudeBot et 200 a l'UA par defaut de la
# bibliotheque. `qualite/sonde.py` utilise donc le sien, et non celui-ci.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; ClaudeBot/1.0; "
        "+claudebot@anthropic.com)"
    ),
    "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
}


# Codes qui disent "reviens plus tard", pas "n'insiste pas". 503 et 429 sont du
# bridage : Shopify a renvoye 503 sur la premiere page d'un catalogue de 2 000
# produits, et sans reprise la source entiere est rentree vide.
CODES_A_REESSAYER = {429, 500, 502, 503, 504}
ATTENTES = (3, 9, 27)   # secondes, doublees a chaque nouvel essai
DELAIS = (10, 20)       # (connexion, lecture) passes a requests
PLAFOND_LECTURE = 45    # duree totale maximale d'une reponse, sans rearmement


def get(url: str, *, params: dict | None = None, pause: float = 1.0,
        essais: int = 3, **kwargs) -> requests.Response:
    """GET poli, avec reprise : en-tetes navigateur, pause, et 3 essais.

    Une seule requete qui expire ne doit pas coûter une source entiere. Un
    ReadTimeout sur le calendrier de Christie's a fait rentrer 0 lot la ou 7 ans
    de resultats etaient accessibles — et l'exception a emporte avec elle tout
    le brut deja telecharge.

    L'attente respecte l'en-tete Retry-After quand le serveur en envoie un.
    """
    entetes = {**HEADERS, **kwargs.pop("headers", {})}
    derniere_erreur = None
    for essai in range(essais):
        try:
            # (connexion, lecture). Le timeout de lecture se REARME a chaque
            # octet recu : un site qui repond au compte-gouttes — Christie's le
            # fait apres quelques centaines de requetes — peut tenir la
            # connexion des minutes malgre un timeout de 20 s. D'ou la limite
            # dure ci-dessous, qui elle ne se rearme jamais.
            resp = requests.get(url, headers=entetes, params=params,
                                timeout=DELAIS, stream=True, **kwargs)
            debut = time.monotonic()
            morceaux = []
            for morceau in resp.iter_content(65536):
                morceaux.append(morceau)
                if time.monotonic() - debut > PLAFOND_LECTURE:
                    resp.close()
                    raise requests.Timeout(
                        f"lecture au-dela de {PLAFOND_LECTURE} s — le site nous ralentit")
            resp._content = b"".join(morceaux)
            resp._content_consumed = True
        except requests.RequestException as exc:
            derniere_erreur = exc
            if essai == essais - 1:
                raise
            time.sleep(ATTENTES[min(essai, len(ATTENTES) - 1)])
            continue

        if resp.status_code in CODES_A_REESSAYER and essai < essais - 1:
            attente = ATTENTES[min(essai, len(ATTENTES) - 1)]
            entete = resp.headers.get("Retry-After")
            if entete and str(entete).isdigit():
                attente = max(attente, min(int(entete), 60))
            time.sleep(attente)
            continue

        time.sleep(pause)  # on reste gentil avec le site
        return resp

    # Inatteignable en pratique : la boucle rend ou leve avant d'arriver ici.
    raise derniere_erreur or RuntimeError(f"echec apres {essais} essais : {url}")


def samples_dir(script_file: str) -> pathlib.Path:
    """Dossier samples/ a cote du script appelant."""
    d = pathlib.Path(script_file).resolve().parent / "samples"
    d.mkdir(exist_ok=True)
    return d


def save_text(path: pathlib.Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    print(f"  -> sauvegarde {path.name} ({len(text):,} caracteres)")


def save_json(path: pathlib.Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  -> sauvegarde {path.name} ({len(data) if hasattr(data,'__len__') else '?'} elements)")


# Les onglets sous lesquels un classeur de registre range ses 210 sources. Le
# nom change d'une campagne a l'autre : 'Toutes les sources' dans DataSources,
# 'Decision' dans DECISION_SOURCES, 'Sources' dans WatchDataSources_v3.
ONGLETS_REGISTRE = ("Toutes les sources", "Décision", "Decision", "Registre 210",
                    "Sources", "Diagnostic 200")


def registre_sources() -> tuple[pathlib.Path, str] | None:
    """(classeur, onglet) du registre des 210 sources, ou qu'il soit rendu.

    Ce fichier porte un nom DATE et descend en `_archive/` a la fin de chaque
    campagne — c'est la regle du projet. Trois modules le cherchaient pourtant a
    un chemin fixe, `docs/livrables/referentiels/DataSources.xlsx`, et `sonde.py
    --registre` s'arretait net depuis qu'il avait ete archive le 01/08/2026 :
    une commande documentee dans le README ne marchait plus.

    On rend aussi l'ONGLET, parce que le resoudre separement ne servait a rien :
    DECISION_SOURCES existe mais ne porte pas 'Toutes les sources', et un
    resolveur qui rend un classeur illisible ne vaut pas mieux qu'un chemin mort.

    None plutot qu'une exception : l'appelant sait mieux que nous si le registre
    lui est indispensable.
    """
    import openpyxl

    racine = config.RACINE
    ref = config.REFERENTIELS
    candidats = [
        ref / "DataSources.xlsx",
        *sorted(ref.glob("DECISION_SOURCES*.xlsx"), reverse=True),
        *sorted(ref.glob("*SOURCES*.xlsx"), reverse=True),
        *sorted(racine.glob("_archive/*/DataSources.xlsx"), reverse=True),
    ]
    for chemin in candidats:
        if not chemin.exists():
            continue
        try:
            classeur = openpyxl.load_workbook(chemin, read_only=True)
            presents = set(classeur.sheetnames)
            classeur.close()
        except Exception:
            continue
        for onglet in ONGLETS_REGISTRE:
            if onglet in presents:
                return chemin, onglet
    return None
