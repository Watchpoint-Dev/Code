"""Everest Horology — mesure de la composition du catalogue et du filtre.

Rejoue la decision SANS une seule requete reseau : tout part de
`samples/products_page1.json`, qui contient le catalogue entier (248 fiches,
la page 2 est vide). C'est ce qui permet de rejuger la source si son catalogue
change de nature un jour.

    backend/.venv/bin/python research/sources/everest/explore.py
"""
from __future__ import annotations

from watchpoint import config

import collections
import json
import pathlib
import sys

ICI = pathlib.Path(__file__).resolve().parent
LABO = config.RACINE.parent

from watchpoint.filtrage.filtre import filtre          # noqa: E402
from watchpoint.sources import _shopify       # noqa: E402

SOURCE = {"id": "everest", "name": "Everest Horology", "type": "dealer",
          "price_nature": "asking"}


def main() -> None:
    produits = json.loads((ICI / "samples/products_page1.json").read_text())["products"]
    print(f"catalogue complet : {len(produits)} fiches (page 2 vide — voir samples/)")

    print("\n--- ce que le marchand declare vendre (product_type) ---")
    for libelle, n in collections.Counter(
            (p.get("product_type") or "(vide)") for p in produits).most_common():
        print(f"  {n:4d}  {libelle}")

    # Normalisation par le moteur generique, telle qu'un adaptateur la ferait.
    records = [r for r in (
        _shopify.fiche(p, SOURCE, devise="USD", domaine="www.everestbands.com",
                       moment="2026-09-21") for p in produits) if r]
    print(f"\n{len(records)} fiches normalisables ({len(produits) - len(records)} "
          f"sous le plancher de prix)")

    # Le filtre, appele EXACTEMENT comme moteur/run.py l'appelle : avec la
    # marque et la categorie publiee. Sans la categorie, le verdict change du
    # tout au tout (191 rejets avec, 55 sans) — la mesure n'a de sens que
    # fidele au pipeline.
    tri = filtre()
    verdicts, regles, gardes = collections.Counter(), collections.Counter(), []
    for r in records:
        v = tri.verdict(r.get("title") or "", "MARKETPLACE", maker=r.get("brand"),
                        categorie_source=r.get("source_category"))
        verdicts[v["verdict"]] += 1
        regles[(v["verdict"], v["rule"])] += 1
        if v["verdict"] != "REJETER":
            gardes.append((v["verdict"], v["rule"], r))

    print("\n--- verdicts du filtre ---")
    print(dict(verdicts))
    for (verdict, regle), n in regles.most_common():
        print(f"  {n:4d}  {verdict} / {regle}")

    print(f"\n--- {len(gardes)} accessoires que le filtre ne rejette PAS ---")
    for verdict, regle, r in gardes:
        print(f"  {verdict:11s} {regle:4s} ref={str(r['reference'])[:12]:12s} "
              f"({r['reference_provenance']:20s}) "
              f"{r['price_currency']} {r['price_amount']:8.2f}  {r['title'][:70]}")

    # La ou ca fait mal : une reference de montre reelle collee a un prix
    # d'accessoire. C'est la limite L1 du filtre, en clair.
    print("\n--- references de montres extraites de titres d'accessoires ---")
    provenances = collections.Counter(
        r["reference_provenance"] for r in records if r["reference"])
    print(f"  {sum(provenances.values())}/{len(records)} fiches portent une "
          f"'reference' : {dict(provenances)}")

    print("\n--- 'vendu' deduit de available=false chez un fabricant de serie ---")
    print(" ", dict(collections.Counter(r["price_nature"] for r in records)))


if __name__ == "__main__":
    main()
