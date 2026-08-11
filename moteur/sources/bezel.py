"""Bezel — marketplace. Annonces structurees, les plus riches du dossier.

ETAT : adaptateur REECRIT sur l'API interne, mais EN ATTENTE D'ARBITRAGE.

  L'ancienne voie (sitemap + __NEXT_DATA__) est morte : le sitemap est passe
  derriere un reCAPTCHA et l'adaptateur rendait 89 prix, puis 7, puis 0.

  La nouvelle voie fonctionne et donne 32 670 annonces au lieu de 89 — mais
  elle pose une question qui n'est pas technique :

      robots.txt AUTORISE /api/ (verifie : aucun Disallow ne le couvre)
      les CGU INTERDISENT verbatim « data mining, robots, scraping » et
      l'acces a toute information « not intentionally made available ».

  Cette seconde clause vise precisement une API interne non documentee.
  C'est un arbitrage humain, pas une decision de code — d'ou le drapeau
  ARBITRAGE_CGU ci-dessous. Tant qu'il vaut False, l'adaptateur ne sollicite
  pas le site et le dit dans son journal.

Pour activer : passer ARBITRAGE_CGU a True, en connaissance de cause.
"""
from __future__ import annotations

import datetime as dt
import json

from schema import price_point
from utils import get

# --------------------------------------------------------------------------
# Mettre a True UNIQUEMENT apres decision explicite sur les CGU (cf. en-tete).
ARBITRAGE_CGU = False
# --------------------------------------------------------------------------

SOURCE = {
    "id": "bezel",
    "name": "Bezel",
    "type": "marketplace",
    "price_nature": "asking",
    "access": "API interne /api/marketplace/listings + jointure catalogue",
    "robots": "OK — seul '?searchQuery=' est interdit ; /api/ n'est couvert par aucun Disallow",
    "statut": "EN ATTENTE — les CGU interdisent le scraping, arbitrage humain requis",
}

BASE = "https://shop.getbezel.com"
ANNONCES = f"{BASE}/api/marketplace/listings"
MODELES = f"{BASE}/api/catalog/models"
COMPTEUR = f"{BASE}/api/listings/stats/count"
PAGE = 200          # plafond serveur : pageSize=201 -> HTTP 400
LOT_MODELES = 200   # meme plafond sur la jointure catalogue


def _resout_modeles(ids: list[int], cache: dict, raw: list, journal: list) -> None:
    """Complete le cache des modeles. Les specs vivent la, pas dans l'annonce."""
    manquants = [i for i in dict.fromkeys(ids) if i not in cache]
    for depart in range(0, len(manquants), LOT_MODELES):
        tranche = manquants[depart:depart + LOT_MODELES]
        resp = get(MODELES, params={"ids": ",".join(map(str, tranche))}, pause=1.1)
        raw.append({"url": resp.url, "status": resp.status_code, "payload": resp.text})
        if resp.status_code != 200:
            journal.append(f"catalogue: HTTP {resp.status_code} sur {len(tranche)} modeles")
            continue
        try:
            for m in json.loads(resp.text) or []:
                if isinstance(m, dict) and m.get("id") is not None:
                    cache[m["id"]] = m
        except json.JSONDecodeError:
            journal.append("catalogue: JSON illisible")


def collect(cap: int = 2000):
    raw: list[dict] = []
    journal: list[str] = []
    records: list[dict] = []

    if not ARBITRAGE_CGU:
        journal.append("EN ATTENTE — collecte suspendue : les CGU de Bezel interdisent "
                       "le scraping. Voir l'en-tete du module. Aucune requete envoyee.")
        return raw, records, journal

    resp = get(COMPTEUR, pause=1.1)
    raw.append({"url": resp.url, "status": resp.status_code, "payload": resp.text})
    if resp.status_code == 200:
        journal.append(f"compteur du site : {resp.text.strip()[:20]} annonces actives")

    cache_modeles: dict[int, dict] = {}
    depart = 0
    while len(records) < cap:
        # `active=true` est OBLIGATOIRE : sans lui le serveur repond 403.
        resp = get(ANNONCES, params={"active": "true", "pageSize": PAGE, "start": depart},
                   pause=1.1)
        raw.append({"url": resp.url, "status": resp.status_code, "payload": resp.text})
        if resp.status_code != 200:
            journal.append(f"annonces start={depart}: HTTP {resp.status_code}")
            break
        try:
            lot = json.loads(resp.text)
        except json.JSONDecodeError:
            journal.append(f"annonces start={depart}: JSON illisible")
            break
        if not lot:
            break

        _resout_modeles([a.get("modelId") for a in lot if a.get("modelId")],
                        cache_modeles, raw, journal)

        for annonce in lot:
            cents = annonce.get("priceCents")
            if not cents:
                continue
            modele = cache_modeles.get(annonce.get("modelId"), {})
            records.append(price_point(
                source_id=SOURCE["id"], source_type=SOURCE["type"],
                source_url=f"{BASE}/listings/{annonce.get('id')}",
                external_id=str(annonce.get("id")),
                price_nature="asking",
                price_amount=float(cents) / 100,
                # L'API n'expose AUCUN champ de devise. USD est une deduction
                # (marketplace americaine), pas une mesure. A revoir si Bezel
                # ouvre un second marche.
                price_currency="USD",
                # PIEGE : `created` est la date de creation de l'ANNONCE, pas
                # celle du prix. 86 % des annonces ont ete revisees depuis
                # (ecart median 105 jours, maximum 1 637). On date donc le prix
                # du jour du releve. C'est la seule date vraie : « ce prix etait
                # affiche ce jour-la ». L'historique se construit en rejouant.
                price_date=dt.date.today().isoformat(),
                brand=modele.get("brand"),
                model=modele.get("displayName") or modele.get("name"),
                # Reference du MODELE : elle identifie un modele, jamais un
                # exemplaire. Plusieurs annonces partagent la meme.
                reference=modele.get("referenceNumber"),
                title=modele.get("displayName"),
                case_material=modele.get("caseMaterials"),
                case_size_mm=modele.get("caseSize"),
                movement=modele.get("movementType"),
                dial_color=modele.get("dialColor"),
                condition=annonce.get("condition"),
                seller="Bezel",
            ))

        depart += len(lot)
        journal.append(f"start={depart}: {len(records)} prix cumules")
        if len(lot) < PAGE:
            break

    if len(records) >= cap:
        journal.append(f"TRONQUE: plafond de {cap} atteint — il reste des donnees a prendre")
    return raw, records[:cap], journal
