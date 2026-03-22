# Codex Loader For Ralph Harness Source Repo

This repository is the source repository for the Codex-native Ralph harness.

Its ground truth is fixed:

- `src/` contains the generic scaffold that gets installed into other projects
- repo root contains this repository's own dogfood runtime and development records
- `skills/` at repo root is the public entry surface for installing or invoking the harness

All paths below are relative to this repository root, which is the live dogfood runtime for this source repository.

## Read Order

Before doing substantial work, read these files in order:

1. `.ralph/constitution.md`
2. `.ralph/runtime-contract.md`
3. `.ralph/policy/project-policy.md`
4. `.ralph/state/workflow-state.json`
5. `.ralph/state/spec-queue.json`
6. `.ralph/state/orchestrator-lease.json`
7. a recent tail of `.ralph/state/orchestrator-intents.jsonl`
8. the report at `last_report_path`
9. active spec artifacts under `specs/<spec-id>-<slug>/`
10. `specs/INDEX.md`
11. `tasks/todo.md`
12. a recent tail of `.ralph/logs/events.jsonl`

When the task is about improving the shipped harness scaffold, also read:

11. `src/install-manifest.txt`
12. `src/generated-runtime-manifest.txt`
13. `src/upgrade-manifest.txt`

## Purpose Of This File

`AGENTS.md` is the Codex-facing loader. It is intentionally thin.

- The durable harness doctrine lives in `.ralph/constitution.md`.
- The generic dogfood runtime doctrine lives in `.ralph/runtime-contract.md`.
- Project-specific workflow rules live in `.ralph/policy/project-policy.md`.
- Runtime execution state lives in `.ralph/state/workflow-state.json`.
- The canonical spec queue lives in `.ralph/state/spec-queue.json`.

## Operating Rule

Do not treat conversational memory as the source of truth when the harness files already contain the needed state or policy.

- make all harness behavior, scaffold, contract, template, skill, config, and implementation changes in `src/`
- treat root `.ralph/`, root `.agents/skills/`, root `.codex/agents/`, root `.codex/`, `tasks/`, and `specs/` as this repository's dogfood/reference runtime, not as the primary implementation surface
- do not make direct implementation edits to the root dogfood runtime in normal harness work
- only touch root dogfood files when the task explicitly says to repair, inspect, or regenerate dogfood records themselves

The root `AGENTS.md` and root `.ralph/constitution.md` describe this source repository itself. The copies shipped from `src/` are generic installed-harness documents and may differ from the root source-repo documents.

If this repository is installed into a project that already has its own `AGENTS.md`, keep that file and append a short Ralph harness section that points Codex to the files listed above.

<!-- RALPH-HARNESS:START -->
# Codex Loader For Ralph Harness

This file is part of the generic Ralph harness scaffold that gets installed into a target repository.

All paths below are relative to the target repository root, which becomes the live harness runtime after installation.

## Read Order

Before doing substantial work, read these files in order:

1. `.ralph/constitution.md`
2. `.ralph/runtime-contract.md`
3. `.ralph/policy/project-policy.md`
4. `.ralph/context/project-truths.md`
5. `.ralph/context/project-facts.json`
6. `.ralph/context/learning-summary.md`
7. `.ralph/state/workflow-state.json`
8. `.ralph/state/spec-queue.json`
9. `.ralph/state/orchestrator-lease.json`
10. a recent tail of `.ralph/state/orchestrator-intents.jsonl`
11. the report at `last_report_path`
12. active spec artifacts under `specs/<spec-id>-<slug>/`
13. `specs/INDEX.md`
14. `tasks/todo.md`
15. a recent tail of `.ralph/logs/events.jsonl`

## Purpose Of This File

`AGENTS.md` is the Codex-facing loader. It is intentionally thin.

- The project-specific Ralph mission lives in `.ralph/constitution.md`.
- The generic installed-runtime doctrine lives in `.ralph/runtime-contract.md`.
- Project-specific workflow rules live in `.ralph/policy/project-policy.md`.
- Project truths and promoted learnings live under `.ralph/context/`.
- Runtime execution state lives in `.ralph/state/workflow-state.json`.
- The canonical spec queue lives in `.ralph/state/spec-queue.json`.
- Scheduler coordination lives in `.ralph/state/orchestrator-lease.json` and `.ralph/state/orchestrator-intents.jsonl`.

## Operating Rule

Do not treat conversational memory as the source of truth when the harness files already contain the needed state or policy.

The repository root is the harness work area after installation.

Treat `.ralph/context/project-truths.md`, `.ralph/context/project-facts.json`, and `.ralph/context/learning-summary.md` as part of the default harness context. Read only a recent tail of `.ralph/context/learning-log.jsonl` when diagnosing issues or promoting candidate learnings.

If this repository is installed into a project that already has its own `AGENTS.md`, keep that file and replace only the managed Ralph block between the markers shown here.
<!-- RALPH-HARNESS:END -->
