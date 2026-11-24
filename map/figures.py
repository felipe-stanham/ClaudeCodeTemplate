"""Figures of the template map (map/build.py). Hand layout; names, counts and values come from F.

coverage(F) reports what F has that a drawing has no place for, naming the constant to edit.
"""
from __future__ import annotations

from svgkit import Fig, width

# fig_loop: column of each Execution Loop step (Rework is drawn as the red loop, not a box).
STEP_POS = {"Ready": 0, "Implement": 1, "Review": 2, "Test": 3, "Document": 4, "Commit": 5, "Merge": 6}
STEP_AGENT = {"Implement": "implementer", "Review": "code-reviewer", "Test": "tester", "Document": "doc-updater"}

# fig_hooks: what each template hook is drawn as — (trigger, effect). facts.KNOWN_HOOKS guards both.
HOOK_TEXT = {
    "pre-tool/01-check-docs-before-push": ("git push", "deny: code changed, docs/System did not"),
    "pre-tool/02-protected-branch": ("commit · merge · push on {protected}", "ask: your approval = the promotion"),
    "pre-tool/03-no-secrets": ("git add · git commit", "deny: .env, .deploy-secrets, docs/local/"),
    "pre-tool/04-task-before-code": ("Edit / Write on code", "deny: outside task-T-* / scope-P-*"),
    "pre-tool/05-arch-check-before-push": ("git push", "deny: .claude/arch-check.sh fails"),
    "session-start/01-template-update-check": ("a new session starts", "version + update notice"),
}


def coverage(F: dict) -> list[str]:
    problems = []
    for _, s in F["steps"]:
        if s != "Rework" and s not in STEP_POS:
            problems.append(f"Execution Loop step {s!r} has no column: add it to STEP_POS in figures.py.")
    if "Rework" not in [s for _, s in F["steps"]]:
        problems.append("CLAUDE.md has no Rework step any more: remove the red loop from fig_loop.")
    for h in F["hooks"]:
        if h not in HOOK_TEXT:
            problems.append(f"Hook {h} has no text: add it to HOOK_TEXT in figures.py.")
    for a in STEP_AGENT.values():
        if a not in F["agents"]:
            problems.append(f"fig_loop draws agent {a}, which is gone: edit STEP_AGENT in figures.py.")
    return problems


def wrap(names, max_w, size=11.5, sep=" · "):
    """Greedy: join names into monospace lines no wider than max_w."""
    lines, cur = [], ""
    for n in names:
        cand = cur + sep + n if cur else n
        if cur and width(cand, size, True) > max_w:
            lines.append("`" + cur)
            cur = n
        else:
            cur = cand
    return lines + (["`" + cur] if cur else [])


def me(F, agent):
    a = F["agents"].get(agent, {})
    return f"{a.get('model', '?')} · {a.get('effort', '?')}"


# ---------------------------------------------------------------------------- 01 overview


