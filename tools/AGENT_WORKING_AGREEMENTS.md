# Agent Working Agreements

## Scope

- Keep changes small and tied to the current request.
- Ask before expanding into unrelated modules.
- If a task requires files outside the agreed working area, say so first.
- Treat the current project root as the filesystem boundary for normal work.
  Do not read, search, edit, create, delete, move, or inspect files in another
  project or arbitrary external folder unless the user gives an explicit
  concrete path and action. Use APIs, connectors, or task-manager endpoints for
  cross-project communication.
- Before filesystem writes, verify that the active project root and target
  identity match the user's current request. Use local identity signals such as
  local instructions, README, manifests, service id, git remote, and project
  memory. If the request appears to target another product, repository, or
  absolute path outside this root, stop and warn the user unless the current
  message explicitly authorizes that exact external path and action.
- Treat nested checkouts, vendored repositories, cloned examples, and
  third-party source trees as separate scope. Do not inspect them as part of the
  main project unless the user explicitly asks, the task is about that nested
  tree, or local instructions identify it as an active workspace component.
- Treat user-home application data and personal telemetry as private external
  sources. Do not read `.codex`, `.cursor`, IDE logs, browser profiles, shell
  history, application SQLite databases, or local app logs outside the project
  root unless the user gives an explicit path and action. For analyzer tasks,
  prefer mock or sample data, or ask for permission to inspect a specific file.
- Treat product plans, `apps.txt`, summaries, and task-manager notes as intent
  signals only. They are not permission to read private local data sources.
- If a required file, skill, config, script, endpoint, task, or other entity is
  missing or not found, first reread the relevant local instructions, runbook,
  project memory, and accepted instruction-kit artifacts for the current scope.
  If the entity is still missing, ask the user a short clarification question.
  Do not use another project folder or the shared instruction library as a
  runtime fallback unless the user explicitly gives that path and action.

## User Changes

- Do not revert user changes unless explicitly requested.
- Treat dirty worktrees as normal.
- If user changes affect the task, work with them.
- Preserve recorded feature workflow contracts. If a feature has an agreed
  runtime workflow, loading order, branching state flow, background work, or
  user-visible guarantee, read that contract before changing the feature and
  update it in the same scoped change when behavior intentionally changes.
- For non-trivial features, keep the feature idea, functional description,
  workflow contract, implementation plan, sprint breakdown, task breakdown,
  definitions of done, and verification connected. Tasks do not replace the
  feature contract.
- Treat project memory as the portable product specification layer. For
  non-trivial feature, business-rule, data-model, integration, or architecture
  work, update the relevant project-memory specification in the same scoped
  change. Write it so another agent could rebuild the behavior on a different
  language, framework, or platform. A handoff summary is not a substitute.
- During such work, compare changed behavior with the relevant spec, source,
  tests, and affected docs. Capture branches, failure handling, invariants, and
  architecture decisions in focused specs, or confirm the existing spec covers
  them, before the implementation task is complete. Git finish does not repeat
  this product-contract audit.
- Mark current, planned, and historical behavior clearly in affected specs;
  support current-implementation claims with a last-check date and source or
  test paths. When adding, renaming, moving, or retiring a spec, update its
  project-memory index entry and verify the relative link in the same change.
- Keep project documentation separate from project memory. Put overview,
  user-visible functionality, stack, commands, operations, and troubleshooting
  in `README.md`, `docs/`, or the runbook. Put algorithms, business rules,
  workflow contracts, state machines, invariants, and verification guarantees in
  project memory.
- After any meaningful implementation, refactor, migration, or configuration
  cleanup batch, verify that every touched layer uses the intended
  source-of-truth for changed defaults, policies, workflows, contracts, or
  interpretation rules. Check backend, frontend, tests, docs, generated
  examples, build metadata, and project-memory specs as relevant; keep unrelated
  files and generated noise out of the batch; and distinguish harmless
  line-ending warnings from real `git diff --check` whitespace errors. Classify
  the batch as refactor, development, verification, operation, migration,
  configuration cleanup, or a named mix; do not hide behavior changes,
  public-contract changes, service operations, or data migrations inside a
  "refactor" label.

