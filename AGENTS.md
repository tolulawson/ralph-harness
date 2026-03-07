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
6. the report at `last_report_path`
7. active spec artifacts under `specs/<spec-id>-<slug>/`
8. `specs/INDEX.md`
9. `tasks/todo.md`
10. a recent tail of `.ralph/logs/events.jsonl`

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

- make harness and scaffold changes in `src/` first
- treat root `.ralph/state/`, `.ralph/logs/`, `.ralph/reports/`, `tasks/`, and `specs/` as this repository's dogfood runtime records unless the task explicitly targets them
- do not change the root dogfood runtime just because `src/` changed; apply root changes only when explicitly requested

The root `AGENTS.md` and root `.ralph/constitution.md` describe this source repository itself. The copies shipped from `src/` are generic installed-harness documents and may differ from the root source-repo documents.

If this repository is installed into a project that already has its own `AGENTS.md`, keep that file and append a short Ralph harness section that points Codex to the files listed above.
