# auto-push-watcher.ps1 - Watches the repo and triggers a debounced sync+push on any change.
# Started by the "EvoLog AutoPush - Watchdog" scheduled task; kept alive by the watchdog.

. (Join-Path $PSScriptRoot 'auto-push-core.ps1')

# Single-instance guard via global mutex.
$script:Mutex = New-Object System.Threading.Mutex($false, 'Global\EvoLogAutoPushWatcher')
if (-not $script:Mutex.WaitOne(0)) {
    Write-AutoPushLog 'INFO' 'Watcher: another instance already running, exiting.'
    exit 0
}

# Shared state: event actions run in their own context and can only see MessageData (by reference).
# Paths ignored (build output, caches, git internals, databases, logs...).
$script:Data = @{
    Exclude    = '\\(\.git|node_modules|\.next|\.venv|venv|__pycache__|dist|build|\.qoder|\.pytest_cache|\.turbo)\\|\.log$|\.db$|\.db-(wal|shm|journal)$|\.sqlite3?$|\.sqlite-(wal|shm|journal)$|\.pyc$|\.tmp$|\.tsbuildinfo$'
    Debounce   = 20
    Dirty      = $false
    QuietUntil = [datetime]::MinValue
}

Write-AutoPushLog 'INFO' "Watcher started for $script:RepoRoot"

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $script:RepoRoot
$watcher.IncludeSubdirectories = $true
$watcher.NotifyFilter = [System.IO.NotifyFilters]::LastWriteTime -bor [System.IO.NotifyFilters]::FileName -bor [System.IO.NotifyFilters]::DirectoryName
$watcher.EnableRaisingEvents = $true

$onChange = {
    $d = $Event.MessageData
    $path = $Event.SourceEventArgs.FullPath
    if ($path -notmatch $d.Exclude) {
        $d.Dirty = $true
        $d.QuietUntil = (Get-Date).AddSeconds($d.Debounce)
    }
}
Register-ObjectEvent $watcher 'Changed' -Action $onChange -MessageData $script:Data | Out-Null
Register-ObjectEvent $watcher 'Created' -Action $onChange -MessageData $script:Data | Out-Null
Register-ObjectEvent $watcher 'Deleted' -Action $onChange -MessageData $script:Data | Out-Null
Register-ObjectEvent $watcher 'Renamed' -Action $onChange -MessageData $script:Data | Out-Null

try {
    while ($true) {
        Start-Sleep -Seconds 2
        Set-Content -Path $script:HeartbeatFile -Value (Get-Date -Format 'o') -NoNewline
        if ($script:Data.Dirty -and (Get-Date) -ge $script:Data.QuietUntil) {
            $script:Data.Dirty = $false
            Invoke-AutoPushSync -Reason 'watcher-change'
        }
    }
} finally {
    $watcher.EnableRaisingEvents = $false
    $watcher.Dispose()
    Get-EventSubscriber | Unregister-Event
    $script:Mutex.ReleaseMutex()
    $script:Mutex.Dispose()
    Write-AutoPushLog 'INFO' 'Watcher stopped.'
}
# auto-push-watcher.ps1 - Watches the repo and triggers a debounced sync+push on any change.
# Started by the "EvoLog AutoPush - Watchdog" scheduled task; kept alive by the watchdog.

. (Join-Path $PSScriptRoot 'auto-push-core.ps1')

# Single-instance guard via global mutex.
$script:Mutex = New-Object System.Threading.Mutex($false, 'Global\EvoLogAutoPushWatcher')
if (-not $script:Mutex.WaitOne(0)) {
    Write-AutoPushLog 'INFO' 'Watcher: another instance already running, exiting.'
    exit 0
}

# Paths to ignore (build output, caches, git internals, databases, logs...).
$script:ExcludeRegex = '\\(\.git|node_modules|\.next|\.venv|venv|__pycache__|dist|build|\.qoder|\.pytest_cache|\.turbo)\\|\.log$|\.db$|\.sqlite3?$|\.pyc$|\.tmp$|\.tsbuildinfo$'
$script:DebounceSeconds = 20
$script:QuietUntil = [datetime]::MinValue
$script:Dirty = $false

Write-AutoPushLog 'INFO' "Watcher started for $script:RepoRoot"

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $script:RepoRoot
$watcher.IncludeSubdirectories = $true
$watcher.NotifyFilter = [System.IO.NotifyFilters]::LastWriteTime -bor [System.IO.NotifyFilters]::FileName -bor [System.IO.NotifyFilters]::DirectoryName
$watcher.EnableRaisingEvents = $true

$onChange = {
    $path = $Event.SourceEventArgs.FullPath
    if ($path -notmatch $script:ExcludeRegex) {
        $script:Dirty = $true
        $script:QuietUntil = (Get-Date).AddSeconds($script:DebounceSeconds)
    }
}
Register-ObjectEvent $watcher 'Changed' -Action $onChange | Out-Null
Register-ObjectEvent $watcher 'Created' -Action $onChange | Out-Null
Register-ObjectEvent $watcher 'Deleted' -Action $onChange | Out-Null
Register-ObjectEvent $watcher 'Renamed' -Action $onChange | Out-Null

try {
    while ($true) {
        Start-Sleep -Seconds 2
        Set-Content -Path $script:HeartbeatFile -Value (Get-Date -Format 'o') -NoNewline
        if ($script:Dirty -and (Get-Date) -ge $script:QuietUntil) {
            $script:Dirty = $false
            Invoke-AutoPushSync -Reason 'watcher-change'
        }
    }
} finally {
    $watcher.EnableRaisingEvents = $false
    $watcher.Dispose()
    Get-EventSubscriber | Unregister-Event
    $script:Mutex.ReleaseMutex()
    $script:Mutex.Dispose()
    Write-AutoPushLog 'INFO' 'Watcher stopped.'
}
