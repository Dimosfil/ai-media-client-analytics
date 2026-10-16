# Pending Tasks

Use this file for active project-wide plans and multi-step work.

Keep entries concise and task-relevant. Do not store full diffs, large logs,
generated outputs, secrets, credentials, or private production data.

## Status Markers

- `[ ]` not started
- `[~]` in progress
- `[x]` done
- `[!]` blocked or needs attention

## Tasks

### UX v2 reporting deployment — 2026-10-16

Goal: deliver the existing aggregate-only UX contract through the connected MCP.

- [x] Verify SSH access and exact reporting service/source identity.
- [x] Confirm deployed legacy files match HEAD; run 41 local tests.
- [x] Stage the reporting package and preserve an exact code rollback copy.
- [x] Execute six legacy, sixteen UX and eight chart checks; explicitly allow
  flagged bounded results, never query/schema failures.
- [x] Switch only reporting code, preserve OAuth/config/state, verify health.
- [x] Verify both connected plugin tools and update the contract/evidence.

Result: deployed, 46 tests pass, all live queries execute. Legacy complete=true;
UX v2 has all blocks and no query errors, but partial row/JSON-limited coverage.
Evidence: docs/reporting-deployment-2026-10-16.md.

Risks: live HogQL compatibility and bounded query time; no application changes,
database connection changes, paid generation, dashboard writes or schedule edits.
Existing OAuth credentials remain private on the VPS; never print or export them.

### TODO Task Name

Goal: TODO

Planned changes:

- [ ] TODO

Execution order:

- [ ] TODO

Risks or dependencies:

- [ ] TODO

Verification:

- [ ] TODO
