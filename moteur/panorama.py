"""Le panorama — toutes les sources, tout le brut, tout ce que le filtre en fait.

    cd ~/Desktop/WP/labo
    shared/.venv/bin/python moteur/panorama.py

Un seul document, genere, qui repond aux questions qu'on pose toujours dans cet
ordre : quelles sources avons-nous, combien de brut, ce que le filtre en garde,
quelles natures de prix, combien de references, et quelle profondeur historique.

Il ne mesure rien de nouveau : il lit ce que la collecte a deja inscrit — le
verdict du filtre appose a l'ingestion, la provenance de la nature et celle de
la reference. Si un chiffre bouge ici sans qu'on ait touche au code, c'est une
source qui a change, pas le rapport.

Les reserves connues de chaque source voyagent avec elle. Une source dont les
prix melangent TTC et HT reste utilisable pour compter des references, pas pour
comparer des niveaux de prix : le tableau doit le dire a cote du chiffre, pas
dans une note de bas de page que personne ne lit.
"""
from __future__ import annotations

import collections
import datetime as dt
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "shared"))

import sources  # noqa: E402

LABO = pathlib.Path(__file__).resolve().parent.parent
DATA = LABO / "data"
CUMUL = DATA / "price_points.jsonl"
RAPPORT = LABO.parent / "notes" / "PANORAMA.md"

NATURES_LISIBLES = {
    "realised": "réalisé (marteau)",
    "sold": "vendu",
    "asking": "demandé",
    "estimate": "estimation",
    "msrp": "prix neuf",
}
TYPES_LISIBLES = {
    "auction": "maison de ventes",
    "dealer": "marchand",
    "marketplace": "marketplace",
    "community": "forums",
    "aggregator": "agrégateur",
}


def milliers(n) -> str:
    return f"{n:,}".replace(",", " ")


def tableau(lignes, entetes) -> list[str]:
    return ["| " + " | ".join(entetes) + " |",
            "|" + "|".join("---" for _ in entetes) + "|"] + \
           ["| " + " | ".join(str(c) for c in ligne) + " |" for ligne in lignes]


def volume_brut() -> dict:
    """Ce qui dort sur le disque, source par source : fichiers, poids, requetes.

    Le brut est la matiere premiere : c'est lui qui permet de rejouer un filtre
    corrige sans redemander une seule page. Savoir combien on en a est donc une
    mesure de capacite, pas une curiosite.
    """
    mesures = {}
    racine = DATA / "raw"
    if not racine.exists():
        return mesures
    for dossier in sorted(racine.iterdir()):
        if not dossier.is_dir():
            continue
        fichiers = [*dossier.glob("*.json"), *dossier.glob("*.json.gz")]
        if not fichiers:
            continue
        octets = sum(f.stat().st_size for f in fichiers)
        dates = sorted(f.name[:10] for f in fichiers)
        mesures[dossier.name] = {
            "collectes": len(fichiers),
            "poids_mo": round(octets / 1_048_576, 1),
            "premiere": dates[0], "derniere": dates[-1],
            "compresse": sum(1 for f in fichiers if f.suffix == ".gz"),
        }
    return mesures


