# auto-push-core.ps1 - Shared logic for the evo-log auto-push protocol.
# Dot-sourced by auto-push-watcher.ps1 and auto-push-watchdog.ps1. Do not run directly.
# All state (logs, heartbeat, lock) lives OUTSIDE the repo (%LOCALAPPDATA%\evo-log-autopush)
# so that syncing never triggers the watcher itself.

$script:RepoRoot = Split-Path -Parent $PSScriptRoot
$script:AutoPushDir = Join-Path $env:LOCALAPPDATA 'evo-log-autopush'
$script:AutoPushLog = Join-Path $script:AutoPushDir 'auto-push.log'
$script:HeartbeatFile = Join-Path $script:AutoPushDir 'watcher.heartbeat'
$script:SyncLockDir = Join-Path $script:AutoPushDir 'sync.lock'

if (-not (Test-Path $script:AutoPushDir)) {
    New-Item -ItemType Directory -Path $script:AutoPushDir -Force | Out-Null
}

function Write-AutoPushLog {
    param([string]$Level, [string]$Message)
    try {
        if ((Test-Path $script:AutoPushLog) -and ((Get-Item $script:AutoPushLog).Length -gt 2MB)) {
            Get-Content $script:AutoPushLog -Tail 1000 | Set-Content $script:AutoPushLog -Encoding UTF8
        }
        "{0} [{1}] {2}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $Level, $Message |
            Add-Content -Path $script:AutoPushLog -Encoding UTF8
    } catch { }
}

function Invoke-Git {
    param([string[]]$Arguments)
    # Runs git inside the repo, returns combined output; $script:GitExit holds the exit code.
    Push-Location $script:RepoRoot
    try {
        $out = & git @Arguments 2>&1 | ForEach-Object { $_.ToString() }
        $script:GitExit = $LASTEXITCODE
        return ($out -join "`n")
    } finally {
        Pop-Location
    }
}

function Invoke-AutoPushSync {
    param([string]$Reason = 'manual')
    # Cross-process lock via mkdir (atomic on NTFS). Stale locks (>15 min) are reclaimed.
    if (Test-Path $script:SyncLockDir) {
        try {
            $ageMin = ((Get-Date) - (Get-Item $script:SyncLockDir).CreationTime).TotalMinutes
            if ($ageMin -lt 15) {
                Write-AutoPushLog 'INFO' ("Sync skipped (locked, {0:N1} min old). Reason: $Reason" -f $ageMin)
                return
            }
            Remove-Item $script:SyncLockDir -Recurse -Force -ErrorAction SilentlyContinue
            Write-AutoPushLog 'WARN' 'Stale sync lock removed.'
        } catch { return }
    }
    New-Item -ItemType Directory -Path $script:SyncLockDir -ErrorAction SilentlyContinue | Out-Null
    if (-not (Test-Path $script:SyncLockDir)) { return }

    try {
        Push-Location $script:RepoRoot
        try {
            Write-AutoPushLog 'INFO' "Sync start (reason: $Reason)"

            $null = Invoke-Git @('add', '-A')
            if ($script:GitExit -ne 0) { Write-AutoPushLog 'ERROR' 'git add failed'; return }

            $null = Invoke-Git @('diff', '--cached', '--quiet')
            $nothingStaged = ($script:GitExit -eq 0)

            if (-not $nothingStaged) {
                $msg = 'chore(auto-push): sync ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
                $null = Invoke-Git @('commit', '-m', $msg)
                if ($script:GitExit -ne 0) { Write-AutoPushLog 'ERROR' 'git commit failed'; return }
            }

            $aheadRaw = Invoke-Git @('rev-list', '--count', 'origin/main..HEAD')
            $ahead = 0
            [void][int]::TryParse(($aheadRaw -replace '\D', ''), [ref]$ahead)
            if ($ahead -le 0) { return }

            for ($try = 1; $try -le 5; $try++) {
                $out = Invoke-Git @('push', 'origin', 'main')
                if ($script:GitExit -eq 0) {
                    Write-AutoPushLog 'INFO' "Pushed $ahead commit(s) OK (attempt $try). Reason: $Reason"
                    return
                }
                Write-AutoPushLog 'WARN' "Push failed (attempt $try): $($out -replace "`r?`n", ' | ')"
                # Remote moved ahead or transient error: rebase local commits on top, abort on conflict.
                $pull = Invoke-Git @('pull', '--rebase', 'origin', 'main')
                if ($script:GitExit -ne 0) {
                    $null = Invoke-Git @('rebase', '--abort')
                    Write-AutoPushLog 'ERROR' "Rebase conflict or fetch failure; commits kept local. Resolve manually. Details: $($pull -replace "`r?`n", ' | ')"
                    return
                }
                Start-Sleep -Seconds (5 * $try)
            }
            Write-AutoPushLog 'ERROR' 'Push failed after 5 attempts; will retry next cycle.'
        } finally {
            Pop-Location
        }
    } finally {
        Remove-Item $script:SyncLockDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}
