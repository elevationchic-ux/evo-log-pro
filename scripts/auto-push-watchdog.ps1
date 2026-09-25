# auto-push-watchdog.ps1 - Guarantee layer. Runs every 2 minutes via Scheduled Task.
# 1) Does a catch-up sync (in case the watcher missed something or was down).
# 2) Restarts the watcher if it is not running (mutex check).

. (Join-Path $PSScriptRoot 'auto-push-core.ps1')

# Catch-up sync (no-op if already clean).
Invoke-AutoPushSync -Reason 'watchdog'

# Restart the watcher if its mutex is free (meaning it is not running).
$mutex = New-Object System.Threading.Mutex($false, 'Global\EvoLogAutoPushWatcher')
$needsRestart = $mutex.WaitOne(0)
$mutex.ReleaseMutex()
$mutex.Dispose()

if ($needsRestart) {
    Write-AutoPushLog 'INFO' 'Watchdog: watcher not running, restarting it.'
    $watcherScript = Join-Path $PSScriptRoot 'auto-push-watcher.ps1'
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = 'powershell.exe'
    $psi.Arguments = "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$watcherScript`""
    $psi.UseShellExecute = $true
    $psi.WindowStyle = 'Hidden'
    [System.Diagnostics.Process]::Start($psi) | Out-Null
}
