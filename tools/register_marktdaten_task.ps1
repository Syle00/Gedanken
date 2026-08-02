<#
.SYNOPSIS
    Registriert eine taegliche Windows-Aufgabe, die lose CSVs in raw/marktdaten/
    in ihren Tagesordner einraeumt.

.DESCRIPTION
    Optional. Ohne diese Aufgabe raeumt bereits jeder Lauf von publish.ps1 und
    analyze_ohlc.py auf -- die Aufgabe ist nur fuer den Fall gedacht, dass die
    Dateien wirklich zeitgesteuert am Tagesende wandern sollen, auch wenn an dem
    Tag nichts anderes am Vault passiert.

    Laeuft unter dem angemeldeten Benutzer, ohne Fenster. Verpasste Laeufe (PC aus)
    werden beim naechsten Hochfahren nachgeholt.

.PARAMETER Time
    Startzeit in lokaler Zeit, Format HH:mm. Default 23:15 -- die CME-Session
    endet um 17:00 New York, das sind 23:00 in Berlin.

.PARAMETER Unregister
    Aufgabe wieder entfernen.

.EXAMPLE
    .\tools\register_marktdaten_task.ps1

.EXAMPLE
    .\tools\register_marktdaten_task.ps1 -Time 23:45

.EXAMPLE
    .\tools\register_marktdaten_task.ps1 -Unregister
#>
[CmdletBinding()]
param(
    [string]$Time = '23:15',
    [switch]$Unregister
)

$ErrorActionPreference = 'Stop'
$taskName = 'Gedanken - Marktdaten einraeumen'
$repo = Split-Path -Parent $PSScriptRoot
$script = Join-Path $repo 'tools\sort_marktdaten.py'

if ($Unregister) {
    try {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
        Write-Host "Aufgabe '$taskName' entfernt." -ForegroundColor Green
    } catch {
        Write-Host "Aufgabe '$taskName' war nicht registriert." -ForegroundColor Yellow
    }
    exit 0
}

if (-not (Test-Path $script)) { throw "Nicht gefunden: $script" }

$python = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $python) { throw "python nicht im PATH gefunden." }

if ($Time -notmatch '^\d{1,2}:\d{2}$') { throw "Ungueltige Zeit: '$Time' (erwartet HH:mm)." }

$action = New-ScheduledTaskAction -Execute $python `
    -Argument "`"$script`" --quiet" -WorkingDirectory $repo
$trigger = New-ScheduledTaskTrigger -Daily -At $Time
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable `
    -DontStopIfGoingOnBatteries -AllowStartIfOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10)

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger `
    -Settings $settings -Description 'Raeumt lose CSV-Exporte in raw/marktdaten/ in Tagesordner (dd.mm.jjjj) ein.' `
    -Force | Out-Null

Write-Host "Aufgabe '$taskName' registriert - taeglich $Time." -ForegroundColor Green
Write-Host "  Entfernen mit: .\tools\register_marktdaten_task.ps1 -Unregister"
