# GI Command Contracts Maintenance Reference

This file preserves detailed accepted command wording for maintainers and
migration review. Runtime agents must resolve a specific command through
`config/gi-command-routes.json` and `tools/resolve-gi-command.ps1`; they must not
load this whole file as normal command context.

Command examples for working with the shared `general-instructions` kit.

For full policies, see `AGENTS.md`, `patterns/GIT_WORKFLOW.md`, and
`patterns/FIRST_MESSAGE_HANDLING.md`.

## Agent Execution Guard

Agents must treat entries in this file as chat commands, not shell commands.
Before executing any state-changing `gi ...` / `ги ...` command, read the
current project's `AGENTS.md` loading contract and the routed
`patterns/AGENTS_RUNTIME/` module for that command. If the routed module is
missing, stop and report the missing path instead of acting from memory.

For `gi restart`, `gi reboot`, `gi docker`, `ги рестарт`, `ги ребут`,
`ги докер`, and equivalent aliases, read
`patterns/AGENTS_RUNTIME/09-project-operation-commands.md` before any process
inspection, Docker build, stop, start, or success report.

Before any `gi` command writes files, agents must verify that the active project
root and target identity match the current request. If the request appears to
target another product, repository, or absolute path outside the current root,
stop and warn the user unless the current message explicitly authorizes that
exact external path and action.

## Команды Для Чата С Агентом

Префикс `gi` — короткая команда для локального instruction kit. Не
переименовывай в `GAI`. `gi` = `general-instructions`, не `git`.
Это команды для чата с агентом, не команды PowerShell. Если пользователь хочет
именно терминальную PowerShell-команду, он пишет `PS` или получает реальную
команду/путь к скрипту, например `.\tools\agent-start.ps1`.

```text
gi help
ги хелп
gi commands
gi ошибка
ги ошибка
gi ошибка фикс
ги ошибка фикс
ги команды
gi обновись
gi init https://github.com/Dimosfil/general-instructions.git
gi init Dimosfil/general-instructions.git
инит https://github.com/Dimosfil/general-instructions.git
init https://github.com/Dimosfil/general-instructions.git
инит <path-to-general-instructions>
инит правила <path-to-general-instructions>
gi язык
ги язык
gi язык: 1 2
ги язык: 1 2
gi language: Russian English
gi проект язык: Russian
ги проект язык: Russian
gi project language: Russian
gi язык проекта: Russian
gi коммит язык: Russian
ги коммит язык: Russian
gi язык коммита: Russian
gi язык коммита: English only
gi систем язык: Russian
ги систем язык: Russian
gi саммари
gi старт
gi restore
gi sql
gi sqlite
gi vector
gi info
ги инфо
gi stack
ги стек
gi logic
ги логика
gi logic <source> [focus]
ги логика <ссылка-или-путь> [фокус]
gi mod
ги мод
gi mod path <game-install-path>
ги мод путь <путь-игры>
gi build
gi собрать
gi rebuild
gi tools rebuild
gi rag rebuild
gi tools rebuild sql
gi rag rebuild sql
gi tools rebuild chunks
gi rag rebuild chunks
gi tools rebuild vector
gi rag rebuild vector
gi tools rebuild manifest
gi rag rebuild manifest
gi tools rebuild evals
gi rag rebuild evals
gi refactor
gi рефактор
ги рефактор
gi full refactor
ги билд
ги собрать
ги ребилд
ги тулс ребилд
ги раг ребилд
ги тулс ребилд sql
ги раг ребилд sql
ги тулс ребилд чанки
ги раг ребилд чанки
ги тулс ребилд вектор
ги раг ребилд вектор
ги тулс ребилд манифест
ги раг ребилд манифест
ги тулс ребилд тесты
ги раг ребилд тесты
gi config
gi config on
gi config off
gi конфиг вкл
gi конфиг выкл
gi конфиг он
gi конфиг офф
ги конфиг вкл
ги конфиг выкл
ги конфиг он
ги конфиг офф
gi config service
gi config service url=http://127.0.0.1:4100
gi config service on
gi config service off
gi prod
gi production
gi прод
ги прод
gi set devops
gi devops
ги девопс
gi deploy <method-or-path>
ги деплой <способ-или-путь>
gi ftp config
gi ftp <deploy-hub-path>
gi ftp
ги фтп конфиг
ги фтп <путь-к-deploy-хабу>
ги фтп
ги конфиг сервис on
ги конфиг сервис off
gi reboot
gi restart
gi docker
gi first test
gi default
gi defaults
ги дефолт
gi первый тест
ги первый тест
ги ребут
ги рестарт
ги докер
ги конфиг сервис урл=http://127.0.0.1:4100
gi install
gi local sprint
gi sprint local
gi локальный спринт
gi спринт локально
gi инсталл
ги инсталл
gi старт спринт
gi гит-обзор
gi git summary
gi тест-план
gi test plan
gi test task
ги тест таск
gi test
ги тест
gi tm
gi active task
gi next task
gi add sprint
gi create sprint
gi добавить спринт
gi manager test
gi tm test
gi план
gi post plan
gi пуш
gi коммит
gi только пуш
gi коммит пуш
gi пул
```

### GI Help / Command Index

```text
gi help
gi хелп
ги help
ги хелп
gi commands
gi команды
ги команды
```

`gi help` asks the agent to show a compact list of available GI chat commands
with short descriptions. The agent reads the local command index when present,
prefers project-local additions over this shared baseline, and does not run
startup restore, resume old work, call task managers, mutate files, or execute
the listed commands.

| Command | Description |
| --- | --- |
| `gi ошибка`, `ги ошибка`, `gi error` | Capture evidence for a suspected GI rule bug without fixing rules yet. |
| `gi ошибка фикс`, `ги ошибка фикс`, `gi error fix` | Repair the logged or supplied GI rule bug in the shared instructions. |
| `gi help`, `ги хелп`, `gi commands`, `ги команды` | Show the local GI command list with short descriptions. |
| `gi обновить`, `gi обновись` | Apply accepted instruction-kit updates and migrations. |
| `gi init <source>`, `инит <source>`, `инит правила <source>` | Bootstrap or restore shared instructions from `general-instructions`. |
| `gi start`, `gi старт`, `gi restore` | Restore minimal project context and ask for the current task. |
| `gi summary`, `gi саммари` | Write a thematic thesis-based handoff summary under `tools/summary/`. |
| `gi language`, `gi язык` | Configure project working-environment languages. |
| `gi project language`, `gi проект язык`, `gi язык проекта` | Configure project-facing language preferences. |
| `gi commit language`, `gi коммит язык`, `gi язык коммита` | Configure commit-message languages. |
| `gi system language`, `gi систем язык` | Configure agent working-response language. |
| `gi sql`, `gi sqlite` | Inspect SQLite/FTS project-memory readiness and metrics. |
| `gi vector` | Inspect semantic/vector retrieval readiness and metrics. |
| `gi info`, `ги инфо` | Find or build the current project's purpose, visible functionality, and stack overview. |
| `gi stack`, `ги стек` | Find or build the current project's verified technology stack inventory. |
| `gi logic`, `ги логика`, `gi logic <source> [focus]` | Find, document, or adapt core project logic; with a source path/URL, study that explicit external project narrowly and map portable logic into the current project. |
| `gi mod`, `ги мод`, `gi mod path <game-install-path>`, `ги мод путь <путь-игры>` | Prepare a game modding project by verifying and recording the selected local game install path separately from mod and log folders. |
| `gi build`, `gi собрать`, `ги билд`, `ги собрать`, `gi rebuild`, `ги ребилд` | Build/rebuild the current project/application only, producing a release/upload-ready artifact such as a static `dist/`, package, executable, or other documented build output. |
| `gi tools rebuild`, `gi rag rebuild`, `ги тулс ребилд`, `ги раг ребилд` | Rebuild the full configured GI/project-memory/RAG system after confirmation. |
| `gi tools rebuild sql`, `gi rag rebuild sql` | Rebuild only the SQL/FTS structured-memory node. |
| `gi tools rebuild chunks`, `gi rag rebuild chunks` | Rebuild only semantic chunk exports. |
| `gi tools rebuild vector`, `gi rag rebuild vector` | Rebuild only the vector retrieval node. |
| `gi tools rebuild manifest`, `gi rag rebuild manifest` | Rebuild only source manifest/inventory metadata. |
| `gi tools rebuild evals`, `gi rag rebuild evals` | Run configured RAG health and retrieval eval checks only. |
| `gi refactor`, `gi рефактор`, `ги рефактор` | Refactor the entire current project according to all applicable GI rules, in verified batches. |
| `gi config`, `gi config service` | Inspect config/discovery service settings. |
| `gi config on/off`, `ги конфиг вкл/выкл`, `ги конфиг он/офф` | Toggle config-service integration for the current project. New projects default to off; existing projects preserve their effective state. |
| `gi config service url=<url>` | Set the config-service URL after validation. |
| `gi config service on`, `gi config service off` | Toggle current app self-registration with config-service. |
| `gi prod`, `gi production`, `gi прод`, `ги прод` | Publish the current development version into the documented production service folder for a live online service. |
| `gi set devops`, `gi devops`, `ги девопс` | Mark the current project as the deploy-infrastructure owner so GI deploy-cleanup migrations keep gateway-owned deploy scripts/config there only. |
| `gi reboot`, `gi restart`, `ги ребут`, `ги рестарт` | Start or restart all documented project apps using local run instructions. |
| `gi docker`, `ги докер` | Restart the current project's documented Docker/Compose runtime, rebuilding first when local Docker state requires it. |
| `gi first test`, `gi первый тест` | Reset documented first-run state and verify first-launch experience. |
| `gi default`, `gi defaults`, `ги дефолт` | Restore the current project to documented first-run/default state. |
| `gi install`, `gi инсталл`, `ги инсталл` | Build/package the current project and verify an installer artifact; default target is Windows unless another platform is named. |
| `gi ftp config`, `gi ftp service`, `gi ftp folder` | Inspect or configure FTP/SFTP deployment settings without uploading. |
| `gi ftp`, `gi ftp push`, `gi deploy ftp`, `gi upload ftp` | Upload configured build output to the configured FTP/SFTP target. |
| `gi deploy <method-or-path>`, `ги деплой <способ-или-путь>`, `gi ftp <deploy-hub-path>`, `ги фтп <путь-к-deploy-хабу>` | Deploy the current project/site through the named method, saved deploy gateway, or user-provided deploy hub path. |
| `gi tm`, `gi manager` | Inspect the configured task manager through config-service. |
| `gi manager test`, `gi tm test` | Test the configured task manager contract and operations. |
| `gi active task`, `gi next task`, `gi get task` | Get executable work from the configured task manager. |
| `gi add sprint`, `gi create sprint`, `gi добавить спринт` | Create a visible Sprint/Cycle through the configured task manager. |
| `gi plan`, `gi план`, `gi post plan` | Send the current plan to the configured task manager. |
| `gi start sprint`, `gi старт спринт` | Take the active Sprint/Cycle into work through the configured task manager. |
| `gi local sprint`, `gi sprint local`, `gi локальный спринт`, `gi спринт локально` | Run a local sprint checklist without task manager or config-service sync. |
| `gi test plan`, `gi тест-план` | Build a verification plan from current project contracts. |
| `gi test task`, `ги тест таск` | Set the active release/full-system verification task for the current project. |
| `gi test`, `ги тест` | Run the documented full project verification flow against the active test task. |
| `gi git summary`, `gi гит-обзор` | Summarize the latest git commit without printing a full diff. |
| `gi commit`, `gi коммит` | Commit scoped changes. |
| `gi push`, `gi пуш` | Commit and push scoped changes. |
| `gi only push`, `gi только пуш` | Push the current branch without creating a commit. |
| `gi commit push`, `gi коммит пуш` | Commit and push scoped changes. |
| `gi pull`, `gi пул` | Fetch and pull the current branch. |

