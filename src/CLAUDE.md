<!-- RALPH-HARNESS:START -->
# Ralph Harness Loader

This file is part of the generic Ralph harness scaffold that gets installed into a target repository.

All paths below are relative to the target repository root, which becomes the live Ralph runtime after installation.

## Read Order

Before doing substantial work, read these files in order:

1. `.ralph/constitution.md`
2. `.ralph/runtime-contract.md`
3. `.ralph/policy/runtime-overrides.md`
4. `.ralph/policy/project-policy.md`
5. `.ralph/context/project-truths.md`
6. `.ralph/context/project-facts.json`
7. `.ralph/context/learning-summary.md`
8. `.ralph/state/workflow-state.json`
9. `.ralph/state/spec-queue.json`
10. `.ralph/state/orchestrator-lease.json`
11. `.ralph/state/worker-claims.json`
12. `recent tail of .ralph/state/orchestrator-intents.jsonl`
13. `report at last_report_path`
14. `active or admitted spec artifacts under specs/<spec-id>-<slug>/`
15. `specs/INDEX.md`
16. `tasks/todo.md`
17. `recent tail of .ralph/logs/events.jsonl`

## Purpose Of This File

This loader is intentionally thin. It points the active coding agent at the canonical Ralph runtime doctrine under `.ralph/`.

- The project-specific Ralph mission lives in `.ralph/constitution.md`.
- The generic installed-runtime doctrine lives in `.ralph/runtime-contract.md`.
- Project-specific runtime extensions live in `.ralph/policy/runtime-overrides.md`.
- Project-specific workflow rules live in `.ralph/policy/project-policy.md`.
- Project truths and promoted learnings live under `.ralph/context/`.
- Runtime execution state lives in `.ralph/state/`.

## Operating Rule

Do not treat conversational memory as the source of truth when the Ralph runtime files already contain the needed state or policy.

Treat the repository root as the harness work area after installation. Keep agent-specific instructions thin and route all substantive behavior back to the shared Ralph runtime contract.

If this repository already has its own loader file, preserve non-Ralph content and replace only the managed Ralph block between the markers shown here.
<!-- RALPH-HARNESS:END -->
