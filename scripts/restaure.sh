#!/usr/bin/env bash
# Reconstruit data/price_points.jsonl depuis l'instantane versionne (apres un clone).
set -euo pipefail
DATA="$(cd "$(dirname "$0")/.." && pwd)/data"
if [ -e "$DATA/price_points.jsonl" ] && [ "${1:-}" != "--ecrase" ]; then
  echo "data/price_points.jsonl existe deja. Relance avec --ecrase pour le remplacer." >&2
  exit 1
fi
gzip -dc "$DATA/price_points.jsonl.gz" > "$DATA/price_points.jsonl"
echo "restaure : $(wc -l < "$DATA/price_points.jsonl") lignes"
