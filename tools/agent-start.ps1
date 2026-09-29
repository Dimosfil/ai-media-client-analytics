[CmdletBinding()]
param(
    [ValidateRange(1, 500)][int]$MaxLines = 80,
    [switch]$ConfigureProjectLanguage,
    [switch]$ConfigureGitCommitLanguages,
    [switch]$ConfigureSystemLanguage
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path

function Invoke-OptionalSelector {
    param(
        [Parameter(Mandatory = $true)][bool]$Enabled,
        [Parameter(Mandatory = $true)][string]$RelativePath
    )
    if (-not $Enabled) { return }

    $selectorPath = Join-Path $projectRoot $RelativePath
    if (-not (Test-Path -LiteralPath $selectorPath -PathType Leaf)) {
        throw "Required selector is missing: $RelativePath"
    }
    & $selectorPath
}

Push-Location $projectRoot
try {
    Invoke-OptionalSelector ([bool]$ConfigureProjectLanguage) "tools/select-project-language.ps1"
    Invoke-OptionalSelector ([bool]$ConfigureGitCommitLanguages) "tools/select-git-commit-languages.ps1"
    Invoke-OptionalSelector ([bool]$ConfigureSystemLanguage) "tools/select-system-language.ps1"

    $contextBuilder = Join-Path $projectRoot "tools/get-gi-context.ps1"
    if (-not (Test-Path -LiteralPath $contextBuilder -PathType Leaf)) {
        throw "GI context builder is missing: tools/get-gi-context.ps1"
    }

    & $contextBuilder -CommandText "gi start" -MaxSummaryLines $MaxLines -MaxStartupFileLines $MaxLines
}
finally {
    Pop-Location
}
