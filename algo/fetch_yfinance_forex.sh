#!/bin/bash
# Laedt die 10 groessten Forex-Paare per yfinance (fetch_yfinance.py --symbol),
# max verfuegbare Historie je Timeframe. Drei Passes pro Paar, weil Yahoo pro Timeframe
# ein hartes Limit hat, das NICHT vom Startdatum im Request abhaengt, sondern die ganze
# Anfrage ablehnt, wenn sie darueber hinausreicht: 1h max 730 Tage zurueck (harte
# Yahoo-Fehlermeldung, nicht nur leere Chunks), 1m/5m/15m faktisch ~30/60 Tage (leere
# Chunks statt Fehler, aber ueber Jahrzehnte trotzdem hunderte sinnlose Requests, siehe
# fetch_yfinance.py::fetch-Docstring). Nur 1d ist unbegrenzt.
SYMS="EURUSD=X USDJPY=X GBPUSD=X USDCHF=X AUDUSD=X USDCAD=X NZDUSD=X EURJPY=X EURGBP=X GBPJPY=X"
for sym in $SYMS; do
  echo "=== $sym deep (1d) $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" >> fetch_yfinance_forex.log
  python fetch_yfinance.py 2000-01-01 2026-08-12 --symbol "$sym" --intervals 1d >> fetch_yfinance_forex.log 2>&1
  echo "=== $sym medium (1h, max 730d) $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" >> fetch_yfinance_forex.log
  python fetch_yfinance.py 2024-08-12 2026-08-12 --symbol "$sym" --intervals 1h >> fetch_yfinance_forex.log 2>&1
  echo "=== $sym shallow (1m,5m,15m) $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" >> fetch_yfinance_forex.log
  python fetch_yfinance.py 2026-06-07 2026-08-12 --symbol "$sym" --intervals 1m,5m,15m >> fetch_yfinance_forex.log 2>&1
done
echo "=== ALL DONE $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" >> fetch_yfinance_forex.log
