"""Charger le journal des prix dans Postgres : data/price_points.jsonl -> price_observation.

    python -m watchpoint charge

Le même code sert l'historique et le quotidien. Chaque ligne est identifiée par
(source, annonce, jour du relevé) : recharger ne crée jamais de doublon, et
seules les lignes nouvelles ou produites par une version antérieure des règles
(normalisation ou filtre) sont écrites. Le chargement est donc idempotent, et
une règle corrigée se propage à toute la base au chargement suivant.

Déroulé, dans une seule transaction :
  1. les sources sont rafraîchies depuis les adaptateurs ;
  2. le journal est normalisé et copié (COPY) dans une table temporaire ;
  3. il est fusionné dans price_observation ;
  4. la table reference est recalculée depuis le journal.
Si quoi que ce soit échoue, la base reste telle qu'elle était.
"""
from __future__ import annotations

import json
import re
import time

from watchpoint import config, normalisation, sources
from watchpoint.collecte.run import GELEES
from watchpoint.db import connexion, hote

# Les colonnes chargées, dans l'ordre du COPY. id et loaded_at sont posés par la base.
COLONNES = (
    "source_id", "external_id", "observed_on", "collected_at", "source_url",
    "price_amount", "price_currency", "price_nature", "price_nature_source",
    "price_date", "price_date_kind", "includes_premium", "estimate_low", "estimate_high",
    "listing_status",
    "brand", "reference_raw", "reference_norm", "reference_source", "model", "title",
    "year", "case_material", "case_size_mm", "movement", "dial_color",
    "condition_raw", "condition", "source_category", "seller",
    "filter_verdict", "filter_rule", "filter_version", "normalisation_version",
)
CLE = ("source_id", "external_id", "observed_on")

_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}")
_DEVISE = re.compile(r"^[A-Z]{3}$")


def _date(valeur) -> str | None:
    texte = str(valeur or "")
    return texte[:10] if _DATE.match(texte) else None


def _nombre(valeur) -> float | None:
    try:
        nombre = float(valeur)
    except (TypeError, ValueError):
        return None
    return nombre if nombre == nombre else None      # écarte NaN


def _annee(valeur) -> int | None:
    nombre = _nombre(valeur)
    return int(nombre) if nombre and 1700 <= nombre <= 2100 else None


def ligne(point: dict, sens_des_dates: dict[str, str]) -> tuple | None:
    """Un point de prix du journal -> une ligne de price_observation, ou None s'il est inutilisable."""
    montant = _nombre(point.get("price_amount"))
    devise = str(point.get("price_currency") or "").upper()
    collecte = point.get("collected_at")
    if not montant or montant <= 0 or not _DEVISE.match(devise) or not _date(collecte):
        return None
    if not point.get("source_id") or not point.get("external_id"):
        return None
    marque = normalisation.marque(point.get("brand"))
    date_prix = _date(point.get("price_date"))
    return (
        point["source_id"], str(point["external_id"]), collecte[:10], collecte,
        point.get("source_url"),
        montant, devise, point.get("price_nature"),
        point.get("price_nature_provenance") or "constante_source",
        date_prix, sens_des_dates.get(point["source_id"]) if date_prix else None,
        point.get("price_includes_premium"),
        _nombre(point.get("estimate_low")), _nombre(point.get("estimate_high")),
        point.get("listing_status"),
        marque, point.get("reference"), normalisation.reference(marque, point.get("reference"),
                                                          point.get("reference_provenance")),
        point.get("reference_provenance"), point.get("model"), point.get("title"),
        _annee(point.get("year")), point.get("case_material"),
        _nombre(point.get("case_size_mm")), point.get("movement"), point.get("dial_color"),
        point.get("condition"), normalisation.etat(point.get("condition")),
        point.get("source_category"), point.get("seller"),
        point.get("filter_verdict") or "QUARANTAINE", point.get("filter_rule"),
        point.get("filter_version"), normalisation.VERSION,
    )


def _sources(cur) -> dict[str, str]:
    """Rafraîchit la table source ; rend le sens de la date de chaque source."""
    sens = {}
    for module in sources.ALL:
        s = module.SOURCE
        sens[s["id"]] = normalisation.sens_de_la_date(s)
        cur.execute(
            """INSERT INTO public.source (id, name, type, default_nature, date_kind, watch_only,
                                          frozen, access, robots, updated_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, now())
               ON CONFLICT (id) DO UPDATE SET
                 name = EXCLUDED.name, type = EXCLUDED.type,
                 default_nature = EXCLUDED.default_nature, date_kind = EXCLUDED.date_kind,
                 watch_only = EXCLUDED.watch_only, frozen = EXCLUDED.frozen,
                 access = EXCLUDED.access, robots = EXCLUDED.robots, updated_at = now()""",
            (s["id"], s["name"], s["type"], s["price_nature"], sens[s["id"]],
             bool(s.get("corpus_horloger")), s["id"] in GELEES, s.get("access"), s.get("robots")))
    return sens


