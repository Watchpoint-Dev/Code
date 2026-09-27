"""Roni Madhvani — mesure de ce que l'API Store rend reellement.

Rejoue la decision SANS requete reseau, depuis `samples/store_v1_products.json`.
Si le site sort un jour de son « Coming Soon », c'est ce script qu'on relance
avant de reconsiderer la source.

    cd /Users/vale/Desktop/WP/labo && shared/.venv/bin/python essais/roni-madhvani/explore.py
"""
from __future__ import annotations

import collections
import json
import pathlib
import sys

ICI = pathlib.Path(__file__).resolve().parent
LABO = ICI.parent.parent
sys.path[:0] = [str(LABO / "moteur"), str(LABO / "shared")]

from sources import _woo  # noqa: E402

SOURCE = {"id": "ronimadhvani", "name": "Roni Madhvani", "type": "dealer",
          "price_nature": "asking"}

# Le jeu de demonstration livre avec WooCommerce (woocommerce/sample-data). Sa
# presence est la preuve que la boutique n'a jamais ete remplie.
DEMO_WOO = {"WordPress Pennant", "Logo Collection", "Beanie with Logo",
            "T-Shirt with Logo", "Single", "Album", "Polo", "Long Sleeve Tee",
            "Sunglasses", "Cap", "Beanie", "T-Shirt", "Hoodie with Zipper",
            "Hoodie with Pocket", "Belt", "Hoodie with Logo", "Hoodie",
            "V-Neck T-Shirt"}


def main() -> None:
    produits = json.loads((ICI / "samples/store_v1_products.json").read_text())
    epuises = json.loads((ICI / "samples/store_v1_products_outofstock.json").read_text())
    print(f"API Store : {len(produits)} fiches en vitrine (X-WP-Total = 18), "
          f"{len(epuises)} epuisees (X-WP-Total = 0)")

    print("\n--- ce que la boutique vend ---")
    for nom, n in collections.Counter(
            c.get("name") for p in produits for c in (p.get("categories") or [])).most_common():
        print(f"  {n:3d}  {nom}")

    noms = {p.get("name") for p in produits}
    print(f"\nfiches appartenant au jeu de demonstration WooCommerce : "
          f"{len(noms & DEMO_WOO)}/{len(noms)}")
    print("fiches hors jeu de demonstration :", sorted(noms - DEMO_WOO) or "aucune")

    print("\n--- ce que l'API publie par fiche ---")
    print("  currency_minor_unit :", dict(collections.Counter(
        (p.get("prices") or {}).get("currency_minor_unit") for p in produits)))
    print("  devise              :", dict(collections.Counter(
        (p.get("prices") or {}).get("currency_code") for p in produits)))
    print("  date_created        :", dict(collections.Counter(
        p.get("date_created") for p in produits)))
    print("  attribut Reference  :", dict(collections.Counter(
        _woo._attribut(p, _woo.LIBELLES_REFERENCE) for p in produits)))
    print("  attributs presents  :", dict(collections.Counter(
        a.get("name") for p in produits for a in (p.get("attributes") or []))))

    # Le moteur generique normalise sans broncher : c'est bien le probleme.
    records = [r for r in (_woo.fiche(p, SOURCE) for p in produits) if r]
    print(f"\n{len(records)} fiches passeraient la normalisation — "
          f"toutes sans date ({sum(1 for r in records if r.get('price_date'))} datee) "
          f"et aucune n'est une montre.")


if __name__ == "__main__":
    main()
