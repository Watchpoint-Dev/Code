"""Sonde une liste de sites et les note — re-executable, pour detecter les regressions.

    cd ~/Desktop/WP/labo
    shared/.venv/bin/python moteur/sonde.py                  # toutes les sources connues
    shared/.venv/bin/python moteur/sonde.py --historique      # rejoue les 200 du dernier passage
    shared/.venv/bin/python moteur/sonde.py christies bezel   # seulement celles-ci
    shared/.venv/bin/python moteur/sonde.py --url https://exemple.com  # un site au hasard

Pourquoi : `catalogue.py` fige des verdicts a la main. Trois sources sont mortes en
trois semaines sans que rien ne le signale. Cette sonde REMESURE ce qui est
mesurable, et compare au dernier passage : une source qui passe de vert a rouge
apparait comme REGRESSION.

Ce qu'elle mesure vraiment (rien d'autre — elle ne devine pas) :

  FAISABILITE            VALEUR
  · robots.txt           · signal de prix (montants + devises dans la page)
  · joignable (HTTP)     · signal de date (dates reperees)
  · anti-bot             · indice de volume (sitemap, pagination)
  · rendu serveur ou JS
  · donnees structurees

Elle est POLIE : robots.txt lu en premier, site saute s'il l'interdit, pause entre
requetes, 3 requetes par site au maximum. Elle ne contourne aucune protection.

CE QU'ELLE NE FAIT PAS — a lire avant de se fier au score :

  Elle ne regarde que la PAGE D'ACCUEIL et deux endpoints standard. Elle ne sait
  pas ou vivent les vraies donnees. Christie's est note bas parce que sa page
  d'accueil ne porte aucun prix — alors que son API interne est la meilleure
  source du projet. L'inverse existe aussi : une vitrine pleine de prix dont le
  catalogue est inatteignable.

  Donc : la note de FAISABILITE est fiable (robots, HTTP, anti-bot, endpoints
  sont mesures directement). La note de VALEUR n'est qu'un indice tire de la page
  d'accueil. Un score bas veut dire "a regarder de plus pres", jamais "sans
  interet". Seul un pilote sur les vraies pages tranche.

  Son vrai usage est le TRIAGE et la SURVEILLANCE : degrossir 200 sites en une
  passe, et surtout detecter qu'une source acquise vient de se fermer.
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import re
import sys
import time
import urllib.parse

import requests

ICI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
sys.path.insert(0, str(ICI.parent / "shared"))

from utils import HEADERS  # noqa: E402

HISTORIQUE = ICI.parent / "data" / "sonde.json"
PAUSE = 1.5
DELAI = 25
PARALLELE = 8   # domaines sondes en meme temps (jamais deux requetes sur le meme)

# L'UA de la sonde, et pourquoi il differe du HEADERS partage.
#
# Le HEADERS du projet annonce "Mozilla/5.0 (compatible; ClaudeBot/1.0; ...)" :
# il pretend etre un navigateur ET se nomme robot. Mesure du 21/09/2026 sur les
# 69 sources classees "robots illisible", meme URL, meme minute :
#
#     ClaudeBot     -> 403 sur 19 d'entre elles
#     python-requests par defaut -> 200 sur ces 19
#
# Parmi les 19 : Wanna Buy A Watch et Watches of Distinction, dont on a
# respectivement 6 441 et 507 prix en base. La sonde declarait fermees des
# sources qui collectent. Meme cause que le ReadTimeout de Christie's du 25/08 :
# beaucoup de WAF blocklistent maintenant ClaudeBot, et un UA qui se reclame de
# Mozilla sans en avoir l'empreinte TLS est le pire des deux mondes.
#
# On ne ment donc sur rien : l'UA par defaut de la bibliotheque dit exactement
# ce que nous sommes, un script Python. C'est ce qui passe.
#
# Le HEADERS partage n'est PAS touche : les 30 adaptateurs collectent avec lui
# et une modification globale se mesure avant de se decider.
UA_SONDE = requests.utils.default_user_agent()
UA_SECOURS = "curl/8.4.0"
HEADERS_SONDE = {"User-Agent": UA_SONDE,
                 "Accept-Language": HEADERS.get("Accept-Language", "en-US,en;q=0.9")}

# Signatures d'anti-bot. On les DETECTE pour classer la source, jamais pour passer outre.
ANTIB0T_DUR = {
    "Cloudflare": ("cf-browser-verification", "cf_chl_", "challenge-platform",
                   "__cf_bm", "Just a moment", "cdn-cgi/challenge"),
    "Incapsula/Imperva": ("_Incapsula_Resource", "incap_ses", "visid_incap"),
    "Akamai": ("ak_bmsc", "_abck", "bm_sz"),
    "AWS WAF": ("awswaf", "aws-waf-token", "challenge.js"),
    "PerimeterX": ("_px", "px-captcha", "perimeterx"),
    "DataDome": ("datadome", "dd_cookie"),
}

# Mecanismes de donnees structurees, du plus exploitable au moins.
STRUCTURE = [
    ("Shopify products.json", "/products.json?limit=1"),
    ("WooCommerce Store API", "/wp-json/wc/store/products?per_page=1"),
]
MARQUEURS_HTML = {
    "JSON-LD": r'type="application/ld\+json"',
    "__NEXT_DATA__": r'id="__NEXT_DATA__"',
    "window.__data": r"window\.__data\s*=",
    "Apollo state": r"__APOLLO_STATE__",
}

MONNAIE = re.compile(
    r"(?:USD|EUR|GBP|CHF|HKD|JPY|\$|€|£|CHF\.?|Fr\.)\s?\d[\d\s.,']{2,}", re.I)
DATE = re.compile(r"\b(?:19|20)\d{2}-\d{2}-\d{2}\b|\b(?:19|20)\d{2}\b")


def _get(url: str, ua: str = UA_SONDE, **kw):
    try:
        r = requests.get(url, headers={**HEADERS_SONDE, "User-Agent": ua},
                         timeout=DELAI, allow_redirects=True, **kw)
        time.sleep(PAUSE)
        return r
    except requests.RequestException as e:
        time.sleep(PAUSE)
        return type("Echec", (), {"status_code": 0, "text": "", "url": url,
                                  "headers": {}, "erreur": type(e).__name__})()


# --------------------------------------------------------------------- robots

def controle_robots(base: str) -> dict:
    """Lit robots.txt AVANT tout le reste. C'est la premiere regle de la maison.

    Un robots illisible fait s'abstenir — et l'abstention empeche la page d'etre
    regardee du tout, donc la source sort a 0/100 sans avoir ete testee. Un
    echec de lecture coute donc tres cher, et il ne doit jamais venir de nous :
    on reessaie avec un second UA avant de conclure.
    """
    url = urllib.parse.urljoin(base, "/robots.txt")
    r = _get(url)
    if r.status_code not in (200, 404):
        # Peut venir de NOTRE identite plutot que du site. Mesure du 21/09 :
        # 19 sources sur 69 repondaient 403 a ClaudeBot et 200 a un UA honnete.
        r2 = _get(url, ua=UA_SECOURS)
        if r2.status_code in (200, 404):
            r = r2

    if r.status_code == 404:
        # 404 franc = le site n'a pas de robots.txt = rien n'est interdit
        return {"robots": "absent (404)", "robots_ok": True, "crawl_delay": None,
                "params_interdits": ""}
    if r.status_code != 200:
        # Timeout, 403, 5xx : on ne SAIT PAS ce que le site autorise. Le defaut
        # prudent est de s'abstenir. Un robots injoignable n'est pas un feu vert.
        cause = getattr(r, "erreur", "") or f"HTTP {r.status_code}"
        return {"robots": f"illisible ({cause}) — abstention",
                "robots_ok": False, "crawl_delay": None, "params_interdits": ""}

    texte = r.text
    if len(texte) < 3000 and any(s in texte for sig in ANTIB0T_DUR.values() for s in sig):
        return {"robots": "illisible (anti-bot sur le robots.txt)", "robots_ok": False,
                "crawl_delay": None, "params_interdits": ""}

    # bloc User-agent: *
    bloc, dans = [], False
    for ligne in texte.splitlines():
        l = ligne.strip()
        if l.lower().startswith("user-agent:"):
            dans = l.split(":", 1)[1].strip() == "*"
        elif dans and l and not l.startswith("#"):
            bloc.append(l)

    interdits = [l.split(":", 1)[1].strip() for l in bloc
                 if l.lower().startswith("disallow:")]
    delai = next((l.split(":", 1)[1].strip() for l in bloc
                  if l.lower().startswith("crawl-delay:")), None)
    tout_interdit = any(i == "/" or i == "*" for i in interdits)
    params = [i for i in interdits if "=" in i or "?" in i]

    return {
        "robots": "INTERDIT TOUT" if tout_interdit else f"{len(interdits)} regles",
        "robots_ok": not tout_interdit,
        "crawl_delay": delai,
        "params_interdits": " · ".join(params[:6]),
    }


# ------------------------------------------------------------------ page type

def controle_page(base: str) -> dict:
    r = _get(base)
    corps = r.text or ""
    res = {
        "http": r.status_code,
        "octets": len(corps),
        "erreur_reseau": getattr(r, "erreur", ""),
    }

    # Une signature d'anti-bot dit quel VENDEUR protege le site. Elle ne dit
    # PAS que nous sommes bloques : presque tout gros site sert ses pages
    # derriere Cloudflare ou Akamai, et leurs cookies (__cf_bm, _abck) sont
    # alors presents dans une reponse parfaitement normale.
    #
    # Mesure du 21/09/2026 : Christie's rend 200 avec 133 ko et Bonhams 200 avec
    # 295 ko, et l'ancienne version les classait toutes deux BLOQUE parce que
    # _abck / __cf_bm apparaissaient dans le corps. Christie's est la meilleure
    # source du projet, 12 507 prix en base.
    #
    # On separe donc deux choses qui n'ont rien a voir :
    #   antibot  le vendeur detecte — une note, jamais un verdict
    #   bloque   la reponse est INUTILISABLE, ce qui se mesure et ne se devine pas
    res["antibot"] = " · ".join(
        nom for nom, signatures in ANTIB0T_DUR.items()
        if any(s.lower() in corps.lower() for s in signatures))

    # Trois cas, et trois seulement, ou l'on est reellement devant un mur.
    if r.status_code in (401, 403, 429) or r.status_code >= 500:
        res["bloque"] = f"HTTP {r.status_code}"
    elif r.status_code == 200 and 0 < len(corps) < 2000:
        # un 200 avec un corps minuscule est une page de challenge deguisee
        res["bloque"] = (f"challenge {res['antibot']}" if res["antibot"]
                         else "page suspecte (200 mais < 2 ko)")
    elif r.status_code == 0:
        res["bloque"] = res["erreur_reseau"] or "injoignable"
    else:
        res["bloque"] = ""
    # reCAPTCHA seul n'est PAS un blocage : c'est souvent un formulaire de contact.
    # On le note sans le compter comme mur — sinon on classe fermees des sources
    # dont l'endpoint repond parfaitement (cas rencontre sur Hodinkee).
    res["signal_faible"] = "reCAPTCHA" if any(
        s in corps.lower() for s in ("g-recaptcha", "recaptcha/api.js")) else ""

    res["mecanismes"] = " · ".join(
        nom for nom, motif in MARQUEURS_HTML.items() if re.search(motif, corps))

    prix = MONNAIE.findall(corps)
    res["signal_prix"] = len(set(prix))
    annees = [int(a) for a in re.findall(r"\b(19\d{2}|20[0-3]\d)\b", corps)]
    res["signal_date"] = len(set(annees))
    res["annee_min"] = min(annees) if annees else None
    return res


def controle_endpoints(base: str, robots_ok: bool) -> dict:
    """Teste les endpoints standard — c'est ce qui rend une source triviale."""
    if not robots_ok:
        return {"endpoint": "", "sitemap": "", "volume_indice": ""}
    for nom, chemin in STRUCTURE:
        r = _get(urllib.parse.urljoin(base, chemin))
        if r.status_code == 200 and r.text.strip().startswith(("{", "[")):
            try:
                d = json.loads(r.text)
                # Shopify renvoie {"products": [...]}, WooCommerce une liste nue
                lot = d.get("products", d) if isinstance(d, dict) else d
                n = len(lot) if isinstance(lot, (list, dict)) else 0
                return {"endpoint": nom, "sitemap": "",
                        "volume_indice": f"{n} sur la 1re page"}
            except json.JSONDecodeError:
                pass
    r = _get(urllib.parse.urljoin(base, "/sitemap.xml"))
    if r.status_code == 200 and "<loc>" in r.text:
        return {"endpoint": "", "sitemap": f"{r.text.count('<loc>')} URLs",
                "volume_indice": f"{r.text.count('<loc>')} URLs au sitemap"}
    return {"endpoint": "", "sitemap": "", "volume_indice": ""}


