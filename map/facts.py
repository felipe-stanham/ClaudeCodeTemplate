"""Facts of the template map, read from Template/.

collect(root) returns (F, problems). Same three patterns as the system-map kit:
  1. Sets drawn one by one (skills, agents, hooks, Execution Loop steps): KNOWN_* here, both directions.
  2. Values the text quotes (version, model · effort, rework limit, protected branches...): read into F.
  3. Hand-written claims (what each hook triggers on and does, what template-sync never touches...):
     a guard that fails when the template says otherwise.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

T = "Template"  # everything that ships to a project lives here


def tracked_files(root: Path, sub: str = "", suffix: str = "", recursive: bool = True) -> list[Path]:
    try:
        out = subprocess.run(["git", "-C", str(root), "ls-files", "-z", "--cached", "--others",
                              "--exclude-standard", "--", sub or "."],
                             capture_output=True, check=True).stdout
        paths = [root / n for n in out.decode("utf-8").split("\0") if n]
    except (OSError, subprocess.CalledProcessError):
        paths = [p for p in (root / sub).rglob("*") if ".git" not in p.parts]
    base = root / sub
    return sorted(p for p in paths if p.is_file() and p.name.endswith(suffix)
                  and (recursive or p.parent == base))


def code(path: Path, comment: str = "#") -> str:
    return "\n".join(ln for ln in path.read_text(encoding="utf-8", errors="replace").split("\n")
                     if not ln.strip().startswith(comment))


def read(root: Path, rel: str, problems: list[str]) -> str:
    p = root / rel
    if not p.is_file():
        problems.append(f"Missing {rel}: the map reads it (map/facts.py).")
        return ""
    return p.read_text(encoding="utf-8")


def section(md: str, heading: str) -> str:
    m = re.search(rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", md, re.M | re.S)
    return m.group(1) if m else ""


# ---------------------------------------------------------------------------- pattern 1: drawn sets

# Skills: name → (where it runs, what it does) — the text of the skills table.
KNOWN_SKILLS = {
    "pitch": ("planning · dev", "Idea → <code>docs/Pitches/I-xxxx.md</code> with a recommendation: Task, Project or archive."),
    "task": ("planning · dev", "<code>docs/Tasks/T-xxxx.md</code> that meets the Definition of Ready. If a promotion trigger fires, hands off to <code>spec</code>."),
    "spec": ("planning · dev", "<code>P-xxxx.md</code> + spec package (<code>spec.md</code>, <code>workflows.md</code>, <code>data_model.md</code>, <code>architecture.md</code>) with ready scopes."),
    "glossary": ("planning · dev", "Maintains <code>docs/System/glossary.md</code> (the Ubiquitous Language) and challenges terminology drift."),
    "arch-check": ("table on dev · script in a task", "Invariants in <code>docs/SYSTEM.md</code> + <code>.claude/arch-check.sh</code>, run by hook 05 and CI."),
    "system-map": ("in a task", "Generates the system map from the code and adds it as an invariant (<code>build.py --check</code>)."),
    "deployment-process": ("when deploying", "Deploys to a target in <code>docs/local/deployment.md</code> and logs it in <code>DEPLOYMENTS.md</code>. A seed: the project adapts it."),
    "template-sync": ("dev, clean tree", "Pulls the latest template and repairs incomplete upgrades."),
    "share": ("when publishing", "Static HTML mini-site from the project docs (<code>docs/shares/&lt;name&gt;</code>)."),
}
# Which lifecycle group draws each skill in fig_overview (planning skills vs the rest).
PLANNING_SKILLS = ("pitch", "task", "spec", "glossary")

# Agents: name → (when it runs, what it does) — the text of the agents table.
KNOWN_AGENTS = {
    "implementer": ("2 · Implement, and every rework", "Writes the code for one task or scope. Returns <code>BLOCKED: &lt;question&gt;</code> when the Definition of Ready is not met. Never commits."),
    "code-reviewer": ("3 · Review", "Reviews the diff: architecture, environments, simplicity, consistency, scope. <code>BLOCK</code> / <code>WARN</code> / <code>OK</code>."),
    "tester": ("4 · Test, and regression before dev → tst", "Generates and caches scripts in <code>tests/cache/</code> from the declarative criteria, and <b>runs</b> them."),
    "doc-updater": ("6 · Document", "Updates <code>docs/System/</code>, fixes what the change made false, regenerates the system map. Ends with <code>DOCS: …</code>."),
    "docs-audit": ("before dev → tst, or on demand", "Read-only: compares every checkable statement in the docs with the code."),
}

# Template hooks per type: "<type>/<file stem>" → (trigger regex in the code, effect regex in the code).
# The figure text for each is in figures.HOOK_TEXT; these guards keep that text true.
KNOWN_HOOKS = {
    "pre-tool/01-check-docs-before-push": (r"hook_runs_git push\b", r"^deny "),
    "pre-tool/02-protected-branch": (r"hook_runs_git commit merge cherry-pick revert push", r"^\s*ask "),
    "pre-tool/03-no-secrets": (r"hook_runs_git add commit", r"^deny "),
    "pre-tool/04-task-before-code": (r"Edit\|Write\|MultiEdit\|NotebookEdit\)", r"^\s*deny "),
    "pre-tool/05-arch-check-before-push": (r"hook_runs_git push\b", r"^\s*deny "),
    "session-start/01-template-update-check": (r"startup\|clear", r"^echo \"ClaudeCodeTemplate version in use"),
}
HOOK_TYPES = {"PreToolUse": "pre-tool", "PostToolUse": "post-tool", "Stop": "stop", "SessionStart": "session-start"}

# Execution Loop steps as CLAUDE.md names them; figures.STEP_POS places each (Rework is an arrow).
KNOWN_STEPS = ("Ready", "Implement", "Review", "Test", "Rework", "Document", "Commit", "Merge")

# What template-sync must never touch — the map states it in fig_sync.
NEVER_TOUCHED = ("docs/SYSTEM.md", "MEMORY.md", ".claude/arch-check.sh", ".claude/hooks/*/project/")


def _frontmatter(text: str) -> dict:
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    out = {}
    for ln in (m.group(1).split("\n") if m else []):
        if ":" in ln:
            k, v = ln.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def _diff(kind: str, found, known, const: str, where: str, problems: list[str]) -> None:
    for n in sorted(set(found) - set(known)):
        problems.append(f"New {kind} {n!r}: add it to {const} in map/facts.py and draw it in {where}.")
    for n in sorted(set(known) - set(found)):
        problems.append(f"{kind.capitalize()} {n!r} is gone from the template: remove it from {const} "
                        f"(map/facts.py) and from {where}.")


# ---------------------------------------------------------------------------- collect


def collect(root: Path) -> tuple[dict, list[str]]:
    problems: list[str] = []
    claude = read(root, f"{T}/CLAUDE.md", problems)

    # -- version (pattern 2)
    m = re.match(r"<!-- TEMPLATE VERSION: (\d+\.\d+\.\d+) -->", claude)
    version = m.group(1) if m else "?"
    if not m:
        problems.append("Line 1 of Template/CLAUDE.md has no TEMPLATE VERSION: the map quotes it.")

    # -- skills (pattern 1)
    skills = sorted({p.parent.name for p in tracked_files(root, f"{T}/.claude/skills", "SKILL.md")})
    _diff("skill", skills, KNOWN_SKILLS, "KNOWN_SKILLS", "sections.py (skills table)", problems)

    # -- agents (pattern 1) + model · effort · tools (pattern 2)
    agents = {}
    for p in tracked_files(root, f"{T}/.claude/agents", ".md", recursive=False):
        if p.name == "README.md":
            continue
        fm = _frontmatter(p.read_text(encoding="utf-8"))
        agents[fm.get("name", p.stem)] = {k: fm.get(k, "?") for k in ("model", "effort", "tools")}
    _diff("agent", agents, KNOWN_AGENTS, "KNOWN_AGENTS", "map/figures.py: fig_loop", problems)

    # Guard (pattern 3): CLAUDE.md's "(model · effort)" for each agent matches its frontmatter.
    loop = section(claude, "Execution Loop")
    for name, a in agents.items():
        mm = re.search(rf"`{re.escape(name)}` \((\w+) · (\w+)\)", loop)
        if mm and (mm.group(1), mm.group(2)) != (a["model"], a["effort"]):
            problems.append(f"CLAUDE.md says {name} runs {mm.group(1)} · {mm.group(2)}, its frontmatter "
                            f"says {a['model']} · {a['effort']}: fix the template (not the map).")

    # -- Execution Loop steps (pattern 1) and rework limit (pattern 2)
    steps = re.findall(r"^(\d+)\. \*\*(\w+):\*\*", loop, re.M)
    _diff("Execution Loop step", [s for _, s in steps], KNOWN_STEPS, "KNOWN_STEPS", "map/figures.py: STEP_POS", problems)
    mm = re.search(r"At most (\d+) rework cycles", loop)
    max_rework = int(mm.group(1)) if mm else 0
    if not mm:
        problems.append("CLAUDE.md no longer says 'At most N rework cycles': update fig_loop's rework label.")
    rework_model = re.search(r"re-invoke `implementer` with `model: (\w+)`", loop)
    rework_model = rework_model.group(1) if rework_model else "?"

    # -- hooks (pattern 1) + guards on what each does (pattern 3)
    hooks = {}
    for p in tracked_files(root, f"{T}/.claude/hooks", ".sh"):
        parts = p.relative_to(root / f"{T}/.claude/hooks").parts
        if len(parts) == 3 and parts[1] == "template" and p.name != "00-dispatch-shim.sh":
            hooks[f"{parts[0]}/{p.stem}"] = p
    _diff("template hook", hooks, KNOWN_HOOKS, "KNOWN_HOOKS", "map/figures.py: HOOK_TEXT", problems)
    for key, (trigger, effect) in KNOWN_HOOKS.items():
        if key in hooks:
            src = code(hooks[key])
            if not re.search(trigger, src):
                problems.append(f"{key}.sh no longer matches its trigger /{trigger}/: the map's text for it "
                                f"(figures.HOOK_TEXT) is wrong now. Re-read the hook and update both.")
            if not re.search(effect, src, re.M):
                problems.append(f"{key}.sh no longer has its effect /{effect}/: update figures.HOOK_TEXT.")

    # settings.json events → hook types; pre-tool matcher
    settings = read(root, f"{T}/.claude/settings.json", problems)
    try:
        sj = json.loads(settings or "{}")
    except json.JSONDecodeError:
        sj, _ = {}, problems.append("Template/.claude/settings.json is not valid JSON.")
    events = sorted(sj.get("hooks", {}))
    _diff("hook event", events, HOOK_TYPES, "HOOK_TYPES", "map/figures.py: fig_overview (Hooks box)", problems)
    matcher = ((sj.get("hooks", {}).get("PreToolUse") or [{}])[0]).get("matcher", "")

    # Guard: the dispatcher contract the map explains (exit codes 0 / 2 / 3).
    dispatch = read(root, f"{T}/.claude/hooks/pre-tool/template/lib/dispatch.sh", problems)
    for code_, word in (("0", "allow"), ("2", "deny"), ("3", "ask the user")):
        if not re.search(rf"^#\s+{code_}\s+{word}", dispatch, re.M):
            problems.append(f"lib/dispatch.sh no longer documents exit {code_} = {word}: update fig_hooks.")
    if not re.search(r'"\$TYPE_DIR/template/"\*\.sh "\$TYPE_DIR/project/"\*\.sh', dispatch):
        problems.append("lib/dispatch.sh no longer runs template/*.sh then project/*.sh: update fig_hooks.")

    # Protected branches (pattern 2), from 02.
    mm = re.search(r"PROTECTED='\^\(([^)]+)\)\$'", code(hooks["pre-tool/02-protected-branch"])) \
        if "pre-tool/02-protected-branch" in hooks else None
    protected = mm.group(1).split("|") if mm else []

    # Paths 04 lets through without a task (pattern 2).
    mm = re.search(r'case "\$REL" in\n\s*(.+?)\) exit 0', code(hooks["pre-tool/04-task-before-code"])
                   if "pre-tool/04-task-before-code" in hooks else "", re.S)
    exempt = mm.group(1).split("|") if mm else []

    # Update check cadence and timeout (pattern 2).
    usrc = code(hooks["session-start/01-template-update-check"]) if "session-start/01-template-update-check" in hooks else ""
    mm = re.search(r"-mmin -(\d+)", usrc)
    every_h = int(mm.group(1)) // 60 if mm else 0
    mm = re.search(r"--max-time (\d+)", usrc)
    timeout_s = int(mm.group(1)) if mm else 0

    # git pre-commit guard (pattern 3): it refuses staged secrets.
    pc = read(root, f"{T}/.githooks/pre-commit", problems)
    if "git diff --cached" not in pc or "exit 1" not in pc:
        problems.append(".githooks/pre-commit no longer refuses staged secrets: update the hooks section.")

    # template-sync never touches these (pattern 3).
    sync = read(root, f"{T}/.claude/skills/template-sync/SKILL.md", problems)
    mm = re.search(r"\*\*Never touched:\*\*(.*?)\n\n", sync, re.S)
    never = mm.group(1) if mm else ""
    for path in NEVER_TOUCHED:
        if f"`{path}`" not in never:
            problems.append(f"template-sync's 'Never touched' list no longer has {path}: update fig_sync.")

    # Manifest (pattern 2): how many files sync owns, how many are seeds.
    man = [ln for ln in read(root, f"{T}/.claude/.template-manifest", problems).splitlines()
           if ln.strip() and not ln.startswith("#")]
    seeds = [ln.split(" ", 1)[1] for ln in man if ln.startswith("seed ")]

    # Docs templates (pattern 2): listed, not drawn.
    doc_templates = [p.name for p in tracked_files(root, f"{T}/docs/templates")]

    # Promotion triggers: the map says there are four (pattern 3).
    wa = section(claude, "Work Artifacts")
    trig = re.search(r"### Promotion: Task → Project\n(.*?)\n### ", wa, re.S)
    n_triggers = len(re.findall(r"^- ", trig.group(1), re.M)) if trig else 0
    if n_triggers != 4:
        problems.append(f"CLAUDE.md lists {n_triggers} Task → Project triggers; the map says four (sections.py, fig_lifecycle).")

    F = {
        "version": version,
        "skills": [(s, *KNOWN_SKILLS[s]) for s in skills if s in KNOWN_SKILLS],
        "planning_skills": [s for s in PLANNING_SKILLS if s in skills],
        "agents": {n: {**a, "when": KNOWN_AGENTS[n][0], "what": KNOWN_AGENTS[n][1]}
                   for n, a in sorted(agents.items()) if n in KNOWN_AGENTS},
        "steps": [(int(n), s) for n, s in steps],
        "max_rework": max_rework,
        "rework_model": rework_model,
        "hooks": sorted(hooks),
        "hook_types": [HOOK_TYPES[e] for e in events if e in HOOK_TYPES],
        "events": events,
        "matcher": matcher,
        "protected": protected,
        "exempt": exempt,
        "update_every_h": every_h,
        "update_timeout_s": timeout_s,
        "manifest_n": len(man),
        "seeds": seeds,
        "doc_templates": doc_templates,
        "never_touched": list(NEVER_TOUCHED),
    }
    return F, problems
