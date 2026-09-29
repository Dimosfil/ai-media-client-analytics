## Deploy Gateway

- Apply the project-local `config_service.enabled` toggle from
  `08-config-service.md` to every operation below. Query or write
  config-service only when integration is effectively enabled. When disabled,
  ordinary local operations use documented project-local runtime config;
  config-service-specific operations stop with the disabled-state blocker and
  point to `gi config on`.
- Treat `gi set devops`, `gi devops`, `ги девопс`, and equivalent wording as a
  request to mark the current project as a deploy-infrastructure owner for GI
  migrations and deploy commands. Verify the active project identity first, then
  create or update an ignored local marker such as
  `tools/project-memory/devops.local.json` with non-secret metadata: role
  `deploy-owner`, timestamp, reason, and optional deploy entrypoint or gateway
  contract pointer. This marker exempts the current project from GI migrations
  that remove project-owned direct deploy scripts or FTP/SFTP config, because
  the project is the deploy gateway itself. It does not grant permission to read
  unrelated projects, expose secrets, edit private gateway config from a
  consuming project, or treat any unmarked project as deploy infrastructure.
- Treat `gi deploy`, `ги деплой`, `gi deploy <method-or-path>`, and
  `ги деплой <способ-или-путь>` as requests to deploy the current project or site
  through the explicitly named method, service, saved deploy gateway, or deploy
  gateway path. If the argument is an absolute or clearly project-local path,
  treat that path as a user-authorized external deploy gateway and record it as
  the current project's selected deploy gateway in an ignored local file such as
  `tools/deploy/deploy-gateway.local.json`; it does not become the active
  editable source project. Future short deploy commands without a method or path
  should reuse the saved gateway. Store only local selection metadata there, such
  as gateway path, entrypoint, source-path parameter, project id, deploy mode,
  and target name; keep credentials and private remote paths in the gateway's
  own ignored config or secret store. Before running anything from that gateway,
  read its local `AGENTS.md`, `COMMANDS.md`, and deploy runbook such as
  `docs/deploy.md` when present. Prefer the gateway's single documented
  entrypoint, for example `tools/deploy/deploy.ps1`, and pass the current project
  root as `-SourcePath` or the gateway's documented source parameter. Pass
  project id, deploy mode, target name, or hosting-project mapping only when the
  gateway contract defines them. Do not infer credentials, print secrets, edit
  the gateway's private local config, run arbitrary helper commands from the
  gateway, or switch to treating the gateway as the product being deployed. If no
  argument is supplied and no selected gateway exists, stop and ask the user to
  make the full first call, for example `gi deploy <method-or-path>` /
  `ги деплой <способ-или-путь>`. Do not reinterpret a bare first `gi deploy` as
  `gi prod`, direct FTP upload, a build, or another deployment workflow. If the
  gateway contract, required entrypoint, source-path parameter, target mapping,
  or deploy mode is missing, ask one short clarification question instead of
  guessing.
- When the user's task explicitly targets preparing or repairing the deploy
  gateway itself, work in that gateway project and create or update the reusable
  deploy contract there: `AGENTS.md`, `COMMANDS.md`, a deploy runbook such as
  `docs/deploy.md`, one documented entrypoint such as
  `tools/deploy/deploy.ps1`, redacted config examples, and verification or
  rollback notes. Keep real secrets and private target paths in the gateway's
  ignored local config or secret store, not in shared instructions or consuming
  projects.
- During GI update migrations that retire project-owned direct deployment,
  non-devops projects must remove, disable, or stop relying on their own direct
  deploy/upload scripts, FTP/SFTP configs, and private deploy helpers. Preserve
  only ignored selected-gateway metadata such as
  `tools/deploy/deploy-gateway.local.json`, redacted examples, and documented
  build artifact contracts needed by the gateway. If the current project is not
  marked devops and no selected deploy gateway exists, stop and ask for the
  gateway path instead of uploading directly or creating a new personal deploy
  path. If the current project is marked devops, keep and maintain the deploy
  scripts/configuration as gateway-owned infrastructure.
- Treat `gi ftp <deploy-hub-path>` and `ги фтп <путь-к-deploy-хабу>` as the
  FTP/SFTP gateway variant: deploy the current project's configured build output
  through the user-provided deploy gateway path, using the gateway's documented
  entrypoint and passing the current project root as the source. Record the path
  as the current project's selected deploy gateway so later `gi ftp` / `ги фтп`
  can use it without repeating the path. The gateway owns FTP/SFTP
  configuration, destination selection, and secret references. Read its local
  instructions first, do not bypass the gateway by rewriting its private local
  JSON files, and do not upload directly unless the gateway contract explicitly
  delegates that operation back to the current project.
- When a deploy gateway accepts project registration, a `gi ftp <deploy-hub-path>`
  run for an unmapped current project should use the current project folder name
  as the default project id, derive the destination from the gateway's documented
  naming convention, register or update that project in the gateway-owned
  deploy registry, and continue through the gateway entrypoint. Unless the
  gateway contract explicitly names an existing target hostname, the derived
  public target must be project-scoped, such as a sanitized project id under the
  gateway's configured base domain. Do not target the apex/root domain, shared
  hub hostname, or another project's hostname as the upload/provisioning target
  for an unmapped project. The project agent should not ask the user to choose a
  remote folder, project id, or subdomain when the gateway contract defines
  deterministic registration; it should use the documented project-id-to-hostname
  rule or stop with the missing gateway contract. The gateway must also record
  enough non-secret metadata for later hub or index maintenance, such as project
  id, public URL or target name, source identity, deploy artifact path, deploy
  time/status, and whether a visible project card is pending. A pending
  domain/hosting request does not by itself stop artifact upload: if the gateway
  contract defines a pending, staging, queue, or handoff upload target, build and
  upload the current artifact there, then report the public site as pending
  devops/hosting publication. If registration, target provisioning, or artifact
  selection cannot continue, do not report a vague blocker; return an explicit
  deploy error with the failed step, evidence, responsible system or owner, next
  required action, and the artifact/source state already recorded. Never fall
  back to a root/default remote path or upload the whole repository.
- Before reporting an unknown deploy project, missing target mapping, or
  provisioning blocker, inspect the gateway-owned registry plus any documented
  project inbox, pending queue, hub-card queue, or domain/hosting request list.
  If the current project already has a pending or errored inbox entry, treat that
  entry as the active deploy state. For a pending entry, update it with the
  latest build/source metadata when the gateway contract allows, upload the
  artifact to the gateway's documented pending/staging/handoff target when one
  exists, and report that devops/hosting publication is still pending. For an
  errored entry or rejected request, first determine whether the evidence is a
  fresh result from the current deploy attempt or only a stale, cached,
  screen-derived, or external quota/provisioning claim. Stale or indirect
  evidence is warning context, not a stop condition: say that a provisioning
  error may occur, then run the gateway's documented create/refresh/provisioning
  attempt when it is safe and non-destructive. Stop only after the current
  attempt returns an explicit error, or when the gateway contract has no
  documented way to attempt or refresh provisioning. The stop report must name
  the failed domain/hosting/provisioning step, evidence, responsible system or
  owner, next required action, and artifact/source state. Do not ask the user
  for a different remote folder, create a duplicate mapping, target the apex/root
  domain, or upload into the gateway root merely because the final
  hosting-project map is not ready yet. If the gateway provides a documented
  request/inbox workflow for new domains, subdomains, or hosting slots, create
  or refresh that non-secret request for the project-scoped hostname before deciding
  whether to continue artifact upload or return an explicit error.
