"""Le point de prix : parsing des montants et des dates, invariants du schema.

Les cas de parsing sont ceux de qualite/verifie.py : chacun a deja casse en vrai.
"""
import pytest

from watchpoint import schema
from watchpoint.qualite import verifie


def test_controle_parsing_sans_echec():
    verifie.echecs.clear()
    verifie.controle_parsing()
    assert verifie.echecs == []


@pytest.mark.parametrize("brut, montant, devise", [
    ("USD 189,000", 189000.0, "USD"),
    ("€ 25.000", 25000.0, "EUR"),
    ("$3,495", 3495.0, "USD"),
])
def test_parse_money(brut, montant, devise):
    assert schema.parse_money(brut) == (montant, devise)


def test_un_point_de_prix_exige_sa_nature():
    with pytest.raises(ValueError, match="price_nature invalide"):
        schema.price_point(source_id="x", price_amount=100, price_nature="inconnue")


def test_un_point_de_prix_porte_toutes_les_colonnes():
    p = schema.price_point(source_id="x", source_type="dealer", price_amount="1 200",
                           price_currency="EUR", price_nature="asking",
                           price_nature_provenance="constante_source", title="Rolex 16610")
    assert set(schema.FIELDS) <= set(p)