## Secrets

- Do not treat a credential pasted into chat as an automatic blocker for the
  whole task. Warn once without repeating the value, recommend rotation, and
  continue every independent task step that does not expose or unsafely persist
  it. If an authenticated operation has no safe credential path, mark only that
  operation blocked or unverified and continue the remaining work.
- Use approved secret stores, environment references, or connector
  authorization for authenticated operations. Never copy a pasted credential
  into source, committed config, logs, project memory, task-manager payloads, or
  later chat responses.

## Git

- Keep rebuildable builds, frontend bundles, installers, and intermediate
  output in dedicated ignored directories; exclude them from staging, commits,
  and pushes to source repositories unless an exact project-specific exception
  is explicitly approved. Keep source and build inputs versioned. Follow
  `patterns/AGENTS_RUNTIME/09-build-and-install.md` for authorized output-layout
  cleanup, index removal that preserves local files, and clean-checkout checks.
- Default: the agent edits and verifies; the user reviews and commits.
- This default permits agent commits on explicit GI Git-finish commands below.
  If a project intentionally forbids all agent commits, state that exception
  explicitly and report `gi пуш` as blocked rather than treating it as a
  push-only command or asking the user to commit and retry it.
- Treat `gi коммит`, `gi пуш`, `gi коммит пуш`, and `gi только пуш` as explicit
  git finish requests. `gi коммит` commits scoped current changes only; `gi пуш`
  and `gi коммит пуш` commit scoped current changes and push the current branch;
  `gi только пуш` pushes existing local commits without creating a new commit.
  Do not reinterpret `gi пуш` as a raw `git push`, a retry of a previous
  terminal push, or a push-only command; if there are no scoped changes to
  commit, report that clearly instead of falling back to push-only behavior.
  Inspect status, keep changes outside the resolved scope out, follow commit-message
  preferences, and stop on ambiguous scope, missing remote, conflicts, secrets,
  or push failures.
- For a branch without an upstream, obtain the intended remote branch before
  staging or committing for a push, then set tracking on the first push. Do not
  infer the target from another branch that happens to contain the same HEAD.
- Resolve commit scope from explicit user-selected changes, then the active
  conversation task. With neither, standalone `gi commit`, `gi push`, and
  `gi commit push` (including Russian aliases) select the current repository's
  eligible tracked and untracked changes, including pre-existing user changes.
  Apply this command-defined scope in a new chat without asking whether to
  include all changes solely because history is absent or many files are dirty.
  Inspect and briefly report scope and exclusions before staging; exclude
  secrets, prohibited content, generated noise, and work reserved separately.
  Do not expand an active task from apparent file similarity. Ask only about
  concrete conflicting scope instructions or inseparable excluded changes.
  `gi only push` never selects working-tree files.
- Git finish does not authorize new implementation, test-expectation rewrites,
  runtime-state deletion, dependency changes, service restart/rebuild, or broad
  cleanup merely to make checks pass. Fix a verification failure only when the
  scoped work caused it and the original task already authorizes the fix;
  otherwise report the blocker and leave unrelated state unchanged.
- Complete every task-scoped tracked write, including handoff and generated
  metadata updates, before staging. After the last commit or push and the last
  filesystem mutation, recheck `git status --short`; for pushes also verify the
  local branch matches its configured upstream. HEAD equality alone does not
  prove a clean worktree. Never report a complete clean finish while a new
  task-scoped diff remains, and do not modify tracked task files after the final
  check without repeating the authorized finish workflow and verification.
- Treat `gi пул`, `gi pull`, and `ги пул` as explicit requests to fetch and pull
  the current branch from its configured upstream. Inspect status, branch, and
  upstream first. Resolve only obvious, low-risk conflicts where intent is clear
  and user changes are preserved; if product judgment, unrelated changes,
  secrets, or uncertainty are involved, stop and ask the user with concise
  options.
