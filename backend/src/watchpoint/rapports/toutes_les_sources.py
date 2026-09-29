"""Le tableau de toutes les sources essayees — celles qui collectent et les autres.

    cd ~/Desktop/WP
    python -m watchpoint rapport toutes_les_sources

Un tableau qui ne montre que les sources retenues ment par omission. Celui-ci
liste les trente-cinq sondees, dans un seul ordre de lecture :

    BRUT        ce qui a ete ramene, ou ce qui serait atteignable si on n'a rien
                ramene — les deux ne sont jamais confondus
    MONTRES     ce que le filtre 0 garde : c'est une montre, d'une marque connue
    REFERENCE   ce que le filtre 1 garde : elle porte une reference constructeur,
                SKU exclus, avec la methode d'obtention propre a la source
    NATURE      les types de prix observes, avec leurs comptes

Chaque ligne porte une remarque : ce qu'il faut savoir avant de s'appuyer dessus.

Ecrit dans docs/rapports/TOUTES_LES_SOURCES.md, jamais a la main.
"""
from __future__ import annotations

from watchpoint import config

import collections
import datetime as dt
import json


from watchpoint import sources  # noqa: E402
from watchpoint.registre.catalogue_essais import ECARTEES  # noqa: E402

LABO = config.RACINE
CUMUL = LABO / "data" / "price_points.jsonl"
RAPPORT = config.RAPPORTS / "TOUTES_LES_SOURCES.md"

NATURES = {"realised": "réalisé", "sold": "vendu", "asking": "demandé",
           "estimate": "estimation", "msrp": "prix neuf"}
TYPES = {"auction": "maison de ventes", "dealer": "marchand", "retail": "détaillant",
         "marketplace": "marketplace", "community": "forums",
         "aggregator": "agrégateur"}
REFERENCE_SURE = {"champ_dedie", "extrait_titre", "extrait_description", "jeton_titre"}

