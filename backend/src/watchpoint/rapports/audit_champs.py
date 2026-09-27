"""Ou vivent la REFERENCE et la NATURE DU PRIX, source par source ?

    cd ~/Desktop/WP
    python -m watchpoint rapport audit_champs            # sur le brut deja collecte
    python -m watchpoint rapport audit_champs --fiches   # + echantillon de fiches en ligne

Deux champs decident de la valeur d'une source, et aucun des deux ne porte le
meme nom deux fois : Bezel publie `referenceNumber`, Shopify publie `sku`,
Christie's n'en publie aucun et l'oblige a etre devine dans le titre. Meme
chose pour la nature : `available` chez un marchand, `price_realised_txt`
absent chez une maison de ventes, rien du tout sur un agregateur de forums.

Cette passe ne devine pas : elle ouvre le brut, enumere TOUS les chemins de
cles reellement presents, mesure leur taux de remplissage, et confronte le
resultat a ce que l'adaptateur en fait aujourd'hui. Elle repond a une seule
question, mais pour de vrai : qu'est-ce qui est disponible, et qu'est-ce qui
ne l'est pas ?

Elle ne modifie rien. Elle ecrit un rapport et un JSON, c'est tout.
"""
from __future__ import annotations

from watchpoint import config

import collections
import gzip
import json
import pathlib
import re
import sys


from watchpoint.filtrage.filtre import filtre  # noqa: E402

LABO = config.RACINE
DATA = LABO / "data"
RAPPORT = config.RAPPORTS / "ETAT_CHAMPS.md"
SORTIE = DATA / "audit_champs.json"

# Les noms qu'une reference constructeur peut prendre. La liste vient de ce
# qu'on a rencontre, elle grandira a chaque source branchee.
NOMS_REFERENCE = re.compile(
    r"(?<![a-z])referenc|(?<![a-z])ref(?:no|num|erence)?$|^ref|_ref|modelnumber|model_number|"
    r"modelno|mpn|sku|partnumber|part_number|articlenumber|itemnumber|item_number|"
    r"catalog|caliber_?ref|serie[sn]?number", re.I)

# Les noms qui portent la nature ou le statut d'un prix.
NOMS_NATURE = re.compile(
    r"available|availabilit|instock|in_stock|sold|sale[_]?status|status|state$|"
    r"realis|realiz|hammer|winning|bid|estimate|reserve|withdraw|unsold|passed|"
    r"offer|listing_?status|is_?active|active$|price_?type|condition", re.I)

# Contexte : ce qui aide a lire les deux precedents.
NOMS_PRIX = re.compile(r"price|amount|montant|cents|currency|devise|value$", re.I)
NOMS_DATE = re.compile(r"date|_at$|_ts$|time|created|published|updated|sold_on", re.I)
NOMS_MARQUE = re.compile(r"brand|maker|marque|manufacturer|vendor|designer|artist", re.I)

FAMILLES = [("reference", NOMS_REFERENCE), ("nature", NOMS_NATURE),
            ("prix", NOMS_PRIX), ("date", NOMS_DATE), ("marque", NOMS_MARQUE)]

# Quand la fiche n'a aucune structure, l'information peut quand meme etre ecrite
# en toutes lettres dans le texte. C'est le cas des fils de forum agreges par
# WatchRecon : pas un seul champ, mais "ref. 16610" en clair dans le message.
MOTIF_REFERENCE = re.compile(
    r"(?<!\w)(?:ref|reference|model)\.?\s*(?:no\.?|n[°o]\.?)?\s*[A-Z0-9][\w./-]{2,15}",
    re.I)
MOTIF_VENDU = re.compile(
    r"(?<!\w)(sold|vendu|no longer available|deal pending|sale pending|"
    r"withdrawn|verkauft)(?!\w)", re.I)

