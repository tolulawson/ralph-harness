---
name: orchestrator
description: Coordinate the Ralph multi-agent runtime by managing the dependency-aware scheduler, durable intent intake, scheduler-lock ownership, execution claims, per-spec worktrees, bounded research fan-out, and canonical shared-state synchronization until the queue is drained or a real stop condition occurs.
---

# Orchestrator

## Use When

- A fresh run needs to resume the harness.
- A role has finished and the next role must be chosen.
- Shared state, reports, the spec queue, lease, durable intents, and event history must be synchronized.
- This skill is already running inside the dedicated orchestrator subagent for the current Ralph entrypoint, not inline on the public entry thread.
- By the time this skill starts, the launcher thread is already done being a launcher. It must not still be acting as a PRD or planning coordinator.
- This invocation owns one orchestrator peer. Multiple orchestrator peers may coordinate through the same control plane, but queue-wide rewrites must flow through the shared scheduler lock.
- Ralph's supported adapters are expected to delegate substantive work through native subagents. Inline worker fallback is not part of the shipped contract.

## Inputs

- `.ralph/constitution.md`
- `.ralph/runtime-contract.md`
- `.ralph/policy/runtime-overrides.md`
- `.ralph/policy/project-policy.md`
- `.ralph/context/project-truths.md`
- `.ralph/context/project-facts.json`
- `.ralph/context/learning-summary.md`
- recent lines from `.ralph/context/learning-log.jsonl` when needed
- `.ralph/state/workflow-state.json`
- `.ralph/state/spec-queue.json`
- `.ralph/state/scheduler-lock.json`
- `.ralph/state/execution-claims.json`
- recent lines from `.ralph/state/scheduler-intents.jsonl`
- latest relevant reports from admitted specs
- admitted spec artifacts in `specs/<spec-id>-<slug>/`
- `specs/<spec-id>-<slug>/task-state.json` when present
- `specs/INDEX.md`
- `tasks/todo.md`
- recent lines from `.ralph/logs/events.jsonl`

## Workflow

1. Read the harness constitution first.
2. Read the runtime contract second.
3. Read runtime overrides third.
4. Read project policy fourth.
5. Read project truths, project facts, and promoted learning summary.
6. Read the canonical workflow state.
7. Read the canonical spec queue.
8. Read the canonical scheduler-lock state, execution-claims state, and recent durable intent window.
9. Attempt to acquire the short-lived global queue write lock only for the current mutation window.
10. If another healthy scheduler-lock holder already owns the queue rewrite window, release promptly and retry later rather than treating that holder as a permanent scheduler owner.
11. Re-read workflow, queue, scheduler lock, claims, and intent state after the queue lock is held.
12. Tail the recent event window instead of loading the full event log.
13. Read only the recent learning log window when diagnosing or promoting learnings.
14. Materialize durable intents in FIFO order:
   - `create_spec`
   - `schedule_spec`
   - `pause_spec`
   - `resume_spec`
   - `status_request`
15. For new specs, seed the queue entry, `depends_on_spec_ids`, default worktree metadata, and compatibility mirrors without bypassing hard dependencies.
16. Compute the admission window and prefer filling every open slot with a runnable spec:
   - active interrupt spec
   - oldest ready interrupt spec by `created_at`
   - else explicit user-requested normal specs whose dependencies are satisfied, in requested order, up to `queue_policy.normal_execution_limit`
   - then remaining dependency-satisfied normal specs by fairness order: `last_dispatch_at`, then `created_at`, then `spec_id`
17. Ensure each admitted spec has a dedicated git worktree, branch, and generated `.ralph/shared/` overlay before dispatching workers, but keep all execution inside those worktrees rather than the canonical checkout.
18. For each admitted spec, choose the next task in this order:
   - first `in_progress`
   - else first `paused`
   - else first `ready`
   - else first `awaiting_review`
   - else first `review_failed`
   - else first `awaiting_verification`
   - else first `verification_failed`
   - else first `awaiting_release`
   - else first `release_failed`
   - else advance the spec using explicit release outcomes and completion rules
19. After a PRD-to-spec pass creates or refreshes a planning batch, identify only the specs from that batch whose `spec.md` exists and whose `research_status` still needs work.
20. For same-batch `research`, dispatch bounded native subagents and record those workers in `.ralph/state/execution-claims.json`.
21. Join the research batch, close each completed research worker or released claim, validate each `research.md`, and then update shared queue metadata once.
22. Outside that batch-scoped research step, decide the next role for each admitted spec from lifecycle state, dependency status, PR state, interruption state, next action, bootstrap readiness, and any explicit scheduling targets, keeping queue-wide throughput as the default posture:
   - spec `plan_check_failed` returns to `plan` or `task-gen`, depending on the latest plan-check findings
   - task `ready` or `in_progress` routes to `implement`
   - task `awaiting_review` or `review_failed` routes to `review`
   - task `awaiting_verification` or `verification_failed` routes to `verify`
   - task `awaiting_release` or `release_failed` routes to `release`
