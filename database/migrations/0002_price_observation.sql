-- 0002 — les prix : une ligne par point de prix observé, le même format pour toutes les sources.
--
-- Écrit par le backend (python -m watchpoint charge), lu par le frontend.
-- Le brut reste sur le disque (data/raw/) ; tout ce qui est ici se reconstruit
-- à partir de lui. Voir docs/ARCHITECTURE.md et docs/donnees.md.

-- ---------------------------------------------------------------------------
-- Les sources : ce qu'on sait d'une source, une fois pour toutes.
-- Rafraîchie à chaque chargement depuis les adaptateurs (sources/__init__.py).
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.source (
  id                TEXT PRIMARY KEY,                -- 'antiquorum', 'hodinkee'…
  name              TEXT NOT NULL,
  type              TEXT NOT NULL,                   -- auction | dealer | retail | marketplace | aggregator | community
  default_nature    TEXT NOT NULL,                   -- la nature de prix déclarée par l'adaptateur
  date_kind         TEXT,                            -- vente | mise_en_ligne | releve : ce que veut dire price_date
  watch_only        BOOLEAN NOT NULL DEFAULT FALSE,  -- la source ne vend que des montres
  frozen            BOOLEAN NOT NULL DEFAULT FALSE,  -- refuse notre robot : plus collectée
  access            TEXT,
  robots            TEXT,
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- Le journal des prix. Une ligne = une annonce, un jour de relevé.
-- La même annonce relevée trois jours de suite donne trois lignes : c'est ce
-- qui permet de voir un prix baisser, puis une annonce disparaître.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.price_observation (
  id                     BIGSERIAL PRIMARY KEY,

  -- identité de la ligne
  source_id              TEXT NOT NULL REFERENCES public.source (id),
  external_id            TEXT NOT NULL,              -- l'identifiant de l'annonce chez la source
  observed_on            DATE NOT NULL,              -- le jour du relevé (UTC)
  collected_at           TIMESTAMPTZ NOT NULL,
  source_url             TEXT,

  -- le prix
  price_amount           NUMERIC(16, 2) NOT NULL CHECK (price_amount > 0),
  price_currency         CHAR(3) NOT NULL,           -- devise d'origine, jamais convertie
  price_nature           TEXT NOT NULL CHECK (price_nature IN ('realised', 'sold', 'asking', 'estimate', 'msrp')),
  price_nature_source    TEXT NOT NULL,              -- champ_dedie | declaree_tag | deduite_statut | constante_source
  price_date             DATE,
  price_date_kind        TEXT CHECK (price_date_kind IN ('vente', 'mise_en_ligne', 'releve')),
  includes_premium       BOOLEAN,                    -- frais acheteur inclus ; NULL = sans objet
  estimate_low           NUMERIC(16, 2),
  estimate_high          NUMERIC(16, 2),
  listing_status         TEXT,

  -- la montre
  brand                  TEXT,                       -- nom canonique (dictionnaire du filtre)
  reference_raw          TEXT,                       -- telle que trouvée
  reference_norm         TEXT,                       -- normalisée : la clé des courbes de cote
  reference_source       TEXT,                       -- champ_dedie | extrait_titre | jeton_titre | extrait_description | sku
  model                  TEXT,
  title                  TEXT,
  year                   SMALLINT,
  case_material          TEXT,
  case_size_mm           NUMERIC(5, 1),
  movement               TEXT,
  dial_color             TEXT,
  condition_raw          TEXT,                       -- l'état tel qu'écrit par la source
  condition              TEXT CHECK (condition IN ('neuf', 'excellent', 'tres_bon', 'bon', 'inconnu')),
  source_category        TEXT,
  seller                 TEXT,

  -- qualité et traçabilité
  filter_verdict         TEXT NOT NULL CHECK (filter_verdict IN ('GARDER', 'REJETER', 'QUARANTAINE')),
  filter_rule            TEXT,
  filter_version         TEXT,
  normalisation_version  TEXT NOT NULL,              -- les règles qui ont produit la ligne
  loaded_at              TIMESTAMPTZ NOT NULL DEFAULT now(),

  CONSTRAINT price_observation_une_par_jour UNIQUE (source_id, external_id, observed_on)
);

-- Les courbes de cote : tous les prix d'une référence, dans le temps.
CREATE INDEX IF NOT EXISTS idx_obs_reference
  ON public.price_observation (brand, reference_norm, price_date)
  WHERE filter_verdict = 'GARDER';
CREATE INDEX IF NOT EXISTS idx_obs_source  ON public.price_observation (source_id, observed_on);
CREATE INDEX IF NOT EXISTS idx_obs_nature  ON public.price_observation (price_nature);

-- ---------------------------------------------------------------------------
-- Les références : une fiche par (marque, référence), consolidée depuis le
-- journal. Entièrement recalculée à chaque chargement : on ne l'édite pas.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.reference (
  brand              TEXT NOT NULL,
  reference_norm     TEXT NOT NULL,
  model              TEXT,                           -- la valeur la plus fréquente parmi les annonces
  case_material      TEXT,
  case_size_mm       NUMERIC(5, 1),
  movement           TEXT,
  n_prices           INTEGER NOT NULL,               -- prix gardés par le filtre
  n_transactions     INTEGER NOT NULL,               -- dont réalisés ou vendus
  n_sources          INTEGER NOT NULL,
  first_price_date   DATE,
  last_price_date    DATE,
  updated_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (brand, reference_norm)
);
