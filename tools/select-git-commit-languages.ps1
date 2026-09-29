param(
    [string]$OutputPath = "tools/project-memory/git-preferences.json",
    [string]$Selection = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$available = @("English", "Russian", "Spanish", "German", "French")
$languageAliases = @{
    "english" = "English"
    "en" = "English"
    "russian" = "Russian"
    "ru" = "Russian"
    "spanish" = "Spanish"
    "es" = "Spanish"
    "german" = "German"
    "de" = "German"
    "french" = "French"
    "fr" = "French"
}
$defaultSelected = @("English")

if (Test-Path -LiteralPath $OutputPath) {
    try {
        $existing = Get-Content -LiteralPath $OutputPath -Raw | ConvertFrom-Json
        $existingLanguages = @()
        if ($existing.commit_message_languages.primary) {
            $existingLanguages += [string]$existing.commit_message_languages.primary
        }
        if ($existing.commit_message_languages.additional) {
            $existingLanguages += @($existing.commit_message_languages.additional | ForEach-Object { [string]$_ })
        }
        $defaultSelected = @($existingLanguages | Where-Object { $available -contains $_ } | Select-Object -Unique)
        if ($defaultSelected.Count -eq 0) {
            $defaultSelected = @("English")
        }
    }
    catch {
        Write-Host "Could not read existing preferences; using defaults."
    }
}

Write-Host "Select commit message languages."
Write-Host "English is always the primary language. Enter numbers or names in any clear format."
Write-Host ""

for ($i = 0; $i -lt $available.Count; $i++) {
    $language = $available[$i]
    $checked = if ($defaultSelected -contains $language) { "[x]" } else { "[ ]" }
    Write-Host ("{0} {1}. {2}" -f $checked, ($i + 1), $language)
}

Write-Host ""
if ([string]::IsNullOrWhiteSpace($Selection)) {
    $inputText = Read-Host "Selection"
}
else {
    $inputText = $Selection
}

if ([string]::IsNullOrWhiteSpace($inputText)) {
    $selected = $defaultSelected
}
else {
    $normalizedInput = $inputText.ToLowerInvariant() -replace "[^0-9a-z]+", " "
    $selected = foreach ($part in ($normalizedInput -split "\s+")) {
        $trimmed = $part.Trim()
        if ($trimmed -match "^[0-9]+$") {
            $index = [int]$trimmed - 1
            if ($index -ge 0 -and $index -lt $available.Count) {
                $available[$index]
            }
        }
        elseif ($languageAliases.ContainsKey($trimmed)) {
            $languageAliases[$trimmed]
        }
    }
}

$selected = @($selected | Where-Object { $_ } | Select-Object -Unique)
if ($selected -notcontains "English") {
    $selected = @("English") + $selected
}

$additional = @($selected | Where-Object { $_ -ne "English" })

$config = [ordered]@{
    commit_message_languages = [ordered]@{
        primary = "English"
        additional = $additional
        available = $available
        format = "english_plus_selected_translations"
    }
}

$directory = Split-Path -Parent $OutputPath
if ($directory -and -not (Test-Path -LiteralPath $directory)) {
    New-Item -ItemType Directory -Path $directory -Force | Out-Null
}

$config | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $OutputPath -Encoding UTF8

Write-Host ""
Write-Host "Saved git commit language preferences to $OutputPath"
Write-Host "Primary: English"
if ($additional.Count -gt 0) {
    Write-Host ("Additional: {0}" -f ($additional -join ", "))
}
else {
    Write-Host "Additional: none"
}
