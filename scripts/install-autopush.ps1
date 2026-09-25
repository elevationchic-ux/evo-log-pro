# install-autopush.ps1 - One-time setup: registers the recurring watchdog Scheduled Task.
# Run ONCE from a normal PowerShell (non-sandboxed). Uses ScheduledTasks cmdlets so the
# repo path containing spaces is handled safely (no schtasks /TR string parsing).
#
# Usage: powershell -NoProfile -ExecutionPolicy Bypass -File install-autopush.ps1

$ErrorActionPreference = 'Stop'
$scriptDir = $PSScriptRoot
$watchdog = Join-Path $scriptDir 'auto-push-watchdog.ps1'
$taskName = 'EvoLogAutoPush'

# Remove a previous registration if present.
Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue | Unregister-ScheduledTask -Confirm:$false

# Action: run the watchdog hidden. Argument is a single string; the quoted path keeps spaces intact.
$argLine = "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$watchdog`""
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $argLine

# Trigger: start now, then repeat every 2 minutes indefinitely (no duration limit).
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Minutes 2)

# Settings: run on battery, don't stop on battery, start if missed, no execution time cap.
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -StartWhenAvailable -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings `
    -Description 'EVO-LOG auto-push: commits and pushes repo changes to GitHub main automatically.' -Force | Out-Null

# Kick it off immediately (also starts the watcher on its first run).
Start-ScheduledTask -TaskName $taskName

Write-Host ""
Write-Host "=== Auto-Push Protocol Installed ===" -ForegroundColor Green
Write-Host "  Task name   : $taskName (every 2 minutes)"
Write-Host "  Watcher     : FileSystemWatcher (20 s debounce -> git add/commit/push)"
Write-Host "  Log file    : $env:LOCALAPPDATA\evo-log-autopush\auto-push.log"
Write-Host "  Status      : Get-ScheduledTaskInfo -TaskName $taskName"
Write-Host "  Uninstall   : Unregister-ScheduledTask -TaskName $taskName -Confirm:`$false"
Write-Host ""
Write-Host "Ignored paths: .git, node_modules, .next, __pycache__, dist, build, *.log, *.db, *.pyc, ..."
