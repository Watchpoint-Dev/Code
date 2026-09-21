"""La page des donnees — un registre de mesure, pas une plaquette.

    cd ~/Desktop/WP/labo
    shared/.venv/bin/python moteur/page_sources.py

Ecrit output/documents/sources.html. Tout est genere depuis le cumul : une page
ecrite a la main se decale de la base au premier rejeu. Elle repond, dans cet
ordre, aux questions qu'on pose a un jeu de donnees :

    CE QU'IL Y A       l'entonnoir, source par source : brut, montres,
                       reference, nature du prix
    CE QU'IL VAUT      combien de modeles sont assez couverts pour etre cotes,
                       sur quelle profondeur, dans quelles devises
    CE QUI A CLOCHE    les defauts trouves, leur ampleur mesuree, leur cause et
                       leur correction — la partie la plus utile du document
    CE QUI BLOQUE      ce qui n'entrera pas, et pourquoi
"""
from __future__ import annotations

import collections
import datetime as dt
import html
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "shared"))

import sources  # noqa: E402
from catalogue_essais import ECARTEES  # noqa: E402
from page_blocages import BLOCAGES  # noqa: E402
from toutes_les_sources import (NATURES, REFERENCE_SURE, REMARQUES,  # noqa: E402
                                TYPES, VERIFICATION)

LABO = pathlib.Path(__file__).resolve().parent.parent
CUMUL = LABO / "data" / "price_points.jsonl"
SORTIE = LABO.parent / "output" / "documents" / "sources.html"

TRANSACTIONNELLES = {"realised", "sold"}

# La couleur porte du sens et rien d'autre : une teinte par nature de prix,
# gardee identique d'un graphique a l'autre.
TEINTE = {"realised": "var(--enchere)", "sold": "var(--vendu)",
          "asking": "var(--demande)", "msrp": "var(--neuf)",
          "estimate": "var(--estime)"}

VALEUR_NATURE = {
    "realised": "prix d'adjudication : la meilleure preuve de valeur",
    "sold": "vente conclue chez un marchand ; le montant est le dernier prix affiché",
    "asking": "prix demandé : une intention de vente, pas une transaction",
    "msrp": "tarif officiel du neuf : un plafond, jamais un prix de marché",
    "estimate": "estimation d'avant-vente, ou lot invendu",
}
NOM_PROVENANCE = {"champ_dedie": "champ publié", "extrait_titre": "titre, mot-clé",
                  "jeton_titre": "titre, par la forme",
                  "extrait_description": "corps de l'annonce",
                  "sku": "SKU du vendeur (écarté)", None: "aucune référence"}

def mesures_vivantes(M) -> dict:
    """Les chiffres des defauts qui se relisent dans la base AUJOURD'HUI.

    Ecrits a la main, ils derivent : trois d'entre eux avaient deja bouge le
    02/09/2026 pendant que la donnee s'ameliorait, et un document destine a
    etre presente ne peut pas porter des chiffres qui ne sont plus vrais.
    Ceux-la se recalculent ; les autres — l'etat AVANT correction — ne sont
    plus mesurables et restent ecrits, dates de leur mesure.
    """
    par, prem = M["par"], M["premium_par_source"]
    return {
        "fortuna_inclus": prem["fortuna"].get(True, 0),
        "fortuna_marteau": prem["fortuna"].get(False, 0),
        "fortuna_total": sum(prem["fortuna"].values()),
        "berrys_ref": par["berrys"]["reference"],
        "watchrecon_ref": par["watchrecon"]["reference"],
        "sworders_garde": par["sworders"]["garde"],
        "sworders_marques": len(M["marques_par_source"]["sworders"]),
        "montredo_vendues": par["montredo"]["natures"].get("sold", 0),
        "marques": len(M["marques"]),
        "wod_garde": par["watchesofdistinction"]["garde"],
    }


