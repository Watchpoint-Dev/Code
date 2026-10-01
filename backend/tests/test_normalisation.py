"""La normalisation : références, état, sens de la date, et la ligne chargée en base.

Chaque cas vient de la base réelle (mesure du 01/10/2026).
"""
import pytest

from watchpoint import normalisation as n
from watchpoint.db.charge import COLONNES, ligne


@pytest.mark.parametrize("marque, brute, attendue", [
    ("Rolex", "116710 LN", "116710LN"),                       # espace
    ("Rolex", "16610lv", "16610LV"),                          # casse
    ("Rolex", "336938-0006", "336938"),                       # suffixe de variante Rolex
    ("Rolex", "18039, inside case back stamped 18000", "18039"),
    ("Patek Philippe", "5227G-010", "5227G"),                 # suffixe de cadran Patek
    ("Patek Philippe", "5711/1A", "5711/1A"),                 # la barre est gardée
    ("Audemars Piguet", "15400ST.OO.1220ST.01", "15400ST"),   # suffixe de bracelet AP
    ("Audemars Piguet", "15400ST", "15400ST"),                # ST = acier, pas un ordinal
    ("Omega", "311.30.42.30.01.005", "311.30.42.30.01.005"),  # Omega : rien n'est retiré
    (None, "ref. 517", "517"),                                # préfixe
    ("Jaeger-LeCoultre", "E 871", "E871"),
])
def test_reference_normalisee(marque, brute, attendue):
    assert n.reference(marque, brute) == attendue


@pytest.mark.parametrize("brute", ["96", "50th", "175th", "25318000", "ELHT", "", None])
def test_ce_qui_n_est_pas_une_reference(brute):
    assert n.reference("Rolex", brute) is None


def test_un_suffixe_n_est_retire_que_pour_sa_marque():
    # « -0001 » est une variante chez Rolex, pas forcément ailleurs.
    assert n.reference("Tudor", "79230-0001") == "79230-0001"


@pytest.mark.parametrize("brut, niveau", [
    ("new", "neuf"), ("Unworn", "neuf"), ("New Old Stock", "neuf"),
    ("AAA", "excellent"), ("Excellent", "excellent"), ("Mint", "excellent"),
    ("AA", "tres_bon"), ("Very Good", "tres_bon"),
    ("A", "bon"), ("B", "bon"), ("Good", "bon"), ("used", "bon"),
    ("preowned", "inconnu"), ("Pre-owned", "inconnu"), ("???", "inconnu"), (None, "inconnu"),
])
def test_etat(brut, niveau):
    assert n.etat(brut) == niveau


@pytest.mark.parametrize("source, sens", [
    ({"id": "antiquorum", "type": "auction"}, "vente"),
    ({"id": "everywatch", "type": "aggregator"}, "vente"),
    ({"id": "montredo", "type": "dealer"}, "releve"),
    ({"id": "hodinkee", "type": "dealer"}, "mise_en_ligne"),
])
def test_sens_de_la_date(source, sens):
    assert n.sens_de_la_date(source) == sens


POINT = {
    "source_id": "grailzee", "external_id": 42, "collected_at": "2026-09-29T12:00:00+00:00",
    "price_amount": 11000, "price_currency": "usd", "price_nature": "realised",
    "price_nature_provenance": "champ_dedie", "price_date": "2026-09-14",
    "price_includes_premium": False, "brand": "Rolex", "reference": "126610LN-0001",
    "reference_provenance": "champ_dedie", "condition": "AA", "year": "2021",
    "filter_verdict": "GARDER", "filter_rule": "R8", "filter_version": "v1",
}


def test_une_ligne_complete():
    valeurs = dict(zip(COLONNES, ligne(POINT, {"grailzee": "vente"})))
    assert len(valeurs) == len(COLONNES)
    assert valeurs["external_id"] == "42"
    assert valeurs["observed_on"] == "2026-09-29"
    assert valeurs["price_currency"] == "USD"
    assert valeurs["price_date_kind"] == "vente"
    assert valeurs["reference_raw"] == "126610LN-0001"
    assert valeurs["reference_norm"] == "126610LN"
    assert valeurs["condition"] == "tres_bon"
    assert valeurs["year"] == 2021
    assert valeurs["normalisation_version"] == n.VERSION


@pytest.mark.parametrize("defaut", [
    {"price_amount": 0}, {"price_amount": None}, {"price_currency": "dollars"},
    {"collected_at": None}, {"external_id": None},
])
def test_une_ligne_inutilisable_est_ecartee(defaut):
    assert ligne({**POINT, **defaut}, {}) is None


def test_pas_de_sens_de_date_sans_date():
    valeurs = dict(zip(COLONNES, ligne({**POINT, "price_date": None}, {"grailzee": "vente"})))
    assert valeurs["price_date"] is None and valeurs["price_date_kind"] is None


@pytest.mark.parametrize("brute, attendue", [
    ("1806; interior case back stamped 1803", "1806"),       # note de catalogue Phillips
    ("16520 inside case back stamped 16500", "16520"),
    ("BRUNSWICK-38-ORCHID-BRACELET", None),                  # code produit de 28 caractères
    ("VINTAGE 1950S ALUMINIUM DESK JET PLANE", None),        # un titre entier
    ("x" * 5000 + "1", None),                                # le cas qui avait fait échouer le chargement
])
def test_notes_et_dechets(brute, attendue):
    assert n.reference("Rolex", brute) == attendue


def test_marque():
    assert n.marque("  Rolex ") == "Rolex"
    assert n.marque("Louis Erard X Alain Silberstein") == "Louis Erard X Alain Silberstein"
    assert n.marque("A Lange & Sohns Abercrombie & Fitch Adanac Agassiz Alain Silberstein " * 3) is None
    assert n.marque(None) is None


def test_un_sku_de_repli_n_est_pas_une_cle_de_courbe():
    assert n.reference("Rolex", "116610LN", "sku") is None
    assert n.reference("Rolex", "116610LN", "champ_dedie") == "116610LN"
    assert n.reference("Rolex", "116610LN", "jeton_titre") == "116610LN"
