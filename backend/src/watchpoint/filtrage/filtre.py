"""Le filtre — est-ce une montre, oui ou non ?

    cd ~/Desktop/WP
    python -m watchpoint filtre            # le banc de test
    python -m watchpoint filtre --base     # effet sur la base
    python -m watchpoint filtre --marquer  # rejoue le filtre sur l'historique

Implemente l'arbre R1 -> R8 specifie dans filtres/Filtres_scrapping.xlsx,
onglet README. La specification est la reference : si ce fichier et l'Excel
divergent, c'est ce fichier qui a tort.

Trois verdicts, et un seul est definitif :

    GARDER        l'annonce entre, ses attributs sont extraits
    REJETER       elle n'entre pas, mais la regle declenchee est conservee
    QUARANTAINE   ni l'un ni l'autre, a echantillonner chaque semaine

Le filtre ne supprime jamais rien. Il MARQUE. On l'applique entre le brut et
le normalise, et comme le brut n'est jamais jete, toute correction de l'Excel
se rejoue sur l'historique complet sans une seule requete reseau. C'est ce qui
rend le filtre corrigeable a tout moment plutot que fige au premier run.

Ce que le filtre ne fait pas, et qu'il ne faut pas lui demander : verifier la
reference, ni la nature du prix. Il repond a une seule question. La reference
et la nature sont mesurees par rapports/audit_champs.py.
"""
from __future__ import annotations

from watchpoint import config

import json
import pathlib
import re
import sys
import unicodedata

CONFIG = config.CONFIG_FILTRE

# La reference dans un titre de vente : "ref. 16710", "Ref 5711/1A", "réf 973".
REFERENCE = re.compile(r"(?<!\w)r[eé]f\.?(?:\s*(?:no|n°|nr)\.?)?\s*[\w./-]*\d", re.I)

GARDER, REJETER, QUARANTAINE = "GARDER", "REJETER", "QUARANTAINE"

# Comment une source nomme sa categorie horlogere. Volontairement large : c'est
# le vocabulaire des vendeurs, pas le notre.
_CATEGORIE_MONTRE = re.compile(r"watch|timepiece|montre|horlog|uhr|orolog|reloj", re.I)

# Les libelles qui ne disent RIEN. Artcurial classe 8 139 de ses 9 316 lots en
# 'OTHER' : cela signifie non renseigne, pas 'ce n'est pas une montre'. Les
# confondre ferait rejeter la source entiere. Une categorie publiee n'informe
# que lorsqu'elle nomme vraiment quelque chose.
_CATEGORIE_MUETTE = re.compile(
    r"^(other|others|autre|autres|misc|miscellaneous|divers|general|generale|"
    r"uncategori[sz]ed|non classe|sans categorie|default|n/?a|inconnu|unknown|"
    # Les rubriques de NAVIGATION d'une boutique ne classent pas un produit :
    # Watches of Switzerland range 1 110 montres sous 'Brands', et sa liste
    # complete se lit ['Brands', 'Cartier', 'Mens Watches'].
    r"brands?|marques?|shop|boutique|sale|soldes|new in|nouveautes?|all|tous|"
    r"gifts?|cadeaux?|home|accueil|[a-z]*all)$", re.I)