Если команда неполная, агент уточняет недостающий параметр.

Ответ на `gi` команду ограничен этой командой; агент не возвращается к
предыдущей задаче без явной просьбы.

Прогресс-апдейты должны быть по фазам, а не после каждого батча команд. Агент
не пишет счётчики вроде "выполнено 4 команды" и не ведёт live-blog каждой
промежуточной гипотезы. Сообщать стоит при смене фазы, значимом выводе,
блокере или долгой паузе.

Автоматические счётчики tool calls, которые показывает UI чата, не считаются
прогресс-апдейтами агента; агент не должен дублировать их текстом.

`gi` команда выполняется в текущем project root. Shared library читается
только как источник `VERSION.md`, `CHANGELOG.md`, `INDEX.md`, `migrations/` и
шаблонов. Отсутствие `.git` не блокирует проверку/применение GI-обновлений,
только commit/push.
На первом конкретном сообщении нового чата/сессии агент перед основной работой
тихо выполняет проверку `gi обновить`: читает локальную metadata instruction kit
и accepted source `VERSION.md`/`migrations/`, применяет pending accepted
migrations по локальному update contract, и сообщает только короткий статус или
blocker. Короткий статус должен явно назвать количество pending migrations,
включая `0`, если новых миграций нет. Эта авто-проверка не читает `updates/`,
старые chat examples, широкие деревья файлов или чужие проекты. Если source
недоступен, агент кратко сообщает blocker и продолжает по текущим локальным
правилам, кроме явной команды `gi обновить`.

`apps.txt`, планы, summary и записи task manager не дают разрешение читать
приватные локальные источники вне project root. Для анализаторов логов агент
использует mock/sample data или спрашивает явное разрешение на конкретный путь
и действие перед чтением `.codex`, `.cursor`, IDE logs, browser profiles, shell
history, SQLite databases или app logs.

Если нужный файл, skill, config, script, endpoint, task или другая сущность не
найдена, агент сначала перечитывает локальные инструкции, runbook, project
memory и принятые instruction-kit artifacts для текущей команды. Если после
этого сущность всё ещё отсутствует, агент задаёт один короткий вопрос
пользователю. Нельзя использовать другой проект или shared library как runtime
fallback без явного пути и действия от пользователя.

После успешного `gi обновить` / `gi обновись` агент коммитит и пушит только те
изменения instruction kit, которые создал сам update-flow, если это git
repository с настроенным remote и изменения касаются только instruction kit.
Команда не является просьбой пушить уже существующие локальные коммиты, синкать
feature branch, продолжать старый план или делать общее Git-обслуживание. Без
remote, при конфликте или unrelated changes — остановиться и объяснить блокер.

### GI Rule Error Intake And Fix

```text
gi ошибка
ги ошибка
gi error
gi ошибка фикс
ги ошибка фикс
gi error fix
```

`gi ошибка` / `ги ошибка` - команда intake для логической ошибки правил GI,
повторяющегося сбоя поведения агента или подозрения на rule gap. Агент собирает
только уже доступные доказательства: текст текущего чата, прикрепленные
скриншоты/файлы, видимый tool output и явно разрешенные локальные пути. Затем
делает privacy review, кратко формулирует symptom, likely violated rule or gap,
evidence summary и status, и записывает это в
`updates/USER_REPORTED_AGENT_BUG_LOG.md` shared library, если она доступна. Если
shared library недоступна, использует project-local intake folder such as
`tools/instruction-updates/`. Эта команда не чинит правила, не читает чужие
проекты и не запускает широкие поиски.

`gi ошибка фикс` / `ги ошибка фикс` - команда на ремонт. Агент читает newest
relevant unresolved bug-log entry и текущие доказательства, выделяет переносимый
rule gap, обновляет live rules, copied-project templates, accepted migration,
`VERSION.md` и `CHANGELOG.md`, проверяет scoped change, затем закрывает или
обновляет bug-log entry с migration/follow-up. В shared rules и migrations нельзя
переносить secrets, private screenshots, raw logs, private project data или
проектно-специфичные детали.

### Новый Проект

```text
Connect shared instructions: https://github.com/Dimosfil/general-instructions.git
инит [Dimosfil/general-instructions.git](https://github.com/Dimosfil/general-instructions.git)
```

Агент:
- сначала разрешает URL Markdown-ссылки и читает корневой `BOOTSTRAP.md`
- читает общие правила и нужные шаблоны
- создаёт локальные `AGENTS.md`, `tools/AGENT_WORKING_AGREEMENTS.md`,
  `tools/AGENT_RUNBOOK.md`, `tools/agent-start.ps1` и project memory files
- не добавляет shared library как dependency, submodule или symlink
- treats `gi init https://github.com/Dimosfil/general-instructions.git`,
  `gi init Dimosfil/general-instructions.git`, and Markdown links to that repo
  as GI instruction bootstrap, not as ordinary git repository initialization or
  remote replacement
- uses the active project root as the default target without requiring a
  machine-specific drive or local shared-library path
- prefers `tools/install-instruction-kit.ps1` from the resolved source checkout
  for deterministic fresh-project setup and preserves existing local files
- не трактует `инит <path-to-general-instructions>` или
  `инит правила <path-to-general-instructions>` как `git init`; не создаёт
  папки, `.git`, `npm init` или `python -m venv` для этой формы
- не спрашивает про языки коммитов при bootstrap
- останавливается после setup и спрашивает, что делать дальше

### Восстановить Контекст Проекта

```text
gi старт
gi restore
```

For `gi start` / `gi restore`, the agent reads the latest handoff summary as
the primary continuation artifact for a new chat. Reading only the summary
filename, timestamp, or metadata is not enough: the agent must recover the
current topic, key theses or decisions, blockers, and next useful direction,
then report that context compactly and ask what to do next. It still avoids
older summaries, full runbooks, logs, memory dumps, and diffs unless a concrete
task needs them.

Также: `gi start`, `gi восстанови`, `gi восстановить контекст`.

Агент восстанавливает контекст из `AGENTS.md`, последнего handoff summary и
`tools/agent-start.ps1`, затем кратко говорит статус и спрашивает, что делать
дальше. Не продолжает старую задачу автоматически.

Старые планы, фазы рефакторинга, заметки из памяти и локальные коммиты впереди
remote можно упомянуть только как компактный контекст. Нельзя превращать их в
предлагаемое следующее действие, если пользователь явно не попросил продолжить,
запустить, дописать или запушить именно это.

### Inspect Project Memory Retrieval

```text
gi sql
gi sqlite
gi vector
```

`gi sql` / `gi sqlite` asks the agent to inspect project-memory SQLite/FTS
readiness. The agent reads `tools/project-memory/rag-system.json`, runs local
stats helpers when available, counts memory/spec files, compares the numbers
with activation limits, and reports whether SQL indexing is absent, current,
stale, or recommended.

`gi vector` asks the agent to inspect semantic/vector readiness. The agent reads
embedding/vector metadata, checks semantic corpus size and chunk count, runs the
vector adapter status helper when available, and reports collection, records,
index path, freshness caveats, and readiness.