# Tous les candidats ne se valent pas. "sold", "available" ou "price_realised"
# tranchent la nature du prix ; "estimate_visible" ou "condition" ne font que
# l'entourer. Le rapport doit citer le premier, pas le second.
POIDS_FORTS = re.compile(
    r"sold|available|availabilit|instock|realis|realiz|hammer|withdraw|unsold|"
    r"passed|sale[_]?status|listing_?status|referenc|^ref|modelnumber|mpn|sku", re.I)

VIDES = (None, "", [], {}, "null", "N/A", "-")


# ---------------------------------------------------------------------------
# Lecture du brut
# ---------------------------------------------------------------------------
def dernier_brut(source: str) -> tuple[pathlib.Path | None, list]:
    """Le brut le plus recent, compresse ou non.

    Les collectes recentes ecrivent en .json.gz ; les anciennes sont en clair.
    On lit les deux, sinon l'historique deja constitue devient invisible.
    """
    dossier = DATA / "raw" / source
    fichiers = sorted([*dossier.glob("*.json"), *dossier.glob("*.json.gz")],
                      key=lambda p: p.name) if dossier.exists() else []
    if not fichiers:
        return None, []
    chemin = fichiers[-1]
    try:
        if chemin.suffix == ".gz":
            with gzip.open(chemin, "rt", encoding="utf-8") as flux:
                return chemin, json.load(flux)
        return chemin, json.loads(chemin.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return chemin, []


def objets_json(payload: str, alerte: list) -> list[dict]:
    """La plus longue liste de dictionnaires trouvee dans la reponse.

    Les API emboitent leur liste utile a des profondeurs variables, et parfois
    sous des noms differents d'un endpoint a l'autre. On ne cherche donc pas un
    nom, on cherche une forme.
    """
    try:
        racine = json.loads(payload)
    except json.JSONDecodeError:
        alerte.append("payload JSON illisible — brut tronque ou reponse HTML")
        return []

    meilleure: list = []

    def marche(noeud):
        nonlocal meilleure
        if isinstance(noeud, list):
            dicts = [x for x in noeud if isinstance(x, dict)]
            if len(dicts) > len(meilleure):
                meilleure = dicts
            for x in noeud:
                marche(x)
        elif isinstance(noeud, dict):
            for v in noeud.values():
                marche(v)

    marche(racine)
    return meilleure or ([racine] if isinstance(racine, dict) else [])


def objets_html(payload: str, alerte: list) -> list[dict]:
    """Ce qu'une page HTML expose de structure : JSON-LD, puis Next.js.

    Une source classee "HTML seul" publie tres souvent un JSON-LD parfait sur
    ses fiches produit. C'est la premiere chose a regarder avant d'ecrire le
    moindre selecteur CSS.
    """
    trouves: list[dict] = []
    for bloc in re.findall(
            r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            payload, re.S | re.I):
        try:
            donnee = json.loads(bloc.strip())
        except json.JSONDecodeError:
            continue
        for item in (donnee if isinstance(donnee, list) else [donnee]):
            if isinstance(item, dict):
                trouves.append(item)
                trouves.extend(x for x in item.get("@graph", []) if isinstance(x, dict))
    if trouves:
        alerte.append(f"JSON-LD present : {len(trouves)} blocs")
        return trouves

    bloc = re.search(r'id="__NEXT_DATA__"[^>]*>(.*?)</script>', payload, re.S)
    if bloc:
        alerte.append("__NEXT_DATA__ present (Next.js)")
        return objets_json(bloc.group(1), [])

    alerte.append("ni JSON-LD ni __NEXT_DATA__ — lecture du DOM")
    return objets_dom(payload, alerte)


def objets_dom(payload: str, alerte: list) -> list[dict]:
    """Dernier recours : la structure repetee du HTML tient lieu de schema.

    Une page de liste est faite de cartes identiques. On repere la classe CSS
    qui se repete, puis on lit chaque carte comme un dictionnaire : la classe
    de chaque element interne devient le nom du champ, son texte la valeur.
    C'est ce que fait deja l'adaptateur WatchRecon a la main ; ici on le fait
    a l'aveugle, pour voir ce qu'il n'exploite pas encore.
    """
    from bs4 import BeautifulSoup

    soupe = BeautifulSoup(payload, "lxml")
    candidats = collections.Counter()
    for element in soupe.find_all(["div", "li", "article", "tr", "section"]):
        for classe_css in element.get("class", []):
            candidats[classe_css] += 1

    meilleure, score_max = None, 0
    for classe_css, nombre in candidats.items():
        if not 4 <= nombre <= 400:
            continue
        elements = soupe.select(f".{classe_css}")[:20]
        # La bonne carte est celle qui porte du texte ET des sous-blocs nommes.
        interne = sum(len(e.select("[class]")) for e in elements) / max(len(elements), 1)
        texte = sum(len(e.get_text(strip=True)) for e in elements) / max(len(elements), 1)
        score = interne * min(texte, 400)
        if score > score_max:
            meilleure, score_max = classe_css, score

    if not meilleure:
        alerte.append("aucun bloc repete identifiable dans le DOM")
        return []

    alerte.append(f"bloc repete : .{meilleure} ({candidats[meilleure]} occurrences)")
    objets = []
    for carte in soupe.select(f".{meilleure}"):
        objet: dict = {}
        for enfant in carte.select("[class]"):
            nom = (enfant.get("class") or [None])[0]
            if not nom:
                continue
            texte = enfant.get_text(" ", strip=True)
            if texte and len(texte) < 300 and nom not in objet:
                objet[nom] = texte
        for lien in carte.select("a[href]")[:3]:
            objet.setdefault("href", lien.get("href"))
        # Les attributs data-* portent souvent l'identifiant et le statut, la ou
        # le texte visible ne les montre pas.
        for enfant in carte.select("[data-status], [data-id], [data-sold], [data-price]"):
            for cle, valeur in enfant.attrs.items():
                if cle.startswith("data-"):
                    objet.setdefault(cle, valeur)
        if objet:
            objets.append(objet)
    return objets


# ---------------------------------------------------------------------------
# Enumeration des chemins de cles
# ---------------------------------------------------------------------------
def aplatir(objet, prefixe="") -> dict:
    """{'variants[].sku': 'ABC'} — les listes sont fusionnees sur un seul niveau."""
    plat = {}
    if isinstance(objet, dict):
        for cle, valeur in objet.items():
            chemin = f"{prefixe}.{cle}" if prefixe else str(cle)
            if isinstance(valeur, (dict, list)):
                plat.update(aplatir(valeur, chemin))
            else:
                plat[chemin] = valeur
    elif isinstance(objet, list):
        for element in objet[:3]:   # 3 suffit pour connaitre la forme
            plat.update(aplatir(element, f"{prefixe}[]"))
    return plat


def profile(objets: list[dict], plafond=400) -> dict:
    """Taux de remplissage et echantillons, chemin par chemin."""
    remplis = collections.Counter()
    vus = collections.Counter()
    echantillons = collections.defaultdict(list)
    for objet in objets[:plafond]:
        plat = aplatir(objet)
        for chemin, valeur in plat.items():
            vus[chemin] += 1
            if valeur not in VIDES:
                remplis[chemin] += 1
                if len(echantillons[chemin]) < 3:
                    texte = str(valeur)
                    echantillons[chemin].append(texte[:60] + ("…" if len(texte) > 60 else ""))
    total = min(len(objets), plafond) or 1
    return {chemin: {"presence": round(100 * vus[chemin] / total),
                     "rempli": round(100 * remplis[chemin] / total),
                     "exemples": echantillons[chemin]}
            for chemin in vus}


def familles(objets: list[dict], mini=5, maxi=3) -> list[tuple[str, list[dict]]]:
    """Regroupe les objets par forme avant de les mesurer.

    Une source expose plusieurs endpoints — un calendrier de ventes et une liste
    de lots n'ont ni les memes cles ni le meme interet. Melanges dans un seul
    profil, chaque famille dilue les taux de remplissage de l'autre et le
    rapport ne veut plus rien dire.
    """
    groupes = collections.defaultdict(list)
    for objet in objets:
        if isinstance(objet, dict):
            groupes[frozenset(list(objet)[:40])].append(objet)
    ordonnes = sorted(groupes.items(), key=lambda kv: -len(kv[1]))
    retenues = []
    for signature, membres in ordonnes[:maxi]:
        if len(membres) < mini:
            continue
        # Un nom lisible : les cles les plus parlantes de la famille.
        parlantes = [c for c in sorted(signature)
                     if re.search(r"title|name|lot|price|id$", str(c), re.I)][:3]
        retenues.append((", ".join(parlantes) or f"{len(signature)} cles", membres))
    return retenues


def classe(profil: dict) -> dict:
    """Range chaque chemin dans la famille qui l'interesse."""
    par_famille = {nom: [] for nom, _ in FAMILLES}
    for chemin, mesure in profil.items():
        feuille = chemin.split(".")[-1].replace("[]", "")
        for nom, motif in FAMILLES:
            if motif.search(feuille):
                par_famille[nom].append({"chemin": chemin, **mesure})
                break
    for nom in par_famille:
        par_famille[nom].sort(key=lambda x: -x["rempli"])
    return par_famille


# ---------------------------------------------------------------------------
# Ce que la base contient reellement, apres normalisation
# ---------------------------------------------------------------------------
def etat_du_cumul() -> dict:
    cumul = DATA / "price_points.jsonl"
    if not cumul.exists():
        return {}
    f = filtre()
    par_source = collections.defaultdict(lambda: {
        "prix": 0,
        "natures": collections.Counter(),
        "provenance_nature": collections.Counter(),
        "statut": collections.Counter(),
        "reference_remplie": 0,
        "provenance_reference": collections.Counter(),
        "verdicts": collections.Counter(),
        "dates": [],
        "sans_montant": 0,
    })
    with cumul.open(encoding="utf-8") as flux:
        for ligne in flux:
            if not ligne.strip():
                continue
            r = json.loads(ligne)
            s = par_source[r["source_id"]]
            s["prix"] += 1
            s["natures"][r.get("price_nature")] += 1
            s["provenance_nature"][r.get("price_nature_provenance") or "non renseignee"] += 1
            s["statut"][r.get("listing_status") or "non renseigne"] += 1
            if r.get("reference"):
                s["reference_remplie"] += 1
                s["provenance_reference"][r.get("reference_provenance") or "non renseignee"] += 1
            if r.get("price_amount") is None:
                s["sans_montant"] += 1
            if r.get("price_date"):
                s["dates"].append(r["price_date"])
            type_source = "AUCTION" if r.get("source_type") == "auction" else "MARKETPLACE"
            s["verdicts"][f.verdict(r.get("title") or "", type_source,
                                    maker=r.get("brand"))["verdict"]] += 1

    resultat = {}
    for source, s in par_source.items():
        dates = sorted(s["dates"])
        resultat[source] = {
            "prix": s["prix"],
            "natures": dict(s["natures"]),
            "provenance_nature": dict(s["provenance_nature"]),
            "statut": dict(s["statut"]),
            "reference_pct": round(100 * s["reference_remplie"] / s["prix"]),
            "provenance_reference": dict(s["provenance_reference"]),
            "verdicts": dict(s["verdicts"]),
            "periode": [dates[0], dates[-1]] if dates else None,
            "sans_montant": s["sans_montant"],
        }
    return resultat


# ---------------------------------------------------------------------------
# Niveau 2 : la fiche. Ce que la page de liste ne dit pas, la fiche le dit.
# ---------------------------------------------------------------------------
def echantillon_fiches(limite=6) -> dict:
    """Ouvre quelques fiches par source et regarde ce qu'elles portent en plus.

    Politesse : 6 fiches par source, 1,5 s entre deux requetes. Le but n'est pas
    de collecter, c'est de savoir ou regarder avant d'ecrire un adaptateur.
    """
    from watchpoint.commun.utils import get

    cumul = DATA / "price_points.jsonl"
    urls = collections.defaultdict(list)
    if cumul.exists():
        with cumul.open(encoding="utf-8") as flux:
            for ligne in flux:
                if not ligne.strip():
                    continue
                r = json.loads(ligne)
                url = r.get("source_url") or ""
                if url.startswith("http"):
                    urls[r["source_id"]].append(url)
    # Les lignes les plus recentes d'abord, et un hote different a chaque fois :
    # les premieres lignes du cumul sont les plus anciennes, et WatchRecon
    # renvoie vers des forums differents dont chacun a sa propre structure.
    for source, liste in urls.items():
        vus, retenues = set(), []
        for url in reversed(liste):
            hote = url.split("/")[2] if "/" in url else url
            if hote in vus and len(vus) > 1:
                continue
            vus.add(hote)
            retenues.append(url)
            if len(retenues) >= limite:
                break
        urls[source] = retenues

    from bs4 import BeautifulSoup

    resultat = {}
    for source, liste in urls.items():
        alerte: list[str] = []
        objets: list[dict] = []
        texte_libre = {"lues": 0, "reference": 0, "vendu": 0, "exemples": []}
        for url in liste:
            try:
                resp = get(url, pause=1.5)
            except Exception as exc:
                alerte.append(f"{type(exc).__name__} sur {url[:60]}")
                continue
            if resp.status_code != 200:
                alerte.append(f"HTTP {resp.status_code} sur {url[:60]}")
                continue
            texte = resp.text
            objets.extend(objets_json(texte, []) if texte.lstrip().startswith(("{", "["))
                          else objets_html(texte, alerte))

            # Quand une fiche n'a aucune structure — un fil de forum, par exemple —
            # la seule question qui reste est : l'information est-elle au moins
            # ecrite quelque part dans le texte ?
            brut = BeautifulSoup(texte, "lxml").get_text(" ", strip=True)[:20000]
            texte_libre["lues"] += 1
            trouve = MOTIF_REFERENCE.search(brut)
            if trouve:
                texte_libre["reference"] += 1
                if len(texte_libre["exemples"]) < 3:
                    texte_libre["exemples"].append(trouve.group(0)[:40])
            if MOTIF_VENDU.search(brut):
                texte_libre["vendu"] += 1
        groupes = familles(objets, mini=2, maxi=2)
        resultat[source] = {
            "fiches_lues": len(liste), "alertes": alerte[:6],
            "texte_libre": texte_libre,
            "familles": [{"nom": nom, "objets": len(membres),
                          "chemins": len(profile(membres)),
                          "champs": classe(profile(membres))}
                         for nom, membres in groupes],
        }
        print(f"  fiches {source} : {len(liste)} lues, "
              f"{len(groupes)} famille(s) d'objets")
    return resultat


# ---------------------------------------------------------------------------
# Rapport
# ---------------------------------------------------------------------------
def tableau(lignes, entetes) -> list[str]:
    sortie = ["| " + " | ".join(entetes) + " |",
              "|" + "|".join("---" for _ in entetes) + "|"]
    sortie += ["| " + " | ".join(str(c) for c in ligne) + " |" for ligne in lignes]
    return sortie


def synthese(audit: dict) -> list[list]:
    """Le verdict par source : la reference et la nature sont-elles disponibles ?

    C'est la seule question que le rapport doit trancher. Tout le reste n'est
    que la preuve qui la soutient.
    """
    lignes = []
    for source in sorted(set(audit["sources"]) | set(audit["cumul"])):
        bloc = audit["sources"].get(source, {})
        base = audit["cumul"].get(source, {})

        # Un nom de classe CSS lu dans le DOM n'est pas un champ publie : il
        # decrit une mise en page, pas une donnee. On ne lui accorde pas le
        # meme credit qu'a une cle de JSON.
        dom_seul = any("lecture du DOM" in a for a in bloc.get("alertes", []))

        meilleur_champ = {"reference": None, "nature": None}
        for famille in bloc.get("familles", []):
            for cle in meilleur_champ:
                for champ in famille["champs"][cle]:
                    if champ["rempli"] < 50:
                        continue
                    note = (2 if POIDS_FORTS.search(
                        champ["chemin"].split(".")[-1].replace("[]", "")) else 1,
                        champ["rempli"])
                    actuel = meilleur_champ[cle]
                    if actuel is None or note > actuel["_note"]:
                        meilleur_champ[cle] = {**champ, "_note": note}

        ref = meilleur_champ["reference"]
        if ref and not dom_seul:
            etat_ref = f"champ publié `{ref['chemin']}` ({ref['rempli']} %)"
        elif base.get("reference_pct", 0) >= 10:
            provenances = base.get("provenance_reference", {})
            comment = " · ".join(sorted(provenances)) or "inconnue"
            etat_ref = f"devinée dans le titre — {base['reference_pct']} % ({comment})"
        elif base:
            etat_ref = f"absente — {base.get('reference_pct', 0)} %"
        elif bloc.get("familles"):
            etat_ref = "aucun champ publié dans le brut"
        else:
            etat_ref = "non mesurable, pas de brut lisible"

        nat = meilleur_champ["nature"]
        provenances = base.get("provenance_nature", {})
        if nat and not dom_seul:
            etat_nat = f"statut publié `{nat['chemin']}` ({nat['rempli']} %)"
        elif "deduite_statut" in provenances:
            etat_nat = "déduite du statut de l'annonce"
        elif provenances:
            etat_nat = "déclarée par l'adaptateur, jamais vérifiée"
        elif nat:
            etat_nat = f"lu dans le DOM : `{nat['chemin']}`, à confirmer sur la fiche"
        else:
            etat_nat = "non mesurable"

        lignes.append([source, etat_ref, etat_nat])
    return lignes


def redige(audit: dict) -> str:
    import datetime as dt

    L = [f"# Où vivent la référence et la nature du prix",
         "",
         f"**Généré le {dt.date.today().isoformat()}** par `python -m watchpoint rapport audit_champs` — "
         "ne pas éditer à la main, ce fichier est écrasé à chaque exécution.",
         "",
         "Deux champs décident de la valeur d'une source. Aucun des deux ne porte le même "
         "nom deux fois de suite, et aucun n'est garanti. Ce rapport mesure ce qui est "
         "réellement disponible, source par source, dans le brut lui-même.",
         ""]

    L += ["## En un coup d'œil", ""]
    L += tableau(synthese(audit), ["Source", "La référence", "La nature du prix"])
    L += ["",
          "Lecture : un champ publié par la source est fiable ; une valeur devinée "
          "dans le titre porte un taux d'erreur ; une nature déclarée par "
          "l'adaptateur ne sait pas distinguer un lot vendu d'un lot invendu.",
          ""]

    cumul = audit["cumul"]
    if cumul:
        L += ["## 1. Ce que la base contient aujourd'hui", ""]
        lignes = []
        for source, s in sorted(cumul.items()):
            natures = " · ".join(f"{n} {c}" for n, c in sorted(s["natures"].items()))
            periode = f"{s['periode'][0]} → {s['periode'][1]}" if s["periode"] else "sans date"
            lignes.append([source, s["prix"], natures, f"{s['reference_pct']} %", periode])
        L += tableau(lignes, ["Source", "Prix", "Natures", "Référence", "Période"])
        L += [""]

        L += ["### La nature du prix : déclarée ou mesurée ?", "",
              "Une nature déclarée une fois pour toutes dans l'adaptateur ne distingue "
              "ni un lot invendu d'un lot vendu, ni une montre en vitrine d'une montre partie.",
              ""]
        lignes = []
        for source, s in sorted(cumul.items()):
            prov = " · ".join(f"{p} {c}" for p, c in sorted(s["provenance_nature"].items()))
            statut = " · ".join(f"{p} {c}" for p, c in sorted(s["statut"].items()))
            lignes.append([source, prov, statut, s["sans_montant"]])
        L += tableau(lignes, ["Source", "Provenance de la nature", "Statut de l'annonce",
                              "Sans montant"])
        L += [""]

        L += ["### La référence : publiée, devinée, ou absente ?", ""]
        lignes = []
        for source, s in sorted(cumul.items()):
            prov = " · ".join(f"{p} {c}" for p, c in sorted(s["provenance_reference"].items())) or "aucune"
            lignes.append([source, f"{s['reference_pct']} %", prov])
        L += tableau(lignes, ["Source", "Référence remplie", "Provenance"])
        L += [""]

        L += ["### Ce que le filtre ferait de cette base", ""]
        lignes = []
        for source, s in sorted(cumul.items()):
            v = s["verdicts"]
            total = sum(v.values()) or 1
            lignes.append([source, v.get("GARDER", 0), v.get("REJETER", 0),
                           v.get("QUARANTAINE", 0),
                           f"{round(100 * v.get('GARDER', 0) / total)} %"])
        L += tableau(lignes, ["Source", "Garder", "Rejeter", "Quarantaine", "% gardé"])
        L += [""]

    L += ["## 2. Ce que le brut expose, champ par champ", "",
          "Enumération de tous les chemins de clés réellement présents dans la dernière "
          "réponse de chaque source, avec leur taux de remplissage mesuré.", ""]

    for source, bloc in sorted(audit["sources"].items()):
        L += [f"### {source}", ""]
        L += [f"- brut lu : `{bloc['fichier']}` ({bloc['requetes']} requêtes)",
              f"- {bloc['objets']} objets analysés"]
        for a in bloc["alertes"][:4]:
            L += [f"- {a}"]
        L += [""]
        if not bloc["familles"]:
            L += ["Aucune famille d'objets exploitable dans ce brut.", ""]
        for famille in bloc["familles"]:
            L += [f"**Famille `{famille['nom']}`** — {famille['objets']} objets, "
                  f"{famille['chemins']} chemins de clés", ""]
            for cle, titre in (("reference", "Candidats RÉFÉRENCE"),
                               ("nature", "Candidats NATURE ou STATUT")):
                champs = famille["champs"][cle][:8]
                if not champs:
                    L += [f"*{titre}* — aucun champ candidat.", ""]
                    continue
                L += [f"*{titre}*", ""]
                L += tableau([[f"`{c['chemin']}`", f"{c['rempli']} %",
                               " · ".join(c["exemples"][:2]) or "—"] for c in champs],
                             ["Champ", "Rempli", "Exemples"])
                L += [""]

    L += ["## 3. La structure complète, source par source", "",
          "Tout ce que la source publie, pas seulement ce qu'on en tire aujourd'hui. "
          "C'est là qu'on voit ce qu'on laisse sur la table.", ""]
    for source, bloc in sorted(audit["sources"].items()):
        for famille in bloc["familles"]:
            if not famille.get("tous"):
                continue
            L += [f"<details><summary><b>{source}</b> — famille "
                  f"<code>{famille['nom']}</code>, {famille['chemins']} champs"
                  f"</summary>", ""]
            L += tableau([[f"`{c['chemin']}`", f"{c['rempli']} %",
                           " · ".join(c["exemples"][:1]) or "—"]
                          for c in famille["tous"][:45]],
                         ["Champ", "Rempli", "Exemple"])
            L += ["", "</details>", ""]

    if audit.get("fiches"):
        L += ["## 4. Ce que la fiche ajoute à la page de liste", "",
              "Une source classée « pauvre » sur sa page de liste publie souvent tout "
              "ce qu'il faut sur ses fiches produit. Échantillon réel.", ""]
        for source, bloc in sorted(audit["fiches"].items()):
            L += [f"### {source} — {bloc['fiches_lues']} fiches lues", ""]
            for a in bloc["alertes"][:4]:
                L += [f"- {a}"]
            libre = bloc.get("texte_libre") or {}
            if libre.get("lues"):
                L += ["",
                      f"**En texte libre**, sur {libre['lues']} fiches lues : "
                      f"{libre['reference']} portent une référence, "
                      f"{libre['vendu']} portent une marque de vente conclue.",
                      ""]
                if libre.get("exemples"):
                    L += ["Références repérées : "
                          + " · ".join(f"`{e}`" for e in libre["exemples"]), ""]
            L += [""]
            for famille in bloc["familles"]:
                L += [f"**Famille `{famille['nom']}`** — {famille['objets']} objets", ""]
                for cle, titre in (("reference", "Candidats RÉFÉRENCE"),
                                   ("nature", "Candidats NATURE ou STATUT")):
                    champs = famille["champs"][cle][:6]
                    if champs:
                        L += [f"*{titre}*", ""]
                        L += tableau([[f"`{c['chemin']}`", f"{c['rempli']} %",
                                       " · ".join(c["exemples"][:2]) or "—"] for c in champs],
                                     ["Champ", "Rempli", "Exemples"])
                        L += [""]

    return "\n".join(L) + "\n"


def main() -> None:
    audit = {"sources": {}, "cumul": {}, "fiches": {}}

    print("brut, source par source :")
    for dossier in sorted((DATA / "raw").iterdir()) if (DATA / "raw").exists() else []:
        if not dossier.is_dir():
            continue
        source = dossier.name
        chemin, entrees = dernier_brut(source)
        if not entrees:
            print(f"  {source} : aucun brut lisible")
            continue
        alerte: list[str] = []
        objets: list[dict] = []
        for entree in entrees:
            payload = entree.get("payload", "") if isinstance(entree, dict) else ""
            if not payload:
                continue
            if payload.lstrip()[:1] in ("{", "["):
                objets.extend(objets_json(payload, alerte))
            else:
                objets.extend(objets_html(payload, alerte))
        groupes = familles(objets)
        blocs = []
        for nom, membres in groupes:
            profil = profile(membres)
            blocs.append({
                "nom": nom, "objets": len(membres), "chemins": len(profil),
                "champs": classe(profil),
                # La structure complete, pour pouvoir juger de ce qu'on n'exploite
                # pas encore : une source ne se resume pas a deux champs.
                "tous": sorted(({"chemin": c, **m} for c, m in profil.items()),
                               key=lambda x: (-x["rempli"], x["chemin"])),
            })
        audit["sources"][source] = {
            "fichier": chemin.name if chemin else None,
            "requetes": len(entrees),
            "objets": len(objets),
            "alertes": sorted(set(alerte)),
            "familles": blocs,
        }
        print(f"  {source} : {len(objets)} objets, "
              f"{len(groupes)} famille(s) d'objets")

    print("\ncumul normalise :")
    audit["cumul"] = etat_du_cumul()
    for source, s in sorted(audit["cumul"].items()):
        print(f"  {source} : {s['prix']} prix, reference {s['reference_pct']} %, "
              f"natures {s['natures']}")

    if "--fiches" in sys.argv:
        print("\nechantillon de fiches en ligne :")
        audit["fiches"] = echantillon_fiches()

    SORTIE.write_text(json.dumps(audit, ensure_ascii=False, indent=1), encoding="utf-8")
    RAPPORT.write_text(redige(audit), encoding="utf-8")
    print(f"\n-> {RAPPORT}")
    print(f"-> {SORTIE}")


if __name__ == "__main__":
    main()
