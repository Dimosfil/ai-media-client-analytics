## Content And Authoring

- Keep instructions reusable across projects.
- Do not add secrets, credentials, private project data, or local machine paths
  unless the file is explicitly a local example.
- If a rule applies only to one specific project, do not put it here.
- If a feature workflow applies only to one project, keep it in that project's
  local docs or project memory. Use shared instructions only for the reusable
  rule that such contracts should exist and be respected.
- When explaining, documenting, or adding a shared GI rule, keep the explanation
  project-agnostic. Do not anchor the rule in the current project, a recent bug,
  one demo, one product name, or one repository unless the user explicitly asks
  for that concrete comparison. Use neutral terms such as "a development tool",
  "a generated product", "a selected run", or "a service"; if an example is
  necessary, mark it as illustrative and keep it replaceable.
- When deriving a reusable rule from a concrete request, bug, screenshot, demo,
  or implementation detail, extract the portable principle before writing the
  rule. Do not promote incidental entities, object types, years, filenames,
  local paths, data partitions, model names, UI labels, query text, or one
  selected workflow into shared defaults, policies, architecture, or examples.
  Treat the concrete case as evidence, then restate it in neutral terms and map
  the principle to configuration, contracts, adapters, manifests,
  user-selected state, or project-local memory as appropriate.
- Prefer small, focused documents over one giant policy file.
- When adding a new instruction file, also add it to `INDEX.md`.
- Write instruction documents in imperative voice, with one rule per bullet when
  practical.
- Avoid long nested conditionals, filler, narration, and non-actionable prose.
- Use clear Markdown headings and copy-pasteable examples.
- Keep developer tools, orchestrators, task managers, agent harnesses, and code
  generators separate from the products they build. Never hard-code one demo,
  customer, project type, workflow run, product name, UI label, folder slug,
  stack, or task contract as if it were part of the development runtime.
  Generated applications, sites, bots, dashboards, libraries, and other
  artifacts are input/output of the tool, not the tool's identity. Model
  selected or active workflow state as data, show debug/progress logs only for
  the selected run, and keep completed runs compact. Follow
  `patterns/DEVELOPMENT_TOOL_PRODUCT_BOUNDARIES.md`.
- Treat `tools/` as a place for project-owned development and agent tooling
  only: scripts, adapters, bootstrap commands, deployment helpers,
  verification helpers, agent-memory tooling, and redacted examples or
  manifests. Before creating or moving any file under `tools/`, classify
  whether the file is tooling or product material. Product runtime/source
  packages, product plugin implementations, product tests, full product
  documentation, generated product output, selected-run artifacts, uploaded
  site contents, screenshots, raw exports, build bundles, downloaded datasets,
  and one-off work results must not be placed under `tools/`. Put product code
  under the project's source/package locations, tests under the test tree,
  product docs under `README.md`/`docs/`/runbooks, and artifacts under
  project-local artifact, evidence, output, data, docs-asset, build, or release
  locations documented by the project. `tools/project-memory/` may contain
  compact implementation-driving specifications and evidence references, but
  it must not become the only product documentation layer or a home for source,
  tests, runtime packages, generated outputs, or bulky evidence.
- Classify scripts by lifecycle and reuse, not by extension. A Python,
  PowerShell, shell, or other executable created only to answer the current
  research question, probe one environment, scrape one source, inspect one data
  case, or run a throwaway diagnostic is one-off work, not durable tooling. Do
  not place it in `tools/`, `tools/research/`, `tools/probes/`, or a similarly
  named tooling subtree. Prefer an inline command; if a file is necessary, use
  a documented ignored project scratch/temp location outside `tools/`, remove
  it after use, and store only required outputs in the documented evidence or
  artifact location. Promote a script into `tools/` only when it has a
  project-owned reusable purpose, stable interface, documentation, and an
  expected future caller.
- Do not hard-code values that can change by deployment, user choice, runtime
  environment, host machine, service discovery, credentials, filesystem layout,
  feature flags, product names, demo data, workflow labels, generated artifact
  names, UI copy that names a specific project, language translation maps,
  synonym dictionaries, intent-interpretation rules, query-normalization rules,
  model-specific prompt expansions, ranking thresholds, or operational policy.
  Keep application code focused on logic, constants, and internal defaults; move
  deploy/user/environment/system/product-selection/model-behavior values into
  documented project-local configuration, environment variables, service
  discovery records, manifests, task payloads, resource files, adapters,
  interpretation/translation modules, or user-selected state. Such modules may
  be deterministic resources, local algorithms, retrieval-backed components, or
  provider-swappable LLM adapters. Avoid embedding machine-specific absolute
  paths in source or shared instructions; when paths are accepted from config,
  resolve and validate them as absolute paths at the application boundary. When
  applying this rule to existing projects, audit and refactor relevant
  hard-coded values instead of only adding the rule text. If a shortcut, legacy
  compatibility case, or test expectation would require violating this boundary,
  first implement the compliant config/resource/adapter path; ask only when the
  source of truth or temporary compatibility layer is genuinely undocumented.
  Follow
  `patterns/CONFIGURATION_BOUNDARIES.md`.