# ------------------------------------------------------------------- notation

def note(m: dict) -> dict:
    """Deux notes sur 100, et leur produit. Chaque point est justifie par une mesure."""
    f = 0
    if m["robots_ok"]:
        f += 30
    if m["http"] == 200:
        f += 25
    if not m.get("bloque"):
        # note le MUR, pas la presence d'un CDN : un site derriere Cloudflare
        # qui nous sert 300 ko de HTML ne nous a rien refuse.
        f += 25
    if m["endpoint"]:
        f += 20
    elif m["mecanismes"]:
        f += 12
    elif m["sitemap"]:
        f += 6

    v = 0
    v += min(40, m["signal_prix"] * 2)       # des prix dans la page
    v += min(30, m["signal_date"] * 3)       # des dates
    if m["volume_indice"]:
        v += 30
    elif m["mecanismes"]:
        v += 15

    return {"faisabilite": f, "valeur": min(100, v), "score": round(f * min(100, v) / 100)}


def etat(v: str) -> str:
    """Reduit un verdict a ce qui compte pour la surveillance : ouvert ou ferme.

    Comparer des scores fait crier au loup a chaque point de variation. Ce qui
    merite une alerte, c'est qu'une source passe d'accessible a murée.
    """
    if v.startswith(("INTERDIT", "BLOQUE", "injoignable", "HTTP")):
        return "ferme"
    return "ouvert"


