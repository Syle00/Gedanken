<#
.SYNOPSIS
    Registriert eine taegliche Windows-Aufgabe, die lose Bilddateien in raw/
    nach raw/bilder/ einraeumt.

.DESCRIPTION
    Optional. Ohne diese Aufgabe raeumt bereits jeder Lauf von push.ps1 auf --
    die Aufgabe ist nur fuer den Fall gedacht, dass die Bilder wirklich
    zeitgesteuert am Tagesende wandern sollen, auch wenn an dem Tag nichts
    anderes am Vault passiert.

    Laeuft unter dem angemeldeten Benutzer, ohne Fenster. Verpasste Laeufe (PC aus)
    werden beim naechsten Hochfahren nachgeholt.

.PARAMETER Time
    Startzeit in lokaler Zeit, Format HH:mm. Default 23:15.

.PARAMETER Unregister
    Aufgabe wieder entfernen.

.EXAMPLE
    .\tools\register_bilder_task.ps1

.EXAMPLE
    .\tools\register_bilder_task.ps1 -Time 23:45

.EXAMPLE
    .\tools\register_bilder_task.ps1 -Unregister
#>
[CmdletBinding()]
param(
    [string]$Time = '23:15',
    [switch]$Unregister
)

$ErrorActionPreference = 'Stop'
$taskName = 'Gedanken - Bilder einraeumen'
$repo = Split-Path -Parent $PSScriptRoot
$script = Join-Path $repo 'tools\sort_bilder.py'

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
    -Settings $settings -Description 'Raeumt lose Bilddateien in raw/ nach raw/bilder/ ein.' `
    -Force | Out-Null

Write-Host "Aufgabe '$taskName' registriert - taeglich $Time." -ForegroundColor Green
Write-Host "  Entfernen mit: .\tools\register_bilder_task.ps1 -Unregister"
