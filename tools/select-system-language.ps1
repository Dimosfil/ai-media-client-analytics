param(
    [string]$OutputPath = "tools/project-memory/system-preferences.json",
    [string]$Selection = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$available = @("Match user", "English", "Russian", "Spanish", "German", "French")
$languageAliases = @{
    "match" = "Match user"
    "auto" = "Match user"
    "user" = "Match user"
    "same" = "Match user"
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
$languageAliases[(-join ((0x0430,0x0432,0x0442,0x043E) | ForEach-Object { [char]$_ }))] = "Match user"
$languageAliases[(-join ((0x0430,0x043D,0x0433,0x043B,0x0438,0x0439,0x0441,0x043A,0x0438,0x0439) | ForEach-Object { [char]$_ }))] = "English"
$languageAliases[(-join ((0x0440,0x0443,0x0441,0x0441,0x043A,0x0438,0x0439) | ForEach-Object { [char]$_ }))] = "Russian"
$languageAliases[(-join ((0x0438,0x0441,0x043F,0x0430,0x043D,0x0441,0x043A,0x0438,0x0439) | ForEach-Object { [char]$_ }))] = "Spanish"
$languageAliases[(-join ((0x043D,0x0435,0x043C,0x0435,0x0446,0x043A,0x0438,0x0439) | ForEach-Object { [char]$_ }))] = "German"
$languageAliases[(-join ((0x0444,0x0440,0x0430,0x043D,0x0446,0x0443,0x0437,0x0441,0x043A,0x0438,0x0439) | ForEach-Object { [char]$_ }))] = "French"
$defaultSelected = "Match user"

if (Test-Path -LiteralPath $OutputPath) {
    try {
        $existing = Get-Content -LiteralPath $OutputPath -Raw | ConvertFrom-Json
        if ($existing.agent_response_language.mode -eq "fixed" -and $existing.agent_response_language.language) {
            $existingLanguage = [string]$existing.agent_response_language.language
            if ($available -contains $existingLanguage) {
                $defaultSelected = $existingLanguage
            }
        }
    }
    catch {
        Write-Host "Could not read existing preferences; using defaults."
    }
}

Write-Host "Select the agent working language for user-facing project messages."
Write-Host "This applies to agent-created task text and is separate from Git commit-message languages."
Write-Host ""

for ($i = 0; $i -lt $available.Count; $i++) {
    $language = $available[$i]
    $checked = if ($defaultSelected -eq $language) { "[x]" } else { "[ ]" }
    Write-Host ("{0} {1}. {2}" -f $checked, ($i + 1), $language)
}

Write-Host ""
if ([string]::IsNullOrWhiteSpace($Selection)) {
    $inputText = Read-Host "Selection"
}
else {
    $inputText = $Selection
}

$selected = $defaultSelected
if (-not [string]::IsNullOrWhiteSpace($inputText)) {
    $normalizedInput = $inputText.ToLowerInvariant() -replace "[^\p{L}0-9]+", " "
    foreach ($part in ($normalizedInput -split "\s+")) {
        $trimmed = $part.Trim()
        if ($trimmed -match "^[0-9]+$") {
            $index = [int]$trimmed - 1
            if ($index -ge 0 -and $index -lt $available.Count) {
                $selected = $available[$index]
                break
            }
        }
        elseif ($languageAliases.ContainsKey($trimmed)) {
            $selected = $languageAliases[$trimmed]
            break
        }
    }
}

if ($selected -eq "Match user") {
    $mode = "match_user"
    $language = ""
}
else {
    $mode = "fixed"
    $language = $selected
}

$config = [ordered]@{
    agent_response_language = [ordered]@{
        mode = $mode
        language = $language
        languages = if ($language) { @($language) } else { @() }
        project_environment_languages = if ($language) { @($language) } else { @() }
        task_language = $language
        task_languages = if ($language) { @($language) } else { @() }
        available = @("English", "Russian", "Spanish", "German", "French")
        applies_to = @(
            "progress_updates",
            "final_answers",
            "clarifying_questions",
            "user_facing_explanations",
            "plans",
            "checklists"
        )
        task_applies_to = @(
            "agent_created_task_titles",
            "agent_created_task_descriptions",
            "task_manager_updates"
        )
        exceptions = @(
            "existing_task_text",
            "code",
            "commands",
            "logs",
            "quoted_text",
            "user_requested_language"
        )
    }
}

$directory = Split-Path -Parent $OutputPath
if ($directory -and -not (Test-Path -LiteralPath $directory)) {
    New-Item -ItemType Directory -Path $directory -Force | Out-Null
}

$config | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $OutputPath -Encoding UTF8

Write-Host ""
Write-Host "Saved agent system language preferences to $OutputPath"
if ($mode -eq "fixed") {
    Write-Host "Agent working language: $language"
}
else {
    Write-Host "Agent working language: match the user's language"
}
