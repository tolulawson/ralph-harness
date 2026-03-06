# Ralph Harness Constitution

## Mission

This repository is the source repository and reference implementation for a Codex-native Ralph harness that runs a durable queue-driven workflow:

- the parent agent owns orchestration
- PRD work defines epochs and feature themes
- numbered specs are the unit of execution
- tasks live inside a spec-owned lifecycle
- each spec moves through branch and GitHub PR execution before the queue advances
- repo files are the source of truth

This repository's structure is fixed:

- `src/` is the generic scaffold shipped to other projects
- repo root `.ralph/state/`, `.ralph/logs/`, `.ralph/reports/`, `tasks/`, and `specs/` are this repository's dogfood runtime and development records
- root `skills/` is the public source-skill entry surface

## Constitutional Priority

Interpret the harness in this order:

1. this constitution
2. `.ralph/policy/project-policy.md`
3. `.ralph/state/workflow-state.json`
4. `.ralph/state/spec-queue.json`
5. active spec artifacts and latest role reports

`AGENTS.md` is only the Codex entrypoint that tells Codex where to read the real operating doctrine.

In this source repository, scaffold behavior is edited in `src/` first. The repository root is the workshop and dogfood runtime for building and validating that scaffold.

External named entry points exist via distributable source skills at repository root:

- `ralph-install`
- `ralph-prd`
- `ralph-plan`
- `ralph-execute`

Those source skills are distinct from the runtime role skills under `.agents/skills/`.

## Source Scaffold Contract

- `src/` is the clean installable scaffold output
- `INSTALLATION.md` is the canonical install source of truth for this source repository
- `src/install-manifest.txt` and `src/generated-runtime-manifest.txt` are subordinate install subcontracts referenced by `INSTALLATION.md`
- `skills/ralph-install/SKILL.md` is an execution adapter and must not define install behavior beyond what `INSTALLATION.md` already specifies
- procedural source-repo work tracking does not belong in `src/`
- target runtime records such as `tasks/todo.md`, `tasks/lessons.md`, `.ralph/logs/events.jsonl`, and `.ralph/reports/` are generated during installation or first run
- any change to `src/` that affects installation behavior, copied paths, generated runtime files, loader read order, or required setup steps must update `INSTALLATION.md` in the same change
- changes to `src/` do not imply root dogfood-runtime changes; apply root updates only when they are explicitly requested
- root `AGENTS.md` and root `.ralph/constitution.md` remain source-repo truth documents and are maintained directly for this repository

## Core Workflow

Follow this loop unless the active role instructions say otherwise:

1. read `.ralph/state/workflow-state.json`
2. read `.ralph/state/spec-queue.json`
3. determine the active spec, or activate the oldest ready spec in FIFO order
4. read the most recent role report referenced by `last_report_path`
5. read the active spec artifacts under `specs/<spec-id>-<slug>/`
6. read only a recent tail from `.ralph/logs/events.jsonl` unless diagnosing a blocker
7. choose the next task inside the active spec in this order:
   - first `in_progress`
   - else first `ready`
   - else first `review_failed`
   - else first `verification_failed`
   - else advance the spec toward PR, merge, or completion
8. decide the next role from spec status, task status, and next action
9. run one role-specific unit of work
10. write or update only the artifacts in scope for that role
11. write a role report to `.ralph/reports/<run-id>/<role>.md`
12. append one event to `.ralph/logs/events.jsonl`
13. update `.ralph/state/workflow-state.json`
14. update `.ralph/state/spec-queue.json`
15. regenerate `.ralph/state/workflow-state.md`
16. regenerate `specs/INDEX.md` when queue-visible metadata changes

## Planning Hierarchy

The durable planning hierarchy is:

1. project PRD
2. epochs
3. numbered specs
4. dependency-ordered tasks
5. branch and GitHub PR execution

Epochs are a grouping and reporting layer. Specs are the actual execution queue.

## State Rules

- `.ralph/state/workflow-state.json` is the canonical machine-readable runtime state.
- `.ralph/state/spec-queue.json` is the canonical machine-readable spec queue and spec-state registry.
- `.ralph/state/workflow-state.md` is a human-readable companion file and must agree with the JSON state.
- `specs/INDEX.md` is a human-readable projection of the spec queue.
- `tasks/`, `specs/`, `.ralph/reports/`, and `.ralph/logs/events.jsonl` are part of the durable memory of the harness.
- do not rely on conversational memory when a file can carry the state.

