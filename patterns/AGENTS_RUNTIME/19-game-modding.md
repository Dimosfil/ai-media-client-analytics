## Game Modding Projects

- Treat `gi mod`, `gi mod path`, `gi game path`, `gi mod game path`,
  `ги мод`, `ги мод путь`, `ги путь игры`, and equivalent wording as requests to
  prepare or inspect the current project as a game modding project.
- For modding work, distinguish at least four paths before editing, building,
  installing, or debugging: current mod project root, selected game install
  root, user/game documents mod folder, and logs or crash-report folder. Do not
  present one of these paths as another.
- Store the selected game install root in project-local ignored configuration,
  preferably `tools/project-memory/game-modding.local.json`, with non-secret
  fields such as `game_name`, `game_install_path`, `mod_install_path`,
  `logs_path`, `launcher`, `detected_from`, `verified_at`, and short evidence
  notes. Do not store machine-specific game paths in shared instructions,
  committed docs, source code defaults, migrations, or templates except as
  redacted placeholders.
- Add or keep `tools/project-memory/game-modding.local.json` ignored when the
  project records local game paths. Project memory may keep a portable modding
  contract, expected folder roles, build/install workflow, and evidence summary,
  but the absolute local install path belongs in ignored local config.
- If the user supplies `gi mod path <path>` / `ги мод путь <путь>` or explicitly
  says to record a game path, treat that path as user-authorized for this
  modding configuration task. Resolve it to an absolute path, verify it exists,
  and check for game-specific evidence such as an executable, launcher manifest,
  app manifest, modding SDK folder, data/content folder, or local runbook match.
  If verification is weak, record the path only with an explicit warning and
  missing evidence notes.
- If no game path is recorded, first search project-local instructions, README,
  runbooks, manifests, existing ignored modding config, and project memory for a
  selected game path. If still missing, inspect only safe common launcher library
  metadata when local policy and user scope allow it. Do not scan arbitrary user
  home folders, sibling projects, or whole drives unless the user explicitly
  asks to find the game on that scope.
- When the path is unknown and cannot be proven locally, ask one concise
  question for the game install root instead of saying only that the agent does
  not know. Include the exact local file where the answer will be saved, for
  example `tools/project-memory/game-modding.local.json`.
- For mod installation or debugging, verify the selected game path and the mod
  deployment/log paths before reporting readiness. If any required path is
  unknown, report the missing path by role and pause the state-changing action.
- Suggested prompt shape for a missing game path:
  `I found the mod project and local mod/log folders, but not the game install
  root. Please send the game install folder, and I will save it in
  tools/project-memory/game-modding.local.json for this project.`
- Russian prompt shape for a missing game path:
  `Я нашел проект мода и локальные папки мода/логов, но не доказал путь
  установки игры. Пришли папку установки игры, и я сохраню ее в
  tools/project-memory/game-modding.local.json для этого проекта.`
- Suggested prompt shape for recording a supplied path:
  `I will record this as the selected game install path for this mod project,
  verify it exists, keep it in ignored local config, and use it for future
  build/install/debug commands.`
- Russian prompt shape for recording a supplied path:
  `Запишу это как выбранный путь установки игры для этого мод-проекта, проверю
  что папка существует, сохраню в ignored local config и буду использовать для
  будущих build/install/debug команд.`
