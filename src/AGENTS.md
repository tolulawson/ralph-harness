# Codex Loader For Ralph Harness

This repository is the reference source for a Codex-native Ralph harness and contains example artifacts that demonstrate the intended queue-driven workflow.

## Read Order

Before doing substantial work, read these files in order:

1. `.ralph/constitution.md`
2. `.ralph/policy/project-policy.md`
3. `.ralph/state/workflow-state.json`
4. `.ralph/state/spec-queue.json`
5. the report at `last_report_path`
6. active spec artifacts under `specs/<spec-id>-<slug>/`
7. `specs/INDEX.md`
8. `tasks/todo.md`
9. a recent tail of `.ralph/logs/events.jsonl`

## Purpose Of This File

`AGENTS.md` is the Codex-facing loader. It is intentionally thin.

- The durable harness doctrine lives in `.ralph/constitution.md`.
- Project-specific workflow rules live in `.ralph/policy/project-policy.md`.
- Runtime execution state lives in `.ralph/state/workflow-state.json`.
- The canonical spec queue lives in `.ralph/state/spec-queue.json`.

## Operating Rule

Do not treat conversational memory as the source of truth when the harness files already contain the needed state or policy.

If this repository is installed into a project that already has its own `AGENTS.md`, keep that file and append a short Ralph harness section that points Codex to the files listed above.