These are inspection commands by default. They do not deploy external services,
install heavy dependencies, upload data, or index private sources unless the
user explicitly asks and project-local rules allow it.

### Собрать Информацию О Проекте

```text
gi info
ги инфо
```

`gi info` / `ги инфо` asks the agent to find or build the current project's
orientation inventory: project purpose, target users or stakeholders,
user-visible functionality, common workflows, technology stack, and open
documentation gaps. The agent first reads project-local instructions, README,
docs indexes, runbooks, existing project-memory specifications, and the
canonical stack inventory when present. It verifies facts against current
manifests, config, run instructions, source entry points, and tests before
writing or reporting them.

If the collected facts already match the current documentation and canonical
stack inventory, the agent reports that the project information is already
current and does not rewrite files. If only part of the inventory changed, such
as the purpose, visible functionality, common workflows, commands, or stack,
update only the affected sections and leave current unchanged sections intact.
Avoid broad reformatting, wording churn, and whole-file rewrites when a scoped
section update is enough.

Write new or updated project information in the configured project working
environment languages from `gi язык` / `gi language`
(`tools/project-memory/system-preferences.json`). Preserve the selected order:
the first configured language is primary. If one language is configured, write
only that language; if multiple languages are configured, write the primary
language first and add one clear translation per additional configured language.
Do not use commit-message or task-manager language preferences for this project
documentation.

If the overview is missing or stale, the agent creates or updates the canonical
project documentation rather than storing the only description in chat or raw
project memory. Prefer `README.md`, `docs/`, and `tools/AGENT_RUNBOOK.md` for
the human-facing overview, visible functionality, commands, operations, and
troubleshooting. Keep or update the technology stack in the canonical stack
inventory, using `tools/project-memory/specs/technology-stack.md` unless local
instructions name another single source of truth. If implementation-driving
business rules, workflows, algorithms, or architecture contracts are discovered
or changed, link to the relevant project-memory specs instead of turning the
overview into the behavioral source of truth.

The command must keep facts evidence-backed. Mark unknown purpose, users,
features, commands, stack components, or runtime assumptions as gaps/TODOs with
evidence paths or missing-source notes. Do not install dependencies, start
services, rebuild indexes, call external APIs, read secrets, or inspect private
paths outside the project root unless the user explicitly approves that scope.

### Собрать Стек Технологий Проекта

```text
gi stack
ги стек
```

`gi stack` / `ги стек` asks the agent to find or build the current project's
technology stack inventory. The agent first looks for a visible project-local
stack source of truth: a top-level README/docs/runbook link near the beginning
of the file, `tools/project-memory/specs/technology-stack.md`, or an equivalent
linked architecture/stack note. If a current inventory exists, the agent reads
it, verifies the key facts against current manifests, lockfiles, config, run
instructions, and source entry points, then reports the stack and any gaps.

If no stack link or inventory exists, the agent creates or updates the canonical
inventory from current project evidence. Use
`tools/project-memory/specs/technology-stack.md` unless local instructions name
a different canonical docs path. Record languages, runtimes, frameworks,
package managers, build/test tools, storage, external services, commands,
evidence paths, and unknowns. For external agents starting outside the project,
the first pass should be able to find the stack pointer in the first relevant
project instructions or docs; when it is missing, add a concise link to the
canonical stack inventory in the appropriate top-level project doc if local
rules allow documentation edits.

This command is an inventory/documentation command. It must not install
dependencies, start services, rebuild indexes, call external APIs, read secrets,
or inspect private paths outside the project root unless the user explicitly
approves that scope.

### Project Logic Adoption

```text
gi logic
ги логика
gi logic <source> [focus]
ги логика <ссылка-или-путь> [фокус]
```

`gi logic` / `ги логика` asks the agent to recover the current project's core
logic and make it durable for future GI work. With no source argument, the
agent inspects only the current project and builds or updates a logic map in
project memory: core domain modules, workflow contracts, invariants, data
flows, integration boundaries, evidence paths, and verification gaps.

`gi logic <source> [focus]` / `ги логика <ссылка-или-путь> [фокус]` asks the
agent to study an explicitly named URL, repository, or local folder as a logic
source and adapt the relevant portable behavior into the current project. The
current project remains the write target unless the user explicitly says to
modify the source project. The source argument is permission for this scoped
logic-adoption task only; it is not permission to read secrets, local app data,
logs, databases, generated artifacts, unrelated sibling repositories, or broad
private folders.

The agent first states the active project root and external source, then reads
only task-relevant source instructions, README/docs, manifests, project-memory
specs, entry points, and focused source modules. If a focus term is supplied,
such as `client`, bot, worker, API, parser, billing, or another component or
workflow name, the agent searches for that focus before broad scans. It extracts
portable behavior contracts and module responsibilities before editing code;
it does not blindly copy another project's source or machine-specific config.

When implementation is requested or clearly implied, the agent adapts the
logic into the current project's architecture and configuration boundaries,
updates durable project memory with source/evidence mapping, and runs the
smallest documented checks that cover the adopted behavior. If the source is a
web URL, prefer official repository/docs pages and avoid crawling unrelated
pages or downloading large assets unless the user asks for that scope.

### GI Mod / Game Path

```text
gi mod
ги мод
gi mod path <game-install-path>
ги мод путь <путь-игры>
gi game path <game-install-path>
ги путь игры <путь-игры>
```

`gi mod` / `ги мод` asks the agent to prepare or inspect the current project as
a game modding project. Before editing, installing, building, or debugging a
mod, the agent must distinguish the current mod project root, the selected game
install root, the user/game documents mod folder, and the logs or crash-report
folder. The agent must not present a known mod folder or log folder as the game
install folder.

`gi mod path <game-install-path>` / `ги мод путь <путь-игры>` records the
selected local game install root for the current mod project. The supplied path
is user authorization for this scoped modding configuration task only. The
agent resolves the path to an absolute path, verifies it exists, and checks for
game-specific evidence such as an executable, launcher manifest, app manifest,
modding SDK folder, data/content folder, or project runbook match.

The selected game install path is machine-local configuration. Store it in an
ignored local file, preferably `tools/project-memory/game-modding.local.json`,
with non-secret fields such as `game_name`, `game_install_path`,
`mod_install_path`, `logs_path`, `launcher`, `detected_from`, `verified_at`,
and evidence notes. Do not commit absolute local game paths to shared
instructions, migrations, templates, source code defaults, or normal project
docs. Durable project memory may keep the portable modding workflow and the
roles of each folder, but not the user's machine-specific game path.

If the game path is not recorded, the agent first checks project-local
instructions, README, runbooks, manifests, existing ignored modding config, and
project memory. If still missing, the agent may inspect only safe common
launcher library metadata when local policy and user scope allow it. It must
not scan arbitrary user-home folders, sibling projects, or whole drives unless
the user explicitly asks to find the game on that scope.

If the game install root remains unknown, the agent asks one concise question
instead of merely saying it does not know. The question names the missing path
role and the exact save target, for example:

```text
I found the mod project and local mod/log folders, but not the game install root.
Please send the game install folder, and I will save it in
tools/project-memory/game-modding.local.json for this project.
```

Russian response shape:

```text
Я нашел проект мода и локальные папки мода/логов, но не доказал путь установки
игры. Пришли папку установки игры, и я сохраню ее в
tools/project-memory/game-modding.local.json для этого проекта.
```

When a path is supplied, the response should be concrete:

```text
I will record this as the selected game install path for this mod project,
verify it exists, keep it in ignored local config, and use it for future
build/install/debug commands.
```

Russian response shape:

```text
Запишу это как выбранный путь установки игры для этого мод-проекта, проверю что
папка существует, сохраню в ignored local config и буду использовать для будущих
build/install/debug команд.
```

### Build/Rebuild Project

```text
gi build
gi собрать
ги билд
ги собрать
gi rebuild
ги ребилд
```

`gi build` / `gi собрать` / `ги билд` / `ги собрать` / `gi rebuild` asks the
agent to build or rebuild the current project/application output. This is the
pre-release distributable intended for upload, hosting, or server publication
when the project defines such an artifact, such as a static `dist/`, bundle,
package, executable, or other documented build output. The agent reads
project-local build or rebuild instructions, manifests, scripts, hosting base
path/public-path config, and packaging metadata before running the documented
command.

This command does not mean dependency restore, tests-only verification, a
RAG-only rebuild, or a combined project-plus-RAG rebuild. It does not rebuild
GI/RAG indexes or tools, perform FTP/SFTP upload, publish to a production
folder, or produce an installer unless the project-local build contract
explicitly makes that part of the build artifact. If no project build/rebuild
contract exists, the agent asks one short clarification question instead of
inventing a command. Use `gi ftp` for upload, `gi prod` for documented
production publication, `gi install` for installer packaging, and
`gi tools rebuild` or `gi rag rebuild` when the GI/RAG layer itself must be
rebuilt.

### Docker Runtime

```text
gi docker
ги докер
```

`gi docker` asks the agent to restart the current project's documented
Docker/Compose runtime and decide whether a rebuild is needed before restart.
The agent first reads project-local run/deploy instructions, Dockerfile or
Containerfile, `compose.yaml`, `compose.yml`, `docker-compose*.yml`, container
scripts, manifests, service records, and project memory that define Docker
ownership and health checks.

If the project has no Docker/Compose config and no documented Docker run
contract, the agent reports that Docker is not configured for this project and
does not invent a container command. If Docker CLI, Docker Compose, or the
Docker engine is unavailable or not running, the agent reports that blocker
instead of treating the restart as complete.