- Exception: after a successful `gi обновить` / `gi обновись`, commit and push
  only the resulting instruction-kit update changes when this project is a git
  repository with a configured remote. If unrelated/user changes, no remote,
  push failure, or conflicts are present, stop and explain the blocker.
- In a shared instruction-library project, a user request to add or accept a
  reusable rule is also an explicit finish request for that accepted rule:
  verify, commit, and push only the scoped rule changes, then run the
  `gi обновить` update flow when accepted instruction-kit propagation applies.
  Do not include unrelated dirty worktree changes or recurse merely because this
  finish rule itself was added or run.
- Branch naming: `TODO`.
- Generated files policy: `TODO`.
- Never commit secrets, credentials, local databases, logs, or caches.
- Never add, stage, commit, or push content payloads such as LLM or other model
  weights/checkpoints, photos, video, audio, datasets, archives, or similar
  large binary artifacts. Keep them outside Git in project-approved artifact or
  object storage; commit only compact manifests, source URLs, checksums, or
  retrieval instructions. Inspect untracked and unusually large files before
  staging and add project-local ignore rules for prohibited content. Require
  explicit user approval for any exact project-specific exception.
- Follow `tools/project-memory/git-preferences.json` for commit-message
  languages. English is primary; selected additional languages are included when
  the user explicitly asks the agent to commit.
- When the user asks in chat to change commit-message languages, update
  `tools/project-memory/git-preferences.json` directly and summarize the new
  setting.
- Do not infer additional commit-message languages from the user's UI language
  or message language. If the requested languages are ambiguous, ask which
  additional languages to enable.
- For ambiguous commit-language selection, ask with a concise numbered Markdown
  checklist showing `English` as always selected and current additional
  languages as checked. Explain that `English` is the required primary
  commit-message language and cannot be disabled. Ask the user to reply with
  language names or numbers. Render each option as a plain inline checkbox
  marker with the number and label on the same physical line, such as
  `[x] 1. English` or `[ ] 2. Russian`. Do not use Markdown task-list syntax
  such as `- [x] 1. English` or ordered-task syntax such as `1. [x] English`,
  because some chat renderers split the checkbox control and label onto
  separate lines. Never emit a standalone checkbox line followed by a separate
  numbered label line.
- When reporting this change, mention the plain
  `tools/project-memory/git-preferences.json` path instead of malformed or
  placeholder markdown links.
- If the user explicitly wants to configure languages manually, they can run:

```powershell
.\tools\select-git-commit-languages.ps1
```

or:

```powershell
.\tools\agent-start.ps1 -ConfigureGitCommitLanguages
```

## Agent Language

- Follow `tools/project-memory/system-preferences.json` for the agent's
  user-facing working language in this project.
- Apply the configured system or project language to progress updates, final
  answers, clarifying questions, user-facing explanations, agent-created task
  titles, task descriptions, task-manager updates, plans, and checklists.
- Start final answers and direct user-facing explanations with the concrete
  answer or decision whenever the user asked a question or needs an outcome.
  Lead with `Yes`, `No`, `Exactly`, `Not yet`, the main conclusion, or the
  requested status before caveats, evidence, context, or implementation
  details. Put nuance and supporting detail after the direct answer so the user
  can decide whether to keep reading.
- For task titles, descriptions, and task-manager updates, treat the first
  configured task language as the main language. If exactly one task language is
  configured, write task text only in that language. If multiple task languages
  are configured, write the main-language text first and then add one clear
  translation per additional language. Do not duplicate the same content twice
  in one language, and do not mix untranslated labels, templates, or Definition
  of Done text from another configured language into the main-language text.
- Do not apply the system or project language to existing task text, code,
  commands, logs, quoted text, or a response language the user explicitly
  requested for a specific message.
- Treat `gi language`, `gi язык`, `ги язык`, `gi project language`,
  `gi проект язык`, `ги проект язык`, `gi язык проекта`, and `ги язык проекта`
  as requests to configure three ordered language sequences: project working
  environment, commit messages, and tasks.
