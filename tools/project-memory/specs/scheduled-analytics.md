# Scheduled analytics contract

Status: UX v2 deployed on 2026-10-16; both connected tools work after the reporting
restart with the existing OAuth grant. User supplied daily reports. Scheduler
execution and explicit refresh remain unverified.
Last live/local check: 2026-10-16. Sources: `reporting/`, `tests/test_reporting.py`,
`POSTHOG_VERSION`; operational guide: `docs/scheduled-analytics.md`.

Additive extension implemented 2026-10-10 and deployed 2026-10-16: metadata includes explicit report-day,
previous-day, seven-day baseline and legacy-window UTC bounds, including daily
row periods. Each legacy query has coverage status, limit and conservative
truncation flag. MCP validates aggregate columns/values and returns fixed safe
errors. Upstream truncation survives transport. UX dashboard 4 is added when
missing, existing Overview/Journey URLs preserved and restricted to configured
origin/project. Legacy complete still means success of six queries, never UX
coverage. Separate ux.coverage accounts for five implemented blocks, missing
linkage properties, failures and upstream/output truncation. Warnings identify
mixed schema/populations and the debug_assumed
coverage change on 2026-10-09. Source/test pointers: reporting/aggregate_safety.py,
reporting/queries.py, reporting/posthog.py, reporting/server.py,
tests/test_reporting.py; public contract: docs/report-contract.md.

Four canonical application files were read with user authorization on 2026-10-10.
Implemented semantics and source/test map: [UX daily report](ux-daily-report.md).
Six legacy and sixteen fixed UX queries run serially within a 270-second budget;
UX payload has a 512,000-byte compact JSON limit. All 22 aggregate and eight chart
queries executed on the live API. Model regex compatibility was fixed while
preserving the canonical ID boundary. Operator --allow-truncated explicitly
permits bounded results, never query/schema failures. The connected report has
all five blocks, no query errors and partial UX coverage because of row/JSON
limits; legacy complete=true is independent. Only reporting code was switched;
prompt/schedule, database connection, OAuth config/state and PostHog were preserved.
Evidence: docs/reporting-deployment-2026-10-16.md.

## Ownership and boundaries

- This repository owns PostHog infrastructure, the aggregate bridge and managed panels.
- AI Media Client source is not changed here. Event collection uses its existing catalog.
- PostHog project 1, HTTPS analytics-195-209-221-217.sslip.io.
- Reporting endpoint reports-195-209-221-217.sslip.io/mcp is deployed; unauthenticated access returns 401.
- ChatGPT cloud task, every day 09:00 Europe/Moscow, same chat for all reports.
  Local Codex automations do not satisfy independence from a running computer.
- Cloud model receives aggregates, not raw identities/event payloads. This is explicitly
  a cloud-processing choice, not a fully local agent. No LLM API credential on VPS.

## Public interface and authority

Only tools `analytics_daily_report(report_day?: ISO date)` and
`analytics_dashboard_links()` are exposed. Project, SQL, properties and event names
are fixed server configuration. Reports allow complete days within the past 30 days.
Six legacy plus sixteen UX aggregate queries execute serially, with bounded
rows, API timeout and a shared per-call budget.
OAuth uses a confidential native PostHog application with ceilings query:read and
project:read, exact ChatGPT redirect allowlist, PKCE, consent and project selection.
Persistent OAuth state is encrypted with a separate stable key, signed sessions use
a separate stable signing key. Administrator setup token never enters service config.
Client registration uses DCR. CIMD is explicitly disabled: on 2026-10-07 the VPS
received HTTP 403 fetching https://chatgpt.com/oauth/client.json, causing
Client Not Registered. Recreate the ChatGPT connection using DCR; do not bypass
PKCE, exact redirect validation or user consent. User supplied a successful report,
not an independently inspected scheduler execution.
Unconfigured/unauthorized access fails; query failures stay explicit, not zeros.

HTTPS is served by existing Caddy via optional CADDY_EXTRA_CONFIG. Bridge binds a
private Docker gateway address, not the public IP; no additional external port.
Only trusted server operator can edit source/env. Reporting user has no Docker access.
384 MiB / 50% one CPU limits contain bridge process, not PostHog query costs.

## Metric semantics

Report: yesterday plus seven preceding full Moscow calendar days, converted to UTC
query boundaries. Deduplicate event counts by event UUID, show delivery repeats.
Visitor and account identities must not be summed as people. Eight-day unique accounts
are not yesterday DAU or seven-day WAU. Terminal events and acceptance can differ in day.
Success = success / (success + fail), cancelled/unknown separate, zero denominator undefined.
Duration samples may include duplicate deliveries. Models are bounded to top 100 over
the whole eight-day window. Missing coverage and sparse samples limit interpretation.
No financial conclusions without application PostgreSQL reconciliation.
Daily narrative follows the user journey, compares yesterday with prior day/seven-day
mean, and labels missing measurement. Current six aggregates do NOT measure new
visitors, registrations, connected conversion cohorts or retention. UX schema-v2
preparation cohorts are implemented separately. login_completed
must never be relabeled as registration; purchase_fulfilled counts are not revenue.
Advice separates observation, hypothesis and verification; small samples cannot
justify causal or statistically significant claims. Prompt: reporting/daily-task-prompt.md.

Panels: two dashboards/eight insights, marked ai-media-analytics-report:v1. Setup creates
missing objects and preserves existing queries, rejects duplicate markers or unexpected
dashboard membership. Run one operator at a time. Named event series exclude smoke.
Native captures may differ from deduplicated report counts. Retention requires mature
cohorts; identity funnel cannot silently link anonymous and account actors.

## Verification boundary and operation

Local tests verify API response failure handling, no cross-origin pagination, timezone
boundaries, fixed MCP schemas, HTTP 401 without auth, OAuth discovery and redirect
rejection, idempotent setup preserving existing panels, and existing Compose policies.
Fixed API payloads were validated against the pinned upstream schema; 2026-10-16
live checks covered all six legacy/sixteen UX queries and eight chart sources.
Live verification 2026-10-06: six aggregates/eight chart sources passed; two dashboards
(IDs 2, 3) and eight insights created with idempotency/membership checked. Linux systemd
service active; HTTPS metadata 200, unauthenticated MCP 401, private port externally
unreachable. Native OAuth app requires RS256 and persistent OIDC_RSA_PRIVATE_KEY on web.
FastMCP update-check setting accepts off; root-created venv must allow service-user reads.
Encrypted reporting backup restored into a clean directory: bytes and ownership verified.
This does NOT verify functional OAuth restoration or a full PostHog data restore.
Historical grant/cloud call: 2026-10-07. Restart continuity is now confirmed by both
connected tools on 2026-10-16. Explicit refresh and scheduled delivery with computer
off remain unverified. See docs/reporting-deployment-2026-10-16.md.

Operator first validates 6 aggregates/8 chart sources on live API using temporary token,
then creates panels, installs/configures OAuth bridge, connects ChatGPT personally,
runs immediately and verifies next scheduled run with PC off. Resource headroom is a
gate: observed host swap nearly full; do not add load based solely on small user count.
Backup report env/state separately from analyticsctl's PostHog volume backup; preserve
secrets and filesystem ownership, refuse restoring over existing state.
