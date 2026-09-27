"""Exploration Barnebys — 1er coup d'oeil sur la structure des donnees.

Objectif de ce starter : recuperer une page de resultats "montres", la
sauvegarder, et detecter OU sont les donnees (HTML brut vs JSON embarque),
pour decider de la strategie de scraping.

Usage:
    source ../shared/.venv/bin/activate
    python explore.py
"""
import re
import sys
import json
import pathlib

sys.path.append(str(next(p for p in pathlib.Path(__file__).resolve().parents if (p/"shared"/"utils.py").exists())/"shared"))
from utils import get, samples_dir, save_text, save_json  # noqa: E402

from bs4 import BeautifulSoup

# Page de recherche montres (a ajuster selon ce qu'on trouve)
URL = "https://www.barnebys.com/search/items/?q=rolex"


def main() -> None:
    print(f"GET {URL}")
    resp = get(URL)
    print(f"  statut HTTP: {resp.status_code}  ·  {len(resp.text):,} caracteres")
    if resp.status_code != 200:
        print("  !! statut non-200 — le site bloque peut-etre le scraping simple.")

    samples = samples_dir(__file__)
    save_text(samples / "search_rolex.html", resp.text)

    soup = BeautifulSoup(resp.text, "lxml")
    print(f"  titre de page: {soup.title.string if soup.title else '(aucun)'}")

    # 1) Y a-t-il du JSON-LD (donnees structurees standard) ?
    ld = soup.find_all("script", type="application/ld+json")
    print(f"\n  JSON-LD trouves: {len(ld)}")
    for i, tag in enumerate(ld):
        try:
            data = json.loads(tag.string or "{}")
            save_json(samples / f"jsonld_{i}.json", data)
        except Exception as e:
            print(f"    (json-ld #{i} illisible: {e})")

    # 2) Y a-t-il un blob JSON d'app (Next.js / Nuxt / etc.) ?
    for marker in ("__NEXT_DATA__", "__NUXT__", "window.__INITIAL_STATE__"):
        if marker in resp.text:
            print(f"  blob JSON detecte: {marker}  -> data probablement en JSON embarque")

    # 3) Combien d'elements ressemblant a des lots ?
    candidates = soup.select("[class*=item], [class*=lot], article, [data-testid]")
    print(f"\n  elements candidats (lots ?): {len(candidates)}")

    print("\nFait. Regarde samples/ : si les prix sont dans search_rolex.html, "
          "scraping HTML direct ; s'ils sont dans un jsonld_*.json ou un blob "
          "__NEXT_DATA__, on lit le JSON (plus propre). Sinon -> playwright.")


if __name__ == "__main__":
    main()
