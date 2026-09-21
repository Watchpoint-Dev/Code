"""Le moteur WooCommerce — une boutique = quinze lignes de configuration.

Le pendant de `_shopify.py` pour l'autre grande plateforme du marche. L'API
Store est publique et non authentifiee :

    /wp-json/wc/store/v1/products?per_page=100&page=N
    /wp-json/wc/store/v1/products?per_page=100&page=N&stock_status=outofstock

Le second appel est indispensable : par defaut l'API ne rend que le stock
courant. Chez Watchtrader, cela ferait 601 montres au lieu de 4 092.

QUATRE PIEGES, tous mesures le 28/08/2026 sur six boutiques :

  `currency_minor_unit` VARIE D'UNE BOUTIQUE A L'AUTRE. Amsterdam Vintage et
  Amsterdam Watch Company le mettent a 0 — les prix sont en euros entiers.
  Watchtrader et Wanna Buy A Watch le mettent a 2 — les prix sont en centimes.
  Diviser par 100 en dur donne un facteur 100 d'erreur une fois sur deux.

  LES PRIX NEGATIFS SONT UNE CONVENTION DE VENTE. Amsterdam Watch Company
  inscrit `price: "-14750"` sur 231 montres parties : la valeur absolue est le
  dernier prix demande. Les jeter perdrait 231 observations.

  LES PRIX SENTINELLES. Un montant de 0 ou de 1 n'est pas un prix : c'est un
  « prix sur demande ». On les ecarte en les comptant.

  LA REFERENCE VIT DANS UN ATTRIBUT DE TAXONOMIE, dont le libelle change :
  'Reference' chez Amsterdam Watch Company, 'Model/Case Ref#' chez Wanna Buy A
  Watch, 'Model' chez Global Watch Shop, 'Mpn' chez Chronofinder. D'ou la liste
  de libelles a essayer, par ordre de preference.
"""
from __future__ import annotations

import json
import re

from filtre import filtre
from schema import price_point, reference_dans, reference_libre
from utils import get

PAR_PAGE = 100
_BALISES = re.compile(r"<[^>]+>")

# Les libelles sous lesquels les boutiques rangent la reference constructeur.
LIBELLES_REFERENCE = ("reference", "model/case ref#", "mpn", "ref",
                      "reference number", "case ref")

# `model` est AMBIGU et ne peut pas vivre dans la liste ci-dessus. Chez Global
# Watch Shop il porte bien la reference — '126710BLNR', '278274'. Chez Watches
# of Knightsbridge il porte 'Datejust 36 OysterQuartz', 'Scafograf 300M',
# 'British Military RAF Mark 11'. Le garde-fou d'origine ne rejetait que les
# valeurs SANS chiffre : « Datejust 36 » en contient un, et 12 noms de modele
# entraient donc en base comme references constructeur en `champ_dedie` — la
# provenance la plus fiable du schema, celle qui alimente le socle.
# On ne l'accepte donc que s'il a la FORME d'une reference.
LIBELLES_REFERENCE_AMBIGUS = ("model",)
LIBELLES_MODELE = ("model name", "modele", "model")


def _a_la_forme_d_une_reference(valeur) -> bool:
    """Un code, pas un nom. Deux chiffres au moins, aucun mot en clair.

    '126710BLNR' et '01 774 7686 4051' (Oris) passent ; 'Datejust 36
    OysterQuartz' et 'Scafograf 300M' sont refuses sur leur mot minuscule.
    """
    if not valeur:
        return False
    valeur = str(valeur).strip()
    if len(valeur) > 30 or len(re.findall(r"\d", valeur)) < 2:
        return False
    return not re.search(r"[a-z]{4,}", valeur)
LIBELLES_MARQUE = ("brand", "maker/brand", "marque", "make")
LIBELLES_ANNEE = ("watch year", "year", "circa", "year of production (circa)",
                  "year of production")


def _attribut(produit: dict, libelles) -> str | None:
    """La valeur d'un attribut de taxonomie, par ordre de preference des noms."""
    disponibles = {}
    for a in produit.get("attributes") or []:
        nom = str(a.get("name", "")).strip().lower()
        termes = [t.get("name") for t in (a.get("terms") or []) if t.get("name")]
        if termes:
            disponibles[nom] = " ".join(termes).strip()
    for libelle in libelles:
        if libelle in disponibles:
            return disponibles[libelle]
    return None