- If the unified project-language command does not include explicit languages,
  ask in three numbered steps. For each step, show a concise numbered Markdown
  checklist with the available languages and the current selection, then accept
  the user's next answer as numbers or language names for that step.
- When a unified project-language step has no current selection, default it to
  `1 2`: `English`, then `Russian`.
- If the user replies with only numbers, such as `1 2`, map them to the most
  recent checklist and preserve that order. Do not ask what those numbers mean
  after showing the checklist.
- Treat `gi system language`, `gi систем язык`, and `ги систем язык` as
  requests to configure this preference.
- Keep this setting separate from commit-message languages. `gi commit
  language`, `gi коммит язык`, `ги коммит язык`, and older `gi язык коммита`
  forms configure `tools/project-memory/git-preferences.json`, not the agent's
  working language. The unified project-language command updates both
  preference files.
- If the user explicitly wants to configure the system language manually, they
  can run:

```powershell
.\tools\select-system-language.ps1
```

or:

```powershell
.\tools\agent-start.ps1 -ConfigureSystemLanguage
```

## Context Hygiene

- Do not print full `git diff` output by default. Prefer `git diff --stat` and
  targeted queries for relevant files or patterns.
- For first-pass project study, read local instructions, README, manifests, and
  config entry points before building a file map. Use recursive scans only after
  a targeted search fails or the task clearly requires repository-wide
  inventory.
- Do not read large files in full by default, including large `index.html`,
  bundled JS/CSS, logs, lockfiles, generated files, and build artifacts. Prefer
  targeted searches, heads, tails, or small line ranges such as
  `Get-Content -TotalCount`, `Get-Content -Tail`, and `Select-String` on
  PowerShell.
- For verification, count or query HTML elements programmatically instead of
  printing the whole HTML document.
- Do not produce broad artifacts, such as zip archives, or run full check
  matrices unless the user explicitly asks for that scope.
- Final responses should summarize only the changes, checks, and current status;
  do not restate the full investigation context.
- Search for specific symbols, paths, errors, or patterns before doing broad
  repository scans.
- Do not print large logs. Prefer tails and targeted error searches.
- Keep progress updates phase-level, not command-level. Do not narrate after
  every command batch, report counters such as "ran 4 commands", or live-blog
  each intermediate hypothesis. Update when the phase changes, a meaningful
  finding changes the next step, a blocker appears, or work has been quiet long
  enough that the user needs reassurance.
- Do not duplicate tool-run counters that the chat UI may show automatically;
  system UI counters are not agent progress updates.
- Launch applications in the background so focus does not jump away from the
  user's current window.
- Treat a short first message as a possible chat title: restore context, then
  ask what to do next instead of executing the title as a task.
- Treat short chat commands that start with `gi` as shared instruction-kit
  commands for the copied `general-instructions` kit in this project. `gi` is
  the only short prefix; do not rename it to `GAI` or another alias.
  If a `gi` command is missing a needed parameter, ask one short clarification
  question instead of guessing.
- Treat `gi help`, `gi хелп`, `ги help`, `ги хелп`, `gi commands`,
  `gi команды`, and `ги команды` as informational requests for the local GI
  command list. Show compact command names and short descriptions; do not run
  startup restore, resume old tasks, call services, or execute the listed
  commands.
- Use the instruction kit as a token-economy and RAG-startup layer: restore only
  task-relevant context from local instructions, summaries, targeted searches,
  and project memory instead of broad repository reads or large outputs.
- Use `gi sql` and `gi vector` as inspection commands for project-memory
  retrieval metrics and activation limits. Report current counts, readiness,
  staleness, and recommendations; do not deploy heavy databases or external
  services by default.
- Use `gi refactor`, `gi рефактор`, or `ги рефактор` for a full current-project
  refactor under all applicable GI rules. Read local instructions, contracts,
  manifests, project memory, and tests first; create a concise plan; then work
  in small verifiable batches that preserve user-visible behavior unless the
  user explicitly changes it. Cover architecture boundaries, configuration
  boundaries, hard-code removal, development-tool/product separation,
  SOLID/DRY/clean-code concerns, duplicated business logic, contracts, tests,
  project-memory updates, and cross-layer source-of-truth consistency. Ask
  before destructive operations, data migrations, public API or storage
  contract changes, dependency replacements, formatting-only churn, or
  private/external paths. Keep structural refactor work separate from
  development work such as new behavior, validation, observability,
  integrations, runtime flows, or new public contracts; label verification and
  service operations separately too.
