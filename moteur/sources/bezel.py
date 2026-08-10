"""Bezel — marketplace. Annonces structurees : la source la plus riche en specs.

Acces : `__NEXT_DATA__` des pages modele, decouvertes par le sitemap. Les specs
(marque, reference, matiere, mouvement, taille) viennent du modele ; le prix et
l'etat viennent de chaque annonce rattachee.
"""
from __future__ import annotations

import json
import re

from schema import price_point
from utils import get

SOURCE = {
    "id": "bezel",
    "name": "Bezel",
    "type": "marketplace",
    "price_nature": "asking",
    "access": "__NEXT_DATA__ pageProps.listings",
    "robots": "OK — seul '?searchQuery=' est interdit, on passe par le sitemap",
}

SITEMAP = "https://shop.getbezel.com/server-sitemap.xml"
MODELES_MAX = 40
ANNONCES_PAR_MODELE = 8


def _next_data(html):
    match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None


def collect(cap: int = 400):
    raw: list[dict] = []
    journal: list[str] = []
    records: list[dict] = []

    index = get(SITEMAP, pause=1.0)
    raw.append({"url": index.url, "status": index.status_code, "payload": index.text})
    if index.status_code != 200:
        journal.append(f"sitemap: HTTP {index.status_code}")
        return raw, records, journal

    sous_sitemaps = re.findall(r"<loc>([^<]+/sitemap/models/[^<]+)</loc>", index.text)
    if not sous_sitemaps:
        journal.append("aucun sitemap de modeles")
        return raw, records, journal

    # On lit TOUS les sous-sitemaps, puis on echantillonne A PAS REGULIER sur la
    # liste complete. Prendre les N premieres URLs du shard 0 donnait 89 annonces
    # dont 81 Patek : la mediane qui en sortait (131 070 USD) etait un artefact
    # d'echantillonnage, et elle est partie dans un document partage.
    journal.append(f"{len(sous_sitemaps)} sous-sitemaps de modeles")
    toutes: list[str] = []
    for sitemap in sous_sitemaps:
        pages = get(sitemap, pause=1.2)
        raw.append({"url": pages.url, "status": pages.status_code, "payload": pages.text})
        if pages.status_code != 200:
            journal.append(f"sous-sitemap {sitemap.rsplit('/', 1)[-1]}: HTTP {pages.status_code}")
            continue
        toutes += re.findall(r"<loc>([^<]+/watches/[^<]+)</loc>", pages.text)

    if not toutes:
        journal.append("aucune page modele trouvee dans les sous-sitemaps")
        return raw, records, journal

    pas = max(1, len(toutes) // MODELES_MAX)
    urls_modeles = toutes[::pas][:MODELES_MAX]
    journal.append(f"{len(toutes)} modeles au catalogue — echantillon regulier "
                   f"de {len(urls_modeles)} (1 sur {pas})")

    for url in urls_modeles:
        if len(records) >= cap:
            break
        resp = get(url, pause=1.2)
        raw.append({"url": resp.url, "status": resp.status_code, "payload": resp.text})
        if resp.status_code != 200:
            continue
        data = _next_data(resp.text)
        if not data:
            continue
        props = (data.get("props") or {}).get("pageProps") or {}
        modele = props.get("model") or {}
        annonces = props.get("listings") or []

        for annonce in annonces[:ANNONCES_PAR_MODELE]:
            cents = annonce.get("priceCents") or (annonce.get("fixedPriceInfo") or {}).get("priceCents")
            if not cents:
                continue
            statut = str(annonce.get("status") or "").upper()
            records.append(price_point(
                source_id=SOURCE["id"], source_type=SOURCE["type"],
                source_url=url, external_id=str(annonce.get("id") or annonce.get("uuid") or ""),
                # une annonce close est un prix VENDU, une annonce vivante un prix DEMANDE
                price_nature="sold" if "SOLD" in statut else "asking",
                price_amount=float(cents) / 100, price_currency="USD",
                price_date=annonce.get("created"),
                brand=(modele.get("brand") or {}).get("name") if isinstance(modele.get("brand"), dict) else modele.get("brand"),
                model=modele.get("displayName") or modele.get("name"),
                reference=modele.get("referenceNumber"),
                title=modele.get("displayName"),
                case_material=modele.get("caseMaterials"),
                case_size_mm=modele.get("caseSize"),
                movement=modele.get("movementType"),
                dial_color=modele.get("dialColor"),
                condition=annonce.get("condition"),
                seller="Bezel",
            ))

    journal.append(f"{len(records)} annonces extraites")
    # Un plafond atteint = collecte partielle. Le dire, sinon le chiffre passe
    # pour un total alors qu'il est un plancher.
    if len(records) >= cap:
        journal.append(f"TRONQUE: plafond de {cap} atteint — il reste des donnees a prendre")
    return raw, records[:cap], journal
