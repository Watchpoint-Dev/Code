"""Le moteur Shopify — une boutique = dix lignes de configuration.

Shopify sert un endpoint public `/products.json` sans authentification, sans
JavaScript et sans cookie. C'est le mecanisme le plus repetable du dossier : une
fois ce fichier ecrit, brancher un marchand de plus ne demande plus qu'un module
de dix lignes qui declare son domaine et sa devise.

Trois pieges, tous payes une fois et traites ici pour toutes les boutiques :

  LA DEVISE. Nos en-tetes portent un Accept-Language, qui declenche la
  localisation Shopify. Sans parametre `currency` explicite, la boutique renvoie
  des prix CONVERTIS qu'on etiquetterait ensuite dans sa devise nominale. L'ecart
  mesure sur Craft & Tailored etait de -17,8 % sur la moitie de la base.

  LE PLAFOND. `page * limit` ne peut pas depasser 25 000 : au-dela, HTTP 400.
  Un catalogue de 28 000 fiches est donc tronque par la plateforme, pas par nous.
  On le dit dans le journal au lieu de rendre un total qui n'en est pas un.

  LE SKU. Ce n'est presque jamais la reference constructeur, c'est un numero
  d'inventaire interne. Il est conserve, mais avec sa provenance : `sku`, pas
  `champ_dedie`. La reference lue dans le titre vaut mieux, quand elle existe.

La nature du prix se deduit de `available` : chez un marchand de pieces uniques,
un produit epuise est une montre partie. C'est du prix VENDU — la nature la plus
rare du dossier, et elle etait jetee.
"""
from __future__ import annotations

import json
import re

from watchpoint.filtrage.filtre import filtre
from watchpoint.schema import parse_money, price_point, reference_dans, reference_libre
from watchpoint.commun.utils import get

PAR_PAGE = 250          # maximum accepte par Shopify
PRIX_PLANCHER = 10      # en dessous, c'est une sentinelle « nous consulter »

# Ce que des boutiques inscrivent dans `vendor` faute de marque. Fidele, mais
# ne nomme personne : mieux vaut relire le titre.
_VENDEURS_MUETS = {"other", "others", "unknown", "n/a", "na", "misc",
                   "various", "divers", "sonstige", "unbranded", "no brand"}
PLAFOND_SHOPIFY = 25000  # page * limit ; au-dela la plateforme repond 400

_REFERENCE = re.compile(
    r"\b(?:ref(?:erence)?|model(?:\s*n[o°]\.?)?)\.?\s*[:#]?\s*([A-Z0-9][A-Z0-9./-]{2,15})", re.I)
_ANNEE = re.compile(r"^\s*(19\d{2}|20[0-2]\d)\b")
_BALISES = re.compile(r"<[^>]+>")

# Les mots par lesquels une boutique nomme sa categorie horlogere. Berry's melange
# 'Mens Watches' et 'Necklaces' dans le meme flux : c'est le vendeur lui-meme qui
# nous dit lesquels sont des montres, et il le sait mieux que nous.
_CATEGORIE_MONTRE = re.compile(r"watch|montre|uhr|orolog", re.I)

# Ce qu'un marchand ajoute DEVANT la reference du constructeur pour dire l'etat
# de la piece. Berry's prefixe 'P-O ' ses fiches d'occasion : 'P-O IW503607'
# n'est pas une reference IWC, 'IW503607' en est une.
_PREFIXE_ETAT = re.compile(r"^(p-?o|pre-?owned|used|second-?hand|new|nos)[\s._-]+", re.I)


def _sans_prefixe(sku: str) -> str | None:
    """'P-O IW503607' -> 'IW503607'"""
    nettoye = _PREFIXE_ETAT.sub("", str(sku)).strip()
    return nettoye if nettoye and re.search(r"\d", nettoye) else None


def sans_balises(html) -> str:
    return _BALISES.sub(" ", str(html or ""))


