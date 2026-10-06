# Scheduled analytics contract

Status: preparation implemented, production deployment and cloud execution unverified.
Last local check: 2026-10-06. Sources: `reporting/`, `tests/test_reporting.py`,
`POSTHOG_VERSION`; operational guide: `docs/scheduled-analytics.md`.

## Ownership and boundaries

- This repository owns PostHog infrastructure, the aggregate bridge and managed panels.
- AI Media Client source is not changed here. Event collection uses its existing catalog.
- PostHog project 1, HTTPS analytics-195-209-221-217.sslip.io.
- Target reporting endpoint reports-195-209-221-217.sslip.io/mcp is planned, not deployed.
- ChatGPT cloud task, every day 09:00 Europe/Moscow, same chat for all reports.
  Local Codex automations do not satisfy independence from a running computer.
- Cloud model receives aggregates, not raw identities/event payloads. This is explicitly
  a cloud-processing choice, not a fully local agent. No LLM API credential on VPS.

## Public interface and authority

Only tools `analytics_daily_report(report_day?: ISO date)` and
`analytics_dashboard_links()` are exposed. Project, SQL, properties and event names
are fixed server configuration. Reports allow complete days within the past 30 days.
Six aggregate queries execute serially, with bounded rows and API timeout.
OAuth uses a confidential native PostHog application with ceilings query:read and
project:read, exact ChatGPT redirect allowlist, PKCE, consent and project selection.
Persistent OAuth state is encrypted with a separate stable key, signed sessions use
a separate stable signing key. Administrator setup token never enters service config.
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

Panels: two dashboards/eight insights, marked ai-media-analytics-report:v1. Setup creates
missing objects and preserves existing queries, rejects duplicate markers or unexpected
dashboard membership. Run one operator at a time. Named event series exclude smoke.
Native captures may differ from deduplicated report counts. Retention requires mature
cohorts; identity funnel cannot silently link anonymous and account actors.

## Verification boundary and operation

Local tests verify API response failure handling, no cross-origin pagination, timezone
boundaries, fixed MCP schemas, HTTP 401 without auth, OAuth discovery and redirect
rejection, idempotent setup preserving existing panels, and existing Compose policies.
All eight queries validate against pinned upstream Pydantic schema.
Live HogQL execution, creation of panels, Linux installation, reverse proxy,
project-scoped OAuth grants, refresh, restart continuity, private-state restoration and
cloud task execution with computer off remain unverified. Do not label them successful.

Operator first validates 6 aggregates/8 chart sources on live API using temporary token,
then creates panels, installs/configures OAuth bridge, connects ChatGPT personally,
runs immediately and verifies next scheduled run with PC off. Resource headroom is a
gate: observed host swap nearly full; do not add load based solely on small user count.
Backup report env/state separately from analyticsctl's PostHog volume backup; preserve
secrets and filesystem ownership, refuse restoring over existing state.
