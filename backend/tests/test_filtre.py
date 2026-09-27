"""Le banc du filtre : les cas de test vivent dans filters.json, compiles depuis l'Excel.

Un echec ici veut dire qu'une modification du classeur a change un verdict
attendu. Voir la boucle de mesure dans backend/README.md.
"""
from watchpoint.filtrage.filtre import banc, filtre


def test_la_config_du_filtre_se_charge():
    f = filtre()
    assert f.conf["test_cases"], "filters.json ne porte aucun cas de test"
    assert f.conf["brands"], "filters.json ne porte aucune marque"


def test_tous_les_cas_du_banc_passent():
    assert banc() == 0