The agent rebuilds before restart when the image is missing, the local Docker
contract says to rebuild, Dockerfile/Compose/build-context/dependency manifests
changed since the known running image, or the agent cannot confidently prove
that the current image matches the working tree. Prefer the project-documented
command when present; otherwise use the narrow Compose command for the project
such as `docker compose up -d --build`, letting Docker's cache no-op unchanged
layers. When the image is current and containers only need a restart, use the
documented restart/up command without a rebuild.

The command is scoped to the current project only. Do not prune Docker system
state, remove volumes, delete images, or stop unrelated containers. After the
operation, verify documented container status, health checks, mapped service
URLs, and recent logs when failures appear, then report rebuilt/restarted/not
configured/blocked status with evidence.

### Rebuild GI/RAG Tools

```text
gi tools rebuild
gi rag rebuild
ги тулс ребилд
ги раг ребилд

gi tools rebuild sql
gi rag rebuild sql
gi tools rebuild chunks
gi rag rebuild chunks
gi tools rebuild vector
gi rag rebuild vector
gi tools rebuild manifest
gi rag rebuild manifest
gi tools rebuild evals
gi rag rebuild evals
ги тулс ребилд sql
ги раг ребилд sql
ги тулс ребилд чанки
ги раг ребилд чанки
ги тулс ребилд вектор
ги раг ребилд вектор
ги тулс ребилд манифест
ги раг ребилд манифест
ги тулс ребилд тесты
ги раг ребилд тесты
```

`gi tools rebuild` / `gi rag rebuild` asks the agent to rebuild the whole
configured GI/project-memory/RAG retrieval system for the current project:
manifest/source inventory, SQLite/FTS or structured indexes, semantic chunk
exports, vector indexes, adapter metadata, and retrieval status/eval checks.

Full rebuild is heavy and requires explicit confirmation immediately before it
runs. Before asking, the agent reads `tools/project-memory/rag-system.json`,
lists configured rebuild nodes, generated paths that may be replaced, commands
or adapters that will run, and privacy exclusions. It does not index secrets,
private runtime data, ignored telemetry, or sources outside the project root.

Node forms such as `gi tools rebuild sql`, `gi rag rebuild chunks`,
`gi tools rebuild vector`, `gi rag rebuild manifest`, and
`gi tools rebuild evals` rebuild only that node through the command documented in
`rag-system.json` or the project-local runbook, then run the matching status
check. Retrieval evals should assert expected source evidence in top keyword,
semantic, or hybrid results rather than exact answer wording. If the node is
not configured, the agent asks one short clarification question instead of
inventing a command.

During `gi обновить`, the agent checks newly applied migrations. If a migration
changes RAG source rules, chunking, embedding metadata, SQLite/vector schemas,
retrieval adapters, or project-memory index scripts, the agent compares the
migration id with `rag-system.json` rebuild state. If affected nodes have not
been rebuilt for that migration, it reports the stale nodes and asks before the
full rebuild, or runs/offers the smallest documented node rebuild for narrow
migrations. Rebuild state is updated only after rebuild and readback/status
checks pass.

### Получить GI Config

```text
gi config
gi конфиг
ги конфиг
gi config on
gi config off
gi конфиг вкл
gi конфиг выкл
gi конфиг он
gi конфиг офф
ги конфиг вкл
ги конфиг выкл
ги конфиг он
ги конфиг офф
gi config service
ги конфиг сервис
gi config service url=http://127.0.0.1:4100
ги конфиг сервис url=http://127.0.0.1:4100
ги конфиг сервис урл=http://127.0.0.1:4100
```

`gi config on/off` / `ги конфиг вкл/выкл` / `ги конфиг он/офф` переключает использование
config-service текущим проектом. Явное состояние хранится как
`config_service.enabled` в `tools/project-memory/instruction-kit.json`. Новые
проекты создаются со значением `false`. Для совместимости отсутствие поля в
существующем проекте означает прежнее эффективное значение `true`; миграция не
должна записывать таким проектам `false`. При выключенном тумблере агент и
приложение не обращаются к config-service, не выполняют саморегистрацию и не
делают обычный локальный запуск зависимым от него, а используют только
документированный project-local runtime config. Команды, которым config-service
необходим по контракту, останавливаются с коротким блокером и предлагают
`gi config on`. Тумблер не запускает и не останавливает процесс config-service.
Любая короткая форма `gi config <toggle>` / `ги конфиг <тумблер>` без слова
`service` / `сервис` всегда управляет интеграцией целиком и никогда не означает
саморегистрацию. Только форма `gi config service <toggle>` /
`ги конфиг сервис <тумблер>` управляет саморегистрацией текущего приложения.

`gi config` без значения показывает явное и эффективное состояние тумблера,
включая legacy `true` при отсутствующем поле, затем URL и настройки
саморегистрации.

При включённом тумблере агент получает bootstrap-конфиг сервиса конфигов, а не
ищет runtime-конфиги в папках соседних проектов. Сначала читать project-local override, если он явно
задан локальными инструкциями, затем `config/gi-main.json` из checkout/cache
канонического source repo `https://github.com/Dimosfil/general-instructions.git`,
текущего checkout shared instructions или пути из `GENERAL_INSTRUCTIONS_HOME`.
Из GI main config взять `configServiceUrl` и проверить сам config-service через
его `/health` или документированный discovery endpoint.

`gi config service` / `ги конфиг сервис` — явное имя того же сценария. Для
runtime-адресов локальных приложений и task manager агент берёт из локального
проекта только имя или service id, затем запрашивает `GET /services/{serviceId}`
в config-service. После этого он использует `endpoints.availability` для
проверки доступности, `endpoints.guide` для агентского onboarding, когда этот
endpoint есть, `endpoints.contract` для актуального протокола и `endpoints.api`
для операций. Если guide и contract расходятся по endpoint, ownership или
permissions, агент останавливается и сообщает mismatch вместо догадок по
старой памяти, dashboard URL, filesystem paths или raw receipts.

`gi config service url=<url>` / `ги конфиг сервис url=<url>` /
`ги конфиг сервис урл=<url>` задаёт canonical URL config-service для текущего
окружения, например
`http://127.0.0.1:4100`. В shared instruction library агент обновляет
`config/gi-main.json`; в проекте с явным local override обновляет только этот
override. Все локальные сервисы используют этот URL, чтобы регистрироваться в
config-service и читать discovery. URL должен быть полным `http://` или
`https://` адресом без секретов, токенов, query string и fragment.

Если GI main config или config-service недоступен, остановиться с коротким
блокером. Не подбирать порты, не сканировать sibling workspace roots, не читать
другие project roots и не использовать старые task-manager записи как замену
config-service.

### Проверить Первый Запуск

```text
gi first test
gi default
gi defaults
ги дефолт
gi первый тест
ги первый тест
```

Агент проверяет сценарий первого запуска текущего приложения. Сначала он читает
project-local run, test, cleanup и cache reset инструкции, manifests и config
entry points, затем останавливает или перезапускает только процессы текущего
проекта, если это требуется для безопасного сброса.

Сброс включает только задокументированные project-owned кеши, временные профили,
локальные настройки приложения, generated state и другие rebuildable данные,
которые проект явно относит к first-run state. Не удалять пользовательские
документы, production данные, секреты, credentials, внешние сервисные данные,
общие системные кеши, sibling project folders или произвольные user-home
папки. Если локальные инструкции не называют точные paths, keys, commands или
reset script, агент задаёт один короткий вопрос вместо угадывания.

После сброса агент запускает приложение как при первом использовании,
проверяет documented smoke checks или onboarding/first-run workflow и сообщает,
что именно было очищено, какие проверки прошли и какие данные намеренно не
трогались.

### Restore Project Defaults

```text
gi default
gi defaults
ги дефолт
```

The agent restores the current project to its documented first-run/default
state. This is broader than `gi first test`: it may clear project-owned app
state, generated caches, local settings, onboarding flags, temporary profiles,
runtime logs, queues, worker state, generated test databases, browser storage
for the app origin, and other rebuildable state that local instructions
explicitly define as safe to reset. Preserve only exclusions explicitly
documented by the current project; old chat, screenshots, previous run
artifacts, and browser state do not create reset exceptions.

Before clearing anything, the agent reads project-local reset, cleanup,
first-run, run, backup, and test instructions. If the project provides a reset
script or contract, use that documented flow. If reset targets are not
documented, ask one short clarification question instead of guessing paths.

Do not delete source files, project memory specifications, instruction-kit
files, user documents, production data, secrets, credentials, external service
data, shared system caches, sibling projects, or arbitrary user-home folders.
If a reset would be irreversible or could remove user-owned data, stop for
explicit confirmation and prefer a backup or rename step when local rules allow
it.

After reset, start the project through documented run instructions and verify
the default or first-launch success signals. Report what was reset, what was
left untouched, what verification passed, and any blocker that prevented a full
clean-slate restore.

### Собрать Билд И Инсталлятор

```text
gi install
gi инсталл
ги инсталл
gi install Inno Setup
gi инсталл Inno Setup
gi инсталл <программа>
gi install macOS
gi install Android
```

Также распознавать очевидные опечатки вроде `gi иснтлл`, если намерение
собрать installer ясно из контекста.

