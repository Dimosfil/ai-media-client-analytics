# Technology Stack Inventory

Keep each GI-enabled project technology stack visible in durable project
documentation.

## Purpose

Agents should not rediscover the same runtimes, frameworks, package managers,
build tools, test tools, external services, and deployment assumptions on every
session. Maintain a concise stack inventory so refactors, dependency changes,
verification plans, and migration work start from a shared source of truth.

Treat `gi stack` and `ги стек` as requests to find or build this inventory for
the current project.

The technology stack is project documentation: it explains how to understand,
run, test, build, and operate the project. It is not the source of business
rules or feature algorithms.

## Required File

Use this compatibility path unless local instructions define a more specific
documentation path:

```text
tools/project-memory/specs/technology-stack.md
```

Create it when a project adopts GI or when `gi обновить` introduces this rule.
If the project already has an equivalent `docs/technology-stack.md`, stack ADR,
or architecture note, keep that note and either link it from
`technology-stack.md` or migrate its current facts into one canonical file
without losing decisions. Do not maintain two independent stack inventories.

Keep a visible pointer to the canonical stack inventory near the beginning of
the project-local instructions, README, docs index, or runbook that an external
agent is expected to read first. If an external agent cannot find a stack link
or inventory in the first relevant project docs, it should gather the stack from
current project evidence and add or request the missing pointer according to
local documentation policy.

## What To Record

Record verified current facts, not guesses:

- primary languages and runtimes;
- application frameworks, UI frameworks, API frameworks, and worker runtimes;
- package managers and lockfiles;
- build, test, lint, formatting, packaging, and deployment tools;
- databases, queues, caches, vector stores, object storage, and search engines;
- external APIs, SDKs, service IDs, and contract endpoints;
- local development entry points, ports, and health checks when stable;
- generated artifacts and rebuildable indexes;
- deprecated, legacy, or transitional stack components;
- evidence paths such as manifests, config files, lockfiles, runbooks,
  documentation, and project-memory specs when they are evidence for
  behavior-sensitive stack choices;
- open verification gaps when the stack cannot be identified from current
  files.

Do not store secrets, tokens, credentials, or private user data. Reference secret
locations only by documented environment variable or config key name.

## Update Rules

- For `gi stack` / `ги стек`, first search project-local instructions, README,
  docs indexes, runbooks, and the compatibility path for a canonical stack
  link or inventory before scanning the repository broadly.
- If a current inventory exists, verify its key facts against manifests,
  lockfiles, config, run instructions, and source entry points before reporting
  it as current.
- If no inventory exists, create it from current evidence and mark unknowns as
  gaps instead of guessing.
- Update the inventory in the same scoped change that adds, removes, upgrades,
  replaces, or materially reconfigures a runtime, framework, package manager,
  storage engine, external service, build tool, test runner, or deployment
  target.
- Verify stack facts from current files before editing code that depends on
  those facts. Handoff summaries and old chats are status evidence only.
- Keep stack choices separate from product identity. Do not hard-code demo
  names, selected workflow labels, generated product names, or user-specific
  paths as if they were technology requirements.
- When a component is only inferred, mark it as inferred and list the evidence
  or the missing verification step.
- Prefer stable relative paths in evidence. Use absolute paths only when the
  project explicitly records an approved external workspace dependency.

## Suggested Shape

```markdown
# Technology Stack

Last reviewed: YYYY-MM-DD

Canonical source: this file
Linked from: TODO

## Summary

- Primary stack: TODO
- Runtime model: TODO
- Current confidence: confirmed | partial | needs review

## Components

| Layer | Technology | Evidence | Notes |
| --- | --- | --- | --- |
| Language/runtime | TODO | TODO | TODO |
| Frontend | TODO | TODO | TODO |
| Backend/API | TODO | TODO | TODO |
| Data/storage | TODO | TODO | TODO |
| Build/package | TODO | TODO | TODO |
| Test/quality | TODO | TODO | TODO |
| Deployment/runtime | TODO | TODO | TODO |

## Commands

| Purpose | Command | Evidence |
| --- | --- | --- |
| Install | TODO | TODO |
| Run | TODO | TODO |
| Test | TODO | TODO |
| Build | TODO | TODO |

## External Services

| Service | Role | Evidence | Boundary |
| --- | --- | --- | --- |
| TODO | TODO | TODO | TODO |

## Gaps

- TODO
```

## Verification

For stack inventory changes, run the smallest checks that fit the scope:

- parse edited JSON/YAML/TOML manifests when touched;
- verify `technology-stack.md` exists for GI-enabled projects;
- check that newly recorded commands match current manifests or runbooks;
- use `git diff --check` or the project equivalent for whitespace issues.
