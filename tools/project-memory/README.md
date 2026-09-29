# Project Memory

Deployment contract: [PostHog deployment](specs/posthog-deployment.md).

This folder stores implementation-driving project knowledge for AI agents.

Use it for verified behavior, rules, and implementation contracts that should
survive chat resets:

- debugging findings
- important decisions
- business rules and invariants
- platform-neutral feature specifications
- workflow algorithms, contracts, and state diagrams
- architecture migration history
- known pitfalls
- dependency and integration contracts that affect behavior
- reusable agent experience that may improve `gi`

Keep general project documentation in `README.md`, `docs/`, and the runbook:
project overview, visible functionality, setup, commands, stack, operations,
examples, screenshots, troubleshooting, and release notes.

Do not store secrets or credentials here.

Do not store raw work results, generated product outputs, screenshots, photos,
crawled/downloaded files, large logs, model outputs, build artifacts, export
bundles, or run datasets in this folder. Put those files in a project-local
artifact, evidence, output, data, or docs-asset location and keep only compact
summaries, manifests, checksums, or links here when they are needed for a
decision, behavior contract, failure, or verification result.

Likewise, do not put product material in `tools/` by default. `tools/` is for
durable development and agent tooling such as scripts, adapters, bootstrap
commands, deployment helpers, verification helpers, agent-memory tooling, and
redacted examples or manifests. Product runtime/source packages, product plugin
implementations, product tests, full product documentation, product outputs,
and selected-run artifacts need the project's normal source, test,
documentation, output, evidence, data, build, release, or docs-asset locations.

Executable file type does not make a script durable tooling. Keep single-task
research probes, exploratory scripts, ad hoc collectors, and throwaway
diagnostics out of `tools/`, `tools/research/`, `tools/probes/`, and similar
subtrees. Prefer inline execution or the project's documented ignored
scratch/temp location outside `tools/`; remove the temporary script after use
and preserve only required evidence in its normal artifact location.

## Documentation Versus Summary Versus Project Memory

`README.md`, `docs/`, and runbooks are the project documentation layer.
`tools/summary/` is compact handoff state for the current or recent chat.
`tools/project-memory/` is long-lived implementation-driving knowledge.

Write project-memory documents so another agent could rebuild the project on a
different language, framework, platform, or UI stack and preserve the same
behavior. Code is the current implementation; project-memory specifications are
the portable behavioral source of truth.

Follow `patterns/PROJECT_DOCUMENTATION_LAYERS.md` when deciding which layer to
update. If a change affects user-visible functionality, stack, commands, setup,
or operations, update project documentation. If a change affects algorithms,
business rules, states, integrations, failure handling, or verification
contracts, update project memory.

Recommended specification structure:

```text
tools/project-memory/
  architecture-migrations.md
  specs/
    features/
    business-rules/
    data-model/
    integration-contracts/
      connected-projects.md
```

Split documents by meaning. Keep feature algorithms, business logic,
architecture contracts, and implementation mapping searchable as separate
focused files instead of one giant document.

Keep a short link for each active specification in this README, or point to the
project's canonical spec index. When a spec is added, renamed, moved, or
retired, update that index in the same change and check its relative links.
Label implemented, planned, and historical behavior in specs when they could
be confused. For current-implementation claims, record the last check date and
source or test paths; dates alone do not prove the claim.

Keep specs concise and current. Revise the relevant contract when behavior
changes; do not append a transcript of every task. Link to source, tests, docs,
and evidence rather than copying their full contents here. Generated SQLite or
vector indexes may help retrieval as the project grows, but the reviewable
contracts remain focused Markdown files.

Keep the current technology stack in project documentation. For compatibility,
GI-enabled projects may keep the stack inventory at:

```text
tools/project-memory/specs/technology-stack.md
```

If the project uses another canonical file such as `docs/technology-stack.md`,
link to it instead of maintaining two independent stack descriptions. Record
verified languages, runtimes, frameworks, package managers, build/test tools,
storage, external services, commands, evidence paths, and open gaps. Update it
when stack components are added, removed, upgraded, replaced, or materially
reconfigured.

Keep a connected-projects register when this project depends on, researches,
vendors, or regularly interacts with external repositories, cloned examples,
service projects, libraries, docs sites, upstream tools, or sibling workspaces:

```text
tools/project-memory/specs/integration-contracts/connected-projects.md
```

For each connected project, record its purpose, business or architectural role,
local folder when applicable, canonical Git/package/docs URLs, service IDs or
runtime endpoints, owner/source of truth, data or API contract, setup/update
commands, privacy and access boundaries, status, caveats, and why this project
needs it. Agents should read the register before touching integrations or
external project folders, and update it when a connected project is added,
removed, moved, replaced, or given a new role.

