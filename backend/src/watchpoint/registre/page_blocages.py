"""Ce qui BLOQUE, et de quel genre est le blocage.

Trois genres, qui ne se traitent pas pareil : une source qui refuse
techniquement, une source qui nous exclut ou dont les conditions interdisent la
collecte, et une limite que la source ou le cout nous impose. Seul le deuxieme
genre demande une decision humaine — et rien n'en a ete collecte en attendant.

Vit a part pour que le generateur de page et les rapports lisent la meme liste.
"""
BLOCAGES = [
    ("EveryWatch", "technique",
     "573 015 annonces, la plus grosse source du dossier. Elle repond a un appel "
     "isole mais REFUSE une collecte : 32 requetes sur 42 rejetees le 28/08. "
     "L'adaptateur est ecrit et pret ; il faudrait un rythme de l'ordre d'une "
     "requete par minute, soit plusieurs semaines.",
     "Rien a decider — c'est une contrainte de la source."),
    ("LiveAuctioneers", "limite de la source",
     "Le blocage etait le notre : en nous annoncant honnetement, la source repond "
     "318 Ko la ou le faux UA Chrome recevait un challenge. Mais son archive ne "
     "pagine que par `/search/?`, que son robots.txt interdit. Le chemin autorise "
     "rend 13 lots prixes, sans page suivante.",
     "Accessible, mais non collectable a l'echelle."),
    ("DavidSW", "limite de cout",
     "Son robots.txt ouvre le catalogue a ClaudeBot mais ferme `/wp-json/`. Ses "
     "18 000 fiches produit nous sont donc ouvertes une par une — et le site "
     "bride dur : 6 refus 429 sur 8 pages a 2,5 s d'intervalle.",
     "Des jours de collecte pour 499 pieces en stock."),
    ("Watches of Distinction", "refus du serveur",
     "Son robots.txt ne nous interdit rien, mais son pare-feu rend 403 a tout UA "
     "de robot depuis notre passage a ClaudeBot. Les 496 montres deja collectees "
     "restent en base avec leur brut.",
     "Collecte gelee. Un 403 est un refus, on ne le contourne pas."),
    ("Watches of Knightsbridge", "decision",
     "Le meilleur rapport profondeur/cout mesure : 57 requetes pour douze ans "
     "d'encheres en MARTEAU NU, invendus publies a 34 %. Mais son robots.txt "
     "porte 'User-agent: ClaudeBot / Disallow: /' — une exclusion nominale.",
     "DECISION REQUISE. Rien n'a ete collecte et rien ne le sera sans arbitrage."),
    ("Grailzee", "decision",
     "Techniquement la meilleure source sondee : 54 603 encheres, reference "
     "normalisee a 99,86 %, invendus publies, une centaine de requetes. Mais "
     "les prix ne sont servis que par un endpoint interne a cle embarquee.",
     "DECISION REQUISE. Rien n'a ete collecte."),
    ("Bezel", "decision",
     "32 670 annonces. Le robots.txt autorise l'API, mais les conditions "
     "d'utilisation interdisent le scraping mot pour mot — les deux se "
     "contredisent.",
     "DECISION REQUISE. L'adaptateur est ecrit et bride par un drapeau."),
    ("Christie's, Artcurial, Lyon & Turnbull", "limite de la source",
     "Leurs API ne servent que les lots VENDUS : les invendus n'existent pas "
     "dans les donnees, alors qu'ils disent ou le marche s'arrete. Seules Lyon & "
     "Turnbull et Loupe This en publient.",
     "Biais de survie assume, et documente ligne par ligne."),
    ("Watches of Switzerland", "limite de cout",
     "33 106 fiches, mais une requete par fiche : neuf heures pour le tout. "
     "La collecte est bornee a 2 500, et le journal le dit.",
     "Levable en laissant tourner une nuit."),
]
