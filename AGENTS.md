# Agent Instructions

This is the lightweight runtime entrypoint for this project. Shared rules live
in focused modules under `patterns/AGENTS_RUNTIME/`; load only what the task
needs and prefer more specific project-local instructions, contracts, memory,
and runbooks over shared defaults.

## Project

TODO: describe the product, users, and primary runtime surface.

## Goal And Loading Contract

- Derive a bounded goal and observable success criteria from the request and
  project context. Ask only when missing information materially changes scope;
  continue independent authorized work while waiting.
- This file alone is sufficient only for greetings and status-neutral replies.
  Before concrete work, select the matching runtime modules.
- For a GI command, run
  `tools/get-gi-context.ps1 -CommandText "<exact user command>"`. It performs the
  staged update check, longest-prefix route resolution, and bounded retrieval.
  Use `COMMANDS.md` directly only for help or command-index requests.
- On the first concrete task in a session, perform the staged update check even
  without a GI command. Equal versions with no explicit skipped migrations mean
  `pending migrations: 0` without reading migration filenames, bodies,
  `CHANGELOG.md`, or `INDEX.md`. When the
  accepted source is newer, enumerate and apply pending accepted migrations if
  enabled; absent `auto_apply_pending_migrations` defaults to `true`. Skip only
  for explicit `false` or a concrete blocker, and report the pending count.
  Never inspect `updates/` during this startup check.
- Treat “do/follow strictly by GI” and equivalents as strict compliance with all
  loaded rules. Report a blocked operation precisely and continue independent
  authorized work.
- Before adding a clarification or approval gate, apply
  `patterns/AGENTS_RUNTIME/03-rule-precedence.md` and existing authorization.
- State-changing GI commands must not run from memory. If the context builder,
  route manifest, resolver, or a mandatory routed file is missing, stop that
  operation and name the missing path.
- Broad or unclear work requires `01-purpose.md`, `03-rule-precedence.md`,
  `06-tool-usage-and-token-economy.md`, and the most relevant task module.
  Cross-topic work requires every matching module.

## Core Safety And Boundaries

- Verify the active project root and target identity before writes. Treat this
  root as the normal filesystem boundary; exact external paths and actions need
  explicit authorization. Preserve unrelated dirty changes.
- A pasted credential is not a blocker for unrelated work. Warn once without
  repeating it, recommend rotation, and block only operations that cannot use it
  safely.
- Never commit secrets, private data, model weights, checkpoints, photos, video,
  audio, datasets, archives, or similar large content payloads. Use approved
  artifact storage and commit compact manifests, checksums, sources, or
  retrieval instructions unless the exact exception is explicitly approved.
- `tools/` is for durable reusable development and agent tooling. Product code,
  tests, docs, outputs, screenshots, exports, downloaded data, build bundles,
  and one-off probes belong in documented project locations.
  `tools/project-memory/` holds compact implementation-driving knowledge and
  evidence references, not bulk artifacts or a replacement for source/tests.
- During meaningful behavior or architecture work, keep scoped code, tests,
  affected docs, and focused project-memory contracts aligned before the
  implementation task is complete.
- For large modular systems, keep a project-local system map, focused module
  passports, and explicit public contracts. Agree on ownership and integration
  edges before independent agents implement both sides; verify assembled
  workflows. Follow `patterns/MODULAR_SERVICE_ENGINEERING.md`.
- Do not revert user changes without an explicit request. Ask before destructive
  operations, broad formatting churn, dependency replacement, data migration,
  public contract changes, or unrelated expansion.

## Runtime Routing

- Purpose, RAG, memory, summaries, connected projects: `01-purpose.md`
- Repository map: `02-repository-map.md`; precedence/scope: `03-rule-precedence.md`
- Authoring, configuration, quality, inventories: `04-content-and-authoring.md`
- Windows shell/networking: `05-windows-command-policy.md`
- Token economy and info/stack/logic/refactor: `06-tool-usage-and-token-economy.md`
- Startup/restore: `07-startup.md`; scope/evidence/cleanup: `07-scope-and-evidence.md`
- Config: `08-config-service.md`; task manager: `08-task-manager.md`; sprints: `08-sprint.md`
- Publication: `09-production.md`; deploy: `09-deploy-gateway.md`; FTP: `09-ftp.md`
- Runtime/restart/defaults: `09-runtime-and-defaults.md`; tests: `09-testing.md`
- Build/install: `09-build-and-install.md`; memory operations: `09-project-memory-operations.md`
- Private/missing context: `10-private-scope-and-missing-context.md`
- Language: `11-language-preferences.md`; UI: `12-ui-and-focus.md`; progress: `13-progress-updates.md`
- Updates: `14-update-intake.md`; verification: `15-verification.md`; Git: `16-git-policy.md`
- Roles: `17-agent-role-office.md`; product engineering: `18-startup-product-engineering.md`
- Game modding: `19-game-modding.md`

All paths above are under `patterns/AGENTS_RUNTIME/`. The legacy combined 07/08/09
files are compatibility indexes only and contain no operational rules.

## Project Memory And Working Areas

- Source: `TODO`; tests: `TODO`; outputs/evidence/build artifacts: `TODO`.
- Summaries: `tools/summary/`; durable project knowledge:
  `tools/project-memory/`; reusable tooling: `tools/`.
- Put product behavior, business rules, workflow contracts, architecture
  decisions, and verified implementation findings in project memory. Put normal
  documentation in `README.md`, `docs/`, and runbooks.
- Preserve text encodings. On Windows, send non-ASCII API/admin write bodies as
  explicit UTF-8 bytes with `charset=utf-8` or via Node `fetch`, then read back
  and check for replacement characters or mojibake.

## Local Commands

TODO: record install, run, test, build, and log-inspection commands in the
project runbook or package-native configuration instead of expanding this file.