# Les familles que la source nomme elle-meme et qui ne sont PAS horlogeres.
# Seule cette liste autorise un « non » sur la foi de la categorie : partout
# ailleurs, une etiquette sans mot horloger ne dit RIEN et l'on retombe sur le
# titre. Mesure du 21/09/2026 : la regle inverse — « pas de mot horloger donc
# pas une montre » — rejetait 332 montres chez Watches of Switzerland
# (`Brands · Omega · Seamaster`) et 119 chez AWCO (`Sports & Tool · Dress`).
# Le nom du modele suffisait a faire basculer l'etiquette de muette a negative.
_CATEGORIE_NON_HORLOGERE = re.compile(
    r"jewel|jewell?ery|bijou|joaill|schmuck|gioiell|joyer|"
    r"necklace|collier|halskett|colgante|"
    r"earring|boucle d.oreille|ohrring|"
    r"\bring\b|rings|bague|bagues|anneau|"
    r"pendant|pendentif|brooch|broche|cufflink|bouton de manchette|"
    r"coin|monnaie|munze|numismat|medal|medaille|"
    r"furniture|mobilier|mobel|"
    r"silverware|argenterie|\bsilver\b|silber|porcelain|porcelaine|ceramic|"
    r"painting|tableau|gemalde|print|estampe|sculpture|"
    r"\bbooks?\b|livre|toy|jouet|spielzeug|firearm|\bgun\b|\barme\b|"
    # Le rayon SOUVENIRS d'un marchand. Mesure du 21/09/2026 : en rendant
    # `None` au lieu de `False`, la premiere version de ce correctif a fait
    # entrer 166 enseignes de vitrine chez Analog:Shift (« Omega Seamaster
    # Titane Signage ») et 59 objets promotionnels chez Bulang & Sons (plateau
    # de valet, porte-cles, couteau suisse Rolex). Leur titre porte une marque,
    # donc R8 les gardait. Ces etiquettes disent bien « pas une montre ».
    r"collecti[bv]|collectab|collectors? item|memorabilia|signage|ephemera|"
    r"poster|affiche|advertis|\bads?\b|publicite|literature|brochure|"
    r"\bseal\b|seals|trophy|award|keyring|key holder|porte-cles|"
    r"stamp|timbre|wine|\bvins?\b|handbag|\bsac\b|shoe|chaussure|"
    r"bangle|\bbracelets?\b|"
    r"clothing|vetement|sunglass|lunette|\bpen\b|stylo", re.I)

# Le piege inverse, et il est vicieux : un rayon d'ACCESSOIRES nomme avec le mot
# « watch » se faisait lire comme horloger. Mesure du 21/09/2026 chez Everest
# Horology (248 fiches, zero montre) : `Watch Buckle`, `Watch Pouch`,
# `Watch Rolls` et `Watch Boxes` donnaient GARDER par R7a, et une boucle
# deployante a 395 $ portant « Daytona 116500 » entrait en base avec cette
# reference. Le mot horloger ne vaut donc que s'il ne qualifie pas un accessoire.
_CATEGORIE_ACCESSOIRE = re.compile(
    r"buckle|clasp|boucle deployante|"
    r"pouch|pochette|etui|\broll\b|rolls|travel case|storage|"
    r"\bbox\b|boxes|boite|\bcase\b(?! material)|schatulle|"
    r"strap|\bband\b|bands|armband\b|"
    # `tool` nu est proscrit : « Sports & Tool » est un TYPE de montre chez AWCO,
    # pas un rayon d'outillage. Et `armband` exige sa frontiere de mot, sinon il
    # devore « Armbanduhr » — la montre-bracelet allemande.
    r"winder|remontoir|tool ?kits?|outillage|spring bar|barrette|"
    r"crystal|verre|glass|dial only|movement only|mouvement seul|"
    r"\bpart\b|parts|piece detachee|spare|"
    r"stand|presentoir|display|cushion|coussin|"
    r"accessor|accessoire|zubehor", re.I)

_CJK = re.compile(r"[぀-ヿ㐀-䶿一-鿿가-힯]")
_motifs: dict[str, re.Pattern] = {}


def normaliser(texte) -> str:
    """Minuscules, accents latins retires, kana intacts.

    Le piege est la : un NFKD suivi d'un retrait aveugle des diacritiques
    transforme パ en ハ, et plus aucune marque japonaise n'est reconnue. On ne
    retire donc la marque combinante que si le caractere de base est latin.
    """
    sortie, base_latine = [], False
    for c in unicodedata.normalize("NFKD", str(texte or "")):
        if unicodedata.combining(c):
            if not base_latine:
                sortie.append(c)
        else:
            base_latine = ord(c) < 0x0250
            sortie.append(c)
    return unicodedata.normalize("NFC", "".join(sortie)).lower()


def _positions(terme: str, texte: str) -> list[int]:
    """Ou le terme apparait dans le texte deja normalise. Vide s'il est absent.

    Frontiere de mot par defaut. Les langues sans espaces (japonais, chinois,
    coreen) basculent en recherche de sous-chaine, detectees automatiquement.
    """
    if not terme:
        return []
    if _CJK.search(terme):
        depart, trouves = 0, []
        while (i := texte.find(terme, depart)) != -1:
            trouves.append(i)
            depart = i + 1
        return trouves
    cle = normaliser(terme)
    motif = _motifs.get(cle)
    if motif is None:
        motif = _motifs[cle] = re.compile(r"(?<!\w)" + re.escape(cle) + r"(?!\w)")
    return [m.start() for m in motif.finditer(texte)]


