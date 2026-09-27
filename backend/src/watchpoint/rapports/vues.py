"""Les vues croisees — qu'est-ce qu'on peut REELLEMENT faire avec cette base ?

    cd ~/Desktop/WP
    python -m watchpoint rapport vues

Compter les lignes ne dit rien. Une ligne n'est exploitable que par la
conjonction de plusieurs champs, et c'est cette conjonction qu'il faut mesurer :

    pour tracer une COTE          il faut une reference constructeur + une date
                                  + une nature transactionnelle (realise ou vendu)
    pour comparer NEUF / OCCASION il faut la meme reference des deux cotes
    pour mesurer une TENDANCE     il faut la meme reference sur plusieurs annees
    pour afficher un PRIX         il faut savoir de quelle nature il est

Une source peut afficher 100 % de references et n'en avoir aucune d'utilisable :
un SKU de marchand n'identifie pas un modele. Ce document separe donc toujours
l'identifiant de la reference constructeur.

Ecrit dans docs/rapports/VUES.md, jamais a la main.
"""
from __future__ import annotations

from watchpoint import config

import collections
import datetime as dt
import json
import pathlib
import sys


from watchpoint import sources  # noqa: E402

LABO = config.RACINE
CUMUL = LABO / "data" / "price_points.jsonl"
RAPPORT = config.RAPPORTS / "VUES.md"

NATURES = {"realised": "réalisé", "sold": "vendu", "asking": "demandé",
           "estimate": "estimation", "msrp": "prix neuf"}
# Les natures qui disent qu'une transaction a eu lieu. Les autres sont des
# opinions de vendeur ou des tarifs affiches.
TRANSACTIONNELLES = {"realised", "sold"}
# Les provenances qui donnent une reference CONSTRUCTEUR, seule utilisable pour
# rapprocher deux annonces du meme modele.
# Une reference n'est exploitable que si elle identifie un MODELE. Le SKU d'un
# marchand n'en est pas une : c'est son numero d'inventaire. En revanche, une
# reference lue dans le corps de l'annonce en est bien une des lors qu'elle
# suit un mot-cle entier et porte un chiffre — verifie le 28/08/2026 sur
# echantillon : YA136208 (Gucci), CK2998 (Omega), 1680 (Rolex Submariner).
REFERENCE_SURE = {"champ_dedie", "extrait_titre", "extrait_description",
                  # Reconnue a sa seule forme, sans mot-cle : 99 % de precision
                  # et 92 % de rappel, mesures contre les 4 086 references en
                  # champ dedie de Watchtrader.
                  "jeton_titre"}


def milliers(n) -> str:
    return f"{n:,}".replace(",", " ")


def tableau(lignes, entetes) -> list[str]:
    return ["| " + " | ".join(entetes) + " |",
            "|" + "|".join("---" for _ in entetes) + "|"] + \
           ["| " + " | ".join(str(c) for c in ligne) + " |" for ligne in lignes]


def charge() -> list[dict]:
    with CUMUL.open(encoding="utf-8") as flux:
        return [json.loads(l) for l in flux if l.strip()]


