#!/bin/zsh
# Reprise du 27/09/2026 : tranches Antiquorum en timeout le 26 au soir + Grailzee/Hodinkee coupees par le reseau.
cd /Users/vale/Desktop/WP/labo/moteur
PY=../shared/.venv/bin/python
LOG=../data/logs/collecte_2026-09-27.log
etape() { echo "\n===== $(date '+%H:%M:%S') $* =====" >> $LOG; }
lance() { etape "$*"; $PY run.py "$@" >> $LOG 2>&1; echo "----- fin $* : code $? a $(date '+%H:%M:%S')" >> $LOG; }
etape "DEBUT"
WP_ANTIQUORUM_ANNEES=2020-2025 lance antiquorum
lance hodinkee
WP_ANTIQUORUM_ANNEES=2000-2009 lance antiquorum
lance grailzee
WP_ANTIQUORUM_ANNEES=1989-1999 lance antiquorum
etape "FIN DE FILE"