- Use `gi build`, `gi собрать`, `ги билд`, `ги собрать`, and `gi rebuild` for
  the current project/application build or rebuild only, such as producing a
  release/upload-ready `dist/`, executable, package, or documented build
  artifact. These commands do not upload, publish to production, or produce an
  installer unless the project-local build contract explicitly says so. Use
  `gi tools rebuild` /
  `gi rag rebuild` only for a confirmed full rebuild of the current project's
  configured GI/RAG project-memory retrieval system. Use node forms such as
  `gi tools rebuild sql`, `gi tools rebuild chunks`, `gi tools rebuild vector`,
  and `gi tools rebuild evals` for scoped GI/RAG rebuilds.
  During `gi обновить`, migrations that change RAG rules, indexers, chunking,
  embedding metadata, or retrieval adapters must leave affected rebuild state
  stale until the documented rebuild and status checks succeed.
- Treat `gi prod`, `gi production`, `gi прод`, and `ги прод` as production
  service publication requests only for online services connected to real
  remote APIs. Normal development, refactors, tests, cleanup, formatting, and
  `gi restart` use the development checkout/service and must not edit, reset,
  stop, or test inside the production service folder. For `gi prod`, read the
  project-local production contract, build or prepare the documented
  development artifact, sync only approved files into the production folder,
  preserve production-local secrets, config, databases, logs, caches, sessions,
  webhook/API state, and service manager files, then restart/reload/switch over
  and verify only through documented commands. If the production folder,
  include/exclude rules, health check, or rollback path is missing, ask one
  concise question instead of guessing.
- Keep `gi` command responses scoped to the shared instruction-kit command. Do
  not resume an older product task after a `gi` command unless the user
  explicitly asks.
- Run `gi` commands against this project root. Do not switch to another
  repository, the shared instruction library, or a path from an older task unless
  the user explicitly asks.
- Task-manager paths, raw intake metadata, summaries, or previous chat context
  are not permission to enter another project folder.
- `gi` means `general-instructions`, not `git`. Missing `.git` blocks only the
  automatic commit/push step after a successful GI update; it does not block
  checking or applying instruction-kit file updates.
- Treat `gi саммари` and `gi summary` as requests to write a handoff summary
  file under `tools/summary/`, not only as requests to summarize in chat.
- Keep handoff summaries focused on thread substance as a thematic handoff, not
  as a short chronological retelling. Break the thread into meaningful topic
  sections, list the key theses under each topic, and briefly describe each
  thesis. Add more detail only when a complex topic would lose necessary
  context without it. Include links to code files, URLs, media, images, logs,
  screenshots, or exact artifacts only when those references are needed to
  understand or verify the context. For architecture or research conversations,
  especially when the user evaluates an external project, article, pattern, or
  tool as a possible integration target, explicitly preserve the user's
  exploration intent and map the external concepts to current project
  components. State whether the discussion was informational or preparation for
  implementation, which external item was considered, which local components it
  could affect, what a future agent must not miss, and which conclusions are
  decisions versus hypotheses. Omit routine command bookkeeping such as
  successful `gi push`, staging counts, git directives, branch names, push
  targets, and commit hashes when git logs or command history can recover them.
  Mention repository state only when it affects the next agent's action. If a
  step-by-step protocol is needed, add a separate `Thread Timeline` section or
  file only when the user asks or the timeline materially helps the handoff.
- When asked where a previous thread stopped, compare the latest handoff summary
  with the most recent visible thread conclusion or user-provided evidence.
  Prefer the last explicit architectural/product decision, open question, or
  agreed next direction over incidental caveats in the summary. Do not turn an
  unverified caveat, environment variable, skipped check, or old `Next Best
  Steps` bullet into the current task unless the user selects it or it blocks
  the stated goal.
