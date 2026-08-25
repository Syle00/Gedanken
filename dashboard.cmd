@echo off
rem Startet die Dashboard-Zentrale und oeffnet sie im Browser.
cd /d "%~dp0"
start "" http://localhost:8787
python tools\dashboard_serve.py