# Ce qu'il faut savoir de chaque source active, en une phrase. Ces remarques
# viennent des reconnaissances et des verifications, pas d'une impression.
REMARQUES = {
    "hodinkee": "Archive figée : plus rien publié après octobre 2024. On l'aspire "
                "une fois, elle ne bougera plus — c'est un gisement, pas un flux.",
    "montredo": "Le tag `inquiry-only` dit « nous consulter », pas « vendue » : 3 071 "
                "fausses ventes ont été retirées le 28/08. Catalogue reconstruit "
                "chaque nuit, d'où une date de relevé et zéro profondeur.",
    "christies": "Publie ses prix FRAIS ACHETEUR INCLUS — mesuré : 39 % de montants "
                 "ronds contre 97 % chez Artcurial. Sa fiche technique donne matière, "
                 "mouvement, cadran et diamètre à plus de 80 %.",
    "artcurial": "Marteau nu, dix-neuf ans de profondeur. L'API ne sert que les lots "
                 "vendus : biais de survie assumé.",
    "analogshift": "La référence vit dans le corps de l'annonce, pas dans le titre ; "
                   "son SKU est un code marchand qu'il ne faut pas confondre.",
    "watchrecon": "Agrégateur de forums, la source la plus fraîche du dossier. Un tiers "
                  "de ses titres portent une référence qu'on ne lisait pas. La nature "
                  "du prix y reste déclarée, jamais mesurée.",
    "wannabuyawatch": "L'API conserve le dernier prix demandé de 5 985 montres que "
                      "la page publique affiche pourtant en « SOLD » sans montant.",
    "lyonandturnbull": "La seule source qui publie ses INVENDUS. Ses ventes "
                       "« horlogères » sont à 80 % de la joaillerie, d'où un taux de "
                       "conservation faible mais justifié.",
    "berrys": "Détaillant AGRÉÉ : son champ SKU porte la vraie référence constructeur "
              "(L38204930, IW503607), pas un code maison. La compter comme un SKU "
              "ramenait la source à 183 références au lieu de 2 125.",
    "keystone": "Le schéma le mieux structuré des marchands : un bloc « Reference / "
                "Year / Brand » dans la description, et huit ans de mise en ligne.",
    "loupethis": "La seule source qui publie À LA FOIS le marteau et le prix frais "
                 "inclus. On charge le marteau ; la relation ×1,10 est vérifiée sur "
                 "243 lots sans exception.",
    "watchtrader": "La référence est un CHAMP DÉDIÉ rempli à 99,8 %. Mais 3 477 de ses "
                   "4 070 fiches ont quitté le catalogue : ce sont des archives, "
                   "pas des offres vives, et la source ne date rien.",
    "fortuna": "Son champ `hammer_price` n'est un marteau que sur les 31 lots où les "
               "frais sont publiés ; sur les 1 713 autres il les inclut déjà. Nous "
               "avions généralisé depuis 1,7 % du corpus — la seule population qui "
               "se comporte autrement.",
    "bulangandsons": "`available` ne dit pas la vente ici, ce sont les tags. Et sa description "
                     "énumère les BRACELETS livrés : 443 fiches portaient la référence "
                     "du bracelet au lieu de celle de la montre.",
    "topper": "Détaillant de NEUF : `available=false` y signifie rupture de stock, "
              "pas vente. Le traiter comme une vente fabriquerait de fausses "
              "transactions.",
    "craft_and_tailored": "97 % de son catalogue est vendu. Le plus gros piège de devise du "
                          "dossier : sans `country=US`, -17,85 % sur la moitié de la base.",
    "cwsellors": "Mélange prix TTC et HT dans le même flux sans champ distinctif : "
                 "un écart de 20 % peut n'être que de la TVA.",
    "awco": "Un prix NÉGATIF y marque une vente, la valeur absolue étant le dernier "
            "prix demandé. Convention unique au dossier.",
    "watchesofswitzerland": "Détaillant agréé : source du prix NEUF au tarif officiel. "
                            "Collecte bornée à 2 500 fiches sur 33 106 — une requête "
                            "par fiche, neuf heures pour le tout.",
    "globalwatchshop": "Référence en champ dédié à 100 %, mais 38 % des fiches sont "
                       "à prix zéro : du prix sur demande masqué.",
    "acollectedman": "Horlogerie indépendante haut de gamme. Ses manquants en référence "
                     "n'en sont pas : Journe et Voutilainen n'ont réellement pas de "
                     "référence constructeur.",
    "chronofinder": "Petite mais intégralement prixée — aucune fiche en « prix sur "
                    "demande », ce qui n'arrive nulle part ailleurs.",
    "hairspring": "Le champ marque vaut « Hairspring » sur 100 % des fiches ; la vraie "
                  "marque se retrouve dans la description, pour la moitié seulement.",
    "monacolegend": "Sept ans d'enchères exclusivement horlogères en 20 requêtes — "
                    "le meilleur rapport volume/coût du dossier. Publie ses INVENDUS "
                    "(421 lots) et deux devises. Prix FRAIS ACHETEUR INCLUS, comme "
                    "Christie's : ne pas le comparer à un marteau nu.",
    "amsterdamvintage": "La fiche la mieux remplie du dossier : référence, année, "
                        "matière et numéro de série en champs DÉDIÉS — 91 % de "
                        "références publiées, 96 % d'années. Mais le prix est "
                        "SUPPRIMÉ à la vente : seul le stock vivant a un montant.",
    "sworders": "Atteinte par sa recherche, marque par marque : son index ne publie "
                "que 57 ventes récentes et ses ventes sont à 80 % joaillières. "
                "Marteau nu vérifié. Aucune date : la source ne la publie que sur "
                "la fiche du lot, à 10 s de délai imposé par requête.",
    "watchesofdistinction": "Fiche très structurée : marque à 100 %, référence à "
                            "93 %, année exacte à 90 %, matière du boîtier à 98 %. "
                            "Mais deux tiers de son catalogue sont à prix zéro — "
                            "4 962 fiches écartées faute de montant.",
    "everywatch": "573 015 annonces annoncées, ~210 000 exploitables — mais la source "
                  "BLOQUE après une dizaine de requêtes : 32 réponses sur 42 refusées "
                  "le 28/08. Elle tolère quelques appels, pas une collecte.",
}