- Treat `gi гит-обзор` and `gi git summary` as requests to summarize the latest
  git commit in the current project in chat. Include commit metadata, changed
  files, compact stats, inferred purpose, and notable risks or checks. Do not
  print a full diff, create a summary file, commit, or push for this command.
- Treat `gi тест-план` and `gi test plan` as requests to inspect local project
  test commands and produce a compact verification plan for the current feature,
  bug fix, or release check. Plan first; run checks only when the user asks or
  when the current task already requires verification.
- Treat `gi test` / `ги тест` as information about the tester and local scenarios,
  settings, prerequisites, and gaps; do not execute or mutate runtime state.
- Treat `gi test start` / `ги тест старт` as execution of the selected local
  scenario. `gi test task` / `ги тест таск` selects its workload without running.
  Follow `patterns/AGENTS_RUNTIME/09-testing.md` for authorization, evidence,
  checkpoint/resume, restoration, and completion states. Projects own scenario
  modes, settings, links, roles, inputs, commands, and artifact locations.
- Include content entry when the selected test needs it: resolve authorized
  material or permitted synthetic inputs, validate case/field mapping, confirm
  acceptance, and track introduced content through cleanup/restoration. Keep
  content values and source paths local; do not invent real IDs or links.
- Use `gi full test`, `gi release test`, or `gi system test` for full-system
  verification, following `patterns/AGENTS_RUNTIME/09-full-testing.md` as well.
  Apply full-system resets only to that flow; an observational scenario uses
  its own state contract. Old evidence and mocked/partial checks do not prove
  a fresh live full-system run.
- For verification plans and smoke checks, confirm exact CLI flags, ports,
  routes, methods, JSON payload fields, and required environment variables from
  current local instructions, manifests, config, or source code. Summaries and
  old chat snippets are evidence, not authoritative command contracts.
- Treat `gi install`, `gi инсталл`, `ги инсталл`, and clear typo variants as
  build-and-installer requests. The task is complete only after the packaging
  command runs and a current installer artifact is produced or explicitly
  verified; restore/build/test alone are preliminary checks. Default to a
  Windows installer when no platform is named. If the user or local packaging
  contract names macOS, iOS, Android, Linux, or another platform, use that
  platform's documented packaging contract and ask one concise question when it
  is missing or ambiguous. Keep platform-specific build instructions, packaging
  configs, signing notes, verification notes, and installer artifacts in
  separate project-local platform folders or per-platform artifact manifests.
- Treat `gi first test`, `gi первый тест`, and `ги первый тест` as first-launch
  verification requests. Reset only documented project-owned app cache,
  generated state, temporary first-run profiles, and rebuildable local settings;
  do not delete user documents, production data, secrets, credentials, shared
  system caches, sibling projects, or arbitrary user-home folders. If exact
  reset paths or commands are missing, ask one concise question instead of
  guessing.
- Treat `gi default`, `gi defaults`, and `ги дефолт` as default-state reset
  requests. Restore only documented project-owned app state, generated caches,
  local settings, onboarding flags, temporary profiles, and other rebuildable
  first-run/default state. Read local reset, cleanup, first-run, backup, run,
  and test instructions before clearing anything. Do not delete source files,
  project memory, instruction-kit files, user documents, production data,
  secrets, credentials, shared system caches, sibling projects, or arbitrary
  user-home folders. If reset targets are undocumented, ask one concise question;
  if reset could be irreversible or user-owned data is involved, require
  explicit confirmation and prefer backup or rename when local rules allow it.
- Treat a first message that points to a shared instruction library as an
  instruction bootstrap, not as a request to add that library as a dependency.
