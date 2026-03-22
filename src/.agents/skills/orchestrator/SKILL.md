---
name: orchestrator
description: Coordinate the Codex-native Ralph harness loop by managing the dependency-aware scheduler, durable intent intake, lease ownership, per-spec worktrees, bounded research fan-out, and canonical shared-state synchronization until a stop condition occurs.
---

# Orchestrator

## Use When

- A fresh run needs to resume the harness.
- A role has finished and the next role must be chosen.
- Shared state, reports, the spec queue, lease, durable intents, and event history must be synchronized.

## Inputs

- `.ralph/constitution.md`
- `.ralph/runtime-contract.md`
- `.ralph/policy/project-policy.md`
- `.ralph/context/project-truths.md`
- `.ralph/context/project-facts.json`
- `.ralph/context/learning-summary.md`
- recent lines from `.ralph/context/learning-log.jsonl` when needed
- `.ralph/state/workflow-state.json`
- `.ralph/state/spec-queue.json`
- `.ralph/state/orchestrator-lease.json`
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
3. Read project policy third.
4. Read project truths, project facts, and promoted learning summary.
5. Read the canonical workflow state.
6. Read the canonical spec queue.
7. Read the canonical lease state and recent durable intent window.
8. Attempt to acquire or renew the single-writer lease before mutating canonical shared state.
9. If another healthy lease-holder already owns the scheduler, record any caller request as a durable intent and stop without mutating shared state.
10. Re-read workflow, queue, lease, and intent state after the lease is held.
11. Tail the recent event window instead of loading the full event log.
12. Read only the recent learning log window when diagnosing or promoting learnings.
13. Materialize durable intents in FIFO order:
   - `create_spec`
   - `schedule_spec`
   - `pause_spec`
   - `resume_spec`
   - `status_request`
14. For new specs, seed the queue entry, `depends_on_spec_ids`, default worktree metadata, and compatibility mirrors without bypassing hard dependencies.
15. Compute the admission window:
   - active interrupt spec
   - oldest ready interrupt spec by `created_at`
   - else oldest dependency-satisfied normal specs in FIFO order up to `queue_policy.normal_execution_limit`
16. Ensure each admitted spec has a dedicated git worktree and branch before dispatching workers.
17. For each admitted spec, choose the next task in this order:
   - first `in_progress`
   - else first `paused`
   - else first `ready`
   - else first `review_failed`
   - else first `verification_failed`
   - else first `plan_check_failed`
   - else advance the spec toward PR, merge, or completion
18. After a PRD-to-spec pass creates or refreshes a planning batch, identify only the specs from that batch whose `spec.md` exists and whose `research_status` still needs work.
19. Spawn research workers for that batch with:
   - `fork_context = true`
   - `agent_type = "explorer"`
   - bounded fan-out only for same-batch `research`
20. Join the research batch with `wait`, close each completed research worker, validate each `research.md`, and then update shared queue metadata once.
21. Outside that batch-scoped research step, decide the next role for each admitted spec from lifecycle state, dependency status, PR state, interruption state, and next action.
22. Preserve the role-based `agent_type` mapping for every worker dispatch.
23. Spawn bounded non-research workers only for admitted specs that do not already have a worker in flight:
   - `explorer`: `plan_check`, `review`, and optionally `research` when analysis depth is the primary concern
   - `worker`: `prd`, `specify`, `plan`, `task_gen`, `implement`, `verify`, `release`
24. Pass each worker a single spec, a single worktree path, and a single report path.
25. Wait for completed workers, close that worker thread, and validate that the worker wrote only the required role-local artifacts, that any failure report includes an `Interruption Assessment`, and that any handoff past implementation includes `Commit Evidence` plus a clean worktree.
26. Synchronize validated control-plane artifacts from worker worktrees back into the canonical checkout before mutating shared state.
27. If a worker failed or blocked with `Scope: interrupt`, create a new interrupt spec using the next numeric `spec_id`, freeze new normal admissions, mark the in-flight normal specs `paused` at role boundaries, and update or create `specs/<origin-spec-key>/amendments.md` when an origin spec exists.
28. Append candidate learnings from worker reports to `.ralph/context/learning-log.jsonl`.
29. Use the `learning` helper skill to classify and promote validated truths or facts when justified.
30. Write `.ralph/reports/<run-id>/orchestrator.md`.
31. Append one orchestrator-owned event to `.ralph/logs/events.jsonl`.
32. Update `.ralph/state/workflow-state.json`.
33. Update `.ralph/state/spec-queue.json`.
34. Update `.ralph/state/orchestrator-lease.json` heartbeat or release state as needed.
35. Regenerate `.ralph/state/workflow-state.md`.
36. Regenerate `specs/INDEX.md` when queue-visible metadata changes.
37. After an interrupt spec is released, pop `resume_spec_stack`, thaw normal admissions, restore paused specs and tasks, and continue dispatching.
38. Continue dispatching until the queue is empty or a runtime-contract stop condition occurs.

## Outputs

- updated workflow state JSON
- updated spec queue JSON
- updated lease state JSON
- updated durable intent status when intents are drained
- updated workflow state Markdown
- updated spec register when needed
- updated learning log, summary, truths, or facts when needed
- one orchestrator-owned event log entry
- orchestrator report

## Stop Condition

Stop only when a runtime-contract stop condition is reached or the orchestration safety cap of 200 worker handoffs is hit.
