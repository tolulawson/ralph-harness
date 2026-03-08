# Ralph Harness Constitution

## Mission

This repository is the source repository and reference implementation for a Codex-native Ralph harness that runs a durable queue-driven workflow.

The harness doctrine is split deliberately:

- root `.ralph/constitution.md` is the source-repo truth for this repository
- root `.ralph/runtime-contract.md` is the dogfood runtime doctrine for this repository's own harness loop
- `src/.ralph/constitution.md` and `src/.ralph/runtime-contract.md` are the installed target-repo scaffold copies

This repository's structure is fixed:

- `src/` is the generic scaffold shipped to other projects
- repo root `.ralph/state/`, `.ralph/logs/`, `.ralph/reports/`, `tasks/`, and `specs/` are this repository's dogfood runtime and development records
- root `skills/` is the public source-skill entry surface

## Constitutional Priority

Interpret the source repository in this order:

1. this constitution
2. `.ralph/runtime-contract.md`
3. `.ralph/policy/project-policy.md`
4. `.ralph/state/workflow-state.json`
5. `.ralph/state/spec-queue.json`
6. active spec artifacts and latest role reports

`AGENTS.md` is only the Codex entrypoint that tells Codex where to read the real operating doctrine.

In this source repository, scaffold behavior is edited in `src/` first. The repository root is the workshop and dogfood runtime for building and validating that scaffold.

The source-of-truth implementation rule is strict:

- all harness behavior, templates, configs, role skills, public skills, and install or upgrade contracts must be changed in `src/`
- root dogfood files are reference runtime artifacts for this repository and are not the primary implementation surface
- do not make direct implementation edits to root dogfood runtime files during normal harness work
- only update root dogfood files when the task explicitly targets dogfood repair, inspection, or regeneration

External named entry points exist via distributable source skills at repository root:

- `ralph-install`
- `ralph-interrupt`
- `ralph-upgrade`
- `ralph-prd`
- `ralph-plan`
- `ralph-execute`

Those source skills are distinct from the runtime role skills under `.agents/skills/`.

## Source Scaffold Contract

- `src/` is the clean installable scaffold output.
- `INSTALLATION.md` is the canonical install source of truth for this source repository.
- `UPGRADING.md` is the canonical upgrade source of truth for this source repository.
- `VERSION` is the canonical semver source for the released scaffold surface.
- `src/install-manifest.txt`, `src/generated-runtime-manifest.txt`, and `src/upgrade-manifest.txt` are subordinate install and upgrade subcontracts referenced by the guides.
- `skills/ralph-install/SKILL.md` and `skills/ralph-upgrade/SKILL.md` are execution adapters and must not define behavior beyond what the canonical guides already specify.
- procedural source-repo work tracking does not belong in `src/`.
- target runtime records such as `tasks/todo.md`, `tasks/lessons.md`, `.ralph/logs/events.jsonl`, and `.ralph/reports/` are generated during installation or first run.
- any change to `src/` that affects installation behavior, upgrade behavior, copied paths, generated runtime files, managed loader content, version metadata, or required setup steps must update the relevant canonical guide in the same change.
- changes to `src/` do not imply root dogfood-runtime changes.
- dogfood runtime updates require an explicit task to repair, inspect, or regenerate root runtime records.

## State Rules

- `.ralph/state/workflow-state.json` is the canonical machine-readable runtime state for the source repo dogfood loop.
- `.ralph/state/spec-queue.json` is the canonical machine-readable spec queue and spec-state registry.
- `.ralph/state/workflow-state.md` is a human-readable companion file and must agree with the JSON state.
- `specs/<spec-id>-<slug>/task-state.json` is the canonical machine-readable task lifecycle registry for a dogfood spec when it exists.
- `specs/INDEX.md` is a human-readable projection of the spec queue.
- `tasks/`, `specs/`, `.ralph/reports/`, and `.ralph/logs/events.jsonl` are part of the durable memory of the harness.
- do not rely on conversational memory when a file can carry the state.

Only neutral seed state and installable contracts belong in `src/.ralph/state/` and `src/specs/`. Development records for this source repository stay at root.

## Resume Order

Use this order whenever a fresh Codex run resumes work in this source repository:

1. `.ralph/constitution.md`
2. `.ralph/runtime-contract.md`
3. `.ralph/policy/project-policy.md`
4. `.ralph/state/workflow-state.json`
5. `.ralph/state/spec-queue.json`
6. `.ralph/reports/<current-run-id>/` or `last_report_path`
7. active spec files in `specs/<spec-id>-<slug>/`
8. `specs/<spec-id>-<slug>/task-state.json` when present
9. `specs/INDEX.md`
10. active PRD files in `tasks/`
11. `tasks/todo.md`
12. recent events from `.ralph/logs/events.jsonl`
13. older logs only if the recent context is insufficient

## Canonical Phases

- `bootstrap`
- `prd`
- `epoch_planning`
- `specification`
- `planning`
- `task_generation`
- `implementation`
- `review`
- `verification`
- `release`
- `blocked`
- `complete`

## Canonical Task Statuses

- `queued`
- `ready`
- `in_progress`
- `paused`
- `awaiting_review`
- `review_failed`
- `awaiting_verification`
- `verification_failed`
- `awaiting_release`
- `released`
- `done`
- `blocked`

## Canonical Spec Statuses

- `draft`
- `planned`
- `ready`
- `in_progress`
- `awaiting_pr`
- `awaiting_review`
- `review_failed`
- `awaiting_verification`
- `verification_failed`
- `awaiting_merge`
- `done`
- `blocked`
- `superseded`
- `paused`

## Planning Hierarchy

The durable planning hierarchy is:

1. project PRD
2. epochs
3. numbered specs
4. dependency-ordered tasks
5. branch and GitHub PR execution

Epochs are a grouping and reporting layer. Specs are the actual execution queue.

## Report Contract

Every role report must include these sections:

- `Objective`
- `Inputs Read`
- `Artifacts Written`
- `Verification`
- `Interruption Assessment`
- `Open Issues`
- `Recommended Next Role`

Role reports are the handoff contract for the next fresh run and should name the active spec and active PR context whenever applicable.
