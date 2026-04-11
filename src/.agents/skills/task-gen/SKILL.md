---
name: task-gen
description: Generate dependency-ordered tasks for one numbered spec so each fresh worker can execute one unit of work without hidden context.
---

# Queue-Aware Task Generation

## Use When

- A numbered spec has both a spec and a plan.

## Inputs

- `specs/<spec-key>/spec.md`
- `specs/<spec-key>/plan.md`
- `.ralph/templates/task-state-template.json`
- optional `research.md`, `data-model.md`, `contracts/`, and `quickstart.md`
- active queue entry from `.ralph/shared/state/spec-queue.json` or the resolved canonical `.ralph/state/spec-queue.json`

If the plan is missing, stop and report that the planning step must complete first.

## Workflow

1. Read the spec, plan, queue entry, and any optional design artifacts. Resolve shared-state reads to the canonical checkout directly or through `.ralph/shared/` when the role runs from a spec worktree.
2. Extract user stories, priorities, technical dependencies, and required checks.
3. Organize tasks by user story so each story can be implemented and verified independently where possible.
4. Use phase structure close to Speckit:
   - Phase 1: setup and branch preparation
   - Phase 2: foundational work
   - Phase 3+: one phase per user story in priority order
   - Final phase: polish, PR readiness, and cross-cutting concerns
5. Use strict task formatting:
   - `- [ ] 001-T001 Description`
   - include `[US1]`, `[US2]`, etc. for story-specific tasks
   - include exact file paths whenever feasible
   - express cross-spec dependencies in the queue entry rather than in the task list, but only when another spec is a true execution prerequisite
   - express intra-spec independence through dependency ordering and phase structure rather than stale parallel markers
6. Ensure each task is executable by a fresh worker without hidden context.
7. Record dependencies, per-task requirement ids, verification commands, planned artifacts, independent test criteria, and PR readiness hooks.
8. Write `specs/<spec-key>/tasks.md`.
9. Write `specs/<spec-key>/task-state.json` so every generated task has a canonical lifecycle record plus requirement and verification metadata.
10. Write the role report to the canonical `.ralph/reports/<run-id>/<spec-key>/task-gen.md`, typically via `.ralph/shared/reports/`, and recommend the next role.

## Outputs

- `specs/<spec-key>/tasks.md`
- `specs/<spec-key>/task-state.json`
- the canonical role report path, typically `.ralph/reports/<run-id>/<spec-key>/task-gen.md`

## Stop Condition

Stop after the task list and report are complete.
