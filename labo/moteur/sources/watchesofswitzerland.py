"""Watches of Switzerland — detaillant agree britannique. Le prix du NEUF.

C'est ce qui la rend unique dans le dossier : toutes nos autres sources donnent
du prix d'occasion — demande, vendu ou marteau. Un detaillant agree affiche le
tarif officiel de la marque sur les montres neuves. C'est la cinquieme nature de
prix, `msrp`, dont la base ne contient aujourd'hui aucune ligne.

Acces : ce n'est PAS du Shopify. C'est SAP Commerce Cloud (Hybris) avec son API
REST OCC exposee publiquement, plus un sitemap produit non pagine de 33 106 URL.

Le cout est la contrainte : robots.txt interdit `/search` et tout parametre
`q=`, donc aucun endpoint de liste n'est utilisable. Une fiche = une requete.
Aspirer les 33 106 produits demanderait environ neuf heures. On borne donc la
collecte et on choisit ce qu'on prend, en le disant.

Trois pieges, releves a l'audit du 11/08/2026 et confirmes le 27/08 :

  LE CHAMP `manufacturer` N'EST PAS LA MARQUE. Il vaut 'Pre-Owned Blancpain',
  'Rolex Certified Pre-Owned', 'Pre-Owned NOMOS Glashutte'. L'ingerer tel quel
  fabriquerait autant de fausses marques que de prefixes commerciaux.

  LE SITEMAP GARDE DES FICHES EPUISEES. `stockLevelStatus` vaut souvent
  'outOfStock' alors que le prix reste affiche. Un prix affiche sur une fiche
  epuisee reste un prix demande valide, mais ce n'est pas une disponibilite.

  NE PAS RECONNAITRE LE PRE-DETENU AU MOT 'Certified'. Une grande partie des
  'Certified' du sitemap sont des Omega NEUVES 'Certified By...'. Le marqueur
  fiable est 'Pre+Owned' dans l'URL.

Fiche de preuve : preuves/fiches/watches_of_switzerland.json
"""
from __future__ import annotations

import json
import re

from filtre import filtre
from schema import parse_money, price_point
from utils import get

SOURCE = {
    "id": "watchesofswitzerland",
    "name": "Watches of Switzerland",
    "type": "retail",
    "price_nature": "msrp",
    "access": "sitemap produit + API OCC v2 (SAP Commerce), une requete par fiche",
    "robots": "OK — /search et '*q=' interdits et non utilises ; les fiches /p/ sont libres",
    "corpus_horloger": True,
    "reserve": "une fiche du sitemap peut etre epuisee ; le prix reste affiche",
}

BASE = "https://www.watches-of-switzerland.co.uk"
SITEMAP = f"{BASE}/sitemap/product-en-gbp.xml"
FICHE = f"{BASE}/occ/v2/WatchesOfSwitzerland_UK/products/{{code}}"

# 'Pre+Owned' dans l'URL est le seul marqueur fiable du pre-detenu.
_PRE_DETENU = re.compile(r"Pre.?Owned", re.I)
_CODE = re.compile(r"/p/(\d+)")
# La reference constructeur est le dernier jeton alphanumerique du slug, avant
# le /p/ : .../Jaeger+LeCoultre-Master-Control-Date-Q1548420/p/17631061
_REFERENCE = re.compile(r"-([A-Z0-9][A-Z0-9./]{3,18})/p/\d+", re.I)
# Les prefixes commerciaux colles devant la marque dans `manufacturer`.
_PREFIXE = re.compile(r"^(pre.?owned|certified pre.?owned|ex.?display)\s+|"
                      r"\s+(certified pre.?owned|pre.?owned)$", re.I)


def _marque(manufacturer, titre, tri):
    """La marque, debarrassee des prefixes commerciaux du detaillant."""
    propre = _PREFIXE.sub("", str(manufacturer or "")).strip()
    if propre:
        return propre
    return tri.verdict(titre or "", "MARKETPLACE", corpus_horloger=True).get("brand")


