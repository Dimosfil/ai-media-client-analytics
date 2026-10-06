# Project Testing Contract

Authoring scaffold only. Fill it from verified project sources before use.
Keep this document at a project-approved docs/test location and link it from
AGENTS.md, README, or the test index. Preserve existing canonical scenarios;
do not create a competing copy. Paths and settings belong to this project.

## Commands And Selection

- `gi test` / `ги тест`: explain scenarios, settings, required content, and gaps.
- `gi test start` / `ги тест старт`: execute the selected scenario.
- `gi test task <task>` / `ги тест таск <задача>`: select the active workload.
- `gi full test`: explicitly request the documented full-system flow.
- Active selection location and default, if any: TODO.

## Scenario Inventory

| Stable ID | Purpose and success criteria | Instructions/settings/contract | Status |
| --- | --- | --- | --- |
| TODO | TODO | TODO | unconfigured |

## Selected Scenario Contract

- Purpose and observable success: TODO.
- Scope, excluded cases, mode, and live/isolated/diagnostic evidence limits: TODO.
- Target identity and environment; URL/service/port configuration source: TODO.
- Required roles/accounts and access; missing-access behavior: TODO.
- Settings source, effective values, parameter policy, and snapshot/version: TODO.
- Input/fixture sources, explicit permissions, validity checks, and privacy: TODO.
- Content requirements and case/field mapping: use the content contract below.
- Allowed actions, forbidden actions, expected effects, and budget if needed: TODO.
- Preparation, dedicated test context, reset targets/exclusions or backup: TODO.
- Exact run/build/health commands and required order, from current sources: TODO.
- Steps, stable case IDs, expected results, and local result classifications: TODO.
- Completion signals, wait limits, retries, and independent failure branches: TODO.
- Coverage counts, parameter combinations, and known unverified areas: TODO.
- Report/evidence paths, ignore rules, private backup path, and retention: TODO.
- Checkpoint fields, batch limits, resume/freshness rules, and comparison keys: TODO.
- Restoration procedure and persisted-state readback after saving: TODO.
- Observed actions, measured requests/effects, and unknown channels: TODO.
- Completion gates and required final report: TODO.

Use `complete`, `incomplete`, `blocked`, or `restoration-required` for run state.
Report discovered product defects separately from completion of the audit.
Historical results are dated evidence and do not replace a new execution.

## Test Content Contract

Fill only what the selected scenario needs. Mark a content-free scenario
explicitly; do not require fixtures for every test.

| Fixture ID | Case / destination field | Type and purpose | Required? | Authorized source or synthetic recipe | Validity constraints / expected result |
| --- | --- | --- | --- | --- | --- |
| TODO | TODO | TODO | TODO | TODO | TODO |

- Availability and missing-content behavior per dependent case: TODO.
- Local values/private references or reproducible preparation recipe: TODO.
- Entry surface and exact text/data/file mapping: TODO.
- Upload/parsing completion and input acceptance checks: TODO.
- Positive, negative, and boundary variants, where selected: TODO.
- Safe manifest/checkpoint fields and provenance: TODO.
- Introduced records/uploads, retention, cleanup, and restoration checks: TODO.

Use authorized provided material, approved fixtures, or permitted non-sensitive
synthetic content. Real IDs/links must be verified; placeholders cannot prove
real-content behavior. Preserve originals and keep private payloads out of
shared reports, memory, and Git. Content entry does not itself authorize paid
execution, publication, or external messages.
