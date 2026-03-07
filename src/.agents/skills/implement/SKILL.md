---
name: implement
description: Execute one assigned task for the active numbered spec, update only the in-scope artifacts, record verification notes, and hand off cleanly for review.
---

# Queue-Aware Implement

## Use When

- The orchestrator has assigned one ready task in the active numbered spec.

## Inputs

- active task from `specs/<spec-key>/tasks.md`
- canonical task entry from `specs/<spec-key>/task-state.json`
- `specs/<spec-key>/plan.md`
- `specs/<spec-key>/spec.md`
- `.ralph/context/project-truths.md`
- `.ralph/context/project-facts.json`
- `.ralph/context/learning-summary.md`
- active queue entry from `.ralph/state/spec-queue.json`
- any bounded file list from the orchestrator
- optional `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

If the task list is missing or incomplete, stop and report that task generation must complete first.

## Workflow

1. Read the active task, canonical task-state entry, spec, plan, queue entry, and any supporting design artifacts.
2. Confirm the branch context matches the active spec branch.
3. Check any checklist files under `specs/<spec-key>/checklists/` if they exist.
4. If checklists are incomplete and proceeding would be risky, stop and report the gap before continuing.
5. Apply explicit project truths and promoted learnings before changing artifacts.
6. Implement one task end to end, respecting task dependencies and file ownership.
7. Prefer tests before code when the task or plan requires TDD or explicit contract coverage.
8. Update only the task-local artifacts that belong to implementation.
9. Do not append orchestrator events or mutate shared queue, workflow state, or task lifecycle state directly.
10. Capture exact validation or blocker evidence.
11. Record any durable gotchas, successful fixes, or anti-patterns in `Candidate Learnings`.
12. Write the implementation report.

## Outputs

- code or artifact changes for the assigned task
- updated `specs/<spec-key>/tasks.md`
- `.ralph/reports/<run-id>/implement.md`

## Stop Condition

Stop after the assigned task is complete or blocked and the report is written.