def fig_overview(F: dict) -> Fig:
    f = Fig("01-overview", 1300, 560, "Overview: what the template installs in a project, and how the rules, "
            "the main session, the skills, the agents and the hooks connect.")
    f.box(640, 14, 290, 58, "You", ["ask, approve, unblock"], "ext")
    f.box(16, 300, 224, 84, "ClaudeCodeTemplate", ["`Template/ on main", "CHANGELOG · MIGRATIONS"], "ext")
    f.frame(264, 100, 1020, 444, "Your project")

    f.box(296, 140, 270, 72, "`CLAUDE.md", [f"the rules · v{F['version']}", "replaced by template-sync"], "store")
    f.box(296, 240, 270, 104, "Project docs",
          ["`docs/SYSTEM.md", "`docs/System/glossary.md", "`MEMORY.md", "yours: sync never touches them"], "store")
    f.box(296, 372, 270, 112, "Work items (on dev)",
          ["`docs/Pitches/I-xxxx.md", "`docs/Tasks/T-xxxx.md", "`docs/Projects/P-xxxx.md", "`TESTS.md"], "store")

    f.box(640, 140, 290, 72, "Main session", ["plans and orchestrates;", "writes no production code"], "proc")
    sk = [s for s, *_ in F["skills"]]
    plan = F["planning_skills"]
    f.box(640, 244, 290, 112, f"Skills ({len(sk)})",
          wrap(plan, 270) + wrap([s for s in sk if s not in plan], 270), "proc")
    ag = list(F["agents"])
    f.box(640, 388, 290, 104, f"Agents ({len(ag)})", wrap(ag, 270) + ["run the Execution Loop"], "proc")

    n_pre = len([h for h in F["hooks"] if h.startswith("pre-tool/")])
    f.box(1000, 140, 260, 120, "Claude Code hooks",
          ["`settings.json → dispatcher.sh", f"pre-tool: {n_pre} hard gates", "session-start: version + updates",
           "post-tool · stop: project/ only"], "proc")
    f.box(1000, 292, 260, 64, "`.githooks/pre-commit", ["stops secrets outside Claude"], "proc")
    f.box(1000, 388, 260, 88, "`.claude/arch-check.sh", ["invariants (optional, yours)", "run by hook 05 and in CI"], "off")

    f.arrow([(785, 72), (785, 140)], "call", "requests / approvals", at=(795, 118), anchor="start", both=True)
    f.arrow([(128, 300), (128, 176), (296, 176)], "main", "template-sync", at=(196, 168))
    f.arrow([(566, 176), (640, 176)], "main", "loads", at=(603, 168))
    f.arrow([(566, 272), (600, 272), (600, 198), (640, 198)], "call")
    f.arrow([(785, 212), (785, 244)], "call", "invokes", at=(795, 233), anchor="start")
    f.arrow([(640, 330), (612, 330), (612, 428), (566, 428)], "main", "write", at=(590, 420))
    f.arrow([(930, 196), (962, 196), (962, 440), (930, 440)], "call")
    f.arrow([(1000, 166), (930, 166)], "fail", "deny / ask", at=(965, 158))
    return f


# ---------------------------------------------------------------------------- 02 lifecycle


def fig_lifecycle(F: dict) -> Fig:
    f = Fig("02-lifecycle", 1300, 350, "Lifecycle of work: from an idea to a pitch, task or project, to the "
            "Execution Loop in a worktree, and from dev to tst and main.")
    f.frame(150, 40, 500, 290, "Planning · primary checkout on dev")
    f.frame(680, 40, 300, 290, "Code · one worktree per branch", "host")
    f.frame(1010, 40, 274, 290, "Promotion")

    f.box(16, 140, 110, 56, "Idea", ["or a change"], "ext")
    f.box(180, 124, 180, 88, "Pitch", ["`docs/Pitches/I-xxxx.md", "skill pitch"], "store")
    f.box(180, 250, 180, 56, "Archived", ["[ARCHIVED] in INDEX"], "off")
    f.box(440, 84, 190, 88, "Task", ["`docs/Tasks/T-xxxx.md", "skill task"], "store")
    f.box(440, 216, 190, 104, "Project", ["`docs/Projects/P-xxxx.md", "+ spec package", "skill spec"], "store")
    f.box(700, 110, 260, 150, "Execution Loop",
          ["`.claude/worktrees/<branch>", "`task-T-xxxx-<desc>", "`scope-P-xxxx-N-<desc>",
           "implementer → reviewer →", "tester → doc-updater"], "proc")
    f.box(1030, 84, 234, 60, "dev", ["integration + planning"], "store")
    f.box(1030, 174, 234, 60, "tst", ["regression + docs-audit"], "store")
    f.box(1030, 264, 234, 56, "main", ["production (prd)"], "store")

    f.arrow([(126, 168), (180, 168)], "main")
    f.arrow([(71, 140), (71, 24), (535, 24), (535, 84)], "call", "small change or hotfix: straight to a task", at=(300, 18))
    f.arrow([(360, 150), (400, 150), (400, 118), (440, 118)], "main")
    f.arrow([(360, 190), (400, 190), (400, 268), (440, 268)], "main")
    f.arrow([(270, 212), (270, 250)], "off")
    f.arrow([(535, 172), (535, 216)], "call", "4 triggers", at=(545, 198), anchor="start")
    f.arrow([(630, 128), (700, 128)], "main", "Ready", at=(665, 120))
    f.arrow([(630, 268), (665, 268), (665, 230), (700, 230)], "main", "per scope", at=(668, 284))
    f.arrow([(960, 140), (995, 140), (995, 114), (1030, 114)], "main", "merge", at=(995, 106))
    f.arrow([(1147, 144), (1147, 174)], "main", "project complete", at=(1157, 163), anchor="start")
    f.arrow([(1147, 234), (1147, 264)], "main", "your approval", at=(1157, 253), anchor="start")
    return f