For each non-trivial feature or workflow, record:

- product intent and success signal;
- actors, roles, permissions, and preconditions;
- user-visible workflow, branches, and terminal states;
- business rules, invariants, inputs, outputs, and validation;
- background work, ordering, retries, cancellation, and failure behavior;
- Mermaid flowcharts or state diagrams when useful;
- verification rules for preserving behavior after a rewrite;
- current implementation map with evidence paths.

Keep major rewrites, platform moves, framework replacements, storage changes,
service splits, and routing changes in `architecture-migrations.md`.

## Reusable Experience For GI

When this project reveals a reusable workflow, failure pattern, token-saving
tactic, or agent-instruction improvement, write a concise recommendation for the
shared instruction kit.

When the user reports a recurring agent-rule failure or asks for such bugs to be
logged, add a compact entry to the shared library's
`updates/USER_REPORTED_AGENT_BUG_LOG.md` when available, or to the local
instruction-updates folder as intake when it is not.

Prefer the `updates/` folder in an available checkout/cache of the canonical
shared-instruction source repo when this repository is being maintained:

```text
<general-instructions checkout>\updates\
```

If the shared library is unavailable, use a local intake folder:

```text
tools/project-memory/instruction-updates/
```

Recommendations should include:

- observed problem or repeated friction
- reusable rule, pattern, template, checklist, or migration idea
- evidence paths or commands
- expected benefit for token economy, startup retrieval, safety, or workflow
- privacy review notes

Do not include secrets, credentials, private user data, production data, or
unnecessary project-specific details.

## Agent Memory SQLite

If the project benefits from searchable agent memory, use a local SQLite
database as an agent index/experience store, not as the application database.

Recommended path:

```text
tools/project-memory/project_memory.sqlite
```

The SQLite file is usually local/generated and ignored by git when it is large
or rebuildable. Commit the indexing script, schema notes, and Markdown exports
instead.

Use the database for verified facts, searchable file/symbol indexes, debugging
findings, useful commands, recurring failures, and durable notes with evidence
paths. Do not store secrets, credentials, private user data, or production data.

Do not dump the database into chat. Query it by symbol, path, topic, error, or
feature name with small limits.

Use SQLite for deterministic project facts and graphs: paths, symbols, exact
references, generated identifiers, asset links, reverse dependencies, commands,
failures, and evidence-backed notes. In Unity-like projects, this can include
`.meta` GUID mappings, prefab/scene/material/script references, and
assembly-definition dependencies.

Keep logical separation between code memory and specification memory. Code
memory tracks current implementation facts such as files, symbols, commands,
schemas, and errors. Specification memory tracks product behavior, business
rules, feature algorithms, workflow contracts, architecture migrations, and
verification guarantees. Small projects may use one SQLite database with source
metadata. Larger projects should split code and spec indexes into separate
databases, schemas, collections, or source groups.

Use vector retrieval only as a second semantic layer for conceptual questions
over curated notes, summaries, architecture docs, and selected chunks. Do not
replace exact graph queries with embeddings, and always verify current source
files before editing because generated indexes can be stale.

## Two Memory Layers

- Markdown is the human-reviewable layer. Keep summaries, decisions,
  architecture notes, and curated exports concise.
- SQLite is the searchable agent-memory layer for detailed findings,
  file/symbol indexes, references, commands, failures, and evidence-backed notes.

Do not blindly migrate all Markdown into SQLite. When Markdown memory becomes
too large to read cheaply, introduce or rebuild the SQLite memory/index and keep
Markdown as the concise reviewable export.

## RAG System Structure

When the project needs retrieval that can grow beyond Markdown and SQLite FTS,
add:

```text
tools/project-memory/rag-system.json
```

Use `templates/rag-system.template.json` as the starter shape and
`patterns/RAG_SYSTEM_STRUCTURE.md` as the architecture rule. Keep vector stores
such as Chroma, Qdrant, and pgvector behind retrieval adapters so prompts and
agent workflows do not depend on one storage backend.

Before enabling vector retrieval, prepare semantic-ready chunks and embedding
metadata with `patterns/SEMANTIC_RAG_RETRIEVAL.md`. Keep generated files such as
`tools/project-memory/semantic-corpus.jsonl` ignored.

For a local semantic MVP, build Chroma from exported chunks:

```powershell
python .\tools\project-memory\build_project_memory_index.py rebuild
python .\tools\project-memory\build_project_memory_index.py export-chunks
uv run --with chromadb python .\tools\project-memory\build_chroma_index.py rebuild
```

