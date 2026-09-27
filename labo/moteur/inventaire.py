"""Ecrit LA liste des sources dans notes/SOURCES.md.

    cd ~/Desktop/WP/labo
    shared/.venv/bin/python moteur/inventaire.py

Avant, l'information vivait a six endroits : le registre Excel, le code des
adaptateurs, les dossiers d'essais, l'etat de la base, six rapports de campagne
et une presentation. Aucun ne disait la meme chose.

Ce script fusionne :
  - les adaptateurs branches       <- lus dans moteur/sources/ (automatique)
  - les volumes reellement collectes <- lus dans data/price_points.jsonl (automatique)
  - les sources testees             <- lues dans essais/ (automatique)
  - prouvees / a negocier / ecartees <- moteur/catalogue.py (le seul fichier a la main)

Le fichier produit est GENERE : ne pas l'editer, il sera ecrase.
"""
from __future__ import annotations

import collections
import datetime as dt
import json
import pathlib
import sys

ICI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))

import catalogue  # noqa: E402
import sources as paquet_sources  # noqa: E402

LABO = ICI.parent
BASE = LABO / "data" / "price_points.jsonl"
ESSAIS = LABO / "essais"
CIBLE = LABO.parent / "notes" / "SOURCES.md"

NATURES = {"realised": "realise", "sold": "vendu", "asking": "demande",
           "estimate": "estimation", "msrp": "prix neuf"}


def volumes_collectes() -> collections.Counter:
    if not BASE.exists():
        return collections.Counter()
    return collections.Counter(
        json.loads(l)["source_id"] for l in BASE.open(encoding="utf-8"))