def reference_du_texte(texte):
    """La reference dans le corps de l'annonce, quand le titre n'en porte pas.

    Mesure du 25/08/2026 sur le brut : body_html porte une reference explicite
    dans 92 % des fiches Montredo, 70 % chez Hairspring, 59 % chez Analog:Shift.
    On ne la lisait pas. Elle est moins sure que dans un titre — le corps cite
    aussi des calibres et des numeros de boitier — d'ou sa provenance distincte.
    """
    return reference_dans(str(texte)[:2000] if texte else None)


def reference_du_titre(titre):
    """'1969 Rolex Daytona (Ref. 6239) Black Dial' -> '6239'"""
    return reference_dans(titre)


def annee_du_titre(titre):
    """L'annee de production ouvre souvent le titre chez les marchands vintage."""
    trouve = _ANNEE.match(str(titre or ""))
    return int(trouve.group(1)) if trouve else None


def fiche(produit: dict, source: dict, *, devise: str, domaine: str,
          cle: str = "id", date: str = "publication",
          indisponible: str = "sold", nature_neuf: str = "asking",
          tags_nature: dict | None = None, moment: str | None = None,
          sku_est_reference: bool = False, etat: str | None = None):
    """Un produit Shopify -> un enregistrement normalise, ou None si sans prix.

    Isolee de la collecte pour une raison precise : le brut etant conserve, on
    doit pouvoir rejouer toute la normalisation sur l'historique sans redemander
    une seule page. C'est ce que fait collecte/rejoue.py.

    `indisponible`  ce que signifie `available=false`. Chez un marchand de
                    pieces uniques, une fiche epuisee est une montre VENDUE.
                    Chez un detaillant de neuf — Topper, Watches of Switzerland —
                    c'est une RUPTURE DE STOCK : la meme reference reviendra.
                    Confondre les deux fabrique de fausses transactions.
    `nature_neuf`   la nature d'un article disponible : `asking` chez un
                    marchand d'occasion, `msrp` chez un detaillant agree qui
                    vend au tarif officiel.
    `tags_nature`   {tag: (nature, statut)}. Un tag de la boutique prime sur la
                    deduction par `available`, parce qu'il est declare et non
                    infere. Montredo marque `inquiry-only` des montres neuves
                    indisponibles a la commande directe : sans ce garde-fou on
                    les comptait comme 3 319 VENTES.
    `sku_est_reference`
                    chez un detaillant AGREE, le champ SKU porte la reference
                    du constructeur et non un code maison : Berry's y inscrit
                    'L38204930' (Longines) et 'IW503607' (IWC). C'est alors un
                    champ publie, plus sur que tout ce qu'on devine d'un titre,
                    et il passe en premier. A ne pas activer a l'aveugle : chez
                    CW Sellors le meme champ vaut 'DOX-333', chez Topper '136'.
    `moment`        la date du releve, quand la source ne date rien elle-meme.
                    Passee explicitement pour que rejouer le brut redonne la
                    meme ligne : `today()` ferait glisser la date a chaque
                    relecture.
    """
    import datetime as _dt

    variante = (produit.get("variants") or [{}])[0]
    montant, _ = parse_money(variante.get("price"))
    # "0.00" = prix masque par la boutique. "1.00" en est la variante polie :
    # un montant sentinelle qui veut dire « nous consulter ». Mesure du
    # 28/08/2026 : 305 fiches gardees chez Bulang & Sons — dont une Daytona
    # 6263 — et 27 chez The Keystone portaient un prix inferieur au plancher.
    # Aucune montre de ce marche ne se vend a dix unites de devise.
    if not montant or montant <= PRIX_PLANCHER:
        return None

    titre = produit.get("title")
    corps_texte = sans_balises(produit.get("body_html"))
    disponible = bool(variante.get("available"))
    sku = (variante.get("sku") or "").strip() or None
    categorie = (produit.get("product_type") or "").strip() or None

    # La nature du prix. Par defaut elle se DEDUIT de `available`, ce qui est
    # une inference. Quand la boutique etiquette elle-meme ses fiches, son tag
    # est une DECLARATION et prime : c'est le vendeur qui parle, pas nous.
    nature = nature_neuf if disponible else (
        "sold" if indisponible == "sold" else nature_neuf)
    statut = "active" if disponible else indisponible
    par_tag = None
    if tags_nature:
        etiquettes = produit.get("tags") or []
        if isinstance(etiquettes, str):
            etiquettes = [t.strip() for t in etiquettes.split(",")]
        etiquettes = {str(t).strip().lower() for t in etiquettes}
        for tag, (dit_nature, dit_statut) in tags_nature.items():
            if tag in etiquettes:
                nature, statut, par_tag = dit_nature, dit_statut, tag
                break

    # La reference, par ordre de confiance decroissante. Le TITRE est epuise
    # AVANT d'ouvrir le corps de l'annonce — d'abord avec mot-cle, puis a la
    # seule forme du jeton — parce qu'un titre ne parle que de la montre alors
    # que le corps cite aussi ce qui l'accompagne.
    #
    # Mesure du 28/08/2026 chez Bulang & Sons, ou la description enumere les
    # bracelets livres avec la montre : 443 fiches gardees portaient une
    # reference qui CONTREDISAIT le numero ecrit dans leur propre titre —
    # 'Rolex Datejust 1601 Grey Sigma Dial' stockee sous 6251H, code du
    # bracelet Oyster. Lire le titre en entier d'abord les corrige toutes.
    if sku_est_reference and sku:
        reference, provenance = _sans_prefixe(sku), "champ_dedie"
    else:
        reference, provenance = None, None
    if not reference:
        reference = reference_du_titre(titre)
        provenance = "extrait_titre" if reference else None
    if not reference:
        # Beaucoup de marchands ecrivent la reference sans mot-cle :
        # 'Rolex Datejust 279173'. On la reconnait a sa forme.
        reference = reference_libre(titre)
        provenance = "jeton_titre" if reference else None
    if not reference:
        reference = reference_du_texte(corps_texte)
        provenance = "extrait_description" if reference else None
    if not reference and sku:
        reference, provenance = sku, "sku"

    # La marque : le champ vendor, sauf quand la boutique s'y met elle-meme —
    # Hairspring inscrit 'Hairspring' sur 100 % de ses fiches. Dans ce cas on
    # cherche la marque dans le texte avec le dictionnaire du filtre.
    marque = (produit.get("vendor") or "").strip() or None
    if marque and marque.lower() in _VENDEURS_MUETS:
        # Craft & Tailored inscrit litteralement 'Other' sur ses fiches Eterna
        # et Movado : le champ est fidele mais ne nomme aucune marque.
        marque = None
    if not marque or marque.lower() in (source["name"].lower(), source["id"].lower()):
        marque = filtre().verdict(f"{titre} {corps_texte[:400]}", "MARKETPLACE",
                                  corpus_horloger=True).get("brand")

    return price_point(
        source_id=source["id"], source_type=source["type"],
        source_url=f"https://{domaine}/products/{produit.get('handle')}",
        external_id=str(produit.get(cle) or produit.get("id")),
        price_nature=nature,
        price_nature_provenance="declaree_tag" if par_tag else "deduite_statut",
        listing_status=statut,
        price_amount=montant, price_currency=devise,
        # PIEGE : c'est la date de mise en ligne de la FICHE, pas celle de la
        # vente. Une montre publiee en 2016 et vendue en 2019 porte 2016.
        price_date=(produit.get("published_at") or produit.get("created_at")
                    if date == "publication"
                    else (moment or _dt.date.today().isoformat())),
        brand=marque, title=titre,
        reference=reference, reference_provenance=provenance,
        source_category=categorie,
        year=annee_du_titre(titre),
        # L'etat est DECLARE par la boutique, il ne se devine pas ici. Ce champ
        # valait "preowned" en dur : mesure du 21/09/2026, 11 des 12 boutiques
        # Shopify portaient donc "preowned" sur 100 % de leurs lignes — dont
        # Topper, detaillant de NEUF, sur ses 3 631 prix catalogue. Un champ
        # rempli a 19 % dans la base et faux sur l'essentiel de son contenu.
        # None dit « la boutique ne l'a pas dit », ce qui est la verite.
        condition=etat,
        seller=source["name"],
    )