# Ce qui a ete VERIFIE source par source le 28/08/2026, contre les pages en
# ligne et non contre notre propre base : montant, reference, nature du prix et
# marque sur un tirage aleatoire, plus un controle propre a chaque source. Le
# resultat est donne tel quel, defauts compris. Une verification qui ne trouve
# jamais rien ne verifie rien.
VERIFICATION = {
    "hodinkee": ("8/8 montants · 8/8 references · 8/8 natures · 8/8 marques",
                 "Rien a corriger. Notre marque est meilleure que celle de la "
                 "boutique : `vendor` dit « HODINKEE Shop », nous disons "
                 "« Audemars Piguet »."),
    "keystone": ("8/8 montants · 8/8 references · 8/8 natures · 8/8 marques",
                 "27 fiches a 1,00 USD, prix sentinelle reellement publie par le "
                 "site — desormais ecartees par le plancher du moteur."),
    "montredo": ("8/8 montants · 7/8 references · 2/8 natures · 8/8 marques",
                 "CORRIGE. 18 des 20 lignes « vendues » tirees au hasard portaient "
                 "le tag `inquiry-only` : 3 071 fausses ventes retirees."),
    "analogshift": ("8/8 montants · 3/8 references · 8/8 natures · 8/8 marques",
                    "Le SKU maison ne sera jamais une reference : 2 946 lignes en "
                    "portent un, et sont comptees a part. La reference reelle est "
                    "dans le corps de l'annonce."),
    "craft_and_tailored": ("8/8 montants · 7/8 references · 8/8 natures · 6/8 marques",
                           "CORRIGE. `vendor` valait litteralement « Other » sur les "
                           "petites maisons ; le moteur relit le titre. Son "
                           "collecteur maison a ete rendu au moteur commun."),
    "bulangandsons": ("8/8 montants · 5/8 references · 8/8 natures · 8/8 marques",
                      "CORRIGE. 443 fiches portaient la reference du BRACELET livre "
                      "avec la montre, et 305 un prix de 1 EUR. Le titre est "
                      "desormais epuise avant la description."),
    "christies": ("7/8 montants · 8/8 references · 8/8 dates",
                  "Le drapeau « frais inclus » est juste : 89 a 95 % des montants se "
                  "decomposent en (marteau sur echelon) x (taux publie). Reserve : "
                  "pour les ventes en ligne la date est l'OUVERTURE, pas "
                  "l'adjudication."),
    "artcurial": ("7/7 montants · 8/8 references · 7/7 dates",
                  "CORRIGE sur la provenance : 495 references venaient de la "
                  "description et se disaient tirees du titre. Notre montant est le "
                  "marteau et ne correspond JAMAIS au « Vendu » affiche, qui est "
                  "frais inclus."),
    "lyonandturnbull": ("7/8 montants · 8/8 references · 7/7 dates",
                        "La plus propre du lot : marteau nu confirme par champ dedie, "
                        "bareme de frais et dates de session explicites."),
    "loupethis": ("8/8 montants · 8/8 references · 8/8 dates",
                  "Marteau nu verifie sur 4 220 lots sur 4 220. Attention au regime "
                  "economique et non au drapeau : les frais n'y sont que de 10 %, "
                  "contre 25 a 30 % ailleurs."),
    "fortuna": ("8/8 montants · 8/8 references · 8/8 dates",
                "CORRIGE, et c'est la correction la plus lourde : `hammer_price` "
                "n'est un marteau que sur 31 lots ; sur les 1 713 autres il inclut "
                "deja 25 % de frais. Les dates et la taxonomie des marques sont "
                "desormais dans le brut : la source est rejouable de bout en bout."),
    "watchrecon": ("8/8 montants · 0/8 references avant correction",
                   "CORRIGE. Un tiers des titres portaient une reference qu'on ne "
                   "lisait pas : 3 232 lignes en ont une aujourd'hui. Le "
                   "dedoublonnage comptait aussi 1 709 annonces deux fois."),
    "watchtrader": ("6/6 montants · 6/6 references · 0/6 natures",
                    "CORRIGE. 3 477 de ses 4 070 fiches ont quitte le catalogue et "
                    "sortaient « en vente » : le moteur lisait un champ de stock que "
                    "l'API n'envoie pas."),
    "wannabuyawatch": ("6/6 montants · 3/6 references · 0/6 natures",
                       "CORRIGE par le meme defaut de stock. 1 218 lignes restent "
                       "sans aucune reference."),
    "awco": ("6/6 montants · 4/6 references · 2/6 natures",
             "CORRIGE par le meme defaut de stock. Le champ SKU est vide chez ce "
             "marchand : la reference vient du titre."),
    "globalwatchshop": ("6/6 montants · 6/6 references · 3/6 natures",
                        "CORRIGE par le meme defaut de stock. Sa fiche Breitling se "
                        "contredit elle-meme entre son champ MODEL et son titre ; on "
                        "recopie le champ."),
    "chronofinder": ("6/6 montants · 5/6 references · 2/6 natures",
                     "CORRIGE par le meme defaut de stock. Une reference divergente "
                     "trouvee sur un champ dedie (18238 contre 18038 en ligne)."),
    "berrys": ("6/6 montants · 6/6 references · 6/6 natures",
               "CORRIGE. Son champ SKU porte la vraie reference constructeur : la "
               "source passe de 183 a 2 125 references exploitables. Sans "
               "`country=GB` le prix perd 16,7 % de TVA."),
    "cwsellors": ("6/6 montants · 1/6 references · 6/6 natures",
                  "Son SKU est un vrai code maison (« DOX-333 ») : 12 % de "
                  "references seulement, et c'est exact. Ses 1 200 « vendues » sont "
                  "des prix catalogue de detaillant agree."),
    "topper": ("6/6 montants · 5/6 references · 6/6 natures",
               "La regle « rupture n'est pas vente » tient : 100 % en prix neuf. Une "
               "Breitling Premier publiee a 500 USD par la boutique elle-meme."),
    "watchesofswitzerland": ("6/6 montants · 3/6 references · 6/6 natures",
                             "API irreprochable. 470 lignes sans reference alors "
                             "qu'elle est dans l'URL : defaut de rappel, pas de "
                             "justesse."),
    "hairspring": ("6/6 montants · 3/6 references · 6/6 natures",
                   "Sans `country=US` le prix chute de 17,8 %. Minuscule, mais la "
                   "plus propre en nature : 0 sur 35 revenue en stock."),
    "acollectedman": ("6/6 montants · 2/6 references · 6/6 natures",
                      "Son SKU est un code maison honnete. La vraie reference est "
                      "parfois dans l'URL et nous echappe."),
    "monacolegend": ("structure revérifiée avant collecte",
                     "Le JSON-LD était passé d'un `EventSeries` nu à un `@graph` "
                     "depuis la reconnaissance : le code lit les deux. Rejeu hors "
                     "ligne identique à la collecte, 4 188 sur 4 188."),
    "amsterdamvintage": ("branchée le 29/08 sur le moteur WooCommerce",
                         "Ni attribut ni champ natif de marque : ses 342 fiches "
                         "sortaient sans marque et R3 les rejetait toutes. Le repli "
                         "sur le titre a été ajouté au moteur — il fait aussi gagner "
                         "des marques à Wanna Buy A Watch et AWCO."),
    "sworders": ("régime de frais vérifié arithmétiquement",
                 "Ses conditions disent « hammer price plus a buyer's premium » de "
                 "27 %, mais cela dit ce qu'on paie, pas ce qu'affiche la page. Le "
                 "contrôle tranche : 77 % des montants tombent sur un échelon "
                 "d'enchère tels quels, 8 % après division par 1,27. C'est un "
                 "marteau."),
    "watchesofdistinction": ("année recoupée titre contre attribut",
                             "Son attribut d'année donne une DÉCENNIE — « 2010's » — "
                             "quand le titre porte le millésime : 401 lignes sur 496 "
                             "divergeaient, dont une montre de 2020 datée de 2010. Le "
                             "titre prime désormais, zéro divergence."),
    "everywatch": ("collecte impossible", "32 reponses sur 42 refusees le 28/08."),
}


