@echo off
REM Legt die zwei Windows-Tasks fuer die Bias-Vorlagen an (einmalig ausfuehren).
REM Als eigene .cmd, weil Git Bash "/create" sonst in einen Pfad umschreibt.
set W=%~dp0bias-cron.cmd

schtasks /create /tn "Gedanken Daily Bias"  /tr "\"%W%\" daily"  /sc weekly /d SUN,MON,TUE,WED,THU /st 20:03 /f
schtasks /create /tn "Gedanken Weekly Bias" /tr "\"%W%\" weekly" /sc weekly /d FRI                 /st 20:03 /f

echo.
echo ===== Kontrolle =====
schtasks /query /tn "Gedanken Daily Bias"  /fo LIST | findstr /i "TaskName Naechste Next Status"
schtasks /query /tn "Gedanken Weekly Bias" /fo LIST | findstr /i "TaskName Naechste Next Status"
