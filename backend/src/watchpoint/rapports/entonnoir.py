"""L'entonnoir, source par source — du brut à la ligne exploitable.

    cd ~/Desktop/WP
    python -m watchpoint rapport entonnoir

Trois questions, dans cet ordre, pour chaque source :

    COMBIEN DE BRUT       ce qu'on a effectivement ramené, et ce qu'on POURRAIT
                          ramener avec tous les efforts du monde — deux chiffres
                          differents qu'il ne faut jamais confondre
    FILTRE 0              est-ce une montre, et de quelle marque ? c'est l'arbre
                          R0 -> R8 du classeur de filtrage
    FILTRE 1              porte-t-elle une reference constructeur ? la methode
                          differe par source, et le rapport doit dire laquelle

S'y ajoute la nature du prix, qui n'est pas un filtre mais une qualification :
une ligne sans nature connue ne se compare a rien.

Le plafond atteignable vient du catalogue des sources (registre/catalogue.py) et
des journaux de collecte : quand une source a dit elle-meme ce qu'elle contient
— 'TRONQUE', '2500 fiches retenues sur 33106' — c'est ce chiffre qui fait foi.
Quand personne ne l'a mesure, la colonne dit 'non mesure' et non pas zero.

Ecrit dans docs/rapports/ENTONNOIR.md, jamais a la main.
"""
from __future__ import annotations

from watchpoint import config

import collections
import datetime as dt
import json
import pathlib
import re
import sys


from watchpoint import sources  # noqa: E402

LABO = config.RACINE
DATA = LABO / "data"
CUMUL = DATA / "price_points.jsonl"
RAPPORT = config.RAPPORTS / "ENTONNOIR.md"

NATURES = {"realised": "réalisé", "sold": "vendu", "asking": "demandé",
           "estimate": "estimation", "msrp": "prix neuf"}
REFERENCE_SURE = {"champ_dedie", "extrait_titre", "extrait_description",
                  # Reconnue a sa seule forme, sans mot-cle : 99 % de precision
                  # et 92 % de rappel, mesures contre les 4 086 references en
                  # champ dedie de Watchtrader.
                  "jeton_titre"}
TRANSACTIONNELLES = {"realised", "sold"}

# Comment la reference est obtenue, source par source. Ce n'est pas une
# preference : c'est ce que la source publie, et il faut le dire.
METHODE_REFERENCE = {
    "christies": "extraite du titre du lot, puis de la fiche technique",
    "watchesofdistinction": "extraite du titre, sous la forme « REF 216570 »",
    "amsterdamvintage": "attribut `Reference` publié par le marchand",
    "sworders": "extraite du titre du lot, rarement présente",
    "monacolegend": "extraite du titre du lot, qui cite la référence en clair",
    "artcurial": "extraite du titre puis de la description HTML",
    "lyonandturnbull": "extraite du sous-titre du lot",
    "craft_and_tailored": "extraite du titre, puis du corps de l'annonce",
    "analogshift": "extraite du corps de l'annonce",
    "montredo": "extraite du corps de l'annonce",
    "berrys": "champ SKU, qui porte ici la vraie référence constructeur",
    "cwsellors": "SKU du marchand, référence parfois dans le corps",
    "hairspring": "extraite du corps de l'annonce",
    "watchesofswitzerland": "lue dans l'URL de la fiche produit",
    "watchrecon": "extraite du titre de l'annonce",
}


def milliers(n) -> str:
    return f"{n:,}".replace(",", " ")


def tableau(lignes, entetes) -> list[str]:
    return ["| " + " | ".join(entetes) + " |",
            "|" + "|".join("---" for _ in entetes) + "|"] + \
           ["| " + " | ".join(str(c) for c in ligne) + " |" for ligne in lignes]


