# Template Migrations

Breaking changes per major version: what changes for an existing project, and any manual step.
`template-sync` shows every entry newer than the project's previous version at the end of a sync.

---

## 1.0.0

**Upgrading from 0.x:** run `template-sync` **twice**. The first run uses your project's old 0.x skill: it
installs the new files and the gates already work, but it can't update `settings.json` and deletes project
skills/agents. The next session start then prints "Template migration incomplete"; the second run (now the
1.0.0 skill) migrates `settings.json`, writes `.claude/.template-manifest`, and offers to restore any
project skill or agent the old sync deleted.

What changes:

- **Hooks now block.** Before 1.0.0 no hook ever blocked (wrong exit code) and project hooks never ran.
  Now: pushes need `docs/System/` updates or a `Docs-Checked: no-changes` trailer; committing, merging, or
  pushing to `main`/`master`/`tst` asks for approval; secrets in git are denied; code edits are denied
  outside a task/scope branch; `.claude/arch-check.sh` runs before every push if present.
- **No code on `dev`, ever.** Every code change gets a `T-xxxx.md` (new `task` skill) and a
  `task-T-xxxx-*` branch. Hotfixes are task branches from `main`/`tst`.
- **Checkout model.** The primary checkout stays on `dev` and is for planning; pitches, tasks, specs and
  the glossary are committed and pushed there as they are written. Code is written in a worktree per
  task/scope branch (`../<repo>-wt/<branch>`).
- **The main session no longer writes code.** The new `implementer` agent does, inside the Execution Loop
  (implementer → code-reviewer → tester → doc-updater → one commit). `code-reviewer` and `tester` now run
  on Opus.
- **Status moves to `dev`.** `[IN PROGRESS]` / `[DONE]` and INDEX updates are made on `dev` after the
  branch merges, not on the branch. `doc-updater` no longer touches INDEX files.
- **`pitch` no longer promotes.** It recommends Task / Project / Archive; `task` or `spec` performs it.
- **Project hooks (`.claude/hooks/*/project/*.sh`) run as subprocesses**, not sourced. Read the tool call
  from `HOOK_TOOL`, `HOOK_CMD`, `HOOK_FILE`, `HOOK_CWD` (or stdin JSON). Exit `2` to deny, `3` to ask; any
  other non-zero exit is reported as an error and does not block. Pre-tool hooks only fire for
  Bash / Edit / Write / MultiEdit / NotebookEdit.
- **`template-sync` stops deleting project files.** It now tracks template-owned files in
  `.claude/.template-manifest`, and also syncs `docs/templates/` and `.githooks/`. Edits you made to files
  under `docs/templates/` are overwritten — keep project-specific templates elsewhere.

Manual steps:

- Make sure `.gitignore` contains `.env`, `.deploy-secrets`, and `docs/local/` — otherwise every
  `git add`/`git commit` is denied.
- If you work on code directly in the primary checkout, move it to a worktree:
  `git worktree add ../<repo>-wt/<branch> <branch>`, then `git checkout dev` in the primary checkout.
- If a project hook relied on being sourced (shared variables, `exit` ending the dispatcher), rewrite it
  for the subprocess contract above.
