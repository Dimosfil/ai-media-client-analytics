## FTP And SFTP Upload

- Apply the project-local `config_service.enabled` toggle from
  `08-config-service.md` to every operation below. Query or write
  config-service only when integration is effectively enabled. When disabled,
  ordinary local operations use documented project-local runtime config;
  config-service-specific operations stop with the disabled-state blocker and
  point to `gi config on`.
- Treat `gi ftp`, `ги фтп`, `gi ftp push`, `ги фтп пуш`, `gi upload ftp`,
  `gi deploy ftp`, and `gi залей на фтп` as requests to upload the current
  project's configured build output to FTP, FTPS, or SFTP. Treat
  `gi ftp config`, `gi ftp конфиг`, and `ги фтп конфиг` as requests to create,
  inspect, or update the project-local FTP/SFTP config without uploading. Treat
  `gi ftp folder`, `gi ftp папка`, and `ги фтп папка` as requests to inspect,
  choose, or update the remote upload folder (`remotePath`) without uploading.
  Treat `gi ftp service`, `gi ftp сервис`, and `ги фтп сервис` as requests to
  manually register, inspect, or select an FTP/FTPS/SFTP service record in
  config-service without uploading. In non-devops projects, these commands must
  use the saved deploy gateway or ask for one; they must not create or use a
  project-owned direct FTP/SFTP deploy path. Direct project-local FTP/SFTP
  upload is allowed only in a project marked devops, or when a documented deploy
  gateway contract explicitly delegates that upload operation back to the
  current project. Read project-local deploy instructions and selected gateway
  metadata first; read `tools/deploy/ftp.local.json` only for a devops project
  or documented gateway delegation. When a devops project needs FTP and local
  config does not name a target service, query config-service for FTP-capable
  services.
  If exactly one matching service exists, use it after verifying its contract;
  if several exist, ask the user to choose with the same plain inline numbered
  checkbox marker style used by language selection. Keep secrets out of
  config-service:
  store only discovery metadata and secret references such as environment
  variable names. Keep project-specific deploy settings in the separate
  project-local config file rather than shared instructions or chat history.
  Treat upload stalls, hangs, repeated timeouts, and failed stream opens as
  failed FTP/FTPS transfers. When FTP/FTPS upload fails or is unreliable,
  immediately check the selected service contract, project-local config, and
  user-provided details for an authorized SSH-based SFTP route to the same
  remote deploy folder. If the needed SSH host, port, user, and credential
  reference are available, switch to SFTP over SSH before more FTP/FTPS upload
  variants and report that fallback. If they are missing, report the exact
  missing SFTP details instead of inventing credentials or retrying the same
  failing FTP path. Do not disable TLS certificate validation or accept invalid
  FTPS certificates as a routine fallback unless the deploy contract or current
  user message explicitly authorizes that degraded security path.
  Prefer `tools/deploy/ftp.local.example.json` only as a redacted shape. Do not
  commit hostnames, usernames, passwords, tokens, private keys, or private
  remote paths unless project policy explicitly marks them non-secret. Follow
  `patterns/PROJECT_FTP_DEPLOY.md`.
