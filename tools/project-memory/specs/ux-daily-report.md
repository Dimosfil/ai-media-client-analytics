# UX daily aggregate contract

Status: deployed and checked through both connected plugin tools on 2026-10-16.
All queries execute; current UX coverage is partial because of explicit row/JSON
limits. Evidence: docs/reporting-deployment-2026-10-16.md.
Public contract/example: docs/report-contract.md. Sources: reporting/ux_contract.py,
ux_queries.py, ux_report.py, aggregate_safety.py, server.py. Verification:
tests/test_ux_reporting.py, tests/ux_sqlite.py, tests/test_reporting.py.

## Inputs and ownership

The analytics repository owns read-only fixed aggregate queries and the MCP tool.
AI Media Client owns event collection. Four canonical files and hashes are listed
in the public contract; see integration-contracts/connected-projects.md for scope.
Do not change application events, production database connection or the task's
prompt/schedule to implement this report. No public SQL, properties or project IDs.

## Invariants

- Preserve report_day, date constraints, configured Moscow timezone and legacy
  fields. Legacy complete means success of six legacy queries; UX status separate.
- Three explicit calendar periods: selected full day, preceding full day, seven
  preceding full days. Previous day overlaps the baseline; never sum identities.
- UX only schema 2, account identities. Seven fixed populations distinguish
  user release/debug, admin release/debug, admin_preview release/debug and unknown.
  Debug is not a synthetic marker. V1/unsupported schema stays diagnostic.
- Deduplicate by UUID/identity before relationships/duration; retain delivery counts.
- A preparation is identity/sample/flow anchored at composer_started. Link clicks
  with flow/attempt, accepted jobs with flow/attempt/generation, then success/view/use
  by the same job. Ordered prefixes cannot borrow stages across jobs or actors.
- Use a 48-hour horizon from preparation, as_of fixed per call. Events after
  midnight stay in the preparation cohort. Mature denominators require full 48h;
  missing stages remain observations, not failures. Delivered UI may be lost.
- Successful-result cohorts have their own 48h horizon from success. Actions can
  be observed without a view here; the complete journey requires the view prefix.
- Usage requires succeeded copy_result/reuse/favorite/play. Download started is
  a separately counted intent. Neither proves the content's actual utility.
- Discovery uses explicit control/action mapping and identity/sample/UI session,
  24h horizon. General clicks do not prove understanding. No advanced-settings pair.
- Obstacles group identity/sample/session/reason at first show, 24h horizon.
  Resolution must follow show, continuation follows show/resolution. Repeated
  same-category incidents cannot be individually linked. Active recovery samples
  remain distinct from wall time. Technical categories are explicit; their
  absence does not establish a working service.
- Initial, clicked and effective settings are scalar allowed parameter aggregates.
  Manual events require user origin. Restored/default/reuse/template are distinct.
  Compare clicked/effective per accepted job/parameter; never attribute difference
  to normalization without a cause property. Provenance refers to pre-normalization.
- Search size is not target-found; action outcomes are aggregates, not connected
  operation conversion without a correlation ID.

## Failure and output boundary

Each query is independently available/empty/unavailable. All five blocks are
accounted for, even after failures. Coverage includes per-event/family/sample
freshness, UUIDs/deliveries, missing links, property presence and unsupported
dimensions/unrecognized keys as counts. Never return unrecognized names/values.
Linkage gaps and truncation make UX complete false. Unknown denominators are null;
never form rates from truncated totals. Zero does not establish no real activity.

Six legacy plus sixteen UX queries execute serially. 400 rows per new query,
512,000 bytes compact UX JSON, 270s shared budget, network timeout ≤45s/remaining.
Explicit truncation includes upstream flags, reaching SQL limit and output trimming.
The operator check is strict by default. An explicit --allow-truncated permits
flagged bounded query results without hiding query/schema failures or changing
the public coverage status. Model IDs use regex allowlisting plus LIKE exclusions
for URLs/traversal; a compound negated regex fails the live HogQL parser.
Validate exact columns even on empty results; scalars must match closed categories,
model/version syntax or the exact parameter allowlist. Errors are fixed messages.
No raw IDs/UUIDs, prompts, searches, names, source URLs, accounts or error text.

## Verification boundary

Synthetic scenarios execute generated production SQL using SQLite/HogQL primitive
adapters, including boundaries and missing-data cases. MCP in-process invocation
and OAuth HTTP discovery/401 are tested. This does not validate the live HogQL
resolver or actual capture/delivery. reporting.check provides the read-only live
gate for an operator with a private scoped token before deployment.
2026-10-10 verification: 41 repository tests passed, all 22 Query API payloads
validated against the pinned PostHog Pydantic schema, documented example matched
the synthetic production-SQL output, and whitespace/UTF-8 checks passed.

2026-10-16: 46 local tests passed; six legacy, sixteen UX and eight chart queries
executed successfully on the live API, using the explicit bounded-result gate.
Configuration/parameter slices reached 400 groups. The connected MCP returned
all blocks and diagnostics after restarting only reporting; legacy complete=true,
UX complete=false/partial, no query failures. Compact JSON trimming was explicit;
linkage diagnostics reported no missing required keys. Existing OAuth grant worked
after restart; private config/state, application, database connection, dashboards
and schedule were preserved. Refresh and scheduler independence were not tested.
