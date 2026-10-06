## Full-System Verification

- Apply the project-local `config_service.enabled` toggle from
  `08-config-service.md`. Query or write config-service only when integration
  is effectively enabled. Otherwise use documented project-local runtime
  configuration; do not invent a discovery fallback.
- Run this flow for `gi full test`, `gi release test`, `gi system test`, or a
  selected `gi test start` scenario explicitly requiring full-system checks.
  Load the active task from the current message, chat, or project-local source;
  if none exists, ask one short question before dependent execution.
- Read current local instructions, README, manifests, runbooks, test configs,
  and relevant source entrypoints to confirm commands, services, apps, ports,
  routes, payloads, environment, storage, auth, queues, workers, and health.
- Before execution, restore project-owned runtime state to the documented
  default/factory baseline using the same reset contract as `gi default`.
  Preserve documented exclusions, user data, secrets, and production-local
  state. Browser storage, generated test databases, logs, queues, temporary
  workers, and caches require documented reset targets and exceptions. If reset
  targets are absent or user-owned data is ambiguous, report that blocker;
  do not perform a guessed reset or claim a dirty-state full test passed.
- Read back effective runtime settings after reset from project-local config,
  backend state, discovery, or database metadata. UI-only browser state is not
  the source of truth for a selected chain, preset, execution mode, ports, task,
  or endpoints. Persist required selection through its documented contract or
  report the missing contract.
- Start or restart documented apps as needed and run the verification ladder
  through the broadest suite justified by the task. Exercise live required
  surfaces: app processes, API/backend, storage, queues/workers, UI/auth,
  discovery, orchestrator or agent handoff loops, and health/contract endpoints
  where defined. Follow `09-testing.md` for scope, authorization, evidence,
  restoration, completion states, and reporting.
- Do not use dry-run, simulation, dispatcher-only execution, replayed logs,
  mock-only runs, or compile/unit-only checks as a full-system test result.
  Run dry-run only when explicitly requested as a diagnostic. Supporting unit
  and isolated tests remain useful but cannot replace required live surfaces.
- If required live services, workers, apps, or UI are unreachable, report the
  full-system test as blocked or not checked. Old summaries, screenshots,
  completed demos, prior statuses, and chat snippets are evidence only. Rerun
  current checks or name the blocker; do not substitute an old result.