def verdict(m: dict) -> str:
    if not m["robots_ok"]:
        # Deux situations tres differentes, a ne jamais confondre dans un document
        # qui sort du projet : le site nous interdit explicitement, ou bien on n'a
        # pas pu lire ses regles. Dans les deux cas on s'abstient, mais on ne
        # raconte pas la meme chose.
        return ("INTERDIT par robots" if "INTERDIT" in m.get("robots", "")
                else "robots illisible — abstention")
    if m["http"] == 0:
        return "injoignable"
    if m["endpoint"]:
        # un endpoint qui rend du JSON prouve l'acces, quoi que dise la page d'accueil
        return f"FACILE ({m['endpoint']})"
    # On ne regarde le mur qu'APRES avoir constate que la reponse est inutilisable.
    # L'ordre inverse condamnait toute source servie derriere un CDN.
    if m.get("bloque"):
        return f"BLOQUE ({m['bloque']})"
    if m["http"] != 200:
        return f"HTTP {m['http']}"
    if m["signal_prix"] == 0:
        return "rendu JS ou pas de prix en clair"
    if m["mecanismes"]:
        return "exploitable (donnees structurees)"
    if m["sitemap"]:
        return "a creuser (sitemap seul, pas d'endpoint)"
    return "exploitable (HTML)"


