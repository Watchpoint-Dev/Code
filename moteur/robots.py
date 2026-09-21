"""Ce que chaque source autorise A CLAUDEBOT, et non a un navigateur.

    cd ~/Desktop/WP/labo
    shared/.venv/bin/python moteur/robots.py

Depuis le 02/09/2026 nous nous annoncons pour ce que nous sommes. La
contrepartie est entiere : les regles qui visent ClaudeBot nous visent. Un site
qui nous exclut nommement nous exclut, et ce module le dit source par source,
en lisant le robots.txt et en appliquant l'ordre de precedence du protocole :

    le groupe le PLUS SPECIFIQUE qui nous nomme l'emporte sur `*`
    a l'interieur d'un groupe, la regle la PLUS LONGUE l'emporte
    a longueur egale, `Allow` l'emporte sur `Disallow`

Aucune collecte n'est lancee ici : ce module constate, il ne ramene rien.
"""
from __future__ import annotations

import pathlib
import re
import sys
import urllib.parse

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "shared"))

import sources  # noqa: E402
from utils import get  # noqa: E402

# Les noms sous lesquels un site peut nous designer, du plus precis au plus
# large. Le premier groupe present dans le fichier fait foi.
NOS_NOMS = ("claudebot", "claude-user", "claude-searchbot", "anthropic-ai")


def groupes(texte: str) -> dict[str, list[tuple[str, str]]]:
    """{agent: [(directive, chemin)]}, agents en minuscules.

    Un groupe peut porter plusieurs `User-agent` consecutifs : ils partagent
    alors les memes regles. DavidSW enumere ainsi douze robots d'IA d'un coup.
    """
    trouves: dict[str, list[tuple[str, str]]] = {}
    agents_courants: list[str] = []
    attend_regles = False
    for ligne in texte.splitlines():
        ligne = ligne.split("#")[0].strip()
        if not ligne or ":" not in ligne:
            continue
        cle, _, valeur = ligne.partition(":")
        cle, valeur = cle.strip().lower(), valeur.strip()
        if cle == "user-agent":
            if attend_regles:
                agents_courants = []
                attend_regles = False
            agents_courants.append(valeur.lower())
            trouves.setdefault(valeur.lower(), [])
        elif cle in ("allow", "disallow") and agents_courants:
            attend_regles = True
            for agent in agents_courants:
                trouves[agent].append((cle, valeur))
    return trouves


def verdict(texte, chemin: str) -> tuple[bool, str]:
    """Ce chemin nous est-il ouvert ? Rend (autorise, la regle qui a tranche).

    FERME PAR DEFAUT quand le fichier n'a pas pu etre lu. C'est le piege que ce
    module s'est tendu a lui-meme le 02/09/2026 : un robots.txt non recupere
    rendait un texte vide, donc aucun groupe, donc « autorise » — et DavidSW
    est ressortie ouverte alors qu'elle interdit `/wp-json/` a ClaudeBot en
    toutes lettres. Un silence n'est pas un consentement.
    """
    if texte is None:
        return False, "robots.txt ILLISIBLE — on s'abstient"
    tous = groupes(texte)
    agent = next((n for n in NOS_NOMS if n in tous), "*" if "*" in tous else None)
    if agent is None:
        if not texte.strip():
            return False, "robots.txt VIDE ou non recupere — on s'abstient"
        return True, "aucun groupe applicable"
    regles = tous[agent]
    if not regles:
        return True, f"groupe `{agent}` sans aucune restriction"

    meilleure = None
    for directive, motif in regles:
        if not motif:
            # `Disallow:` vide veut dire « rien n'est interdit ».
            continue
        # Le motif accepte `*` et `$`, comme le protocole le prevoit.
        expression = re.escape(motif).replace(r"\*", ".*")
        if expression.endswith(r"\$"):
            expression = expression[:-2] + "$"
        if re.match(expression, chemin):
            poids = (len(motif), directive == "allow")
            if meilleure is None or poids > meilleure[0]:
                meilleure = (poids, directive, motif)
    if meilleure is None:
        return True, f"groupe `{agent}` : aucune regle ne vise ce chemin"
    _, directive, motif = meilleure
    return directive == "allow", f"`{agent}` · {directive.title()}: {motif}"


def main() -> None:
    demandees = [a for a in sys.argv[1:] if not a.startswith("-")]
    interdites = []
    for module in sources.ALL:
        s = module.SOURCE
        if demandees and s["id"] not in demandees:
            continue
        # Le chemin reellement appele, tel que l'adaptateur le declare.
        acces = str(s.get("access", ""))
        chemin = "/"
        for candidat in ("/wp-json/", "/products.json", "/_next/data/",
                         "/auction", "/api/"):
            if candidat.strip("/").split("/")[0] in acces.replace(".", " ").lower() \
                    or candidat in acces:
                chemin = candidat
                break
        domaine = None
        for attribut in ("BASE", "DOMAINE"):
            if hasattr(module, attribut):
                domaine = str(getattr(module, attribut))
                break
        if not domaine:
            reglages = getattr(module, "NORMALISATION", {}) or {}
            if reglages.get("domaine"):
                domaine = "https://" + reglages["domaine"]
        if not domaine:
            # Les adaptateurs WooCommerce passent leur base en argument de
            # `collect` : on la lit dans le source plutot que d'en tenir une
            # seconde copie ici, qui finirait par diverger.
            texte_source = pathlib.Path(module.__file__).read_text(encoding="utf-8")
            trouve = re.search(r'base="(https?://[^"]+)"', texte_source) \
                or re.search(r'domaine="([^"]+)"', texte_source) \
                or re.search(r'BASE\s*=\s*"(https?://[^"]+)"', texte_source)
            if trouve:
                domaine = trouve.group(1)
                if not domaine.startswith("http"):
                    domaine = "https://" + domaine
        if not domaine:
            print(f"{s['id']:<24}domaine inconnu — a verifier a la main")
            continue
        racine = urllib.parse.urlsplit(domaine)
        racine = f"{racine.scheme or 'https'}://{racine.netloc or racine.path}"

        # Un 404 sur robots.txt veut dire « rien n'est interdit » ; une panne
        # de lecture ne veut rien dire du tout, et ne s'interprete pas en notre
        # faveur. Les deux sont distingues.
        texte = None
        try:
            resp = get(f"{racine}/robots.txt", pause=0.4)
            if resp.status_code == 200:
                texte = resp.text
            elif resp.status_code == 404:
                texte = "# aucun robots.txt publie"
        except Exception:
            texte = None

        ouvert, regle = verdict(texte, chemin)
        marque = "OK  " if ouvert else "NON "
        print(f"{marque}{s['id']:<24}{chemin:<16}{regle}")
        if not ouvert:
            interdites.append(s["id"])

    if interdites:
        print(f"\nINTERDITES a ClaudeBot : {', '.join(interdites)}")
        print("Ces sources ne doivent plus etre collectees tant que la regle tient.")
    else:
        print("\nAucune source active ne nous exclut.")


if __name__ == "__main__":
    main()
