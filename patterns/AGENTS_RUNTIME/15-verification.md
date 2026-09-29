## Verification

Choose checks by changed behavior, affected layers, risk, and the documented
project contract. Complete required checks, including any explicitly requested
full test or release workflow. Use the smallest sufficient set for other tasks.
Do not add tests for reversible, low-impact edits when they only restate the
implementation and protect no meaningful behavior.

After relevant checks pass, broaden or repeat them only for a new change,
failure, unresolved concern, or mandatory project gate. Do not rerun unchanged
checks merely to gain confidence. Report unavailable checks as specific
verification gaps and continue independent authorized work.

For documentation-only changes:

```powershell
git diff --check
```

For larger changes, reread the edited files and confirm links, paths, and
checklists still match the repository layout.

For a meaningful feature, workflow, business-rule, data-model, integration, or
architecture change, compare the scoped diff with the relevant durable
contracts before calling the task complete. Check each changed behavior,
state transition, failure path, invariant, and architecture decision against
the current source and tests. Update the affected focused project-memory spec
in the same scope, or record why an existing spec already covers it. Check
affected user-facing documentation separately, and verify links and current
implementation maps. A report, handoff summary, ticket, or commit message does
not satisfy this contract check. Do not expand the check into a whole-project
audit when the change is narrow.
When a spec is added, renamed, moved, or retired, check the project-memory
README or canonical spec index and its relative links in the same batch.

After API, admin-tool, or service writes that include Russian or other
non-ASCII text, read the saved value back through the API or product UI and
check the stored data, not only terminal display. Treat literal `????`,
replacement characters such as `�` or `пїЅ`, and whole mojibake fragments such
as `Р Сџ`, `Р С™`, `РЎРѓ`, or `РЎвЂљ` where readable text is expected as failures.
Do not flag a single normal Cyrillic letter such as `Р` or `С` by itself as
corruption.

If adding a file under `templates/`, `patterns/`, or `checklists/`, update
`INDEX.md` in the same change.
