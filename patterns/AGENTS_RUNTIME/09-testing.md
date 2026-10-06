## Project Tester

- Treat `gi test`, `ги тест`, `gi тест`, and `gi testing` as information requests:
  load this rule and the current project's testing entrypoint, then explain
  available scenarios, scope, modes, settings, required test content and its
  availability, prerequisites, evidence paths, known gaps, and how to start.
  Do not run tests, start apps, reset state, open
  UI, write configuration, or create reports from this information command.
- Treat `gi test start`, `ги тест старт`, `gi тест старт`, and `gi testing start`
  as requests to execute the selected project-local scenario. Resolve selection
  from the current message, an active task in this chat, or documented local
  selection/default. Reuse existing authorization. If several scenarios remain
  equally possible or no task is defined, ask one focused question and continue
  independent preparation; do not silently choose full-system verification.
- Treat `gi test task`, `gi testing task`, `gi тест таск`, `ги тест таск`,
  `gi задача теста`, and `ги задача теста` as requests to set the active scenario
  or verification workload. Use its documented project-local location, or keep
  it in current chat context and say where it is tracked. Task selection is
  intent, not a passed test. `gi test plan` remains plan-only by default.
- Treat `gi full test`, `gi release test`, and `gi system test` as explicit
  full-system runs. Read `09-full-testing.md` for that flow, also when a selected
  `gi test start` scenario explicitly requires full-system verification.

### Shared Rule And Local Contract

- Keep the shared tester independent of products and tools. Each project owns
  its scenario inventory, active selection, modes, settings, URLs, ports,
  roles, inputs/fixtures, adapters, commands, expected results, verification
  gates, and storage paths. Do not copy one project's values into GI defaults.
- Find the canonical testing entrypoint through local `AGENTS.md`, README,
  runbook, or test index before searching broadly. Read the selected scenario's
  instructions, settings, and behavioral contract; confirm command flags,
  endpoints, payloads, and environment sources against current config/source.
  Keep one linked source of truth instead of repeating scenario instructions.
- Require a local scenario to define purpose and observable success, scope and
  exclusions, environment identity, access, effective settings, input policy,
  allowed/forbidden actions, state preparation/reset/backup/restoration,
  steps and expected results, waiting/retry limits, checkpoint/resume rules,
  evidence destinations, and completion criteria. Mark missing fields as gaps.
  `templates/PROJECT_TESTING.template.md` is an optional authoring scaffold;
  it is not a configured scenario or an executable runner.
- If local testing documentation is absent, `gi test` reports the missing
  contract and scaffold. `gi test start` may resolve it from an explicit current
  task and verified local sources; block only dependent actions whose contracts
  remain missing. Do not invent addresses, roles, fixtures, reset targets,
  budgets, or credentials. Do not auto-install a runner or rewrite product
  tests/configuration merely to execute a scenario.

### Test Content And Input

- Treat content entry as part of a scenario when its cases require it. Projects
  define the needed text, structured data, documents, media, links, or existing
  records; these examples do not impose a universal content set. Map each input
  to its case and destination field, with purpose, source, required/optional
  status, expected use, and validity constraints.
- Resolve content from the current task, authorized supplied material, approved
  project fixtures, or reproducible synthetic inputs permitted by the scenario.
  Prepare simple non-sensitive synthetic content locally when that satisfies
  the case. Do not invent existing record IDs, working links, credentials, or
  material whose authenticity is part of the test. Required real content that
  is unavailable blocks only dependent cases; report what is missing.
- Keep content values, fixture paths, generation/preparation recipes, and input
  constraints project-local. Record a safe content manifest with stable fixture
  IDs, type, source/provenance, relevant characteristics, and case/field mapping.
  Store private values and original payloads only in approved private locations.
- Validate inputs before entry against the selected case: format, schema,
  encoding, size, dimensions, duration, or other relevant constraints. Use
  invalid or boundary content only for an explicitly selected negative/boundary
  case and record the expected rejection. Do not silently alter supplied files
  or replace required content with an unrelated placeholder.
