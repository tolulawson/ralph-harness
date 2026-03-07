---
name: orchestrator
description: Coordinate the Codex-native Ralph harness loop by reading runtime state, managing the FIFO spec queue, spawning exactly one worker at a time, validating outputs, and synchronizing shared state until a stop condition occurs.
---

# Orchestrator

## Use When

- A fresh run needs to resume the harness.
- A role has finished and the next role must be chosen.
- Shared state, reports, the spec queue, and event history must be synchronized.

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
- latest report from `last_report_path`
- active spec artifacts in `specs/<spec-id>-<slug>/`
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
7. Activate the oldest ready spec if no active spec is already in progress.
8. Load only the active spec artifacts, `task-state.json`, and the latest report.
9. Tail the recent event window instead of loading the full event log.
10. Read only the recent learning log window when diagnosing or promoting learnings.
11. Choose the next task in this order:
   - first `in_progress`
   - else first `ready`
   - else first `review_failed`
   - else first `verification_failed`
   - else advance the spec toward PR, merge, or completion
12. Decide the next role from spec status, task lifecycle state, PR state, and next action.
13. Use Codex multi-agent controls such as `spawn_agent` and `wait` to run exactly one worker role at a time.
14. Wait for the worker to finish before doing any further orchestration work.
15. Validate that the worker wrote only the required role-local artifacts.
16. Append candidate learnings from the worker report to `.ralph/context/learning-log.jsonl`.
17. Use the `learning` helper skill to classify and promote validated truths or facts when justified.
18. Write `.ralph/reports/<run-id>/orchestrator.md`.
19. Append one orchestrator-owned event to `.ralph/logs/events.jsonl`.
20. Update `.ralph/state/workflow-state.json`.
21. Update `.ralph/state/spec-queue.json`.
22. Regenerate `.ralph/state/workflow-state.md`.
23. Regenerate `specs/INDEX.md` when queue-visible metadata changes.
24. Continue dispatching until the queue is empty or a runtime-contract stop condition occurs.

## Outputs

- updated workflow state JSON
- updated spec queue JSON
- updated workflow state Markdown
- updated spec register when needed
- updated learning log, summary, truths, or facts when needed
- one orchestrator-owned event log entry
- orchestrator report

## Stop Condition

Stop only when a runtime-contract stop condition is reached or the orchestration safety cap of 200 worker handoffs is hit.