def present(terme: str, texte: str) -> bool:
    return bool(_positions(terme, texte))


def _sans_signes(texte: str) -> str:
    """'Jaeger-Le Coultre' et 'JAEGER LECOULTRE' donnent la meme cle."""
    return re.sub(r"[^a-z0-9]", "", str(texte).lower())


class Filtre:
    """L'arbre de decision, charge une fois, applique des millions de fois."""

    def __init__(self, config: pathlib.Path = CONFIG):
        self.conf = json.loads(pathlib.Path(config).read_text(encoding="utf-8"))
        self.version = self.conf["generated_at"]
        reglages = self.conf.get("matching", {})
        self.ref_vaut_token = reglages.get("reference_counts_as_token", True)
        self.fenetre_descriptive = reglages.get("descriptive_window_chars", 30)

        # Toutes langues confondues : une source allemande ecrit ses titres en
        # allemand, mais cite "full set" et "tropical dial" en anglais.
        self.tokens = [t for termes in self.conf["category_tokens"].values()
                       for t in termes]
        self.marqueurs = {
            famille: [t for termes in langues.values() for t in termes]
            for famille, langues in self.conf["markers"].items()
        }
        # case_pocket et alarm_complication sont lus par R3b et R1b, jamais par
        # la logique CONDITIONAL generique : sans cette mise a l'ecart, une
        # montre de poche Patek retomberait en quarantaine par R7a.
        self.reserves = {"case_pocket", "alarm_complication"}
        self.durs = [e for e in self.conf["exclusions"] if e["severity"] == "HARD"]
        self.conditionnels = [e for e in self.conf["exclusions"]
                              if e["severity"] == "CONDITIONAL"
                              and e["concept"] not in self.reserves]
        self.poche = [e for e in self.conf["exclusions"]
                      if e["concept"] == "case_pocket"]
        self.reveil = [e for e in self.conf["exclusions"]
                       if e["concept"] == "alarm_complication"]

    # -- outils internes ---------------------------------------------------
    @staticmethod
    def _scope_ok(scope: str, type_source: str) -> bool:
        return scope == "ALL" or scope == type_source

    def _touches(self, regles, texte, type_source):
        """Les entrees d'exclusion dont un terme apparait dans le texte."""
        for e in regles:
            if not self._scope_ok(e["scope"], type_source):
                continue
            for terme in e["terms"]:
                pos = _positions(terme, texte)
                if pos:
                    yield e, terme, pos

    def _marqueur(self, famille, texte):
        return any(present(t, texte) for t in self.marqueurs.get(famille, ()))

    def _descriptif_devant(self, position, texte) -> bool:
        """Un qualificatif descriptif precede-t-il le terme conditionnel ?

        'white dial' decrit une montre, 'dial' seul peut etre une piece. On
        regarde en arriere sur une fenetre courte : au-dela, le qualificatif
        porte sur autre chose dans le titre.
        """
        debut = max(0, position - self.fenetre_descriptive)
        avant = texte[debut:position]
        return any(present(t, avant) for t in self.marqueurs.get("DESCRIPTIVE", ()))

    # -- l'arbre -----------------------------------------------------------
    def verdict(self, titre, type_source, maker=None, description=None,
                corpus_horloger=False, categorie_source=None) -> dict:
        """Rend le verdict, la regle qui l'a produit, et ce qu'on a appris.

        `type_source` vaut AUCTION ou MARKETPLACE. Champ d'application, tel que
        specifie : la marque et les exclusions dures ne lisent que le titre et
        le fabricant — jamais la description, ou un essai de catalogue sur une
        Omega cite Rolex trois fois. Les conditionnelles lisent en plus les 200
        premiers caracteres de la description. Les attributs lisent tout.
        """
        type_source = (type_source or "").upper()
        titre_n = normaliser(titre)
        identite = normaliser(f"{titre} {maker}" if maker else titre)
        conditionnel_n = titre_n
        if description:
            conditionnel_n = normaliser(f"{titre} {str(description)[:200]}")

        # R0 — la categorie publiee par la source. Un vendeur qui range sa fiche
        # en 'Necklaces' a deja tranche, et il a l'objet en main. Trois etats :
        # montre, pas une montre, ou rien de publie.
        categorie = self.categorie(categorie_source)

        token = any(present(t, identite) for t in self.tokens) or categorie is True
        # Les exceptions traversees sont conservees a part : la regle terminale
        # les ecrase, or c'est justement leur effet qu'on veut pouvoir mesurer.
        resultat = {"verdict": None, "rule": None, "brand": None, "concepts": [],
                    "set_completeness": None, "exceptions": [],
                    "filter_version": self.version}

        def conclure(verdict, regle, **extra):
            resultat.update(verdict=verdict, rule=regle, **extra)
            return resultat

        if categorie is False:
            return conclure(REJETER, "R0")

        # R1 — exclusion dure. Bijoux, horloges, contrefacons, lots melanges.
        durs = [(e, terme, pos) for e, terme, pos in self._touches(
            self.durs, identite, type_source)]
        if durs:
            # R1b — un reveil au poignet n'est pas un reveil de chevet. Le terme
            # de complication ne suffit pas : il faut aussi le mot montre.
            seuls_reveils = all(e["concept"] == "alarm_clock" for e, _, _ in durs)
            # La preuve de complication ne doit pas etre LE MOT qui a declenche
            # le rejet. 'Seiko alarm clock' : 'alarm clock' nomme l'objet, et
            # 'alarm' n'est que sa premiere moitie. On exige donc une occurrence
            # situee hors de l'empan du terme dur.
            empans = [(p, p + len(normaliser(terme)))
                      for _, terme, positions in durs for p in positions]
            complication = any(
                not any(debut <= p < fin for debut, fin in empans)
                for e in self.reveil for t in e["terms"]
                for p in _positions(t, identite))
            # Une marque horlogere reconnue vaut la meme preuve qu'un token :
            # 'Blancpain Leman Reveil GMT' n'ecrit pas le mot montre et n'en
            # est pas moins une montre. Le garde-fou tient parce que R1b ne
            # s'applique que si alarm_clock est la SEULE exclusion dure — une
            # pendulette de voyage declenche aussi desk_clock.
            marque_connue = any(
                any(present(x, identite) for x in [b["name"]] + b["aliases"])
                for b in self.conf["brands"] if self._scope_ok(b["scope"], type_source))
            if not (seuls_reveils and (token or marque_connue) and complication):
                return conclure(REJETER, "R1", concepts=[durs[0][0]["concept"]])
            resultat["exceptions"].append("R1b")

        # R2 — la negation de categorie. "no watch", "sans montre", "ohne Uhr".
        if self._marqueur("NEGATION_CATEGORY", identite):
            return conclure(REJETER, "R2")

        # R3 — la porte positive : sans marque connue, on ne garde pas.
        marque = None
        for b in self.conf["brands"]:
            if not self._scope_ok(b["scope"], type_source):
                continue
            if any(present(x, identite) for x in [b["name"]] + b["aliases"]):
                marque = b
                break
        if marque is None:
            return conclure(REJETER, "R3")
        resultat["brand"] = marque["name"]

        # R3b — montre de poche chez une marque qui n'en a jamais produit.
        if not marque["accept_pocket"] and any(
                present(t, identite) for e in self.poche for t in e["terms"]):
            return conclure(REJETER, "R3b", concepts=["case_pocket"])

        # R4 — marque a nom ambigu sans le mot montre.
        if marque["requires_category_token"] and not token:
            # R4c — sauf si la source ne publie que des montres. Dans une vente
            # de la specialite MONTRES, exiger le mot "montre" dans le titre du
            # lot n'a aucun sens : la categorie est garantie par le corpus.
            # Seule R4 est concernee ; les exclusions dures et les pieces
            # detachees continuent de s'appliquer.
            if corpus_horloger:
                resultat["exceptions"].append("R4c")
            else:
                # R4b — sauf si le titre porte une reference : ni un lot
                # Christie's ni une annonce de marketplace n'ecrivent le mot
                # "watch", et un bijou ne porte pas de reference constructeur.
                # C'est une preuve positive, independante du type de source.
                if not (self.ref_vaut_token and REFERENCE.search(titre or "")):
                    return conclure(REJETER, "R4")
                resultat["exceptions"].append("R4b")

        # Les pieces detachees : le mot n'est jamais le signal, le marqueur l'est.
        touches = list(self._touches(self.conditionnels, conditionnel_n, type_source))
        concepts = sorted({e["concept"] for e, _, _ in touches})

        if touches:
            # R5 — vendu seul. "bracelet only", "cadran seul", "Ersatz".
            if self._marqueur("EXCLUSIVITY", conditionnel_n):
                return conclure(REJETER, "R5", concepts=concepts)
            # R6 — l'accompagnement d'une montre. "no box no papers" decrit un
            # set incomplet : c'est une variable de prix, pas un dechet.
            if self._marqueur("COMPLETENESS", conditionnel_n):
                return conclure(GARDER, "R6", concepts=concepts,
                                set_completeness=self._completude(conditionnel_n))
            # R6b — le qualificatif descriptif. "white dial", "cadran tropical".
            if any(self._descriptif_devant(p, conditionnel_n)
                   for _, _, positions in touches for p in positions):
                return conclure(GARDER, "R6b", concepts=concepts)
            # R6c — deux accessoires cites ensemble decrivent une montre complete.
            # "Box & Papers" et "Box, Papers.." disent la meme chose que "full
            # set" ; poursuivre les variantes de ponctuation n'aurait pas de fin.
            accessoires = {e["concept"] for e, _, _ in touches
                           if e["axis"] == "ACCESSORIES"}
            if len(accessoires) >= 2:
                return conclure(GARDER, "R6c", concepts=concepts,
                                set_completeness="|".join(sorted(accessoires)))
            # R7a — le texte ne tranche pas : la source tranche a sa place.
            # `token` est vrai des que la categorie publiee dit 'montre'.
            if token or type_source == "AUCTION":
                return conclure(GARDER, "R7a", concepts=concepts)
            return conclure(QUARANTAINE, "R7a", concepts=concepts)

        # R8 — rien ne s'oppose a l'entree.
        return conclure(GARDER, "R8")

    def categorie(self, libelle):
        """True = montre, False = autre chose, None = la source ne dit rien.

        Le libelle vient de la source telle qu'elle s'exprime : 'Watch',
        'Timepiece', 'Mens Watches', 'Necklaces', 'Vintage Collectibles'.
        """
        if not libelle:
            return None
        # Une source peut publier PLUSIEURS etiquettes pour une meme fiche :
        # ['Brands', 'Cartier', 'Mens Watches']. Une seule etiquette horlogere
        # suffit a trancher ; si toutes sont muettes ou de navigation, la
        # source n'a rien dit.
        etiquettes = [normaliser(x).strip().replace("_", " ")
                      for x in re.split(r"[·|,/>]|\s{2,}", str(libelle)) if x.strip()]
        if not etiquettes:
            return None
        # 1. Le NOM-TETE tranche, et il est en derniere position : « Watch Boxes »
        #    sont des boites, « Bracelet Watches » sont des montres. Les deux
        #    portent les deux signaux ; seule la place du mot les distingue.
        if any(_CATEGORIE_MONTRE.search(e.split()[-1])
               for e in etiquettes if e.split()):
            return True
        # 2. Le nom-tete n'est pas horloger. Si la source nomme un accessoire ou
        #    une famille non horlogere, c'est le SEUL cas ou son etiquette
        #    autorise un « non ».
        if any(_CATEGORIE_ACCESSOIRE.search(e) for e in etiquettes):
            return False
        if any(_CATEGORIE_NON_HORLOGERE.search(e) for e in etiquettes):
            return False
        # 3. Un mot horloger ailleurs qu'en tete, sans accessoire pour le
        #    qualifier : la source parle bien d'horlogerie.
        if any(_CATEGORIE_MONTRE.search(e) for e in etiquettes):
            return True
        # 3. Tout le reste ne dit RIEN, et se lit sur le titre. Une etiquette
        #    qui n'est qu'un nom de marque ne classe pas ('Brands', 'Cartier'
        #    ne dit pas si l'objet est une montre ou un briquet) — mais un nom
        #    de MODELE ('Seamaster'), un type d'usage ('Sports & Tool · Dress')
        #    ou un rangement maison ('A-Rolex', 'Archive') n'en disent pas plus.
        #    Rendre False ici revenait a inventer un « non » que la source
        #    n'avait jamais prononce.
        return None

    def marque_canonique(self, ecrit):
        """'ROLEX', 'Jaeger Le Coultre' -> 'Rolex', 'Jaeger-LeCoultre'.

        Les sources ecrivent la meme maison de neuf facons — mesure du
        29/08/2026 : 109 groupes de graphies pour 946 marques apparentes, et
        95 906 lignes concernees. Jaeger-LeCoultre a lui seul en portait neuf.
        Deux graphies font deux marques, donc deux modeles distincts pour la
        meme montre : la cote se coupe en deux sans que rien ne le signale.

        Le dictionnaire du filtre porte deja le nom canonique et ses alias.
        C'est lui qui tranche, et rien d'autre : on ne devine pas une marque
        qu'il ne connait pas, on la laisse telle quelle.
        """
        if not ecrit:
            return None
        cle = _sans_signes(str(ecrit))
        if not cle:
            return None
        if not hasattr(self, "_canoniques"):
            table = {}
            for b in self.conf["brands"]:
                for graphie in [b["name"], *b.get("aliases", [])]:
                    table.setdefault(_sans_signes(graphie), b["name"])
            self._canoniques = table
        return self._canoniques.get(cle, str(ecrit).strip() or None)

    def _est_une_marque(self, etiquette: str) -> bool:
        """L'etiquette n'est-elle qu'un nom de marque, eventuellement prefixe ?

        Amsterdam Watch Company range son archive en 'A-Rolex', 'A-Omega'. Une
        comparaison stricte n'y voyait pas la marque, et R0 rejetait 2 263
        montres. On tolere donc un prefixe d'archive et on cherche la marque
        comme un mot entier dans une etiquette courte.
        """
        propre = re.sub(r"^(a|archive|sold|pre.?owned|vintage|used)\s*[- ]\s*", "",
                        etiquette).strip()
        if not propre or len(propre.split()) > 4:
            return False
        for b in self.conf["brands"]:
            for libelle in [b["name"]] + b["aliases"]:
                normalise = normaliser(libelle)
                if normalise == propre or present(normalise, propre):
                    return True
        return False

    def _completude(self, texte) -> str:
        """full set / watch only / partiel — l'ecart de prix entre les deux est
        une variable de pricing, autant la nommer des l'ingestion."""
        complet = [a for a in self.conf["attributes"]
                   if a["group"] == "SET_COMPLETENESS"
                   and any(present(t, texte) for t in a["terms"])]
        if not complet:
            return "inconnu"
        cles = sorted({a["key"] for a in complet})
        return "|".join(cles)

    def attributs(self, titre, description=None) -> dict[str, list[str]]:
        """Extraction pure, sans effet filtrant, toutes langues confondues."""
        texte = normaliser(f"{titre} {description}" if description else titre)
        trouves: dict[str, set] = {}
        for a in self.conf["attributes"]:
            if any(present(t, texte) for t in a["terms"]):
                trouves.setdefault(a["group"].lower(), set()).add(a["key"])
        return {groupe: sorted(cles) for groupe, cles in trouves.items()}


