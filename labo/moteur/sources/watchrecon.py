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
from schema import parse_money, price_point, reference_dans, reference_libre
from utils import get

SOURCE = {
    "id": "watchrecon",
    "name": "WatchRecon",
    "type": "community",
    "price_nature": "asking",
    "access": "HTML structure (.galleryItemContainer)",
    "robots": "OK sous conditions — 'last_days=' et 'page_size=' interdits, non utilises",
    # Le corpus est garanti horloger (agregateur de forums horlogers) : R4 n'a pas
    # a exiger le mot "montre" dans le titre pour valider une marque ambigue.
    "corpus_horloger": True,
}

BASE = "https://www.watchrecon.com/"
# Noms de parametres releves sur #queryForm : 'brand' + 'current_page'.
# (Les tentatives avec 'q=' et 'page=' sont ignorees par le site, qui renvoie
# alors toujours les 50 memes annonces recentes.)
# 24 marques donnaient 3 520 annonces. Le forum en agrege bien davantage : la
# liste suit les marques les plus echangees du dossier, plus les independants
# et les micro-marques qui circulent surtout en occasion.
MARQUES = ("rolex", "omega", "patek philippe", "tudor", "cartier",
           "audemars piguet", "seiko", "iwc", "breitling", "jaeger-lecoultre",
           "grand seiko", "panerai", "zenith", "longines", "vacheron constantin",
           "a. lange & sohne", "chopard", "hublot", "oris", "sinn",
           "universal geneve", "heuer", "blancpain", "glashutte",
           "tag heuer", "nomos", "bell & ross", "bremont", "christopher ward",
           "doxa", "farer", "fortis", "girard-perregaux", "hamilton", "junghans",
           "laco", "longines", "meistersinger", "mido", "ming", "montblanc",
           "movado", "muhle", "nivada", "orient", "piaget", "rado", "raymond weil",
           "richard mille", "roger dubuis", "seagull", "serica", "sinn",
           "stowa", "tissot", "traska", "ulysse nardin", "unimatic", "vulcain",
           "yema", "zodiac", "baume", "bulova", "citizen", "certina", "eterna",
           "franck muller", "frederique constant", "graham", "halios", "jlc",
           "maurice lacroix", "monta", "oak & oscar", "porsche design",
           "seiko prospex", "squale", "steinhart", "tudor black bay")
PAGES = tuple(range(1, 9))

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


def fiche(annonce, url_page: str, maintenant=None) -> dict | None:
    """Un bloc d'annonce -> un enregistrement normalise, ou None si inexploitable.

    Isolee de la collecte pour que moteur/rejoue.py refasse la normalisation sur
    les pages deja stockees. WatchRecon etait la derniere source a melanger
    lecture reseau et normalisation, donc la seule qu'on ne pouvait pas
    reconstruire hors ligne.
    """
    maintenant = maintenant or dt.datetime.now(dt.timezone.utc)
    lien = annonce.select_one(".subjectInfo a")
    titre = (lien.get("title") or lien.get_text(strip=True)) if lien else None
    montant, devise = parse_money(_texte(annonce, ".priceInfo"))
    if not titre or montant is None:
        return None

    detail = annonce.select_one('a[href^="detail.php"]')
    identifiant = None
    if detail:
        cid = re.search(r"cid=(\d+)", detail.get("href", ""))
        identifiant = cid.group(1) if cid else None

    reference = reference_dans(titre)
    provenance = "extrait_titre" if reference else None
    if not reference:
        reference = reference_libre(titre)
        provenance = "jeton_titre" if reference else None

    return price_point(
        source_id=SOURCE["id"], source_type=SOURCE["type"],
        source_url=(lien.get("href") if lien else None) or url_page,
        external_id=identifiant,
        price_nature="asking",
        # La page de liste n'expose aucun statut : une annonce vendue y reste
        # affichee a l'identique. La nature est donc declaree, pas mesuree —
        # c'est le point faible de la source.
        price_nature_provenance="constante_source",
        listing_status="unknown",
        price_amount=montant, price_currency=devise or "USD",
        price_date=_date_depuis_relatif(_texte(annonce, ".postDateInfo"), maintenant),
        brand=_texte(annonce, ".brandInfo"),
        # 1 488 des 4 244 titres (35 %) portent une reference exploitable —
        # 'Ref. IW325502', '126710BLRO', '311.30.40.30.01.001' — et la source
        # sortait a zero reference. C'est le seul champ d'identite qu'elle
        # offre : ne pas le lire la rendait inutilisable pour l'appariement.
        reference=reference, reference_provenance=provenance,
        title=titre,
        seller=_texte(annonce, ".userNameInfo"),
    )


def lots_du_brut(entrees: list, moment=None) -> list[tuple]:
    """(bloc d'annonce, url de la page, moment de lecture) pour chaque annonce.

    PIEGE : la date de cette source est RELATIVE ('3 days ago'). Elle n'a de
    sens que rapportee a l'instant ou la page a ete lue. Rejouer avec l'heure
    du jour daterait toutes les annonces d'aujourd'hui, ce qui est faux et
    silencieux. Le moment est donc passe par l'appelant, qui le lit dans le nom
    du fichier brut.
    """
    trouves = []
    for entree in entrees:
        payload = entree.get("payload") or ""
        if ".galleryItemContainer" not in payload and "galleryItemContainer" not in payload:
            continue
        soupe = BeautifulSoup(payload, "lxml")
        for annonce in soupe.select(".galleryItemContainer"):
            trouves.append((annonce, entree.get("url", BASE), moment))
    return trouves


def collect(cap: int = 20000):
    raw: list[dict] = []
    journal: list[str] = []
    records: list[dict] = []
    vus: set[str] = set()
    maintenant = dt.datetime.now(dt.timezone.utc)

    for requete in MARQUES:
        if len(records) >= cap:
            break
        for page in PAGES:
            try:
                resp = get(BASE, params={"brand": requete, "current_page": page}, pause=1.2)
            except Exception as exc:
                journal.append(f"{requete} p{page}: {type(exc).__name__}")
                break
            raw.append({"url": resp.url, "status": resp.status_code, "payload": resp.text})
            if resp.status_code != 200:
                journal.append(f"{requete} p{page}: HTTP {resp.status_code}")
                break

            annonces = BeautifulSoup(resp.text, "lxml").select(".galleryItemContainer")
            nouveaux = 0
            for annonce in annonces:
                enregistrement = fiche(annonce, resp.url, maintenant)
                if enregistrement is None:
                    continue
                identifiant = enregistrement["external_id"]
                if identifiant and identifiant in vus:
                    continue
                if identifiant:
                    vus.add(identifiant)
                nouveaux += 1
                records.append(enregistrement)

            journal.append(f"{requete} p{page}: {nouveaux} annonces sur {len(annonces)} blocs")
            if not annonces:
                break

    # Un plafond atteint = collecte partielle. Le dire, sinon le chiffre passe
    # pour un total alors qu'il est un plancher.
    if len(records) >= cap:
        journal.append(f"TRONQUE: plafond de {cap} atteint — il reste des donnees a prendre")
    return raw, records[:cap], journal
