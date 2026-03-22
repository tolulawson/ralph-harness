<!-- RALPH-HARNESS:START -->
# Codex Loader For Ralph Harness

This file is part of the generic Ralph harness scaffold that gets installed into a target repository.

All paths below are relative to the target repository root, which becomes the live harness runtime after installation.

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
11. a recent tail of `.ralph/state/orchestrator-intents.jsonl`
12. the report at `last_report_path`
13. active or admitted spec artifacts under `specs/<spec-id>-<slug>/`
14. `specs/INDEX.md`
15. `tasks/todo.md`
16. a recent tail of `.ralph/logs/events.jsonl`

## Purpose Of This File

`AGENTS.md` is the Codex-facing loader. It is intentionally thin.

- The project-specific Ralph mission lives in `.ralph/constitution.md`.
- The generic installed-runtime doctrine lives in `.ralph/runtime-contract.md`.
- Project-specific runtime extensions live in `.ralph/policy/runtime-overrides.md`.
- Project-specific workflow rules live in `.ralph/policy/project-policy.md`.
- Project truths and promoted learnings live under `.ralph/context/`.
- Runtime execution state lives in `.ralph/state/workflow-state.json`.
- The canonical spec queue lives in `.ralph/state/spec-queue.json`.
- Scheduler coordination lives in `.ralph/state/orchestrator-lease.json` and `.ralph/state/orchestrator-intents.jsonl`.

## Operating Rule

Do not treat conversational memory as the source of truth when the harness files already contain the needed state or policy.

The repository root is the harness work area after installation.

Treat `.ralph/policy/runtime-overrides.md`, `.ralph/context/project-truths.md`, `.ralph/context/project-facts.json`, and `.ralph/context/learning-summary.md` as part of the default harness context. Read only a recent tail of `.ralph/context/learning-log.jsonl` when diagnosing issues or promoting candidate learnings.

If this repository is installed into a project that already has its own `AGENTS.md`, keep that file and replace only the managed Ralph block between the markers shown here.
<!-- RALPH-HARNESS:END -->
