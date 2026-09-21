"""Toutes les sources ESSAYEES, y compris celles qu'on a ecartees.

Un tableau qui ne montre que ce qui a marche ment par omission : il laisse
croire qu'on a choisi douze sources sur douze, alors qu'on en a sonde trente-cinq.
Ce fichier garde donc la trace de chacune — celles qui collectent, celles qui
ont ete mesurees puis ecartees, et celles qui attendent une decision.

Les chiffres des sources ACTIVES ne sont pas ici : ils se lisent dans le cumul,
qui fait foi. Ici ne vivent que les sources dont on n'a PAS de donnees, avec ce
qui a ete mesure lors de la reconnaissance et la raison de la mise a l'ecart.

Chaque entree porte :
    volume      ce qui serait atteignable, mesure et non estime
    prix        la nature de prix qu'elle publie
    reference   la couverture mesuree, et ou elle vit
    profondeur  la date la plus ancienne prouvee
    remarque    ce qu'il faut savoir, en une phrase
"""

# --------------------------------------------------------------------------
# ECARTEES APRES MESURE. Chaque ligne a coute des requetes reelles : ce sont
# des mesures, pas des impressions.
# --------------------------------------------------------------------------
ECARTEES = {
    "cottone": dict(
        nom="Cottone Auctions", type="maison de ventes", volume="~210 lots horlogers",
        prix="realise, frais inclus (publie : « Hammer Price w/ BP »)",
        reference="11 %", profondeur="2009 -> 2026",
        verdict="branchee",
        remarque="RE-EXAMINEE le 21/09/2026, le verdict « ecartee » etait fonde "
                 "sur le mauvais rayon. Les 3 323 lots mesures = 67 pages x 50, "
                 "c'est-a-dire exactement la categorie `clocks-timepieces` : des "
                 "regulateurs et des horloges de parquet, d'ou les 40 gardes. "
                 "Mais Cottone classe PAR MATIERE et non par fonction — ses "
                 "montres-bracelets sont rangees sous `Jewelry`, avec les bagues. "
                 "La mesure etait juste, la conclusion ne l'etait pas. "
                 "Sa date de vente est servie dans un COMMENTAIRE HTML avant le "
                 "montant : 50 lots dates par requete, sans requete de plus, "
                 "462/462 dates et recoupes au jour pres sur 4 lots de 2009 a "
                 "2022. Volume modeste mais qualite rare. "
                 "Piege : passer `categorie_source` a Cottone fait rejeter 100 % "
                 "de ses montres par R0 (`Jewelry`), mesure 27 GARDER -> 0. "
                 "L'adaptateur ne le passe donc pas."),
    "lempertz": dict(
        nom="Kunsthaus Lempertz", type="maison de ventes", volume="271 lots horlogers",
        prix="realise, frais inclus", reference="non mesuree", profondeur="2002",
        verdict="ecartee",
        remarque="86 805 URL enumerees par ses sitemaps pour 271 lots horlogers "
                 "seulement, et aucun prix marteau disponible. Mauvais rapport."),
    "menta": dict(
        nom="Menta Watches", type="marchand", volume="2 902 fiches",
        prix="demande", reference="60 % (titre)", profondeur="import 2023",
        verdict="ecartee",
        remarque="L'archive est fermee a l'API : 1 produit rendu sur 300 demandes. "
                 "8,8 % des fiches conservent un prix, et 73 % datent du meme "
                 "import de lancement."),
    "certifiedwatchstore": dict(
        nom="Certified Watch Store", type="marchand", volume="1 127 montres",
        prix="neuf remise", reference="98 % (SKU prefixe)", profondeur="aucune",
        verdict="ecartee",
        remarque="1 076 fiches creees le meme jour par un import d'avril 2026 : "
                 "aucun signal temporel. Entree de gamme, marche secondaire absent."),
    "thewatchclub": dict(
        nom="The Watch Club", type="marchand", volume="59 montres",
        prix="demande (AUD)", reference="~0 %", profondeur="aucune",
        verdict="ecartee",
        remarque="Le champ marque vaut 'The Watch Club' sur toutes les fiches, et "
                 "le catalogue contient plus de livres que de montres."),
    "morphy": dict(
        nom="Morphy Auctions", type="maison de ventes", volume="~12 ventes horlogeres",
        prix="realise, frais a taux variable", reference="0 %", profondeur="2016",
        verdict="ecartee",
        remarque="Zero reference sur 132 titres examines, et des frais acheteur "
                 "variables selon le canal d'enchere : le marteau n'est pas "
                 "reconstructible. La page de resultats est en Disallow."),
    "abell": dict(
        nom="Abell Auction", type="maison de ventes", volume="~250 lots horlogers",
        prix="realise, marteau nu", reference="quasi nulle", profondeur="12/2024",
        verdict="a creuser",
        remarque="Le JSON-LD laisse fuiter le prix realise malgre le 'Login for "
                 "Price' affiche. Mais l'archive s'arrete a la migration de fin "
                 "2024 : vingt mois, et 1,2 % de lots horlogers."),
    "johnmoran": dict(
        nom="John Moran Auctioneers", type="maison de ventes",
        volume="1 catalogue passe accessible", prix="realise, frais inclus (+27 %)",
        reference="non mesurable", profondeur="non atteignable",
        verdict="ecartee",
        remarque="Resondee le 29/08/2026 : le site est une marque blanche "
                 "d'Invaluable, avec `realizedPriceIndicator:false` et un "
                 "catalogue servi par Algolia, 20 lots par page au-dela desquels "
                 "il faut une cle. Sa boutique WordPress ne vend que des sacs et "
                 "des livres d'art. La profondeur de 1993 n'est pas atteignable "
                 "par le site lui-meme."),
    "neworleans": dict(
        nom="New Orleans Auction", type="maison de ventes", volume="~178 000 lots",
        prix="realise, frais inclus (+25 %)", reference="65 % texte libre",
        profondeur="26/07/1992", verdict="a creuser",
        remarque="La plus profonde de toutes — trente-quatre ans. Resondee le "
                 "02/09/2026 : l'archive est bien la, en marque blanche "
                 "d'Invaluable, et les prix REALISES sont servis dans le HTML — "
                 "16 lots prixes sur les 20 d'une page. Mais la pagination ne "
                 "repond pas : ?page=2 rend toujours la page 0. Au-dela de "
                 "20 lots par catalogue il faut appeler Algolia avec la cle "
                 "embarquee du site. Meme cas que Grailzee : decision requise."),
    "watchesofknightsbridge": dict(
        nom="Watches of Knightsbridge", type="maison de ventes", volume="~12 000 lots",
        prix="realise, MARTEAU NU", reference="31 a 40 % (titre tronque)",
        profondeur="12/07/2014", verdict="decision requise",
        remarque="Le meilleur rapport profondeur/cout du dossier — 57 requetes pour "
                 "douze ans en marteau nu, invendus a 34 %. Mais son robots.txt "
                 "porte 'User-agent: ClaudeBot / Disallow: /' : exclusion explicite."),
    "grailzee": dict(
        nom="Grailzee", type="marketplace d'encheres", volume="54 603 encheres",
        prix="realise, marteau nu", reference="99,86 % champ structure",
        profondeur="19/08/2022", verdict="decision requise",
        remarque="Techniquement la meilleure source mesuree : reference normalisee "
                 "a 99,9 %, invendus publies, ~110 requetes. Mais les prix ne sont "
                 "accessibles que par un endpoint interne a cle embarquee."),
    "davidsw": dict(
        nom="DavidSW", type="marchand", volume="499 fiches servies par l'API",
        prix="demande", reference="~87,5 % (titre)", profondeur="2022",
        verdict="decision requise",
        remarque="Resondee le 02/09/2026 : l'API WooCommerce repond et sert 499 "
                 "fiches prixees, marque et modele en categories. MAIS son "
                 "robots.txt porte `Disallow: /wp-json/` pour `User-agent: *`, et "
                 "c'est sous cette regle que nous tombons puisque nous envoyons un "
                 "UA Chrome. Verifie le 02/09/2026 apres etre passes a ClaudeBot : "
                 "le groupe `claudebot` interdit LUI AUSSI `/wp-json/` — c'est la "
                 "plomberie qui est fermee, pas le catalogue. Ses fiches produit "
                 "nous sont ouvertes, mais elles sont 18 000 et le site bride dur : "
                 "6 refus 429 sur 8 pages a 2,5 s d'intervalle. Des jours de "
                 "collecte pour un marchand de 499 pieces en stock."),
    "watchfinder": dict(
        nom="Watchfinder", type="marchand", volume="~5 500 fiches",
        prix="demande", reference="URL et titre", profondeur="aucune",
        verdict="a creuser",
        remarque="L'API de stock est explicitement en Disallow, donc une requete par "
                 "fiche. Aucune date nulle part : c'est un instantane de stock."),
    "everywatch_reserve": dict(
        nom="EveryWatch (fenetre)", type="agregateur", volume="573 015 annonces",
        prix="realise, frais inclus", reference="63 % champ dedie",
        profondeur="24 mois glissants", verdict="branchee, avec reserve",
        remarque="Resondee le 02/09/2026 : le BLOCAGE EST LEVE — 2 refus sur 42 "
                 "contre 32 le 28/08. Mais la source est desormais videe : sur "
                 "50 lots servis en `auctionLotType: RESULT`, ZERO porte un prix "
                 "ou une date. Une requete entiere n'a rendu qu'un seul lot "
                 "exploitable, date de la veille. L'acces est ouvert, la donnee "
                 "ne l'est plus."),
    "bezel": dict(
        nom="Bezel", type="marketplace", volume="32 670 annonces",
        prix="demande", reference="champ dedie", profondeur="releve",
        verdict="decision requise",
        remarque="robots.txt autorise l'API mais les CGU interdisent verbatim le "
                 "scraping. Adaptateur ecrit, bride par un drapeau, en attente "
                 "d'arbitrage humain."),
    "liveauctioneers": dict(
        nom="LiveAuctioneers", type="agregateur", volume="non mesurable",
        prix="realise", reference="non mesuree", profondeur="—",
        verdict="a creuser",
        remarque="LE BLOCAGE ETAIT LE NOTRE. En nous annoncant honnetement "
                 "ClaudeBot le 02/09/2026, la source repond 318 Ko la ou notre faux "
                 "UA Chrome recevait 962 octets de challenge — l'anti-bot visait le "
                 "navigateur simule. Mais l'archive reste hors d'atteinte : "
                 "?status=archive rend 13 lots prixes sur 14, sans pagination, et "
                 "le seul chemin qui pagine est `/search/?`, explicitement interdit "
                 "par son robots.txt. Accessible n'est pas collectable."),
    "cortrie": dict(
        nom="Cortrie Auktionen", type="maison de ventes", volume="24 lots vedettes",
        prix="realise, FRAIS INCLUS ('inkl. Aufgeld')", reference="~100 % (titre)",
        profondeur="non atteignable", verdict="ecartee",
        remarque="Resondee le 29/08 puis le 02/09/2026, sans changement. La fiche "
                 "est la plus riche qu'on ait "
                 "vue — 'Referenz 6241, Seriennummer 17673..., Zuschlag: "
                 "272.360,00 € inkl. Aufgeld'. Mais l'archive n'est pas ouverte : "
                 "le parametre de pagination est IGNORE (les memes 24 lots "
                 "vedettes reviennent identiques a start=0, 24, 48, 72 et 4800) et les "
                 "ventes passees repondent 404. Seule la vente en cours est visible."),
}

# --------------------------------------------------------------------------
# PERDUE EN CHANGEANT D'IDENTITE. Le prix a payer de l'en-tete honnete, et il
# faut le dire aussi franchement que les gains.
# --------------------------------------------------------------------------
ECARTEES["watchesofdistinction_perdue"] = dict(
    nom="Watches of Distinction (collecte gelee)", type="marchand",
    volume="507 lignes deja collectees", prix="demande",
    reference="93 % (titre)", profondeur="aucune",
    verdict="gelee",
    remarque="Collectee le 02/09/2026 sous l'ancien en-tete, quand son robots.txt "
             "l'autorisait et qu'elle repondait. Depuis notre passage a ClaudeBot "
             "elle rend 403 sur toute requete : son robots.txt ne nous interdit "
             "rien, mais son pare-feu refuse les UA de robot. Un 403 est un refus, "
             "on ne le contourne pas. Les 496 montres deja en base restent, avec "
             "leur brut ; la source ne sera plus rappelee.")