def plafonds() -> dict:
    """Ce que chaque source a DIT d'elle-meme dans les journaux de collecte."""
    trouves = {}
    dossier = DATA / "runs"
    if not dossier.exists():
        return trouves
    for chemin in sorted(dossier.glob("*.json")):
        try:
            manifeste = json.loads(chemin.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        for s in manifeste.get("sources", []):
            for ligne in s.get("journal", []):
                texte = str(ligne)
                if "retenues sur" in texte or "fiches," in texte:
                    trouves[s["id"]] = texte
                elif texte.startswith("TRONQUE") and s["id"] not in trouves:
                    trouves[s["id"]] = texte
    return trouves


def main() -> None:
    metas = {m.SOURCE["id"]: m.SOURCE for m in sources.ALL}
    par = collections.defaultdict(lambda: {
        "brut": 0, "garde": 0, "avec_ref": 0, "socle": 0,
        "natures": collections.Counter(), "annees": set(),
        "regles_rejet": collections.Counter(),
    })

    with CUMUL.open(encoding="utf-8") as flux:
        for ligne in flux:
            if not ligne.strip():
                continue
            r = json.loads(ligne)
            d = par[r["source_id"]]
            d["brut"] += 1
            if r.get("filter_verdict") != "GARDER":
                d["regles_rejet"][f"{r.get('filter_verdict')} {r.get('filter_rule')}"] += 1
                continue
            d["garde"] += 1
            d["natures"][r.get("price_nature")] += 1
            sure = r.get("reference") and r.get("reference_provenance") in REFERENCE_SURE
            if sure:
                d["avec_ref"] += 1
                if r.get("price_date") and r.get("price_nature") in TRANSACTIONNELLES:
                    d["socle"] += 1
                    d["annees"].add(r["price_date"][:4])

    # volume du brut sur disque
    poids = {}
    if (DATA / "raw").exists():
        for dossier in (DATA / "raw").iterdir():
            if dossier.is_dir():
                f = [*dossier.glob("*.json"), *dossier.glob("*.json.gz")]
                if f:
                    poids[dossier.name] = (len(f), sum(x.stat().st_size for x in f) / 1048576)

    dit = plafonds()
    ordre = sorted(par.items(), key=lambda kv: -kv[1]["brut"])
    total = {c: sum(d[c] for _, d in ordre) for c in ("brut", "garde", "avec_ref", "socle")}

    L = ["# L'entonnoir, source par source", "",
         f"**Généré le {dt.date.today().isoformat()}** par `python -m watchpoint rapport entonnoir` — "
         "ne pas éditer à la main.", "",
         "Trois questions dans l'ordre : combien de brut, qu'en garde le filtre, "
         "et combien portent une référence constructeur.", ""]

    L += ["## En un coup d'œil", "",
          f"- **{milliers(total['brut'])} lignes collectées** depuis {len(ordre)} sources",
          f"- **{milliers(total['garde'])} passent le filtre 0** — c'est une montre, "
          f"d'une marque connue ({round(100 * total['garde'] / total['brut'])} %)",
          f"- **{milliers(total['avec_ref'])} passent le filtre 1** — elles portent une "
          f"référence constructeur ({round(100 * total['avec_ref'] / total['brut'])} %)",
          f"- **{milliers(total['socle'])} forment le socle** — référence + date + "
          f"transaction réelle ({round(100 * total['socle'] / total['brut'])} %)",
          ""]

    L += ["## 1. L'entonnoir", "",
          "Chaque colonne est un sous-ensemble de la précédente.", ""]
    lignes = []
    for source, d in ordre:
        n, mo = poids.get(source, (0, 0))
        lignes.append([
            metas.get(source, {}).get("name", source),
            milliers(d["brut"]), f"{mo:.0f} Mo",
            f"{milliers(d['garde'])} ({round(100 * d['garde'] / max(d['brut'], 1))} %)",
            f"{milliers(d['avec_ref'])} ({round(100 * d['avec_ref'] / max(d['brut'], 1))} %)",
            f"**{milliers(d['socle'])}**",
        ])
    L += tableau(lignes, ["Source", "Brut collecté", "Sur disque", "Filtre 0 : montre",
                          "Filtre 1 : référence", "Socle"])
    L += [""]

    L += ["## 2. Comment la référence est obtenue, source par source", "",
          "La méthode diffère parce que les sources ne publient pas la même chose. "
          "Un SKU de marchand n'est jamais une référence constructeur.", ""]
    L += tableau([[metas.get(s, {}).get("name", s),
                   METHODE_REFERENCE.get(s, "non documentée"),
                   f"{round(100 * d['avec_ref'] / max(d['garde'], 1))} % du gardé"]
                  for s, d in ordre],
                 ["Source", "Méthode", "Rendement"])
    L += [""]

    L += ["## 3. Les natures de prix par source", "",
          "Une ligne dont on ignore la nature ne se compare à rien.", ""]
    L += tableau([[metas.get(s, {}).get("name", s),
                   " · ".join(f"{NATURES.get(n, n)} {milliers(c)}"
                              for n, c in d["natures"].most_common()),
                   f"{min(d['annees'])} → {max(d['annees'])}" if d["annees"] else "—"]
                  for s, d in ordre],
                 ["Source", "Natures observées", "Années du socle"])
    L += [""]

    L += ["## 4. Ce que la source a dit de ses propres limites", "",
          "Mot pour mot, ce que le collecteur a inscrit dans son journal. Une "
          "collecte plafonnée n'est pas un total.", ""]
    if dit:
        L += tableau([[metas.get(s, {}).get("name", s), f"`{t}`"] for s, t in dit.items()
                      if s in par],
                     ["Source", "Journal de collecte"])
    else:
        L += ["Aucune limite déclarée.", ""]
    L += [""]

    L += ["## 5. Pourquoi les lignes sont écartées", ""]
    regles = collections.Counter()
    for _, d in ordre:
        regles.update(d["regles_rejet"])
    L += tableau([[f"`{r}`", milliers(c)] for r, c in regles.most_common(10)],
                 ["Verdict et règle", "Lignes"])

    RAPPORT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"-> {RAPPORT}")
    for source, d in ordre:
        print(f"  {metas.get(source, {}).get('name', source):<26}"
              f"{d['brut']:>7} brut · {d['garde']:>7} montres · "
              f"{d['avec_ref']:>7} avec ref · {d['socle']:>6} socle")


if __name__ == "__main__":
    main()