- Classify external variables as startup-critical or optional by their actual
  dependency. Give optional variables safe defaults, validate overrides, and
  disable only the dependent backend/UI capability when an optional value is
  absent or invalid. Keep the core running and surface a sanitized reason;
  never use dummy credentials as valid defaults. Fail clearly for invalid
  startup-critical values and cover them in local startup and tests. Follow
  `patterns/CONFIGURATION_BOUNDARIES.md`.
- Treat API keys and external-service tokens as secret boundaries, not ordinary
  config values. Keep them out of source, client bundles, public frontend env
  vars, logs, traces, chat, generated artifacts, and project memory; prefer
  per-person or per-service credentials, separate dev/staging/prod secrets,
  managed production secret stores, scoped permissions, usage monitoring,
  rotation, and network restrictions where supported. Follow
  `patterns/API_KEY_SECRET_SAFETY.md`.
- Do not turn a credential pasted into chat into a whole-task development
  blocker. Warn once without repeating the value, recommend rotation, and keep
  working on every independent step that can be completed without exposing or
  unsafely persisting the credential. Block or leave unverified only the
  specific operation that has no safe credential path.
- Build applications with clear architecture and code-quality boundaries.
  Choose the paradigm that fits the stack; apply SOLID, DRY, KISS, YAGNI, and
  separation of concerns to classes, modules, functions, components, or systems
  where they help. Keep domain/product logic, orchestration, UI, persistence,
  filesystem, external services, and configuration behind explicit boundaries.
  Record measurable quality goals and significant architecture tradeoffs. Follow
  `patterns/ARCHITECTURE_AND_CODE_QUALITY.md`.
- For large modular systems, keep a project-local system map, module passports,
  and public contracts. Coordinate agents through those contracts and verify an
  assembled workflow. A module need not be a deployable service. Follow
  `patterns/MODULAR_SERVICE_ENGINEERING.md`.
- Treat senior agent behavior as a compact engineering execution standard, not
  as a separate personality label. Before code changes, agents should load
  relevant local context, preserve intended behavior, keep architecture and
  configuration boundaries clear, work in coherent verified batches, update
  durable project memory when behavior or architecture changes, and escalate
  high-risk actions through the documented approval path. Follow
  `patterns/SENIOR_AGENT_ENGINEERING_STANDARD.md`.
- Use an agent role office when specialist judgment improves the work. Select
  the smallest useful set of professional role lenses, such as product owner,
  tech lead, C#/.NET backend, frontend, UI/UX design, visual art, QA,
  DevOps/release, security, or documentation, then synthesize their input into
  one accountable plan, implementation, or review. When development begins,
  infer and briefly propose the most useful lead role or smallest role set from
  the project context after initial context loading; continue on an obvious
  low-risk assumption and ask only when the role choice would materially change
  scope, architecture, external systems, cost, data safety, or user-visible
  behavior. Add new reusable roles only when repeated work shows a real
  specialty gap. Follow
  `patterns/AGENT_ROLE_OFFICE.md`.
- Treat startup-style product engineering as delivery of a working business
  outcome, not isolated code snippets. Agents should clarify business value,
  deadline pressure, acceptance criteria, and risk; choose the smallest
  reliable implementation path; apply pragmatic design principles; respect
  C#/.NET async and concurrency boundaries; follow frontend framework
  conventions; and communicate professionally when English is the expected
  working language. Follow `patterns/STARTUP_PRODUCT_ENGINEERING.md`.
- Keep the current technology stack visible in durable project memory. For
  GI-enabled projects, maintain `tools/project-memory/specs/technology-stack.md`
  or an equivalent linked stack inventory with verified languages, runtimes,
  frameworks, package managers, build/test tools, storage, external services,
  commands, evidence paths, and open verification gaps. Update it when stack
  components are added, removed, upgraded, replaced, or materially
  reconfigured. Follow `patterns/TECHNOLOGY_STACK_INVENTORY.md`.
- Keep the current project purpose, target users or stakeholders,
  user-visible functionality, common workflows, and stack pointer visible in
  project documentation. Treat `gi info` and `ги инфо` as the command to find or
  build this orientation inventory. Prefer `README.md`, `docs/`, and
  `tools/AGENT_RUNBOOK.md` for the human-facing overview; use project memory
  only for implementation-driving behavior, contracts, algorithms, invariants,
  and architecture decisions. Mark unknowns as gaps/TODOs with evidence paths
  or missing-source notes instead of guessing.
- After any meaningful implementation, refactor, migration, or configuration
  cleanup batch, verify the batch at the right abstraction level. Check all
  touched layers for duplicated defaults, policies, workflows, contracts, or
  interpretation rules; keep one authoritative source where possible; update
  durable project-memory specs when behavior or architecture changes; inspect
  the changed-file list for unrelated edits or generated noise; and separate
  harmless line-ending warnings from real whitespace errors in `git diff
  --check`. Follow `patterns/COHERENT_BATCH_VERIFICATION.md`.
