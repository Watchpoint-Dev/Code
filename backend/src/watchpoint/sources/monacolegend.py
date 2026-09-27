"""Monaco Legend — maison de ventes horlogere. Prix REALISES, et INVENDUS publies.

Vingt requetes pour sept ans d'encheres exclusivement horlogeres : c'est le
meilleur rapport volume/cout du dossier. La maison ne vend que des montres,
donc rien du bruit de joaillerie qui fait tomber Lyon & Turnbull a 18 %.

Acces en deux niveaux, sans pagination :

  1. /auction porte un unique JSON-LD. Son `EventSeries` liste les 19 ventes
     passees avec leur `startDate` — c'est la date de vente, la seule vraie.
  2. /auction/{slug} rend TOUS les lots de la vente en une page, jusqu'a 288.

QUATRE POINTS MESURES, dans l'ordre ou ils feraient mal :

  LE PRIX EST FRAIS ACHETEUR INCLUS. Le libelle dit 'Result (Premium)' et le
  qualificatif est present sur toutes les ventes. C'est donc la convention de
  Christie's, pas celle d'Artcurial : `price_includes_premium=True`. Comparer
  sans le savoir surevalue la maison d'environ un quart.

  NE JAMAIS LIRE LE PRIX AFFICHE. Le site ecrit '€ 25.000' et "Fr. 32'500" : le
  point est un separateur de MILLIERS, et l'apostrophe suisse s'y ajoute.
  L'attribut `data-price` porte deja l'entier propre. On lit l'attribut.

  DEUX DEVISES. La maison vend a Monaco en EUR et a Geneve en CHF. Coder l'une
  en dur trompe sur des ventes entieres — la 41 est integralement en francs.
  La devise se lit sur le symbole du montant affiche, lui seul.

  L'INVENDU N'EST PAS UN PRIX A ZERO. Un lot passe porte `data-price` VIDE et
  affiche 'Passed'. Il entre quand meme, en nature `estimate` avec son statut :
  savoir ou le marche a refuse de suivre vaut autant que savoir ou il a suivi.
  Seuls les lots retires — classe `lot-withdrawn` — sont ecartes, parce qu'ils
  n'ont jamais ete soumis aux encheres.

Reconnaissance du 09/08/2026, structure reverifiee le 28/08/2026 : le JSON-LD
est passe d'un `EventSeries` nu a un `@graph`, et le code lit les deux.
"""
from __future__ import annotations

import json
import re

from watchpoint.schema import parse_money, price_point, reference_dans, reference_libre
from watchpoint.commun.utils import get

SOURCE = {
    "id": "monacolegend",
    "name": "Monaco Legend Auctions",
    "type": "auction",
    "price_nature": "realised",
    "access": "JSON-LD EventSeries + attributs data- des pages de vente",
    "robots": "OK — /auction autorise ; /livewire interdit et non utilise",
    # Maison exclusivement horlogere : R4 n'a pas a exiger le mot "montre" dans
    # le titre pour valider une marque ambigue.
    "corpus_horloger": True,
    "reserve": "prix frais acheteur INCLUS, comme Christie's — pas un marteau nu",
}

BASE = "https://www.monacolegendauctions.com"
INDEX = f"{BASE}/auction"

