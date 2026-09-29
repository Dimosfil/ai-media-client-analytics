# Project Documentation Layers

Use this pattern to keep human-facing project documentation separate from
implementation-driving project memory.

## Purpose

Projects need two durable documentation layers:

- project documentation: the human and agent orientation layer;
- project memory: the behavioral specification layer used to write and verify
  code.

Do not let one layer silently replace the other. A readable project overview is
not enough to preserve business behavior, and a detailed algorithm spec is not a
good user-facing entry point.

## Project Documentation Layer

Use project documentation for information that helps a person or agent
understand, run, operate, or evaluate the project:

- project purpose, audience, and product surface;
- user-visible functionality and common workflows;
- installation, run, test, build, smoke-check, and log commands;
- technology stack, runtime model, deployment assumptions, and external
  services;
- screenshots, demos, examples, release notes, troubleshooting, and FAQs;
- high-level architecture summaries and links to deeper specifications.

Preferred locations:

```text
README.md
docs/
tools/AGENT_RUNBOOK.md
tools/AGENT_WORKING_AGREEMENTS.md
```

For GI-enabled projects, the technology stack inventory belongs to this
documentation layer even when an existing project stores the file under
`tools/project-memory/specs/technology-stack.md` for compatibility. If both
`docs/technology-stack.md` and `tools/project-memory/specs/technology-stack.md`
exist, make one canonical and link the other to it instead of maintaining two
independent stack descriptions.

## Project Memory Layer

Use project memory for implementation-driving knowledge that code must preserve:

- feature algorithms and workflow contracts;
- business rules, invariants, permissions, and validation rules;
- state machines, terminal states, failure handling, retries, and cancellation;
- data-model semantics, source-of-truth rules, freshness, and migrations;
- integration contracts and boundaries that affect behavior;
- architecture decisions and migration history;
- verification guarantees and current implementation maps.

Preferred locations:

```text
tools/project-memory/
  architecture-migrations.md
  specs/
    features/
    business-rules/
    data-model/
    integration-contracts/
```

Write project-memory specifications so another agent could rebuild the behavior
on a different language, framework, platform, or UI toolkit. Code is the current
implementation; project memory is the portable behavior record.

## Separation Rules

- Do not store the only description of user-facing functionality in
  `tools/project-memory/`. Keep an overview in `README.md` or `docs/`.
- Do not store product runtime/source packages, product plugin implementations,
  product tests, or full product documentation under `tools/project-memory/`.
  Project memory stores compact behavior contracts, decisions, implementation
  maps, and evidence references for agents; code belongs in source/package
  directories, tests in the test tree, and product documentation in
  `README.md`, `docs/`, or runbooks.
- Do not store raw work results, generated product outputs, screenshots, photos,
  crawled/downloaded files, large logs, model outputs, build artifacts, export
  bundles, or run datasets in `tools/project-memory/`. Put them in a
  project-local artifact, evidence, output, data, or docs-asset location and
  keep only compact summaries, manifests, checksums, or links in project memory
  when they are needed for behavior or verification.
- Do not store algorithms, business rules, state machines, or verification
  contracts only in user documentation, screenshots, tickets, chats, or commit
  messages. Keep them in project memory.
- User documentation may link to project-memory specs, but should summarize
  behavior without becoming the source of implementation truth.
- Project memory may link to user documentation for product context, but should
  stay focused on rules, contracts, algorithms, invariants, and verification.
- When meaningful work changes both product-visible behavior and implementation
  rules, update both layers in the same scoped change.
- When only copy, screenshots, examples, or command documentation changes,
  update project documentation; update project memory only if behavior or
  contracts changed.
- When only internal algorithms, business rules, data semantics, or architecture
  contracts change, update project memory; update user documentation only when
  the change affects user-visible functionality, operations, or stack facts.
- Keep each layer bounded: update the smallest relevant spec instead of adding
  a chronological work log or copying full docs into project memory. Link to
  source, tests, detailed human documentation, and external evidence rather
  than duplicating them. Revise or retire stale contracts when behavior changes.

## Retrieval And Startup

During startup or task restoration, load from the layer that matches the task:

- orientation, setup, stack, commands, and visible functionality: read
  `README.md`, `docs/`, and the runbook first;
- feature implementation, refactoring, migrations, business behavior, or
  regression checks: read the relevant project-memory specs first;
- incident debugging: read project documentation for commands and project
  memory for invariants, failure rules, and implementation maps.

RAG and SQLite indexes may include both layers, but should preserve source
metadata so retrieval can distinguish documentation evidence from behavioral
specification evidence.

## GI Info Command

Treat `gi info` and `ги инфо` as the command to find or build a compact project
orientation inventory across these layers. It should answer and, when missing
or stale, document:

- project purpose, audience, and product/runtime surface;
- user-visible functionality and common workflows;
- technology stack pointer and summary;
- setup, run, test, build, operation, and troubleshooting pointers when present;
- open gaps where evidence is missing or contradictory.

Before editing, compare the verified facts with the existing overview and stack
inventory. If purpose, functionality, workflows, commands, operations,
troubleshooting pointers, and stack facts are already current, report that no
documentation update is needed. If only some facts changed, update the smallest
affected sections and preserve unchanged sections. Do not rewrite the whole
overview, retranslate unchanged content, or reformat unrelated documentation
just because `gi info` was invoked.

The command should write the human-facing overview to `README.md`, `docs/`, or
the runbook in the configured project working-environment languages from
`gi язык` / `gi language`, preserving the selected order with the first language
as primary. It should keep the stack in the canonical stack inventory, avoid
making `tools/project-memory/` the only source for purpose or visible
functionality, and avoid duplicating detailed behavior contracts out of project
memory into the overview.

## Verification

After documentation or memory changes:

- confirm there is one canonical source for stack facts, commands, and
  user-visible feature descriptions;
- confirm implementation-driving behavior is present in project memory when the
  change affects algorithms, business rules, workflows, or architecture;
- confirm user-facing documentation is present when the change affects setup,
  commands, stack, features, or operation;
- run `git diff --check` or the project equivalent for Markdown-only changes.