_filtre: Filtre | None = None


def filtre() -> Filtre:
    """Instance partagee — la config n'est lue qu'une fois par processus."""
    global _filtre
    if _filtre is None:
        _filtre = Filtre()
    return _filtre


def verdict(titre, type_source, maker=None, description=None,
            corpus_horloger=False, categorie_source=None) -> dict:
    return filtre().verdict(titre, type_source, maker, description,
                            corpus_horloger, categorie_source)


# ---------------------------------------------------------------------------
# Le banc de test. Un cas rouge doit rendre le build rouge.
# ---------------------------------------------------------------------------
def banc() -> int:
    f = filtre()
    cas = f.conf["test_cases"]
    echecs = []
    for c in cas:
        obtenu = f.verdict(c["title"], c["source_type"],
                           corpus_horloger=c.get("watch_corpus", False),
                           categorie_source=c.get("source_category"))
        if obtenu["verdict"] != c["expected"]:
            echecs.append((c, obtenu))

    for c, obtenu in echecs:
        print(f"  ECHEC #{c['id']:>3}  attendu {c['expected']:<11} obtenu "
              f"{obtenu['verdict']:<11} par {obtenu['rule']}")
        print(f"           {c['title'][:88]}")
        print(f"           regle visee : {c.get('rule') or 'non renseignee'}")

    print(f"\n  {len(cas) - len(echecs)}/{len(cas)} cas de test passent "
          f"(filtre du {f.version})")
    return len(echecs)


