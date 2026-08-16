@echo off
REM Bias-Vorlagen headless erzeugen -- Payload fuer den Windows Task Scheduler.
REM Aufruf: bias-cron.cmd daily   bzw.   bias-cron.cmd weekly
REM Der Claude-Code-eigene Cron (CronCreate) taugt hier nicht: session-only,
REM in-memory, feuert nur bei offener idler REPL, laeuft nach 7 Tagen aus.
cd /d "%~dp0.."
set LOG=%~dp0..\algo\live\bias-cron.log
echo. >> "%LOG%"
echo ===== %DATE% %TIME% ^| %1 ===== >> "%LOG%"
"%USERPROFILE%\.local\bin\claude.exe" -p "/bias-vorlage-%1" --allowedTools Bash Read Write Glob Grep >> "%LOG%" 2>&1