Агент собирает production build и установочный файл для текущего проекта.
Если целевая платформа не указана, по умолчанию собирать Windows installer.
Для Windows, если программа не указана, по умолчанию использовать Inno Setup:
найти project-local build/package инструкции, скрипты и `.iss` файл, затем
собрать приложение и installer. Если после команды указана программа,
использовать её как предпочитаемый packaging/installer tool вместо Inno Setup.
Если пользователь явно называет macOS, iOS, Android, Linux или другую
платформу, либо такая платформа задана project-local packaging contract,
следовать соответствующему локальному контракту сборки/подписи/пакетирования.
Если указанная платформа поддерживается проектом, но нужный packaging contract
не найден или неоднозначен, задать один короткий уточняющий вопрос вместо
переключения на Windows по умолчанию.

Для каждой целевой платформы держать отдельную project-local папку. В ней
должны лежать или быть явно связаны инструкции сборки, packaging configs,
signing/notarization/provisioning notes, verification notes и текущие installer
artifacts для этой платформы. Если проект уже задаёт свой layout, следовать
ему; если агент создаёт или исправляет packaging layout, использовать
платформенные подпапки вроде `packaging/windows/`, `packaging/macos/`,
`packaging/ios/`, `packaging/android/`, `packaging/linux/` или эквивалентные
project-local имена. Не смешивать artifacts разных платформ в одной общей
папке без per-platform manifest.

Перед packaging агент определяет версию приложения из project-local metadata:
manifests, package files, assembly attributes, release files или installer
configs. Агент обновляет версию в production build, installer metadata и имени
installer-файла или installer-артефакта, если локальные инструменты это
поддерживают. Если versioning contract отсутствует или неоднозначен, агент
задаёт один короткий уточняющий вопрос вместо изобретения версии.

Перед сборкой агент проверяет локальные инструкции, README, manifests и
существующие packaging scripts/configs. Если build или installer contract не
найден, агент задаёт короткий уточняющий вопрос вместо изобретения installer
конфига без опоры на проект. `restore`, dependency install, build и test
являются только предварительными проверками: они не завершают `gi install`,
пока packaging command не выполнена и текущий installer artifact не создан или
явно не проверен. Если агент выполнил только проверки, он сообщает именно это
и не называет проект установленным/восстановленным. После успешного packaging
агент кратко сообщает версию, путь к инсталлятору и выполненные проверки.

### Взять Активный Sprint В Работу

```text
gi старт спринт
```

Также: `gi start sprint`, `gi sprint start`, `gi активный спринт`,
`gi work sprint`.

Агент восстанавливает контекст, затем через настроенный task manager находит
активный sprint и выполняет задачи по порядку. Если sprint'ов 0 или >1 —
показать варианты и спросить.

Before starting sprint workflow, verify that the configured manager API endpoint
supports active sprint lookup, next-task lookup, and task completion for the
selected workflow. If only generic health works, stop before executing tasks.
This command is more specific than plain `gi start`; do not answer it with only
generic startup restore when a configured task-manager workflow is available.

### Run Local Sprint Checklist

```text
gi local sprint
gi sprint local
gi локальный спринт
gi спринт локально
```

Use this when the user wants sprint-shaped work without a configured task
manager or config-service. The agent uses sprint content from the current
message, current chat context, or a project-local checklist file explicitly
named by local instructions. If no sprint content is available, ask one short
question for the sprint goal and task list.

This command is not a task-manager workflow. Do not resolve config-service,
create raw manager intake, edit task-manager internals, or claim that a visible
Sprint/Cycle was created, started, completed, or synchronized. If the user asks
for `gi start sprint` and the manager/config-service setup is missing, report
that blocker and mention `gi local sprint` as the explicit local alternative.

### Проверить Обновления Инструкций

```text
Обновись из https://github.com/Dimosfil/general-instructions.git
```

Если локального kit ещё нет — bootstrap/init. Если уже есть — применить
только недостающие миграции. Использовать `VERSION.md`, `CHANGELOG.md` и
`migrations/`, не читать `updates/`.

`gi обновить` тихий по умолчанию: без прогресс-нарратива, без широких чтений,
без повторяющихся статусов. Только компактный результат: версии до/после,
количество миграций, ID применённых, изменённые файлы, проверки, commit/push.

`gi обновить` применяет принятые instruction-kit миграции. Не предлагать пушить
локальные коммиты, которые существовали до обновления, и не подменять команду
git-синхронизацией проекта.

Если после обновления впервые стал доступен task-manager plan sync, но
`tools/project-memory/task-managers.json` отсутствует или не содержит
включенных менеджеров, сразу предложить plain inline numbered checkbox marker checklist с
доступными адаптерами и `none`. Не подключать WorkNest или другой менеджер
автоматически.

Если локальный checkout/cache path недоступен — использовать `source_repo` из
metadata, URL из команды, текущий checkout/cache shared instructions или
`GENERAL_INSTRUCTIONS_HOME`. Локальный путь хранить только как cache/checkout,
а канонический источник брать из GitHub repo.

### Настроить Язык Проекта

```text
gi язык
ги язык
gi язык: 1 2
ги язык: 1 2
gi language: Russian English
gi проект язык: Russian
ги проект язык: Russian
gi project language: Russian
gi язык проекта: Russian
ги язык проекта: Russian
```

Это основной способ выбрать языки проекта. Команда задаёт три выбора с одним и
тем же списком языков:

1. Project working environment: общение, progress updates, финальные ответы,
   уточняющие вопросы, планы и checklists.
2. Commit messages.
3. Tasks: task titles, task descriptions и task-manager updates.

В каждом выборе можно указать один или несколько языков; порядок важен. Первый
выбранный язык становится основным для этой поверхности, второй — вторым
языком, и так далее. Агент обновляет
`tools/project-memory/system-preferences.json` и
`tools/project-memory/git-preferences.json`.

Если команда пришла без выбора, агент показывает три последовательных выбора.
Если у одной из трёх поверхностей ещё нет текущего выбора, агент использует
дефолт `1 2`: `English`, затем `Russian`.
Если язык указан сразу после команды, агент использует этот порядок для всех
трёх поверхностей, пока пользователь не задаст отдельные значения.

В чатовой форме каждый из трёх выборов показывается как короткий нумерованный
plain inline numbered checkbox marker checklist с одним и тем же списком языков и текущими отметками.
Пользователь может ответить номерами или названиями языков. Если пользователь
отвечает только числами, например `1 2`, агент применяет их к последнему
показанному списку и сохраняет этот порядок для текущего этапа, не уточняя
повторно, какие языки соответствуют числам.
Перед первым выбором агент показывает короткий блок текущих настроек для всех
трёх поверхностей. В каждый список добавляется вариант `Cancel / Отмена`; если
пользователь выбирает его или отвечает `cancel`/`отмена`, агент завершает
настройку без изменения файлов предпочтений.

Пример первого этапа:

```markdown
Current settings:
- Project working environment: English, Russian
- Commit messages: English, Russian
- Tasks: English, Russian

1/3. Project working environment language order

Reply with numbers or language names in priority order, or choose cancel.

[x] 1. English
[x] 2. Russian
[ ] 3. Spanish
[ ] 4. German
[ ] 5. French
[ ] 6. Cancel / Отмена
```

Настройка не переводит уже существующий текст задач, код, команды, логи,
цитаты или язык, который пользователь явно попросил для конкретного ответа.
Если пользователь не называет язык, агент показывает короткий Markdown
checklist с доступными языками и текущим выбором.

Если пользователь явно хочет настроить язык проекта вручную, можно запустить:

```powershell
.\tools\select-project-language.ps1
```

или:

```powershell
.\tools\agent-start.ps1 -ConfigureProjectLanguage
```

### Настроить Языки Коммитов

```text
gi коммит язык: Russian
ги коммит язык: Russian
gi commit language: Russian
gi язык коммита: Russian
gi язык коммита: English only
```

Это старая настройка языка commit-сообщений. По умолчанию `English` без
дополнительных языков. Агент обновляет
`tools/project-memory/git-preferences.json` сам и кратко подтверждает. Если
пользователь не называет языки, агент показывает plain inline numbered checkbox marker checklist с текущим
выбором и пояснением, что `English` обязателен.

### Настроить Системный Язык Агента

```text
gi систем язык: Russian
ги систем язык: Russian
gi system language: Russian
```

Это настройка языка работы агента в проекте: progress updates, финальные
ответы, уточняющие вопросы, пользовательские объяснения, task titles, task
descriptions, task-manager updates, планы и checklists. Агент обновляет
`tools/project-memory/system-preferences.json` сам и кратко подтверждает. Эта
настройка не меняет язык commit-сообщений, код, команды, логи, цитаты или язык,
который пользователь явно попросил для конкретного ответа.

### Git Finish Commands

Правило проекта «обычно коммит делает пользователь» не отменяет явные команды
Git-finish ниже. Если проект безусловно запрещает агенту коммиты, `gi пуш`
блокируется; его нельзя заменить push-only действием или советом сделать
коммит вручную и повторить ту же команду.

```text
gi пуш            # commit + push
gi коммит          # commit только
gi только пуш      # push без commit
gi коммит пуш      # commit + push (алиас gi пуш)
gi пул            # fetch + pull текущей ветки
```

