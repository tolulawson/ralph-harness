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
- `git status --short --branch`
- `.ralph/context/project-truths.md`
- `.ralph/context/project-facts.json`
- `.ralph/context/learning-summary.md`
- active queue entry from `.ralph/state/spec-queue.json`
- any bounded file list from the orchestrator
- optional `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

If the task list is missing or incomplete, stop and report that task generation must complete first.

## Workflow

1. Read the active task, canonical task-state entry, spec, plan, queue entry, and any supporting design artifacts.
2. Confirm the branch context matches the active spec branch and inspect the current worktree state before editing.
3. Check any checklist files under `specs/<spec-key>/checklists/` if they exist.
4. If checklists are incomplete and proceeding would be risky, stop and report the gap before continuing.
5. Apply explicit project truths and promoted learnings before changing artifacts.
6. Implement one task end to end, respecting task dependencies and file ownership.
7. Prefer tests before code when the task or plan requires TDD or explicit contract coverage.
8. Create at least one atomic commit before marking the task complete. Multiple commits are allowed only when each commit is a coherent checkpoint inside the same task.
9. End the task with a clean worktree before handing off to review.
10. Update only the task-local artifacts that belong to implementation.
11. Do not append orchestrator events or mutate shared queue, workflow state, or task lifecycle state directly.
12. Capture exact validation or blocker evidence and record the checkpoint in `Commit Evidence`:
   - `Head commit` must be the task checkpoint commit under handoff
   - `Commit subject` must match that checkpoint commit
   - `Task ids covered` must name the assigned task and any tightly coupled sub-slices
   - `Validation run` must name the exact command or check tied to the checkpoint
   - `Additional commits or range` must be `None` for a single-checkpoint task or list the extra task commits plus any later report-only bookkeeping commit
13. Fill in the `Interruption Assessment` section:
   - use `Scope: current` for in-scope defects that belong to the active spec
   - use `Scope: interrupt` only for failing out-of-scope bugs that belong to an earlier spec or no spec at all
14. Record any durable gotchas, successful fixes, or anti-patterns in `Candidate Learnings`.
15. Write the implementation report.

## Outputs

- code or artifact changes for the assigned task
- updated `specs/<spec-key>/tasks.md`
- `.ralph/reports/<run-id>/implement.md`

## Stop Condition

Stop after the assigned task is complete or blocked, the checkpoint is committed, the worktree is clean, and the report is written.