def requetes_par_source() -> dict:
    """Le nombre de requetes HTTP du dernier run de chaque source."""
    mesures = {}
    dossier = DATA / "runs"
    if not dossier.exists():
        return mesures
    for chemin in sorted(dossier.glob("*.json")):
        try:
            manifeste = json.loads(chemin.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        for s in manifeste.get("sources", []):
            if s.get("records"):
                journal = s.get("journal", [])
                # Une collecte plafonnee ou echantillonnee n'est pas un total.
                # Le dire a cote du chiffre, pas dans une note de bas de page.
                partielle = next(
                    (l for l in journal
                     if str(l).startswith("TRONQUE") or "retenues sur" in str(l)), None)
                mesures[s["id"]] = {"requetes": s.get("requetes_http"),
                                    "run": manifeste.get("run", "")[:10],
                                    "partielle": partielle, "journal": journal}
    return mesures


def lire_cumul() -> dict:
    """Tout ce que le cumul sait dire, agrege par source, en une seule passe."""
    par_source = collections.defaultdict(lambda: {
        "prix": 0,
        "natures": collections.Counter(),
        "provenance_nature": collections.Counter(),
        "verdicts": collections.Counter(),
        "regles": collections.Counter(),
        "reference": 0,
        "provenance_reference": collections.Counter(),
        "devises": collections.Counter(),
        "annees": collections.Counter(),
        "marque": 0,
        "montants": [],
    })
    if not CUMUL.exists():
        return par_source

    with CUMUL.open(encoding="utf-8") as flux:
        for ligne in flux:
            if not ligne.strip():
                continue
            r = json.loads(ligne)
            s = par_source[r["source_id"]]
            s["prix"] += 1
            s["natures"][r.get("price_nature")] += 1
            s["provenance_nature"][r.get("price_nature_provenance") or "non renseignée"] += 1
            s["verdicts"][r.get("filter_verdict") or "non filtré"] += 1
            if r.get("filter_verdict") and r["filter_verdict"] != "GARDER":
                s["regles"][f"{r['filter_verdict']} {r.get('filter_rule')}"] += 1
            if r.get("reference"):
                s["reference"] += 1
                s["provenance_reference"][r.get("reference_provenance") or "non renseignée"] += 1
            if r.get("reference_provenance") in ("champ_dedie", "extrait_titre",
                                                 "extrait_description"):
                s["reference_sure"] = s.get("reference_sure", 0) + 1
            if r.get("brand"):
                s["marque"] += 1
            if r.get("price_currency"):
                s["devises"][r["price_currency"]] += 1
            if r.get("price_date"):
                s["annees"][str(r["price_date"])[:4]] += 1
            if r.get("price_amount"):
                s["montants"].append(r["price_amount"])
    return par_source


def redige(cumul, brut, runs) -> str:
    metas = {m.SOURCE["id"]: m.SOURCE for m in sources.ALL}
    actives = {s: d for s, d in cumul.items() if d["prix"]}
    total_prix = sum(d["prix"] for d in actives.values())
    total_garde = sum(d["verdicts"].get("GARDER", 0) for d in actives.values())
    total_quarantaine = sum(d["verdicts"].get("QUARANTAINE", 0) for d in actives.values())
    total_rejet = sum(d["verdicts"].get("REJETER", 0) for d in actives.values())
    non_filtre = sum(d["verdicts"].get("non filtré", 0) for d in actives.values())
    poids = sum(b["poids_mo"] for b in brut.values())
    annees = collections.Counter()
    for d in actives.values():
        annees.update(d["annees"])

    L = ["# Panorama des sources", "",
         f"**Généré le {dt.date.today().isoformat()}** par "
         "`python moteur/panorama.py` — ne pas éditer à la main, ce fichier est "
         "écrasé à chaque exécution.", ""]

    L += ["## En un coup d'œil", "",
          f"- **{milliers(total_prix)} prix** collectés, sur **{len(actives)} sources** "
          f"qui rendent des données ({len(metas)} adaptateurs écrits)",
          f"- **{milliers(total_garde)} gardés** par le filtre "
          f"({round(100 * total_garde / max(total_prix, 1))} %), "
          f"{milliers(total_rejet)} rejetés, {milliers(total_quarantaine)} en quarantaine",
          f"- **{poids:.0f} Mo de brut** conservé sur le disque, rejouable sans "
          f"une seule requête réseau",
          f"- période couverte : **{min(annees, default='—')} → {max(annees, default='—')}**",
          ""]
    if non_filtre:
        L += [f"- {milliers(non_filtre)} lignes n'ont pas de verdict : elles ont été "
              f"collectées avant que le filtre soit apposé à l'ingestion. "
              f"`moteur/filtre.py --base` les évalue à la volée.", ""]

    # ---- 1. les sources
    L += ["## 1. Les sources", ""]
    lignes = []
    for source, d in sorted(actives.items(), key=lambda kv: -kv[1]["prix"]):
        meta = metas.get(source, {})
        b = brut.get(source, {})
        r = runs.get(source, {})
        nature = " · ".join(f"{NATURES_LISIBLES.get(n, n)}"
                            for n, _ in d["natures"].most_common(2))
        lignes.append([
            f"**{meta.get('name', source)}**",
            TYPES_LISIBLES.get(meta.get("type"), meta.get("type", "—")),
            milliers(d["prix"]),
            nature,
            f"{min(d['annees'], default='—')} → {max(d['annees'], default='—')}",
            f"{b.get('poids_mo', 0)} Mo",
            "partielle" if r.get("partielle") else "complète",
        ])
    L += tableau(lignes, ["Source", "Type", "Prix", "Nature dominante",
                          "Période", "Brut", "Collecte"])
    partielles = [(metas.get(s, {}).get("name", s), runs[s]["partielle"])
                  for s in actives if runs.get(s, {}).get("partielle")]
    if partielles:
        L += ["", "**Les collectes marquées partielles ne sont pas des totaux.** "
              "Ce qui les a arrêtées, mot pour mot :", ""]
        L += tableau([[nom, f"`{texte}`"] for nom, texte in partielles],
                     ["Source", "Ce que le collecteur a inscrit"])

    L += ["", "Les adaptateurs écrits mais qui ne rendent rien aujourd'hui :", ""]
    muettes = [(m.SOURCE["id"], m.SOURCE) for m in sources.ALL
               if m.SOURCE["id"] not in actives]
    if muettes:
        L += tableau([[f"**{meta.get('name', sid)}**",
                       TYPES_LISIBLES.get(meta.get("type"), "—"),
                       meta.get("statut") or "adaptateur écrit, collecte pas encore aboutie"]
                      for sid, meta in muettes],
                     ["Source", "Type", "Pourquoi"])
    L += [""]

    # ---- 2. le filtre
    L += ["## 2. Ce que le filtre en fait", "",
          "Le filtre est apposé à l'ingestion : chaque ligne porte son verdict, la "
          "règle qui l'a produit et la version du filtre utilisée. Rien n'est "
          "supprimé — corriger le filtre et rejouer l'historique ne coûte aucune "
          "requête.", ""]
    lignes = []
    for source, d in sorted(actives.items(), key=lambda kv: -kv[1]["prix"]):
        v = d["verdicts"]
        connus = v.get("GARDER", 0) + v.get("REJETER", 0) + v.get("QUARANTAINE", 0)
        if not connus:
            continue
        lignes.append([metas.get(source, {}).get("name", source),
                       milliers(v.get("GARDER", 0)),
                       milliers(v.get("REJETER", 0)),
                       milliers(v.get("QUARANTAINE", 0)),
                       f"{round(100 * v.get('GARDER', 0) / connus)} %"])
    if lignes:
        L += tableau(lignes, ["Source", "Gardé", "Rejeté", "Quarantaine", "% gardé"])
    L += [""]

    regles = collections.Counter()
    for d in actives.values():
        regles.update(d["regles"])
    if regles:
        L += ["### Pourquoi une ligne ne passe pas", ""]
        L += tableau([[f"`{regle}`", milliers(n)] for regle, n in regles.most_common(10)],
                     ["Verdict et règle", "Lignes"])
        L += ["",
              "R3 = aucune marque connue dans le titre · R4 = marque au nom ambigu "
              "sans le mot montre · R1 = objet qui n'est pas une montre · "
              "R7a = le texte ne tranche pas, mise en quarantaine.", ""]

    # ---- 3. les natures de prix
    L += ["## 3. Les natures de prix", "",
          "C'est la question qui décide de ce qu'on peut afficher. Un prix demandé "
          "est une opinion de vendeur ; un prix réalisé est une transaction.", ""]
    natures = collections.Counter()
    for d in actives.values():
        natures.update(d["natures"])
    L += tableau([[NATURES_LISIBLES.get(n, n), milliers(c),
                   f"{round(100 * c / max(total_prix, 1))} %"]
                  for n, c in natures.most_common()],
                 ["Nature", "Prix", "Part"])
    L += [""]

    L += ["### Déclarée ou mesurée ?", "",
          "Une nature déclarée une fois pour toutes dans l'adaptateur ne distingue "
          "ni un lot invendu d'un lot vendu, ni une montre en vitrine d'une montre "
          "partie. Une nature déduite du statut de l'annonce, si.", ""]
    lignes = []
    for source, d in sorted(actives.items(), key=lambda kv: -kv[1]["prix"]):
        lignes.append([metas.get(source, {}).get("name", source),
                       " · ".join(f"{NATURES_LISIBLES.get(n, n)} {milliers(c)}"
                                  for n, c in d["natures"].most_common()),
                       " · ".join(f"{p} {milliers(c)}"
                                  for p, c in d["provenance_nature"].most_common())])
    L += tableau(lignes, ["Source", "Natures", "Provenance"])
    L += [""]

    # ---- 4. la reference
    L += ["## 4. La référence", "",
          "Elle n'est pas un critère de filtrage — un prix sans référence reste une "
          "observation de marché valide. Elle est le crochet d'identité entre une "
          "annonce et une montre : sans elle, on a un prix mais pas de quoi, et on "
          "ne peut pas construire l'objet Watch.", ""]
    lignes = []
    total_ref = total_sure = 0
    for source, d in sorted(actives.items(), key=lambda kv: -kv[1]["prix"]):
        total_ref += d["reference"]
        sure = d.get("reference_sure", 0)
        total_sure += sure
        lignes.append([
            metas.get(source, {}).get("name", source),
            f"{round(100 * d['reference'] / max(d['prix'], 1))} %",
            f"**{round(100 * sure / max(d['prix'], 1))} %**",
            f"{round(100 * d['marque'] / max(d['prix'], 1))} %",
            " · ".join(f"{p} {milliers(c)}"
                       for p, c in d["provenance_reference"].most_common()) or "aucune",
        ])
    L += tableau(lignes, ["Source", "Un identifiant", "Dont référence constructeur",
                          "Avec marque", "D'où il vient"])
    L += ["",
          f"**{milliers(total_ref)} prix sur {milliers(total_prix)} portent un "
          f"identifiant ({round(100 * total_ref / max(total_prix, 1))} %), mais "
          f"seulement {milliers(total_sure)} portent une vraie référence "
          f"constructeur ({round(100 * total_sure / max(total_prix, 1))} %).** "
          "La différence n'est pas cosmétique. Un SKU est un numéro d'inventaire "
          "de marchand — `P-O 82172/000P-H062` chez Berry's — et une référence "
          "lue dans le corps de l'annonce peut être un calibre ou un numéro de "
          "boîtier. Une source affichant 100 % d'identifiants peut n'avoir aucune "
          "référence exploitable : c'est le cas de CW Sellors et de Montredo.", ""]

    # ---- 5. la profondeur
    L += ["## 5. La profondeur historique", "",
          "Attention à ce que la date signifie : chez une maison de ventes c'est le "
          "jour du marteau, chez un marchand c'est la mise en ligne de l'annonce. "
          "La seconde ne date pas une transaction.", ""]
    lignes = []
    for annee in sorted(annees, reverse=True):
        if int(annee) < 1990:
            continue
        part = collections.Counter()
        for source, d in actives.items():
            if d["annees"].get(annee):
                part[metas.get(source, {}).get("name", source)] = d["annees"][annee]
        lignes.append([annee, milliers(annees[annee]),
                       " · ".join(f"{s} {milliers(c)}" for s, c in part.most_common(3))])
    L += tableau(lignes, ["Année", "Prix", "Principales sources"])
    L += [""]

    # ---- 6. devises
    devises = collections.Counter()
    for d in actives.values():
        devises.update(d["devises"])
    L += ["## 6. Les devises", "",
          "Aucune conversion n'est appliquée : les montants sont ceux de la source. "
          "**Ne jamais comparer deux lignes de devises différentes.**", ""]
    L += tableau([[d, milliers(c)] for d, c in devises.most_common()],
                 ["Devise", "Prix"])
    L += [""]

    # ---- 7. les reserves
    L += ["## 7. Les réserves connues", "",
          "Ce que chaque source ne peut pas dire, ou dit mal. À lire avant toute "
          "analyse qui s'appuie sur elle.", ""]
    reserves = [[metas[s].get("name", s), metas[s]["reserve"]]
                for s in actives if metas.get(s, {}).get("reserve")]
    if reserves:
        L += tableau(reserves, ["Source", "Réserve"])
    else:
        L += ["Aucune réserve enregistrée sur les sources actives.", ""]
    L += ["",
          "S'y ajoutent trois réserves transverses, et la première est la plus "
          "coûteuse. **Deux maisons de ventes ne publient pas la même chose** : "
          "Christie's affiche le prix frais acheteur inclus, Artcurial et Lyon & "
          "Turnbull le marteau nu. L'écart est d'environ un quart. Le champ "
          "`price_includes_premium` porte l'information ligne par ligne — toute "
          "comparaison entre maisons qui l'ignore surévalue Christie's. "
          "**Les invendus sont invisibles** "
          "chez les maisons de ventes qui ne servent que leurs lots vendus : toute "
          "moyenne héritera d'un biais de survie. **La date d'un marchand est celle "
          "de la mise en ligne**, pas celle de la vente : une montre publiée en 2016 "
          "et vendue en 2019 porte 2016.", ""]

    return "\n".join(L) + "\n"


def main() -> None:
    cumul = lire_cumul()
    brut = volume_brut()
    runs = requetes_par_source()
    RAPPORT.write_text(redige(cumul, brut, runs), encoding="utf-8")

    actives = {s: d for s, d in cumul.items() if d["prix"]}
    print(f"{sum(d['prix'] for d in actives.values())} prix · {len(actives)} sources "
          f"· {sum(b['poids_mo'] for b in brut.values()):.0f} Mo de brut")
    print(f"-> {RAPPORT}")


if __name__ == "__main__":
    main()
