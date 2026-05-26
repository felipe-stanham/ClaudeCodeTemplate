# Claude Code Project Template

A ready-to-use template for coding projects using [Claude Code](https://claude.ai/code). It bundles the `CLAUDE.md` project instructions, custom agents, skills, hooks, and doc templates I use across all my projects.

## What's included

| Path | Purpose |
|------|---------|
| `CLAUDE.md` | Project instructions loaded by Claude Code at session start — covers branching, environments, testing, memory, logging, and code review rules |
| `.claude/agents/` | Subagents: `code-reviewer`, `doc-updater`, `tester` |
| `.claude/skills/` | Skills: `pitch` (idea refinement), `spec` (project specification), `glossary` (ubiquitous language), `deployment-process` |
| `.claude/hooks/` | Pre-push hook that checks docs are up to date |
| `.claude/settings.json` | Claude Code settings |
| `docs/templates/` | Starter templates for `SYSTEM.md`, index files, test registry, and deploy secrets |

## Usage

1. Copy the `Template/` folder into a new project root.
2. Rename or adapt `CLAUDE.md` to your project.
3. Fill in `docs/templates/SYSTEM.template.md` → `docs/SYSTEM.md`.
4. Add `.env` and `docs/local/deployment.md` (both gitignored).

## Work artifact flow

```
Pitch (I-xxxx.md) → Task (T-xxxx.md) → Project (P-xxxx.md)
```

Ideas are refined with `/pitch`, scoped into tasks or projects, implemented on feature branches, and promoted through `dev → tst → main`.
