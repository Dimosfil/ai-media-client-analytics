## Config Service And Runtime Discovery

- Treat `gi config`, `gi конфиг`, `ги конфиг`, `gi config service`,
  `ги конфиг сервис`, `ги конфиг сервис url=<url>`, and
  `ги конфиг сервис урл=<url>` as requests to get or set the bootstrap config
  for the config/discovery service. Read the
  project-local override only if local instructions define one, then read GI
  main config from the configured shared-instruction source repo checkout/cache,
  the current shared-instruction checkout, or `GENERAL_INSTRUCTIONS_HOME`. Use
  its `config/gi-main.json` `configServiceUrl` to query the config service.
  Resolve local app and task-manager runtime URLs by service id through
  config-service; project task-manager config should keep only the selected
  manager name/id and non-secret project preferences. For the `url=<url>` form,
  validate a full `http://` or `https://` URL with no secrets, update the shared
  `configServiceUrl` or the explicit project-local override, and tell services
  to use that URL for registration and discovery. Do not scan sibling project
  folders, guess ports, copy URLs from old task-manager memory, or use stale
  task-manager records as a runtime fallback. For inspection forms, report the
  explicit and effective integration-toggle state, including whether an absent
  field is using legacy `true`, before reporting URL or registration settings.
- Treat `gi config on`, `gi config off`, `gi конфиг вкл`, `gi конфиг выкл`,
  `gi конфиг он`, `gi конфиг офф`, `ги конфиг вкл`, `ги конфиг выкл`,
  `ги конфиг он`, and `ги конфиг офф` as the project-local config-service
  integration toggle. Store the explicit state as `config_service.enabled` in
  `tools/project-memory/instruction-kit.json`. Fresh GI bootstraps must create
  this setting as `false`. To preserve working integrations, an existing
  project whose metadata has no `config_service.enabled` field uses the legacy
  effective value `true`; migrations must not insert `false` into such projects.
  `on`/`вкл`/`он` writes `true`, and `off`/`выкл`/`офф` writes `false`. Any
  short `gi config <toggle>` or `ги конфиг <toggle>` form without the explicit
  `service`/`сервис` segment controls this whole-project integration toggle and
  must never be interpreted as the app self-registration flag. When disabled, do
  not query config-service, self-register, or require config-service discovery
  during ordinary startup; use only documented project-local runtime config.
  A command that inherently requires config-service, including manager-backed
  task commands, must stop with a concise disabled-state blocker and point to
  `gi config on`. Do not reinterpret this toggle as starting or stopping the
  config-service process.
- For agent-facing HTTP services, prefer a service-owned guide endpoint plus a
  strict contract endpoint. Resolve runtime URLs through config-service. Read
  `endpoints.guide` first when present, then `endpoints.contract` before
  sending state-changing requests. Treat the guide as onboarding and the
  contract as workflow validation. If they disagree, stop and report the
  mismatch. Do not infer permissions from filesystem paths, stale memory, old
  dashboard URLs, or raw task receipts.
- Treat `gi config service on`, `gi config service off`, `ги конфиг сервис on`,
  `ги конфиг сервис off`, `ги конфиг сервис вкл`, `ги конфиг сервис выкл`,
  `ги конфиг сервис он`, and `ги конфиг сервис офф` as requests to set the current application's
  project-local config-service self-registration flag. `on` means the app
  should publish or refresh its own service record during startup; `off` means
  it must not. Do not reinterpret this as starting or stopping config-service
  itself. When setting `on`, first confirm a config-service URL is already
  configured in the same local config area or documented GI bootstrap config; if
  no URL is configured, tell the user to set `gi config service url=<url>`
  before enabling self-registration. Ask one short question if no local config
  location is documented.
- When the project-local config-service integration toggle is enabled, for
  web-facing applications that expose a port, HTTP API, web UI, task-manager
  service, or local daemon endpoint, require a live config-service lookup before
  the process binds or reserves any port in local development. On every local
  startup, read the configured config-service URL, verify the config service is
  reachable, and query the app's own `service_id` startup/service record. If
  the record exists, bind only the recorded port and use config-service records
  for neighboring service endpoints. Before starting a new process, check
  whether the recorded port is already occupied. If it is occupied by the same
  documented service instance, restart or reuse it only as the local run
  contract allows. If the owner is another service, unknown, or cannot be
  verified from documented identity signals such as service id, command, cwd,
  health endpoint, or process metadata, stop with a port-conflict blocker. Do
  not kill the owner without explicit user approval and verified ownership, and
  do not bind an alternate port just because the recorded one is busy. Changing
  the port changes the browser origin and can hide browser-owned state such as
  localStorage, cookies, and IndexedDB. Treat ports and URLs in README files,
  runbooks, old logs, screenshots, package metadata, and examples as hints for
  documentation drift only; they are not runtime authority until reflected in a
  config-service record. If the record is missing and project-local
  self-registration is `on`, read the config-service guide and contract, list
  existing records, select or request a local development port only through that
  contract, create or update the service record, then start the app using the
  recorded value and verify its health endpoint. If the record is missing and
  self-registration is `off`, or config-service lacks a documented registration
  contract, stop with a clear blocker; do not invent payloads, write storage
  directly, reuse stale local config, or bind a fallback port while
  config-service is unavailable. If the recorded endpoints changed, refresh the
  record only after the config-service check succeeds. Desktop apps, CLI tools,
  libraries, scripts, and other non-web applications must not query or publish
  to config-service during normal startup unless local instructions explicitly
  define a discoverable web/API runtime. Production, hosting, and remote deploy
  targets use their own hosting/deploy runtime contract rather than the local
  config-service flow unless the project-local production instructions require
  config-service there too.