def milliers(n) -> str:
    return f"{n:,}".replace(",", " ")


def tableau(lignes, entetes) -> list[str]:
    return ["| " + " | ".join(entetes) + " |",
            "|" + "|".join("---" for _ in entetes) + "|"] + \
           ["| " + " | ".join(str(c) for c in ligne) + " |" for ligne in lignes]


def mesure() -> dict:
    par = collections.defaultdict(lambda: {
        "brut": 0, "montres": 0, "reference": 0, "sku": 0,
        "natures": collections.Counter(), "provenances": collections.Counter(),
        "annees": set(), "devises": collections.Counter(),
    })
    with CUMUL.open(encoding="utf-8") as flux:
        for ligne in flux:
            if not ligne.strip():
                continue
            r = json.loads(ligne)
            d = par[r["source_id"]]
            d["brut"] += 1
            if r.get("filter_verdict") != "GARDER":
                continue
            d["montres"] += 1
            d["natures"][r.get("price_nature")] += 1
            d["devises"][r.get("price_currency")] += 1
            if r.get("price_date"):
                d["annees"].add(r["price_date"][:4])
            provenance = r.get("reference_provenance")
            if r.get("reference"):
                d["provenances"][provenance] += 1
                if provenance in REFERENCE_SURE:
                    d["reference"] += 1
                elif provenance == "sku":
                    d["sku"] += 1
    return par