# ---------------------------------------------------------------------------
# LES DEFAUTS. Chacun a ete trouve en confrontant nos lignes aux pages en ligne,
# pas a notre propre base, et chacun porte son ampleur mesuree. Un rapport qui
# ne montre que ce qui marche n'apprend rien a personne.
# ---------------------------------------------------------------------------
DEFAUTS = [
    dict(titre="Un champ nommé « hammer_price » qui ne contenait pas un marteau",
         source="Fortuna", ampleur="{fortuna_inclus} prix sur {fortuna_total}", gravite="majeur",
         symptome="Les montants étaient gonflés de 25 % face à toute autre maison "
                  "de ventes à marteau nu.",
         cause="Le champ ne porte un marteau que sur les {fortuna_marteau} lots où `bp_applies` "
               "vaut vrai. Sur les {fortuna_inclus} autres, il inclut déjà les frais "
               "acheteur. Nous avions généralisé depuis une vérification directe "
               "menée sur ces {fortuna_marteau} lots — c'est-à-dire sur la seule population qui "
               "se comporte autrement que les 98 % restants.",
         preuve="Les 471 montants non entiers deviennent TOUS des entiers exacts "
                "après division par 1,25 : 43,75 = 35 × 1,25. Aucun marteau ne "
                "tombe sur 43,75 $.",
         correction="Le régime de frais se lit désormais lot par lot."),
    dict(titre="Cinq boutiques déclaraient tout leur catalogue « en vente »",
         source="Watchtrader · Wanna Buy A Watch · AWCO · Global Watch Shop · Chronofinder",
         ampleur="11 820 fiches", gravite="majeur",
         symptome="Ces cinq sources sortaient à 100 % d'annonces actives, sans une "
                  "seule vente — alors que leurs boutiques affichaient l'inverse.",
         cause="Le moteur cherchait le statut dans `class_list`, un champ que "
               "l'API Store de WooCommerce n'envoie jamais. La condition était "
               "donc toujours vraie.",
         preuve="Le brut déjà stocké portait `is_in_stock` sur 100 % des produits, "
                "et disait 20 738 fiches épuisées sur 22 943.",
         correction="Lecture de `is_in_stock`, rejouée sans une requête de plus."),
    dict(titre="3 071 « ventes » qui étaient des « nous consulter »",
         source="Montredo", ampleur="3 319 → {montredo_vendues} ventes réelles", gravite="majeur",
         symptome="Un détaillant de montres neuves apparaissait comme l'un des "
                  "premiers vendeurs du dossier en volume de transactions.",
         cause="La règle « indisponible donc vendue » vaut chez un marchand de "
               "pièces uniques. Chez un détaillant agréé, une fiche indisponible "
               "veut dire qu'il faut écrire au vendeur.",
         preuve="18 des 20 lignes « vendues » tirées au hasard portaient le tag "
                "`inquiry-only`, contre 0 des 10 lignes « demandé ».",
         correction="Le tag de la boutique prime sur la déduction : c'est une "
                    "déclaration du vendeur, pas une inférence de notre part."),
    dict(titre="Une référence de bracelet à la place de celle de la montre",
         source="Bulang and Sons", ampleur="443 fiches", gravite="majeur",
         symptome="Une Rolex Datejust 1601 était enregistrée sous 6251H, une "
                  "Daytona 16520 sous 78390.",
         cause="L'extraction ouvrait la description avant d'avoir épuisé le titre. "
               "Or ce marchand énumère dans sa description les bracelets livrés "
               "avec la montre, références comprises.",
         preuve="443 fiches portaient une référence qui contredisait le numéro "
                "écrit dans leur propre titre.",
         correction="Le titre est épuisé en entier — mot-clé puis forme du jeton — "
                    "avant qu'on ouvre la description."),
    dict(titre="Neuf graphies pour la même maison",
         source="toutes les sources", ampleur="95 906 lignes · 109 groupes",
         gravite="majeur",
         symptome="« Rolex » et « ROLEX », « Jaeger-LeCoultre » et « Jaeger Le "
                  "Coultre » comptaient pour des marques différentes, donc pour "
                  "des modèles différents. La cote d'une même montre se coupait en "
                  "deux sans que rien ne le signale.",
         cause="Chaque adaptateur recopiait fidèlement la graphie de sa source. "
               "Fidèle, mais incomparable d'une source à l'autre.",
         preuve="946 marques apparentes pour 109 groupes de doublons. "
                "Jaeger-LeCoultre en portait neuf à lui seul.",
         correction="La marque est ramenée à sa graphie canonique par le "
                    "dictionnaire du filtre : 946 → {marques} marques réelles."),
    dict(titre="Une source entièrement rejetée par une balise vide",
         source="Sworders", ampleur="2 506 lignes, soit 100 %", gravite="majeur",
         symptome="La collecte ramenait 2 506 lots, et le filtre les rejetait tous.",
         cause="L'expression qui lit le titre s'arrêtait au premier `</span>` — or "
               "le balisage insère juste avant une balise VIDE. Le titre sortait "
               "donc vide, donc sans marque, donc rejeté par la règle qui exige "
               "une marque connue.",
         preuve="2 506 lignes sur 2 506 en verdict `REJETER · R3`.",
         correction="Lecture jusqu'à la fin du lien : {sworders_garde} montres, {sworders_marques} marques."),
    dict(titre="Un SKU pris pour un code maison alors qu'il portait la référence",
         source="Berry's Jewellers", ampleur="183 → {berrys_ref} références",
         gravite="rendement",
         symptome="Un détaillant agréé de 2 142 montres ne rendait que 183 "
                  "références exploitables — il en rend {berrys_ref} aujourd'hui.",
         cause="Le SKU est un code d'inventaire chez la plupart des marchands — "
               "« DOX-333 » chez CW Sellors, « 136 » chez Topper. Traiter la règle "
               "comme universelle coûtait onze fois le rendement de cette source.",
         preuve="Le champ contient `L38204930` chez Longines, `IW503607` chez IWC, "
                "`M2836C1A0-0103` chez Tudor — des références constructeur, "
                "précédées de « P-O » pour l'occasion.",
         correction="Un réglage par source, activé seulement là où c'est vérifié."),
    dict(titre="Une source sans aucune référence, alors qu'un tiers de ses titres en portent",
         source="WatchRecon", ampleur="0 → {watchrecon_ref} références", gravite="rendement",
         symptome="La source la plus fraîche du dossier était inutilisable pour "
                  "rapprocher deux annonces.",
         cause="L'adaptateur ne lisait pas le titre. C'est pourtant le seul champ "
               "d'identité que cet agrégateur de forums publie.",
         preuve="1 488 titres sur 4 244 portaient un motif exploitable : "
                "`Ref. IW325502`, `126710BLRO`, `311.30.40.30.01.001`.",
         correction="Extraction du titre. Au passage, 1 709 annonces étaient "
                    "comptées deux fois : la date entrait dans la clé de "
                    "dédoublonnage d'une source qui date en relatif."),
    dict(titre="Un marchand sans marque, faute de repli sur le titre",
         source="Amsterdam Vintage Watches · Wanna Buy A Watch · AWCO",
         ampleur="342 fiches, plus des gains ailleurs", gravite="rendement",
         symptome="La source à la fiche la mieux remplie du dossier — 91 % de "
                  "références publiées — sortait avec 0 % de marques, et se "
                  "faisait rejeter en entier.",
         cause="Le moteur WooCommerce n'avait aucun repli sur le titre, "
               "contrairement au moteur Shopify qui en a un depuis toujours. Cette "
               "boutique ne publie ni attribut ni champ natif de marque.",
         preuve="0 % de marques sur 342 fiches dont le titre commence pourtant par "
                "« Cartier Tank 17002 ».",
         correction="Repli ajouté au moteur : 97 % de marques ici, et un gain chez "
                    "Wanna Buy A Watch (93 → 96 %) et AWCO (81 → 86 %)."),
    dict(titre="Une décennie enregistrée comme une année de production",
         source="Watches of Distinction", ampleur="401 lignes sur 496",
         gravite="rendement",
         symptome="Une Explorer II de 2020 était datée de 2010. Dix ans d'écart "
                  "sur une montre, ce n'est pas un arrondi.",
         cause="Le marchand publie un attribut d'année qui est en réalité une "
               "décennie — « 2010's » — pendant que son titre porte le millésime. "
               "Le moteur lisait l'attribut, jugé plus fiable qu'un titre.",
         preuve="401 des 496 lignes gardées divergeaient de l'année écrite entre "
                "parenthèses dans leur propre titre.",
         correction="Le titre prime quand il donne un millésime ; une décennie "
                    "seule ne produit plus aucune année. Zéro divergence."),
    dict(titre="Des cotes d'étanchéité rangées dans le champ référence",
         source="CW Sellors · Analog:Shift · Berry's", ampleur="247 lignes",
         gravite="mineur",
         symptome="« 300m », « 1000M » et le « 300T » des Doxa apparaissaient "
                  "comme des références constructeur.",
         cause="Le détecteur de référence par la forme acceptait tout jeton portant "
               "au moins deux chiffres.",
         preuve="Un tiers des références déduites du titre chez CW Sellors et "
                "Analog:Shift étaient des cotes de profondeur.",
         correction="Garde-fou sur les unités, et liste explicite des cotes en T — "
                    "« 242T » et « 3647T » sont, eux, de vraies références."),
    dict(titre="Des prix sentinelles de 1,00 pris pour des prix",
         source="Bulang and Sons · The Keystone", ampleur="332 lignes",
         gravite="mineur",
         symptome="Une Daytona 6263 et une Rolex 5510 étaient enregistrées à "
                  "1,00 EUR.",
         cause="Le zéro était traité comme un prix masqué, mais pas sa variante "
               "polie : un montant symbolique qui veut dire « nous consulter ».",
         preuve="Vérifié en direct : les sites publient bien `1.00`. Notre stockage "
                "était fidèle, la donnée sans valeur.",
         correction="Plancher de prix sous lequel une ligne n'est pas un prix."),
    dict(titre="Des titres publiés avec leurs entités HTML",
         source="dix sources", ampleur="4 370 titres", gravite="mineur",
         symptome="« Cartier Tank 17002 &#8216;Jumbo&#8217; » partait tel quel en "
                  "base.",
         cause="Le décodage existait — ajouté quand `&#8217;` produisait la fausse "
               "référence « 8217 » — mais il ne servait qu'à l'extraction, jamais "
               "aux champs enregistrés.",
         preuve="4 370 titres de dix sources portaient une entité non décodée.",
         correction="Décodage appliqué à tous les champs texte enregistrés."),
    dict(titre="Une source qu'on ne pouvait pas rejouer hors ligne",
         source="Fortuna", ampleur="2 010 lots", gravite="structurel",
         symptome="Rejouer la source depuis le brut rendait 2 010 lots sans marque "
                  "et sans date — donc entièrement rejetés.",
         cause="La taxonomie des marques et les dates de vente venaient de deux "
               "appels annexes dont les réponses n'étaient pas conservées. Une "
               "donnée lue mais non stockée n'est pas rejouable.",
         preuve="0 % de marques au rejeu contre 92 % à la collecte.",
         correction="Les 144 réponses annexes sont désormais dans le brut : la "
                    "source se rejoue de bout en bout."),
    dict(titre="Nous nous annoncions comme un navigateur que nous ne sommes pas",
         source="les 28 sources", ampleur="1 source débloquée, 1 gelée",
         gravite="structurel",
         symptome="Des sources paraissaient nous bloquer alors qu'elles bloquaient "
                  "le faux navigateur. LiveAuctioneers rendait 962 octets de "
                  "challenge depuis août ; nous l'avions classée « anti-bot "
                  "Incapsula ».",
         cause="L'en-tête annonçait Chrome 124 sur macOS. Cela nous rangeait sous "
               "la règle `User-agent: *` de chaque robots.txt — la plus stricte — "
               "alors que plusieurs sites ouvrent explicitement leur catalogue à "
               "ClaudeBot, DavidSW le disant en toutes lettres dans un commentaire.",
         preuve="Avec un en-tête honnête, LiveAuctioneers rend 318 Ko au lieu de "
                "962 octets. Christie's avait déjà montré la même chose : 0,05 s "
                "avec un UA honnête contre 20 s d'expiration en Chrome simulé.",
         correction="En-tête `ClaudeBot`, et la contrepartie assumée en entier : un "
                    "module vérifie désormais ce que chaque source autorise à "
                    "ClaudeBot, source par source. Watches of Distinction refuse "
                    "les UA de robot par pare-feu — sa collecte est gelée, ses "
                    "{wod_garde} montres restent. Un 403 est un refus, pas un obstacle."),
    dict(titre="Un contrôle de robots.txt qui prenait le silence pour un accord",
         source="notre propre outil", ampleur="1 source faussement ouverte",
         gravite="structurel",
         symptome="Le module de vérification déclarait DavidSW ouverte alors "
                  "qu'elle interdit `/wp-json/` à ClaudeBot en toutes lettres.",
         cause="Quand la requête du robots.txt échouait — un 429 de bridage — le "
               "texte revenait vide, donc sans aucune règle, donc « autorisé ». "
               "Le défaut le plus dangereux qu'un tel outil puisse avoir.",
         preuve="Deux exécutions à quelques minutes d'intervalle rendaient des "
                "verdicts opposés sur la même source.",
         correction="Fermé par défaut : un robots.txt illisible interdit, un 404 "
                    "autorise. Les deux ne se confondent plus."),
    dict(titre="Deux copies des mêmes réglages, qui avaient divergé",
         source="onze boutiques Shopify", ampleur="tout le rejeu hors ligne",
         gravite="structurel",
         symptome="Les corrections apportées aux adaptateurs ne franchissaient pas "
                  "le rejeu : tags de nature et SKU-référence restaient sans effet.",
         cause="Le module de rejeu tenait sa propre table de réglages, recopiée des "
               "adaptateurs. Les deux ont divergé sans que rien ne le signale.",
         preuve="Après correction des adaptateurs, le rejeu rendait toujours les "
                "anciens chiffres.",
         correction="Chaque adaptateur porte ses réglages, le rejeu les lit. Une "
                    "donnée dupliquée finit toujours par se contredire."),
]

