[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$CommandText,
    [string]$RouteFile = "config/gi-command-routes.json",
    [switch]$PathsOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Normalize-CommandText {
    param([Parameter(Mandatory = $true)][string]$Value)

    return (($Value.Trim().ToLowerInvariant() -replace '\s+', ' '))
}

$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$resolvedRouteFile = if ([System.IO.Path]::IsPathRooted($RouteFile)) {
    $RouteFile
}
else {
    Join-Path $projectRoot $RouteFile
}

if (-not (Test-Path -LiteralPath $resolvedRouteFile -PathType Leaf)) {
    throw "GI command route manifest is missing: $resolvedRouteFile"
}

$manifest = Get-Content -LiteralPath $resolvedRouteFile -Raw | ConvertFrom-Json
$normalizedCommand = Normalize-CommandText -Value $CommandText
$routeMatches = @()

foreach ($route in $manifest.routes) {
    foreach ($aliasValue in $route.aliases) {
        $alias = Normalize-CommandText -Value ([string]$aliasValue)
        $pattern = '^{0}(?:$|[\s:=])' -f [regex]::Escape($alias)
        if ($normalizedCommand -match $pattern) {
            $routeMatches += [pscustomobject]@{
                Route = $route
                Alias = $alias
                AliasLength = $alias.Length
            }
        }
    }
}

if ($routeMatches.Count -eq 0) {
    throw "No GI command route matched: $CommandText"
}

$selected = $routeMatches | Sort-Object AliasLength -Descending | Select-Object -First 1
$route = $selected.Route

Write-Output ("GI route: {0}" -f $route.id)
Write-Output ("Matched alias: {0}" -f $selected.Alias)
Write-Output ("Contract: {0}" -f $route.contract)
Write-Output "Mandatory context files:"

foreach ($relativePathValue in $route.context_files) {
    $relativePath = [string]$relativePathValue
    $fullPath = Join-Path $projectRoot $relativePath
    if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) {
        throw "Mandatory routed context file is missing: $relativePath"
    }

    Write-Output ("- {0}" -f $relativePath)
}

if ($PathsOnly) {
    exit 0
}

foreach ($relativePathValue in $route.context_files) {
    $relativePath = [string]$relativePathValue
    $fullPath = Join-Path $projectRoot $relativePath
    Write-Output ""
    Write-Output ("===== BEGIN {0} =====" -f $relativePath)
    Get-Content -LiteralPath $fullPath -Raw
    Write-Output ("===== END {0} =====" -f $relativePath)
}