- Treat `gi init <source>`, `init <source>`, `инит <source>`,
  `инициализируй <source>`, and `инит правила <source>` as shared-instruction
  bootstrap/startup requests when `<source>` points to the canonical
  `https://github.com/Dimosfil/general-instructions.git` repo, the shorter
  `Dimosfil/general-instructions.git` GitHub form, a Markdown link to either
  form, a local checkout/cache, or another known `general-instructions` source.
  Never reinterpret these forms as `git init`, git remote replacement, folder
  creation, OpenCode setup, project creation, `npm init`, or `python -m venv`
  unless the user explicitly names that action.
- If the user asks to update from a shared instruction library and this project
  has no `tools/project-memory/instruction-kit.json`, treat that as first-time
  instruction bootstrap/init.
- Run `gi обновить` quietly by default: do not narrate step-by-step reasoning,
  repeated progress, command transcripts, broad file reads, or full diffs during
  normal successful updates. Apply the update, then report a compact summary
  with versions, migration counts/IDs, changed files, checks, commit/push
  result, and blockers if any.
- For web applications, assume the user will inspect the UI manually. Do not
  open, browse, screenshot, or visually inspect the UI automatically unless the
  user explicitly asks for that.

## Editing

- Prefer patch-style edits for manual changes.
- Avoid unrelated formatting churn.
- Add comments only when they clarify non-obvious behavior.

## Task Planning

- For analysis, refactoring, migration, or multi-step implementation tasks,
  create or update a concise checklist in `tools/project-memory/pending-tasks.md`
  or a dedicated task plan in `tools/project-memory/` before editing code.
- Include the goal, planned changes, execution order, risks or dependencies, and
  verification steps.
- Update progress as meaningful steps complete.
- Update feature/business/architecture specifications as meaningful behavior
  changes are completed.
- Keep plans concise. Do not store full diffs, large logs, generated outputs,
  secrets, credentials, or private production data.

## Shared Instruction Updates

- When this project reveals a reusable improvement to agent instructions,
  workflows, templates, or checklists, write a dated recommendation to the shared
  instruction library's `updates/` folder if it is available.
- If no shared instruction library is available, use a local intake folder such
  as `tools/instruction-updates/` or
  `tools/project-memory/instruction-updates/`.
- Treat recommendations as intake, not accepted rules.
- Recommendations should explain the observed problem, reusable rule or
  workflow, evidence paths, affected files or commands, risks, and privacy
  review.
- Capture reusable workflows, failure patterns, token-saving tactics, and
  agent-instruction improvements that could improve `gi` for other projects.
- Do not add a shared instruction library as a project dependency, package,
  submodule, symlink, or runtime reference unless the user explicitly asks for
  that.

## Task Managers

- Treat task-manager configuration as project-local state.
- Store only the manager name or `service_id` plus non-secret project
  preferences in project memory.
- Resolve task-manager runtime URLs through GI config-service by service id only
  when project config-service integration is enabled; do not store, guess, or
  copy API endpoints from old notes or other projects. If integration is
  disabled, manager-backed commands stop and point to `gi config on`.
- If a configured manager id is missing from config-service, stop with a concise
  blocker instead of falling back to port scans or stale task-manager memory.
- Before posting plans or starting sprint work, read the manager guide when
  present, then verify the workflow-specific manager contract and capabilities,
  not only generic health.
- For agent-facing HTTP services, treat `endpoints.guide` as service-owned
  onboarding and `endpoints.contract` as strict workflow validation. If the
  guide and contract disagree about endpoints, ownership, or permissions, stop
  and report the mismatch instead of inferring behavior from stale memory,
  filesystem paths, dashboard URLs, or raw receipts.
- Treat task managers as work queues and lifecycle recorders, not as the actors
  doing implementation work. The agent takes, implements, verifies, and reports
  tasks through the manager.
- For single-task intake, require executable lifecycle identifiers, a clear
  rejection, or explicit intake-only documentation. Do not create replacement
  one-task plans to work around raw task receipts that cannot be advanced
  through lifecycle endpoints.

## Verification

- Reread edited files after changes.
- Run the fastest relevant check first.
- Record checks run and failures in the handoff summary.

## Processes

- Ask before closing editors, apps, servers, or other visible processes.
- Launch GUI tools quietly in the background when possible.
