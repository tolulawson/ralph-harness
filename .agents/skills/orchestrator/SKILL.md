---
name: orchestrator
description: Coordinate the Codex-native Ralph harness loop by reading runtime state, managing the FIFO spec queue, selecting the next task, validating outputs, appending one event, and synchronizing state files.
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
4. Read the canonical workflow state.
5. Read the canonical spec queue.
6. Activate the oldest ready spec if no active spec is already in progress.
7. Load only the active spec artifacts, `task-state.json`, and the latest report.
8. Tail the recent event window instead of loading the full event log.
9. Choose the next task in this order:
   - first `in_progress`
   - else first `ready`
   - else first `review_failed`
   - else first `verification_failed`
   - else advance the spec toward PR, merge, or completion
10. Decide the next role from spec status, task lifecycle state, PR state, and next action.
11. Use Codex multi-agent controls such as `spawn_agent` and `wait` to run exactly one worker role at a time.
12. Wait for the worker to finish before doing any further orchestration work.
13. Validate that the worker wrote only the required role-local artifacts.
14. Write `.ralph/reports/<run-id>/orchestrator.md`.
15. Append one orchestrator-owned event to `.ralph/logs/events.jsonl`.
16. Update `.ralph/state/workflow-state.json`.
17. Update `.ralph/state/spec-queue.json`.
18. Regenerate `.ralph/state/workflow-state.md`.
19. Regenerate `specs/INDEX.md` when queue-visible metadata changes.
20. Continue dispatching until the queue is empty or a runtime-contract stop condition occurs.

## Outputs

- updated workflow state JSON
- updated spec queue JSON
- updated workflow state Markdown
- updated spec register when needed
- one event log entry
- orchestrator report

## Stop Condition

Stop only when a runtime-contract stop condition is reached or the orchestration safety cap of 200 worker handoffs is hit.