def corpus_par_source() -> dict:
    """Quelles sources declarent un corpus exclusivement horloger.

    Import differe : les adaptateurs importent ce module (Artcurial se sert du
    dictionnaire de marques), l'importer en tete creerait un cycle.
    """
    try:
        from watchpoint import sources
    except Exception:
        return {}
    return {m.SOURCE["id"]: bool(m.SOURCE.get("corpus_horloger"))
            for m in sources.ALL}


def sur_la_base() -> None:
    """Ce que le filtre ferait du cumul actuel. Aucune ecriture, aucun reseau."""
    import collections

    cumul = config.DATA / "price_points.jsonl"
    if not cumul.exists():
        sys.exit(f"cumul introuvable : {cumul}")

    f = filtre()
    corpus = corpus_par_source()
    par_source = collections.defaultdict(collections.Counter)
    regles = collections.Counter()
    exemples = collections.defaultdict(list)

    with cumul.open(encoding="utf-8") as flux:
        for ligne in flux:
            rec = json.loads(ligne)
            type_source = "AUCTION" if rec.get("source_type") == "auction" else "MARKETPLACE"
            r = f.verdict(rec.get("title") or "", type_source, maker=rec.get("brand"),
                          corpus_horloger=corpus.get(rec["source_id"], False),
                          categorie_source=rec.get("source_category"))
            par_source[rec["source_id"]][r["verdict"]] += 1
            if r["verdict"] != GARDER:
                cle = f"{r['verdict']} {r['rule']}" + (
                    f" ({r['concepts'][0]})" if r["concepts"] else "")
                regles[cle] += 1
                if len(exemples[cle]) < 2:
                    exemples[cle].append((rec["source_id"], (rec.get("title") or "")[:84]))

    print(f"\n  {'source':<20}{'garder':>8}{'rejeter':>9}{'quarant.':>10}{'% garde':>9}")
    total = collections.Counter()
    for source, compte in sorted(par_source.items()):
        total.update(compte)
        n = sum(compte.values())
        print(f"  {source:<20}{compte[GARDER]:>8}{compte[REJETER]:>9}"
              f"{compte[QUARANTAINE]:>10}{100 * compte[GARDER] / n:>8.1f}%")
    n = sum(total.values())
    print(f"  {'TOTAL':<20}{total[GARDER]:>8}{total[REJETER]:>9}"
          f"{total[QUARANTAINE]:>10}{100 * total[GARDER] / n:>8.1f}%")

    print("\n  ce qui ne passe pas :")
    for cle, compte in regles.most_common(12):
        print(f"    {compte:>5}  {cle}")
        for source, titre in exemples[cle]:
            print(f"           [{source}] {titre}")