# ---------------------------------------------------------------------------- 03 execution loop


def fig_loop(F: dict) -> Fig:
    f = Fig("03-execution-loop", 1300, 400, "Execution Loop: the steps of every task or scope, the agent that runs "
            "each one, the rework when review or test fails, and the BLOCKED path.")
    num = {s: n for n, s in F["steps"]}
    text = {
        "Ready": ["main session", "Definition of Ready", "`[IN PROGRESS] on dev"],
        "Commit": ["main session", "code + tests + docs", "push: gates 01 and 05"],
        "Merge": ["merge into dev", "`[DONE] + TESTS.md", "remove the worktree"],
    }
    extra = {"Implement": "writes, never commits", "Review": "BLOCK / WARN / OK",
             "Test": "runs the criteria", "Document": "docs/System + map"}
    for s, i in STEP_POS.items():
        if s not in num:
            continue
        lines = text.get(s) or ["`" + STEP_AGENT[s], me(F, STEP_AGENT[s]), extra[s]]
        kind = "proc" if s in STEP_AGENT else "store"
        f.box(24 + i * 182, 210, 160, 100, f"{num[s]} · {s}", lines, kind)
        if i:
            f.arrow([(24 + i * 182 - 22, 250), (24 + i * 182, 250)], "main")

    x = {s: 24 + i * 182 + 80 for s, i in STEP_POS.items()}
    f.raw(f'<polyline points="{x["Review"]},310 {x["Review"]},350" class="e-fail" fill="none"/>')
    f.arrow([(x["Test"], 310), (x["Test"], 350), (x["Implement"], 350), (x["Implement"], 310)], "fail")
    f.text(x["Review"], 374, f"{num.get('Rework', '?')} · Rework: BLOCK or FAIL → implementer on {F['rework_model']} "
           f"+ the findings · at most {F['max_rework']} cycles, then you decide", cls="lbl lk-fail", anchor="middle", size=11.5)

    f.box(206, 40, 250, 72, "You", ["answer the BLOCKED", f"decide after {F['max_rework']} reworks"], "ext")
    f.box(560, 40, 260, 72, "Task or spec on dev", ["fixed and pushed", "`git merge dev in the branch"], "store")
    f.arrow([(250, 210), (250, 112)], "fail", "BLOCKED: question", at=(240, 170), anchor="end")
    f.arrow([(456, 76), (560, 76)], "call")
    f.arrow([(690, 112), (690, 160), (320, 160), (320, 210)], "call", "re-invokes", at=(505, 152))
    return f


# ---------------------------------------------------------------------------- 04 hooks


