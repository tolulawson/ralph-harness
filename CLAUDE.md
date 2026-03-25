# Ralph Harness Loader Source Repo

This repository is the source repository for the Ralph multi-agent runtime.

Before doing substantial work, read these files in order:

1. `.ralph/constitution.md`
2. `.ralph/runtime-contract.md`
3. `.ralph/policy/runtime-overrides.md`
4. `.ralph/policy/project-policy.md`
5. `.ralph/state/workflow-state.json`
6. `.ralph/state/spec-queue.json`
7. `.ralph/state/orchestrator-lease.json`
8. a recent tail of `.ralph/state/orchestrator-intents.jsonl`
9. the report at `last_report_path`
10. active spec artifacts under `specs/<spec-id>-<slug>/`
11. `specs/INDEX.md`
12. `tasks/todo.md`
13. a recent tail of `.ralph/logs/events.jsonl`

When the task is about improving the shipped harness scaffold, also read:

1. `src/install-manifest.txt`
2. `src/generated-runtime-manifest.txt`
3. `src/upgrade-manifest.txt`

The live source-repo implementation still belongs in `src/`. Treat root `.ralph/`, root `.agents/skills/`, root `.codex/`, `tasks/`, and `specs/` as this repository's dogfood runtime unless a task explicitly targets dogfood repair.
