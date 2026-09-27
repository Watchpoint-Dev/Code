#!/usr/bin/env bash
# Instantane compresse de l'actif, celui qui est versionne dans git.
# gzip -9n : sans horodatage ni nom de fichier, donc deterministe — deux
# instantanes d'une meme base donnent le meme fichier, et git ne voit rien.
set -euo pipefail
DATA="$(cd "$(dirname "$0")/.." && pwd)/data"
n=$(wc -l < "$DATA/price_points.jsonl")
# Seules les lignes COMPLETES : une collecte peut etre en train d'ecrire.
head -n "$n" "$DATA/price_points.jsonl" | gzip -9n > "$DATA/price_points.jsonl.gz"
echo "instantane : $n lignes -> data/price_points.jsonl.gz ($(du -h "$DATA/price_points.jsonl.gz" | cut -f1))"
