#!/usr/bin/env bash
# File de collecte SEQUENTIELLE : une source par processus, un journal par jour.
#
#   scripts/collecte.sh                          toutes les sources (hors gelees)
#   scripts/collecte.sh morphy grailzee          celles-ci, l'une apres l'autre
#   scripts/collecte.sh antiquorum:2000-2009     une tranche d'annees (Antiquorum, Christie's)
#   scripts/collecte.sh grailzee:31-36           une tranche de pages du catalogue (Grailzee)
#
# Pourquoi une source par processus : trois collectes en parallele ont epuise la
# memoire le 21/09/2026. Pourquoi caffeinate : le 26/09, le Mac s'est mis en
# veille a 11h45 et toutes les sources suivantes ont echoue en ConnectionError.
# Le cumul etant dedoublonne, relancer une file interrompue ne duplique rien.
set -uo pipefail

RACINE="$(cd "$(dirname "$0")/.." && pwd)"
PY="$RACINE/backend/.venv/bin/python"
mkdir -p "$RACINE/data/logs"
LOG="$RACINE/data/logs/collecte_$(date +%Y-%m-%d).log"

# Empeche la mise en veille tant que la file tourne (macOS uniquement).
if command -v caffeinate >/dev/null && [ -z "${WP_SANS_CAFFEINE:-}" ]; then
  exec env WP_SANS_CAFFEINE=1 caffeinate -is "$0" "$@"
fi

etape() { printf '\n===== %s %s =====\n' "$(date +%H:%M:%S)" "$*" >> "$LOG"; }

lance() {  # lance <source>[:<annees>]
  local source="${1%%:*}" annees=""
  [[ "$1" == *:* ]] && annees="${1#*:}"
  etape "$1"
  case "$source" in
    antiquorum) WP_ANTIQUORUM_ANNEES="$annees" "$PY" -m watchpoint collecte "$source" >> "$LOG" 2>&1 ;;
    christies)  WP_CHRISTIES_ANNEES="$annees"  "$PY" -m watchpoint collecte "$source" >> "$LOG" 2>&1 ;;
    grailzee)   WP_GRAILZEE_PAGES="$annees"    "$PY" -m watchpoint collecte "$source" >> "$LOG" 2>&1 ;;
    "")                                        "$PY" -m watchpoint collecte >> "$LOG" 2>&1 ;;
    *)                                         "$PY" -m watchpoint collecte "$source" >> "$LOG" 2>&1 ;;
  esac
  printf -- '----- fin %s : code %s a %s\n' "$1" "$?" "$(date +%H:%M:%S)" >> "$LOG"
}

etape "DEBUT"
if [ $# -eq 0 ]; then
  lance ""   # sans argument, le moteur prend toutes les sources non gelees
else
  for element in "$@"; do lance "$element"; done
fi
etape "FIN DE FILE"
echo "journal : $LOG"