23. Preserve the canonical role classification for every dispatch:
   - analysis-heavy: `plan_check`, `review`, and optionally `research`
   - delivery-heavy: `prd`, `specify`, `plan`, `task_gen`, `bootstrap`, `implement`, `verify`, `release`
24. On supported adapters, claim one runnable non-research role for one admitted spec after releasing the scheduler lock, and allow multiple orchestrator peers to do the same across the ready set.
25. As claims finish, reacquire the scheduler lock briefly, refill freed execution slots from the remaining admitted ready set, then release the lock before more execution.
26. Record every delegated worker in `.ralph/state/execution-claims.json` with `execution_mode = native_subagent`; do not execute worker roles inline while holding the scheduler lock.
27. Pass each delegated worker a single spec, a single worktree path, a single canonical report path, and one execution mode. Shared-state reads must resolve to the canonical checkout directly or through `.ralph/shared/`.
28. Require `bootstrap` before `implement`, and require a passed bootstrap claim with `validation_ready = true` before any non-bootstrap worker role begins in that session.
29. Wait for completed workers or released claims, close that worker thread when one exists, and validate that the worker wrote only the required role-local artifacts from the assigned worktree, that any failure report includes an `Interruption Assessment`, and that any handoff past implementation includes `Quality Gate`, `Commit Evidence`, a clean worktree, and no edits to tracked shared-control-plane paths inside the worktree.
30. Treat `review_failed`, `verification_failed`, and `release_failed` as remediation states rather than terminal stops. Requeue the spec for the next fixing role unless the report names an explicit human-gated blocker.
31. Classify every release report with one explicit outcome: `pr_created`, `awaiting_review`, `awaiting_merge`, `merge_completed`, `release_failed`, or `human_gate_waiting`.
32. Treat worker outputs as spec-local only. Workers release their claims and exit, and any orchestrator peer may later acquire the scheduler lock, mutate canonical shared state directly in the canonical checkout, refresh projections, and dispatch the next role.
33. If a worker failed or blocked with `Scope: interrupt`, create a new interrupt spec using the next numeric `spec_id`, freeze new normal admissions, mark the in-flight normal specs `paused` at role boundaries, and update or create `specs/<origin-spec-key>/amendments.md` when an origin spec exists.
34. Append candidate learnings from worker reports to `.ralph/context/learning-log.jsonl`.
35. Use the `learning` helper skill to classify and promote validated truths or facts when justified.
36. Write `.ralph/reports/<run-id>/orchestrator.md`.
37. Append one orchestrator-owned event to `.ralph/logs/events.jsonl`.
38. Update `.ralph/state/workflow-state.json`.
39. Update `.ralph/state/spec-queue.json`.
40. Update `.ralph/state/scheduler-lock.json` heartbeat or release state as needed.
41. Regenerate `.ralph/state/workflow-state.md`.
42. Regenerate `specs/INDEX.md` when queue-visible metadata changes.
43. After an interrupt spec is released, pop `resume_spec_stack`, thaw normal admissions, restore paused specs and tasks, and continue dispatching.
44. Continue dispatching until the queue is empty, lease ownership must transfer, or a human-gated stop condition occurs.
45. If the active runtime ships the Ralph stop-boundary hook, treat it as a conservative backstop only. The orchestrator should still avoid stopping just because it hit a self-resolvable objection.

## Outputs

- updated workflow state JSON
- updated spec queue JSON
- updated lease state JSON
- updated execution claims JSON
- updated durable intent status when intents are drained
- updated workflow state Markdown
- updated spec register when needed
- updated learning log, summary, truths, or facts when needed
- one orchestrator-owned event log entry
- orchestrator report

## Stop Condition

Stop only when the queue is empty, lease ownership must transfer, or a human-gated runtime-contract stop condition is reached. Do not stop merely because review, verification, or release failed. Do not stop merely because one spec finished, one worker handed off successfully, or one worker claim completed while other runnable specs remain. Treat the orchestration safety cap as a human review boundary, not an automatic failure state. The shipped stop hook may prompt one extra self-check, but it must not replace deliberate stop-boundary reasoning inside the orchestrator itself.
