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
- `.ralph/shared/context/project-truths.md` or the resolved canonical `.ralph/context/project-truths.md`
- `.ralph/shared/context/project-facts.json` or the resolved canonical `.ralph/context/project-facts.json`
- `.ralph/shared/context/learning-summary.md` or the resolved canonical `.ralph/context/learning-summary.md`
- active queue entry from `.ralph/shared/state/spec-queue.json` or the resolved canonical `.ralph/state/spec-queue.json`
- active claim from `.ralph/shared/state/execution-claims.json` or the resolved canonical `.ralph/state/execution-claims.json`
- any bounded file list from the orchestrator
- optional `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

If the task list is missing or incomplete, stop and report that task generation must complete first.

## Workflow

1. Read the active task, canonical task-state entry, spec, plan, queue entry, active claim, and any supporting design artifacts.
2. Confirm the current claim already passed `bootstrap` with `validation_ready = true`. If bootstrap has not passed, stop and route back to `bootstrap` before implementation begins.
3. Confirm the assigned worktree path matches the active spec branch, inspect that spec worktree state before editing, and verify `.ralph/shared/` resolves shared inputs back to the canonical checkout.
4. Check any checklist files under `specs/<spec-key>/checklists/` if they exist.
5. If checklists are incomplete and proceeding would be risky, stop and report the gap before continuing.
6. Apply explicit project truths and promoted learnings before changing artifacts.
7. Implement one task end to end, respecting task dependencies and file ownership.
8. Prefer tests before code when the task or plan requires TDD or explicit contract coverage.
9. If changed files include React components, hooks, or `useEffect`, run the `react-effects-without-effects` helper skill and apply the recommended replacements or documented keeps.
10. Run the `deslopify-lite` helper skill across changed files and resolve in-scope slop findings before handoff.
11. Create at least one atomic commit before marking the task complete. Multiple commits are allowed only when each commit is a coherent checkpoint inside the same task.
12. End the assigned spec worktree with a clean worktree before handing off to review.
13. Update only the task-local artifacts that belong to implementation.
14. Do not append orchestrator events, mutate shared queue, workflow state, scheduler-lock state, or task lifecycle state directly, or rely on tracked worktree copies of shared-control-plane files.
15. Fill in the `Quality Gate` section:
   - `React Effects Audit` must be `pass` when React scope was touched, else `not_applicable`
   - `React files checked` must list audited files or `None`
   - `Deslopify Lite` must be `pass`
   - `Deslopify notes` must list fixed slop issues or `none found`
16. Capture exact validation or blocker evidence and record the checkpoint in `Commit Evidence`:
   - `Head commit` must be the task checkpoint commit under handoff
   - `Commit subject` must match that checkpoint commit
   - `Task ids covered` must name the assigned task and any tightly coupled sub-slices
   - `Validation run` must name the exact command or check tied to the checkpoint
   - `Additional commits or range` must be `None` for a single-checkpoint task or list the extra task commits plus any later report-only bookkeeping commit
17. Fill in the `Interruption Assessment` section:
   - use `Scope: current` for in-scope defects that belong to the active spec
   - use `Scope: interrupt` only for failing out-of-scope bugs that belong to an earlier spec or no spec at all
18. Record any durable gotchas, successful fixes, or anti-patterns in `Candidate Learnings`.
19. Write the implementation report to the canonical `.ralph/reports/<run-id>/<spec-key>/implement.md`, typically via `.ralph/shared/reports/`.

## Outputs

- code or artifact changes for the assigned task
- updated `specs/<spec-key>/tasks.md`
- the assigned role report path, typically `.ralph/reports/<run-id>/<spec-key>/implement.md`

## Stop Condition

Stop after the assigned task is complete or blocked, the checkpoint is committed, the worktree is clean, and the report is written.