def redige(lignes) -> str:
    metas = {m.SOURCE["id"]: m.SOURCE for m in sources.ALL}
    gardees = [r for r in lignes if r.get("filter_verdict") == "GARDER"]
    n = len(gardees)

    def sure(r):
        return r.get("reference") and r.get("reference_provenance") in REFERENCE_SURE

    L = ["# Ce qu'on peut faire avec les données", "",
         f"**Généré le {dt.date.today().isoformat()}** par `python -m watchpoint rapport vues` — "
         "ne pas éditer à la main.", "",
         f"Sur {milliers(len(lignes))} lignes collectées, **{milliers(n)} sont "
         "gardées par le filtre**. Tout ce qui suit ne porte que sur celles-là : "
         "les lignes rejetées restent en base pour l'audit, elles ne servent pas "
         "l'analyse.", ""]

    # ---- 1. L'escalier : de la ligne brute a la ligne exploitable
    L += ["## 1. L'escalier de l'exploitabilité", "",
          "Chaque marche retire ce qui manque. C'est le chiffre du bas qui compte, "
          "pas celui du haut.", ""]

    avec_marque = [r for r in gardees if r.get("brand")]
    avec_prix = [r for r in avec_marque if r.get("price_amount")]
    avec_date = [r for r in avec_prix if r.get("price_date")]
    avec_ref = [r for r in avec_date if sure(r)]
    transac = [r for r in avec_ref if r.get("price_nature") in TRANSACTIONNELLES]

    escalier = [
        ("gardées par le filtre", gardees, "on sait que c'est une montre"),
        ("+ une marque", avec_marque, "on sait de qui elle est"),
        ("+ un prix chiffré", avec_prix, "on a une valeur"),
        ("+ une date", avec_date, "on peut la situer dans le temps"),
        ("+ une référence constructeur", avec_ref,
         "on peut la rapprocher d'une autre annonce du même modèle"),
        ("+ une transaction réelle", transac,
         "**le socle d'une cote** : réalisé ou vendu, pas une opinion de vendeur"),
    ]
    L += tableau([[libelle, milliers(len(sous)), f"{round(100 * len(sous) / max(n, 1))} %",
                   commentaire] for libelle, sous, commentaire in escalier],
                 ["Marche", "Lignes", "Part", "Ce que ça permet"])
    L += ["",
          f"**{milliers(len(transac))} lignes forment le socle exploitable**, soit "
          f"{round(100 * len(transac) / max(n, 1))} % du gardé. C'est peu, et c'est "
          "normal : les marchands publient des prix sans référence constructeur, "
          "les forums sans référence du tout.", ""]

    # ---- 2. Nature de prix croisee avec la reference
    L += ["## 2. Nature du prix croisée avec la référence", "",
          "La question qui commande tout le reste : de quoi parle ce prix, et "
          "sait-on à quel modèle il se rapporte ?", ""]
    croix = collections.defaultdict(collections.Counter)
    for r in gardees:
        cle = ("référence constructeur" if sure(r)
               else "identifiant faible" if r.get("reference") else "aucun identifiant")
        croix[r.get("price_nature")][cle] += 1
    ordre_cles = ["référence constructeur", "identifiant faible", "aucun identifiant"]
    L += tableau([[NATURES.get(nat, nat)] +
                  [milliers(croix[nat][c]) for c in ordre_cles] +
                  [milliers(sum(croix[nat].values()))]
                  for nat in sorted(croix, key=lambda x: -sum(croix[x].values()))],
                 ["Nature"] + ordre_cles + ["Total"])
    L += ["",
          "L'identifiant faible est un SKU de marchand — `P-O 82172/000P-H062` "
          "chez Berry's, `LMMOD3312RNNS` chez Craft & Tailored. C'est un numéro "
          "d'inventaire : il identifie un exemplaire dans un stock, jamais un "
          "modèle, et ne permet donc aucun rapprochement entre deux annonces.", ""]

    # ---- 3. Ce que chaque source apporte VRAIMENT
    L += ["## 3. Ce que chaque source apporte au socle", "",
          "Le volume d'une source ne dit pas sa valeur. Seules comptent les lignes "
          "qui franchissent toutes les marches.", ""]
    par_source = collections.defaultdict(lambda: {"gardees": 0, "socle": 0,
                                                  "annees": set(), "natures": collections.Counter()})
    for r in gardees:
        d = par_source[r["source_id"]]
        d["gardees"] += 1
        d["natures"][r.get("price_nature")] += 1
        if sure(r) and r.get("price_date") and r.get("price_nature") in TRANSACTIONNELLES:
            d["socle"] += 1
            d["annees"].add(r["price_date"][:4])
    lignes_src = []
    for source, d in sorted(par_source.items(), key=lambda kv: -kv[1]["socle"]):
        annees = sorted(d["annees"])
        lignes_src.append([
            metas.get(source, {}).get("name", source),
            milliers(d["gardees"]), milliers(d["socle"]),
            f"{round(100 * d['socle'] / max(d['gardees'], 1))} %",
            f"{annees[0]} → {annees[-1]}" if annees else "—",
        ])
    L += tableau(lignes_src, ["Source", "Gardées", "Dans le socle", "Rendement",
                              "Années couvertes"])
    L += [""]

    # ---- 4. La profondeur du socle
    L += ["## 4. La profondeur du socle, année par année", "",
          "Combien de transactions datées et rattachables à un modèle, par année. "
          "C'est la matière d'une courbe de cote.", ""]
    par_annee = collections.Counter(r["price_date"][:4] for r in transac)
    pic = max(par_annee.values(), default=1)
    L += tableau([[annee, milliers(c), "█" * max(1, round(28 * c / pic))]
                  for annee, c in sorted(par_annee.items(), reverse=True)],
                 ["Année", "Transactions", ""])
    L += [""]

    # ---- 5. Les modeles reellement suivis
    L += ["## 5. Les modèles qu'on peut réellement suivre", "",
          "Une référence n'a d'intérêt que si elle revient. Voici celles qui "
          "apparaissent le plus souvent dans le socle — ce sont elles qui "
          "permettront les premières courbes.", ""]
    par_ref = collections.Counter(
        (str(r.get("brand") or "").title(), str(r["reference"]).upper()) for r in transac)
    L += tableau([[f"{marque} {ref}", milliers(c)]
                  for (marque, ref), c in par_ref.most_common(15)],
                 ["Marque et référence", "Transactions"])
    plusieurs = sum(1 for c in par_ref.values() if c >= 3)
    L += ["",
          f"**{milliers(len(par_ref))} références distinctes** dans le socle, dont "
          f"**{milliers(plusieurs)} apparaissent au moins trois fois** — le minimum "
          "pour esquisser une tendance plutôt qu'un point isolé.", ""]

    # ---- 6. Le neuf face a l'occasion
    L += ["## 6. Le neuf face à l'occasion", "",
          "Comparer un tarif catalogue à un prix de marché demande la même "
          "référence des deux côtés. Voici où c'est possible aujourd'hui.", ""]
    refs_neuf = {str(r["reference"]).upper() for r in gardees
                 if r.get("price_nature") == "msrp" and sure(r)}
    refs_occasion = {str(r["reference"]).upper() for r in transac}
    communes = refs_neuf & refs_occasion
    L += [f"- **{milliers(len(refs_neuf))} références** portent un prix neuf",
          f"- **{milliers(len(refs_occasion))} références** portent une transaction",
          f"- **{milliers(len(communes))} sont communes aux deux** — c'est là, et "
          "seulement là, qu'on peut mesurer une décote",
          ""]
    if communes:
        exemples = [r for r in gardees
                    if sure(r) and str(r["reference"]).upper() in communes][:0]
        neuf = {str(r["reference"]).upper(): r for r in gardees
                if r.get("price_nature") == "msrp" and sure(r)}
        occas = collections.defaultdict(list)
        for r in transac:
            occas[str(r["reference"]).upper()].append(r)
        lignes_dec = []
        for ref in list(communes)[:12]:
            n_ = neuf[ref]
            marche = occas[ref]
            if n_.get("price_currency") != marche[0].get("price_currency"):
                continue
            median = sorted(x["price_amount"] for x in marche)[len(marche) // 2]
            ecart = round(100 * (median - n_["price_amount"]) / n_["price_amount"])
            lignes_dec.append([
                f"{(n_.get('brand') or '').title()} {ref}",
                f"{n_['price_amount']:,.0f} {n_['price_currency']}".replace(",", " "),
                f"{median:,.0f}".replace(",", " "), len(marche),
                f"{ecart:+d} %"])
        if lignes_dec:
            L += ["Premiers rapprochements possibles, à devise identique :", ""]
            L += tableau(lignes_dec, ["Référence", "Prix neuf", "Médiane marché",
                                      "Transactions", "Écart"])
            L += ["",
                  "Réserve : le prix neuf est relevé chez un détaillant britannique "
                  "en GBP, et les transactions viennent de maisons de ventes dont "
                  "certaines publient frais acheteur inclus. Ces écarts sont des "
                  "ordres de grandeur, pas des décotes établies.", ""]

    # ---- 7. Ce qui manque
    L += ["## 7. Ce qui manque pour aller plus loin", ""]
    manques = [
        ["Référence constructeur chez les marchands",
         f"{milliers(sum(1 for r in gardees if r.get('reference') and not sure(r)))} lignes "
         "portent un SKU au lieu d'une référence",
         "lire la fiche produit au lieu du catalogue"],
        ["Date de transaction chez les marchands",
         "la date publiée est celle de la mise en ligne, pas de la vente",
         "relever les disparitions d'annonces jour après jour"],
        ["Profondeur avant 2017 hors Artcurial",
         "Christie's ne sert plus ses lots anciens, les marchands n'ont pas d'archive",
         "brancher une maison de ventes à archive profonde"],
        ["Le modèle, presque absent",
         f"{round(100 * sum(1 for r in gardees if r.get('model')) / max(n, 1))} % des "
         "lignes portent un nom de modèle en champ propre",
         "le déduire de la référence, une fois le référentiel constitué"],
    ]
    L += tableau(manques, ["Ce qui manque", "Constat mesuré", "Ce qu'il faudrait"])

    return "\n".join(L) + "\n"


def main() -> None:
    lignes = charge()
    RAPPORT.write_text(redige(lignes), encoding="utf-8")
    print(f"-> {RAPPORT}")


if __name__ == "__main__":
    main()