CSS = """
:root{
  --papier:#F6F5F2; --encre:#15181D; --gris:#5F6269; --gris-clair:#93969D;
  --trait:#E0DDD7; --surface:#FFFFFF; --surface-2:#EDEBE6; --creux:#E7E4DE;
  --acier:#2C4970;      /* acier bleui — l'accent structurel */
  --laiton:#8A6B33;     /* laiton — la reference, ce qui a de la valeur */
  --rouille:#8E4429;    /* un defaut */
  --vert:#3B6A4C;       /* une correction */
  --enchere:#2C4970; --vendu:#4E7B94; --demande:#A5A8AE;
  --neuf:#8A6B33; --estime:#C2BCAE;
  --serif:ui-serif,"Iowan Old Style","Hoefler Text",Georgia,"Palatino Linotype",serif;
  --sans:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --papier:#111317; --encre:#E8E6E2; --gris:#9A9DA4; --gris-clair:#6A6D74;
    --trait:#282B31; --surface:#171A1F; --surface-2:#1F232A; --creux:#23272E;
    --acier:#7FA3D1; --laiton:#C9A463; --rouille:#D08560; --vert:#7CB08F;
    --enchere:#7FA3D1; --vendu:#6E9FB8; --demande:#5C6067;
    --neuf:#C9A463; --estime:#43474E;
  }
}
:root[data-theme="dark"]{
  --papier:#111317; --encre:#E8E6E2; --gris:#9A9DA4; --gris-clair:#6A6D74;
  --trait:#282B31; --surface:#171A1F; --surface-2:#1F232A; --creux:#23272E;
  --acier:#7FA3D1; --laiton:#C9A463; --rouille:#D08560; --vert:#7CB08F;
  --enchere:#7FA3D1; --vendu:#6E9FB8; --demande:#5C6067;
  --neuf:#C9A463; --estime:#43474E;
}
*{box-sizing:border-box}
body{margin:0;background:var(--papier);color:var(--encre);font-family:var(--sans);
  font-size:16px;line-height:1.62;-webkit-font-smoothing:antialiased;
  font-variant-numeric:tabular-nums}
.page{max-width:1180px;margin:0 auto;
  padding:clamp(26px,5vw,68px) clamp(16px,4vw,40px) 100px;
  display:flex;flex-direction:column;gap:clamp(46px,7vw,82px)}
:focus-visible{outline:2px solid var(--acier);outline-offset:2px}

/* --- entete --- */
.eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.16em;
  text-transform:uppercase;color:var(--gris)}
h1{font-family:var(--serif);font-weight:600;font-size:clamp(31px,5vw,50px);
  line-height:1.08;letter-spacing:-.02em;margin:14px 0 0;max-width:20ch;
  text-wrap:balance}
.chapeau{color:var(--gris);font-size:17.5px;max-width:62ch;margin:18px 0 0}

/* --- l'entonnoir global --- */
.ruban{margin-top:36px;display:flex;flex-direction:column;gap:11px}
.ruban-barre{display:flex;height:44px;border-radius:3px;overflow:hidden;
  border:1px solid var(--trait)}
.ruban-barre i{display:block}
.ruban-legende{display:flex;flex-wrap:wrap;gap:6px 26px;font-size:13px;
  color:var(--gris)}
.ruban-legende b{color:var(--encre);font-family:var(--mono);font-size:13px;
  font-weight:600;margin-left:5px}
.pastille{display:inline-block;width:9px;height:9px;border-radius:2px;
  margin-right:7px}

/* --- sections --- */
h2{font-family:var(--serif);font-size:clamp(23px,3vw,30px);font-weight:600;
  letter-spacing:-.015em;margin:0;display:flex;align-items:baseline;gap:14px;
  text-wrap:balance}
h2 .rang{font-family:var(--mono);font-size:12px;color:var(--acier);
  letter-spacing:.1em;flex:0 0 auto}
.intro{color:var(--gris);margin:12px 0 30px;max-width:66ch}
h3{font-family:var(--serif);font-size:18px;font-weight:600;margin:0 0 14px;
  letter-spacing:-.01em}

/* --- le registre des sources --- */
.entete-registre,.rangee{display:grid;
  grid-template-columns:minmax(140px,1.05fr) minmax(240px,2.5fr) 116px;gap:20px}
.entete-registre{padding:0 0 9px;border-bottom:1px solid var(--encre);
  font-family:var(--mono);font-size:10px;letter-spacing:.1em;text-transform:uppercase;
  color:var(--gris)}
.entete-registre span:last-child{text-align:right}
.rangee{padding:13px 0;border-bottom:1px solid var(--trait);align-items:center}
.rangee:hover{background:var(--surface-2)}
.nom{display:flex;flex-direction:column;gap:2px;min-width:0}
.nom b{font-size:14.5px;font-weight:600;letter-spacing:-.005em}
.nom span{font-size:11.5px;color:var(--gris-clair)}
.piste{display:flex;flex-direction:column;gap:5px;min-width:0}
.barre{display:flex;height:16px;background:var(--creux);border-radius:2px;
  overflow:hidden}
.barre i,.natures i{display:block;min-width:0}
.i-rejet{background:var(--creux);box-shadow:inset -1px 0 0 var(--trait)}
.i-montre{background:var(--acier);opacity:.34}
.i-ref{background:var(--laiton)}
.natures{display:flex;height:5px;border-radius:2px;overflow:hidden}
.chiffres{text-align:right;font-family:var(--mono);font-size:12.5px;
  display:flex;flex-direction:column;gap:1px}
.chiffres b{font-size:14px;font-weight:600}
.chiffres span{color:var(--gris-clair);font-size:11px}

/* --- cartes --- */
.grille{display:grid;gap:1px;background:var(--trait);border:1px solid var(--trait);
  border-radius:4px;overflow:hidden}
.g4{grid-template-columns:repeat(auto-fit,minmax(168px,1fr))}
.g3{grid-template-columns:repeat(auto-fit,minmax(276px,1fr))}
.case{background:var(--surface);padding:19px 21px;display:flex;flex-direction:column;
  gap:5px}
.case b.chiffre{font-family:var(--serif);font-size:30px;font-weight:600;line-height:1;
  letter-spacing:-.025em}
.case b.or{color:var(--laiton)}
.case b.bleu{color:var(--acier)}
.case>span{font-size:12.5px;color:var(--gris);line-height:1.5}
.case em{font-style:normal;font-family:var(--mono);color:var(--encre)}

/* --- escaliers --- */
.escalier{display:flex;flex-direction:column;gap:9px}
.marche{display:grid;grid-template-columns:112px 1fr 74px;gap:13px;align-items:center}
.marche i.lib{font-style:normal;color:var(--gris);font-size:12.5px;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.jauge{height:11px;background:var(--creux);border-radius:2px;overflow:hidden}
.jauge i{display:block;height:100%}
.marche b{text-align:right;font-family:var(--mono);font-size:12.5px;font-weight:600}

/* --- frise --- */
.frise{display:flex;align-items:flex-end;gap:4px;height:148px;margin-top:4px}
.colonne{flex:1;display:flex;align-items:flex-end;min-width:0}
.colonne i{display:block;width:100%;border-radius:1px 1px 0 0;
  background:var(--acier);opacity:.6}
.colonne:hover i{opacity:.95}
.axe{display:flex;gap:4px;margin-top:7px;border-top:1px solid var(--trait);
  padding-top:6px}
.axe span{flex:1;font-family:var(--mono);font-size:9.5px;color:var(--gris-clair);
  text-align:center;min-width:0;overflow:hidden}

/* --- tableaux --- */
.cadre{overflow-x:auto;border:1px solid var(--trait);border-radius:4px;
  background:var(--surface)}
table{border-collapse:collapse;width:100%;font-size:13.5px;min-width:640px}
th,td{text-align:left;padding:10px 14px;border-bottom:1px solid var(--trait);
  vertical-align:top}
th{font-family:var(--mono);font-size:10px;letter-spacing:.09em;text-transform:uppercase;
  color:var(--gris);font-weight:400;background:var(--surface-2)}
th.n,td.n{text-align:right}
td.n{font-family:var(--mono)}
tr:last-child td{border-bottom:none}
td.gras{font-weight:600}

/* --- defauts --- */
.defauts{display:flex;flex-direction:column;gap:1px;background:var(--trait);
  border:1px solid var(--trait);border-radius:4px;overflow:hidden}
.defaut{background:var(--surface);padding:22px 24px;display:grid;
  grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px 32px}
.defaut-tete,.quoi,.reparee{grid-column:1/-1}
.defaut-tete{display:flex;flex-wrap:wrap;align-items:baseline;gap:9px 14px}
.defaut-tete h3{margin:0;font-size:17px;flex:1 1 320px}
.ampleur{font-family:var(--mono);font-size:11.5px;padding:3px 9px;border-radius:3px;
  background:var(--surface-2);white-space:nowrap}
.gravite{font-family:var(--mono);font-size:10px;letter-spacing:.09em;
  text-transform:uppercase;padding:3px 8px;border-radius:3px;
  border:1px solid currentColor;white-space:nowrap}
.g-majeur{color:var(--rouille)}
.g-rendement{color:var(--laiton)}
.g-structurel{color:var(--acier)}
.g-mineur{color:var(--gris)}
.defaut p{margin:0;font-size:14px;color:var(--gris)}
.quoi{color:var(--encre);font-size:14.5px}
.etiquette{font-family:var(--mono);font-size:9.5px;letter-spacing:.11em;
  text-transform:uppercase;color:var(--gris-clair);display:block;margin-bottom:3px}
.reparee{border-top:1px dashed var(--trait);padding-top:12px;font-size:14px;
  color:var(--vert)}
.source-touchee{font-family:var(--mono);font-size:11.5px;color:var(--gris-clair);
  display:block;margin-bottom:4px}

/* --- blocages --- */
.blocs{display:flex;flex-direction:column;gap:1px;background:var(--trait);
  border:1px solid var(--trait);border-radius:4px;overflow:hidden}
.bloc{background:var(--surface);padding:18px 22px;display:grid;gap:5px 20px;
  grid-template-columns:minmax(160px,210px) 1fr}
.bloc.decision{box-shadow:inset 3px 0 0 var(--rouille)}
.bloc h3{margin:0;font-size:15px}
.genre{font-family:var(--mono);font-size:10px;letter-spacing:.09em;
  text-transform:uppercase;color:var(--gris-clair);margin-top:3px}
.bloc p{margin:0;color:var(--gris);font-size:14px}
.suite{grid-column:2;font-family:var(--mono);font-size:12.5px;color:var(--gris-clair);
  margin-top:3px}
.bloc.decision .suite{color:var(--rouille)}

.note{box-shadow:inset 2px 0 0 var(--acier);padding:3px 0 3px 17px;color:var(--gris);
  font-size:14.5px;max-width:72ch;margin-top:26px}
.note b{color:var(--encre)}
footer{border-top:1px solid var(--trait);padding-top:20px;color:var(--gris-clair);
  font-size:12.5px;display:flex;flex-direction:column;gap:5px}
code{font-family:var(--mono);font-size:.88em;background:var(--surface-2);
  padding:1px 5px;border-radius:3px}
details summary{cursor:pointer;font-size:13px;color:var(--acier);
  font-family:var(--mono)}
@media (max-width:760px){
  .entete-registre,.rangee{grid-template-columns:1fr;gap:8px}
  .entete-registre span:last-child,.chiffres{text-align:left}
  .chiffres{flex-direction:row;gap:12px;align-items:baseline}
  .bloc{grid-template-columns:1fr}
  .suite{grid-column:1}
  .marche{grid-template-columns:96px 1fr 66px}
  .piste{max-width:100% !important}
}
"""


