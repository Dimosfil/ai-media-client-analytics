# Coherent Batch Verification

Use this pattern after any meaningful implementation, refactor, migration, or
configuration cleanup batch.

## Purpose

A coherent batch is a small, reviewable set of changes that advances one
behavioral or architectural goal. It should leave the project in a verified
state and make the next batch obvious without hiding unfinished risks.

## Rule

- Keep each batch tied to one product, architecture, configuration, or
  verification goal.
- Classify the batch before editing as refactor, development, verification,
  operation, migration, configuration cleanup, or a named mix. Do not hide
  feature work, behavior changes, public contract changes, service operations,
  or data migrations inside a "refactor" label.
- Preserve user-visible behavior unless the user explicitly requested a behavior
  change.
- Check every touched layer that can contain the same decision, default, state,
  policy, contract, or interpretation rule.
- Prefer one authoritative source for changeable values and behavior contracts.
  Other layers should load, render, validate, or adapt that source instead of
  copying it.
- When a value or rule is intentionally duplicated for performance, packaging,
  offline operation, or generated output, document the generation or sync path
  and verify it in the same batch.
- Update durable project-memory specifications for meaningful behavior,
  workflow, data-model, integration, or architecture changes. Active checklists
  and handoff summaries are status aids, not durable specifications.
- When the user says to work "by GI", "strictly by GI", or an equivalent
  local-language phrase, treat this writeback as a completion gate. Do not
  finish with known drift between implementation and durable specifications
  unless the user explicitly defers the spec update for the current task.
- Keep the diff scope clean: include only files required for the batch, plus
  directly related tests, docs, migration notes, and project-memory updates.
- Before finishing, inspect the changed-file list and remove or explain
  unrelated edits, generated noise, local-only artifacts, and accidental
  formatting churn.
- Keep rollback scope clear. A batch should be reviewable and revertible without
  undoing unrelated user work or previous completed batches.
- Run the fastest relevant checks first, then broader checks only when the risk
  or project contract requires them.
- After sufficient checks pass, repeat or broaden them only for new changes,
  failures, unresolved concerns, or a required project gate. Do not add tests
  that merely mirror a reversible, low-impact edit. Follow
  `AGENTS_RUNTIME/15-verification.md` for verification scope and stopping rules.
- Treat `git diff --check` as a whitespace/error check, not as a substitute for
  tests or behavior verification. If it reports warnings, distinguish harmless
  line-ending warnings from actual whitespace errors.
- Report remaining risks at the same abstraction level as the batch, such as
  "frontend still has an independent default source" or "architecture spec still
  needs a migration note", instead of only naming files.

## Layer Consistency Checklist

Use targeted searches or structured queries for the kind of change being made:

- configuration defaults, feature flags, model/provider choices, ports, paths,
  endpoints, and product-selection state;
- backend config loaders, domain services, routers, dispatchers, workers, CLI
  entry points, and API schemas;
- frontend HTML, JavaScript, templates, generated assets, fixtures, demos, and
  onboarding/default-state flows;
- tests, snapshots, examples, docs, runbooks, feature specs, architecture
  migrations, and task-manager or service contracts;
- build, packaging, installer, deployment, and service-discovery metadata.

Do not read large generated bundles or full HTML documents by default. Search
for relevant symbols, values, labels, and contract names, then inspect small
surrounding ranges or structured parsed output.

## Completion Standard

At the end of the batch, the agent should be able to answer:

- What is the single purpose of this batch?
- What type of work was this batch, and did any development, verification, or
  operational work ride along with a refactor?
- Which source is authoritative for each changed default, policy, workflow, or
  contract?
- Which layers consume that source, and how was drift checked?
- Which durable specification changed, or why no durable spec update was
  needed?
- If strict GI wording was used, was project-memory/spec writeback required and
  completed, or what explicit blocker/deferral remains?
- Which checks prove the batch, and what do their warnings mean?
- What is the smallest safe rollback scope?
- Which follow-up batch remains, if any?