_LDJSON = re.compile(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', re.S)
_LOT = re.compile(r'<section class="lot([^"]*)"([^>]*)>(.*?)</section>', re.S)
_ATTR = re.compile(r'data-(\w+)="([^"]*)"')
_CHAMP = {
    "brand": re.compile(r"lot-brand'>(.*?)</span>", re.S),
    "titre": re.compile(r"lot-title'>(.*?)</span>", re.S),
    "numero": re.compile(r"lot-number'>(.*?)</span>", re.S),
}
_ESTIMATION = re.compile(r"lot-estimation'>(.*?)</p>", re.S)
_MONTANT = re.compile(r'lot-status-value[^>]*>(.*?)</span>', re.S)
_LIEN = re.compile(r"href=['\"]([^'\"]*?/lot-\d+)['\"]")
_BALISES = re.compile(r"<[^>]+>")
_DEVISES = {"€": "EUR", "Fr.": "CHF", "$": "USD", "£": "GBP"}


def _texte(html) -> str:
    """Le contenu d'une balise, entites decodees et sur une seule ligne."""
    import html as _h
    return re.sub(r"\s+", " ", _h.unescape(_BALISES.sub(" ", str(html or "")))).strip()


def _devise(affiche: str) -> str | None:
    """"Fr. 32'500" -> CHF. Le symbole est la seule source sure : deux ventes
    sur dix-neuf sont libellees en francs suisses."""
    for symbole, code in _DEVISES.items():
        if symbole in affiche:
            return code
    return None


def _ventes(payload: str) -> list[dict]:
    """Les ventes passees et leur date, depuis le JSON-LD de l'index.

    Le site a change de forme entre la reconnaissance et la mise en service :
    l'`EventSeries` etait a la racine, il vit maintenant dans un `@graph`. Les
    deux sont acceptes — une structure de page n'est jamais un contrat.
    """
    for trouve in _LDJSON.finditer(payload or ""):
        try:
            donnee = json.loads(trouve.group(1))
        except json.JSONDecodeError:
            continue
        noeuds = donnee.get("@graph") if isinstance(donnee, dict) else None
        for noeud in (noeuds or [donnee]):
            if not isinstance(noeud, dict) or not noeud.get("subEvent"):
                continue
            return [v for v in noeud["subEvent"]
                    if isinstance(v, dict) and v.get("url")
                    and "Past" in str(v.get("eventStatus", ""))]
    return []


def fiche(lot: tuple, date_vente=None, devise_vente=None) -> dict | None:
    """(classes, attributs, corps) d'un lot -> un enregistrement, ou None."""
    classes, attributs, corps = lot
    # Un lot retire n'a jamais ete soumis aux encheres : il ne dit rien du
    # marche, contrairement a un invendu.
    if "lot-withdrawn" in classes:
        return None

    donnees = dict(_ATTR.findall(attributs))
    titre = _texte(_CHAMP["titre"].search(corps).group(1)) \
        if _CHAMP["titre"].search(corps) else None
    marque = _texte(_CHAMP["brand"].search(corps).group(1)) \
        if _CHAMP["brand"].search(corps) else None
    affiche = _texte(_MONTANT.search(corps).group(1)) if _MONTANT.search(corps) else ""

    # Le montant vient de l'attribut, jamais du texte : '€ 25.000' se lit 25,0
    # si on le parse comme un nombre. La devise, elle, ne vit que dans le texte.
    brut = (donnees.get("price") or "").strip()
    vendu = bool(brut and brut not in ("0", "0.00"))
    try:
        montant = float(brut) if vendu else None
    except ValueError:
        montant = None
    devise = _devise(affiche) or devise_vente or "EUR"

    estimation = _ESTIMATION.search(corps)
    bas = haut = None
    if estimation:
        # 'Fr. 25\'000 – 50\'000' : deux nombres, meme devise.
        nombres = re.findall(r"[\d.'  ]{3,}", _texte(estimation.group(1)))
        montants = [parse_money(n)[0] for n in nombres[:2]]
        montants = [m for m in montants if m]
        bas = montants[0] if montants else None
        haut = montants[1] if len(montants) > 1 else None
    if bas is None and donnees.get("est"):
        try:
            bas = float(donnees["est"])
        except ValueError:
            pass

    if montant is None and bas is None:
        return None

    lien = _LIEN.search(corps)
    reference = reference_dans(titre) or reference_libre(titre)

    annee = None
    if donnees.get("year", "").isdigit():
        annee = int(donnees["year"])

    return price_point(
        source_id=SOURCE["id"], source_type=SOURCE["type"],
        source_url=lien.group(1) if lien else None,
        external_id=donnees.get("id"),
        # L'invendu entre en estimation : il dit ou le marche a refuse de
        # suivre. Seules Lyon & Turnbull et Loupe This publient la meme chose.
        price_nature="realised" if vendu else "estimate",
        price_nature_provenance="champ_dedie",
        listing_status="sold" if vendu else "unsold",
        # 'Result (Premium)' sur toutes les ventes : le montant porte deja les
        # frais acheteur. Convention de Christie's, pas d'Artcurial.
        price_includes_premium=True if vendu else None,
        price_amount=montant if vendu else bas,
        price_currency=devise,
        price_date=date_vente,
        estimate_low=bas, estimate_high=haut,
        brand=marque, title=titre,
        reference=reference,
        reference_provenance=("extrait_titre" if reference and reference_dans(titre)
                              else "jeton_titre" if reference else None),
        year=annee,
        condition="preowned",
        seller=SOURCE["name"],
    )


def lots_du_brut(entrees: list) -> list[tuple]:
    """(lot, date de vente, devise) pour chaque lot du brut deja stocke.

    La date de vente n'est PAS sur la page de la vente : elle vient du JSON-LD
    de l'index, conserve dans le meme brut. Sans lui, rejouer la source
    rendrait des prix realises sans date, donc hors socle.
    """
    dates: dict[str, str] = {}
    for entree in entrees:
        for vente in _ventes(entree.get("payload") or ""):
            debut = str(vente.get("startDate") or "")[:10]
            if debut:
                dates[str(vente["url"]).rstrip("/").split("/")[-1]] = debut

    trouves = []
    for entree in entrees:
        url = entree.get("url") or ""
        if "/auction/" not in url:
            continue
        slug = url.rstrip("/").split("/")[-1]
        payload = entree.get("payload") or ""
        # La devise est celle de la vente : on la prend sur son premier lot
        # prixe, pour que les lots invendus de la meme vente en heritent.
        devise = None
        for lot in _LOT.finditer(payload):
            trouve = _MONTANT.search(lot.group(3))
            if trouve:
                devise = _devise(_texte(trouve.group(1)))
            if devise:
                break
        for lot in _LOT.finditer(payload):
            trouves.append((lot.groups(), dates.get(slug), devise))
    return trouves


def collect(cap: int = 8000):
    raw: list[dict] = []
    journal: list[str] = []
    records: list[dict] = []
    invendus = 0

    try:
        index = get(INDEX, pause=1.5)
    except Exception as exc:
        return raw, records, [f"index: {type(exc).__name__}"]
    raw.append({"url": index.url, "status": index.status_code, "payload": index.text})
    ventes = _ventes(index.text)
    if not ventes:
        return raw, records, ["index: aucun EventSeries — la structure a change"]
    journal.append(f"{len(ventes)} ventes passees listees par le JSON-LD")

    for vente in ventes:
        if len(records) >= cap:
            break
        try:
            resp = get(str(vente["url"]), pause=1.5)
        except Exception as exc:
            journal.append(f"{vente.get('name')}: {type(exc).__name__}")
            continue
        raw.append({"url": resp.url, "status": resp.status_code, "payload": resp.text})
        if resp.status_code != 200:
            journal.append(f"{vente.get('name')}: HTTP {resp.status_code}")
            continue

        date_vente = str(vente.get("startDate") or "")[:10] or None
        devise = None
        for lot in _LOT.finditer(resp.text):
            trouve = _MONTANT.search(lot.group(3))
            if trouve:
                devise = _devise(_texte(trouve.group(1)))
            if devise:
                break

        avant = len(records)
        for lot in _LOT.finditer(resp.text):
            if len(records) >= cap:
                break
            enregistrement = fiche(lot.groups(), date_vente, devise)
            if enregistrement is None:
                continue
            if enregistrement["listing_status"] == "unsold":
                invendus += 1
            records.append(enregistrement)
        journal.append(f"{date_vente} {str(vente.get('name'))[:34]} : "
                       f"{len(records) - avant} lots ({devise or '?'})")

    if invendus:
        journal.append(f"{invendus} lots INVENDUS conserves en nature 'estimate' — "
                       f"seules trois sources du dossier les publient")
    if len(records) >= cap:
        journal.append(f"TRONQUE: plafond de {cap} atteint — il reste des donnees a prendre")
    return raw, records, journal
