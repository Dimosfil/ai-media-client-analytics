# Modular Service Engineering With Agents

Use this pattern when a product is large enough that several modules or agents
must contribute to one working system. Scale the documents and checks to the
actual complexity. A module is a responsibility boundary; it does not imply a
separate process, repository, database, or deployable service.

## System Before Parts

- Start with the product outcome and at least one end-to-end user or operator
  workflow. Record the system boundary, important quality targets, constraints,
  and the observable result that proves the assembled system works.
- Draw a small system map: subsystems, modules, consumers, dependencies, data
  owners, integration edges, and runtime/deployment units. Mark planned edges
  separately from implemented ones and link current claims to source or tests.
- Decompose by cohesive behavior, data ownership, and reasons to change. Avoid
  splitting solely by team size, file count, framework layer, or agent count.
- Record significant boundary decisions and alternatives in project-local
  architecture notes. Revisit a boundary when integration evidence shows that
  it hides shared state or forces repeated cross-module changes.
- Use `templates/SYSTEM_MAP.template.md` as a starting shape, not as mandatory
  paperwork for a small project.

## Module Definition And Passport

A module owns a bounded responsibility, exposes an explicit contract, declares
dependencies, and can be checked through its public entry points. Its internals
remain private to consumers. A module can contain smaller components and can
run inside a larger application or as an independently deployed service.

For each consequential module, keep a concise passport based on
`templates/MODULE_PASSPORT.template.md` in project-local documentation or
project memory. Record:

- purpose, owner of the contract, status, and place in the system map;
- responsibilities, excluded responsibilities, and owned data or state;
- public operations/events and links to their contract source of truth;
- dependencies and permitted dependency direction;
- invariants, side effects, error and empty-state behavior;
- configuration, health/diagnostics, and relevant resource limits;
- verification through public entry points and at least one assembled workflow;
- current implementation and evidence, with planned behavior labeled clearly.

Give each contract, schema, default, and business rule one authoritative source.
The passport links to that source rather than duplicating it. Record ownership
by project role or maintained area; do not tie durable ownership to one agent
chat or temporary task.

## Contracts And Integration Edges

- Agree on the observable contract before independent agents implement its two
  sides. Identify caller and provider, input/output meaning and validation,
  errors, empty results, side effects, and invariants. Use
  `templates/MODULE_CONTRACT.template.md` when a separate contract is useful.
- State data ownership explicitly. Consumers use a documented interface or
  shared read model; they do not rely on another module's private tables,
  internal types, mutable state, or undocumented files.
- For network or asynchronous edges, specify timeouts, retries, duplicate
  handling, ordering, cancellation, partial failure, and recovery where they
  affect behavior. Do not prescribe one transport or transaction strategy to
  every project.
- Define how compatible changes are introduced and how breaking changes are
  coordinated with consumers. Show the overlap period and retirement condition
  when old and new versions run together.
- Keep schema examples and contract tests aligned with the actual public
  boundary. Test provider and consumer expectations, including important errors.

## Shared System Rules

Identify the project-local authority for authentication and authorization,
configuration and secrets, identifiers and time, error semantics, logging and
tracing, resource limits, data migrations, and release health. Each module
documents how it uses these rules. Share code only where a real common contract
or repeated behavior warrants it; avoid a utility package that becomes an
unowned dependency for every module.

## Agent Work And Coordination

- Give each agent a bounded goal, affected module(s), writable scope, relevant
  system map and contracts, expected checks, and a handoff format. Agents read
  only task-relevant neighboring passports and current source.
- Name one accountable integrator for a multi-module change. Module owners
  implement within their boundary; the integrator checks the full workflow and
  resolves cross-module mismatches. One agent may fill several roles.
- Parallelize implementation after shared contracts and file/data ownership are
  clear. Identify overlapping edits and decisions that must be sequenced.
- When work reveals a contract change, list affected consumers and the rollout
  order before editing the public boundary. Do not let a local implementation
  silently redefine the system agreement.
- In the handoff, state changed behavior, contracts, source files, checks and
  evidence, remaining risks, and the next integration step. Preserve durable
  decisions in project documentation or focused project-memory specs, not only
  in chat or a transient task summary.

## Assembly And Verification

- Build a small useful vertical workflow through the required modules early.
  Extend the system through working slices so integration assumptions are tested
  while they are still cheap to change.
- Check module behavior at its public boundary, provider/consumer contracts,
  real integration edges, and an end-to-end outcome. Add load, security,
  recovery, and failure checks where quality targets or risks require them.
- Treat mocks as evidence only for the behavior they model. Verify critical
  paths with actual dependencies before claiming the assembled system works.
- Before completion, compare code, schemas, tests, runbooks, system map, and
  focused project-memory contracts for drift. Record unavailable checks as
  concrete gaps instead of presenting an unverified module as integrated.

## Change And Replacement

For a module split, replacement, or public contract change, identify every
consumer and stateful dependency. Plan compatibility, data migration, rollout,
observation, rollback, and removal of the old path. Verify both the new module
behavior and the affected end-to-end workflow. Record significant structural
changes in the project's architecture migration history.

## Completion Standard

A module is ready for integration when its responsibilities, contract, data
ownership, dependencies, implementation, and public-boundary checks are clear.
The system is ready for the claimed scope when the assembled workflows and
relevant quality targets have been verified with their real integration edges.
