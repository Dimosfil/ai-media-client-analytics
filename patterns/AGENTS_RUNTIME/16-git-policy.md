## Git Policy

Default policy: the agent may edit and verify files; the user reviews and
commits unless they explicitly ask the agent to commit. Follow
`patterns/GIT_WORKFLOW.md` for commit requests, dirty worktrees, diff hygiene,
and project commit-message language preferences.

- `gi пуш` / `ги пуш` explicitly requests a scoped commit followed by a push;
  `gi только пуш` requests a push of existing commits only. A project rule that
  the user commits by default does not cancel these explicit commands. An
  unconditional project-local ban on agent commits does override them: report
  the conflict instead of treating `gi пуш` as push-only or suggesting a manual
  commit followed by the same command.
- Before staging for a push, identify the current branch and its upstream. If
  no upstream exists, obtain the intended remote branch before committing and
  set tracking on the first push. Do not infer the destination from another
  remote branch that contains the current HEAD.

- Treat commit/push as the final task-write boundary: complete task-scoped
  tracked writes before staging, then recheck `git status --short` after the
  last mutation and after commit/push. Local and upstream HEAD equality does not
  prove that the worktree is clean. Never report a complete clean finish while
  a new task-scoped diff remains.
- Git finish does not start a project-memory audit, specification writeback,
  feature implementation, or product test cycle. Those belong to the
  implementation task. Perform only the requested Git operation and the
  compact Git safety checks below, unless a more specific project-local rule
  expressly requires another finish-time check.
- Treat Git finish as finalization of an already established scope, not as a new
  implementation or repair task. Resolve scope only from the active conversation
  task or explicit user-selected changes; never classify the whole dirty
  worktree as one package from apparent similarity. If scope is ambiguous, stop
  before staging or writes and ask what to include.
- A failed finish-time check does not by itself authorize product fixes, test
  rewrites, runtime-state deletion, dependency changes, service restarts, or
  broad cleanup. Correct only failures caused by the scoped work when the fix is
  already covered by the original task; otherwise report the blocker.
- Before staging, inspect untracked and unusually large files. Never add, stage,
  commit, or push content payloads such as LLM or other model
  weights/checkpoints, photos, video, audio, datasets, archives, or similar
  large binary artifacts. Store them outside Git and track only compact
  manifests, source URLs, checksums, or retrieval instructions. Add an ignore
  rule during finish only for active-task output or when already authorized;
  leave unrelated prohibited content unstaged and report it. Proceed only when
  the user explicitly approves an exact project-specific exception and storage
  approach.