Run RAG health checks and retrieval evals when an eval runner is present:

```powershell
python .\tools\project-memory\rag_check.py --skip-vector run
uv run --with chromadb python .\tools\project-memory\rag_check.py run
```

The check should verify generated-ignore rules, count consistency across
enabled retrieval layers, and expected source paths in top keyword, semantic,
or hybrid results. Test retrieval evidence first; do not use a model's
free-form answer wording as the primary eval target.

## Optional Code Intelligence

Keep project memory authoritative for requirements, workflows, decisions,
business rules, exact project metadata, and durable notes. For deeper symbol,
call/dependency, Git-risk, or code-health evidence, configure the optional
`code_intelligence` section in `rag-system.json` and use:

```powershell
python .\tools\project-memory\code_intelligence.py status
python .\tools\project-memory\code_intelligence.py route "who calls this symbol?"
python .\tools\project-memory\code_intelligence.py invoke context MySymbol
```

Keep the provider disabled until it is separately installed, indexed, and
verified. Only allowlist read-only MCP tools, keep generated indexes ignored,
and verify provider results against current source. Repowise is the first
tested adapter, not a hard dependency. Follow
`patterns/CODE_INTELLIGENCE_ADAPTERS.md`.

## Activation Limits And Diagnostics

Start with Markdown specifications and targeted search. Use generated databases
when size or retrieval failures justify them.

Default SQLite/FTS activation limits:

- tracked text sources exceed 50 files;
- project-memory Markdown/JSON exceeds 25 files or about 200 KB;
- feature specifications exceed 10 files;
- exact retrieval repeatedly misses paths, commands, symbols, or feature specs;
- startup restore needs too many focused file reads.

Default vector activation limits:

- semantic-ready chunks exceed 300;
- curated project-memory specs exceed about 500 KB;
- feature specifications exceed 25 files;
- conceptual retrieval misses relevant memory at least three times;
- multiple agents need conceptual lookup over the same memory.

Use `gi sql` to inspect SQLite/FTS readiness and metrics. The agent should read
`rag-system.json`, run the local stats helper when available, count memory/spec
files, compare them with limits, and report whether SQL indexing is absent,
current, stale, or recommended.

Use `gi vector` to inspect vector readiness and metrics. The agent should read
embedding/vector metadata, check semantic corpus size and chunk count, run the
vector adapter status helper when available, and report collection, record
count, index path, freshness caveats, and readiness.

## Suggested Files

- `pending-tasks.md`: active project-wide plans and multi-step work.
- `STUDY_PLAN.md`: roadmap for understanding the project.
- `git-preferences.json`: commit-message language preferences.
- `system-preferences.json`: agent user-facing working language preferences.
- `rag-system.json`: RAG source, exclusion, retrieval, context-packet, and
  writeback configuration.
- `architecture-migrations.md`: major architecture rewrites, platform moves,
  framework replacements, and storage/service/routing migrations.
- `specs/`: platform-neutral feature, business-rule, data-model, and
  integration-contract specifications.
- `specs/integration-contracts/connected-projects.md`: register of external
  repositories, services, libraries, docs, tools, and sibling workspaces.
- `retrieval-evals.json` or `semantic-retrieval-evals.md`: small eval set for
  keyword, semantic, and hybrid retrieval quality.
- `rag_check.py`: optional health and retrieval eval runner.
- `code_intelligence.py`: optional provider-neutral MCP bridge for symbol,
  dependency, risk, and health evidence.
- `build_chroma_index.py`: optional local Chroma adapter when semantic
  retrieval is enabled.
- `NOTES.md`: reviewable export of durable notes from local agent memory.
- `architecture.md`: verified architecture notes.
- `decisions.md`: durable decisions and rationale.
- `known-issues.md`: recurring bugs, caveats, and workarounds.

Avoid folders such as `evidence/`, `photos/`, `outputs/`, `runs/`, `exports/`,
or `builds/` inside project memory unless the project has explicitly defined
them as small, reviewable manifests rather than raw artifact storage.

## Task Planning

For analysis, refactoring, migration, or multi-step implementation tasks, keep a
concise checklist in `pending-tasks.md` or a dedicated task plan in this folder.

Include:

- goal
- planned changes
- execution order
- risks or dependencies
- verification steps

Update progress as meaningful steps complete. Keep plans task-relevant and avoid
full diffs, large logs, generated outputs, secrets, credentials, or private
production data.

## Rule

If a future agent would waste time rediscovering the same fact, write it down.
