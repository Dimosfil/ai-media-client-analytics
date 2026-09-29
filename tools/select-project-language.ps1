param(
    [string]$SystemOutputPath = "tools/project-memory/system-preferences.json",
    [string]$GitOutputPath = "tools/project-memory/git-preferences.json",
    [string]$Selection = "",
    [string]$ProjectSelection = "",
    [string]$CommitSelection = "",
    [string]$TaskSelection = ""
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
$languageAliases[(-join ((0x0430,0x043D,0x0433,0x043B,0x0438,0x0439,0x0441,0x043A,0x0438,0x0439) | ForEach-Object { [char]$_ }))] = "English"
$languageAliases[(-join ((0x0440,0x0443,0x0441,0x0441,0x043A,0x0438,0x0439) | ForEach-Object { [char]$_ }))] = "Russian"
$languageAliases[(-join ((0x0438,0x0441,0x043F,0x0430,0x043D,0x0441,0x043A,0x0438,0x0439) | ForEach-Object { [char]$_ }))] = "Spanish"
$languageAliases[(-join ((0x043D,0x0435,0x043C,0x0435,0x0446,0x043A,0x0438,0x0439) | ForEach-Object { [char]$_ }))] = "German"
$languageAliases[(-join ((0x0444,0x0440,0x0430,0x043D,0x0446,0x0443,0x0437,0x0441,0x043A,0x0438,0x0439) | ForEach-Object { [char]$_ }))] = "French"
$defaultLanguageOrder = @("English", "Russian")

function Select-LanguageOrder {
    param(
        [Parameter(Mandatory = $true)][string]$Title,
        [Parameter(Mandatory = $true)][string[]]$DefaultSelected,
        [string]$InputText = ""
    )

    $default = @($DefaultSelected | Where-Object { $available -contains $_ } | Select-Object -Unique)
    if ($default.Count -eq 0) {
        $default = @($defaultLanguageOrder)
    }

    Write-Host ""
    Write-Host $Title
    Write-Host "Enter numbers or names in priority order, for example: 1 2"
    Write-Host ""

    for ($i = 0; $i -lt $available.Count; $i++) {
        $language = $available[$i]
        $checked = if ($default -contains $language) { "[x]" } else { "[ ]" }
        Write-Host ("{0} {1}. {2}" -f $checked, ($i + 1), $language)
    }

    if ([string]::IsNullOrWhiteSpace($InputText)) {
        $InputText = Read-Host "Selection"
    }

    if ([string]::IsNullOrWhiteSpace($InputText)) {
        return $default
    }

    $normalizedInput = $InputText.ToLowerInvariant() -replace "[^\p{L}0-9]+", " "
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

    $selected = @($selected | Where-Object { $_ } | Select-Object -Unique)
    if ($selected.Count -eq 0) {
        return $default
    }

    return $selected
}

$defaultProject = @($defaultLanguageOrder)
$defaultTasks = @($defaultLanguageOrder)
if (Test-Path -LiteralPath $SystemOutputPath) {
    try {
        $existing = Get-Content -LiteralPath $SystemOutputPath -Raw | ConvertFrom-Json
        if ($existing.agent_response_language.project_environment_languages) {
            $defaultProject = @($existing.agent_response_language.project_environment_languages | ForEach-Object { [string]$_ })
        }
        elseif ($existing.agent_response_language.languages) {
            $defaultProject = @($existing.agent_response_language.languages | ForEach-Object { [string]$_ })
        }
        elseif ($existing.agent_response_language.mode -eq "fixed" -and $existing.agent_response_language.language) {
            $defaultProject = @([string]$existing.agent_response_language.language)
        }

        if ($existing.agent_response_language.task_languages) {
            $defaultTasks = @($existing.agent_response_language.task_languages | ForEach-Object { [string]$_ })
        }
        else {
            $defaultTasks = $defaultProject
        }
    }
    catch {
        Write-Host "Could not read existing system preferences; using defaults."
    }
}

$defaultCommits = @($defaultLanguageOrder)
if (Test-Path -LiteralPath $GitOutputPath) {
    try {
        $existingGit = Get-Content -LiteralPath $GitOutputPath -Raw | ConvertFrom-Json
        $defaultCommits = @()
        if ($existingGit.commit_message_languages.primary) {
            $defaultCommits += [string]$existingGit.commit_message_languages.primary
        }
        if ($existingGit.commit_message_languages.additional) {
            $defaultCommits += @($existingGit.commit_message_languages.additional | ForEach-Object { [string]$_ })
        }
    }
    catch {
        Write-Host "Could not read existing git preferences; using defaults."
    }
}

if (-not [string]::IsNullOrWhiteSpace($Selection)) {
    $ProjectSelection = $Selection
    $CommitSelection = $Selection
    $TaskSelection = $Selection
}

Write-Host "Configure language order for this project."
Write-Host "You will choose: 1) project working environment, 2) commits, 3) tasks."

$projectLanguages = @(Select-LanguageOrder -Title "1. Project working environment language order" -DefaultSelected $defaultProject -InputText $ProjectSelection)
$commitLanguages = @(Select-LanguageOrder -Title "2. Commit message language order" -DefaultSelected $defaultCommits -InputText $CommitSelection)
$taskLanguages = @(Select-LanguageOrder -Title "3. Task language order" -DefaultSelected $defaultTasks -InputText $TaskSelection)

$systemConfig = [ordered]@{
    agent_response_language = [ordered]@{
        mode = "fixed"
        language = $projectLanguages[0]
        languages = $projectLanguages
        project_environment_languages = $projectLanguages
        task_language = $taskLanguages[0]
        task_languages = $taskLanguages
        available = $available
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

$commitAdditional = @($commitLanguages | Select-Object -Skip 1)
$gitConfig = [ordered]@{
    commit_message_languages = [ordered]@{
        primary = $commitLanguages[0]
        additional = $commitAdditional
        available = $available
        format = "selected_order"
    }
}

foreach ($path in @($SystemOutputPath, $GitOutputPath)) {
    $directory = Split-Path -Parent $path
    if ($directory -and -not (Test-Path -LiteralPath $directory)) {
        New-Item -ItemType Directory -Path $directory -Force | Out-Null
    }
}

$systemConfig | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $SystemOutputPath -Encoding UTF8
$gitConfig | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $GitOutputPath -Encoding UTF8

Write-Host ""
Write-Host "Saved language preferences."
Write-Host ("Project working environment: {0}" -f ($projectLanguages -join ", "))
Write-Host ("Commit messages: {0}" -f ($commitLanguages -join ", "))
Write-Host ("Tasks: {0}" -f ($taskLanguages -join ", "))
