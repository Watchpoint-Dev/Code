"""Le rapport complet, une fiche par source.

    cd ~/Desktop/WP
    python -m watchpoint rapport rapport_source

Le tableau de TOUTES_LES_SOURCES.md repond a « combien ». Ce rapport-ci repond
a « peut-on s'en servir, et pour quoi faire ». Chaque source y a une fiche qui
dit, dans cet ordre :

    CE QU'ELLE EST        type, acces, ce que le robots.txt autorise
    CE QU'ELLE DONNE      l'entonnoir, les natures de prix, la periode
    CE QU'ELLE VAUT       la completude champ par champ, mesuree
    D'OU VIENT LA DONNEE  la provenance de la reference et de la nature
    CE QU'IL FAUT SAVOIR  la reserve declaree par l'adaptateur, la remarque
    CE QUI A ETE VERIFIE  le tirage de controle et ce qu'il a trouve

Tout vient du cumul et des adaptateurs. Rien n'est saisi a la main : une fiche
ecrite a la main se decale de la base au premier rejeu.

Ecrit dans docs/rapports/RAPPORT_PAR_SOURCE.md.
"""
from __future__ import annotations

from watchpoint import config

import collections
import datetime as dt
import json


from watchpoint import sources  # noqa: E402
from watchpoint.registre.catalogue_essais import ECARTEES  # noqa: E402
from watchpoint.rapports.toutes_les_sources import (NATURES, REFERENCE_SURE, REMARQUES,  # noqa: E402
                                TYPES, VERIFICATION)

LABO = config.RACINE
CUMUL = LABO / "data" / "price_points.jsonl"
RAPPORT = config.RAPPORTS / "RAPPORT_PAR_SOURCE.md"

TRANSACTIONNELLES = {"realised", "sold"}
# Les champs dont la presence change ce qu'on peut faire de la ligne.
CHAMPS = [("price_amount", "montant"), ("price_currency", "devise"),
          ("price_date", "date"), ("brand", "marque"), ("reference", "référence"),
          ("model", "modèle"), ("year", "année"), ("case_material", "boîtier"),
          ("case_size_mm", "diamètre"), ("movement", "mouvement"),
          ("dial_color", "cadran"), ("estimate_low", "estimation")]


def mille(n) -> str:
    return f"{n:,}".replace(",", " ")


def mesure() -> dict:
    par = collections.defaultdict(lambda: {
        "brut": 0, "garde": 0, "reference": 0, "socle": 0,
        "natures": collections.Counter(), "statuts": collections.Counter(),
        "provenance_ref": collections.Counter(),
        "provenance_nature": collections.Counter(),
        "devises": collections.Counter(), "annees": collections.Counter(),
        "champs": collections.Counter(), "rejets": collections.Counter(),
        "premium": collections.Counter(), "montants": [],
    })
    with CUMUL.open(encoding="utf-8") as flux:
        for ligne in flux:
            if not ligne.strip():
                continue
            r = json.loads(ligne)
            d = par[r["source_id"]]
            d["brut"] += 1
            if r.get("filter_verdict") != "GARDER":
                d["rejets"][f'{r.get("filter_verdict")} · {r.get("filter_rule")}'] += 1
                continue
            d["garde"] += 1
            d["natures"][r.get("price_nature")] += 1
            d["statuts"][r.get("listing_status")] += 1
            d["provenance_nature"][r.get("price_nature_provenance")] += 1
            d["devises"][r.get("price_currency")] += 1
            if r.get("price_includes_premium") is not None:
                d["premium"][r["price_includes_premium"]] += 1
            if r.get("price_date"):
                d["annees"][r["price_date"][:4]] += 1
            if isinstance(r.get("price_amount"), (int, float)):
                d["montants"].append(r["price_amount"])
            for champ, _ in CHAMPS:
                if r.get(champ) not in (None, ""):
                    d["champs"][champ] += 1
            if r.get("reference"):
                d["provenance_ref"][r.get("reference_provenance")] += 1
                if r.get("reference_provenance") in REFERENCE_SURE:
                    d["reference"] += 1
                    if r.get("price_date") and r["price_nature"] in TRANSACTIONNELLES:
                        d["socle"] += 1
    return par


