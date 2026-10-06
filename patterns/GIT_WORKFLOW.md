# Git Workflow

Use this pattern for project Git policy, commit requests, and commit message
language preferences.

## Default Policy

- The agent may edit and verify files.
- The user reviews and commits unless they explicitly ask the agent to commit.
- Do not run `git commit`, `git push`, branch changes, destructive git commands,
  or history rewrites without an explicit user request.
- Treat `gi коммит`, `gi пуш`, `gi коммит пуш`, and `gi только пуш` as explicit
  git finish requests for the current project.
- Treat `gi пул`, `gi pull`, and `ги пул` as explicit requests to update the
  current branch from its configured upstream.
- `gi коммит` means commit only.
- `gi пуш` means commit the scoped current changes, then push the current branch.
- `gi коммит пуш` means the same as `gi пуш`.
- `gi только пуш` means push existing local commits only; do not create a new
  commit for this command.
- A project-local statement that the user normally creates commits is a default,
  not a veto of these explicit commands. If a project instead unconditionally
  forbids agent-created commits, follow that specific rule and report that
  `gi пуш` cannot complete until the project rule changes. Do not advise a
  manual commit followed by `gi пуш`: that command does not fall back to
  push-only behavior.
- Do not reinterpret `gi пуш` as a raw `git push`, a retry of a previous
  terminal push, or a push-only command. Push-only behavior is reserved for
  `gi только пуш`.
- `gi пул` means fetch and pull the current branch only; do not switch branches,
  rewrite history, or pull from a different remote unless the user explicitly
  asks.
- Exception: a successful `gi обновить` / `gi обновись` is an explicit request to
  commit and push the resulting instruction-kit update changes, if the current
  project is a git repository with a configured remote and the changes are
  limited to instruction-kit files.
- If the current project is not a git repository, still apply successful GI
  instruction-kit updates when possible, then skip commit/push and report that
  git is unavailable for this project.
- In a shared instruction-library repository, a user request to add or accept a
  reusable rule is an explicit finish request for that accepted rule: update the
  relevant files, verify them, commit and push only the scoped rule changes,
  then run the `gi обновить` update flow when accepted instruction-kit
  propagation applies. Do not include unrelated dirty worktree changes, secrets,
  private data, or generated noise; do not recurse into another commit/push
  merely because this finish rule itself was added or run.
- Apply accepted RAG, startup, command, workflow, and agent-safety rules to the
  shared instruction source repository itself and to copied-project propagation
  artifacts in the same scoped change. Keep source live files, templates,
  migrations, version/changelog, and local instruction-kit metadata in sync.
- Treat dirty worktrees as normal.
- Do not revert user changes unless the user explicitly asks.
- Keep changes scoped to the current task or the standalone command's scope.
- A Git-finish command authorizes Git finalization, compact read-only inspection,
  and proportionate verification of the resolved commit scope. It does
  not authorize new product implementation, test-expectation rewrites, runtime
  or service repair, dependency changes, broad cleanup, or other tracked-file
  edits merely to make the worktree or verification clean.
- Resolve commit scope in order: explicit user-selected paths/changes, the active
  conversation task, then the standalone command's repository scope. With no
  selected paths or active task, `gi commit`, `gi push`, and `gi commit push`
  (including Russian aliases) select all current eligible tracked and untracked
  changes in the verified repository. Apply this default in a new chat without
  asking whether to include all changes solely because history is absent or the
  dirty file count is large. Inspect the selected changes and briefly report
  scope and exclusions before staging. Exclude secrets, prohibited content,
  generated noise, and work explicitly reserved separately.
  Never infer that all dirty files belong to an active task from similarity or
  timestamps. Ask only when concrete
  conflicting scope instructions or inseparable excluded changes prevent safe
  selection. `gi only push` does not select working-tree changes.
- Do not commit secrets, credentials, local databases, logs, or generated
  caches.
