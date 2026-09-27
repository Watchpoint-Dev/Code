"""Artcurial — maison de ventes. Prix REALISES depuis 2007 : la profondeur.

8 454 lots de montres sur 88 ventes, 19 ans d'historique date. C'est la source
qui fait passer la base de deux ans de profondeur a dix-neuf.

Acces : API JSON interne 'ACE', sans authentification ni JavaScript. Deux appels
enchaines — la liste des ventes filtree sur la specialite WATCHES, puis les lots
de chaque vente. Aucune jointure.

Les pieges, tous releves lors de l'audit du 11/08/2026 et traites ici :

  DEUX PRIX COEXISTENT. `adjudicationPrice` est le marteau, `finalPrice` le prix
  frais acheteur inclus. Le rapport va de 1,23 a 1,324 selon la juridiction.
  Prendre finalPrice en croyant lire un marteau surevalue de 30 % — on charge
  donc adjudicationPrice, et finalPrice part dans un champ separe.

  LES INVENDUS SONT ABSENTS. Sur 416 lots temoins, 416 en status=SOLD. Un taux
  de vente de 100 % n'existe pas dans ce metier : la lecture honnete est que
  l'API ne sert que les lots vendus. La base heritera d'un biais de survie, et
  il faut le dire plutot que de le decouvrir plus tard dans une moyenne.

  LA MARQUE N'EXISTE QUE SUR LES VENTES RECENTES. La fiche de preuve annoncait
  qu'aucun champ structure n'existait ; c'est inexact, verifie le 25/08/2026 :
  `descriptions.{LOCALE}.brand` et `.model` sont remplis sur la vente de 2026 et
  vides sur celles de 2007 et 2016. Il faut donc les deux mecanismes — le champ
  quand la source le publie, la detection dans le titre sinon, avec le
  dictionnaire du filtre (213 marques et leurs alias, deja entretenu).
  La reference, elle, n'est jamais un champ : elle se lit dans le titre
  ('ref. 1603') ou dans le corps ('<p>Ref. C17391</p>').

  DEUX JURIDICTIONS. Les ventes se repartissent entre Paris (tenant fr) et
  Monaco (tenant mc), dont les regimes de frais different. Le tenant voyage donc
  avec le vendeur, sinon toute analyse des frais melange deux fiscalites.

  L'API ANNONCE 88 VENTES ET EN SERT 87. L'ecart est stable. Un controle naif
  `len(content) == totalElements` ferait echouer la collecte a chaque passage.

Fiche de preuve : preuves/fiches/artcurial.json
"""
from __future__ import annotations

import html
import json
import re

from filtre import filtre
from schema import price_point, reference_dans
from utils import get

SOURCE = {
    "id": "artcurial",
    "name": "Artcurial",
    "type": "auction",
    "price_nature": "realised",
    "access": "API JSON interne /ace (Nuxt runtimeConfig)",
    "robots": "OK — aucun Disallow sur /ace, robots.txt relu le 11/08/2026",
    # Le corpus est garanti horloger (vente de la specialite MONTRES uniquement) : R4 n'a pas
    # a exiger le mot "montre" dans le titre pour valider une marque ambigue.
    "corpus_horloger": True,
    "reserve": "l'API ne sert que les lots vendus : biais de survie assume",
}

BASE = "https://www.artcurial.com/ace"
VENTES = f"{BASE}/sales/results"
FILTRE_MONTRES = "specialties.specialty.ref,MTCA,WATCHES"
LOTS_PAR_PAGE = 300

_REFERENCE = re.compile(
    r"(?:r[ée]f(?:\.|erence|érence)?|n[°o]|no\.)\s*:?\s*([A-Z0-9][A-Z0-9./-]{2,15})", re.I)
_BALISES = re.compile(r"<[^>]+>")


def _texte(html_brut) -> str:
    """La description est du HTML : on en sort du texte, une seule fois."""
    if not html_brut:
        return ""
    return html.unescape(_BALISES.sub(" ", str(html_brut))).replace("\xa0", " ").strip()


def _fiche_texte(lot) -> dict:
    """Titre, marque, modele et texte du lot, quelle que soit la locale.

    Supposer la cle 'FRENCH' perdrait silencieusement les ventes anglophones —
    dont la plus recente et la plus chere du corpus. Et les champs `brand` et
    `model` n'existent QUE sur les ventes recentes : mesure faite le 25/08/2026,
    ils sont remplis sur la vente 2026 et vides sur celles de 2007 et 2016. Il
    faut donc les deux mecanismes, le champ quand il existe, la detection dans
    le titre sinon.
    """
    descriptions = lot.get("descriptions") or {}
    if not isinstance(descriptions, dict):
        return {}
    titres, textes, marque, modele = [], [], None, None
    for bloc in descriptions.values():
        if not isinstance(bloc, dict):
            continue
        titres.append(_texte(bloc.get("titleWithHtml") or bloc.get("title")))
        textes.append(_texte(bloc.get("descriptionWithHtml") or bloc.get("description")))
        marque = marque or (bloc.get("brand") or "").strip() or None
        modele = modele or (bloc.get("model") or "").strip() or None
    return {
        "titre": " ".join(t for t in titres if t)[:300] or None,
        "texte": " ".join(t for t in textes if t),
        "marque": marque,
        "modele": modele,
    }