def mediane(valeurs):
    if not valeurs:
        return None
    tri = sorted(valeurs)
    return tri[len(tri) // 2]


def main() -> None:
    metas = {m.SOURCE["id"]: m.SOURCE for m in sources.ALL}
    par = {s: d for s, d in mesure().items() if d["brut"]}
    ordre = sorted(par.items(), key=lambda kv: -kv[1]["brut"])
    tot = {c: sum(d[c] for _, d in ordre)
           for c in ("brut", "garde", "reference", "socle")}

    L = ["# Rapport par source", "",
         f"**Généré le {dt.date.today().isoformat()}** par "
         "`python -m watchpoint rapport rapport_source` — ne pas éditer à la main.", "",
         "Une fiche par source. Le tableau `TOUTES_LES_SOURCES.md` répond à "
         "« combien » ; ce rapport-ci répond à « peut-on s'en servir, et pour "
         "quoi faire ».", "",
         f"**{len(ordre)} sources collectent**, {len(ECARTEES)} ont été sondées "
         "puis écartées. En tout :", "",
         f"- **{mille(tot['brut'])} lignes** ramenées",
         f"- **{mille(tot['garde'])}** sont une montre d'une marque connue "
         f"({round(100 * tot['garde'] / tot['brut'])} %)",
         f"- **{mille(tot['reference'])}** portent une référence constructeur "
         f"({round(100 * tot['reference'] / tot['brut'])} %)",
         f"- **{mille(tot['socle'])}** forment le socle : référence + date + "
         f"transaction réelle ({round(100 * tot['socle'] / tot['brut'])} %)", "",
         "---", ""]

    # --- sommaire
    L += ["## Sommaire", "",
          "| # | Source | Type | Brut | Socle | Ce qu'elle apporte |",
          "|---|---|---|---|---|---|"]
    for rang, (s, d) in enumerate(ordre, 1):
        meta = metas.get(s, {})
        apport = ("le socle — transactions datées et référencées" if d["socle"] > 500
                  else "des références et des prix, sans date" if d["reference"] > 500
                  else "un appoint")
        L += [f"| {rang} | [{meta.get('name', s)}](#{rang}-{s}) | "
              f"{TYPES.get(meta.get('type'), '—')} | {mille(d['brut'])} | "
              f"{mille(d['socle'])} | {apport} |"]
    L += ["", "---", ""]

    # --- une fiche par source
    for rang, (s, d) in enumerate(ordre, 1):
        meta = metas.get(s, {})
        annees = sorted(d["annees"])
        tirage, trouve = VERIFICATION.get(s, ("non vérifiée", "—"))
        med = mediane(d["montants"])

        L += [f'<a name="{rang}-{s}"></a>', "",
              f"## {rang}. {meta.get('name', s)}", "",
              f"`{s}` · {TYPES.get(meta.get('type'), meta.get('type', '—'))} · "
              f"{meta.get('access', 'accès non documenté')}", ""]

        # l'entonnoir
        L += ["**Ce qu'elle donne**", "",
              "| Étape | Lignes | Part du brut |", "|---|---|---|",
              f"| Brut collecté | {mille(d['brut'])} | 100 % |",
              f"| Filtre 0 — c'est une montre | {mille(d['garde'])} | "
              f"{round(100 * d['garde'] / d['brut'])} % |",
              f"| Filtre 1 — référence constructeur | {mille(d['reference'])} | "
              f"{round(100 * d['reference'] / d['brut'])} % |",
              f"| Socle — + date + transaction | {mille(d['socle'])} | "
              f"{round(100 * d['socle'] / d['brut'])} % |", ""]

        details = []
        if d["natures"]:
            details.append("**Natures de prix** — " + " · ".join(
                f"{NATURES.get(n, n)} {mille(c)}" for n, c in d["natures"].most_common()))
        if d["devises"]:
            details.append("**Devises** — " + " · ".join(
                f"{v} {mille(c)}" for v, c in d["devises"].most_common()))
        if annees:
            details.append(f"**Période** — {annees[0]} → {annees[-1]} "
                           f"({len(annees)} années)")
        else:
            details.append("**Période** — aucune date : ces lignes ne peuvent "
                           "pas entrer dans le socle")
        if med:
            details.append(f"**Montant médian** — {mille(round(med))}")
        if d["premium"]:
            regime = ("frais acheteur INCLUS" if d["premium"].get(True) else "MARTEAU NU")
            if len(d["premium"]) > 1:
                regime = (f"MIXTE — {mille(d['premium'].get(True, 0))} frais inclus, "
                          f"{mille(d['premium'].get(False, 0))} marteau nu")
            details.append(f"**Régime de frais** — {regime}")
        L += [l + "  " for l in details] + [""]

        # la completude
        L += ["**Ce qu'elle remplit**", "",
              "| " + " | ".join(nom for _, nom in CHAMPS) + " |",
              "|" + "|".join("---" for _ in CHAMPS) + "|",
              "| " + " | ".join(
                  f"{round(100 * d['champs'][champ] / max(d['garde'], 1))} %"
                  for champ, _ in CHAMPS) + " |", ""]

        # les provenances
        L += ["**D'où vient la donnée**", "",
              "- Référence : " + (" · ".join(
                  f"`{p or 'aucune'}` {mille(c)}"
                  for p, c in d["provenance_ref"].most_common()) or "aucune référence"),
              "- Nature du prix : " + " · ".join(
                  f"`{p}` {mille(c)}" for p, c in d["provenance_nature"].most_common()),
              "- Statut d'annonce : " + " · ".join(
                  f"{p} {mille(c)}" for p, c in d["statuts"].most_common()), ""]

        # ce qu'il faut savoir
        L += ["**Ce qu'il faut savoir**", "", REMARQUES.get(s, "—"), ""]
        if meta.get("reserve"):
            L += [f"> **Réserve déclarée** — {meta['reserve']}", ""]
        if meta.get("robots"):
            L += [f"*robots.txt : {meta['robots']}*", ""]

        # la verification
        L += ["**Ce qui a été vérifié**", "",
              f"`{tirage}` — {trouve}", ""]

        if d["rejets"]:
            L += ["<details><summary>Pourquoi des lignes sont écartées</summary>", "",
                  "| Verdict et règle | Lignes |", "|---|---|"] + \
                 [f"| `{r}` | {mille(c)} |" for r, c in d["rejets"].most_common(5)] + \
                 ["", "</details>", ""]
        L += ["---", ""]

    # --- les ecartees
    L += ["## Les sources sondées puis écartées", "",
          "Chacune a coûté des requêtes réelles. Le volume est ce qui serait "
          "*atteignable*, jamais ce qui a été collecté.", "",
          "| Source | Type | Volume atteignable | Prix | Référence | Profondeur | "
          "Verdict |", "|---|---|---|---|---|---|---|"]
    ecartees = sorted(ECARTEES.items(), key=lambda kv: (kv[1]["verdict"], kv[1]["nom"]))
    for _, x in ecartees:
        L += [f"| **{x['nom']}** | {x['type']} | {x['volume']} | {x['prix']} | "
              f"{x['reference']} | {x['profondeur']} | {x['verdict']} |"]
    L += ["", "### Pourquoi", ""]
    for _, x in ecartees:
        L += [f"**{x['nom']}** — {x['remarque']}", ""]

    RAPPORT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"-> {RAPPORT}  ({len(L)} lignes)")
    print(f"{len(ordre)} fiches de source + {len(ECARTEES)} écartées")


if __name__ == "__main__":
    main()
