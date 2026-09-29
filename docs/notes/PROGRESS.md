# Avancement

Ce qui a réellement avancé, daté, le plus récent en haut. Plus libre que le
CHANGELOG : les blocages, les doutes et les prochaines étapes y ont leur place.

<!-- Format :
## AAAA-MM-JJ — titre
- Fait :
- Bloqué / ouvert :
- Ensuite :
-->

## 2026-09-22 → 2026-09-29 — Monorepo, documentation, collecte Antiquorum
- Fait :
  - **Restructuration en monorepo `Watchpoint-Dev/Code`.** `labo` et `wp-3-main`
    réunis, historiques conservés. Le moteur devient le package
    `backend/src/watchpoint` ; tous les chemins passent par `config.py`.
    Vérification : rejeu complet du brut avec l'ancien puis le nouveau code,
    empreinte identique sur les 35 sources rejouables. Voir `docs/ARCHITECTURE.md`.
  - **Décisions tranchées** (`docs/decisions/`) : Python pour le moteur, la base
    Postgres comme contrat backend/frontend, journal d'observations, pas d'ORM,
    branche Neon pour le dev, base versionnée compressée.
  - **Documentation** : guides d'installation, de collecte, d'ajout de source, du
    filtre et de déploiement ; dictionnaire des données ; glossaire ; CONTRIBUTING.
  - **Collecte** : Phillips 16 347 lots (22/09) ; Antiquorum 2010-2012 (+4 852),
    2020-2025 (+8 215), 2026 (+801), 2004-2009 (+9 907), 1993 (+83) ; Morphy
    2 476 ; nouveau relevé des 27 sources existantes (Montredo +11 706 par
    ré-observation). Base : 187 096 → 241 061 prix.
