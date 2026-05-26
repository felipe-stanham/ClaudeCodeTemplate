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

---

## README

When adding or removing a skill or agent from `Template/`, update the feature table in `README.md` in the same commit.

---

## No automated tests

Validate changes by reading the diff carefully. Check that:
- Skills reference the correct file paths and index conventions from `CLAUDE.md`
- New templates follow the same comment-driven placeholder style as existing ones
- The version comment is on line 1 of `Template/CLAUDE.md` (the `template-sync` skill greps lines 1–5)
