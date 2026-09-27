"""Les regles de l'architecture, verifiees plutot que promises.

docs/ARCHITECTURE.md §7 : la production n'importe jamais depuis research/, et
aucun chemin absolu de machine n'est code en dur.
"""
import pathlib
import re

SRC = pathlib.Path(__file__).resolve().parents[1] / "src" / "watchpoint"
FICHIERS = sorted(SRC.rglob("*.py"))


def test_la_production_n_importe_pas_research():
    fautifs = [f.name for f in FICHIERS
               if re.search(r"^\s*(from|import)\s+research\b", f.read_text(encoding="utf-8"), re.M)]
    assert fautifs == []


def test_aucun_chemin_absolu_de_machine():
    fautifs = [f.name for f in FICHIERS if "/Users/" in f.read_text(encoding="utf-8")]
    assert fautifs == []


def test_plus_aucun_bricolage_de_sys_path():
    fautifs = [f.name for f in FICHIERS
               if re.search(r"^\s*sys\.path\.(insert|append)", f.read_text(encoding="utf-8"), re.M)]
    assert fautifs == []
