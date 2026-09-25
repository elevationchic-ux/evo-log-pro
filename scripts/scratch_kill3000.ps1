$conns = Get-NetTCPConnection -State Listen -LocalPort 3000 -ErrorAction SilentlyContinue
$pids = @()
foreach ($c in $conns) {
  if ($pids -notcontains $c.OwningProcess) {
    Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue
    Write-Output ("killed PID " + $c.OwningProcess)
    $pids += $c.OwningProcess
  }
}