def _urls(raw, journal, cap):
    """Les fiches a visiter : le neuf d'abord, c'est lui qui porte le tarif."""
    try:
        resp = get(SITEMAP, pause=1.0)
    except Exception as exc:
        journal.append(f"sitemap: {type(exc).__name__}")
        return []
    raw.append({"url": resp.url, "status": resp.status_code, "payload": resp.text[:2000]})
    if resp.status_code != 200:
        journal.append(f"sitemap: HTTP {resp.status_code}")
        return []

    toutes = re.findall(r"<loc>([^<]+)</loc>", resp.text)
    neuves = [u for u in toutes if not _PRE_DETENU.search(u)]
    detenues = [u for u in toutes if _PRE_DETENU.search(u)]
    journal.append(f"sitemap : {len(toutes)} fiches, {len(neuves)} neuves, "
                   f"{len(detenues)} pre-detenues")

    # Le neuf d'abord : c'est la seule source de prix catalogue du dossier.
    # Une fiche par marque et par modele suffit a etablir un tarif, donc on
    # etale la selection sur tout le sitemap plutot que de prendre les
    # premieres, qui sont regroupees par marque.
    choix = neuves[::max(1, len(neuves) // max(cap, 1))][:cap]
    if len(choix) < cap:
        pas = max(1, len(detenues) // max(cap - len(choix), 1))
        choix += detenues[::pas][:cap - len(choix)]
    journal.append(f"{len(choix)} fiches retenues sur {len(toutes)} — "
                   f"selection etalee, la collecte complete demanderait ~9 h")
    return choix


def fiche_produit(donnee: dict, url: str, tri=None) -> dict | None:
    """Une fiche OCC -> un enregistrement normalise, ou None si sans prix.

    Isolee de la collecte pour que moteur/rejoue.py refasse la normalisation
    sur le brut deja stocke : 2 500 fiches coutent trois heures de requetes.
    """
    tri = tri or filtre()
    prix = donnee.get("price") or {}
    montant, _ = parse_money(prix.get("formattedValue") or prix.get("value"))
    if not montant:
        return None

    pre_detenu = bool(_PRE_DETENU.search(url))
    stock = (donnee.get("stock") or {}).get("stockLevelStatus")
    reference = _REFERENCE.search(url)
    # PIEGE MESURE LE 28/08/2026 : `categories[0]` est souvent 'Brands', une
    # rubrique de NAVIGATION. Prendre la premiere faisait rejeter 1 110 montres
    # par R0. La liste complete dit la verite : ['Brands', 'Cartier',
    # 'Mens Watches'].
    categories = [c.get("name") for c in (donnee.get("categories") or [])
                  if c.get("name")]
    titre = donnee.get("name")
    marque = _marque(donnee.get("manufacturer"), titre, tri)

    return price_point(
        source_id=SOURCE["id"], source_type=SOURCE["type"],
        source_url=url, external_id=str(donnee.get("code")),
        # Une montre NEUVE chez un detaillant agree est vendue au tarif
        # officiel : c'est du prix catalogue. Une montre pre-detenue chez le
        # meme detaillant est un prix demande d'occasion.
        price_nature="asking" if pre_detenu else "msrp",
        price_nature_provenance="deduite_statut",
        listing_status="active" if stock != "outOfStock" else "inactive",
        price_amount=montant,
        price_currency=prix.get("currencyIso") or "GBP",
        # Le detaillant ne date pas ses fiches : le prix vaut au jour du releve.
        price_date=None,
        brand=marque, model=titre,
        reference=reference.group(1) if reference else None,
        reference_provenance="extrait_titre" if reference else None,
        source_category=" · ".join(categories) or None,
        title=f"{marque or ''} {titre or ''}".strip(),
        condition="preowned" if pre_detenu else "new",
        seller="Watches of Switzerland",
    )


def lots_du_brut(entrees: list) -> list[tuple]:
    """(fiche, url) pour chaque produit d'une collecte deja stockee."""
    trouves = []
    for entree in entrees:
        url = entree.get("url", "")
        if "/occ/v2/" not in url:
            continue
        try:
            donnee = json.loads(entree.get("payload", ""))
        except (json.JSONDecodeError, AttributeError):
            continue
        # La reponse OCC porte son propre chemin public, celui qui contient la
        # reference et le marqueur 'Pre+Owned'. Le brut est donc rejouable sans
        # avoir a reconserver le sitemap.
        chemin = donnee.get("url")
        if not chemin:
            continue
        trouves.append((donnee, f"{BASE}{chemin}"))
    return trouves


def collect(cap: int = 2500):
    raw: list[dict] = []
    journal: list[str] = []
    records: list[dict] = []
    tri = filtre()

    for url in _urls(raw, journal, cap):
        code = _CODE.search(url)
        if not code:
            continue
        try:
            resp = get(FICHE.format(code=code.group(1)),
                       params={"fields": "FULL"}, pause=1.0)
        except Exception as exc:
            journal.append(f"fiche {code.group(1)}: {type(exc).__name__}")
            continue
        raw.append({"url": resp.url, "status": resp.status_code, "payload": resp.text})
        if resp.status_code != 200:
            continue
        try:
            fiche = json.loads(resp.text)
        except json.JSONDecodeError:
            continue

        enregistrement = fiche_produit(fiche, url, tri)
        if enregistrement is not None:
            records.append(enregistrement)

    if len(records) >= cap:
        journal.append(f"TRONQUE: plafond de {cap} atteint — il reste des donnees a prendre")
    return raw, records, journal
