---
name: orchestrator
description: Coordinate the Ralph multi-agent runtime by managing the dependency-aware scheduler, durable intent intake, lease ownership, worker claims, per-spec worktrees, bounded research fan-out, and canonical shared-state synchronization until a stop condition occurs.
---

# Orchestrator

## Use When

- A fresh run needs to resume the harness.
- A role has finished and the next role must be chosen.
- Shared state, reports, the spec queue, lease, durable intents, and event history must be synchronized.

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
- `.ralph/state/orchestrator-lease.json`
- `.ralph/state/worker-claims.json`
- recent lines from `.ralph/state/orchestrator-intents.jsonl`
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
8. Read the canonical lease state, worker claims state, and recent durable intent window.
9. Attempt to acquire or renew the single-writer lease before mutating canonical shared state.
10. If another healthy lease-holder already owns the scheduler, record any caller request as a durable intent and stop without mutating shared state.
11. Re-read workflow, queue, lease, claims, and intent state after the lease is held.
12. Tail the recent event window instead of loading the full event log.
13. Read only the recent learning log window when diagnosing or promoting learnings.
14. Materialize durable intents in FIFO order:
   - `create_spec`
   - `schedule_spec`
   - `pause_spec`
   - `resume_spec`
   - `status_request`
15. For new specs, seed the queue entry, `depends_on_spec_ids`, default worktree metadata, and compatibility mirrors without bypassing hard dependencies.
16. Compute the admission window:
   - active interrupt spec
   - oldest ready interrupt spec by `created_at`
   - else oldest dependency-satisfied normal specs in FIFO order up to `queue_policy.normal_execution_limit`
17. Ensure each admitted spec has a dedicated git worktree and branch before dispatching workers.
18. For each admitted spec, choose the next task in this order:
   - first `in_progress`
   - else first `paused`
   - else first `ready`
   - else first `review_failed`
   - else first `verification_failed`
   - else first `plan_check_failed`
   - else advance the spec toward PR, merge, or completion
19. After a PRD-to-spec pass creates or refreshes a planning batch, identify only the specs from that batch whose `spec.md` exists and whose `research_status` still needs work.
20. For same-batch `research`, either dispatch bounded native subagents when the active runtime supports them or expose those slots for claim in `.ralph/state/worker-claims.json`.
21. Join the research batch, close each completed research worker or released claim, validate each `research.md`, and then update shared queue metadata once.
22. Outside that batch-scoped research step, decide the next role for each admitted spec from lifecycle state, dependency status, PR state, interruption state, and next action.
23. Preserve the canonical role classification for every dispatch:
   - analysis-heavy: `plan_check`, `review`, and optionally `research`
   - delivery-heavy: `prd`, `specify`, `plan`, `task_gen`, `implement`, `verify`, `release`
24. Spawn bounded non-research workers only for admitted specs that do not already have a healthy worker claim in flight.
25. Pass each worker or current session claim holder a single spec, a single worktree path, a single report path, and one execution mode.
26. Wait for completed workers or released claims, close that worker thread when one exists, and validate that the worker wrote only the required role-local artifacts, that any failure report includes an `Interruption Assessment`, and that any handoff past implementation includes `Quality Gate`, `Commit Evidence`, and a clean worktree.
27. Treat `review_failed`, `verification_failed`, and `release_failed` as remediation states rather than terminal stops. Requeue the spec for the next fixing role unless the report names an explicit human-gated blocker.
28. Synchronize validated control-plane artifacts from worker worktrees back into the canonical checkout before mutating shared state.
29. If a worker failed or blocked with `Scope: interrupt`, create a new interrupt spec using the next numeric `spec_id`, freeze new normal admissions, mark the in-flight normal specs `paused` at role boundaries, and update or create `specs/<origin-spec-key>/amendments.md` when an origin spec exists.
30. Append candidate learnings from worker reports to `.ralph/context/learning-log.jsonl`.
31. Use the `learning` helper skill to classify and promote validated truths or facts when justified.
32. Write `.ralph/reports/<run-id>/orchestrator.md`.
33. Append one orchestrator-owned event to `.ralph/logs/events.jsonl`.
34. Update `.ralph/state/workflow-state.json`.
35. Update `.ralph/state/spec-queue.json`.
36. Update `.ralph/state/orchestrator-lease.json` heartbeat or release state as needed.
37. Regenerate `.ralph/state/workflow-state.md`.
38. Regenerate `specs/INDEX.md` when queue-visible metadata changes.
39. After an interrupt spec is released, pop `resume_spec_stack`, thaw normal admissions, restore paused specs and tasks, and continue dispatching.
40. Continue dispatching until the queue is empty, lease ownership must transfer, or a human-gated stop condition occurs.

## Outputs

- updated workflow state JSON
- updated spec queue JSON
- updated lease state JSON
- updated worker claims JSON
- updated durable intent status when intents are drained
- updated workflow state Markdown
- updated spec register when needed
- updated learning log, summary, truths, or facts when needed
- one orchestrator-owned event log entry
- orchestrator report

## Stop Condition

Stop only when the queue is empty, lease ownership must transfer, or a human-gated runtime-contract stop condition is reached. Do not stop merely because review, verification, or release failed. Treat the orchestration safety cap as a human review boundary, not an automatic failure state.
