# Connected projects

## AI Media Client

Role: canonical event schema and collector for the analytics report. Local folder
authorized for reading by the user on 2026-10-10: F:/Projects/AIMediaClient.
Read scope: src/analytics/contract.mjs, src/services/product-analytics.js,
src/analytics/reports.cjs, docs/ux-analytics.md. No changes to this project.
The four source hashes were rechecked unchanged on 2026-10-16 before deployment.

The analytics runtime consumes PostHog project 1 over its existing read-only API;
it does not import application source or require this local folder on the VPS.
Contract projection: reporting/ux_contract.py; source hashes and known gaps:
docs/report-contract.md; portable behavior: specs/ux-daily-report.md.
To refresh the projection, read these four current files in an authorized source
checkout, compare schema/collector semantics, update queries/spec/tests together.
Do not treat another project's test/deploy instructions as permission to restart
that application or touch its production database.