def main() -> None:
    volumes = volumes_collectes()
    branchees = [m.SOURCE for m in paquet_sources.ALL]

    # Un dossier d'essai a un "verdict" des qu'il apparait quelque part : branche,
    # prouve, a negocier ou ecarte. On compare sur une forme reduite (minuscules,
    # sans separateurs) pour rapprocher "watchbox-1916" de "WatchBox / 1916 Company".
    def reduit(texte: str) -> str:
        return "".join(c for c in texte.lower() if c.isalnum())

    juges: set[str] = set()
    for s in branchees:
        juges |= {reduit(s["id"]), reduit(s["name"])}
    for groupe, cle in ((catalogue.PROUVEES, "nom"), (catalogue.A_NEGOCIER, "nom"),
                        (catalogue.ECARTEES, "nom")):
        for entree in groupe:
            # "Rolex, Omega, Cartier…" et "WatchBox / 1916" couvrent plusieurs sites
            for morceau in entree[cle].replace("—", ",").replace("/", ",").split(","):
                if morceau.strip():
                    juges.add(reduit(morceau))

    out: list[str] = []
    A = out.append

    A("# Les sources")
    A("")
    A(f"**Généré le {dt.date.today().isoformat()}** par `python moteur/inventaire.py`.")
    A("Ne pas éditer à la main — ce fichier est écrasé. Pour corriger un fait,")
    A("modifier `labo/moteur/catalogue.py`, puis relancer la commande.")
    A("")
    A(f"> {catalogue.AVERTISSEMENT}")
    A("")

    # ---------------------------------------------------------------- 1
    A("## 1. Branchées sur le moteur")
    A("")
    A("Elles collectent aujourd'hui. Le volume est ce qui est **réellement en base**.")
    A("")
    A("| Source | Catégorie | Nature | En base | Accès | État |")
    A("|---|---|---|---:|---|---|")
    for s in sorted(branchees, key=lambda x: -volumes.get(x["id"], 0)):
        etat = "**bloquée**" if "statut" in s else "active"
        A(f"| {s['name']} | {s['type']} | {NATURES.get(s['price_nature'], s['price_nature'])} "
          f"| {volumes.get(s['id'], 0)} | {s['access']} | {etat} |")
    A("")
    total = sum(volumes.values())
    A(f"**{total:,} prix** collectés au total.".replace(",", " "))
    A("")

    # ---------------------------------------------------------------- 2
    A("## 2. Prouvées, pas encore branchées")
    A("")
    A("Validées par récupération réelle de données — échantillons dans `labo/preuves/`.")
    A("Le volume est ce qui est **atteignable**, pas ce qui est collecté.")
    A("")
    A("| Source | Catégorie | Nature | Atteignable | Historique | Accès |")
    A("|---|---|---|---:|---|---|")
    for p in catalogue.PROUVEES:
        A(f"| **{p['nom']}** | {p['categorie']} | {p['nature']} | {p['volume']} "
          f"| {p['historique']} | {p['acces']} |")
    A("")
    A("Points d'attention :")
    A("")
    for p in catalogue.PROUVEES:
        if p.get("note"):
            A(f"- **{p['nom']}** — {p['note']}")
    A("")

    # ---------------------------------------------------------------- 3
    A("## 3. À démarcher")
    A("")
    A("Fermées techniquement. Aucune quantité de travail ne les ouvre : il faut")
    A("un accord commercial ou un accès officiel.")
    A("")
    titres = {
        1: "Priorité 1 — le type de prix qui manque totalement",
        2: "Priorité 2 — accès officiels à obtenir",
        3: "Priorité 3 — enchères et archives fermées",
        4: "Priorité 4 — marques (prix neuf)",
        5: "Priorité 5 — forums",
    }
    for niveau in sorted({n["priorite"] for n in catalogue.A_NEGOCIER}):
        A(f"### {titres[niveau]}")
        A("")
        A("| Source | Ce qu'on demande | Blocage |")
        A("|---|---|---|")
        for n in catalogue.A_NEGOCIER:
            if n["priorite"] == niveau:
                A(f"| **{n['nom']}** | {n['demande']} | {n['blocage']} |")
        A("")
    A("Les forums ont un impact limité : **WatchRecon les agrège déjà** et nous est")
    A("accessible. Les démarcher n'apporterait que de la profondeur, pas du volume.")
    A("")

    # ---------------------------------------------------------------- 4
    A("## 4. Écartées")
    A("")
    A("| Source | Raison |")
    A("|---|---|")
    for e in catalogue.ECARTEES:
        A(f"| {e['nom']} | {e['raison']} |")
    A("")

    # ---------------------------------------------------------------- 5
    dossiers = sorted(d.name for d in ESSAIS.iterdir()
                      if d.is_dir() and not d.name.startswith("_"))
    orphelins = [d for d in dossiers if reduit(d) not in juges]
    A("## 5. Bac à sable")
    A("")
    A(f"`labo/essais/` contient **{len(dossiers)} dossiers** de sources explorées.")
    A("Un dossier n'est pas un verdict : c'est une piste ouverte un jour.")
    A("")
    A("<details><summary>Voir la liste</summary>")
    A("")
    A(" · ".join(f"`{d}`" for d in dossiers))
    A("")
    A("</details>")
    A("")
    if orphelins:
        A(f"Dont **{len(orphelins)}** sans verdict enregistré ni dans le catalogue ni "
          f"dans le moteur — à trancher ou à archiver :")
        A("")
        A(" · ".join(f"`{d}`" for d in orphelins))
        A("")

    A("---")
    A("")
    A("Le registre complet des 210 sources recensées reste dans")
    A("`output/referentiels/` — le classeur le plus récent y fait foi ; c'est le")
    A("document de travail partagé")
    A("avec les associés, avec ses colonnes « assigné à » et « feedback ».")
    A("Ce fichier-ci est la vue technique : ce qui marche, ce qui est prouvé, ce qui est fermé.")

    CIBLE.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"écrit : notes/{CIBLE.name}")
    print(f"  {len(branchees)} branchées ({total} prix) · {len(catalogue.PROUVEES)} prouvées · "
          f"{len(catalogue.A_NEGOCIER)} à démarcher · {len(catalogue.ECARTEES)} écartées")
    if orphelins:
        print(f"  {len(orphelins)} dossier(s) d'essai sans verdict : {', '.join(orphelins)}")


if __name__ == "__main__":
    main()