# La description d'Artcurial n'est pas de la prose libre : elle est etiquetee en
# francais. Mesure du 25/08/2026 sur 1 992 lots : 'Boitier :' 83 %, 'Cadran :'
# 66 %, 'Mouvement :' 64 %, et une ligne 'Vers AAAA' qui date la fabrication.
# Ces champs etaient a zero dans la base.
_CHAMP_FR = {
    "movement": re.compile(r"Mouvement\s*:\s*([^\n]{2,90})", re.I),
    "dial_color": re.compile(r"Cadran\s*:\s*([^\n,]{2,60})", re.I),
    "boitier": re.compile(r"Bo[iî]tier\s*:\s*([^\n]{2,90})", re.I),
}
_ANNEE_FR = re.compile(r"\bvers\s+(1[89]\d{2}|20[0-2]\d)\b", re.I)
# Les matieres telles qu'elles sont ecrites dans la premiere ligne du lot :
# "Montre-bracelet de plongee en acier et or rose 18k (750)".
_MATIERES = (
    ("or rose", "or rose"), ("or jaune", "or jaune"), ("or gris", "or gris"),
    ("or blanc", "or blanc"), ("platine", "platine"), ("titane", "titane"),
    ("acier", "acier"), ("argent", "argent"), ("bronze", "bronze"),
    ("ceramique", "ceramique"), ("céramique", "ceramique"), ("plaque", "plaque or"),
)


def _matiere(texte):
    minuscule = str(texte or "").lower()
    trouvees = [propre for motif, propre in _MATIERES if motif in minuscule]
    return " et ".join(dict.fromkeys(trouvees))[:60] or None


def _specifications(texte) -> dict:
    if not texte:
        return {}
    specs = {}
    for cle, motif in _CHAMP_FR.items():
        trouve = motif.search(texte)
        if trouve:
            specs[cle] = trouve.group(1).strip(" .,;")
    annee = _ANNEE_FR.search(texte)
    if annee:
        specs["year"] = int(annee.group(1))
    return specs


def _reference(texte):
    return reference_dans(texte)


def _ventes_montres(raw, journal):
    params = {"filter": FILTRE_MONTRES, "page": 0, "size": 500,
              "sort": "effectiveDate,desc"}
    try:
        resp = get(VENTES, params=params, pause=1.0)
    except Exception as exc:
        journal.append(f"liste des ventes: {type(exc).__name__}")
        return []
    raw.append({"url": resp.url, "status": resp.status_code, "payload": resp.text})
    if resp.status_code != 200:
        journal.append(f"liste des ventes: HTTP {resp.status_code}")
        return []
    try:
        donnee = json.loads(resp.text)
    except json.JSONDecodeError:
        journal.append("liste des ventes: JSON illisible")
        return []

    ventes = donnee.get("content") or []
    annonce = donnee.get("totalElements")
    # L'ecart de 1 est connu et stable : on le signale, on n'echoue pas dessus.
    if annonce is not None and annonce != len(ventes):
        journal.append(f"l'API annonce {annonce} ventes et en sert {len(ventes)} "
                       f"— ecart connu, non bloquant")
    return ventes


