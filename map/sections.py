"""Text of the template map: title, lede, legend and sections, in reading order.

Every value comes from F (facts.py); every claim the template could make false has a guard there.
"""
from __future__ import annotations

import figures
from page import CHIPS, FIG, H3, ITEMS, P, TABLE, c  # noqa: F401

TITLE = "ClaudeCodeTemplate map"
LANG = "en"

LEGEND = [
    ("e-main", "the main path"),
    ("e-call", "a call or trigger"),
    ("e-fail", "a failure, block or rework"),
    ("e-off", "optional or passive"),
    ("n-proc", "template code (skills, agents, hooks)"),
    ("n-store", "files and branches"),
    ("n-ext", "outside the project"),
    ("n-off", "optional, or yours"),
]


def lede(F: dict) -> str:
    return (f"Version {c('v' + F['version'])}. The template turns Claude Code into a process: the rules live "
            f"in {c('CLAUDE.md')}, <b>skills</b> create the work (pitch, task, project), <b>agents</b> build it "
            f"in the Execution Loop, and <b>hooks</b> stop whatever breaks the rules before it happens. This "
            f"page is generated from {c('Template/')} by {c('map/build.py')}.")


def build_sections(F: dict):
    ag = F["agents"]
    skills_rows = [[c(s), where, what] for s, where, what in F["skills"]]
    agent_rows = [[c(n), f"{a['model']} · {a['effort']}", a["when"], c(a["tools"]), a["what"]]
                  for n, a in ag.items()]
    prot = " / ".join(c(b) for b in F["protected"])

    return [
        ("overview", "The template in one picture", [
            P(f"What it installs in a project: {c('CLAUDE.md')} with the rules, {len(F['skills'])} skills, "
              f"{len(ag)} agents, hooks for {len(F['hook_types'])} Claude Code events, a git hook, and "
              f"{len(F['doc_templates'])} starter files in {c('docs/templates/')}. At startup the session reads "
              f"{c('CLAUDE.md')}, {c('MEMORY.md')}, {c('docs/SYSTEM.md')} and the glossary, and confirms the "
              f"template version. From then on it plans and orchestrates; the agents write the code."),
            FIG(figures.fig_overview(F),
                "The frame is your repository. What comes in from the left is brought by template-sync; what "
                "sits on the right runs by itself (hooks) on every tool call, commit or push."),
        ]),
        ("lifecycle", "From idea to code", [
            P("Work matures in three steps: a <b>Pitch</b> (a half-formed idea), a <b>Task</b> (one bounded "
              "change, one branch) and a <b>Project</b> (several scopes, with a spec package). All of that is "
              f"planning: it is written and pushed on {c('dev')}, in the primary checkout. Code is always written "
              f"in a worktree per branch, inside {c('.claude/worktrees/')}."),
            FIG(figures.fig_lifecycle(F),
                "A pitch ends as a task, a project, or archived. A task becomes a project when any of the 4 "
                "triggers fires: more than 3 scopes, more than one subsystem, a data model change, or a new "
                "external service. After the merge into dev, the item is marked [DONE] and its critical "
                "tests are promoted into TESTS.md."),
            H3("Definition of Ready: what a task or scope needs before the implementer"),
            CHIPS(["Goal", "Touches", "Tasks", "Acceptance Criteria", "OUT of scope / No-gos",
                   "no Open Questions"]),
            H3("Skills"),
            TABLE(["Skill", "Where it runs", "What it does"], skills_rows),
        ]),
        ("loop", "The Execution Loop", [
            P("How every task or scope is built, from its worktree. The main session writes no code: it invokes "
              "the agents in order and commits once at the end, with the code, the cached tests and the docs "
              "together."),
            FIG(figures.fig_loop(F),
                "Boxes with a dark border are agents, with the model and effort from their frontmatter. The red "
                "line at the bottom is the rework, with one counter shared by review and test. At the top, the "
                "path when the implementer lacks information: it never guesses."),
            TABLE(["Agent", "Model · effort", "When", "Tools", "What it does"], agent_rows),
        ]),
        ("hooks", "Hooks: the hard gates", [
            P(f"Hooks are scripts Claude Code runs by itself. {c('settings.json')} points each event at a "
              f"{c('dispatcher.sh')} that is a fixed stub; all the logic lives in {c('lib/dispatch.sh')}, so even "
              f"an old template-sync can update it without breaking anything. Gates catch mechanical mistakes "
              f"(wrong branch, secrets, missing docs); design judgment is left to the code-reviewer."),
            FIG(figures.fig_hooks(F),
                f"The PreToolUse matcher is {c(F['matcher'])}: other tools never reach the gates. Your own hooks "
                f"go in {c('.claude/hooks/<type>/project/')}, and template-sync never touches them."),
            TABLE(["Hook", "When", "Effect"], [
                [c("pre-tool/01-check-docs-before-push"), c("git push"),
                 f"Deny when the unpushed commits change source but not the hand-written docs in "
                 f"{c('docs/System/')} (the generated map does not count), unless they carry "
                 f"{c('Docs-Checked: no-changes — …')}."],
                [c("pre-tool/02-protected-branch"), f"commit, merge, cherry-pick or revert on {prot}, or a push to one",
                 "Ask: your approval is the promotion or hotfix authorization."],
                [c("pre-tool/03-no-secrets"), f"{c('git add')}, {c('git commit')}",
                 f"Deny when {c('.env')}, {c('.deploy-secrets')} or {c('docs/local/')} are not ignored, are tracked "
                 f"or staged; also when {c('.claude/worktrees/')} exists and is not ignored."],
                [c("pre-tool/04-task-before-code"), "Edit / Write on code",
                 f"Deny outside a {c('task-T-*')} / {c('scope-P-*')} branch whose task or project file exists. "
                 "It does not see files written through Bash."],
                [c("pre-tool/05-arch-check-before-push"), c("git push"),
                 f"Deny when {c('.claude/arch-check.sh')} exists and fails or is not executable."],
                [c("session-start/01-template-update-check"), "a new session, or /clear",
                 "Tells Claude the version in use and, when a newer one is out, its CHANGELOG notes. "
                 "Never changes anything."],
                [c(".githooks/pre-commit"), "every commit, also outside Claude",
                 "Refuses commits that stage secrets. The backstop for 03."],
            ]),
            H3("What gate 04 lets you edit without a task"),
            CHIPS(F["exempt"]),
        ]),
        ("branches", "Branches and worktrees", [
            ITEMS([
                (c("main"), "Production. Only receives merges from tst (with your approval) and hotfixes."),
                (c("tst"), "Staging. Receives dev when the project is complete, the regression tests pass and "
                           "docs-audit reports no differences."),
                (c("dev"), "Integration and planning. The primary checkout lives here. Never code directly."),
                (c("task-T-xxxx-<desc>"), "One per task, from dev (from main/tst for a hotfix)."),
                (c("scope-P-xxxx-N-<desc>"), "One per project scope, from dev."),
                (c(".claude/worktrees/<branch>"), "One worktree per code branch, gitignored. Removed after the merge."),
            ]),
            TABLE(["What changes", "Committed on", "By"], [
                ["Pitches, tasks, projects, glossary and their INDEX", c("dev") + ", as written", "planning skills"],
                ["Spec/task fixes after a BLOCKED", c("dev") + f", then {c('git merge dev')} into the branch", "main session"],
                ["Code + docs/System + map", "the task/scope branch", "main session (Execution Loop)"],
                ["Docs fixes with no code change (from docs-audit)", c("dev"), "main session"],
                ["Status [IN PROGRESS] / [DONE], INDEX, TESTS.md", c("dev") + ", right after the merge", "main session"],
            ]),
        ]),
        ("updates", "Template updates", [
            P(f"Each project keeps its template version on line 1 of {c('CLAUDE.md')}. When a session starts, the "
              f"hook compares it with the CHANGELOG on {c('main')} and, if the project is behind, shows you the "
              f"release notes. Only when you say yes does {c('template-sync')} run; it also repairs projects "
              f"half-upgraded by older versions."),
            FIG(figures.fig_sync(F),
                f"The manifest ({c('.claude/.template-manifest')}) defines what the template owns. "
                f"{c('seed')} entries ({', '.join(c(s) for s in F['seeds'])}) are copied only when missing: the "
                f"project adapts them. To turn the notice off: {c('CLAUDE_TEMPLATE_UPDATE_CHECK=0')}."),
        ]),
        ("upkeep", "How this map stays current", [
            P(f"Generated by {c('map/build.py')}, with the engine of the {c('system-map')} skill: never edit "
              f"{c('map/README.md')}, {c('map/index.html')} or {c('map/svg/')} by hand. {c('facts.py')} reads "
              f"the version, skills, agents (model, effort and tools from their frontmatter), hooks and Execution "
              f"Loop steps from {c('Template/')}. {c('python3 map/build.py --check')} fails when the committed "
              f"map is stale, when the template has something the figures do not draw, or when a hook stops doing "
              f"what the map says; the message names the file to edit."),
        ]),
    ]