Only neutral seed state and installable contracts belong in `src/.ralph/state/` and `src/specs/`. Development records for this source repository stay at root.

## Resume Order

Use this order whenever a fresh Codex run resumes work:

1. `.ralph/state/workflow-state.json`
2. `.ralph/state/spec-queue.json`
3. `.ralph/reports/<current-run-id>/` or `last_report_path`
4. active spec files in `specs/<spec-id>-<slug>/`
5. `specs/INDEX.md`
6. active PRD files in `tasks/`
7. `tasks/todo.md`
8. recent events from `.ralph/logs/events.jsonl`
9. older logs only if the recent context is insufficient

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

## Queue Policy

- Strict FIFO is the default scheduling rule.
- Specs are processed in `spec_id` order unless emergency preemption is active.
- Only one normal spec may be `in_progress` at a time.
- Later ready specs may not start while an earlier ready spec remains unfinished.

## Emergency Preemption

Urgent work can interrupt the queue only through an emergency spec:

1. create an emergency spec entry and mark its kind as `emergency`
2. mark the interrupted spec `paused`
3. set `resume_spec_id` in `.ralph/state/workflow-state.json`
4. run the emergency spec through the same branch, PR, review, verification, and merge loop
5. restore the paused spec when the emergency spec is done

## Role Boundaries

Each role must stay inside its lane:

- `orchestrator`: chooses the active spec, selects the next task, validates outputs, updates state, records events
- `prd`: writes or updates `tasks/prd-<project>.md` and epoch framing
- `specify`: writes or updates one spec at `specs/<spec-id>-<slug>/spec.md`
- `plan`: writes or updates one spec plan and seeds or refreshes queue-visible spec metadata
- `task-gen`: writes or updates one spec task list
- `implement`: executes one task inside the active spec branch context
- `review`: performs review against the active spec branch or PR and records findings or approval
- `verify`: runs required checks against the active spec branch or PR and captures evidence
- `release`: manages branch, GitHub PR, merge, and final spec advancement

Do not silently absorb another role's responsibilities. If a role finishes early, it should recommend the next role and stop.

## Skill Policy

Repo-local skills live under `.agents/skills/`. Use exactly one primary role skill per run and only the helper skills allowed by that role's config or report contract.

Default helper policy:

- `prd`: `reporting`
- `specify`: `reporting`, `state-sync`
- `plan`: `reporting`, `state-sync`
- `task-gen`: `reporting`
- `implement`: `reporting` plus optional domain skills
- `review`: `reporting`, `analyze`
- `verify`: `reporting` plus optional browser or mobile test skills
- `release`: `reporting`, `state-sync`

## Report Contract

Every role report must include these sections:

- `Objective`
- `Inputs Read`
- `Artifacts Written`
- `Verification`
- `Open Issues`
- `Recommended Next Role`

Role reports are the handoff contract for the next fresh run and should name the active spec and active PR context whenever applicable.

## Git And PR Policy

Default policy is one branch and one GitHub PR per spec:

- branch format: `codex/<spec-key>`
- optional task branch suffix: `codex/<spec-key>/<task-id>` when policy explicitly allows it
- base branch defaults to the project policy setting
- direct-to-main is disabled by default
- review is required before merge
- verification is required before merge
- a spec is not `done` until its GitHub PR is merged

The reference repo may contain example queue entries with null PR metadata when no live PR was opened locally. Installed target projects should treat real GitHub PR tracking as required.

## Verification Standard

Do not mark a task, spec, or phase complete without proof. Proof can include:

- schema validation
- config parsing
- build or typecheck commands
- test commands
- structured review findings
- GitHub PR metadata and merge evidence

When full runtime verification is unavailable, record the exact limitation rather than pretending the workflow is fully green.

## Self-Improvement

- record durable corrections in `tasks/lessons.md`
- update `tasks/todo.md` as work progresses
- add or refine repo-local skills when repeated work patterns emerge
