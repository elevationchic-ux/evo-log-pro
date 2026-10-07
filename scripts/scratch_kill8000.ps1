$ErrorActionPreference = 'SilentlyContinue'
$conns = Get-NetTCPConnection -LocalPort 8000
foreach ($c in $conns) {
    $procId = $c.OwningProcess
    $p = Get-Process -Id $procId
    Write-Host "PID $procId : $($p.ProcessName) : $($p.Path)"
    Stop-Process -Id $procId -Force
    Write-Host "KILLED PID $procId"
}