# L'annee exacte, entre parentheses en fin de titre : 'REF 216570 (2020)'.
_ANNEE_AU_TITRE = re.compile(r"\((18\d{2}|19\d{2}|20[0-2]\d)\)")
# Une DECENNIE, pas une annee : "2010's", "1990s".
_DECENNIE = re.compile(r"\b(1[89]\d0|20[0-2]0)\s*(?:'s|s)\b", re.I)


def _annee(valeur, titre=None):
    """L'annee de production. Le TITRE prime quand il donne l'annee exacte.

    Watches of Distinction publie un attribut d'annee qui est en realite une
    DECENNIE — "2010's" — pendant que son titre porte l'annee au millesime :
    'Rolex EXPLORER II REF 216570 (2020)'. Mesure du 02/09/2026 : 401 lignes
    gardees sur 496 divergeaient, dont une montre de 2020 datee de 2010. Dix
    ans d'ecart sur une montre, ce n'est pas un arrondi.
    """
    exacte = _ANNEE_AU_TITRE.search(str(titre or ""))
    if exacte:
        return int(exacte.group(1))
    brut = str(valeur or "")
    # Une decennie ne vaut pas une annee : mieux vaut ne rien dire.
    if _DECENNIE.search(brut):
        return None
    trouve = re.search(r"\b(18\d{2}|19\d{2}|20[0-2]\d)\b", brut)
    return int(trouve.group(1)) if trouve else None


def fiche(produit: dict, source: dict) -> dict | None:
    """Un produit WooCommerce -> un enregistrement normalise, ou None.

    Isolee de la collecte pour que moteur/rejoue.py refasse la normalisation
    sur le brut deja stocke.
    """
    prix = produit.get("prices") or {}
    brut = prix.get("price")
    try:
        montant = float(str(brut).replace(",", "").strip())
    except (TypeError, ValueError):
        return None

    # Un prix negatif marque une vente chez certaines boutiques : la valeur
    # absolue est le dernier prix demande.
    negatif = montant < 0
    montant = abs(montant)
    unite = prix.get("currency_minor_unit")
    if unite:
        montant = montant / (10 ** int(unite))
    # 0 et 1 sont des sentinelles de « prix sur demande », pas des prix.
    if montant <= 1:
        return None

    titre = produit.get("name")
    description = _BALISES.sub(" ", produit.get("description") or "")
    # LE STOCK. L'API Store publie `is_in_stock`, un booleen present sur 100 %
    # des produits des cinq boutiques. On lisait a la place `class_list`, que
    # cette API n'envoie JAMAIS : la condition etait donc toujours vraie et les
    # 13 338 lignes des cinq boutiques sortaient « en vente », alors que le
    # brut deja stocke disait 20 738 fiches epuisees sur 22 943. Mesure et
    # correction du 28/08/2026, rejouees sans une requete de plus.
    if "is_in_stock" in produit:
        disponible = bool(produit["is_in_stock"]) and not negatif
    else:
        classes = " ".join(str(c) for c in (produit.get("class_list") or []))
        disponible = "outofstock" not in classes and not negatif

    reference = _attribut(produit, LIBELLES_REFERENCE)
    if reference and (not re.search(r"\d", reference) or reference.lower() in ("n/a", "na")):
        reference = None
    # Le libelle ambigu, et seulement s'il a la forme d'un code.
    _modele_brut = _attribut(produit, LIBELLES_REFERENCE_AMBIGUS)
    if not reference and _a_la_forme_d_une_reference(_modele_brut):
        reference = _modele_brut
    provenance = "champ_dedie" if reference else None
    if not reference:
        reference = reference_dans(titre)
        provenance = "extrait_titre" if reference else None
    if not reference:
        reference = reference_dans(description[:1500])
        provenance = "extrait_description" if reference else None
    if not reference:
        reference = reference_libre(titre)
        provenance = "jeton_titre" if reference else None

    # La marque vit tantot dans un attribut de taxonomie, tantot dans le champ
    # natif `brands` de WooCommerce — Chronofinder n'a que le second, et sans lui
    # le filtre rejetait la source entiere par R3.
    marque = _attribut(produit, LIBELLES_MARQUE)
    if not marque:
        natives = [b.get("name") for b in (produit.get("brands") or []) if b.get("name")]
        marque = natives[0] if natives else None
    if marque and marque.lower() in ("other brands", "autres", source["name"].lower()):
        marque = None
    if not marque:
        # Amsterdam Vintage ne publie NI attribut de marque, NI champ natif :
        # sa marque n'existe qu'en tete de titre ('Cartier Tank 17002'). Sans
        # ce repli, ses 342 fiches sortaient sans marque et R3 les rejetait
        # toutes — alors qu'elles portent 96 % de references et 95 % d'annees.
        # C'est le meme repli que le moteur Shopify fait depuis toujours.
        marque = filtre().verdict(f"{titre} {description[:400]}", "MARKETPLACE",
                                  corpus_horloger=bool(source.get("corpus_horloger"))
                                  ).get("brand")

    return price_point(
        source_id=source["id"], source_type=source["type"],
        source_url=produit.get("permalink"),
        external_id=str(produit.get("id")),
        # Chez un marchand de pieces uniques, une fiche epuisee est une montre
        # PARTIE — mais le montant affiche reste le dernier prix DEMANDE, que
        # la boutique n'a pas remplace par le prix de la transaction. Le statut
        # dit donc la vente, la nature dit ce que le montant est reellement.
        # Les confondre gonflerait le socle de prix qui ne sont pas des ventes.
        price_nature="asking",
        price_nature_provenance="deduite_statut",
        listing_status="active" if disponible else "sold",
        price_amount=montant,
        price_currency=prix.get("currency_code") or "USD",
        # Aucune de ces boutiques ne date ses ventes : la date vient de
        # /wp-json/wp/v2/product et vaut mise en ligne.
        price_date=produit.get("date_created"),
        source_category=" · ".join(
            c.get("name") for c in (produit.get("categories") or []) if c.get("name")) or None,
        brand=marque,
        # Un `model` refuse comme reference n'est pas perdu : c'est un nom de
        # modele, et c'est ici qu'il appartient. S'il a DEJA servi de reference,
        # on ne le recopie pas.
        model=_attribut(produit, LIBELLES_MODELE if reference != _modele_brut
                        else ("model name", "modele")),
        reference=reference, reference_provenance=provenance,
        year=_annee(_attribut(produit, LIBELLES_ANNEE), titre),
        case_material=_attribut(produit, ("case material", "material")),
        condition=_attribut(produit, ("condition",)),
        title=titre,
        seller=source["name"],
    )