def fig_hooks(F: dict) -> Fig:
    f = Fig("04-hooks", 1300, 520, "Hooks: how a tool call goes through settings.json, the dispatcher and the "
            "runner, which runs every gate and combines their exit codes into allow, ask or deny.")
    f.box(24, 200, 190, 84, "Claude Code", ["about to use a tool", "`Bash · Edit · Write…"], "ext")
    f.box(250, 200, 200, 84, "`settings.json", [f"{len(F['events'])} events → dispatchers", "pre-tool: Bash and edits"], "store")
    f.box(486, 200, 190, 84, "`dispatcher.sh", ["one stub per type", "never changes"], "proc")
    f.box(712, 180, 220, 124, "`lib/dispatch.sh",
          ["runs template/*.sh,", "then project/*.sh", "each one reads HOOK_*", "wins: deny › ask › allow"], "proc")
    for x1, x2 in ((214, 250), (450, 486), (676, 712)):
        f.arrow([(x1, 242), (x2, 242)], "main")

    pre = [h for h in F["hooks"] if h.startswith("pre-tool/")]
    rows = [(h.split("/", 1)[1], *HOOK_TEXT.get(h, ("?", "?")), "proc") for h in pre]
    rows.append(("project/*.sh", "your hooks, same contract", "exit 0 · 2 · 3", "off"))
    ys = [40 + i * 76 for i in range(len(rows))]
    f.raw(f'<polyline points="932,242 952,242" class="e-call" fill="none"/>')
    f.raw(f'<polyline points="952,{ys[0] + 31} 952,{ys[-1] + 31}" class="e-call" fill="none"/>')
    for (name, trig, eff, kind), y in zip(rows, ys):
        trig = trig.format(protected="/".join(F["protected"]))
        f.box(976, y, 300, 62, "`" + name, [trig, eff], kind, size=11.5)
        f.arrow([(952, y + 31), (976, y + 31)], "call")

    f.raw('<polyline points="822,304 822,356" class="e-call" fill="none"/>')
    f.raw('<polyline points="350,356 822,356" class="e-call" fill="none"/>')
    f.box(250, 380, 200, 60, "exit 0 · allow", ["the tool runs"], "ok")
    f.box(486, 380, 190, 60, "exit 3 · ask", ["asks you"], "warn")
    f.box(712, 380, 220, 60, "exit 2 · deny", ["the reason goes to Claude"], "bad")
    for cx in (350, 581, 822):
        f.arrow([(cx, 356), (cx, 380)], "call")
    f.text(24, 480, "All 0 → allow. Any 3 and no 2 → ask. Any 2 → deny. Any other code → a visible hook error that does not block.",
           cls="sub", size=12)
    return f


# ---------------------------------------------------------------------------- 05 sync


def fig_sync(F: dict) -> Fig:
    f = Fig("05-updates", 1300, 360, "Updates: the session-start hook announces a newer version; template-sync, "
            "only after your yes, replaces the template's files and never yours.")
    f.box(24, 130, 230, 84, "ClaudeCodeTemplate", ["`main · Template/", "`CHANGELOG.md"], "ext")
    f.box(340, 30, 270, 84, "Hook session-start",
          ["`01-template-update-check", f"every {F['update_every_h']} h at most · {F['update_timeout_s']} s cap"], "proc")
    f.box(680, 30, 260, 84, "Session context", [f"version in use (v{F['version']})", "+ release notes if behind"], "store")
    f.box(1010, 30, 266, 84, "You", ["decide whether to sync", "it never syncs by itself"], "ext")
    f.box(340, 196, 270, 120, "template-sync skill",
          ["on dev, clean tree", "copies the manifest files", "merges its settings hooks", "repairs old upgrades"], "proc")
    f.box(680, 196, 260, 120, "Replaced (template-owned)",
          ["`CLAUDE.md", f"{F['manifest_n']} files in the manifest", "`hooks/*/template/", "settings: only its hooks"], "store")
    f.box(1010, 196, 266, 120, "Never touched (yours)",
          ["`" + p for p in F["never_touched"]] + ["your own skills/agents"], "store")

    f.arrow([(254, 150), (296, 150), (296, 72), (340, 72)], "off", "reads", at=(306, 112), anchor="start")
    f.arrow([(610, 72), (680, 72)], "main")
    f.arrow([(940, 72), (1010, 72)], "main")
    f.arrow([(1143, 114), (1143, 156), (475, 156), (475, 196)], "call", "“yes” → template-sync", at=(809, 148))
    f.arrow([(254, 190), (296, 190), (296, 256), (340, 256)], "main", "clones", at=(306, 230), anchor="start")
    f.arrow([(610, 256), (680, 256)], "main", "copies", at=(645, 248))
    f.arrow([(475, 316), (475, 340), (1143, 340), (1143, 316)], "off", "never touches", at=(809, 334))
    return f