def main() -> None:
    metas = {m.SOURCE["id"]: m.SOURCE for m in sources.ALL}
    par = mesure()
    actives = {s: d for s, d in par.items() if d["brut"]}
    ordre = sorted(actives.items(), key=lambda kv: -kv[1]["brut"])

    total = {c: sum(d[c] for _, d in ordre) for c in ("brut", "montres", "reference")}

    L = ["# Toutes les sources essayées", "",
         f"**Généré le {dt.date.today().isoformat()}** par "
         "`python -m watchpoint rapport toutes_les_sources` — ne pas éditer à la main.", "",
         f"**{len(ordre)} sources collectent aujourd'hui**, "
         f"**{len(ECARTEES)} autres ont été sondées** puis écartées, mises de côté "
         "ou laissées à une décision. Toutes figurent ci-dessous : un tableau qui "
         "ne montrerait que les sources retenues laisserait croire qu'on a choisi "
         "sans comparer.", "",
         f"- **{milliers(total['brut'])} lignes collectées**",
         f"- **{milliers(total['montres'])} passent le filtre 0** — c'est une montre "
         f"d'une marque connue ({round(100 * total['montres'] / total['brut'])} %)",
         f"- **{milliers(total['reference'])} passent le filtre 1** — référence "
         f"constructeur, SKU exclus ({round(100 * total['reference'] / total['brut'])} %)",
         ""]

    L += ["## 1. Les sources qui collectent", "",
          "Le brut est ce qui a été réellement ramené. Les colonnes suivantes en "
          "sont des sous-ensembles.", ""]
    lignes = []
    for source, d in ordre:
        meta = metas.get(source, {})
        natures = " · ".join(f"{NATURES.get(n, n)} {milliers(c)}"
                             for n, c in d["natures"].most_common(3))
        annees = sorted(d["annees"])
        lignes.append([
            f"**{meta.get('name', source)}**",
            TYPES.get(meta.get("type"), meta.get("type", "—")),
            milliers(d["brut"]),
            f"{milliers(d['montres'])} ({round(100 * d['montres'] / max(d['brut'], 1))} %)",
            f"{milliers(d['reference'])} ({round(100 * d['reference'] / max(d['brut'], 1))} %)",
            natures or "—",
            f"{annees[0]}→{annees[-1]}" if annees else "sans date",
        ])
    L += tableau(lignes, ["Source", "Type", "Brut", "Filtre 0 : montres",
                          "Filtre 1 : référence", "Natures de prix", "Période"])
    L += [""]

    L += ["### Ce qui a été vérifié, source par source", "",
          "Le 28/08/2026, contre les pages en ligne et non contre notre propre "
          "base. Un tirage aléatoire par source, plus un contrôle taillé pour "
          "elle : paramètre `country` chez les boutiques Shopify, régime de "
          "frais chez les maisons de ventes, statut de stock chez les "
          "WooCommerce. Les défauts trouvés sont donnés tels quels — une "
          "vérification qui ne trouve jamais rien ne vérifie rien.", ""]
    L += tableau([[metas.get(s, {}).get("name", s),
                   VERIFICATION.get(s, ("non vérifiée", "—"))[0],
                   VERIFICATION.get(s, ("", "—"))[1]]
                  for s, _ in ordre],
                 ["Source", "Tirage vérifié", "Ce qu'il a trouvé"])
    L += [""]

    L += ["### Ce qu'il faut savoir de chacune", ""]
    L += tableau([[metas.get(s, {}).get("name", s), REMARQUES.get(s, "—")]
                  for s, _ in ordre], ["Source", "Remarque"])
    L += [""]

    L += ["### D'où vient la référence, source par source", "",
          "La méthode diffère parce que les sources ne publient pas la même chose. "
          "Un SKU est compté à part : c'est un numéro d'inventaire de marchand, il "
          "n'identifie pas un modèle.", ""]
    L += tableau([[metas.get(s, {}).get("name", s),
                   " · ".join(f"{p or 'aucune'} {milliers(c)}"
                              for p, c in d["provenances"].most_common()) or "aucune",
                   milliers(d["sku"])]
                  for s, d in ordre],
                 ["Source", "Provenance des références", "Dont SKU (écartés)"])
    L += [""]

    L += ["## 2. Les sources sondées puis écartées ou mises de côté", "",
          "Chacune a coûté des requêtes réelles. Le volume indiqué est ce qui serait "
          "**atteignable**, pas ce qui a été collecté.", ""]
    ordre_ecartees = sorted(ECARTEES.items(),
                            key=lambda kv: (kv[1]["verdict"], kv[1]["nom"]))
    L += tableau([[f"**{e['nom']}**", e["type"], e["volume"], e["prix"],
                   e["reference"], e["profondeur"], e["verdict"]]
                  for _, e in ordre_ecartees],
                 ["Source", "Type", "Volume atteignable", "Nature du prix",
                  "Référence", "Profondeur", "Verdict"])
    L += [""]
    L += ["### Pourquoi", ""]
    L += tableau([[e["nom"], e["remarque"]] for _, e in ordre_ecartees],
                 ["Source", "Remarque"])
    L += [""]

    L += ["## 3. Les régimes de prix, et pourquoi ils ne se mélangent pas", "",
          "Trois régimes cohabitent dans la base, et rien sur les pages ne les "
          "signale. Le champ `price_includes_premium` porte l'information ligne "
          "par ligne.", ""]
    premium = collections.defaultdict(collections.Counter)
    with CUMUL.open(encoding="utf-8") as flux:
        for ligne in flux:
            if not ligne.strip():
                continue
            r = json.loads(ligne)
            if r.get("price_includes_premium") is not None:
                premium[r["source_id"]][r["price_includes_premium"]] += 1
    L += tableau([[metas.get(s, {}).get("name", s),
                   "frais acheteur INCLUS" if c.get(True) else "MARTEAU NU",
                   milliers(sum(c.values()))]
                  for s, c in sorted(premium.items(), key=lambda kv: -sum(kv[1].values()))],
                 ["Source", "Régime", "Lignes"])
    L += ["",
          "Comparer un marteau nu à un prix frais inclus fausse l'écart d'environ "
          "un quart. C'est la réserve la plus coûteuse du dossier.", ""]

    RAPPORT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"-> {RAPPORT}")
    print(f"{len(ordre)} sources actives, {len(ECARTEES)} sondées et écartées, "
          f"{len(ordre) + len(ECARTEES)} au total")


if __name__ == "__main__":
    main()