# ---------------------------------------------------------------------- cibles

def cibles_registre() -> list[tuple[str, str]]:
    """Les 210 sources recensees, lues dans le registre partage.

    Le chemin n'est plus fixe : le classeur porte un nom date et descend en
    archive a chaque campagne, ce qui cassait cette commande. `--historique`
    reste preferable pour une re-mesure, puisqu'il rejoue exactement le
    perimetre du passage precedent.
    """
    import pandas as pd
    from utils import registre_sources
    trouve = registre_sources()
    if trouve is None:
        sys.exit("aucun registre de sources trouve — utilise --historique pour "
                 "rejouer le perimetre du dernier passage")
    registre, onglet = trouve
    print(f"registre : {registre.name} (onglet « {onglet} »)")
    d = pd.read_excel(registre, sheet_name=onglet)
    vus, liste = set(), []
    for _, r in d.iterrows():
        url = str(r.get("URL") or "").strip()
        if not url.startswith("http"):
            continue
        dom = urllib.parse.urlparse(url).netloc
        if dom and dom not in vus:
            vus.add(dom)
            liste.append((str(r["Source"]).strip(), f"https://{dom}/"))
    return liste


def cibles_historique() -> list[tuple[str, str]]:
    """Exactement les sources du dernier passage, relues dans data/sonde.json.

    Le registre Excel descend en archive a chaque campagne ; l'historique de la
    sonde, lui, reste. C'est donc lui qui definit le perimetre re-mesurable —
    et c'est ce qui permet de comparer deux passages terme a terme.
    """
    if not HISTORIQUE.exists():
        sys.exit(f"aucun historique a rejouer : {HISTORIQUE}")
    vus, liste = set(), []
    for m in json.loads(HISTORIQUE.read_text())["mesures"]:
        d = urllib.parse.urlparse(m["url"]).netloc
        if d and d not in vus:
            vus.add(d)
            liste.append((m["source"], m["url"]))
    return liste


