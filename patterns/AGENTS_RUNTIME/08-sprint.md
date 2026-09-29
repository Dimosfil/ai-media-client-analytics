## Sprint Commands

- Treat `gi start sprint`, `gi sprint start`, and equivalent active-sprint
  wording as requests to take the active Sprint/Cycle into work through the
  configured task manager. Resolve the manager through config-service, read the
  guide and contract, request the active sprint/cycle or next task through the
  documented operation, move work through the documented lifecycle states, and
  submit completion through the manager contract. Stop with the exact blocker
  instead of falling back to generic `gi start`, local task notes, raw intake,
  guessed endpoints, or filesystem task edits.
- Treat `gi local sprint`, `gi sprint local`, `gi локальный спринт`,
  `gi спринт локально`, and equivalent explicitly local sprint wording as
  requests to run a local sprint checklist without a
  configured task manager or config-service. Use the sprint content supplied in
  the current message, current chat context, or a project-local planning file
  named by local instructions. If no sprint content is available, ask one short
  question for the local sprint goal and task list. Track progress only in the
  current response or in a project-local checklist file when local instructions
  already define one; do not create raw manager intake, edit task-manager
  internals, resolve config-service, or claim that a visible Sprint/Cycle was
  created or updated. If the user asks for `gi start sprint` and no manager is
  configured, stop with the manager/config-service blocker and mention
  `gi local sprint` as the explicit local alternative.
