# Development Tool And Product Boundaries

Developer tools, orchestrators, task managers, agent harnesses, code generators,
and scaffolding systems must stay separate from the products they build.

The development runtime owns coordination, planning, execution, review,
configuration, and artifact management. The product under development is data:
task input, generated source, a selected workflow run, a build artifact, or a
project-local repository. Do not let one demo or test product become the
runtime's identity.

When explaining this rule, do not use the current project as the default
example. This pattern exists for any project that builds, coordinates, tests, or
manages other artifacts. Use neutral terms unless the user explicitly requests a
comparison to a named repository or product.

## Core Rule

- Treat every product, demo, customer, project type, task, workflow run, and
  generated artifact as replaceable input or output.
- Use `tools/` for durable development tooling, automation scripts, adapters,
  bootstrap commands, deployment helpers, verification helpers, agent-memory
  tooling, and redacted example manifests. Before writing under `tools/`,
  classify the file as tooling or product material. Product runtime/source
  packages, product plugin implementations, product tests, full product
  documentation, generated product output, selected-run artifacts, uploaded
  site contents, screenshots, raw exports, build bundles, downloaded datasets,
  and one-off work results do not belong under `tools/` merely because an agent
  or script created them. Store product source in the project source/package
  tree, tests in the test tree, product documentation in `README.md`, `docs/`,
  or runbooks, and generated/evidence files in project-local artifact,
  evidence, output, data, docs-asset, build, or release locations documented by
  the project.
- File type does not establish durability. A `.py`, `.ps1`, shell script, or
  other executable made for one research question, environment probe, scrape,
  data inspection, or temporary diagnostic is a one-off work file. Do not put
  it under `tools/`, including convenient-looking subtrees such as
  `tools/research/`, `tools/probes/`, or `tools/scratch/`, unless that subtree is
  an already documented reusable subsystem and the new script satisfies its
  stable contract. Prefer inline execution; otherwise use a documented ignored
  scratch/temp location outside `tools/`, remove the script after use, and keep
  only necessary evidence or outputs in their documented artifact location.
- Promote a script to durable tooling only when the project has an expected
  future caller, reusable project-owned behavior, a stable invocation contract,
  and enough documentation or verification to maintain it. A useful result in
  the current task alone is not sufficient.
- Treat `tools/project-memory/` as a narrow exception for compact
  implementation-driving specifications, decisions, contracts, and evidence
  references used by agents. It is not a source package, plugin directory,
  product test tree, full documentation site, artifact bucket, or dump folder.
- Do not let one selected request, run, generated artifact, or debugging
  example define the generic runtime contract. Extract the reusable behavior and
  keep the concrete case as replaceable task data, fixture data, or documented
  example evidence.
- Do not hard-code product names, demo domains, customer names, task titles,
  folder slugs, repository names, UI labels, agent profiles, stacks, routes,
  ports, or workflow contracts into the development runtime unless they are true
  runtime concepts.
- If a value can differ for the next generated product, next user, next run, or
  next environment, load it from task data, a manifest, project-local config,
  service discovery, or explicit user selection.
- Keep examples, seed data, screenshots, and tests clearly marked as examples.
  They may verify behavior, but they must not define the generic runtime
  contract.
- Search for old demo names and generated product names before finishing a
  generic orchestrator, generator, task-manager, or agent-harness change.

## Workflow And Progress Logs

- A workflow log is state for a selected or active run, not a global task board
  and not a product identity.
- Name progress UI by the generic job it performs, such as `Progress`,
  `Execution`, or `Workflow log`, instead of naming one test product.
- Show detailed step logs only for the active or selected run. For completed
  runs, collapse the log by default or show a compact final status line.
- Do not duplicate a Kanban board, task list, or lifecycle state view with a
  large second panel unless the second panel exposes different debugging
  evidence.
- Include the meaningful execution sequence when useful for debugging, such as
  planner produced a plan, executor applied changes, reviewer checked results,
  and final event status.

## Architecture Requirements

Use `patterns/ARCHITECTURE_AND_CODE_QUALITY.md` as the general architecture and
code-quality baseline. For development tools and generators, apply that baseline
with these additional product-boundary constraints:

- Follow OOP, SOLID, DRY, clean-code, maintainability, extensibility, and
  established architecture-pattern principles where they fit the stack,
  including clean architecture, microservices, DDD, and equivalent
  stack-appropriate patterns. In object-oriented code, prefer
  single-purpose classes, open extension points, substitutable implementations,
  small interfaces, and dependencies inverted behind ports/adapters.
- In non-OOP stacks, preserve the same boundaries with cohesive modules,
  functions, services, protocols, and typed or validated data contracts.
- Apply DRY to repeated knowledge and behavior, but avoid premature abstractions
  when similar code does not yet share a stable meaning.
- Keep orchestration logic separate from product/domain logic, UI rendering,
  persistence, external service adapters, filesystem layout, and generated
  artifact content.
- When a tool needs to read or write generated outputs, make the output root an
  explicit project-local configuration, task payload, manifest, or command
  argument. Validate that target before writing instead of falling back to the
  tool's own source folder.
- Prefer established architecture patterns that fit the stack, such as
  layered architecture, hexagonal/ports-and-adapters, clean architecture,
  domain-driven design, microservices, feature modules, MVC/MVVM, repository
  adapters, command handlers, and explicit service contracts.
- Inject or configure product-specific behavior through task payloads,
  manifests, plugins, adapters, or project-local configuration instead of
  branching on a concrete product name.
- Keep tests at the boundary: one test may use a sample product, but assertions
  should prove generic behavior such as "uses task-provided slug" or "renders
  selected run log", not "knows about one sample domain".

## Hard-Code Audit Checklist

Before claiming a development tool is product-agnostic, check the touched paths
for:

- product or demo names;
- customer or business-domain names;
- fixed repository, folder, or artifact slugs;
- generated or downloaded outputs written below `tools/` without an explicit
  project-local tooling contract that marks them as small reviewable manifests;
- product runtime/source packages, plugin implementations, tests, or full
  product docs placed under `tools/` instead of source, test, or documentation
  locations;
- fixed stack choices that should come from task data;
- fixed ports, URLs, service IDs, or dashboard links;
- UI copy that names a generated product instead of the runtime feature;
- workflow steps tied to one task shape instead of the documented run contract;
- tests whose expected values encode a demo as the default runtime contract.

Move findings into task input, manifests, configuration, service discovery,
fixtures, or example docs. If a cleanup is too large, record the remaining
hard-code debt in project memory with evidence paths.

## Verification

- Run focused tests for the generic runtime contract and at least one sample
  product/task fixture.
- Search the changed runtime code and tests for the old product/demo names.
- Verify default cards, labels, folders, and workflow logs use neutral runtime
  terms unless a user-selected product is currently active.
- Verify completed workflow runs render compactly or collapsed when their
  detailed log is no longer the user's active debugging surface.