- Keep rebuildable application builds, frontend bundles, installers, and
  intermediate build output in dedicated ignored directories. Do not add,
  stage, commit, or push them to source repositories without an explicit
  approved project-specific exception. Keep source, required source assets,
  manifests, lockfiles, build configuration, and build/packaging scripts
  versioned. Follow `patterns/AGENTS_RUNTIME/09-build-and-install.md` for
  output layout, tracked-output cleanup, and clean-checkout verification.
- Exclude build output during Git finish, including already tracked output
  changes; allow scoped index removals from authorized output cleanup.
  Do not mistake generated code or database migrations for build
  artifacts. Git finish alone does not authorize moving output, changing
  build/deployment paths, or removing unrelated tracked files from the index;
  complete that work during an authorized implementation/cleanup task.
- Never add, stage, commit, or push content payloads such as LLM or other model
  weights/checkpoints, photos, video, audio, datasets, archives, or similar
  large binary artifacts. Keep them in project-approved artifact or object
  storage outside Git. Commit only compact manifests, source URLs, checksums,
  or retrieval instructions, and add project-local ignore rules that prevent
  the prohibited content from being staged again. An exception requires the
  user's explicit approval of the exact content and Git storage approach for
  the current project.
- Prefer `git diff --stat` and targeted file checks over full diff dumps.

## Finish Workflow

Before any `gi коммит`, `gi пуш`, `gi коммит пуш`, or `gi только пуш` action:

- finish every task-scoped filesystem write first, including project-memory,
  handoff, generated metadata, formatting, and verification-driven corrections;
  do not create or update a tracked task artifact after staging or committing;
- inspect `git status --short`;
- inspect untracked and unusually large files before staging and exclude
  prohibited model/media/content payloads; add an ignore rule during Git finish
  only when the payload was created by the active scoped task or the ignore
  change was already authorized, otherwise leave it unstaged and report it;
- inspect staged and unstaged changes with compact stats or targeted checks;
- identify the current branch and configured remote;
- for a push, identify the upstream before staging or committing. If it is
  absent, ask which remote branch to use and set tracking on the first push;
  never infer the destination from another remote branch containing HEAD;
- keep changes outside the resolved scope out of the commit; pre-existing user
  changes are eligible under the standalone repository scope unless excluded;
- stop and explain the blocker if scope is ambiguous, conflicts are present,
  secrets may be included, the project is not a git repository, no remote is
  configured for a push, or push fails.
- Do not start a project-memory audit, feature work, or new product test cycle
  solely because Git finish was requested. Implementation work completes its
  own writeback and verification. Follow a more specific project-local
  finish-time gate when one is expressly required; a failing gate does not
  authorize unrelated code or test repairs, runtime deletion, or service
  rebuilds/restarts.

For `gi коммит`:

- stage only scoped task changes;
- create one commit using the configured commit-message language preferences;
- do not push.

For `gi пуш` and `gi коммит пуш`:

- stage only scoped task changes;
- create one commit using the configured commit-message language preferences;
- if there are no scoped changes to commit, report that clearly instead of
  running a push-only fallback;
- push the current branch to its configured upstream.

For `gi только пуш`:

- do not stage files;
- do not create a commit;
- push only already committed local work on the current branch.

After the last commit or push and before the success response:

- run a final `git status --short` after the last filesystem mutation;
- verify the resulting commit contains every intended task-scoped tracked
  change, and for a push verify the local branch matches its configured
  upstream;
- distinguish pre-existing unrelated dirt from new task-scoped residue; never
  claim a clean worktree merely because local and remote HEAD match;
- if a required task file was changed after the commit, do not silently leave
  it behind or report full success: include it through the authorized finish
  workflow before pushing, or report the exact uncommitted remainder and the
  operation as incomplete;
- do not mutate tracked task files after this final status check. If another
  mutation becomes necessary, repeat verification and the applicable authorized
  finish workflow before responding.

## Pull Workflow

