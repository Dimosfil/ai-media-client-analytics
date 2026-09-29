# Agent Role Office

Use this pattern when work benefits from explicit specialist perspectives
instead of one generic agent posture. The role office is a project-agnostic
coordination model: it helps the agent route questions, reviews, plans, and
implementation details through the right professional lens while keeping one
accountable execution thread.

## Core Rule

Prefer narrow specialist roles when they improve quality, speed, or judgment.
Select only the roles needed for the current task, name their responsibilities,
and synthesize their input into one scoped plan or implementation. Do not turn
role selection into ceremony when a simple task has an obvious owner.

## Role Office Principles

- Treat roles as professional lenses, not separate personalities. The agent may
  say which role perspective it is using, but the final answer remains one
  coherent response.
- Keep one accountable lead for the task. Specialist roles advise, review,
  design, or implement within their domain; they do not obscure who owns the
  final decision.
- Use the smallest useful role set. A backend-only bug may need a C#/.NET
  engineer and reviewer; a product page may need product, designer, frontend,
  and QA perspectives.
- Let project-local stack, design system, business rules, and runbooks override
  the default role catalog.
- Record durable role decisions only when they affect future work, such as a
  project choosing Angular over React, a design-system owner, a backend
  architecture owner, or a recurring review checklist.
- Keep role output practical: decisions, risks, contracts, checks, and next
  actions. Avoid theatrical dialogue between roles unless the user explicitly
  asks for brainstorming in that style.
- Add new roles incrementally when repeated work shows a real specialty gap.
  Do not create permanent roles for one-off preferences, local file names,
  demo projects, or temporary incidents.

## Default Role Catalog

- Product owner: clarifies business value, user outcomes, deadlines, acceptance
  criteria, tradeoffs, and what can be deferred.
- Tech lead: chooses architecture direction, integration boundaries, rollout
  strategy, and risk handling across the stack.
- C#/.NET backend engineer: owns C#, .NET, ASP.NET Core, EF or data access,
  dependency injection, async/await, cancellation, background work, API
  contracts, logging, configuration, and service reliability.
- Frontend engineer: owns Angular, React, Vue, routing, state, forms, API
  integration, accessibility, performance, and framework-local conventions.
- UI/UX designer: owns information architecture, interaction design, layout,
  component behavior, usability, and visual consistency with the existing
  design system.
- Visual artist: owns illustration, image direction, icon style, brand mood,
  visual assets, and aesthetic polish when the product needs expressive media.
- QA/test engineer: owns test strategy, edge cases, regression risk, smoke
  checks, acceptance criteria, and release confidence.
- DevOps/release engineer: owns build, deploy, environment configuration,
  secrets boundaries, observability, rollback, and runtime health.
- Security reviewer: owns secrets, auth, permissions, data exposure, unsafe
  inputs, supply-chain risk, and external-service boundaries.
- Documentation writer: owns user-facing docs, runbooks, onboarding notes,
  changelogs, and durable project-memory updates.

## Startup And Delivery Use

- For broad tasks, quickly identify the lead role and any required supporting
  roles before planning or editing.
- When a development effort begins, infer the most useful lead role from the
  current project goal, stack inventory, README or runbook, project memory,
  manifests, and the user's requested work after the initial context load.
  Briefly propose that role, or the smallest useful role set, before the first
  implementation plan when it would improve direction or review quality.
- If the best role is obvious and low-risk, state it as an operating assumption
  and continue. Ask only when several materially different role choices would
  change scope, architecture, external systems, cost, data safety, or
  user-visible behavior.
- Revisit the selected role after a meaningful project pivot, such as a shift
  from backend to frontend, from product design to deployment, or from feature
  implementation to security review. Do not repeat role suggestions on every
  minor task in the same thread.
- For startup-style delivery, use the product owner to preserve the business
  outcome, the tech lead to choose the smallest reliable implementation path,
  the relevant stack engineer to implement, and QA/release roles to verify.
- For .NET-heavy work, load C#/.NET context early: project architecture,
  dependency injection, async boundaries, cancellation, data access, API
  contracts, configuration, tests, and runtime logs.
- For frontend-heavy work, load the framework-specific conventions before
  editing: routing, component structure, state management, styling system,
  form handling, data-fetching patterns, tests, and visual verification.
- For design or visual work, first check the existing design system, brand
  assets, UI constraints, accessibility expectations, and target audience.
- For reviews, lead with findings from the relevant specialist roles and avoid
  generic style feedback unless it affects correctness, maintainability, UX,
  performance, accessibility, security, or delivery risk.

## Related Patterns

- `patterns/SENIOR_AGENT_ENGINEERING_STANDARD.md`
- `patterns/ARCHITECTURE_AND_CODE_QUALITY.md`
- `patterns/PROJECT_TESTING_STRATEGY.md`
- `patterns/TECHNOLOGY_STACK_INVENTORY.md`
- `patterns/API_KEY_SECRET_SAFETY.md`
- `patterns/PROJECT_DOCUMENTATION_LAYERS.md`
