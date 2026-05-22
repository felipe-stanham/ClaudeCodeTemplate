The expected `SYSTEM.md` format is:

```
# System: [System Name]

## What This System Does
[2–4 sentences describing the system's purpose and main components]

## Architecture Principles
- [Key decision that must be respected, e.g., "API-first: all features exposed via REST before UI"]
- [Another constraint, e.g., "Single Postgres database — no secondary datastores"]

## Cross-Project Constraints
- [Constraint that applies to every project, e.g., "All auth uses JWT via auth-service"]

## Subsystems / Components
- [Named subsystem 1] — [one-line description]
- [Named subsystem 2] — [one-line description]
<!-- This list is what the "touches multiple subsystems" promotion trigger checks against. Keep names stable. -->

## Work Artifact Indexes
- Pitches: [docs/Pitches/INDEX.md](Pitches/INDEX.md)
- Tasks: [docs/Tasks/INDEX.md](Tasks/INDEX.md)
- Projects: [docs/Projects/INDEX.md](Projects/INDEX.md)

## Deployment
- Targets and procedures: see `docs/local/deployment.md` (gitignored — not in this repo).
- Secrets: see `.deploy-secrets` (gitignored — not in this repo).
- Do NOT inline target details, hostnames, or credentials in this file.
```

---

## Rules

- Keep `SYSTEM.md` under ~150 lines.
- Do NOT list individual projects, tasks, or pitches here. Those live in their respective `INDEX.md` files.
- Do NOT inline deployment targets here. SYSTEM.md is public-repo safe; deployment targets are not.
- Update the Subsystems / Components section only when a new top-level component is introduced or removed.
