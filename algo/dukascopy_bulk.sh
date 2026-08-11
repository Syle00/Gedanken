#!/bin/bash
SYMS="EURUSD USDJPY GBPUSD USDCHF AUDUSD USDCAD NZDUSD EURJPY EURGBP GBPJPY"
for sym in $SYMS; do
  echo "=== $sym start $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" >> dukascopy_bulk.log
  python fetch_dukascopy.py "$sym" --von 2003-01-01 --bis 2026-08-11 --bericht "results/dukascopy_${sym}_report.json" >> dukascopy_bulk.log 2>&1
  echo "=== $sym done $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" >> dukascopy_bulk.log
done
echo "=== ALL DONE $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" >> dukascopy_bulk.log