- Enter content through the scenario's documented surface. Use visible fields
  and supported upload/file chooser tools for UI cases, or the verified request
  contract for API cases. Confirm the content reached its intended field,
  parsing/upload completed, and the current validation/final result used it.
  A loaded attachment alone does not prove that the required input is filled.
- Content preparation or upload does not authorize paid generation, publication,
  external messaging, or reuse of unrelated personal data. Respect already
  authorized sources and budgets; ask only for actually missing authorization.
  Do not acquire fixtures through such actions without that authorization.
- Track content introduced by the run in its checkpoint. Avoid duplicate
  uploads on uncertain timeouts; inspect current state first. Follow the local
  retention/cleanup/restoration contract for test records and uploaded content,
  preserving original files and unrelated data. Report any remaining artifacts
  and cleanup gaps; do not infer their absence from zero generation actions.

### Execution And Evidence

- Verify the active root and runtime identity before changing state. Use the
  documented development/test environment and current configuration source.
  Apply `08-config-service.md` only when discovery is needed; query the service
  only when local integration is enabled. Preserve the intended connection and
  access boundaries; do not substitute storage or elevate a role to pass.
- Run only the selected scope and its required verification gates. Follow the
  project's documented environment/build/health order. An observational audit
  uses its backup/restoration contract; it does not inherit full-system resets.
  If mandatory preparation is unsafe or unavailable, stop dependent mutations
  and record the exact blocker while continuing safe independent checks.
- A test-start request authorizes the documented UI interaction required by the
  selected scenario. Read applicable computer/browser instructions and operate
  through supported tools. A test-info request does not authorize UI inspection.
  Do not replace a UI workflow check with API-only or hidden-state mutation.
- Exclude chargeable, destructive, externally visible, and out-of-scope actions
  unless explicitly authorized for this scenario, with a budget where relevant.
  Reuse prior authorization for the same target and scope. Safe reads and the
  selected scenario's documented reversible steps do not need another approval.
  An audit is not permission to repair the product, import settings, or deploy.
- Before altering drafts, user-owned state, or shared work, prepare the local
  backup and dedicated test context required by the scenario; check durability
  and privacy. In-memory agent variables do not replace a required backup.
  Restore affected state after completion, interruption, or failure; verify the
  persisted result after asynchronous saving. Preserve backup if restoration
  is unconfirmed and report `restoration-required`.
- Build fresh coverage by stable case IDs and settings. Distinguish inventory
  entries, unique entities, parameter combinations, and repeated checks. Wait
  for the current operation's final result; ignore stale responses and transient
  loading. Apply bounded retries, then record timeout/error and continue
  independent cases. Classify local result codes by their actual meaning.
- Save results and durable checkpoints in bounded batches under a new run ID at
  project-configured paths. Record scope/settings, environment/version, case
  IDs, observations, reasons, checked/skipped counts, remaining work, and
  restoration. Before resume, verify target, access, input and configuration
  freshness; do not merge changed scopes or snapshots as a single fresh run.
- Keep raw evidence in approved project artifact locations, private backups
  separately, and only compact verified contracts/evidence references in
  project memory. Check ignore/privacy rules before saving; exclude secrets,
  personal content, and unrelated history from reports and Git.
- Report observed actions separately from measured network requests or effects.
  If a channel was not observed, record its count as unknown, not zero. A
  preview, estimate, mocked check, or old report proves only its stated scope;
  it does not prove live execution, final cost, or a fresh run.
- Finish as `complete` only when selected coverage is accounted for, evidence
  saved, restoration confirmed where required, and mandatory gates passed.
  Found defects may coexist with a completed audit; report product failures
  separately. Use `incomplete` for remaining coverage, `blocked` for unavailable
  prerequisites, and `restoration-required` for unconfirmed restoration. The
  final report states scope, defects, coverage, skips, effects, restoration,
  environment checks, evidence locations, and remaining blockers.
