<#
.SYNOPSIS
    Baut die HTML-Website neu, erstellt einen lokalen Checkpoint-Commit und pusht ihn.

.DESCRIPTION
    Der Standardweg nach jedem Ingest. Reihenfolge ist bewusst: erst bauen, dann
    committen -- schlaegt der Build fehl, entsteht kein Commit mit kaputter Website.

.PARAMETER Message
    Commit-Nachricht. Ohne Angabe: "wiki update <Datum>".

.PARAMETER NoPush
    Nur lokal committen, nicht pushen.

.EXAMPLE
    .\push.ps1 -Message "ingest | Essentials To ICT Daytrading"

.EXAMPLE
    .\push.ps1
#>
[CmdletBinding()]
param(
    [string]$Message,
    [switch]$NoPush
)

# Bewusst NICHT 'Stop': git schreibt Hinweise (CRLF-Warnungen, Push-Fortschritt) auf
# stderr. Mit 'Stop' wuerde das Skript daran abbrechen, sobald jemand die Ausgabe
# umleitet. Fehler werden stattdessen unten explizit ueber $LASTEXITCODE geprueft.
$ErrorActionPreference = 'Continue'
$repo = $PSScriptRoot
Set-Location $repo

function Fail($text) { Write-Host "FEHLER: $text" -ForegroundColor Red; exit 1 }

$env:PYTHONIOENCODING = 'utf-8'

# --- 0. Marktdaten einraeumen ----------------------------------------------
# Lose CSV-Exporte wandern in ihren Tagesordner (dd.mm.jjjj), bevor irgendetwas
# committet wird. Bewusst nicht abbruchrelevant: eine Datei, deren Timeframe
# nicht erkannt wird, darf keinen Publish blockieren -- sie bleibt einfach liegen.
python (Join-Path $repo 'tools\sort_marktdaten.py') --quiet

# --- 0b. Bilder einraeumen --------------------------------------------------
# Lose Bilddateien direkt unter raw/ wandern nach raw/bilder/.
python (Join-Path $repo 'tools\sort_bilder.py') --quiet

# --- 1. Website bauen ------------------------------------------------------
Write-Host "[1/4] Website bauen ..." -ForegroundColor Cyan
python (Join-Path $repo 'tools\build_site.py')
if ($LASTEXITCODE -ne 0) {
    Fail "Build fehlgeschlagen (Exit $LASTEXITCODE). Es wurde nichts committet."
}

# --- 2. Aenderungen einsammeln --------------------------------------------
Write-Host "`n[2/4] Aenderungen einsammeln ..." -ForegroundColor Cyan
git add -A
if ($LASTEXITCODE -ne 0) { Fail "'git add' fehlgeschlagen." }

git diff --cached --quiet
$nothingToCommit = ($LASTEXITCODE -eq 0)

# --- 3. Commit -------------------------------------------------------------
# Auch ohne neue Aenderungen weiterlaufen: es koennen noch ungepushte Commits
# aus einem frueheren Lauf offen sein (z.B. weil damals kein Remote existierte).
if ($nothingToCommit) {
    Write-Host "  Keine Aenderungen - kein Commit noetig." -ForegroundColor Yellow
    Write-Host "`n[3/4] Commit uebersprungen." -ForegroundColor Cyan
} else {
    Write-Host "  $(git diff --cached --shortstat)"
    if (-not $Message) { $Message = "wiki update $(Get-Date -Format 'yyyy-MM-dd')" }
    Write-Host "`n[3/4] Commit: $Message" -ForegroundColor Cyan
    git commit -q -m $Message
    if ($LASTEXITCODE -ne 0) { Fail "'git commit' fehlgeschlagen." }
    Write-Host "  $(git log -1 --format='%h %s')"
}

# --- 4. Push ---------------------------------------------------------------
if ($NoPush) {
    Write-Host "`n[4/4] Push uebersprungen (-NoPush)." -ForegroundColor Yellow
    exit 0
}

$remotes = git remote
if (-not $remotes) {
    Write-Host "`n[4/4] Kein Remote konfiguriert - nur lokaler Checkpoint." -ForegroundColor Yellow
    Write-Host "      Einrichten mit: git remote add origin <URL>"
    exit 0
}

Write-Host "`n[4/4] Push nach origin ..." -ForegroundColor Cyan
$branch = git rev-parse --abbrev-ref HEAD
git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    git push -u origin $branch          # erster Push: Upstream setzen
} else {
    git push
}
if ($LASTEXITCODE -ne 0) {
    Write-Host "Push fehlgeschlagen. Der lokale Commit ist erhalten -" -ForegroundColor Red
    Write-Host "spaeter einfach 'git push' erneut ausfuehren." -ForegroundColor Red
    exit 1
}

Write-Host "`nFertig. Website: $(Join-Path $repo 'site\index.html')" -ForegroundColor Green