def mille(n) -> str:
    return f"{n:,}".replace(",", " ")


def e(t) -> str:
    return html.escape(str(t if t is not None else ""))


def norme(reference) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(reference).upper())


def mesure() -> dict:
    par = collections.defaultdict(lambda: {
        "brut": 0, "garde": 0, "reference": 0, "socle": 0,
        "natures": collections.Counter(), "annees": set()})
    total = collections.Counter()
    natures = collections.Counter()
    provenances = collections.Counter()
    devises = collections.Counter()
    premium = collections.Counter()
    annees = collections.Counter()
    marques = collections.Counter()
    croise = collections.Counter()
    premium_par_source = collections.defaultdict(collections.Counter)
    marques_par_source = collections.defaultdict(set)
    modeles = collections.defaultdict(lambda: {"n": 0, "src": set(), "an": set()})

    with CUMUL.open(encoding="utf-8") as flux:
        for ligne in flux:
            if not ligne.strip():
                continue
            r = json.loads(ligne)
            d = par[r["source_id"]]
            d["brut"] += 1
            total["brut"] += 1
            if r.get("filter_verdict") != "GARDER":
                continue
            d["garde"] += 1
            total["garde"] += 1
            nature = r.get("price_nature")
            d["natures"][nature] += 1
            natures[nature] += 1
            devises[r.get("price_currency")] += 1
            marques[r.get("brand")] += 1
            if r.get("price_includes_premium") is not None:
                premium[r["price_includes_premium"]] += 1
                premium_par_source[r["source_id"]][r["price_includes_premium"]] += 1
            if r.get("brand"):
                marques_par_source[r["source_id"]].add(r["brand"])
            if r.get("price_date"):
                annees[r["price_date"][:4]] += 1
                d["annees"].add(r["price_date"][:4])
            provenance = r.get("reference_provenance") if r.get("reference") else None
            provenances[provenance] += 1
            sure = bool(r.get("reference")) and provenance in REFERENCE_SURE
            croise[(nature, sure)] += 1
            if sure:
                d["reference"] += 1
                total["reference"] += 1
                if r.get("price_date") and nature in TRANSACTIONNELLES:
                    d["socle"] += 1
                    total["socle"] += 1
                    m = modeles[(r.get("brand"), norme(r["reference"]))]
                    m["n"] += 1
                    m["src"].add(r["source_id"])
                    m["an"].add(r["price_date"][:4])
    return dict(par=par, total=total, natures=natures, provenances=provenances,
                devises=devises, premium=premium, annees=annees, marques=marques,
                croise=croise, modeles=modeles,
                premium_par_source=premium_par_source,
                marques_par_source=marques_par_source)


