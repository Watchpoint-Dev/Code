# Installer un poste de développement

Ce guide part d'un clone vide et va jusqu'à une collecte qui tourne et un site
qui s'affiche en local. Compter une quinzaine de minutes.

## Prérequis

| Outil | Version | Pour quoi |
|---|---|---|
| Python | 3.12 ou plus (3.13 en usage) | le backend |
| Node.js | 20 | le frontend |
| npm | celui livré avec Node | le frontend (pas de pnpm ni de bun : le lockfile est npm) |
| git | 2.40 ou plus | |

Sur macOS, `brew install python@3.13 node@20` suffit.

## 1. Cloner

```bash
git clone git@github.com:Watchpoint-Dev/Code.git watchpoint
cd watchpoint
git switch dev
```

On travaille sur `dev`. `main` est la production.

## 2. Le backend

```bash
python3 -m venv backend/.venv
backend/.venv/bin/pip install -e "backend[dev]"
```

`-e` installe le package en mode éditable : une modification dans
`backend/src/watchpoint/` est prise en compte sans réinstaller. L'extra `dev`
ajoute pytest et ruff ; `db` ajoutera le pilote Postgres quand le chargeur
existera.

Vérifier :

```bash
backend/.venv/bin/python -m watchpoint aide     # la liste des commandes
backend/.venv/bin/pytest backend                # 11 tests, moins d'une seconde
```

Raccourci : `make install` fait les étapes 2 et 3 d'un coup.

## 3. Les données

La base de prix n'est pas dans git sous sa forme brute (plus de 200 Mo). Elle y
est compressée. Pour la reconstruire :

```bash
scripts/restaure.sh
backend/.venv/bin/python -m watchpoint verifie  # doit finir par « Tout est vert. »
```

Le brut des collectes (`data/raw/`, environ 500 Mo) n'est pas versionné du tout.
Sans lui, tout fonctionne sauf `rejoue` et `filtre --marquer`, qui relisent le
brut. Il se récupère depuis la sauvegarde disque du projet ; il ne se recollecte
pas à l'identique, les sites ayant changé depuis.

## 4. Le frontend

```bash
cd frontend
npm ci
cp .env.example .env.local      # puis remplir les valeurs, voir ci-dessous
npm run dev                     # http://localhost:3000
```

Les valeurs de `.env.local` :

| Variable | Où la trouver |
|---|---|
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY` | tableau de bord Clerk, *API Keys* |
| `NEXT_PUBLIC_CLERK_SIGN_IN_URL`, `NEXT_PUBLIC_CLERK_SIGN_UP_URL` | `/sign-in` et `/sign-up` |
| `DATABASE_URL` | Neon, **branche `dev`**, chaîne de connexion *pooled* |

Ne jamais mettre l'URL de la branche de production dans un `.env` local.

Sans `DATABASE_URL`, le site démarre quand même : seule la synchronisation des
comptes répond 503.

## 5. Vérifier que tout est en ordre

```bash
make test        # backend : pytest
make check       # frontend : typecheck, lint, build
```

Ce sont exactement les deux vérifications que la CI lance sur chaque push.

## Problèmes fréquents

**`ModuleNotFoundError: No module named 'watchpoint'`**
Le package n'est pas installé dans le venv utilisé. Relancer
`backend/.venv/bin/pip install -e "backend[dev]"` et appeler Python par
`backend/.venv/bin/python`, pas par le `python3` du système.

**`une collecte tourne deja (pid …)`**
Le verrou `data/.collecte-en-cours` existe. Si aucune collecte ne tourne
(`ps aux | grep "watchpoint collecte"`), c'est un verrou orphelin laissé par un
arrêt brutal : le supprimer, ou relancer avec `--force`.

**`verifie` signale des doublons ou des colonnes manquantes après un `restaure`**
L'instantané `.gz` est peut-être plus ancien que le code. Récupérer la dernière
version (`git pull`) puis `scripts/restaure.sh --ecrase`.

**Le site affiche une page blanche après connexion**
Les clés Clerk de `.env.local` ne correspondent pas à l'application Clerk du
projet, ou `NEXT_PUBLIC_CLERK_SIGN_IN_URL` est vide.