Before any `gi пул`, `gi pull`, or `ги пул` action:

- inspect `git status --short`;
- identify the current branch and configured upstream;
- inspect compact incoming/outgoing state when possible;
- stop and explain the blocker if the project is not a git repository, no
  upstream is configured, the worktree has unresolved conflicts, or local
  changes make the pull unsafe.

For `gi пул`:

- fetch from the configured remote for the current branch;
- pull only the current branch from its configured upstream;
- avoid branch switches, history rewrites, rebases, or broad cleanup unless the
  user explicitly asks;
- if conflicts appear, inspect the conflicted files and resolve only obvious,
  low-risk conflicts where intent is clear and user changes are preserved;
- run a targeted verification or at least `git diff --check` after resolving
  documentation-only conflicts;
- if a conflict needs product judgment, touches secrets or unrelated user
  changes, spans files outside the requested scope, or cannot be resolved with
  high confidence, stop and ask the user with a concise summary of the conflict
  and the available choices.

## Commit Message Languages

Projects may keep commit message preferences in:

```text
tools/project-memory/git-preferences.json
```

Default language policy:

- English is the primary commit-message language.
- Additional languages are optional.
- When at least one additional language is selected, write commit messages in
  English plus the selected language or languages.
- Keep each language concise.

Suggested commit format:

```text
English summary

<Selected language>: translated summary
```

If multiple additional languages are selected, add one translated summary line
per language.

## Supported Startup Choices

Offer these five languages when a project is configured:

- English
- Russian
- Spanish
- German
- French

English should be selected by default and treated as the primary language.

## Selection Workflow

During project bootstrap, copy the default preferences file and do not pause to
ask about commit-message languages.

When the user asks in chat to configure commit-message languages, update
`tools/project-memory/git-preferences.json` directly and briefly summarize the
new setting. Ask a short clarification only if the requested languages are
ambiguous.

Treat `gi commit language`, `gi коммит язык`, `ги коммит язык`, and older
`gi язык коммита` forms as the short shared-instruction command forms for this
workflow.

Do not use commit-language commands to change the agent's user-facing working
language. That is configured separately with `gi system language`, `gi систем
язык`, or `ги систем язык` in `tools/project-memory/system-preferences.json`.

Do not infer additional commit-message languages from the user's UI language or
message language. If the user says only "choose/select commit language" without
naming languages, ask which additional languages to enable, or offer the
supported list.

For ambiguous commit-language selection, present a concise plain numbered
selection checklist instead of a prose-only list. Show `English` as always selected,
explain that it is the required primary commit-message language, and mark
current additional languages as checked. Ask the user to reply with language
names or numbers. Render each option as a plain inline checkbox marker with the
number and label on the same physical line, such as `[x] 1. English` or
`[ ] 2. Russian`. Do not use Markdown task-list syntax such as
`- [x] 1. English` or ordered-task syntax such as `1. [x] English`, because
some chat renderers split the checkbox control and label onto separate lines.
Never emit a standalone checkbox line followed by a separate numbered label
line.

Example:

```markdown
Which additional commit-message languages should be enabled?

English is the required primary commit-message language and cannot be disabled.
Reply with numbers or language names for any additional languages to enable.

[x] 1. English (primary, required)
[x] 2. Russian
[ ] 3. Spanish
[ ] 4. German
[ ] 5. French
```

When reporting the change, mention the plain path
`tools/project-memory/git-preferences.json`. Do not emit malformed markdown
links or placeholder links.

Do not answer a chat request only by telling the user to run a PowerShell
command. The selector is a helper for users who explicitly want to run the
configuration themselves:

```powershell
.\tools\select-git-commit-languages.ps1
```

The startup script may also expose the same choice:

```powershell
.\tools\agent-start.ps1 -ConfigureGitCommitLanguages
```

Run the same command any time the user asks to change commit language
preferences.

The script should save the selected languages in project memory so future agents
working in the same project can reuse the preference.
