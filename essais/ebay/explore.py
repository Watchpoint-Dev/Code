"""eBay — Browse API (annonces ACTIVES = prix demande).

Prerequis : copier .env.example vers .env et y coller les cles du keyset
(https://developer.ebay.com/my/keys). Aucune cle n'est ecrite en dur ici.

Usage:
    source ../../shared/.venv/bin/activate
    python explore.py auth                      # 1. la connexion marche-t-elle ?
    python explore.py search "rolex submariner" # 2. a quoi ressemble la data
    python explore.py pilot "rolex" 200         # 3. volume + completude des champs

Rappel : le Sandbox est une fausse boutique quasi vide. `auth` doit y passer,
mais `search` y renverra 0 resultat — c'est normal, pas un bug. Le pilote n'a
de sens qu'en production (EBAY_ENV=production), une fois le keyset active.

Ce que cette API donne : prix DEMANDE (annonces en cours).
Les prix VENDUS passent par Marketplace Insights API, sur approbation eBay.
"""
from __future__ import annotations

import base64
import json
import os
import pathlib
import sys
import time

import requests

# rend `shared/` importable quelle que soit la profondeur
sys.path.append(str(next(p for p in pathlib.Path(__file__).resolve().parents
                         if (p / "shared" / "utils.py").exists()) / "shared"))
from utils import samples_dir, save_json  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
TOKEN_CACHE = HERE / ".token.json"

# Champs qu'on veut vraiment pour le modele de donnees. Un prix sans reference
# exploitable ne sert a rien : c'est ce que le pilote mesure.
ASPECTS_CLES = [
    "Brand",
    "Model",
    "Reference Number",
    "Year Manufactured",
    "Movement",
    "Case Material",
    "Case Size",
    "Dial Color",
]


# --------------------------------------------------------------------------
# config
# --------------------------------------------------------------------------

def load_env() -> None:
    """Charge le .env pose a cote du script (pas de dependance externe)."""
    env_file = HERE / ".env"
    if not env_file.exists():
        sys.exit("Pas de fichier .env ici.\n"
                 "  -> cp .env.example .env  puis colle tes cles dedans.")
    for raw in env_file.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

    for required in ("EBAY_APP_ID", "EBAY_CERT_ID"):
        if not os.environ.get(required):
            sys.exit(f"{required} est vide dans .env — va le chercher sur "
                     "https://developer.ebay.com/my/keys")


def env_name() -> str:
    return os.environ.get("EBAY_ENV", "sandbox").strip().lower()


def base_url() -> str:
    return ("https://api.ebay.com" if env_name() == "production"
            else "https://api.sandbox.ebay.com")


def marketplace() -> str:
    return os.environ.get("EBAY_MARKETPLACE", "EBAY_US")


# --------------------------------------------------------------------------
# authentification (OAuth2 client_credentials — pas de login utilisateur)
# --------------------------------------------------------------------------

def get_token(*, force: bool = False) -> str:
    """Token applicatif, valable ~2h, mis en cache sur disque.

    Le cache evite de redemander un token a chaque appel : l'endpoint d'auth
    a lui aussi un quota. Marge de securite de 5 min avant expiration.
    """
    if not force and TOKEN_CACHE.exists():
        cached = json.loads(TOKEN_CACHE.read_text())
        if cached.get("env") == env_name() and cached.get("expires_at", 0) > time.time() + 300:
            return cached["access_token"]

    creds = base64.b64encode(
        f"{os.environ['EBAY_APP_ID']}:{os.environ['EBAY_CERT_ID']}".encode()
    ).decode()

    resp = requests.post(
        f"{base_url()}/identity/v1/oauth2/token",
        headers={"Authorization": f"Basic {creds}",
                 "Content-Type": "application/x-www-form-urlencoded"},
        # NB: le scope s'ecrit bien avec api.ebay.com MEME en sandbox.
        # C'est un identifiant de permission, pas une adresse a appeler.
        data={"grant_type": "client_credentials",
              "scope": "https://api.ebay.com/oauth/api_scope"},
        timeout=30,
    )
    if resp.status_code != 200:
        _expliquer_erreur(resp)

    payload = resp.json()
    TOKEN_CACHE.write_text(json.dumps({
        "env": env_name(),
        "access_token": payload["access_token"],
        "expires_at": time.time() + payload.get("expires_in", 7200),
    }))
    return payload["access_token"]


def _expliquer_erreur(resp: requests.Response) -> None:
    """Traduit les erreurs eBay les plus frequentes en message utile."""
    corps = resp.text[:400]
    if resp.status_code == 401:
        sys.exit(f"401 refuse.\n  App ID ou Cert ID faux, ou cles Sandbox "
                 f"utilisees avec EBAY_ENV=production (ou l'inverse).\n  {corps}")
    if resp.status_code == 403:
        sys.exit(f"403 interdit.\n  Le keyset est probablement encore DISABLED "
                 f"cote eBay (conformite 'marketplace account deletion' a faire "
                 f"sur developer.ebay.com/my/keys).\n  {corps}")
    if resp.status_code == 429:
        sys.exit(f"429 quota depasse pour aujourd'hui. Attendre le reset.\n  {corps}")
    sys.exit(f"HTTP {resp.status_code}\n  {corps}")


