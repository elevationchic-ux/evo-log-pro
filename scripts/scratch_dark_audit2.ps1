$pat = 'bg-white|bg-gray-(50|100|200)([^0-9a-f]|$)|bg-slate-(50|100|200)([^0-9a-f]|$)|divide-(slate|gray)-(100|200)|border-(slate|gray)-(100|200|300)([^0-9a-f]|$)|text-(slate|gray)-(7|8|9)00|hover:bg-(slate|gray)-(50|100)([^0-9a-f]|$)'
$root = Join-Path $PSScriptRoot '..\evo-log-frontend\src'
Get-ChildItem -Path $root -Recurse -Filter *.tsx |
  Select-String -Pattern $pat |
  Where-Object { $_.Line -notmatch 'dark:' } |
  ForEach-Object { '{0}:{1}: {2}' -f $_.Filename, $_.LineNumber, $_.Line.Trim().Substring(0, [Math]::Min(140, $_.Line.Trim().Length)) }