def fiche(lot: dict, ref_vente: str, tenant=None) -> dict | None:
    """Un lot Artcurial -> un enregistrement normalise.

    Isolee de la collecte pour que moteur/rejoue.py refasse la normalisation sur
    le brut deja stocke. Le champ `type` est repris ici : il vaut WATCH_VARIOUS,
    JEWELRY, OTHER... C'est la categorie publiee par la maison, celle que R0 lit.
    Le champ `category`, lui, ne sert a rien pour trier des montres : il classe
    les memes lots en ART_WORK et JEWELRY sans logique horlogere.
    """
    marteau = lot.get("adjudicationPrice")
    if not marteau:
        return None
    fiche_texte = _fiche_texte(lot)
    titre = fiche_texte.get("titre")
    if not titre:
        return None

    verdict = filtre().verdict(titre, "AUCTION")
    texte = fiche_texte.get("texte") or ""
    reference = _reference(titre)
    provenance = "extrait_titre" if reference else None
    if not reference:
        # 495 des 2 912 references d'Artcurial viennent en realite d'ici, et
        # sortaient etiquetees 'extrait_titre'. Une provenance fausse est pire
        # qu'une reference absente : elle donne confiance a tort.
        reference = _reference(texte)
        provenance = "extrait_description" if reference else None
    specs = _specifications(texte)

    return price_point(
        source_id=SOURCE["id"], source_type=SOURCE["type"],
        # /fr/lot-{uuid} rendait 404 sur toutes les lignes : verifie le
        # 25/08/2026. Le site lie ses lots par /ventes/{vente}/lots/{index}-{sous},
        # comme on peut le lire dans les liens de sa propre page d'accueil.
        source_url=(f"https://www.artcurial.com/ventes/{ref_vente}"
                    f"/lots/{lot.get('index')}-{lot.get('subIndex') or 'a'}"),
        external_id=f"{ref_vente}-{lot.get('index')}{lot.get('subIndex') or ''}",
        price_nature="realised",
        price_nature_provenance="champ_dedie",
        listing_status="sold",
        # adjudicationPrice est le marteau nu ; finalPrice, ecarte ici, vaut
        # 1,23 a 1,32 fois plus.
        price_includes_premium=False,
        price_amount=float(marteau),
        price_currency=lot.get("currency") or "EUR",
        price_date=lot.get("adjudicationDate"),
        estimate_low=lot.get("low"), estimate_high=lot.get("high"),
        brand=fiche_texte.get("marque") or verdict.get("brand"),
        model=fiche_texte.get("modele"),
        reference=reference,
        reference_provenance=provenance,
        source_category=lot.get("type"),
        year=specs.get("year"),
        # La matiere se lit dans la premiere ligne du lot, pas dans un champ.
        case_material=_matiere(texte[:300]),
        movement=specs.get("movement"),
        dial_color=specs.get("dial_color"),
        title=titre,
        seller=f"Artcurial {tenant}" if tenant else "Artcurial",
    )


def lots_du_brut(entrees: list) -> list[tuple]:
    """(lot, ref_vente, tenant) pour chaque lot d'une collecte deja stockee.

    La reference de vente n'est pas dans le lot : elle est dans l'URL appelee.
    """
    trouves = []
    for entree in entrees:
        url = entree.get("url", "")
        vente = re.search(r"/sales/([^/]+)/items", url)
        if not vente:
            continue
        try:
            contenu = json.loads(entree.get("payload", "")).get("content") or []
        except (json.JSONDecodeError, AttributeError):
            continue
        for lot in contenu:
            trouves.append((lot, vente.group(1), lot.get("tenant")))
    return trouves


def collect(cap: int = 25000):
    raw: list[dict] = []
    journal: list[str] = []
    records: list[dict] = []
    tri = filtre()

    ventes = _ventes_montres(raw, journal)
    journal.append(f"{len(ventes)} ventes montres")
    # Un meme lot est servi deux fois quand la vente a deux vacations — une a
    # Paris, une a Monaco (vacationRef 'fr-2462-1' et 'mc-2462-1'). Meme lot,
    # meme prix, deux uuid. Sans ce garde-fou, 690 doublons entrent en base.
    vus: set[tuple] = set()

    for vente in ventes:
        if len(records) >= cap:
            break
        ref_vente = vente.get("ref") or vente.get("saleRef") or vente.get("id")
        if not ref_vente:
            continue
        tenant = vente.get("tenant")
        # La maison peut demander de masquer ses adjudications : on respecte.
        if vente.get("hideAdjudicationResult"):
            journal.append(f"vente {ref_vente}: adjudications masquees par la maison, ignoree")
            continue

        page = 0
        while len(records) < cap:
            try:
                resp = get(f"{BASE}/sales/{ref_vente}/items",
                           params={"page": page, "size": LOTS_PAR_PAGE}, pause=1.0)
            except Exception as exc:
                journal.append(f"vente {ref_vente} p{page}: {type(exc).__name__}")
                break
            raw.append({"url": resp.url, "status": resp.status_code, "payload": resp.text})
            if resp.status_code != 200:
                journal.append(f"vente {ref_vente} p{page}: HTTP {resp.status_code}")
                break
            try:
                lots = (json.loads(resp.text).get("content") or [])
            except json.JSONDecodeError:
                break
            if not lots:
                break

            for lot in lots:
                identite = (ref_vente, lot.get("index"), lot.get("subIndex"))
                if identite in vus:
                    continue
                vus.add(identite)
                enregistrement = fiche(lot, ref_vente, tenant)
                if enregistrement is not None:
                    records.append(enregistrement)

            if len(lots) < LOTS_PAR_PAGE:
                break
            page += 1

    if len(records) >= cap:
        journal.append(f"TRONQUE: plafond de {cap} atteint — il reste des donnees a prendre")
    return raw, records[:cap], journal
