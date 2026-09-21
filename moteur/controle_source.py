"""Le controle de vraisemblance — nos lignes disent-elles la verite ?

    cd ~/Desktop/WP/labo
    shared/.venv/bin/python moteur/controle_source.py            # 5 lignes par source
    shared/.venv/bin/python moteur/controle_source.py christies 12

Toutes les autres passes mesurent la base contre elle-meme : combien de champs
remplis, combien de lignes gardees. Aucune ne verifie que ce qu'on a stocke
correspond a ce que la source affiche. C'est pourtant la seule question qui
compte : une base coherente peut etre entierement fausse.

Le principe est brutal et volontairement naif. On tire des lignes au hasard, on
retourne sur leur `source_url`, et on cherche dans la page :

    le MONTANT      dans toutes les ecritures plausibles (1234, 1 234, 1.234,
                    1,234) — un prix mal parse ne se retrouvera pas
    la REFERENCE    telle qu'on l'a extraite
    le STATUT       les mots qui disent vendu, disponible, invendu

Ce controle ne prouve pas qu'une ligne est juste : une page peut avoir change,
un lot peut avoir ete retire, un marchand peut avoir baisse son prix. Il prouve
qu'une ligne est INVRAISEMBLABLE quand rien ne correspond, et c'est deja ce
qu'on cherche. Le rapport distingue donc l'echec de la page introuvable.
"""
from __future__ import annotations

import collections
import json
import pathlib
import random
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "shared"))

from utils import get  # noqa: E402

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"
CUMUL = DATA / "price_points.jsonl"
RAPPORT = DATA / "controle_source.json"

# Certaines sources refusent les en-tetes navigateur (cf. sources/christies.py).
import requests  # noqa: E402
ENTETES_PAR_SOURCE = {"christies": {"User-Agent": requests.utils.default_user_agent()}}

# Les boutiques Shopify localisent leurs prix. Interroger la page publique sans
# parametre de devise renvoie un montant CONVERTI — mesure du 25/08/2026 sur
# Craft & Tailored : 8 794 sans devise contre 10 750 avec `currency=USD`, soit
# -18,2 %. Le controle doit donc demander la fiche dans la meme devise que la
# collecte, sinon il accuse la base d'une erreur qui est la sienne.
# Et ce n'est pas la devise qui commande, c'est le PAYS. Mesure du 25/08/2026
# sur six ecarts, tous tombes sur deux ratios exacts : 0,8333 = 1/1,2, la TVA
# britannique retiree chez Berry's et CW Sellors ; 0,9084 chez Montredo, la
# bascule sur le marche suisse annoncee par sa fiche de preuve. Les deux
# disparaissent des qu'on envoie `country`.
DEVISE_SHOPIFY = {
    "craft_and_tailored": ("USD", None), "analogshift": ("USD", "US"),
    "hairspring": ("USD", "US"), "berrys": ("GBP", "GB"),
    "cwsellors": ("GBP", "GB"), "montredo": ("EUR", "DE"),
}

VENDU = re.compile(r"\b(sold|vendu|verkauft|adjug|hammer|realis|out of stock|"
                   r"sold out|no longer available)\b", re.I)
DISPO = re.compile(r"\b(add to (cart|basket|bag)|in stock|available|acheter|"
                   r"buy now|panier)\b", re.I)
BALISES = re.compile(r"<[^>]+>")