Перед любым commit/push агент проверяет `git status --short`, staged/unstaged
changes, remote и ветку. Коммитит только изменения текущей задачи или
явно указанного scope. Scope берётся только из активной задачи текущего диалога
или явно выбранного пользователем набора изменений; видимое сходство dirty-файлов
не позволяет объявлять их одним пакетом. При неоднозначном scope агент
останавливается до staging и любых записей. `gi пуш` нельзя подменять сырым `git push`, повтором
предыдущего terminal push или push-only действием; если scoped изменений для
commit нет, агент сообщает это вместо push-only fallback. Push без нового
commit выполняется только по `gi только пуш`. Git-finish сам по себе не
разрешает новую реализацию, переписывание ожиданий тестов, удаление runtime-state,
изменение зависимостей, перезапуск/пересборку сервисов или широкий cleanup ради
успешной проверки. Ошибка проверки исправляется только когда её вызвали scoped
изменения и исходная задача уже разрешает такое исправление; иначе это blocker.
При блокерах — кратко объясняет. Если у текущей ветки нет upstream, агент до
staging/commit уточняет целевую удалённую ветку и при первом push настраивает
tracking. Совпадение текущего HEAD с другой удалённой веткой не определяет
направление отправки.
Контракты project-memory обновляются во время разработки функционала, а не
проверяются заново по команде Git-finish. `ги пуш` выполняет commit и push
подготовленного scope с компактными проверками Git; отдельную разработку,
аудит продуктовой логики и цикл продуктовых тестов команда не запускает.
Все task-scoped записи, включая handoff и generated metadata, завершаются до
staging. После последнего commit/push и последней записи агент снова
проверяет `git status --short`, а для push — и совпадение с upstream. Совпадение HEAD
не доказывает чистое working tree: при новом task-scoped diff нельзя сообщать о
полном успехе. После final status check tracked task-файлы не меняются без повтора
разрешённого finish workflow и проверки.

Для `gi пул` агент проверяет состояние рабочей копии, текущую ветку и upstream,
затем делает `git fetch` и подтягивает текущую ветку. Если появляются
конфликты, агент сначала оценивает их по затронутым файлам и решает только
очевидные, низкорисковые конфликты, сохраняя пользовательские изменения. Если
конфликт требует продуктового решения, затрагивает чужие или секретные файлы,
или его нельзя решить уверенно, агент останавливается и обращается к
пользователю с кратким описанием вариантов.

### Записать Handoff Summary

```text
gi саммари
```

Создаёт `tools/summary/YYYY-MM-DD_HH-mm-ss_AGENT_WORK_SUMMARY.md` по
структуре из `templates/SUMMARY.template.md`. Summary фиксирует смысл треда:
намерение пользователя, решения, изменения кода/архитектуры/бизнес-логики,
проверки, блокеры и следующий полезный контекст. Summary строится как
тематический handoff, а не короткий пересказ подряд: агент разбивает тред на
смысловые темы, выделяет тезисы внутри каждой темы, кратко описывает тезисы и
добавляет детали только там, где сложная тема потеряет контекст без них. Ссылки
на кодовые файлы, URL, медиа, картинки, логи, скриншоты или точные артефакты
оставляются только когда они нужны для понимания или проверки контекста.
Для архитектурных и research-тредов, особенно когда пользователь оценивает
внешний проект, статью, паттерн или инструмент как возможную цель интеграции,
summary явно сохраняет намерение пользователя, маппит внешние концепты на
текущие компоненты проекта и разделяет решения и гипотезы.
Рутинные успешные `gi push`,
`gi commit`, staging counts, git directives, branch/push metadata и commit hash
не записываются, если их можно восстановить из git logs или command history.
Если нужен подробный протокол, он пишется отдельно как `Thread Timeline`, а не
подмешивается в обычный handoff summary.

Когда пользователь спрашивает, на чём остановились в прошлом треде, агент
сверяет handoff summary с последним видимым выводом треда, скриншотами или
цитатами пользователя. Приоритет у последнего явного архитектурного/продуктового
решения, открытого вопроса или согласованного направления, а не у случайного
caveat из summary. Непроверенный env/config caveat, пропущенный check или
старый next-step bullet не становятся текущей задачей сами по себе.

### Собрать Обзор Последнего Git-Коммита

```text
gi гит-обзор
gi git summary
```

Агент показывает hash, дату, автора, тему, изменённые файлы (компактно),
предполагаемый смысл и заметные риски. Без полного diff, без создания
summary-файла, без commit/push.

### Составить План Тестирования

```text
gi тест-план
gi test plan
```

Агент изучает локальные инструкции, скрипты и тестовую структуру, выдаёт
компактную "лестницу проверок": syntax checks → unit → integration → smoke →
manual → regression. По умолчанию планирует без запуска, если пользователь не
просит запустить.

Перед рекомендацией или запуском smoke/API/CLI checks агент сверяет точные
commands, flags, ports, routes, methods, JSON payload fields и env vars с
текущими project-local instructions, README, manifests, config или source code.
Summary, screenshots и старый чат считаются evidence/status, а не
authoritative command contract.

Для новой фичи: expected behavior, failure paths, edge cases, rollback, что
проверено, что требует ручной проверки.

### Full Project Test

```text
gi test task <release/full-system test task>
ги тест таск <release/full-system test task>
gi test
ги тест
```

`gi test task` sets the active verification workload for the current project.
The task text is the selected scenario for the next `gi test`, not proof that
the scenario has already passed. Use the project-local test-task location when
local instructions define one; otherwise keep the task in current chat context
and say where it is tracked.

`gi test` runs the documented full verification flow against the active test
task. It is different from `gi test plan`: `gi test plan` plans by default,
while `gi test` runs. Before running, the agent rereads current local
instructions, README, manifests, runbooks, test configs, and source entry
points needed to verify exact commands, services, app set, ports, routes,
payloads, environment, storage, auth, queues, workers, and health checks.
Before the live checks, the agent must reset project-owned runtime state to the
documented default/factory baseline, preserving only exclusions explicitly
documented by the current project. Browser storage, generated databases, logs,
queues, temporary workers, app caches, and similar rebuildable state are cleared
unless the project-local reset contract lists them as exceptions. If reset
targets or safe exceptions are undocumented, report that blocker instead of
running a dirty-state test.

After reset, selected chain/preset/execution mode, ports, task, and service
endpoints must be read from the project-local source of truth such as config
files, backend state, service discovery, or database metadata. Browser
`localStorage` is only UI cache; it cannot be the source of truth for `gi test`.

For `gi test`, dry-run mode is not a valid result. Do not report `--dry-run`,
simulation mode, dispatcher-only execution, replayed logs, mock-only runs, or
compile/unit-only checks as a passed `gi test`, and do not run dry-run mode at
all unless the user explicitly asks for that diagnostic mode. A full test must
exercise the documented live runtime surface for the selected task: apps,
backend/API, storage, queues/workers, UI/auth, service discovery, orchestrator
or agent handoff loops, and health/contract endpoints when the project defines
them. If the live system cannot be started or reached, report the full test as
blocked or not checked.

Old summaries, screenshots, completed demo artifacts, previous task statuses,
and old chat snippets are evidence only. They do not satisfy a fresh `gi test`
request; rerun the current documented checks or report the exact blocker.

### Full Project Refactor

```text
gi refactor
gi рефактор
ги рефактор
gi full refactor
```

The agent treats this as approval to refactor the entire current project
according to all applicable GI rules, not as a proposal-only request. Before
editing, it reads project-local instructions, README, manifests, architecture or
runbooks, project-memory specifications, connected-project registers, and
relevant test/build contracts. It creates a concise refactor plan covering
architecture boundaries, configuration boundaries, hard-coded deploy/user/runtime
values, development-tool versus generated-product boundaries, SOLID/DRY/clean
code, duplicated business logic, oversized modules, dependency direction, typed
or validated contracts, tests, and project-memory updates.

The agent works in small verifiable batches and preserves user-visible behavior
unless the user explicitly changes it. It separates structural refactor work
from development work such as new behavior, validation, observability,
integrations, runtime flows, or new public contracts; verification and service
operations stay labeled separately too. It asks before destructive operations,
data migrations, public API or storage contract changes, dependency
replacements, broad formatting-only churn, or private/external paths. After
meaningful batches, it runs documented checks for affected areas, updates
durable project-memory specs for behavior or architecture changes, avoids
committing generated/rebuildable artifacts unless local rules require them, and
reports remaining risks or continuation batches.

### Настроить Task-Manager Plan Sync

```text
gi tm
```

Агент проверяет `tools/project-memory/task-managers.json`. Если менеджеры уже
есть — обновляет skill/config из shared kit. Если нет — показывает checklist
доступных адаптеров и `none`. После выбора создаёт конфиг и заполняет
обязательные поля. В конфиге task manager хранится имя или service id менеджера
и project-local preferences; runtime URL агент получает через config-service по
этому service id.

Task-manager commands are routine sync/execution commands once the user has
provided the sprint/task content or selected the workflow. They are suitable for
fast or weaker models only if the model still follows the manager guide and
contract exactly: resolve service id, verify capabilities, send the documented
payload, read back lifecycle identifiers, and stop with the exact blocker when
that cannot be done. Do not replace the manager operation with
`project-memory`, pending-task notes, raw intake receipts, guessed commands,
local checklists, or a request for the user to provide the exact manager
command.

### Test Current Task Manager

```text
gi manager test
gi tm test
gi манагер тест
gi менеджер тест
```

The agent tests the configured task manager end to end in the current project:
resolve the manager service id through config-service, read the manager contract,
create a disposable no-op task through the documented API entry point, load/read
it back, take it in work when the adapter supports that lifecycle step, complete
it as `done`, read the final status, and report the manager id, resolved service
endpoint, task id or URL, completed lifecycle steps, and any missing capability.
The test must not edit repository files, touch secrets, perform destructive
actions, or use another project folder.

### Get Active Task From Task Manager

```text
gi active task
gi next task
gi get task
```

