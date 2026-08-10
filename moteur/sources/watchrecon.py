"""WatchRecon — agregateur d'annonces de forums. Prix DEMANDES.

Acces : HTML structure. Chaque annonce est un `.galleryItemContainer` qui porte
titre, prix, marque, date relative, vendeur et forum d'origine.

Contrainte robots : les parametres `last_days=`, `page_size=`, `sort_*=`,
`filter_*=` sont interdits. On n'utilise que `q=` et `page=`. Les liens marque
du HTML contiennent `last_days=0` — on lit leur texte, on ne les suit pas.
"""
from __future__ import annotations

import datetime as dt
import re

from bs4 import BeautifulSoup
from schema import parse_money, price_point
from utils import get

SOURCE = {
    "id": "watchrecon",
    "name": "WatchRecon",
    "type": "community",
    "price_nature": "asking",
    "access": "HTML structure (.galleryItemContainer)",
    "robots": "OK sous conditions — 'last_days=' et 'page_size=' interdits, non utilises",
}

BASE = "https://www.watchrecon.com/"
# Noms de parametres releves sur #queryForm : 'brand' + 'current_page'.
# (Les tentatives avec 'q=' et 'page=' sont ignorees par le site, qui renvoie
# alors toujours les 50 memes annonces recentes.)
MARQUES = ("rolex", "omega", "patek philippe", "tudor", "cartier",
           "audemars piguet", "seiko", "iwc", "breitling", "jaeger-lecoultre")
PAGES = (1, 2, 3)

# "4 mins ago", "2 days ago", "1 month ago"
_DUREE = re.compile(r"(\d+)\s*(min|hour|day|week|month|year)", re.I)
_EN_JOURS = {"min": 0, "hour": 0, "day": 1, "week": 7, "month": 30, "year": 365}


def _date_depuis_relatif(texte, maintenant):
    """'3 days ago' -> date absolue. La seule date que la source expose."""
    if not texte:
        return None
    trouve = _DUREE.search(texte)
    if not trouve:
        return None
    jours = int(trouve.group(1)) * _EN_JOURS[trouve.group(2).lower()]
    return (maintenant - dt.timedelta(days=jours)).date().isoformat()


def _texte(element, selecteur):
    trouve = element.select_one(selecteur)
    return trouve.get_text(strip=True) if trouve else None


def collect(cap: int = 600):
    raw: list[dict] = []
    journal: list[str] = []
    records: list[dict] = []
    vus: set[str] = set()
    maintenant = dt.datetime.now(dt.timezone.utc)

    for requete in MARQUES:
        if len(records) >= cap:
            break
        for page in PAGES:
            resp = get(BASE, params={"brand": requete, "current_page": page}, pause=1.2)
            raw.append({"url": resp.url, "status": resp.status_code, "payload": resp.text})
            if resp.status_code != 200:
                journal.append(f"{requete} p{page}: HTTP {resp.status_code}")
                break

            soupe = BeautifulSoup(resp.text, "lxml")
            annonces = soupe.select(".galleryItemContainer")
            nouveaux = 0

            for annonce in annonces:
                lien = annonce.select_one(".subjectInfo a")
                titre = lien.get("title") or lien.get_text(strip=True) if lien else None
                montant, devise = parse_money(_texte(annonce, ".priceInfo"))
                if not titre or montant is None:
                    continue

                detail = annonce.select_one('a[href^="detail.php"]')
                identifiant = None
                if detail:
                    cid = re.search(r"cid=(\d+)", detail.get("href", ""))
                    identifiant = cid.group(1) if cid else None
                if identifiant and identifiant in vus:
                    continue
                if identifiant:
                    vus.add(identifiant)
                nouveaux += 1

                records.append(price_point(
                    source_id=SOURCE["id"], source_type=SOURCE["type"],
                    source_url=lien.get("href") if lien else resp.url,
                    external_id=identifiant,
                    price_nature="asking",
                    price_amount=montant, price_currency=devise or "USD",
                    price_date=_date_depuis_relatif(_texte(annonce, ".postDateInfo"), maintenant),
                    brand=_texte(annonce, ".brandInfo"),
                    title=titre,
                    seller=_texte(annonce, ".userNameInfo"),
                ))

            journal.append(f"{requete} p{page}: {nouveaux} annonces sur {len(annonces)} blocs")
            if not annonces:
                break

    # Un plafond atteint = collecte partielle. Le dire, sinon le chiffre passe
    # pour un total alors qu'il est un plancher.
    if len(records) >= cap:
        journal.append(f"TRONQUE: plafond de {cap} atteint — il reste des donnees a prendre")
    return raw, records[:cap], journal
