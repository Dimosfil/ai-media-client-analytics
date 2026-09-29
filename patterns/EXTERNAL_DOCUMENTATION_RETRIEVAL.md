# External Documentation Retrieval

Use external documentation retrieval tools such as Context7 only for current
library, framework, SDK, and API documentation.

## When To Use Context7

- Use Context7 when the user asks for current documentation or when a coding
  task depends on fast-moving public APIs.
- Use Context7 when a project has already configured the MCP, CLI, plugin, or
  API integration for it.
- Prefer exact library IDs and pinned versions when the project or user names
  them.
- Treat retrieved examples as documentation evidence. Verify the current local
  source files, project configuration, lockfiles, and tests before editing.

## Precedence

- Prefer project-local `AGENTS.md`, runbooks, project memory, manifests,
  source code, and configured service guide/contract endpoints for current
  project behavior.
- Prefer official OpenAI documentation workflows for OpenAI product and API
  questions.
- Prefer vendor-owned documentation and primary sources over third-party
  summaries when Context7 results disagree with source docs.
- Do not use Context7 as a task manager, service discovery mechanism, durable
  project-memory store, or replacement for exact graph/file queries.

## Privacy And Scope

- Do not send secrets, credentials, tokens, private keys, private source code,
  private business rules, user data, production data, telemetry, local paths, or
  project-memory contents to Context7 or similar external documentation
  services.
- For private repositories, private docs, Confluence, OpenAPI specs, or other
  private sources, require explicit project configuration and user approval for
  the exact source scope before querying or indexing.
- Keep private-source exclusions, access rules, and generated indexes
  project-local and out of shared instructions.
- If a query would reveal sensitive implementation details, rewrite it as a
  generic library/API question or ask the user for approval.

## Agent Behavior

- Mention when external documentation retrieval was used for a decision.
- Keep retrieved context small and task-relevant.
- Do not install, enable, or configure Context7 globally unless the user asks or
  project-local instructions require it.
- If Context7 is unavailable, fall back to official documentation or primary
  sources rather than guessing unstable API details.