def cibles_connues() -> list[tuple[str, str]]:
    """Les sites qu'on connait, tires du code et du catalogue."""
    import catalogue
    import sources as paquet

    vus, liste = set(), []

    def ajoute(nom, url):
        d = urllib.parse.urlparse(url).netloc
        if d and d not in vus:
            vus.add(d)
            liste.append((nom, f"https://{d}/"))

    for m in paquet.ALL:
        base = (getattr(m, "BASE", None) or getattr(m, "SITEMAP", None)
                or getattr(m, "CALENDAR", None) or getattr(m, "LOTSEARCH", None) or "")
        ajoute(m.SOURCE["name"], base)

    connus = {
        "EveryWatch": "https://everywatch.com", "Loupe This": "https://loupethis.com",
        "Monaco Legend": "https://monacolegendauctions.com",
        "Hodinkee Shop": "https://shop.hodinkee.com",
        "Watchtrader": "https://watchtrader.co.uk",
        "Wanna Buy A Watch": "https://wannabuyawatch.com",
        "Menta Watches": "https://mentawatches.com",
        "Amsterdam Vintage Watches": "https://amsterdamvintagewatches.com",
        "Patek Philippe": "https://www.patek.com", "Grand Seiko": "https://www.grand-seiko.com",
        "WatchCharts": "https://watchcharts.com", "Chrono24": "https://www.chrono24.com",
        "Barnebys": "https://www.barnebys.com", "Phillips": "https://www.phillips.com",
        "Sotheby's": "https://www.sothebys.com", "the-saleroom": "https://www.the-saleroom.com",
        "Invaluable": "https://www.invaluable.com", "Bonhams": "https://www.bonhams.com",
        "Antiquorum": "https://www.antiquorum.swiss", "Artcurial": "https://www.artcurial.com",
        "Dorotheum": "https://www.dorotheum.com", "Heritage": "https://www.ha.com",
        "Watchfinder": "https://www.watchfinder.co.uk", "Bob's Watches": "https://www.bobswatches.com",
        "Chronext": "https://www.chronext.com", "1stDibs": "https://www.1stdibs.com",
    }
    for nom, url in connus.items():
        ajoute(nom, url)
    return liste


# ------------------------------------------------------------------------ run