The agent gets executable work from the configured task manager, not from raw
intake receipts or guessed UI routes. It resolves the manager through
config-service, reads the contract, requests the active task first when
supported, otherwise requests the next task through the documented operation,
marks it in progress when supported, executes the task, and sends progress,
blocker, or completion notes back to the manager.

If project config-service integration is disabled, all manager-backed commands
stop with that blocker and point to `gi config on`; they do not use stale or
guessed manager endpoints.

For WorkNest, external agents use `/agent-intake/...` API operations. They do
not move Markdown files, edit internal statuses, archive tasks, or rely on an
old local URL instead of resolving `service_id: worknest` through config-service.

If the manager cannot return lifecycle identifiers, cannot update status, or
the requested object type is blocked by auth/permissions, the agent stops and
reports the exact blocker. It must not create a different object type, raw
intake record, or local checklist note as a substitute for the requested
manager object.

### Add Sprint To Task Manager

```text
gi add sprint
gi create sprint
gi добавить спринт
```

The agent creates a visible executable Sprint/Cycle in the configured task
manager. It resolves the manager through config-service, reads the contract, and
uses only the documented sprint/cycle creation operation or the adapter's
documented executable plan payload. After creation it reads the sprint/cycle
back and reports the lifecycle identifiers or URL.

If the manager only accepts raw intake, or the sprint/cycle endpoint returns an
auth, permission, schema, routing, or object-type error, the agent stops and
reports the blocker. It must not create a Work Item, raw receipt, local
checklist, or one-task plan as a substitute for the requested Sprint/Cycle.

### Отправить План В Task Manager

```text
gi план
gi post plan
```

Агент отправляет текущий план в подключенный task manager. Если менеджер не
настроен — сначала выполняет setup flow как `gi tm`. Если план не дан в
сообщении и не найден в контексте — спрашивает.

Для WorkNest: `POST /agent-intake/raw`. Ответ intake — квитанция, не
подтверждение создания карточки. Before sending, verify raw intake capability,
not only `/health`.

## PS PowerShell Commands

For when you want to run helpers yourself from a bootstrapped project root.
Only commands in this section are meant to be run literally in PowerShell.

### Startup

```text
.\tools\agent-start.ps1
.\tools\agent-start.ps1 -ConfigureGitCommitLanguages
.\tools\agent-start.ps1 -ConfigureSystemLanguage
```

### Configure Commit Languages

```text
.\tools\select-git-commit-languages.ps1
```

### Configure Agent System Language

```text
.\tools\select-system-language.ps1
```

### Check Instruction Updates

```text
.\tools\check-instruction-kit-updates.ps1
.\tools\check-instruction-kit-updates.ps1 -VerboseOutput
.\tools\check-instruction-kit-updates.ps1 -RecordApplied   # только после применения и верификации
```

`-Apply` не является metadata-only shortcut. Применяй файлы миграций до
записи metadata.

### Maintain This Library

```powershell
git diff --check
git diff --stat
git status --short
```

## Команды Для Чата С Агентом: Runtime

### Production Service And FTP Deploy

```text
gi prod
gi production
gi прод
ги прод
gi set devops
gi devops
ги девопс
gi deploy <method-or-path>
ги деплой <способ-или-путь>
gi ftp config
gi ftp service
gi ftp folder
gi ftp push
gi ftp <deploy-hub-path>
gi ftp
ги фтп конфиг
ги фтп сервис
ги фтп папка
ги фтп пуш
ги фтп <путь-к-deploy-хабу>
ги фтп
gi upload ftp
gi deploy ftp
gi zaley na ftp
gi залей на фтп
```

`gi prod` / `gi production` / `gi прод` / `ги прод` publishes the current
development version into the documented production service folder for an online
service connected to real remote APIs. It is for continuously running services
such as bots, webhook workers, marketplace connectors, payment integrations, or
other live external integrations.

The agent first reads project-local production/deploy instructions, service
contracts, production folder config, secret-handling rules, ignore rules,
restart or switchover commands, health checks, and rollback requirements.
Normal development, refactoring, tests, cleanup, formatting, and `gi restart`
operate on the development checkout/service and must not edit, stop, reset, or
test inside the production service folder unless the user explicitly invokes
the production workflow or local instructions define a stricter command.

The production folder is a live runtime target, not the editable source of
truth. During `gi prod`, build or prepare the documented artifact from the
development checkout, sync only approved source/build files into the production
folder, preserve production-local `.env`, secrets, databases, sessions, logs,
caches, service-manager files, webhook/API state, and user data, and use a
backup, rollback, or atomic handoff when available. Never copy production
secrets or runtime data back into development. If the production folder,
include/exclude rules, restart/switchover command, health check, or rollback
path is undocumented, ask one concise clarification question instead of
guessing. Follow `patterns/PROJECT_DEV_PROD_SERVICES.md`.

`gi set devops` / `gi devops` / `ги девопс` marks the current project as the
deploy-infrastructure owner for GI migrations and deploy commands. The agent
verifies the active project identity first, then creates or updates an ignored
local marker such as `tools/project-memory/devops.local.json` with non-secret
metadata: role `deploy-owner`, timestamp, reason, and optional deploy entrypoint
or gateway contract pointer. This marker tells future GI updates not to remove
gateway-owned direct deploy scripts or FTP/SFTP config from this project. It
does not authorize reading unrelated projects, exposing secrets, editing
private gateway config from a consuming project, or treating any unmarked
project as deploy infrastructure.

`gi deploy <method-or-path>` / `ги деплой <способ-или-путь>` deploys the current
project or site through the explicitly named method, service, saved deploy
gateway, or deploy hub path. If the argument is an absolute or clearly
project-local path, treat that directory as a user-authorized external deploy
gateway and record it as the current project's selected deploy gateway in an
ignored local file such as `tools/deploy/deploy-gateway.local.json`. Future
short commands such as `gi deploy`, `ги деплой`, `gi ftp`, or `ги фтп` should
reuse the saved gateway when no method or path is supplied. Store only local
selection metadata there, such as gateway path, entrypoint, source-path
parameter, project id, deploy mode, and target name; keep credentials and
private remote paths in the gateway's own ignored config or secret store.
Before touching the gateway, read its own `AGENTS.md`, `COMMANDS.md`, and
documented deploy runbook such as `docs/deploy.md` when present. Prefer a
single documented gateway entrypoint such as `tools/deploy/deploy.ps1`; pass the
current project root as `-SourcePath` or the gateway's documented equivalent,
and pass project id, deployment mode, or target name only when the gateway
contract defines them. Do not infer credentials, print secrets, edit the
gateway's private local config, or run arbitrary helper commands from that
directory. If no argument is supplied and no selected gateway exists, stop and
ask the user to make the full first call, for example
`gi deploy <method-or-path>` / `ги деплой <способ-или-путь>`. Do not reinterpret
a bare first `gi deploy` as `gi prod`, direct FTP upload, a build, or another
deployment workflow. If the gateway contract, required entrypoint, source-path
parameter, target project mapping, or deploy mode is missing, ask one concise
clarification question instead of guessing.

If the user's task is to prepare or repair the deploy gateway itself, work in
that gateway project and create or update the reusable deploy contract there:
`AGENTS.md`, `COMMANDS.md`, a deploy runbook such as `docs/deploy.md`, one
documented entrypoint such as `tools/deploy/deploy.ps1`, redacted config
examples, and verification/rollback notes. Keep real secrets and private target
paths in the gateway's ignored local config or secret store, not in shared
instructions or consuming projects.

During GI update migrations that retire project-owned direct deployment,
non-devops projects remove, disable, or stop relying on their own direct
deploy/upload scripts, FTP/SFTP configs, and private deploy helpers. They keep
only ignored selected-gateway metadata such as
`tools/deploy/deploy-gateway.local.json`, redacted examples, and documented
build artifact contracts needed by the gateway. If no selected deploy gateway
exists, the agent asks for the gateway path instead of uploading directly or
creating a new personal deploy path. Projects marked with `gi set devops` keep
and maintain deploy scripts/configuration as gateway-owned infrastructure.

`gi ftp <deploy-hub-path>` / `ги фтп <путь-к-deploy-хабу>` is the FTP/SFTP
variant of the same gateway flow: the current project is the upload source, and
the path names the deploy gateway that owns FTP/SFTP configuration, destination
selection, and secret references. Record that gateway as the current project's
selected deploy gateway, then use the gateway entrypoint and pass the current
project root as the source. Later `gi ftp` / `ги фтп` without a path should use
the saved gateway. Do not bypass the gateway by reading or rewriting its private
local JSON files except as its own instructions explicitly allow.

