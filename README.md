# Claude Code Project Template

A ready-to-use template for coding projects using [Claude Code](https://claude.ai/code). It bundles the `CLAUDE.md` project instructions, custom agents, skills, hooks, and doc templates I use across all my projects.

## What's included

| Path | Purpose |
|------|---------|
| `CLAUDE.md` | Project instructions loaded by Claude Code at session start — covers the Execution Loop, branching and worktrees, environments, testing, memory, logging, and hard gates |
| `.claude/agents/` | Subagents with pinned models: `implementer` (sonnet — writes the code), `code-reviewer` (opus), `tester` (opus), `doc-updater` (sonnet) |
| `.claude/skills/` | Skills: `pitch` (idea refinement), `task` (ready-to-implement tasks, small changes, hotfixes), `spec` (project specification), `glossary` (ubiquitous language), `arch-check` (architecture invariants), `deployment-process`, `share` (shareable HTML mini-sites from docs), `template-sync` |
| `.claude/hooks/` | Hard gates: docs updated before push, protected branches ask, no secrets in git, no code outside a task/scope branch, architecture check before push |
| `.claude/settings.json` | Claude Code settings |
| `.githooks/` | `pre-commit` secrets backstop for commits made outside Claude Code |
| `docs/templates/` | Starter templates for `SYSTEM.md`, tasks, index files, test registry, deploy secrets, and the arch-check CI workflow |

## Usage

1. Copy the `Template/` folder into a new project root and create the `dev` branch — the primary checkout stays on it.
2. Fill in `docs/templates/SYSTEM.template.md` → `docs/SYSTEM.md` (project-specific instructions go there, not in `CLAUDE.md`).
3. Add `.env` and `docs/local/deployment.md` (both gitignored), and run `git config core.hooksPath .githooks`.
4. To update an existing project, run the `template-sync` skill. Upgrading from 0.x: run it twice — see `Template/.claude/skills/template-sync/MIGRATIONS.md`.

## Work artifact flow

```
Pitch (I-xxxx.md) → Task (T-xxxx.md) → Project (P-xxxx.md)
```

Ideas are refined with `/pitch`, scoped into tasks (`/task`) or projects (`/spec`) on `dev`, implemented in a worktree per task/scope branch, and promoted through `dev → tst → main`.

## Workflow and model routing (v1.0.0)

Opus plans and judges; Sonnet codes against tightly defined scopes. Planning runs in the main session (model chosen by you — Opus recommended, Fable opt-in). Coding, review, and testing run in subagents with pinned models. Hexagons are hard gates enforced by hooks. The primary checkout always stays on `dev`, where every planning doc (pitches, tasks, projects/specs) is committed and pushed as it is written. Code never goes to `dev` directly: every change, however small, gets a task (`T-xxxx.md`) or project scope and is built in its own worktree on a branch created from `dev`, then merged back.

**Definition of Ready** — a task or scope reaches the implementer only when it has: goal, files/modules it touches (with a pattern reference), task checklist, declarative acceptance criteria, OUT-of-scope constraints, and no open questions.

```mermaid
flowchart TD
    subgraph PLAN["Planning — main session on dev (Opus recommended · Fable opt-in)"]
        idea([Raw idea]) --> pitch["pitch skill<br/>I-xxxx.md"]
        pitch -->|not worth it| archived([Archived])
        pitch -->|recommends Task| task["task skill<br/>T-xxxx.md"]
        pitch -->|recommends Project| spec["spec skill · xhigh<br/>P-xxxx.md + spec package"]
        small([Small change / hotfix]) --> task
        task -->|outgrows task| spec
        task --> dor{"Definition<br/>of Ready?"}
        spec --> dor
        dor -->|no| refine["Refine with user"] --> dor
        pitch -.-> pushPlan
        archived -.-> pushPlan
        dor -->|yes| pushPlan["Push #1 — planning docs<br/>commit + push to dev"]
    end

    pushPlan --> branch["Branch task-T-* / scope-P-* from dev<br/>in its own worktree"]

    subgraph LOOP["Execution Loop — orchestrated by main session (writes no code)"]
        branch --> impl["implementer<br/>sonnet · xhigh"]
        impl -->|"BLOCKED: question"| ask["Ask user · update spec"] --> impl
        impl --> review["code-reviewer<br/>opus · xhigh"]
        review -->|PASS| test["tester<br/>opus · high"]
        review -->|BLOCK| rework["implementer rework<br/>opus · xhigh"]
        test -->|FAIL| rework
        rework -->|"≤ 2 cycles in total"| review
        rework -->|cycles exhausted| escalate([Escalate to user])
        test -->|PASS| docs["doc-updater<br/>sonnet · medium"]
        docs --> commit["Commit code + docs"]
    end

    commit --> push["Push #2 — implementation<br/>push scope branch"]
    push --> merge["Merge scope → dev<br/>mark DONE on dev"]
    merge --> tst["dev → tst<br/>after regression tests pass"]
    tst --> main["tst → main<br/>after your approval"]

    gEdit{{"Task-before-code<br/>code edits only on a task/scope branch"}} -.-> impl
    gCommit{{"Protected branch → ask<br/>No secrets staged"}} -.-> commit
    gPush{{"Docs updated or Docs-Checked · Protected branch<br/>Arch-check passes"}} -.-> push
    gPlan{{"Protected branch · No secrets<br/>docs-only → docs gate skips"}} -.-> pushPlan

    classDef gate fill:#fde8e8,stroke:#c0392b,color:#000
    classDef opus fill:#e8e0f8,stroke:#6c3fc5,color:#000
    classDef sonnet fill:#e0f0fb,stroke:#2b7bb9,color:#000
    class gEdit,gCommit,gPush,gPlan gate
    class review,test,rework opus
    class impl,docs sonnet
```