def sonde_un(nom: str, url: str) -> dict:
    m = {"source": nom, "url": url}
    m.update(controle_robots(url))
    if m["robots_ok"]:
        m.update(controle_page(url))
        m.update(controle_endpoints(url, m["robots_ok"]))
    else:
        m.update({"http": 0, "octets": 0, "antibot": "", "bloque": "",
                  "signal_faible": "", "mecanismes": "",
                  "signal_prix": 0, "signal_date": 0, "annee_min": None,
                  "erreur_reseau": "", "endpoint": "", "sitemap": "",
                  "volume_indice": ""})
    m.update(note(m))
    m["verdict"] = verdict(m)
    return m


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--url" in sys.argv:
        u = sys.argv[sys.argv.index("--url") + 1]
        cibles = [(urllib.parse.urlparse(u).netloc, u)]
    elif "--registre" in sys.argv:
        cibles = cibles_registre()
    elif "--historique" in sys.argv:
        cibles = cibles_historique()
    else:
        cibles = cibles_connues()
        if args:
            filtre = {a.lower() for a in args}
            cibles = [(n, u) for n, u in cibles
                      if any(f in n.lower() or f in u.lower() for f in filtre)]
    if not cibles:
        sys.exit("aucune cible — noms connus : " +
                 ", ".join(n for n, _ in cibles_connues()))

    ancien = {}
    if HISTORIQUE.exists():
        ancien = {d["source"]: d for d in json.loads(HISTORIQUE.read_text())["mesures"]}

    print(f"Sonde de {len(cibles)} site(s) — robots.txt d'abord, {PAUSE}s entre requetes\n")
    mesures, regressions, progressions = [], [], []

    # Les domaines sont sondes en parallele, mais CHAQUE site garde ses pauses :
    # la politesse se mesure par hote, pas globalement. Un seul site ne recoit
    # jamais deux requetes simultanees.
    resultats = {}
    if len(cibles) > 12:
        from concurrent.futures import ThreadPoolExecutor, as_completed
        with ThreadPoolExecutor(max_workers=PARALLELE) as pool:
            futurs = {pool.submit(sonde_un, n, u): (n, u) for n, u in cibles}
            faits = 0
            for f in as_completed(futurs):
                nom, _ = futurs[f]
                faits += 1
                try:
                    resultats[nom] = f.result()
                except Exception as e:
                    resultats[nom] = None
                if faits % 25 == 0:
                    print(f"    ... {faits}/{len(cibles)} sondes")
        ordonne = [(n, resultats.get(n)) for n, _ in cibles]
    else:
        ordonne = [(n, sonde_un(n, u)) for n, u in cibles]

    # Seconde passe SEQUENTIELLE sur les injoignables. Un timeout pendant une passe
    # parallele peut etre de notre fait ; s'il persiste seul, c'est le site qui filtre.
    # On ne retente PAS un site interdit par robots : son http vaut 0 par choix,
    # pas par accident. Le relabelliser en "hors ligne" masquerait l'interdiction.
    a_reprendre = [(n, m) for n, m in ordonne
                   if m and m.get("http") == 0 and m.get("robots_ok")]
    if a_reprendre:
        print(f"\n    seconde passe sur {len(a_reprendre)} site(s) injoignable(s)...")
        for nom, ancien in a_reprendre:
            url = ancien["url"]
            neuf = sonde_un(ancien["source"], url)
            if neuf["http"] != 0:
                ordonne[[n for n, _ in ordonne].index(nom)] = (nom, neuf)
            else:
                ancien["verdict"] = "filtre ou hors ligne (2 tentatives)"
        print()

    for i, (nom_src, m) in enumerate(ordonne, 1):
        if m is None:
            continue
        nom = m["source"]
        mesures.append(m)
        avant = ancien.get(nom)
        fleche = ""
        if avant:
            hier, aujourdhui = etat(avant["verdict"]), etat(m["verdict"])
            if hier == "ouvert" and aujourdhui == "ferme":
                regressions.append((nom, avant["verdict"], m["verdict"]))
                fleche = "  <== S'EST FERME"
            elif hier == "ferme" and aujourdhui == "ouvert":
                progressions.append((nom, avant["verdict"], m["verdict"]))
                fleche = "  <== s'est ouvert"
        print(f"{i:>3}. {nom:<26} {m['score']:>3}/100  {m['verdict']}{fleche}")

    HISTORIQUE.write_text(json.dumps(
        {"date": dt.datetime.now().isoformat(timespec="seconds"), "mesures": mesures},
        ensure_ascii=False, indent=1), encoding="utf-8")

    print("\n" + "=" * 74)
    for m in sorted(mesures, key=lambda x: -x["score"])[:5]:
        print(f"  meilleur  {m['source']:<26} {m['score']:>3}  {m['verdict']}")
    fermes = [m for m in mesures if m["score"] < 40]
    print(f"\n  {len(mesures) - len(fermes)} exploitables · {len(fermes)} fermes")

    if regressions:
        print("\n" + "!" * 74)
        for nom, avant, apres in regressions:
            print(f"S'EST FERME  {nom} : {avant} -> {apres}")
        print("!" * 74)
    for nom, avant, apres in progressions:
        print(f"OUVERTURE   {nom} : {avant} -> {apres}")

    if len(mesures) > 12:
        import pandas as pd
        cadre = pd.DataFrame(mesures)[[
            "source", "url", "verdict", "score", "faisabilite", "valeur",
            "robots", "crawl_delay", "params_interdits", "http", "octets",
            "bloque", "antibot", "signal_faible", "mecanismes", "endpoint", "sitemap",
            "volume_indice", "signal_prix", "signal_date", "annee_min",
            "erreur_reseau"]].sort_values("score", ascending=False)
        sortie = (ICI.parent.parent / "output" / "referentiels" /
                  f"diagnostic_{dt.date.today().isoformat()}.xlsx")
        with pd.ExcelWriter(sortie, engine="openpyxl") as w:
            cadre.to_excel(w, sheet_name="Diagnostic", index=False)
            ws = w.sheets["Diagnostic"]
            ws.freeze_panes = "A2"
            for i, c in enumerate(cadre.columns, 1):
                lg = cadre[c].astype(str).str.len().max()
                ws.column_dimensions[ws.cell(1, i).column_letter].width = min(
                    max(len(c), 0 if pd.isna(lg) else int(lg)) + 2, 46)
        print(f"\nExcel : output/referentiels/{sortie.name}")

    print(f"\nmesures enregistrees dans data/{HISTORIQUE.name} "
          f"(relance la sonde pour comparer)")
    if regressions:
        sys.exit(1)


if __name__ == "__main__":
    main()