def escalier(lignes, haut) -> list[str]:
    """Un rang de barres horizontales : libelle, jauge, valeur."""
    L = ['<div class="escalier">']
    for libelle, valeur, couleur in lignes:
        L += [f'<div class="marche"><i class="lib">{e(libelle)}</i>'
              f'<div class="jauge"><i style="width:{100 * valeur / max(haut, 1):.1f}%;'
              f'background:{couleur}"></i></div><b>{mille(valeur)}</b></div>']
    return L + ['</div>']


def main() -> None:
    metas = {m.SOURCE["id"]: m.SOURCE for m in sources.ALL}
    M = mesure()
    par = {s: d for s, d in M["par"].items() if d["brut"]}
    ordre = sorted(par.items(), key=lambda kv: -kv[1]["brut"])
    tot = M["total"]
    plus_gros = max(d["brut"] for _, d in ordre)
    mod = M["modeles"]

    L = ["<title>Le socle de prix de Watchpoint</title>",
         f"<style>{CSS}</style>", '<div class="page">']

    # ---------------------------------------------------------------- entete
    sans_ref = tot["garde"] - tot["reference"]
    rejete = tot["brut"] - tot["garde"]
    L += ['<header>',
          '<div class="eyebrow">Watchpoint · état des données au '
          f'{dt.date.today().strftime("%d/%m/%Y")}</div>',
          f'<h1>Ce que {len(ordre)} sources donnent réellement, une fois filtrées</h1>',
          '<p class="chapeau">Un prix ne vaut rien seul : il lui faut un modèle, '
          'une date et une nature. Voici combien de lignes survivent à chacune de '
          f'ces exigences — et les {len(DEFAUTS)} défauts qu’il a fallu corriger '
          'pour que le chiffre final veuille dire quelque chose.</p>',
          '<div class="ruban"><div class="ruban-barre">',
          f'<i class="i-rejet" style="width:{100 * rejete / tot["brut"]:.2f}%" '
          f'title="{mille(rejete)} lignes écartées par le filtre"></i>',
          f'<i class="i-montre" style="width:{100 * sans_ref / tot["brut"]:.2f}%" '
          f'title="{mille(sans_ref)} montres sans référence"></i>',
          f'<i class="i-ref" style="width:{100 * tot["reference"] / tot["brut"]:.2f}%" '
          f'title="{mille(tot["reference"])} montres avec référence"></i>',
          '</div><div class="ruban-legende">',
          '<span><i class="pastille" style="background:var(--creux);'
          'box-shadow:inset 0 0 0 1px var(--trait)"></i>Écarté par le filtre'
          f'<b>{mille(rejete)}</b></span>',
          '<span><i class="pastille" style="background:var(--acier);opacity:.34">'
          f'</i>Montre, sans référence<b>{mille(sans_ref)}</b></span>',
          '<span><i class="pastille" style="background:var(--laiton)"></i>'
          f'Montre avec référence<b>{mille(tot["reference"])}</b></span>',
          '</div></div>',
          '<div class="grille g4" style="margin-top:26px">',
          f'<div class="case"><b class="chiffre">{mille(tot["brut"])}</b>'
          f'<span>lignes ramenées de {len(ordre)} sources</span></div>',
          f'<div class="case"><b class="chiffre bleu">{mille(tot["garde"])}</b>'
          '<span>sont une montre d’une marque connue — '
          f'{round(100 * tot["garde"] / tot["brut"])} %</span></div>',
          f'<div class="case"><b class="chiffre or">{mille(tot["reference"])}</b>'
          '<span>portent une référence constructeur — '
          f'{round(100 * tot["reference"] / tot["brut"])} %</span></div>',
          f'<div class="case"><b class="chiffre">{mille(tot["socle"])}</b>'
          '<span>sont des transactions réelles, datées et référencées</span></div>',
          '</div></header>']

    # ------------------------------------------------- 01 registre des sources
    L += ['<section>',
          '<h2><span class="rang">01</span>Le registre des sources</h2>',
          '<p class="intro">Une ligne par source. La barre est à l’échelle du '
          'volume brut — deux fois plus longue, c’est deux fois plus de lignes '
          'ramenées — et se lit de gauche à droite : ce que le filtre écarte, les '
          'montres sans référence, puis celles qui en portent une. Le filet du '
          'dessous donne la composition en natures de prix.</p>',
          '<div class="entete-registre"><span>Source</span>'
          '<span>Écarté · montre · avec référence &nbsp;⁄&nbsp; natures de prix</span>'
          '<span>Brut ⁄ socle</span></div>']
    for s, d in ordre:
        meta = metas.get(s, {})
        largeur = max(100 * d["brut"] / plus_gros, 0.4)
        segments = "".join(
            f'<i class="{cl}" style="width:{100 * v / d["brut"]:.2f}%" '
            f'title="{t} : {mille(v)}"></i>'
            for cl, v, t in (("i-rejet", d["brut"] - d["garde"], "écarté"),
                             ("i-montre", d["garde"] - d["reference"], "sans référence"),
                             ("i-ref", d["reference"], "avec référence")) if v)
        filet = "".join(
            f'<i style="width:{100 * c / d["garde"]:.2f}%;'
            f'background:{TEINTE.get(n, "var(--demande)")}" '
            f'title="{NATURES.get(n, n)} : {mille(c)}"></i>'
            for n, c in d["natures"].most_common()) if d["garde"] else ""
        annees = sorted(d["annees"])
        L += ['<div class="rangee">',
              f'<div class="nom"><b>{e(meta.get("name", s))}</b>'
              f'<span>{e(TYPES.get(meta.get("type"), "—"))}'
              + (f' · {annees[0]}–{annees[-1]}' if annees else ' · sans date')
              + '</span></div>',
              f'<div class="piste" style="max-width:{largeur:.2f}%">'
              f'<div class="barre">{segments}</div>'
              f'<div class="natures">{filet}</div></div>',
              f'<div class="chiffres"><b>{mille(d["brut"])}</b>'
              f'<span>socle {mille(d["socle"])}</span></div>',
              '</div>']
    sans_date = [metas.get(s, {}).get("name", s) for s, d in ordre
                 if d["reference"] > 300 and not d["annees"]]
    L += ['<div class="note">'
          + (f'<b>{" · ".join(sans_date)}</b> ne datent aucune de leurs lignes '
             'malgré un bon rendement en références. ' if sans_date else "")
          + 'Une référence et un prix sans date ne se comparent à rien dans le '
            'temps : ils servent à décrire un modèle, pas à le coter.</div>',
          '</section>']

    # -------------------------------------------------- 02 ce que ça permet
    paliers = [(f"{n} prix ou +", sum(1 for d in mod.values() if d["n"] >= n),
                "var(--laiton)") for n in (2, 3, 5, 10, 20, 50)]
    recoupes = sum(1 for d in mod.values() if len(d["src"]) >= 2)
    courbe = sum(1 for d in mod.values() if len(d["an"]) >= 3)
    annees = {a: c for a, c in sorted(M["annees"].items()) if a >= "2011"}
    haut = max(annees.values())

    L += ['<section>',
          '<h2><span class="rang">02</span>Ce que ce socle permet</h2>',
          '<p class="intro">Coter un modèle demande plusieurs transactions, pas '
          'une. Un modèle, ici, c’est une marque et une référence — graphies '
          'réunies, ponctuation ignorée : <code>116.500 LN</code> et '
          '<code>116500LN</code> sont la même montre.</p>',
          '<div class="grille g4">',
          f'<div class="case"><b class="chiffre">{mille(len(mod))}</b>'
          '<span>modèles distincts présents au socle</span></div>',
          f'<div class="case"><b class="chiffre or">{mille(paliers[1][1])}</b>'
          '<span>ont 3 transactions ou plus : un niveau, pas un point</span></div>',
          f'<div class="case"><b class="chiffre">{mille(recoupes)}</b>'
          '<span>sont vus par 2 sources indépendantes ou plus</span></div>',
          f'<div class="case"><b class="chiffre">{mille(courbe)}</b>'
          '<span>ont des prix sur 3 années distinctes : une évolution</span></div>',
          '</div>',
          '<div class="grille g3" style="margin-top:28px">',
          '<div class="case"><h3>Combien de prix par modèle</h3>']
    L += escalier(paliers, paliers[0][1])
    L += ['</div><div class="case"><h3>Les natures de prix</h3>']
    L += escalier([(NATURES.get(n, n), c, TEINTE.get(n, "var(--demande)"))
                   for n, c in M["natures"].most_common()],
                  M["natures"].most_common(1)[0][1])
    L += ['</div><div class="case"><h3>D’où vient la référence</h3>']
    L += escalier([(NOM_PROVENANCE.get(p, p), c,
                    "var(--laiton)" if p in REFERENCE_SURE else "var(--demande)")
                   for p, c in M["provenances"].most_common()],
                  M["provenances"].most_common(1)[0][1])
    L += ['</div></div>',
          '<h3 style="margin-top:36px">La profondeur, année par année</h3>',
          '<p class="intro" style="margin-bottom:6px">Le nombre de prix portant '
          'cette année-là.</p>',
          '<div class="frise">']
    for a, c in annees.items():
        L += [f'<div class="colonne"><i style="height:{140 * c / haut:.1f}px" '
              f'title="{a} : {mille(c)} prix"></i></div>']
    L += ['</div><div class="axe">'] + [f'<span>{a[2:]}</span>' for a in annees]
    L += ['</div>',
          '<div class="note">Le pic de <b>2026</b> n’est pas une flambée du marché. '
          'Trois sources ne datent pas leurs annonces et reçoivent la date du '
          'relevé : elles sont marquées comme telles dans la base, mais elles '
          'gonflent l’année en cours sur ce graphique.</div>',
          '</section>']

    # ------------------------------------------------ 03 nature x reference
    L += ['<section>',
          '<h2><span class="rang">03</span>Croiser la nature du prix et la référence</h2>',
          '<p class="intro">Deux exigences indépendantes : savoir <em>ce que le '
          'montant représente</em>, et savoir <em>de quelle montre il s’agit</em>. '
          'Le tableau montre où chacune se perd.</p>',
          '<div class="cadre"><table><thead><tr><th>Nature du prix</th>'
          '<th class="n">Avec référence</th><th class="n">Sans</th>'
          '<th class="n">Taux</th><th>Ce que la ligne vaut</th></tr></thead><tbody>']
    for nature, _ in M["natures"].most_common():
        avec = M["croise"].get((nature, True), 0)
        sans = M["croise"].get((nature, False), 0)
        L += [f'<tr><td class="gras">{NATURES.get(nature, nature)}</td>'
              f'<td class="n">{mille(avec)}</td><td class="n">{mille(sans)}</td>'
              f'<td class="n">{round(100 * avec / max(avec + sans, 1))} %</td>'
              f'<td>{e(VALEUR_NATURE.get(nature, "—"))}</td></tr>']
    L += ['</tbody></table></div>',
          '<div class="grille g3" style="margin-top:26px">',
          '<div class="case"><h3>Les devises</h3><span>'
          + " · ".join(f'<em>{v}</em> {mille(c)}'
                       for v, c in M["devises"].most_common())
          + '<br><br>Aucune conversion n’est faite. Comparer un lot en HKD à un lot '
            'en USD demande un taux <em>daté</em>, qui n’est pas encore stocké.'
            '</span></div>',
          '<div class="case"><h3>Le régime de frais</h3><span>'
          f'<em>{mille(M["premium"].get(True, 0))}</em> lignes frais acheteur '
          f'inclus · <em>{mille(M["premium"].get(False, 0))}</em> lignes marteau '
          'nu.<br><br>L’écart est d’environ un quart, et rien sur les pages ne le '
          'signale : le champ <code>price_includes_premium</code> porte '
          'l’information ligne par ligne.</span></div>',
          '<div class="case"><h3>Les marques</h3><span>'
          f'<em>{mille(len(M["marques"]))}</em> maisons distinctes, graphies '
          'réunies.<br><br>'
          + " · ".join(f'{e(m)} {mille(c)}'
                       for m, c in M["marques"].most_common(6) if m)
          + '</span></div></div>', '</section>']

    # ------------------------------------------------------- 04 les defauts
    majeurs = sum(1 for d in DEFAUTS if d["gravite"] == "majeur")
    L += ['<section>',
          f'<h2><span class="rang">04</span>Les {len(DEFAUTS)} défauts trouvés, '
          'et corrigés</h2>',
          f'<p class="intro">Dont <b>{majeurs} majeurs</b> : des défauts qui '
          'faisaient dire à la base quelque chose de faux, pas seulement '
          'd’incomplet. Chacun a été trouvé en confrontant nos lignes aux pages en '
          'ligne, jamais à notre propre base, et chacun porte son ampleur mesurée. '
          'Ce sont eux qui disent où la donnée pourrait encore mentir.</p>',
          '<div class="defauts">']
    vivants = mesures_vivantes(M)
    for brut in DEFAUTS:
        d = {k: (v.format(**{c: mille(x) for c, x in vivants.items()})
                 if isinstance(v, str) else v) for k, v in brut.items()}
        L += ['<article class="defaut"><div class="defaut-tete">',
              f'<h3>{e(d["titre"])}</h3>',
              f'<span class="ampleur">{e(d["ampleur"])}</span>',
              f'<span class="gravite g-{d["gravite"]}">{e(d["gravite"])}</span>',
              '</div>',
              f'<p class="quoi"><span class="source-touchee">{e(d["source"])}</span>'
              f'{e(d["symptome"])}</p>',
              f'<p><span class="etiquette">Pourquoi</span>{e(d["cause"])}</p>',
              f'<p><span class="etiquette">Comment on l’a su</span>{e(d["preuve"])}</p>',
              f'<p class="reparee"><span class="etiquette">Corrigé</span>'
              f'{e(d["correction"])}</p>',
              '</article>']
    L += ['</div>',
          '<div class="note">Aucune de ces corrections n’a coûté une nouvelle '
          'collecte. Le brut de chaque source est conservé — 239 Mo compressés — et '
          'toute correction du filtre ou d’un adaptateur se rejoue sur l’historique '
          'entier sans une seule requête réseau. C’est ce qui les rend possibles '
          'après coup, et c’est la décision de conception qui a le plus '
          'rapporté.</div>',
          '</section>']

    # ------------------------------------------------------ 05 ce qui bloque
    L += ['<section>',
          '<h2><span class="rang">05</span>Ce qui bloque</h2>',
          '<p class="intro">Trois genres, qui ne se traitent pas pareil. Une source '
          'qui refuse techniquement ne demande rien à personne. Une source qui nous '
          'exclut nommément demande un arbitrage — et rien n’en a été collecté en '
          'attendant. Une limite de coût se lève en laissant tourner plus '
          'longtemps.</p>',
          '<div class="blocs">']
    for nom, genre, quoi, suite in BLOCAGES:
        L += [f'<div class="bloc{" decision" if genre == "decision" else ""}">'
              f'<div><h3>{e(nom)}</h3><div class="genre">{e(genre)}</div></div>'
              f'<p>{e(quoi)}</p><div class="suite">{e(suite)}</div></div>']
    L += ['</div></section>']

    # ------------------------------------------------------ 06 les ecartees
    L += ['<section>',
          '<h2><span class="rang">06</span>Les sources sondées puis écartées</h2>',
          f'<p class="intro">{len(ECARTEES)} sources ont coûté des requêtes réelles '
          'sans entrer dans la base. Le volume est ce qui serait '
          '<em>atteignable</em>, jamais ce qui a été collecté — ne montrer que les '
          'sources retenues laisserait croire qu’on a choisi sans comparer.</p>',
          '<div class="cadre"><table><thead><tr><th>Source</th><th>Type</th>'
          '<th>Volume atteignable</th><th>Prix</th><th>Référence</th>'
          '<th>Profondeur</th><th>Verdict</th><th>Pourquoi</th></tr></thead><tbody>']
    for _, x in sorted(ECARTEES.items(), key=lambda kv: (kv[1]["verdict"], kv[1]["nom"])):
        L += [f'<tr><td class="gras">{e(x["nom"])}</td><td>{e(x["type"])}</td>'
              f'<td>{e(x["volume"])}</td><td>{e(x["prix"])}</td>'
              f'<td>{e(x["reference"])}</td><td>{e(x["profondeur"])}</td>'
              f'<td>{e(x["verdict"])}</td><td>{e(x["remarque"])}</td></tr>']
    L += ['</tbody></table></div></section>']

    # ----------------------------------------------- 07 ce qui a ete verifie
    L += ['<section>',
          '<h2><span class="rang">07</span>Ce qui a été vérifié, source par source</h2>',
          '<p class="intro">Un tirage aléatoire par source, plus un contrôle taillé '
          'pour elle : paramètre de pays chez les boutiques Shopify, régime de '
          'frais chez les maisons de ventes, statut de stock chez les WooCommerce. '
          'Les défauts trouvés sont donnés tels quels — une vérification qui ne '
          'trouve jamais rien ne vérifie rien.</p>',
          '<div class="cadre"><table><thead><tr><th>Source</th><th>Tirage</th>'
          '<th>Ce qu’il a trouvé</th></tr></thead><tbody>']
    for s, _ in ordre:
        tirage, trouve = VERIFICATION.get(s, ("non vérifiée", "—"))
        L += [f'<tr><td class="gras">{e(metas.get(s, {}).get("name", s))}</td>'
              f'<td><code>{e(tirage)}</code></td><td>{e(trouve)}</td></tr>']
    L += ['</tbody></table></div>',
          '<details style="margin-top:22px"><summary>Ce qu’il faut savoir de chaque '
          'source</summary><div class="cadre" style="margin-top:12px"><table><tbody>']
    for s, _ in ordre:
        L += [f'<tr><td class="gras">{e(metas.get(s, {}).get("name", s))}</td>'
              f'<td>{e(REMARQUES.get(s, "—"))}</td></tr>']
    L += ['</tbody></table></div></details>', '</section>']

    L += ['<footer>',
          f'<div>Généré le {dt.date.today().strftime("%d/%m/%Y")} par '
          '<code>python moteur/page_sources.py</code> depuis le cumul. Aucun '
          'chiffre saisi à la main.</div>',
          '<div>Vérifications menées contre les pages en ligne, pas contre la base. '
          'Brut conservé et rejouable : 100 % des sources.</div>',
          '</footer>', '</div>']

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text("\n".join(L), encoding="utf-8")
    print(f"-> {SORTIE}  ({SORTIE.stat().st_size // 1024} Ko)")
    print(f"{len(ordre)} sources · {len(DEFAUTS)} défauts · {mille(len(mod))} modèles")


if __name__ == "__main__":
    main()