_FUSION = f"""
    INSERT INTO public.price_observation ({", ".join(COLONNES)})
    SELECT DISTINCT ON ({", ".join(CLE)}) {", ".join(COLONNES)}
    FROM charge_tmp
    ORDER BY {", ".join(CLE)}, collected_at DESC
    ON CONFLICT ({", ".join(CLE)}) DO UPDATE SET
      {", ".join(f"{c} = EXCLUDED.{c}" for c in COLONNES if c not in CLE)},
      loaded_at = now()
    WHERE price_observation.normalisation_version IS DISTINCT FROM EXCLUDED.normalisation_version
       OR price_observation.filter_version IS DISTINCT FROM EXCLUDED.filter_version
       OR price_observation.filter_verdict IS DISTINCT FROM EXCLUDED.filter_verdict
    RETURNING (xmax = 0) AS nouvelle
"""

# La fiche de chaque référence, consolidée : la valeur la plus fréquente parmi
# les annonces gardées par le filtre. Recalculée en entier : elle n'est qu'une vue
# matérialisée du journal, on ne l'édite jamais à la main.
_REFERENCES = """
    DELETE FROM public.reference;
    INSERT INTO public.reference (brand, reference_norm, model, case_material, case_size_mm,
                                  movement, n_prices, n_transactions, n_sources,
                                  first_price_date, last_price_date)
    SELECT brand, reference_norm,
           mode() WITHIN GROUP (ORDER BY model),
           mode() WITHIN GROUP (ORDER BY case_material),
           mode() WITHIN GROUP (ORDER BY case_size_mm),
           mode() WITHIN GROUP (ORDER BY movement),
           count(*),
           count(*) FILTER (WHERE price_nature IN ('realised', 'sold')),
           count(DISTINCT source_id),
           min(price_date), max(price_date)
    FROM public.price_observation
    WHERE filter_verdict = 'GARDER' AND brand IS NOT NULL AND reference_norm IS NOT NULL
    GROUP BY brand, reference_norm;
"""


def charger() -> dict:
    debut = time.monotonic()
    compte = {"lues": 0, "ecartees": 0}
    with connexion() as c:
        with c.transaction(), c.cursor() as cur:
            cur.execute("SELECT to_regclass('public.price_observation')")
            if cur.fetchone()[0] is None:
                raise SystemExit("la table price_observation n'existe pas : "
                                 "lancer d'abord `python -m watchpoint db migrate`")
            sens = _sources(cur)
            cur.execute("CREATE TEMP TABLE charge_tmp (LIKE public.price_observation "
                        "INCLUDING DEFAULTS) ON COMMIT DROP")
            with cur.copy(f"COPY charge_tmp ({', '.join(COLONNES)}) FROM STDIN") as copie:
                with config.CUMUL.open(encoding="utf-8") as journal:
                    for texte in journal:
                        compte["lues"] += 1
                        try:
                            valeurs = ligne(json.loads(texte), sens)
                        except json.JSONDecodeError:
                            valeurs = None
                        if valeurs is None:
                            compte["ecartees"] += 1
                            continue
                        copie.write_row(valeurs)
            cur.execute(_FUSION)
            retours = [r[0] for r in cur.fetchall()]
            compte["nouvelles"] = sum(retours)
            compte["mises_a_jour"] = len(retours) - compte["nouvelles"]
            cur.execute(_REFERENCES)
            cur.execute("SELECT count(*) FROM public.price_observation")
            compte["total"] = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM public.reference")
            compte["references"] = cur.fetchone()[0]
    compte["secondes"] = round(time.monotonic() - debut)
    return compte


def main() -> None:
    print(f"base : {hote()}")
    print(f"journal : {config.CUMUL}  ·  normalisation {normalisation.VERSION}")
    r = charger()
    print(f"""
lignes lues dans le journal   {r['lues']:>9}
  écartées (inutilisables)    {r['ecartees']:>9}
nouvelles en base             {r['nouvelles']:>9}
mises à jour (règles changées){r['mises_a_jour']:>9}
total price_observation       {r['total']:>9}
références consolidées        {r['references']:>9}
durée                         {r['secondes']:>8}s""")


if __name__ == "__main__":
    main()