def marquer_la_base() -> None:
    """Rejoue le filtre courant sur tout le cumul et reinscrit les verdicts.

    C'est la promesse tenue : le filtre change, on relit l'historique deja
    collecte, on remplace les verdicts, et pas une seule requete reseau n'est
    envoyee. Les lignes anterieures a la mise en place du marquage recoivent
    ainsi leur verdict, et une correction de l'Excel se propage a tout le passe.

    L'ecriture passe par un fichier temporaire : une interruption en cours de
    route ne peut pas laisser un cumul a moitie reecrit.
    """
    import collections

    cumul = config.DATA / "price_points.jsonl"
    if not cumul.exists():
        sys.exit(f"cumul introuvable : {cumul}")

    f = filtre()
    corpus = corpus_par_source()
    provisoire = cumul.with_suffix(".jsonl.tmp")
    avant, apres = collections.Counter(), collections.Counter()
    n = 0

    with cumul.open(encoding="utf-8") as entree, provisoire.open("w", encoding="utf-8") as sortie:
        for ligne in entree:
            if not ligne.strip():
                continue
            record = json.loads(ligne)
            avant[record.get("filter_verdict") or "aucun"] += 1
            type_source = "AUCTION" if record.get("source_type") == "auction" else "MARKETPLACE"
            r = f.verdict(record.get("title") or "", type_source, maker=record.get("brand"),
                          corpus_horloger=corpus.get(record["source_id"], False),
                          categorie_source=record.get("source_category"))
            record["filter_verdict"] = r["verdict"]
            record["filter_rule"] = r["rule"]
            record["filter_version"] = r["filter_version"]
            apres[r["verdict"]] += 1
            sortie.write(json.dumps(record, ensure_ascii=False) + "\n")
            n += 1

    provisoire.replace(cumul)
    print(f"  {n} lignes remarquees avec le filtre du {f.version}")
    print(f"  avant : {dict(avant)}")
    print(f"  apres : {dict(apres)}")


if __name__ == "__main__":
    if "--base" in sys.argv:
        sur_la_base()
    elif "--marquer" in sys.argv:
        marquer_la_base()
    else:
        sys.exit(1 if banc() else 0)
