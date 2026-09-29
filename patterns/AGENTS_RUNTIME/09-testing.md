## Full Project Testing

- Apply the project-local `config_service.enabled` toggle from
  `08-config-service.md` to every operation below. Query or write
  config-service only when integration is effectively enabled. When disabled,
  ordinary local operations use documented project-local runtime config;
  config-service-specific operations stop with the disabled-state blocker and
  point to `gi config on`.
- Treat `gi test task`, `gi testing task`, `gi тест таск`, `ги тест таск`,
  `gi задача теста`, and equivalent wording as requests to set the active
  release/full-system verification workload for the current project. The
  supplied task text is the user-selected scenario for the next `gi test`; it is
  not evidence that the scenario already passed. Record it in the
  project-local test task location when local instructions define one,
  otherwise keep it as current chat context and report where it is tracked.
  Do not replace this with a generic `gi test plan`, old task status, demo
  artifact, or stale handoff summary.
- Treat `gi test`, `ги тест`, `gi full test`, `gi release test`,
  `gi system test`, and equivalent full-project test wording as requests to
  run the current project's documented full verification flow against the
  active test task. Do not confuse this with `gi test plan`, which remains a
  plan-only command by default. First load the active test task from the current
  message or project-local memory; if none exists, ask one short question for
  the test task before running. Then read project-local instructions, README,
  manifests, runbooks, test configs, and source entry points needed to identify
  exact current commands, services, app set, ports, routes, payloads,
  environment variables, storage, auth, queues, workers, and health checks.
  Before executing the verification ladder, restore the project-owned runtime
  state to the documented default/factory baseline using the same reset contract
  as `gi default`, while preserving only project-local exclusions that are
  explicitly documented for the current project. Examples of exclusions may
  include secrets, production-local state, user data, configured external
  service credentials, or named persistent fixtures; browser `localStorage`,
  cookies, IndexedDB, generated test databases, runtime logs, queues, temporary
  worker state, and app caches are not exclusions unless the current project's
  reset contract says so. If the project has no documented reset targets or the
  reset would touch ambiguous user-owned data, stop with that blocker instead
  of running a dirty-state test. After reset, read back the effective runtime
  configuration from the project-local source of truth, such as config files,
  backend state, service discovery, or database metadata. UI-only browser state
  is not a valid source of truth for selected chain, preset, execution mode,
  ports, task, or service endpoints; if the live test depends on such a value,
  persist it through the documented backend or project-local config first, or
  report the missing contract as the blocker.
  Start or restart documented apps when needed, run the verification ladder
  through the broadest documented suite justified by the command, and report
  the task used, commands run, results, blockers, and unverified areas. For
  `gi test`, dry-run mode is retired as a validity path: do not use `--dry-run`,
  simulation mode, dispatcher-only execution, replayed logs, mock-only runs, or
  compile/unit-only checks as the test result, and do not run dry-run mode at
  all unless the user explicitly asks for that diagnostic mode. If explicitly
  requested, label it as diagnostic and never report it as a passed `gi test`.
  A full-system `gi test` must exercise the documented live runtime surface for
  the selected task, including application processes, API/backend, storage,
  queues or workers, UI/auth flows, service discovery, orchestrator or agent
  handoff loops, and health/contract endpoints when the project defines them.
  If the live services/apps/workers/UI cannot be started or reached, report
  `gi test` as blocked or not checked instead of substituting a dry-run. Old
  summaries, screenshots, completed demo artifacts, previous task statuses, and
  old chat snippets are evidence only; they do not satisfy a fresh `gi test`
  request. Rerun the current documented checks or report the exact blocker that
  prevents a rerun.