def api_get(path: str, token: str, params: dict | None = None) -> dict:
    """GET authentifie sur l'API. Le header marketplace est obligatoire."""
    resp = requests.get(
        f"{base_url()}{path}",
        headers={"Authorization": f"Bearer {token}",
                 "X-EBAY-C-MARKETPLACE-ID": marketplace()},
        params=params,
        timeout=30,
    )
    if resp.status_code != 200:
        _expliquer_erreur(resp)
    return resp.json()


# --------------------------------------------------------------------------
# modes
# --------------------------------------------------------------------------

def mode_auth() -> None:
    print(f"environnement : {env_name()}  ({base_url()})")
    print(f"marche        : {marketplace()}")
    token = get_token(force=True)
    print(f"\nOK — token obtenu : {token[:24]}...")
    print("La connexion fonctionne. (Token mis en cache dans .token.json)")


def mode_search(query: str, limit: int = 10) -> None:
    token = get_token()
    print(f"[{env_name()}] recherche : {query!r}")
    data = api_get("/buy/browse/v1/item_summary/search", token,
                   {"q": query, "limit": limit})

    total = data.get("total", 0)
    resultats = data.get("itemSummaries", []) or []
    print(f"  total annonce par eBay : {total:,}")
    print(f"  recu dans cette page   : {len(resultats)}\n")

    if not resultats and env_name() == "sandbox":
        print("  0 resultat : NORMAL en sandbox (fausse boutique quasi vide).")
        print("  L'auth est validee, c'etait le but. Passe en production pour")
        print("  juger la vraie data.")
        return

    for item in resultats[:10]:
        prix = item.get("price", {})
        print(f"  {prix.get('value', '?'):>10} {prix.get('currency', '')} · "
              f"{(item.get('title') or '')[:70]}")

    chemin = samples_dir(__file__) / f"search_{env_name()}.json"
    save_json(chemin, data)


def mode_pilot(query: str = "rolex", cible: int = 200, details: int = 25) -> None:
    """Tire un echantillon reel puis mesure la completude des champs.

    La question du pilote n'est pas "est-ce que ca repond" mais "les champs
    utiles (marque, reference, annee, mouvement) sont-ils remplis ?".
    """
    token = get_token()
    print(f"[{env_name()}] pilote : {query!r}, cible {cible} annonces\n")

    # --- 1. volume : pagination des resumes
    resumes: list[dict] = []
    offset, page_size = 0, min(200, cible)
    while len(resumes) < cible:
        data = api_get("/buy/browse/v1/item_summary/search", token,
                       {"q": query, "limit": page_size, "offset": offset})
        lot = data.get("itemSummaries", []) or []
        if not lot:
            break
        resumes.extend(lot)
        offset += len(lot)
        print(f"  ... {len(resumes)} annonces")
        time.sleep(0.3)  # on reste poli, et le quota journalier est limite

    if not resumes:
        print("  0 annonce recuperee.")
        if env_name() == "sandbox":
            print("  Normal en sandbox. Repasse ce pilote en production.")
        return

    save_json(samples_dir(__file__) / "pilot_summaries.json", resumes)

    # --- 2. qualite : le detail complet, seul endroit ou vivent les aspects
    print(f"\n  detail complet sur {min(details, len(resumes))} annonces...")
    fiches: list[dict] = []
    for item in resumes[:details]:
        item_id = item.get("itemId")
        if not item_id:
            continue
        fiches.append(api_get(f"/buy/browse/v1/item/{item_id}", token))
        time.sleep(0.3)

    save_json(samples_dir(__file__) / "pilot_items.json", fiches)

    # --- 3. le chiffre qui decide si la source vaut quelque chose
    print(f"\n  COMPLETUDE des champs cles (sur {len(fiches)} fiches) :")
    for aspect in ASPECTS_CLES:
        presents = sum(
            1 for f in fiches
            if any(a.get("name") == aspect and a.get("value")
                   for a in (f.get("localizedAspects") or []))
        )
        pct = 100 * presents / len(fiches) if fiches else 0
        print(f"    {aspect:<20} {pct:5.1f}%  {'#' * int(pct / 5)}")

    devises = {f.get("price", {}).get("currency") for f in fiches}
    print(f"\n  devises rencontrees : {', '.join(sorted(filter(None, devises)))}")
    print("  -> reporte ces chiffres dans notes.md")


# --------------------------------------------------------------------------

def main() -> None:
    load_env()
    args = sys.argv[1:]
    mode = args[0] if args else "auth"

    if mode == "auth":
        mode_auth()
    elif mode == "search":
        mode_search(args[1] if len(args) > 1 else "rolex submariner")
    elif mode == "pilot":
        mode_pilot(args[1] if len(args) > 1 else "rolex",
                   int(args[2]) if len(args) > 2 else 200)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