def lots_du_brut(entrees: list) -> list[dict]:
    trouves = []
    for entree in entrees:
        try:
            produits = json.loads(entree.get("payload", ""))
        except (json.JSONDecodeError, AttributeError):
            continue
        if isinstance(produits, list):
            trouves.extend(p for p in produits if isinstance(p, dict))
    return trouves


def collecte(source: dict, cap: int, *, base: str, pause: float = 1.0,
             chemin: str = "/wp-json/wc/store/v1/products"):
    """Parcourt le stock courant PUIS les fiches epuisees."""
    raw: list[dict] = []
    journal: list[str] = []
    records: list[dict] = []
    vus: set[str] = set()
    sans_prix = 0

    for statut, libelle in ((None, "en vitrine"), ("outofstock", "parties")):
        page = 1
        avant = len(records)
        while len(records) < cap:
            params = {"per_page": PAR_PAGE, "page": page}
            if statut:
                params["stock_status"] = statut
            try:
                resp = get(f"{base}{chemin}", params=params, pause=pause)
            except Exception as exc:
                journal.append(f"{libelle} p{page}: {type(exc).__name__}")
                break
            raw.append({"url": resp.url, "status": resp.status_code, "payload": resp.text})
            if resp.status_code != 200:
                journal.append(f"{libelle} p{page}: HTTP {resp.status_code}")
                break
            try:
                produits = json.loads(resp.text)
            except json.JSONDecodeError:
                break
            if not isinstance(produits, list) or not produits:
                break
            if page == 1 and resp.headers.get("X-WP-Total"):
                journal.append(f"{libelle} : {resp.headers['X-WP-Total']} annonces")

            for produit in produits:
                enregistrement = fiche(produit, source)
                if enregistrement is None:
                    sans_prix += 1
                    continue
                if enregistrement["external_id"] in vus:
                    continue
                vus.add(enregistrement["external_id"])
                records.append(enregistrement)

            if len(produits) < PAR_PAGE:
                break
            page += 1
        journal.append(f"{libelle} : {len(records) - avant} fiches retenues")

    if sans_prix:
        journal.append(f"{sans_prix} fiches ecartees : prix absent, nul ou sentinelle")
    if len(records) >= cap:
        journal.append(f"TRONQUE: plafond de {cap} atteint — il reste des donnees a prendre")
    return raw, records, journal
