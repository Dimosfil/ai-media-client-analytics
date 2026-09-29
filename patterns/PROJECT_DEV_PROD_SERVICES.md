# Project Dev/Prod Services

Use this pattern when a project contains a service that stays online against
real remote APIs while development continues in a separate working copy.

## Intent

- Treat the normal project checkout as the development source of truth.
- Treat the production service folder as a live runtime target for a deployed
  copy of the service.
- Use this pattern for continuously running integrations such as bots,
  webhook receivers, marketplace connectors, payment integrations, workers, or
  other services connected to live external APIs.
- Do not apply this pattern to ordinary build artifacts, static exports, local
  test servers, or FTP/SFTP upload targets unless the project explicitly maps
  them to the same production service workflow.

## Command

- `gi prod`, `gi production`, `gi прод`, and `ги прод` publish the current
  development version into the documented production service folder.
- The command does not mean "edit production directly", "pull files back from
  production", or "deploy to FTP" unless local instructions explicitly combine
  those workflows.
- If a project defines a more specific production command, script, or runbook,
  use that local contract.

## Required Local Contract

Before publishing, identify the project-local production contract:

- production folder path;
- source or build artifact to publish;
- include and exclude rules;
- production-local config and secret locations to preserve;
- backup, rollback, or atomic swap strategy;
- service stop/restart/reload or zero-downtime handoff command;
- health check or harmless remote-API verification;
- files that must never be copied from production back into development.

Keep this contract in project-local docs or project memory. A good default
location for private machine-specific settings is `tools/deploy/prod.local.json`
or an equivalent ignored local file.

## Safety

- During ordinary development, do not edit, format, reset, delete, search
  broadly, or run tests inside the production service folder.
- Do not stop or restart the production service during `gi restart`,
  `gi test`, `gi default`, `gi first test`, refactors, or cleanup unless the
  user explicitly invokes the production workflow or local instructions make
  that action part of the requested command.
- Never copy production secrets, credentials, local databases, queues, message
  offsets, sessions, user uploads, logs, caches, or remote API state into the
  development checkout.
- Never overwrite production-local `.env`, config, credentials, runtime
  databases, logs, caches, webhook state, or service manager files unless the
  project-local production contract explicitly says they are generated and safe
  to replace.
- Keep real remote API credentials separate from development credentials. Prefer
  sandbox, test, or separate bot/application tokens for development.
- Prefer managed secret stores, KMS, vaults, deployment secrets, or equivalent
  production secret backends for live service credentials. When the provider
  supports scoped credentials, usage monitoring, rotation, or network
  restrictions such as IP allowlists, document and use those controls in the
  project-local production contract. Follow
  `patterns/API_KEY_SECRET_SAFETY.md`.
- If the production folder lives under the repository root, ensure it is
  excluded from commits unless the project deliberately tracks a deployable
  production tree.

## Workflow

- Read the local production contract, runbook, manifests, service manager
  config, and deployment scripts before taking action.
- Build or prepare the development artifact with the documented production
  build command when required.
- Create a backup, staging folder, or atomic swap candidate when local tooling
  supports it.
- Sync only approved source/build files from development to the production
  service folder.
- Preserve production-local config, secrets, runtime state, logs, caches, and
  service metadata.
- Restart, reload, or switch over the production service only through the
  documented command. If no command is documented, leave the service running and
  report the missing handoff step.
- Verify with the documented health signal, local process/service status, or a
  harmless remote-API check. Do not send real customer/user messages or mutate
  remote production data as a smoke test unless the runbook explicitly allows
  it.

## Missing Context

If any required production detail is missing, ask one concise clarification
question. Do not infer a production folder from sibling directories, old chat
history, process names, port scans, webhook URLs, or secrets found on disk.

## Reporting

After `gi prod`, report:

- development source or artifact used;
- production folder updated;
- preserved production-local files or state categories;
- restart/reload/switchover action, or that the service was left running;
- verification performed;
- rollback or backup location when one was created;
- blockers or unverified risks.
