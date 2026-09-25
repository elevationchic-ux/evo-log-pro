$pat = 'bg-white|bg-gray-(50|100|200)([^0-9a-f]|$)|bg-slate-(50|100|200)([^0-9a-f]|$)|divide-(slate|gray)-(100|200)|border-(slate|gray)-(100|200|300)([^0-9a-f]|$)|text-(slate|gray)-(7|8|9)00|hover:bg-(slate|gray)-(50|100)([^0-9a-f]|$)|dark:'
$root = Join-Path $PSScriptRoot '..\evo-log-frontend\src\app'
Get-ChildItem -Path $root -Recurse -Filter *.tsx |
  Select-String -Pattern $pat |
  Group-Object Path |
  Sort-Object Count -Descending |
  ForEach-Object { '{0,4}  {1}' -f $_.Count, $_.Name }