def ecritures(montant: float) -> list[str]:
    """Toutes les facons plausibles d'ecrire ce montant sur une page."""
    entier = int(round(montant))
    formes = {str(entier), f"{entier:,}", f"{entier:,}".replace(",", " "),
              f"{entier:,}".replace(",", "."), f"{entier:,}".replace(",", "'")}
    if abs(montant - entier) > 0.004:
        formes.add(f"{montant:,.2f}")
        formes.add(f"{montant:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    # Le marteau nu quand la page n'affiche que le prix frais inclus, et
    # l'inverse : on tolere les taux de frais usuels, en le disant.
    return sorted(formes, key=len, reverse=True)


def controle(ligne: dict) -> dict:
    url = ligne.get("source_url") or ""
    resultat = {"source": ligne["source_id"], "url": url,
                "montant": ligne.get("price_amount"),
                "reference": ligne.get("reference"),
                "statut": ligne.get("listing_status"), "verdict": None}
    if not url.startswith("http"):
        resultat["verdict"] = "PAS D'URL"
        return resultat

    # WatchRecon renvoie vers l'annonce d'origine, sur un forum ou sur Reddit.
    # Reddit sert un mur de connexion a tout client non authentifie : la page
    # est illisible, ce qui ne dit rien sur notre ligne. On verifie donc sur la
    # fiche WatchRecon elle-meme, qui est la ou le prix a ete lu.
    if ligne["source_id"] == "watchrecon" and ligne.get("external_id"):
        url = f"https://www.watchrecon.com/detail.php?cid={ligne['external_id']}"
        resultat["url"] = url

    entetes = ENTETES_PAR_SOURCE.get(ligne["source_id"], {})
    devise, pays = DEVISE_SHOPIFY.get(ligne["source_id"], (None, None))
    parametres = {}
    if devise:
        url = url + ".json"
        parametres = {"currency": devise}
        if pays:
            parametres["country"] = pays
        resultat["url"] = url
    try:
        reponse = get(url, params=parametres, pause=1.2, essais=2, headers=entetes)
    except Exception as exc:
        resultat["verdict"] = f"INJOIGNABLE ({type(exc).__name__})"
        return resultat
    if reponse.status_code != 200:
        resultat["verdict"] = f"HTTP {reponse.status_code}"
        return resultat

    texte = BALISES.sub(" ", reponse.text)
    plat = re.sub(r"\s+", " ", texte)

    # Sur une fiche Shopify on peut comparer le nombre exactement, sans passer
    # par les ecritures possibles : la reponse est du JSON.
    if devise:
        try:
            variante = (json.loads(reponse.text)["product"]["variants"] or [{}])[0]
            affiche = float(str(variante.get("price")).replace(",", ""))
            resultat["prix_source"] = affiche
            resultat["montant_trouve"] = abs(affiche - (ligne.get("price_amount") or -1)) < 0.51
            resultat["reference_trouvee"] = bool(
                ligne.get("reference")
                and re.search(re.escape(str(ligne["reference"])), reponse.text, re.I))
            resultat["page_dit_vendu"] = variante.get("available") is False
            resultat["page_dit_dispo"] = variante.get("available") is True
            resultat["verdict"] = ("MONTANT CONFIRME" if resultat["montant_trouve"]
                                   else f"ECART ({affiche} vs {ligne.get('price_amount')})")
            return resultat
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            resultat["verdict"] = "FICHE JSON ILLISIBLE"
            return resultat

    montant = ligne.get("price_amount")
    resultat["montant_trouve"] = bool(
        montant and any(f in plat for f in ecritures(montant)))
    reference = ligne.get("reference")
    resultat["reference_trouvee"] = bool(
        reference and re.search(re.escape(str(reference)), plat, re.I))
    resultat["page_dit_vendu"] = bool(VENDU.search(plat))
    resultat["page_dit_dispo"] = bool(DISPO.search(plat))

    if resultat["montant_trouve"]:
        resultat["verdict"] = "MONTANT CONFIRME"
    elif reference and resultat["reference_trouvee"]:
        resultat["verdict"] = "REFERENCE SEULE"
    else:
        resultat["verdict"] = "RIEN NE CORRESPOND"
    return resultat


def main() -> None:
    args = [a for a in sys.argv[1:]]
    sources_voulues = [a for a in args if not a.isdigit()]
    par_source = int(next((a for a in args if a.isdigit()), 5))

    lignes = collections.defaultdict(list)
    with CUMUL.open(encoding="utf-8") as flux:
        for ligne in flux:
            if not ligne.strip():
                continue
            r = json.loads(ligne)
            if r.get("filter_verdict") != "GARDER":
                continue
            if sources_voulues and r["source_id"] not in sources_voulues:
                continue
            lignes[r["source_id"]].append(r)

    alea = random.Random(20260825)  # tirage reproductible
    rapport = []
    for source, toutes in sorted(lignes.items()):
        echantillon = alea.sample(toutes, min(par_source, len(toutes)))
        print(f"\n{source} — {len(echantillon)} lignes tirees sur {len(toutes)}")
        for ligne in echantillon:
            r = controle(ligne)
            rapport.append(r)
            montant = f"{r['montant']:,.0f}".replace(",", " ") if r["montant"] else "?"
            print(f"   {r['verdict']:<20} {montant:>10} {ligne.get('price_currency') or '':<4}"
                  f" {str(r['reference'] or '—')[:14]:<15} {r['url'][-58:]}")

    RAPPORT.write_text(json.dumps(rapport, ensure_ascii=False, indent=1), encoding="utf-8")
    compte = collections.Counter(r["verdict"] for r in rapport)
    print(f"\n{'=' * 74}")
    for verdict, n in compte.most_common():
        print(f"  {n:>4}  {verdict}")
    print(f"\n-> {RAPPORT}")


if __name__ == "__main__":
    main()
