# Claude Code — ClaudeCodeTemplate Repo Instructions

This repo IS the template. All template content lives under `Template/`. The repo root contains only `README.md` and this file.

---

## Orientation

| Path | What it is |
|---|---|
| `Template/CLAUDE.md` | The file that ships to projects — the primary template artifact |
| `Template/.claude/skills/` | Skills bundled with the template |
| `Template/.claude/agents/` | Agents bundled with the template |
| `Template/.claude/hooks/` | Hook scripts bundled with the template |
| `Template/.claude/.template-manifest` | Template-owned files that `template-sync` copies (see Manifest) |
| `Template/.claude/skills/template-sync/MIGRATIONS.md` | Breaking changes per major version |
| `Template/.githooks/` | Git hooks bundled with the template |
| `Template/docs/templates/` | Seed files new projects copy into `docs/` |
| `README.md` | Public-facing description of the template |

Do NOT create `docs/`, `MEMORY.md`, pitches, tasks, or projects in this repo. This repo does not use the template — it is the template.

---

## Versioning

The template version is tracked in line 1 of `Template/CLAUDE.md`:

```
<!-- TEMPLATE VERSION: X.Y.Z -->
```

**Before every push that changes template content, bump this version.** Use semver:

| Change | Bump |
|---|---|
| Typo fix, wording correction, minor rule clarification | Patch (`0.x.Y → 0.x.Z`) |
| New skill, new agent, new doc template, new section in CLAUDE.md | Minor (`0.X.0`) |
| Removed or renamed skill/agent, changed hook interface, breaking CLAUDE.md restructure | Major (`X.0.0`) |

Projects running `template-sync` compare this version string to decide whether to apply an update. A missed bump means they silently skip real changes.

### Breaking changes

You do not control when, or from which version, a project upgrades — and it upgrades by running **its own, old** `template-sync`, not the one you just wrote.

- A major release must work correctly after a sync run by the oldest `template-sync` still in use (every 0.x skill behaves the same: overwrite `CLAUDE.md`, `rsync --delete` skills/agents/`hooks/*/template/`, write the old inline dispatcher, never touch `settings.json`). It must not depend on the new sync for correctness — the new sync's repair mode only finishes the migration.
- `hooks/*/dispatcher.sh` stays a stub forever. Hook-system changes go in `Template/.claude/hooks/pre-tool/template/lib/`, which every sync version copies. Keep `00-dispatch-shim.sh` in all three `template/` directories.
- Every major bump adds an entry to `Template/.claude/skills/template-sync/MIGRATIONS.md` in the same commit: what changes for an existing project, and any manual step.
- Before releasing a major, simulate the upgrade: install the template from the oldest version still in use into a scratch repo, run that version's sync steps against the release branch, check the gates, then run the new sync and check the repair.

### Manifest

`Template/.claude/.template-manifest` lists every template-owned file; `template-sync` copies those and deletes the ones a release drops. When adding, renaming, or removing a file under `Template/.claude/skills`, `agents`, `hooks/*/template`, `.githooks`, or `docs/templates`, regenerate it in the same commit:

```bash
cd Template && { sed -n '1,4p' .claude/.template-manifest; find .claude/skills .claude/agents .claude/hooks/*/template .claude/hooks/*/dispatcher.sh .githooks docs/templates -type f ! -name .DS_Store | sort | sed 's#^\(\.claude/skills/deployment-process/.*\)#seed \1#'; } > /tmp/manifest && mv /tmp/manifest .claude/.template-manifest
```

`seed` entries are files projects adapt after install (today: `deployment-process`); sync copies them only when missing.

### Executable bits

Hook scripts, dispatchers, and `.githooks/pre-commit` must be committed as `100755` (`git ls-files -s` shows the mode). `git add` resets the mode from disk, so after staging run `git update-index --chmod=+x <files>` if the files on disk are not executable.

---

## README

When adding or removing a skill or agent from `Template/`, update the feature table in `README.md` in the same commit.

---

## No automated tests

Validate changes by reading the diff carefully. Check that:
- Skills reference the correct file paths and index conventions from `CLAUDE.md`
- New templates follow the same comment-driven placeholder style as existing ones
- The version comment is on line 1 of `Template/CLAUDE.md` (the `template-sync` skill greps lines 1–5)
