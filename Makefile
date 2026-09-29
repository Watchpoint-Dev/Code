# Les commandes courantes. `make` sans argument affiche l'aide.
#
# Le backend s'appelle toujours par le Python de son venv : pas besoin
# d'activer quoi que ce soit.

PY := backend/.venv/bin/python
SOURCES ?=

.DEFAULT_GOAL := aide
.PHONY: aide install test lint check verifie collecte rapports sauvegarde restaure front

aide:
	@echo "Installation"
	@echo "  make install              venv backend + dépendances frontend"
	@echo "Vérifications"
	@echo "  make test                 tests du backend (pytest)"
	@echo "  make lint                 ruff sur le backend"
	@echo "  make check                typecheck + lint + build du frontend"
	@echo "  make verifie              invariants de la base de prix"
	@echo "Données"
	@echo "  make collecte SOURCES='morphy antiquorum:2010-2012'"
	@echo "  make rapports             régénère docs/rapports/"
	@echo "  make sauvegarde           instantané data/price_points.jsonl.gz"
	@echo "  make restaure             reconstruit data/price_points.jsonl"
	@echo "Site"
	@echo "  make front                serveur de développement, http://localhost:3000"

install:
	python3 -m venv backend/.venv
	$(PY) -m pip install -e "backend[dev]"
	cd frontend && npm ci

test:
	backend/.venv/bin/pytest backend

lint:
	backend/.venv/bin/ruff check backend/src backend/tests

check:
	cd frontend && npm run check

verifie:
	$(PY) -m watchpoint verifie

collecte:
	scripts/collecte.sh $(SOURCES)

rapports:
	$(PY) -m watchpoint rapports

sauvegarde:
	scripts/sauvegarde.sh

restaure:
	scripts/restaure.sh

front:
	cd frontend && npm run dev
