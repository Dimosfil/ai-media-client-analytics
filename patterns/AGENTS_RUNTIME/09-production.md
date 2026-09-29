## Production Publication

- Apply the project-local `config_service.enabled` toggle from
  `08-config-service.md` to every operation below. Query or write
  config-service only when integration is effectively enabled. When disabled,
  ordinary local operations use documented project-local runtime config;
  config-service-specific operations stop with the disabled-state blocker and
  point to `gi config on`.
- Treat `gi prod`, `gi production`, `gi прод`, and `ги прод` as requests to
  publish the current development version of an online service into its
  documented production service folder. Use this only for services that run
  continuously against real remote APIs, webhooks, chats, marketplaces,
  payment providers, or other live external systems. Normal development,
  refactoring, tests, formatting, cleanup, and `gi restart` operate on the
  development checkout/service and must not edit, stop, reset, or test against
  the production service folder unless the user explicitly invokes the
  production command or local instructions define a stricter production
  workflow. Before `gi prod`, read project-local run/deploy instructions,
  service contracts, production folder config, secret-handling rules, ignore
  rules, and verification requirements. The production folder is a live runtime
  target, not the editable source of truth: never copy production secrets,
  databases, logs, caches, user data, or remote API state back into development.
  Build or prepare the documented artifact from the development checkout,
  exclude dev caches and generated noise, sync only approved source/build files
  into the production folder, preserve production-local config and secrets, and
  use an atomic or backup/rollback-friendly handoff when local tooling supports
  it. If the production folder, include/exclude rules, restart/switchover
  command, health check, or rollback path is undocumented, ask one short
  clarification question instead of guessing. After publishing, verify the
  production service with the documented health signal or harmless remote-API
  check and report exactly what was synced, what production-local state was
  preserved, whether the live service was restarted or left running, and any
  unverified risk. Follow `patterns/PROJECT_DEV_PROD_SERVICES.md`.
