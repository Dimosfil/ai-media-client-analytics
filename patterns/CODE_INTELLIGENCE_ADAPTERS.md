# Code Intelligence Adapters

Use an optional code-intelligence provider when a project needs symbol context,
call/dependency graphs, change-risk evidence, Git-aware hotspots, or code-health
signals beyond the project-memory index.

## Boundary

Code intelligence complements project memory; it does not replace it.

| Question or fact | Primary authority | Supporting source |
| --- | --- | --- |
| Product requirements, business rules, decisions, workflows, runbooks | Project documentation and project-memory specifications | Current source code and code intelligence |
| Exact project-owned asset IDs, GUIDs, configured services, durable notes | Structured project memory and current project files | Code intelligence when it indexes that file type correctly |
| Symbols, callers, callees, imports, inheritance, code dependencies | Current source code | Code-intelligence index |
| Blast radius, Git hotspots, code health | Current source code and Git history | Code-intelligence analysis |

For a mixed question, retrieve from both sources and label the evidence. Never
turn a provider inference into a product decision or business rule without a
reviewable project source.

## Configuration Contract

Configure the layer under `code_intelligence` in
`tools/project-memory/rag-system.json`. Keep it disabled until the project has
selected, installed, indexed, and verified a provider.

The project-local contract must define:

- a provider id and project path;
- a subprocess argument array, not a shell command string;
- an explicit allowlist of read-only MCP tools;
- provider-neutral capabilities mapped to provider tool names;
- question-routing indicators in configuration rather than application code;
- freshness policy, request timeout, and generated index paths;
- environment-variable names only, never credential values.

The shared adapter supports local MCP over stdio. It does not install a
provider, initialize or rebuild an index, generate editor configuration, modify
agent instructions, or invoke tools absent from the allowlist. A project may
document separate setup and rebuild commands after reviewing the provider's
license, privacy model, generated files, and operating cost.

## Routing Contract

Use project memory for intent and durable knowledge: requirements, decisions,
business rules, workflows, specifications, policies, and runbooks. Use code
intelligence for implementation topology: symbols, callers/callees, dependency
edges, blast radius, Git risk, and health signals. Route to both for questions
that cross intent and implementation.

Keep language terms, synonyms, file extensions, and provider-specific argument
mapping in `rag-system.json`. The adapter may score those declared indicators,
but must not hide a project-specific interpretation dictionary in Python code.

## Freshness And Evidence

Every provider response should preserve its raw MCP result and add a GI
freshness envelope containing the indexed commit, provider live HEAD, local Git
HEAD, dirty-worktree state, stale status, and warnings. Treat the result as
stale when the indexed commit differs from current HEAD or the provider reports
a stale warning. A dirty worktree is a separate warning because commit equality
cannot prove that uncommitted source is indexed.

The default is to return stale evidence with an explicit warning so an agent can
fall back to current source files. Projects may set `reject_stale` when stale
results are unsafe. Verify exact source before editing in either mode.

## Safety And Privacy

- Keep generated indexes ignored and rebuildable.
- Do not send private code to a remote provider without explicit project
  configuration and user-approved scope.
- Do not pass credentials as JSON config values or command-line arguments.
- Do not enable code generation, refactoring writes, repository mutation, or
  arbitrary provider tools through a broad allowlist.
- Keep external project paths blocked by default. Use the opt-in only for an
  explicitly authorized local evaluation.
- Pin or otherwise review provider versions in project setup instructions when
  reproducibility matters.

## Repowise Adapter

Repowise is the first tested adapter, not a GI dependency or source of truth.
Its local MCP tools can provide useful symbol context, change risk, and health
signals. Projects must install and index it separately, review its AGPL license,
and keep `.repowise/` ignored. Start with the verified read-only allowlist in
`templates/rag-system.template.json`; expand it only after project-specific
quality checks. Avoid treating generated wiki text, inferred decisions,
dead-code reports, or broad searches as authoritative without source review.

## Commands

```powershell
python .\tools\project-memory\code_intelligence.py status
python .\tools\project-memory\code_intelligence.py route "who calls this symbol?"
python .\tools\project-memory\code_intelligence.py invoke context MySymbol
python .\tools\project-memory\code_intelligence.py call get_risk --arguments '{"target":"MySymbol"}'
```

`status` validates configuration and negotiates MCP without indexing the
repository. `route` is local and does not start the provider. `invoke` uses a
provider-neutral capability mapping. `call` exists for explicitly allowlisted
provider tools.

## Verification

- Parse `rag-system.json` and run the adapter unit tests.
- Confirm every configured generated path is ignored.
- Run `status` after the provider is installed and indexed.
- Exercise at least context and risk queries against known source relationships.
- Compare indexed commit, live HEAD, local HEAD, and dirty state.
- Check returned paths and edges against current source before relying on them.
- Confirm disabling or losing the provider leaves project-memory retrieval and
  direct source inspection functional.
