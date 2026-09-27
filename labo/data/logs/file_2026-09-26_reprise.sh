#!/bin/zsh
# File de collecte du 26/09/2026 — sequentielle (verrou de run.py), une source par processus.
cd /Users/vale/Desktop/WP/labo/moteur
PY=../shared/.venv/bin/python
LOG=../data/logs/collecte_2026-09-26_reprise.log
etape() { echo "\n===== $(date '+%H:%M:%S') $* =====" >> $LOG; }
lance() { etape "$*"; $PY run.py "$@" >> $LOG 2>&1; echo "----- fin $* : code $? a $(date '+%H:%M:%S')" >> $LOG; }
etape "DEBUT"
lance morphy
for s in \
         montredo cwsellors berrys hairspring hodinkee \
         keystone watchtrader awco globalwatchshop chronofinder bulangandsons \
         acollectedman amsterdamvintage sworders topper watchrecon knightsbridge \
         certifiedwatchstore cottone; do
  lance $s
done
WP_ANTIQUORUM_ANNEES=2020-2026 lance antiquorum
WP_ANTIQUORUM_ANNEES=2000-2009 lance antiquorum
WP_ANTIQUORUM_ANNEES=1989-1999 lance antiquorum
etape "FIN DE FILE"