When the deploy gateway supports automatic project registration, an unmapped
current project uses its root folder name as the default project id. The gateway
derives the remote destination from its documented naming convention, records or
updates the project in its deploy registry, and leaves non-secret metadata for
later hub/card/index updates. Unless the gateway contract explicitly names an
existing target hostname, the public target must be project-scoped, normally
from the sanitized project id under the configured base domain; the agent must
not target the apex/root domain, shared hub hostname, or another project's
hostname for an unmapped project. The project agent should not ask the user to
pick a remote folder, project id, or subdomain when the gateway contract defines
deterministic registration; it should use the documented project-id-to-hostname
rule or report the missing gateway contract.
Before reporting an unknown deploy project or missing target mapping, the agent
checks the gateway registry and any documented project inbox, pending queue,
hub-card queue, or domain/hosting request list. A pending or errored inbox entry
is the active deploy state. For a pending entry, the agent refreshes allowed
non-secret metadata, uploads the artifact to the gateway's documented
pending/staging/handoff target when one exists, and reports that devops/hosting
publication is still pending instead of creating a duplicate mapping or
uploading to the gateway root. For an errored entry or rejected request, the
agent first checks whether the evidence is fresh from the current attempt or
stale/indirect, such as an old inbox status, cached host-limit check, screenshot,
or external quota claim. Stale evidence is warning context: the agent says that
provisioning may fail, then runs the gateway's documented safe create, refresh,
or provisioning attempt when available. It stops only when the current attempt
returns an explicit rejection or the gateway has no documented attempt/refresh
path. If the gateway has a documented new-domain/request workflow, create or
refresh that request before deciding whether to continue artifact upload, leave
the request pending, or return an explicit error.
If registration, provisioning, or artifact selection cannot continue, the agent
does not report a vague blocker. A pending domain/hosting request should still
upload to the gateway's documented pending/staging/handoff target when
available. Otherwise the agent returns an explicit deploy error with the failed
step, evidence, responsible system or owner, next required action, and the
artifact/source state already recorded. It must not fall back to a root/default
remote path, apex/root domain, shared hub hostname, another project's hostname,
or upload the whole repository.

`gi ftp config` / `ги фтп конфиг` creates, inspects, or updates FTP/SFTP config
without uploading. In ordinary non-devops projects, this must select or use a
deploy gateway; it must not create a project-owned direct FTP/SFTP deploy path.
Direct project-local FTP/SFTP config belongs only in a project marked devops, or
behind a documented deploy-gateway delegation. Use a separate ignored local file
such as `tools/deploy/ftp.local.json`. Prefer secrets through environment
variables or private keys; do not commit real hostnames, usernames, passwords,
tokens, private keys, or private remote paths unless project policy explicitly
marks them non-secret.

`gi ftp service` / `ги фтп сервис` manually registers, inspects, or selects an
FTP/FTPS/SFTP service record in config-service without uploading. In ordinary
non-devops projects, service selection belongs to the saved or supplied deploy
gateway. Only a devops project or documented gateway delegation should query
config-service for FTP-capable services for direct upload. If one exists, the
agent verifies its contract and uses it; if several exist, it asks the user to
choose with the same plain inline numbered checkbox marker style used by
language selection. Store only non-secret discovery metadata and secret
reference names in config-service, never raw credentials or private remote
paths.

`gi ftp folder` / `ги фтп папка` inspects, chooses, or updates the remote upload
folder (`remotePath`) without uploading. In ordinary non-devops projects, this
is resolved through the deploy gateway and must not create a project-owned
direct remote path. In a devops project or documented gateway delegation, if
credentials and a selected FTP service are available, the agent may list remote
directories and ask the user to choose with plain inline numbered checkbox
markers; otherwise it asks for the destination path and saves it in the
gateway-owned or devops `tools/deploy/ftp.local.json`.

`gi ftp push` / `ги фтп пуш` is the explicit upload command. `gi ftp` /
`ги фтп` remains a shorter alias. In ordinary non-devops projects, the agent
uses the selected deploy gateway; if none is selected, it asks for the gateway
path. In a devops project or documented gateway delegation, the agent reads
project-local deploy instructions and `tools/deploy/ftp.local.json`, builds the
configured `localPath` when needed, then uploads to `remotePath`. If the direct
config is missing in an allowed direct-upload context, use the redacted template
shape from `templates/ftp.local.template.json` or
`tools/deploy/ftp.local.example.json` and ask only for missing required values.
Treat upload stalls, hangs, repeated timeouts, and failed stream opens as failed
FTP/FTPS transfers. If FTP/FTPS connects but upload fails or is unreliable,
immediately inspect the service contract, project-local config, and current
user-provided details for an authorized SFTP-over-SSH route to the same remote
deploy folder. When the needed SSH host, port, user, and credential reference
are available, switch to SFTP before more FTP/FTPS upload variants and report
that fallback. If they are missing, report the exact missing SFTP details
instead of inventing credentials or retrying the same failing FTP path. Do not
disable TLS certificate validation or accept invalid FTPS certificates as a
routine fallback unless the deploy contract or current user message explicitly
authorizes that degraded security path.
Do not print secrets or full credential-bearing commands.

`gi config service on` / `gi config service off` sets the current application's
project-local config-service self-registration flag in the same documented
local config area as its config-service URL. `on` is for web-facing apps that
expose a port, HTTP API, web UI, task-manager service, or local daemon endpoint:
on startup they must contact config-service and read their own `service_id`
startup/service record before binding any port. The port to bind and neighboring
service endpoints come from config-service. If the recorded port is already
occupied, the app or agent must verify whether the owner is the same documented
service instance. A same-service owner may be reused or restarted only through
the local run contract. A different, unknown, or unverifiable owner is a
port-conflict blocker: do not stop it without explicit approval, do not rewrite
the service record, and do not bind a neighboring fallback port. Changing ports
changes browser origin and can make browser-owned state such as localStorage,
cookies, and IndexedDB appear missing. If config-service is missing,
unreachable, has no record for the app, or returns incomplete startup config,
startup reports the blocker and waits for config-service to be configured,
repaired, or started; it does not guess, scan, or use stale fallback ports.
`off` means the app must not publish or refresh its own service record. Desktop
apps, CLI tools, libraries, scripts, and other non-web apps should not query or
publish to config-service during normal startup unless local instructions
explicitly define a discoverable web/API runtime. If the flag is being set to
`on` and no config-service URL is configured, stop and tell the user to set
`gi config service url=<url>` first. Do not reinterpret `on`/`off` as starting
or stopping the config-service process.
This self-registration flag is separate from `gi config on/off` and has effect
only while project config-service integration is enabled.

`gi reboot` / `gi restart` starts or restarts all documented applications in the
current project using project-local run instructions. Before starting anything,
identify the full app set from local run instructions, manifests, service
records, desktop packaging metadata, or project memory; do not assume a
successful web/API start covers the project. For local web/API services, when
config-service integration is enabled, resolve the service id, port, URL, and
neighboring endpoints through config-service before running a start command;
fixed ports in local runbooks or examples do not authorize a fallback bind.
When integration is disabled, use only documented project-local runtime config
and stop if required values are missing. If the selected port is occupied,
verify whether the owner is the same documented service; otherwise report a
port-conflict blocker and do not move the app to another port. If a
config-service record is missing, use only the documented config-service
registration workflow to create or update it before startup, or stop with the
exact missing contract. If local
instructions define a preferred start/restart command that launches the full
app set, use it with runtime values selected by the enabled config-service flow
or the disabled project-local flow. Otherwise enumerate every documented app or runtime, such as
desktop app, web/API app, and background workers, then restart each running app
and start each missing app in the background. After launch, wait briefly and
verify the documented startup success signal for each app: expected processes
are still running, visible desktop windows exist when applicable, web/API health
or discovery succeeds when applicable, and relevant startup or crash logs do not
show a new failure. The final report must account for each app by name or role
with started/restarted/skipped status and verification evidence. Do not report
reboot success from a PID alone, from a web health check alone, or while any
expected desktop app, web/API app, or worker is unlaunched or unverified. If a
documented desktop app lacks a launch command or window verification signal,
report that as a blocker or partial failure instead of success. Published
hosting environments follow their hosting or production deploy contract and are
not restarted by local `gi reboot` unless project-local production instructions
explicitly define that behavior.

`gi docker` / `ги докер` restarts the current project's documented Docker or
Docker Compose runtime. The agent first reads project-local Docker/run
instructions, compose files, Dockerfile or Containerfile, scripts, manifests,
service records, and health-check contracts. If no Docker/Compose config or
documented Docker run contract exists, report that Docker is not configured for
this project and stop. If Docker CLI, Docker Compose, or the Docker engine is
missing or unavailable, report that blocker. Rebuild before restart when the
image is missing, local Docker/build inputs changed, the local contract requires
it, or freshness cannot be proven; otherwise restart/up the existing current
image. Prefer documented commands; without one, use the narrow project Compose
command such as `docker compose up -d --build` when rebuilding is needed, or
`docker compose up -d` / documented restart when it is not. Do not prune Docker
state, remove volumes/images, or stop unrelated containers. Verify container
status, health checks, mapped URLs, and relevant recent logs before reporting
rebuilt/restarted/not-configured/blocked status.

`gi first test` / `gi первый тест` / `ги первый тест` resets only documented
project-owned application cache, generated state, temporary first-run profiles,
and rebuildable local app settings, then starts the app and verifies the
documented first-launch workflow. The agent first reads project-local run,
cleanup, cache reset, and test instructions. It must not delete user documents,
production data, secrets, credentials, external service data, shared system
caches, sibling projects, or arbitrary user-home folders. If exact reset paths,
keys, or commands are missing, ask one concise clarification question instead
of guessing.

`gi default` / `gi defaults` / `ги дефолт` restores the current project to its
documented first-run/default state. The agent first reads project-local reset,
cleanup, first-run, run, backup, and test instructions, then uses only
documented reset scripts, paths, keys, or contracts. It must not delete source
files, project-memory specifications, instruction-kit files, user documents,
production data, secrets, credentials, external service data, shared system
caches, sibling projects, or arbitrary user-home folders. If reset targets are
not documented, ask one concise clarification question instead of guessing. If
the reset could be irreversible or remove user-owned data, stop for explicit
confirmation and prefer a backup or rename step when local rules allow it.
After reset, start the project through documented run instructions, verify the
default or first-launch success signals, and report what was reset, what was
left untouched, what passed, and any blocker.
