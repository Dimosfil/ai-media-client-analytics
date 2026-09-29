## Build And Installer Packaging

- Apply the project-local `config_service.enabled` toggle from
  `08-config-service.md` to every operation below. Query or write
  config-service only when integration is effectively enabled. When disabled,
  ordinary local operations use documented project-local runtime config;
  config-service-specific operations stop with the disabled-state blocker and
  point to `gi config on`.
- Treat `gi install`, `gi инсталл`, `ги инсталл`, and obvious typo variants
  such as `gi иснтлл` as requests to build the current project and produce an
  installer. Use Windows as the default target platform when the user and the
  project-local packaging contract do not name a different platform. For
  Windows, use Inno Setup by default when no installer tool is named. If the
  user writes a program after `gi install` / `gi инсталл`, use that program as
  the preferred packaging tool. If the user names macOS, iOS, Android, Linux,
  or another platform, or the project-local packaging contract selects one,
  follow that platform's local build, signing, packaging, and artifact
  verification contract instead of falling back to Windows. Ask a short
  clarification question if the named platform is supported by the project but
  its packaging contract is missing or ambiguous. Read project-local build and
  packaging instructions, scripts, manifests, and installer configs first.
  Keep build instructions, packaging configs, signing/notarization/provisioning
  notes, verification notes, and produced installer artifacts separated by
  target platform in project-local folders or per-platform artifact manifests.
  Follow the project's existing packaging layout when it has one; when creating
  or repairing a layout, use platform-specific folders such as
  `packaging/windows/`, `packaging/macos/`, `packaging/ios/`,
  `packaging/android/`, `packaging/linux/`, or equivalent project-local names.
  Do not mix artifacts for different platforms in one unscoped output folder.
  Resolve the application version from project-local metadata such as
  manifests, package files, assembly attributes, release files, or installer
  configs before packaging; update the version in build output, installer
  metadata, and the installer filename or artifact name when the local tooling
  supports it.
  `restore`, dependency install, build, and test checks are prerequisites only:
  they do not complete `gi install` unless the packaging command also runs and
  a current installer artifact is produced or explicitly verified. Do not report
  the project as installed/restored when only verification ran; report the
  installer artifact path, version, and checks after successful packaging. Ask a
  short clarification question if the build, installer, or versioning contract
  is missing instead of inventing one.
- Treat `gi build`, `gi собрать`, `ги билд`, `ги собрать`, `gi rebuild`, and
  `ги ребилд` as requests to build or rebuild the current project or
  application only, producing the documented release/upload-ready output such
  as a static `dist/`, bundle, executable, package, or other artifact. Read
  project-local build or rebuild instructions, manifests, scripts, hosting
  base-path/public-path config, and packaging metadata before running the
  documented command.
  Do not treat these project build commands as dependency restore, tests-only
  verification, FTP/SFTP upload, production publication, installer packaging,
  or any RAG/GI tooling rebuild, and do not combine them with a RAG rebuild
  unless the user explicitly asks for both. If no project build/rebuild
  contract exists, ask one short clarification question instead of inventing a
  command. Use `gi ftp` for upload, `gi prod` for documented production
  publication, `gi install` for installer packaging, and `gi tools rebuild` or
  `gi rag rebuild` when the GI/RAG layer itself must be rebuilt.
