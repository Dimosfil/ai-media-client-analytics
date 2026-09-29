## Runtime, Docker, First Launch, And Defaults

- Apply the project-local `config_service.enabled` toggle from
  `08-config-service.md` to every operation below. Query or write
  config-service only when integration is effectively enabled. When disabled,
  ordinary local operations use documented project-local runtime config;
  config-service-specific operations stop with the disabled-state blocker and
  point to `gi config on`.
- Treat `gi reboot`, `ги ребут`, `gi restart`, and `ги рестарт` as requests to
  start or restart all documented applications in the current project using
  project-local run instructions. Before starting anything, identify the full
  app set from local run instructions, manifests, service records, desktop
  packaging metadata, or project memory; do not assume a successful web/API
  start covers the project. For local web/API services with config-service
  integration enabled, resolve the service id, port, URL, and neighboring
  endpoints through config-service before running a start command; fixed ports
  in local runbooks or examples do not authorize a fallback bind. With
  integration disabled, use only the documented project-local run config and
  stop if required runtime values are missing. If the selected port is occupied,
  verify whether the owner is
  the same documented service instance using project-local identity signals
  such as service id, command, cwd, health endpoint, or process metadata. If the
  port belongs to another service or ownership is unclear, stop and report the
  port-conflict blocker; do not stop the owner without explicit user approval
  and do not move the requested app to another port. If the owner is the same
  service, restart or reuse it only through the documented run contract. If a
  config-service record is missing, use only the documented
  config-service registration workflow from `08-config-service.md`
  to create or update it before startup, or stop with the exact missing
  contract. If local instructions define a preferred start/restart command that
  launches the full app set, use it with the runtime values selected by the
  enabled config-service flow or the disabled project-local flow. Otherwise
  enumerate every documented app or
  runtime, such as desktop app, web/API app, and background workers, then
  restart each running app and start each missing app. Launch in the background
  so focus does not jump away from the user's current window. After launch, wait
  briefly and verify the documented startup success signal for each app:
  still-running expected processes, visible desktop windows when applicable,
  health/discovery endpoints for web/API apps, and relevant startup or crash
  logs when documented. The final report must account for each app by name or
  role with started/restarted/skipped status and verification evidence. Do not
  report reboot success from a PID alone, from a web health check alone, or
  while any expected desktop app, web/API app, or worker is unlaunched or
  unverified. If a documented desktop app lacks a launch command or window
  verification signal, report that as a blocker or partial failure instead of
  success. If any app exits, no expected window or health signal appears, or a
  new startup traceback is present, report the reboot as failed or partially
  unverified with the concrete evidence. Published hosting environments follow
  their hosting or production deploy contract and are not restarted by local
  `gi reboot` unless project-local production instructions explicitly define
  that behavior.
- Treat `gi docker`, `ги докер`, and equivalent Docker restart wording as a
  request to restart the current project's documented Docker or Docker Compose
  runtime, rebuilding first only when local Docker state requires it. Read
  project-local Docker/run instructions, Dockerfile or Containerfile,
  `compose.yaml`, `compose.yml`, `docker-compose*.yml`, container scripts,
  manifests, service records, and project memory before touching containers. If
  the project has no Docker/Compose config and no documented Docker run
  contract, report that Docker is not configured for this project and stop
  instead of inventing commands. If Docker CLI, Docker Compose, or the Docker
  engine is unavailable or not running, report that blocker and do not claim a
  restart. Rebuild before restart when the image is missing, the local Docker
  contract says to rebuild, Dockerfile/Compose/build-context/dependency
  manifests changed since the known running image, or freshness cannot be
  confidently proven. Prefer project-documented commands; otherwise use the
  narrow project Compose operation, such as `docker compose up -d --build` when
  rebuilding is needed and `docker compose up -d` or the documented restart
  command when the existing image is current. Scope all operations to the
  current project only: do not prune Docker system state, remove volumes, delete
  images, or stop unrelated containers. After the operation, verify documented
  container status, health checks, mapped service URLs, and recent logs when
  failures appear, then report rebuilt/restarted/not-configured/blocked status
  with evidence.
- Treat `gi first test`, `gi первый тест`, and `ги первый тест` as requests to
  verify the current application's first-launch experience by resetting only
  documented project-owned app cache, generated state, temporary first-run
  profiles, and rebuildable local app settings. Read project-local run, cleanup,
  cache reset, and test instructions first. Do not delete user documents,
  production data, secrets, credentials, external service data, shared system
  caches, sibling projects, or arbitrary user-home folders. If exact reset
  paths, keys, scripts, or commands are missing, ask one short clarification
  question instead of guessing. After reset, start the app, run the documented
  first-launch smoke/onboarding checks, and report what was cleared, what
  passed, and what was intentionally left untouched.
- Treat `gi default`, `gi defaults`, and `ги дефолт` as requests to restore the
  current project to its documented first-run/default state. Read project-local
  reset, cleanup, first-run, run, backup, and test instructions first. Use only
  documented reset scripts, paths, keys, or contracts for project-owned app
  state, generated caches, local settings, onboarding flags, temporary profiles,
  runtime logs, queues, worker state, generated test databases, browser storage
  for the app origin, and other rebuildable state. Preserve only exclusions
  explicitly documented by the current project; do not infer exclusions from old
  chat, screenshots, stale run artifacts, or browser state. Do not delete source
  files, project-memory specifications, instruction-kit files, user documents,
  production data, secrets, credentials, external service data, shared system
  caches, sibling projects, or arbitrary user-home folders. If reset targets are
  not documented, ask one short clarification question instead of guessing. If a
  reset could be irreversible or remove user-owned data, stop for explicit
  confirmation and prefer a backup or rename step when local rules allow it.
  After reset, start the project through documented run instructions, verify the
  default or first-launch success signals, and report what was reset, what was left
  untouched, what passed, and any blocker.
