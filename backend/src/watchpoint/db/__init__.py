"""Postgres : connexion, migrations, chargement du journal jsonl dans les tables.

A FAIRE — etape 6 du plan. Le schema vit dans database/migrations/ ; ce module
l'applique (`python -m watchpoint db migrate`) et charge data/price_points.jsonl
de facon idempotente. Voir docs/ARCHITECTURE.md §4.
"""