- Bloqué / ouvert :
  - **Les coupures réseau coûtent cher.** Une source n'est écrite qu'une fois
    terminée : une tranche Antiquorum de dix ans (plus d'une heure) interrompue
    à la fin est entièrement perdue. C'est arrivé trois fois. Parade : des
    tranches de deux ou trois ans. Correctif de fond à envisager : écrire une
    source vente par vente.
  - Grailzee n'a jamais pu finir (194 lots sur ~20 000 attendus), toujours
    interrompue par le réseau.
  - Le push GitHub et la bascule Vercel vers le nouveau dépôt restent à faire.
- Ensuite : finir Antiquorum 1989-2003 et Grailzee, puis l'étape 3 du plan :
  la migration `0002` (le journal d'observations).

## 2026-09-21 — Sonde réparée, vague 1 de collecte : 8 adaptateurs, potentiel ×2 sur la base
- Done:
  - **Sonde des 200 sources rejouée, et RÉPARÉE** — trois défauts trouvés et corrigés
    dans `moteur/sonde.py`. (1) Elle s'annonçait `Mozilla/5.0 (compatible; ClaudeBot)`,
    qui prétend être un navigateur ET se nomme robot : mesure sur les 69 sources
    classées « robots illisible », **19 répondent 200 à `python-requests` et 403 à
    ClaudeBot** — dont Wanna Buy A Watch (6 441 prix en base) et Watches of Distinction
    (507). La sonde déclarait fermées des sources qui collectent. (2) `verdict()`
    testait la signature anti-bot AVANT le code HTTP : Christie's (200, 132 ko) et
    Bonhams (200, 295 ko) étaient classées BLOQUÉ parce qu'un cookie `_abck` ou
    `__cf_bm` apparaissait dans le corps. `antibot` (le vendeur détecté) et `bloque`
    (la réponse est inutilisable) sont désormais deux champs distincts. (3) Un
    `robots.txt` illisible faisait s'abstenir SANS que la page soit jamais regardée —
    la source sortait à 0/100 sans avoir été testée ; elle réessaie maintenant avec
    un second UA avant de conclure. Drapeau `--historique` ajouté : `--registre`
    pointait vers `DataSources.xlsx`, descendu en archive, et la commande était cassée.
  - **Résultat de la sonde corrigée : 119 sources ouvertes, 27 réellement fermées,
    54 indéterminées.** Les 36 « BLOQUÉ par un vendeur anti-bot » étaient TOUS des
    faux positifs (Cloudflare 30 → 0, Akamai / AWS WAF / PerimeterX / Incapsula → 0).
    Passages archivés : `data/sonde_2026-08-11.json` et
    `data/sonde_2026-09-21_avant-correctif.json`.
  - **Vague 1 : 8 adaptateurs écrits** (un agent par source, ~41 requêtes chacun,
    aucun mur franchi), et **2 sources refusées après mesure**.
    - **Antiquorum** — la meilleure du dossier. ~89 000 lots vendus sur **38 ans
      (1989 → 2026)**, dont **~57 000 utiles aujourd'hui** et ~46 000 avec référence.
      L'URL de l'audit de juillet rend 404 : le catalogue a déménagé sur
      `catalog.antiquorum.swiss`. La profondeur commence en 1989, pas 1920.
      Coût d'une collecte complète : ~6 050 requêtes, ~8 h 30 au Crawl-delay 5.
    - **Phillips** (+ Hong Kong + New York, un seul adaptateur) — ~15 750 lots
      réalisés datés 2015 → 2026, **86 % de référence**. 106 requêtes pour tout le
      fonds. Mécanisme : payload React Router, pas le JSON-LD.
    - **Grailzee** — du prix RÉALISÉ avec référence en champ dédié, la nature qui
      manque le plus au projet. ~20 000 lots conclus, un peu moins de la moitié vendus.
    - **Morphy** — 2 000 à 5 000 lots datés, 84 % de référence en « Wrist Watches ».
      2 requêtes par vente entière.
    - **Cottone** — ~210 lots seulement, mais date de vente servie dans un
      commentaire HTML : 50 lots datés par requête. 2009 → 2026.
    - **Knightsbridge**, **Certified Watch Store** (98 % de référence), **Watches.com**.
    - Refusées : **Everest Horology** (0 montre sur 248, c'est un fabricant de
      bracelets) et **Roni Madhvani** (les 18 fiches sont le jeu de démonstration de
      WooCommerce, lorem ipsum compris).
  - **Six pièges du même genre, tous attrapés avant ingestion : un champ crédible
    qui n'est pas le bon prix.** Le JSON-LD de Phillips et le RDFa d'Antiquorum
    donnent l'ESTIMATION BASSE (Daytona 116520 : 15 000 CHF affichés contre 23 940
    réels, −37 % sans le moindre signal d'erreur) ; le prix Shopify de Grailzee est
    la COMMISSION d'acheteur (67 lots sur 120 à exactement 250,00, le plancher de
    l'app) — le brancher aurait écrit ~25 000 faux prix de montres.
  - **Frais acheteur mesurés et non devinés**, source par source : Phillips inclus
    (`soldPrice == hammerPricePlusBP` sur 449/449, barème 25 % → 26 % → 27 %),
    Antiquorum marteau nu (109 lots recoupés, taux 1,150 → 1,250 → 1,312 et
    DÉGRESSIF sur les gros lots), Cottone et Morphy inclus (la maison l'écrit),
    Grailzee marteau nu.
  - **Consolidation** : 8 modules enregistrés (`sources/__init__.py`, 38 adaptateurs
    dont 35 rejouables) et `rejoue.py` mis à jour.
  - **Filtre, cinq corrections, effet mesuré sur le brut** (onglet JOURNAL, 5 entrées) :
    - **R0 rendait `False` là où la source n'avait rien dit.** Ajouter le nom du
      modèle faisait basculer une catégorie de muette à négative : `Brands · Omega`
      → muette, `Brands · Omega · Seamaster` → « pas une montre ». **+589 lignes**
      (Watches of Switzerland +266, AWCO +94, Amsterdam Vintage +63, Global Watch
      Shop +46).
    - Deux pièges opposés sur la même règle : `Watch Buckle` valait montre (une
      boucle à 395 $ portant « Daytona 116500 » entrait en base avec cette
      référence) et `Jewelry` valait non-montre (Cottone classe ses
      montres-bracelets sous Jewelry). **La règle du nom-tête tranche** : « Watch
      Boxes » sont des boîtes, « Bracelet Watches » sont des montres.
    - Mon premier jet de ce correctif a fait entrer **166 enseignes de vitrine chez
      Analog:Shift et 59 objets promotionnels chez Bulang** (plateau de valet,
      porte-clés, couteau suisse Rolex) : les familles SOUVENIRS ont été ajoutées,
      191 lignes de déchet retirées. C'est la mesure sur le brut qui l'a montré.
    - **22 horlogers ajoutés au dictionnaire.** Deux sources indépendantes donnent
      le MÊME chiffre : montres-bracelets gardées à 90-92 %, montres de poche à
      **19 %** (Antiquorum 8/42, Morphy 498 rejets sur 646). Lacune du dictionnaire
      sur les horlogers d'avant 1900, pas un jugement sur les sources. Ajoutés :
      Vixa et Airain (Type 20, chronographes militaires cotés), Solvil, Paul
      Ditisheim, Tempor, Roskopf, Lépine, Ilbery, Bronnikov, Charles Frodsham,
      Léo Juvet, Benson, Romain Gauthier, Ludovic Ballouard, Urban Jürgensen…
      Les mots ambigus (Universal, Volta, Hamlet, Mugnier, Benson) exigent un jeton
      de catégorie ; les horlogers de poche sont en `scope=AUCTION`.
    - **`Universal` seul manquait** alors que `Universal Geneve` était présent, et
      c'est ainsi qu'Antiquorum l'écrit. Ligne séparée, jeton exigé.
    - **Bovet : `accept_pocket` FALSE → TRUE.** R3b rejetait sa production chinoise
      du XIXe, celle pour laquelle la maison est connue.
    - Banc de tests : 76/76 avant et après.
  - **Quatre défauts préexistants corrigés, mesurés sur la base :**
    - `_shopify.py` écrivait **`condition="preowned"` en dur** : 11 des 12 boutiques
      portaient donc « occasion » sur 100 % de leurs lignes, dont **Topper,
      détaillant de NEUF, sur ses 3 631 prix catalogue**. L'état est désormais
      déclaré par chaque boutique, et `None` quand elle ne le dit pas.
    - `_woo.py` acceptait l'attribut **`model` comme référence constructeur en
      `champ_dedie`** — la provenance la plus fiable du schéma, celle qui alimente
      le socle. Le garde-fou ne rejetait que les valeurs sans chiffre, or
      « Datejust 36 OysterQuartz » en contient un. Un test de FORME a été ajouté
      (deux chiffres, aucun mot en clair) : `126710BLNR` et `01 774 7686 4051`
      passent, « Scafograf 300M » non. Impact sur la base existante : latent,
      0 ligne au socle, car ces marchands sont tous en `asking`.
    - **Une note fausse dans `shared/utils.py`** affirmait que Watches of
      Knightsbridge porte `User-agent: ClaudeBot / Disallow: /` et que la source
      « resterait fermée ». Son `robots.txt` du jour fait 77 octets et ne contient
      aucune règle ClaudeBot : le 403 venait d'un filtre d'UA de son pare-feu.
      Cette note a écarté la source deux mois.
    - `ECARTEES["cottone"]` dans `catalogue_essais.py` : ses « 3 323 lots aspirés,
      40 gardés » = 67 pages × 50, c'est-à-dire exactement `clocks-timepieces`.
      La mesure était juste, le rayon était le mauvais — ses montres-bracelets sont
      sous `Jewelry`.
- Blocked / open:
  - **La collecte n'a pas encore tourné** : les 8 adaptateurs existent et sont
    enregistrés, mais aucun n'a collecté. C'est la vague 4, qui demande un
    **budget de requêtes partagé par domaine** — pièce à construire, et réclamée
    par `notes/CARNET.md` depuis que treize boutiques ont été perdues d'un coup.
  - **Le journal d'observations n'existe toujours pas.** `price_points.jsonl` porte
    136 051 annonces distinctes pour 136 377 lignes : **326 ré-observations en
    tout**. C'est un état, pas un journal. Les 49 805 prix demandés ne valent donc
    rien seuls, et « déduire les ventes par disparition » comme l'indice de
    sentiment restent impossibles. Chaque jour sans collecte est perdu pour de bon.
  - Les estimations d'avant-mesure se sont révélées fausses **toujours par le
    haut** : Phillips ×9, Knightsbridge ×20-40, Cottone ×160. Ne plus annoncer un
    volume qu'un agent n'a pas mesuré.
  - Wright, Rago/Toomey et Beaussant Lefèvre répondent 403 à un UA honnête et 200
    à Chrome : accessibles seulement en se faisant passer pour un navigateur.
    **Arbitrage humain**, non tranché.
  - Bezel : drapeau `ARBITRAGE_CGU` toujours en attente. LiveAuctioneers est passée
    en « robots illisible » et ne rendait déjà presque rien.
  - Décisions ouvertes depuis juillet, toujours ouvertes : langage du moteur
    (recommandation : Python), contrat de données du front, base de dev.
- Next:
  - Vague 2 : ouvrir les 54 sources indéterminées (« rendu JS » et « robots
    illisible »), que personne n'a jamais regardées.
  - Vague 3 : re-tester les 27 fermées en appliquant la leçon de l'UA honnête.
  - Vague 4 : le budget de requêtes partagé, puis la collecte profonde. Commencer
    par **Antiquorum 2010-2019** : cette seule tranche pèse la moitié du volume
    utile et 71 % des lignes référencées.
  - Pousser `labo` sur GitHub. Le dépôt n'a **aucun remote** : tout le moteur
    n'existe qu'en un exemplaire sur ce disque.

## 2026-09-07 — API eBay : diagnostic complet, jamais consigné
- Done: quatre diagnostics successifs (`ebay/ebay_diagnostic{,2,3,4}.py`, rapports
  dans `ebay/diagnostic_output/`). Accès mesuré : **Browse API 200** (annonces
  actives), Taxonomy 200 (46 attributs, `Reference Number` présent), Developer
  Analytics 200 — mais **Marketplace Insights 403** (les prix VENDUS) et **Feed
  API 403** (le téléchargement en masse). Quota ~5 000 appels/jour. **Plafond de
  10 000 résultats par requête**, mesuré au lot près (10 062 OK, 10 093 refusé).
  Balayage TUDOR : 102 % de couverture en 70 appels, d'où un **balayage luxe
  complet projeté à 1 894 appels**, soit 38 % du quota quotidien. Stock GB 2,5 M
  montres, US 2,9 M, DE 747 k. Rotation 43 k/24 h, 309 k/7 j.
- Blocked / open: **la valeur est dans Marketplace Insights, et c'est une démarche
  administrative, pas du code** (conformité « suppression de compte » d'abord).
  Browse seule donne du prix DEMANDÉ, la nature dont le projet a déjà trop.
- Next: candidater à Marketplace Insights. Ces résultats n'avaient été consignés
  nulle part — d'où cette entrée, écrite le 21/09.

## 2026-08-11 → 2026-09-02 — Campagne de collecte : 42 154 → 136 377 prix
- Done: 30 adaptateurs portés à 28 sources qui collectent. Rapports générés le
  02/09 et qui font foi : `notes/ETAT_DATA.md`, `notes/ENTONNOIR.md`,
  `notes/VUES.md`, `notes/TOUTES_LES_SOURCES.md`, `notes/ETAT_CHAMPS.md`.
  État à l'issue : **136 377 lignes, 112 377 gardées par le filtre, 2007 → 2026,
  47 778 lignes au socle** (référence + date + transaction réelle). Levier Shopify
  et WooCommerce génériques (`_shopify.py`, `_woo.py`) : une boutique de plus ne
  demande qu'une dizaine de lignes. Christie's débloquée en cessant de mentir sur
  son identité. Sonde des 200 domaines du registre.
- Blocked / open: cette période n'avait pas été journalisée — entrée reconstituée
  le 21/09 depuis les rapports générés et l'historique git, et volontairement
  limitée à ce qu'ils attestent.

## 2026-07-21 — Track B : audits profonds + registre maître des sources
- Done:
  - **Méga-audit multi-agents de 50 sources** (90 agents) → tiers 1-4 + verdicts,
    corrige les 1ers jets trop optimistes (EveryWatch RISKY, eBay gated, Phillips
    JS, Crown&Caliber/Watchmaster morts). Christie's = meilleure (API JSON, 1998→).
    → `notes/research/faisability/mega_audit_50.md` (+ _raw.json).
  - **Audit durabilité** (17 agents) : historique daté = seulement maisons de
    ventes ; marchands/marketplaces = historique à construire par snapshots.
    → `audit_durabilite.md`.
  - **Fiches deep-detail** des meilleures (variables, historique, difficulté)
    → `dossier_final.md` + `dossier_final_variables.md`.
  - **Pilotes d'échelle réels** (data dans `DataSourcingTemplate/testdata/`) :
    Christie's 84, Antiquorum 145, Amsterdam VW 300, Bezel/EuropeanWatch/Bob's OK,
    Phillips = 403 rate-limit. Complétude souvent ~100%. → `testdata/PILOT_RESULTS.md`.
  - **Registre maître Excel** `DataSourcingTemplate/WatchDataSources_FINAL.xlsx` :
    **210 sources**, 33 colonnes (Type, prix, historique, format, difficulté,
    variables, verdict, tier, pilote, ToS, + colonnes collaboratives Assigné à/
    Feedback). Vérif auto de chaque source (accès + robots.txt) → colonne
    "Utilisable ?" : **99 VERT / 49 ORANGE / 62 ROUGE** (rouge = bloqué/mort/
    robots interdit/verdict NON — ex. Barnebys). Onglet Explication pour les
    associés. Prêt à distribuer.
  - Conclusion sources : ~5-8 maisons donnent l'historique daté ; les marchands
    (pattern Shopify/WooCommerce répétable) donnent la quantité ; agrégateurs =
    à éviter (bloqués/interdits). Top 3 absolu : Christie's, Antiquorum, Amsterdam VW.
- Blocked / open: ToS à valider par source ; ~60 "à évaluer" restent à compléter
  (par les associés via l'Excel) ; décision pipeline TS vs Python toujours en attente.
- Next: décider pipeline → Phase 2 design (schéma DB + 1er adaptateur sur une
  source prouvée : Christie's ou Amsterdam VW). Rédiger le rapport final fondateurs.

## 2026-07-20 — Track B : data sourcing & faisabilité (gros bloc)
- Done:
  - Monté le labo `DataSourcingTemplate/` (clusters MaisonsVentes/Agregateurs/
    Marketplaces/Marchands, 1 dossier/source, venv Python partagé).
  - Construit le banc d'essai `faisability/` : scripts qui testent ~30 sources
    sur 3 axes (permis via robots / accessible & format / quantité & data),
    scoring priorité = valeur × faisabilité, + extraction d'échantillon réel.
  - Top 30 sources tous types → sélection 2/type → **vérif profonde + réelle**.
  - Trouvé les mécanismes de collecte : endpoint JSON Next.js (EveryWatch),
    API WooCommerce (WoK), sitemap (European Watch), pagination (Bob's,
    Watchfinder, Bonhams). LiveAuctioneers = API gated ; eBay = API officielle.
  - **8 sources vérifiées en direct avec échantillon réel** (2/type) :
    EveryWatch(558k), WatchRecon | Bob's Watches, eBay(API) | WoK(API, réf/année/
    métal/mvt), Bonhams(Rolex 125k$ réalisé) | Watchfinder, European Watch Co.
  - Barnebys écarté (robots `Disallow: /`) → boussole/licence uniquement.
  - Ajouté la section data-sourcing au `20Jul.md` (founders) ; rapports rangés
    dans `notes/research/faisability/` (sources_finales, solutions, verified,
    final_report, report).
- Blocked / open: valider les ToS de chaque source avant collecte à l'échelle ;
  sécuriser un 2e agrégateur "facile" durable (WatchRecon ok mais léger) ;
  EveryWatch buildId change à chaque déploiement (à relire).
- Next: décider pipeline (TS vs Python) ; démarrer Phase 2 design (schéma DB +
  1er adaptateur sur une source prouvée, ex. WoK ou Bob's Watches).

## 2026-07-19 (suite 3) — Phase 1 durcissement (code)
- Done:
  - Pin Next.js `latest` -> **16.2.10** : corrige la faille App Router
    middleware/proxy bypass ; vulnérabilités **18 -> 2** (moderate, build-only).
  - **CI GitHub Actions** (`.github/workflows/ci.yml`) : typecheck + lint + build
    sur push/PR vers `main` et `dev`.
  - **README** étoffé : setup local, variables d'env, workflow branches/deploy.
  - Retiré `tsconfig.tsbuildinfo` du suivi git (+ .gitignore).
  - **Branche `dev` créée et poussée** (2 environnements : main=prod, dev=preview).
  - Tout vérifié vert : typecheck, lint, build, middleware toujours actif.
- Reste pour clore Phase 1 (côté toi / navigateur):
  - Donner accès aux 4 autres devs (GitHub `WPV3`, Vercel, Neon).
  - Vérifier dans Vercel que Production Branch = `main`.
  - (Reporté) clés Clerk "production" + domaine ; 2 vulns moderate build-only.

## 2026-07-19 (suite 2) — Déploiement Vercel validé
- Done: **App déployée sur Vercel** (`wpv-3.vercel.app`), connectée au repo GitHub.
  Chaîne complète vérifiée EN PRODUCTION : connexion sur l'URL en ligne → Clerk →
  écriture dans Neon confirmée (`last_seen_at` mis à jour à l'instant du login live).
  Variables d'env (clés Clerk + DATABASE_URL) bien présentes côté Vercel.
- Note: on utilise des clés Clerk de TEST (`pk_test`/`sk_test`) sur l'URL en ligne
  → mode "dev" de Clerk (d'où un 404 pour un simple robot/curl, mais OK dans le
  navigateur). Pour la vraie prod: créer une instance Clerk "production" (clés
  `pk_live`) plus tard.
- Next: créer la branche `dev` (2 environnements prod/preview); clés Clerk prod;
  carry-overs (pin Next, npm audit). Puis Phase 2 (design).

## 2026-07-19 (suite) — Phase 1 démarrée
- Done: **Repo GitHub créé et poussé.** `Watchpoint-Dev/WPV3` (org d'équipe,
  privé). `wp-3-main` transformé en repo git indépendant, 1er commit, push via
  SSH (clé `id_ed25519` ajoutée au compte Watchpoint-Dev). Sécurité vérifiée:
  `.env.local` + `node_modules` ignorés, aucun secret poussé (seul `.env.example`
  vide). Standardisé sur npm (bun.lockb retiré). Le placeholder README auto de
  GitHub a été remplacé par notre historique (force-with-lease, repo neuf).
- Next (Phase 1 reste): brancher Vercel (env test + prod) sur le repo; définir la
  stratégie de branches/PR pour l'équipe; carry-overs (pin version Next, npm audit).

## 2026-07-19
- Done: **Phase 0 CLOSED.** Created `.env.local` (Clerk test keys + a fresh Neon
  project on Valentin's own account; old DB abandoned, nothing lost). Verified
  live: Neon connects (PostgreSQL 18.4), route protection enforced (logged-out →
  redirect to /sign-in), and end-to-end Clerk→Neon sync works (browser signup
  wrote a row to `app_users`). `.env.local` confirmed git-ignored.
- Open / next: Phase 1 — create a clean dedicated GitHub repo (none exists yet;
  `bavma-project` is unrelated), then wire Vercel (test + prod). Carry-overs:
  pick one package manager (npm), pin exact Next version, `npm audit` triage.
  Decision still pending: pipeline language (TS vs Python).

## 2026-07-12 / 13
- Done:
  - Full read + diagnostic of the inherited `wp-3-main` codebase (Next.js App
    Router, Clerk auth, Neon, shadcn UI on 100% dummy JSON; ~15-20% vs vision).
  - Wrote `Diagnostic_10-07.md` (structure / good-reusable / bad / scorecard).
  - Wrote then rebuilt `Plan1_10-07.md` into detailed phases: Phase 0 verify
    (inventory + shakedown), Phase 1 setup (GitHub-no-repo-yet, Neon explainer,
    hosting), Phase 2 design (code structure, hexagonal, DB schema, TS-vs-Python),
    Phase 3 build (later), Track B data sourcing.
  - Wrote `tools.md` (current vs planned stack, ORM explainer, TS-vs-Python).
  - Created `research/data-sources.md` living tracker, seeded with eBay,
    WatchCharts, Chrono24, WatchBox, auction houses.
  - Notebook housekeeping: added `TODO.md`, removed empty scaffolding, rewrote
    README as a simple map.
  - Ran the Phase 0 shakedown → `research/phase0-verified-baseline.md`. Facts:
    installs + typechecks + builds + runs (Next 16.1.5). Middleware (`proxy.ts`)
    IS registered — auth-wiring risk resolved. Bun not installed (bun.lockb
    unusable → use npm). 18 npm vulns (2 critical).
- Blocked / open: no `.env.local` (missing Clerk keys + Neon `DATABASE_URL`) →
  can't verify auth enforcement + DB write yet; pipeline language decision
  (TS vs Python) pending; pick one package manager.
- Next: get secrets → re-test auth/DB; then Phase 1 (GitHub repo, Neon access).

## 2026-07-10
- Done: set up `notes/` working notebook (objectives, backlog, ideas, progress,
  questions, research).
- Blocked / open: objectives + first backlog items still to be defined.
- Next: fill OBJECTIVES.md and seed BACKLOG.md.