def est_une_montre(categorie) -> bool:
    """La boutique classe-t-elle elle-meme cet objet comme une montre ?"""
    return bool(categorie and _CATEGORIE_MONTRE.search(str(categorie)))


def collecte(source: dict, cap: int, *, devise: str, domaine: str,
             pays: str | None = None, pause: float = 2.0,
             chemin: str | tuple = "/products.json", cle: str = "id",
             date: str = "publication", indisponible: str = "sold",
             nature_neuf: str = "asking", tags_nature: dict | None = None,
             sku_est_reference: bool = False, etat: str | None = None):
    """Parcourt /products.json et rend (raw, records, journal).

    `chemin`  une collection dediee aux montres evite d'avaler tout le rayon
              bijouterie. Plusieurs chemins sont acceptes : CW Sellors range ses
              montres en 'mens-watches', 'ladies-watches' et 'luxury-watches',
              et sa collection 'watches' n'en contient que 191 sur ~3 000. Les
              doublons entre collections sont ecartes sur l'identifiant.
    `cle`     'id' ou 'handle'. Une boutique qui reconstruit son catalogue
              chaque nuit change ses identifiants numeriques : le handle est
              alors la seule cle stable.
    `date`    'publication' ou 'releve'. Quand la date publiee est celle du
              dernier rebuild du catalogue, elle ne date rien.
    """
    import datetime as _dt
    moment = _dt.date.today().isoformat()
    chemins = (chemin,) if isinstance(chemin, str) else tuple(chemin)
    raw: list[dict] = []
    journal: list[str] = []
    records: list[dict] = []
    sans_prix = 0
    vus: set[str] = set()

    for un_chemin in chemins:
        base = f"https://{domaine}{un_chemin}"
        avant = len(records)
        page = 1

        while len(records) < cap:
            if page * PAR_PAGE > PLAFOND_SHOPIFY:
                journal.append(
                    f"PLAFOND SHOPIFY: page*limit > {PLAFOND_SHOPIFY} — la plateforme "
                    f"refuse d'aller plus loin, le catalogue restant est inaccessible")
                break

            params = {"limit": PAR_PAGE, "page": page, "currency": devise}
            if pays:
                params["country"] = pays
            try:
                resp = get(base, params=params, pause=pause)
            except Exception as exc:
                journal.append(f"{un_chemin} p{page}: {type(exc).__name__}")
                break
            raw.append({"url": resp.url, "status": resp.status_code, "payload": resp.text})
            if resp.status_code != 200:
                journal.append(f"{un_chemin} p{page}: HTTP {resp.status_code}")
                break
            try:
                produits = json.loads(resp.text).get("products", [])
            except json.JSONDecodeError:
                journal.append(f"{un_chemin} p{page}: JSON illisible")
                break
            if not produits:
                break

            for produit in produits:
                enregistrement = fiche(produit, source, devise=devise, domaine=domaine,
                                       cle=cle, date=date, indisponible=indisponible,
                                       nature_neuf=nature_neuf, tags_nature=tags_nature,
                                       sku_est_reference=sku_est_reference,
                                       etat=etat, moment=moment)
                if enregistrement is None:
                    sans_prix += 1
                    continue
                # Les collections se recoupent : une meme montre est rangee
                # dans 'mens-watches' et dans 'luxury-watches'.
                if enregistrement["external_id"] in vus:
                    continue
                vus.add(enregistrement["external_id"])
                records.append(enregistrement)

            if len(produits) < PAR_PAGE:
                break
            page += 1

        if len(chemins) > 1:
            journal.append(f"{un_chemin} : {len(records) - avant} fiches nouvelles")

    if sans_prix:
        journal.append(f"{sans_prix} fiches ecartees : prix masque par la boutique")
    if len(records) >= cap:
        journal.append(f"TRONQUE: plafond de {cap} atteint — il reste des donnees a prendre")
    return raw, records[:cap], journal
